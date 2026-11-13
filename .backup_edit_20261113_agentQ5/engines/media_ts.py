"""Mốc thời gian tiếng của file nguồn — sửa tiếng "dồn mẫu" ở file ghép nhiều tập.

File ghép copy nhiều tập AAC giữ lại 1024 mẫu mồi (priming) đầu mỗi tập: gói đó có
mốc gần như trùng gói trước (stts ~0) nhưng vẫn chứa 23 ms tiếng. Giải mã thường
(ffmpeg không aresample) dồn hết mẫu → audio.wav dài hơn hình, lệch tăng dần theo
số chỗ nối (0281: +1.2 s ở phút 54, +25 s ở cuối). ASR/TTS/sub/tiếng nền đều trễ theo.

Sửa: mọi chỗ tách tiếng từ video dùng AUDIO_TS_FIX (bám mốc, bỏ mẫu chồng, đệm khe).
Job cũ đã ASR trên audio dồn mẫu: ensure_job_audio_ts() dời mốc asr/script/tts/srt
về trục hình rồi ghép lại dub_fit — không cần ASR/TTS lại.
"""
from __future__ import annotations
import sys as _sync_sys  # sync_from_v2: bootstrap — chạy trực tiếp vẫn import được core.*/engines.*
from pathlib import Path as _SyncP
_SYNC_ROOT = str(_SyncP(__file__).resolve().parents[1])
if _SYNC_ROOT not in _sync_sys.path:
    _sync_sys.path.insert(0, _SYNC_ROOT)

import bisect
import json
import shutil
import struct
import subprocess
import time
from pathlib import Path

AUDIO_TS_FIX = "aresample=async=1:min_hard_comp=0.01:first_pts=0"
DRIFT_MIN_SEC = 0.3
MARK = ".audio_ts_fixed.json"
MARK_PENDING = ".audio_ts_pending.json"
_JSON_FILES = ("asr.json", "script.json", "script.display.json", "script.pre_review.json", "tts.json")
_SRT_FILES = ("sub.zh.srt", "sub.vi.srt", "sub.vi.burn.srt")
_STALE_AUDIO = ("mixed_audio.wav", "mixed_audio.partial.wav", "orig_audio.flac", "orig_audio.wav")
_DEMUCS = ("no_vocals.wav", "vocals.wav")


def _boxes(f, start: int, end: int):
    pos = start
    while pos + 8 <= end:
        f.seek(pos)
        size, typ = struct.unpack(">I4s", f.read(8))
        hdr = 8
        if size == 1:
            size = struct.unpack(">Q", f.read(8))[0]
            hdr = 16
        elif size == 0:
            size = end - pos
        if size < hdr:
            return
        yield typ, pos + hdr, pos + size
        pos += size


def _child(f, s: int, e: int, name: bytes):
    return next(((s2, e2) for t, s2, e2 in _boxes(f, s, e) if t == name), None)


def mp4_track_stts(video: Path, kind: bytes = b"soun") -> tuple[int, list[tuple[int, int]]] | None:
    """(timescale, [(count, delta)]) của track đầu tiên loại `kind` (soun/vide)."""
    if Path(video).suffix.lower() not in (".mp4", ".mov", ".m4v"):
        return None
    try:
        with open(video, "rb") as f:
            f.seek(0, 2)
            moov = _child(f, 0, f.tell(), b"moov")
            if not moov:
                return None
            for t, s, e in _boxes(f, *moov):
                if t != b"trak":
                    continue
                mdia = _child(f, s, e, b"mdia")
                if not mdia:
                    continue
                hdlr, mdhd, minf = (_child(f, *mdia, n) for n in (b"hdlr", b"mdhd", b"minf"))
                if not (hdlr and mdhd and minf):
                    continue
                f.seek(hdlr[0] + 8)
                if f.read(4) != kind:
                    continue
                f.seek(mdhd[0])
                ver = f.read(1)[0]
                f.seek(mdhd[0] + (20 if ver else 12))
                tsc = struct.unpack(">I", f.read(4))[0]
                stbl = _child(f, *minf, b"stbl")
                stts = _child(f, *stbl, b"stts") if stbl else None
                if not stts:
                    return None
                f.seek(stts[0] + 4)
                n = struct.unpack(">I", f.read(4))[0]
                data = f.read(8 * n)
                return tsc, [struct.unpack_from(">II", data, 8 * i) for i in range(n)]
    except (OSError, struct.error, StopIteration):
        return None
    return None


