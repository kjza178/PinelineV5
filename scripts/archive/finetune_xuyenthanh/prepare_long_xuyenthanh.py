# -*- coding: utf-8 -*-
"""Split long Res.wav + Whisper-VI ASR -> VieNeu finetune dataset."""
from __future__ import annotations

import re
import wave
from pathlib import Path

import numpy as np
from faster_whisper import WhisperModel

SRC = Path(r"Z:\Pineline\rvc_data\Res.wav")
OUT_DIR = Path(r"Z:\VieNeu-TTS\finetune\dataset")
RAW = OUT_DIR / "raw_audio"
META = OUT_DIR / "metadata.csv"

MIN_SEC = 3.0
MAX_SEC = 14.5
TARGET_SEC = 8.0
MODEL_SIZE = "large-v3"  # fallback handled in main


def _load_wav_mono_16k(path: Path) -> tuple[np.ndarray, int]:
    import soundfile as sf
    import soxr

    audio, sr = sf.read(str(path), always_2d=False)
    if getattr(audio, "ndim", 1) > 1:
        audio = audio.mean(axis=1)
    audio = audio.astype(np.float32)
    if sr != 16000:
        audio = soxr.resample(audio, sr, 16000).astype(np.float32)
        sr = 16000
    return audio, sr


def _write_wav(path: Path, audio: np.ndarray, sr: int = 16000) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = np.clip(audio, -1.0, 1.0)
    pcm_i16 = (pcm * 32767.0).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm_i16.tobytes())


def _clean_text(t: str) -> str:
    t = (t or "").strip()
    t = re.sub(r"\s+", " ", t)
    # strip digits / weird symbols for filter_data
    if re.search(r"\d", t):
        return ""
    if re.search(r"(?:[A-Z]){2,}", t):
        return ""
    if not t:
        return ""
    if t[-1] not in ".?!":
        t += "."
    return t


def _pack_segments(segments: list[dict]) -> list[dict]:
    """Merge consecutive ASR segments into clips ~TARGET_SEC within [MIN, MAX]."""
    packs: list[dict] = []
    cur_texts: list[str] = []
    cur_start: float | None = None
    cur_end: float | None = None

    def flush() -> None:
        nonlocal cur_texts, cur_start, cur_end
        if cur_start is None or cur_end is None or not cur_texts:
            cur_texts, cur_start, cur_end = [], None, None
            return
        dur = cur_end - cur_start
        text = _clean_text(" ".join(cur_texts))
        if MIN_SEC <= dur <= MAX_SEC and text:
            packs.append({"start": cur_start, "end": cur_end, "text": text})
        cur_texts, cur_start, cur_end = [], None, None

    for seg in segments:
        s, e, txt = float(seg["start"]), float(seg["end"]), (seg["text"] or "").strip()
        if not txt or e <= s:
            continue
        if cur_start is None:
            cur_start, cur_end, cur_texts = s, e, [txt]
            continue
        # if adding would exceed MAX, flush first
        if e - cur_start > MAX_SEC:
            flush()
            cur_start, cur_end, cur_texts = s, e, [txt]
            continue
        cur_texts.append(txt)
        cur_end = e
        if (cur_end - cur_start) >= TARGET_SEC:
            flush()

    flush()
    return packs


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Missing source: {SRC}")

    print(f"Loading audio: {SRC}")
    audio, sr = _load_wav_mono_16k(SRC)
    print(f"Audio: {len(audio)/sr:.1f}s @ {sr}Hz")

    # Prefer CUDA large-v3; fall back medium if OOM/unavailable
    device = "cuda"
    compute = "float16"
    size = MODEL_SIZE
    try:
        print(f"Loading Whisper {size} on {device}...")
        model = WhisperModel(size, device=device, compute_type=compute)
    except Exception as e:
        print(f"large-v3 failed ({e}); trying medium...")
        size = "medium"
        model = WhisperModel(size, device=device, compute_type=compute)

    print("Transcribing (vi, VAD)...")
    segs_iter, info = model.transcribe(
        str(SRC),
        language="vi",
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=400),
        beam_size=5,
        condition_on_previous_text=True,
    )
    segments = [{"start": s.start, "end": s.end, "text": s.text} for s in segs_iter]
    print(f"ASR segments: {len(segments)} (lang={info.language})")

    packs = _pack_segments(segments)
    print(f"Packed clips: {len(packs)}")

    # Wipe previous XuyenThanh_* seeds only; keep unrelated if any
    RAW.mkdir(parents=True, exist_ok=True)
    for old in RAW.glob("Res_*.wav"):
        old.unlink()

    rows: list[str] = []
    for i, p in enumerate(packs, start=1):
        a0 = int(p["start"] * sr)
        a1 = int(p["end"] * sr)
        clip = audio[a0:a1]
        name = f"Res_{i:04d}.wav"
        _write_wav(RAW / name, clip, sr)
        rows.append(f"{name}|{p['text']}")

    META.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")
    total = sum(p["end"] - p["start"] for p in packs)
    print(f"Wrote {len(rows)} wavs + {META}")
    print(f"Usable audio: {total/60:.1f} min")


if __name__ == "__main__":
    main()
