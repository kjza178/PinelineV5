"""
asr_retry_nano.py — Pass 3: retry đoạn aligned xấu bằng Fun-ASR-Nano (pad).

Đọc:
  asr.aligned.json (+ asr.paraformer_zh.chars.json để re-time)
  audio.wav
  optional align_qa_report.json / tự detect

Ghi sidecar (không đụng asr.json):
  asr.aligned_retry.json
  sub.zh.aligned_retry.srt
  asr.aligned_retry.meta.json

Chạy:
  python asr_retry_nano.py work/<job>
  python asr_retry_nano.py work/<job> --aligned asr.aligned.json --max 80
"""
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
import time
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")

from asr_align_nano_para import align_nano_to_para, _norm_chars
from asr_vad_utils import DEFAULT_PAD_S
from fun_asr_nano import MODEL_ID, VAD_ID, _pick_device, _spread_sentences, _wav_dur
from subs import to_srt, split_long_segments, sub_split_cfg, _plain_len
from vram import free_gpu_vram

_PUNCT_RE = re.compile(r"[^\u4e00-\u9fff0-9a-zA-Z]+")


def _norm(s: str) -> str:
    return _PUNCT_RE.sub("", s or "")


def _find_bad_spans(
    aligned: list[dict],
    para_chars: list[dict],
    miss_thr: float = 0.35,
    cluster_fix: bool = True,
) -> list[tuple[float, float]]:
    """Trả các cửa sổ [start,end] cần retry (đã merge gần nhau)."""
    para_keep = []
    for c in para_chars:
        nc = _norm(c.get("ch") or "")
        if nc:
            para_keep.append((nc[0], float(c["start"]), float(c["end"])))

    windows: list[tuple[float, float]] = []
    for a in aligned:
        if cluster_fix and a.get("align") == "monotonic_fix":
            windows.append((float(a["start"]) - 0.3, float(a["end"]) + 0.3))
            continue
        nt = _norm(a.get("text") or "")
        if len(nt) < 4:
            continue
        t0, t1 = float(a["start"]) - 0.8, float(a["end"]) + 0.8
        idxs = [i for i, (_, s, e) in enumerate(para_keep) if e >= t0 and s <= t1]
        if not idxs:
            windows.append((t0, t1))
            continue
        window = "".join(para_keep[i][0] for i in idxs)
        if nt in window:
            continue
        j = hit = 0
        for ch in nt:
            k = window.find(ch, j)
            if k >= 0:
                hit += 1
                j = k + 1
        miss = 1 - hit / len(nt)
        if miss >= miss_thr:
            windows.append((float(a["start"]) - 0.4, float(a["end"]) + 0.4))

    if not windows:
        return []
    windows.sort()
    merged = [list(windows[0])]
    for st, en in windows[1:]:
        if st <= merged[-1][1] + 1.0:
            merged[-1][1] = max(merged[-1][1], en)
        else:
            merged.append([st, en])
    return [(max(0.0, a), b) for a, b in merged]


def _asr_clip_nano(asr_m, clip, sr: int, language: str = "中文") -> str:
    try:
        res = asr_m.generate(
            input=[clip], cache={}, batch_size=1, language=language, itn=True, fs=sr,
        )
    except Exception:  # noqa: BLE001
        tp = None
        try:
            import soundfile as sf
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tp = tmp.name
            sf.write(tp, clip, sr)
            res = asr_m.generate(
                input=tp, cache={}, batch_size=1, language=language, itn=True,
            )
        except Exception:  # noqa: BLE001
            return ""
        finally:
            if tp:
                Path(tp).unlink(missing_ok=True)
    if not res:
        return ""
    it = res[0] if isinstance(res, list) else res
    if isinstance(it, dict):
        return (it.get("text") or "").strip()
    return ""