def audio_drift_points(video: Path) -> tuple[list[float], list[float]] | None:
    """Trục 'dồn mẫu' → trục mốc: (vị trí theo mẫu [s], tiếng dư tích luỹ tới đó [s]).

    Mỗi gói AAC chứa `normal` mẫu (gói chuẩn có delta = normal). Gói lệch delta
    → dư (normal - delta) mẫu so với mốc (dương = chồng, âm = khe).
    """
    got = mp4_track_stts(video, b"soun")
    if not got:
        return None
    tsc, ent = got
    counts: dict[int, int] = {}
    for c, d in ent:
        counts[d] = counts.get(d, 0) + c
    normal = max(counts, key=counts.get)
    pos, acc = 0, 0
    xs: list[float] = []
    ys: list[float] = []
    last = len(ent) - 1
    for k, (c, d) in enumerate(ent):
        pos += c * normal
        if d != normal and not (k == last and c == 1):
            acc += c * (normal - d)
            xs.append(pos / tsc)
            ys.append(acc / tsc)
    return xs, ys


def audio_ts_drift(video: Path) -> float:
    """Tổng tiếng dư so với mốc (s). 0 nếu không đọc được."""
    pts = audio_drift_points(video)
    return pts[1][-1] if pts and pts[1] else 0.0


def make_retime(video: Path):
    """Hàm t(trục dồn mẫu) → t(trục hình). None nếu lệch không đáng kể."""
    pts = audio_drift_points(video)
    if not pts or not pts[1] or abs(pts[1][-1]) < DRIFT_MIN_SEC:
        return None
    xs, ys = pts

    def f(t: float) -> float:
        i = bisect.bisect_right(xs, t)
        return max(0.0, t - (ys[i - 1] if i else 0.0))
    return f


def _probe_dur(p: Path) -> float:
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(p)], capture_output=True, text=True, timeout=120)
        return float(r.stdout.strip())
    except (ValueError, OSError, subprocess.SubprocessError):
        return 0.0


def _retime_srt(text: str, f) -> str:
    import re

    def conv(m):
        h, mi, s, ms = (int(x) for x in m.groups())
        t = f(h * 3600 + mi * 60 + s + ms / 1000)
        ms_t = int(round(t * 1000))
        return f"{ms_t // 3600000:02d}:{ms_t // 60000 % 60:02d}:{ms_t // 1000 % 60:02d},{ms_t % 1000:03d}"
    return re.sub(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})", conv, text)


def ensure_job_audio_ts(work_dir: Path, video: Path) -> dict:
    """Job đã ASR trên audio dồn mẫu → dời mốc về trục hình + ghép lại dub_fit.

    Nhận diện qua độ dài audio.wav: bằng trục dồn mẫu (= hình + drift) thì cần dời.
    Ghi MARK để không dời 2 lần. Trả {"status": ok|fixed|skip, ...}.
    """
    work_dir = Path(work_dir)
    mark = work_dir / MARK
    if mark.exists():
        return {"status": "ok", "why": "đã dời mốc trước đó"}
    pending = work_dir / MARK_PENDING
    if pending.exists():
        # Crash giữa lúc thay file: tmp đã tính từ bản gốc → chỉ commit nốt, KHÔNG dời mốc lần 2
        info = json.loads(pending.read_text(encoding="utf-8"))
        print("[audio-ts] tiếp tục commit dở từ lần trước", flush=True)
        return _commit_retime(work_dir, info)
    drift = audio_ts_drift(video)
    if abs(drift) < DRIFT_MIN_SEC:
        return {"status": "ok", "drift": drift}
    wav = work_dir / "audio.wav"
    vdur = _probe_dur(video)
    adur = _probe_dur(wav) if wav.exists() else 0.0
    if adur and abs(adur - vdur) < min(1.0, abs(drift) / 2):
        return {"status": "ok", "drift": drift, "why": "audio.wav đã bám mốc"}
    if not adur or abs(adur - (vdur + drift)) > max(1.0, abs(drift) * 0.2):
        return {"status": "skip", "drift": drift, "why": f"audio.wav {adur:.1f}s không ở trục dồn mẫu"}
    f = make_retime(video)
    if f is None:
        return {"status": "ok", "drift": drift}
    print(f"[audio-ts] nguồn dư {drift:+.2f}s tiếng so với hình (ghép nhiều tập) → dời mốc job về trục hình",
        flush=True)
    bak = work_dir / "_pre_audio_ts"
    bak.mkdir(exist_ok=True)
    changed = []
    for name in _JSON_FILES:
        p = work_dir / name
        if not p.exists():
            continue
        rows = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(rows, list):
            continue
        _backup_once(p, bak)
        for r in rows:
            if not isinstance(r, dict):
                continue
            for k in ("start", "end"):
                if isinstance(r.get(k), (int, float)) and not isinstance(r.get(k), bool):
                    r[k] = round(f(float(r[k])), 3)
            for w in r.get("words") or []:
                if isinstance(w, dict):
                    for k in ("start", "end"):
                        if isinstance(w.get(k), (int, float)):
                            w[k] = round(f(float(w[k])), 3)
        indent = 2 if name == "script.display.json" else None
        _tmp_of(p).write_text(json.dumps(rows, ensure_ascii=False, indent=indent), encoding="utf-8")
        changed.append(name)
    for name in _SRT_FILES:
        p = work_dir / name
        if p.exists():
            _backup_once(p, bak)
            _tmp_of(p).write_text(_retime_srt(p.read_text(encoding="utf-8"), f), encoding="utf-8")
            changed.append(name)
    tmp = work_dir / "audio.ts.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vn", "-af", AUDIO_TS_FIX,
                    "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(tmp)], check=True)
    info = {"drift": round(drift, 3), "video_dur": vdur, "audio_dur_before": adur,
            "changed": changed, "at": time.strftime("%Y-%m-%d %H:%M:%S")}
    _atomic_write(work_dir / MARK_PENDING, json.dumps(info, ensure_ascii=False, indent=1))
    return _commit_retime(work_dir, info)


