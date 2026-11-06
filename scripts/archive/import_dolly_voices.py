# -*- coding: utf-8 -*-
"""Import giọng mẫu clone từ dataset dolly-audio (parquet) -> đăng ký vào
voices/f5_voices.json (registry dùng chung cho vieneu/omnivoice).

Mỗi voice_id -> ghép ~TARGET_SEC giây clip sạch của CÙNG người + transcript ->
voices/dolly_refs/<voice>.wav + entry {ref, text}. Chọn giọng bằng tên trong app.

Dùng:
  python import_dolly_voices.py <parquet> --voices "Distinguished Gentleman,Decisive Queen"
  python import_dolly_voices.py <parquet> --list          # chỉ liệt kê giọng
  python import_dolly_voices.py <parquet> --all --min-sec 8
"""
from __future__ import annotations
import argparse, io, json, re
from pathlib import Path
from collections import defaultdict

import numpy as np
import soundfile as sf
import pyarrow.parquet as pq

_PROJ = Path(__file__).parent
REF_DIR = _PROJ / "voices" / "dolly_refs"
REG = _PROJ / "voices" / "f5_voices.json"
TARGET_SEC = 10.0


def _safe(name: str) -> str:
    s = re.sub(r"[^0-9A-Za-z]+", "_", name).strip("_")
    return s or "voice"


def _load_registry() -> dict:
    if REG.exists():
        return json.loads(REG.read_text(encoding="utf-8"))
    return {}


def _save_registry(d: dict) -> None:
    REG.parent.mkdir(parents=True, exist_ok=True)
    REG.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def _trim(wav: np.ndarray, sr: int, thresh: float = 0.01) -> np.ndarray:
    """Cắt lặng đầu/cuối nhẹ."""
    idx = np.where(np.abs(wav) > thresh)[0]
    if len(idx) < 2:
        return wav
    a = max(0, idx[0] - int(0.03 * sr))
    b = min(len(wav), idx[-1] + int(0.05 * sr))
    return wav[a:b]


def collect(parquet: str) -> dict:
    """voice_id -> list[(dur, wav24, text)] (đã trim)."""
    pf = pq.ParquetFile(parquet)
    by = defaultdict(list)
    for b in pf.iter_batches(batch_size=500, columns=["text", "voice_id", "audio"]):
        d = b.to_pydict()
        for t, v, a in zip(d["text"], d["voice_id"], d["audio"]):
            try:
                wav, sr = sf.read(io.BytesIO(a["bytes"]), dtype="float32")
            except Exception:  # noqa: BLE001
                continue
            if getattr(wav, "ndim", 1) > 1:
                wav = wav.mean(axis=1)
            wav = _trim(wav, sr)
            by[v].append((len(wav) / sr, wav, sr, (t or "").strip()))
    return by


def build_ref(voice: str, clips: list, target_sec: float = TARGET_SEC) -> tuple[Path, str] | None:
    """Ghép clip CÙNG người tới ~target_sec -> wav + transcript. Ưu tiên clip vừa phải."""
    if not clips:
        return None
    sr = clips[0][2]
    clips = sorted(clips, key=lambda c: -c[0])            # dài -> ngắn
    picked, total = [], 0.0
    for dur, wav, s, txt in clips:
        if s != sr:
            continue
        picked.append((wav, txt)); total += dur
        if total >= target_sec:
            break
    if not picked:
        return None
    gap = np.zeros(int(sr * 0.15), dtype=np.float32)
    audio = np.concatenate([w for w, _ in [(picked[0][0], 0)] ] +
                           sum([[gap, w] for w, _ in picked[1:]], []) ) if len(picked) > 1 \
        else picked[0][0]
    text = " ".join(t for _, t in picked).strip()
    REF_DIR.mkdir(parents=True, exist_ok=True)
    out = REF_DIR / f"{_safe(voice)}.wav"
    sf.write(str(out), audio, sr)
    return out, text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parquet")
    ap.add_argument("--voices", default="", help="danh sách voice_id, ngăn bằng dấu phẩy")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--min-sec", type=float, default=6.0, help="bỏ giọng tổng clip < ngưỡng")
    ap.add_argument("--target-sec", type=float, default=TARGET_SEC)
    args = ap.parse_args()

    by = collect(args.parquet)
    if args.list:
        for v, cl in sorted(by.items(), key=lambda x: -sum(c[0] for c in x[1])):
            print(f"{v:<26} {len(cl):>2} clip  {sum(c[0] for c in cl):>5.1f}s tổng")
        return

    want = set(x.strip() for x in args.voices.split(",") if x.strip())
    if args.all:
        want = set(by.keys())
    if not want:
        print("Chưa chọn --voices hoặc --all"); return

    reg = _load_registry()
    n = 0
    for v in want:
        cl = by.get(v)
        if not cl or sum(c[0] for c in cl) < args.min_sec:
            print(f"[bỏ] {v}: thiếu audio"); continue
        res = build_ref(v, cl, args.target_sec)
        if not res:
            print(f"[bỏ] {v}: không ghép được"); continue
        ref, text = res
        name = _safe(v)
        reg[name] = {"ref": str(ref.relative_to(_PROJ)).replace("\\", "/"), "text": text}
        dur = sf.info(str(ref)).duration
        print(f"[ok] {name}: mẫu {dur:.1f}s")
        n += 1
    _save_registry(reg)
    print(f"Đã đăng ký {n} giọng -> {REG}")


if __name__ == "__main__":
    main()