def run_retry(
    work_dir: str | Path,
    aligned_name: str = "asr.aligned.json",
    chars_name: str = "asr.paraformer_zh.chars.json",
    out_tag: str = "aligned_retry",
    device: str = "auto",
    hub: str = "hf",
    language: str = "中文",
    max_windows: int = 120,
    miss_thr: float = 0.35,
    pad_s: float | None = None,
) -> dict:
    work_dir = Path(work_dir)
    wav = work_dir / "audio.wav"
    aligned_path = work_dir / aligned_name
    chars_path = work_dir / chars_name
    if not aligned_path.exists():
        raise FileNotFoundError(aligned_path)
    if not wav.exists():
        raise FileNotFoundError(wav)

    aligned = json.loads(aligned_path.read_text(encoding="utf-8"))
    para_chars = []
    if chars_path.exists():
        para_chars = json.loads(chars_path.read_text(encoding="utf-8"))

    windows = _find_bad_spans(aligned, para_chars, miss_thr=miss_thr)
    print(f"[retry] bad windows: {len(windows)} (cap {max_windows})", flush=True)
    windows = windows[:max_windows]
    if not windows:
        # copy through
        out_asr = work_dir / f"asr.{out_tag}.json"
        out_srt = work_dir / f"sub.zh.{out_tag}.srt"
        out_asr.write_text(json.dumps(aligned, ensure_ascii=False, indent=2), encoding="utf-8")
        out_srt.write_text(to_srt(aligned, key="text"), encoding="utf-8")
        meta = {"status": "done", "n_retry_windows": 0, "n_segments": len(aligned),
                "note": "no bad spans"}
        (work_dir / f"asr.{out_tag}.meta.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return meta

    pad = DEFAULT_PAD_S if pad_s is None else float(pad_s)
    total = _wav_dur(wav)
    free_gpu_vram("trước Nano retry")
    dev = _pick_device(device)
    from funasr import AutoModel
    print(f"[retry] nạp {MODEL_ID} trên {dev}…", flush=True)
    asr_m = AutoModel(
        model=MODEL_ID, trust_remote_code=True, device=dev, hub=hub, disable_update=True,
    )

    import soundfile as sf
    # thay text các câu nằm trong window bằng kết quả Nano (giữ timing aligned)
    rows = [dict(r) for r in aligned]
    n_replaced = 0
    with sf.SoundFile(str(wav), "r") as f:
        sr = int(f.samplerate)
        for wi, (st, en) in enumerate(windows):
            ss = max(0.0, st - pad)
            ee = min(total, en + pad) if total > 0 else en + pad
            a0, a1 = int(ss * sr), int(ee * sr)
            f.seek(max(a0, 0))
            clip = f.read(max(a1 - a0, 0), dtype="float32")
            if clip is None or len(clip) < 160:
                continue
            if getattr(clip, "ndim", 1) > 1:
                clip = clip.mean(axis=1)
            text = _asr_clip_nano(asr_m, clip, sr, language=language)
            if not text:
                continue
            # câu nào overlap cửa sổ → thay text; timing giữ; đánh dấu retry
            parts = _spread_sentences(text, st, en) if _plain_len(text) > 18 else [
                {"start": st, "end": en, "text": text}
            ]
            # xóa câu cũ trong [st,en], chèn parts
            keep = [r for r in rows if not (float(r["end"]) > st and float(r["start"]) < en)]
            for p in parts:
                keep.append({
                    "start": round(float(p["start"]), 3),
                    "end": round(float(p["end"]), 3),
                    "text": p["text"],
                    "align": "nano_retry",
                })
            rows = keep
            n_replaced += 1
            if (wi + 1) % 10 == 0 or wi + 1 == len(windows):
                print(f"[retry] {wi+1}/{len(windows)} · replaced_windows={n_replaced}", flush=True)

    rows.sort(key=lambda r: float(r["start"]))
    # re-align timing với para chars nếu có
    if para_chars:
        rows = align_nano_to_para(
            [{"start": r["start"], "end": r["end"], "text": r["text"]} for r in rows],
            para_chars,
        )
        for r in rows:
            if r.get("align") == "para_char":
                pass
            # giữ nano_retry nếu vừa sửa — align_nano_to_para ghi đè align
        # đánh dấu lại: không cần

    max_zh, _, max_dur = sub_split_cfg()
    rows = split_long_segments(rows, max_chars=max_zh, key="text", max_dur=max_dur)
    for i, r in enumerate(rows):
        r["i"] = i

    out_asr = work_dir / f"asr.{out_tag}.json"
    out_srt = work_dir / f"sub.zh.{out_tag}.srt"
    out_asr.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    out_srt.write_text(to_srt(rows, key="text"), encoding="utf-8")
    meta = {
        "status": "done",
        "n_retry_windows": len(windows),
        "n_replaced_windows": n_replaced,
        "n_segments": len(rows),
        "asr_path": str(out_asr),
        "srt_path": str(out_srt),
        "pad_s": pad,
        "miss_thr": miss_thr,
        "model": MODEL_ID,
    }
    (work_dir / f"asr.{out_tag}.meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[ok] retry → {out_asr.name} ({len(rows)} câu, {n_replaced} windows)", flush=True)
    return meta


def main(argv=None):
    ap = argparse.ArgumentParser(description="Retry đoạn aligned xấu bằng Fun-ASR-Nano")
    ap.add_argument("work_dir")
    ap.add_argument("--aligned", default="asr.aligned.json")
    ap.add_argument("--chars", default="asr.paraformer_zh.chars.json")
    ap.add_argument("--out-tag", default="aligned_retry")
    ap.add_argument("--device", default="auto")
    ap.add_argument("--hub", default="hf", choices=("hf", "ms"))
    ap.add_argument("--max", type=int, default=120)
    ap.add_argument("--miss", type=float, default=0.35)
    ap.add_argument("--pad", type=float, default=None)
    args = ap.parse_args(argv)
    run_retry(
        args.work_dir, aligned_name=args.aligned, chars_name=args.chars,
        out_tag=args.out_tag, device=args.device, hub=args.hub,
        max_windows=args.max, miss_thr=args.miss, pad_s=args.pad,
    )


if __name__ == "__main__":
    main()