def _tmp_of(p: Path) -> Path:
    return p.with_name(p.name + ".audio_ts.tmp")


def _backup_once(p: Path, bak: Path) -> None:
    """Không bao giờ đè backup đã có — bản trong _pre_audio_ts luôn là bản gốc trước lần dời đầu."""
    if not (bak / p.name).exists():
        shutil.copy2(p, bak / p.name)


def _atomic_write(p: Path, text: str) -> None:
    t = p.with_name(p.name + ".tmp")
    t.write_text(text, encoding="utf-8")
    t.replace(p)


def _commit_retime(work_dir: Path, info: dict) -> dict:
    """Pha thay file — chạy lại an toàn: mỗi bước kiểm tra trạng thái trước khi làm."""
    bak = work_dir / "_pre_audio_ts"
    bak.mkdir(exist_ok=True)
    for name in info.get("changed") or []:
        t = _tmp_of(work_dir / name)
        if t.exists():
            t.replace(work_dir / name)
    for name in _STALE_AUDIO:
        (work_dir / name).unlink(missing_ok=True)
    for name in _DEMUCS:
        p = work_dir / name
        if p.exists():
            p.replace(work_dir / f"{p.stem}.drifted{p.suffix}")
            print(f"[audio-ts] {name} tách trên audio dồn mẫu → đổi tên .drifted, cần tách nền lại", flush=True)
    wav, tmp = work_dir / "audio.wav", work_dir / "audio.ts.wav"
    if tmp.exists():
        if wav.exists():
            if (bak / "audio.wav").exists():
                wav.unlink()
            else:
                wav.replace(bak / "audio.wav")
        tmp.replace(wav)
    from engines.assemble import assemble_fit
    if (work_dir / "tts.json").exists():
        r = assemble_fit(work_dir)
        print(f"[audio-ts] ghép lại dub_fit: lệch>0.5s {r.get('n_drift_gt_0_5')} · max {r.get('max_drift')}s",
            flush=True)
    _atomic_write(work_dir / MARK, json.dumps(info, ensure_ascii=False, indent=1))
    (work_dir / MARK_PENDING).unlink(missing_ok=True)
    print(f"[audio-ts] xong: {', '.join(info.get('changed') or [])} · bản cũ ở {bak.name}/", flush=True)
    return {"status": "fixed", **info}


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description="Kiểm/sửa tiếng dồn mẫu của job (file ghép nhiều tập).")
    ap.add_argument("work_dir")
    ap.add_argument("--check", action="store_true", help="chỉ báo độ lệch, không sửa")
    a = ap.parse_args(argv)
    wd = Path(a.work_dir)
    vids = sorted(p for p in wd.glob("source.*") if p.suffix.lower() in (".mp4", ".mov", ".m4v", ".mkv"))
    try:
        import json as _json
        vp = (((_json.loads((wd / "manifest.json").read_text(encoding="utf-8")).get("stages") or {})
               .get("download") or {}).get("video_path"))
        if vp and Path(vp).is_file():
            vids = [Path(vp)]
    except (OSError, ValueError):
        pass
    if not vids:
        raise SystemExit("không thấy video nguồn (manifest video_path / source.*)")
    d = audio_ts_drift(vids[0])
    print(f"{vids[0].name}: tiếng dư {d:+.3f}s so với hình")
    if not a.check:
        print(ensure_job_audio_ts(wd, vids[0]))


if __name__ == "__main__":
    main()
