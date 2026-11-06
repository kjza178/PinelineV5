# -*- coding: utf-8 -*-
"""A/B: base / ckpt2500 / final LoRA — cùng ref + text."""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(r"Z:\VieNeu-TTS")
OUT = Path(r"Z:\Pineline\finetune_xuyenthanh\test_outputs")
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from vieneu import Vieneu

REF_AUDIO = ROOT / "finetune" / "dataset" / "raw_audio" / "Res_0053.wav"
REF_TEXT = "Độc của ta đã hoàn toàn giải trừ rồi."
TEXT = "Xin chào. Đây là giọng Res sau khi fine-tune. Hôm nay trời đẹp quá."

VARIANTS = [
    ("base_no_lora", None),
    ("old_XuyenThanh_v2", ROOT / "finetune" / "output" / "XuyenThanh-LoRA-v2"),
    ("Res_v1", ROOT / "finetune" / "output" / "Res-LoRA-v1"),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    print("[load] VieNeu-TTS-0.3B ...")
    tts = Vieneu(
        mode="standard",
        backbone_repo="pnnbao-ump/VieNeu-TTS-0.3B",
        codec_repo="neuphonic/neucodec",
        backbone_device="cuda",
        codec_device="cuda",
        gguf_filename=None,
    )

    for name, lora in VARIANTS:
        if lora is not None and getattr(tts, "_lora_loaded", False):
            tts.unload_lora_adapter()
        if lora is not None:
            if not (Path(lora) / "adapter_model.safetensors").exists():
                print(f"[skip] missing {lora}")
                continue
            print(f"[lora] {lora}")
            tts.load_lora_adapter(str(lora))
        else:
            print("[lora] none (base)")

        # default SDK: temperature=1.0, top_k=50
        audio = tts.infer(
            text=TEXT,
            ref_audio=str(REF_AUDIO),
            ref_text=REF_TEXT,
        )
        out = OUT / f"ab_{name}.wav"
        tts.save(audio, str(out))
        print(f"[ok] {out}")

    tts.close()
    print("[done] nghe so: ab_base_no_lora.wav | ab_ckpt2500.wav | ab_final_7500.wav")


if __name__ == "__main__":
    main()
