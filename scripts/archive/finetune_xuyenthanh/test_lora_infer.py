# -*- coding: utf-8 -*-
"""Nghe thử LoRA Res (VieNeu-TTS-0.3B + adapter local)."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(r"Z:\VieNeu-TTS")
PIN = Path(r"Z:\Pineline\finetune_xuyenthanh")
DATASET = ROOT / "finetune" / "dataset"
DEFAULT_LORA = ROOT / "finetune" / "output" / "Res-LoRA-v1"
OUT_DIR = PIN / "test_outputs"

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from vieneu import Vieneu  # noqa: E402


def _pick_ref_from_metadata() -> tuple[Path, str]:
    """Chọn clip ref 4–9s, transcript vừa phải — tránh dòng đầu (thường dài/lạ)."""
    import wave

    meta = DATASET / "metadata_cleaned.csv"
    if not meta.exists():
        meta = DATASET / "metadata.csv"
    if not meta.exists():
        raise FileNotFoundError(f"Missing metadata in {DATASET}")

    raw = DATASET / "raw_audio"
    best: tuple[float, Path, str] | None = None
    for line in meta.read_text(encoding="utf-8").splitlines():
        parts = line.split("|", 1)
        if len(parts) < 2:
            continue
        fname, text = parts[0].strip(), parts[1].strip()
        audio = raw / fname
        if not audio.exists():
            continue
        n = len(text)
        if not (20 <= n <= 80) or text.count(",") > 2:
            continue
        try:
            with wave.open(str(audio), "rb") as w:
                dur = w.getnframes() / float(w.getframerate())
        except Exception:
            continue
        if not (4.0 <= dur <= 9.0):
            continue
        score = abs(dur - 6.0) + abs(n - 45) * 0.02
        if best is None or score < best[0]:
            best = (score, audio, text)

    if best is None:
        line = meta.read_text(encoding="utf-8").splitlines()[0]
        fname, text = line.split("|", 1)
        return raw / fname.strip(), text.strip()
    return best[1], best[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="Test LoRA inference (VieNeu 0.3B)")
    parser.add_argument(
        "--lora",
        default=str(DEFAULT_LORA),
        help="Folder LoRA (final hoac checkpoint-3000, checkpoint-2500,...)",
    )
    parser.add_argument(
        "--text",
        default="Xin chào. Đây là giọng Res sau khi fine-tune LoRA. Hôm nay trời đẹp quá.",
    )
    parser.add_argument("--ref-audio", default=None, help="WAV mau (nen lay tu raw_audio dataset)")
    parser.add_argument("--ref-text", default=None, help="Transcript khop 100%% voi ref-audio")
    parser.add_argument("--no-play", action="store_true", help="Khong mo file WAV sau khi tao")
    args = parser.parse_args()

    lora_path = Path(args.lora)
    if not (lora_path / "adapter_model.safetensors").exists():
        print(f"[ERR] Khong thay adapter trong: {lora_path}")
        sys.exit(1)

    if args.ref_audio:
        ref_audio = Path(args.ref_audio)
        ref_text = args.ref_text or ""
    else:
        ref_audio, ref_text = _pick_ref_from_metadata()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tag = lora_path.name.replace("checkpoint-", "ckpt")
    out_wav = OUT_DIR / f"lora_test_{tag}.wav"

    print("[1/3] Load VieNeu-TTS-0.3B (PyTorch, CUDA)...")
    tts = Vieneu(
        mode="standard",
        backbone_repo="pnnbao-ump/VieNeu-TTS-0.3B",
        codec_repo="neuphonic/neucodec",
        backbone_device="cuda",
        codec_device="cuda",
        gguf_filename=None,  # bat buoc PyTorch — LoRA khong chay tren GGUF/llama_cpp
    )

    print(f"[2/3] Load LoRA: {lora_path}")
    tts.load_lora_adapter(str(lora_path))

    print("[3/3] Tong hop...")
    print(f"  ref_audio : {ref_audio}")
    print(f"  ref_text  : {ref_text[:80]}{'...' if len(ref_text) > 80 else ''}")
    print(f"  synth     : {args.text}")
    # Dung default SDK (temperature=1.0, top_k=50) — temp thap de bi nuot chu / meo
    audio = tts.infer(
        text=args.text,
        ref_audio=str(ref_audio),
        ref_text=ref_text,
    )
    tts.save(audio, str(out_wav))
    tts.close()

    print(f"[OK] Da luu: {out_wav}")
    if not args.no_play:
        os.startfile(str(out_wav))


if __name__ == "__main__":
    main()
