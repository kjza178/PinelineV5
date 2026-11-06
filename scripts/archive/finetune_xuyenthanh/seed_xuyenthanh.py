# -*- coding: utf-8 -*-
"""Copy XuyenThanh clone ref into VieNeu-TTS finetune dataset (idempotent)."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

PINELINE = Path(r"Z:\Pineline")
DEST_DIR = Path(r"Z:\VieNeu-TTS\finetune\dataset")
RAW = DEST_DIR / "raw_audio"
META = DEST_DIR / "metadata.csv"
SRC_WAV = PINELINE / "voices" / "clone_refs" / "XuyenThanh.wav"
VOICES_JSON = PINELINE / "voices" / "f5_voices.json"
OUT_NAME = "XuyenThanh_001.wav"


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    if not SRC_WAV.is_file():
        raise SystemExit(f"Missing source wav: {SRC_WAV}")

    voices = json.loads(VOICES_JSON.read_text(encoding="utf-8"))
    text = (voices.get("XuyenThanh") or {}).get("text") or ""
    text = text.strip()
    # filter_data yêu cầu kết thúc .,?! và không chứa số
    while text.endswith("…") or text.endswith("..."):
        text = text[:-3].rstrip() if text.endswith("...") else text[:-1].rstrip()
    if text and text[-1] not in ".?!":
        text += "."

    shutil.copy2(SRC_WAV, RAW / OUT_NAME)

    # Merge: giữ dòng khác, ghi đè dòng XuyenThanh_001
    lines: list[str] = []
    if META.is_file():
        for line in META.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith(OUT_NAME + "|"):
                continue
            lines.append(line)
    lines.append(f"{OUT_NAME}|{text}")
    META.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {RAW / OUT_NAME}")
    print(f"Wrote {META} ({len(lines)} rows)")
    print(f"Text: {text[:80]}...")


if __name__ == "__main__":
    main()
