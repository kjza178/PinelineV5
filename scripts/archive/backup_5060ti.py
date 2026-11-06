#!/usr/bin/env python3
"""backup_5060ti.py — Gói FULL code Pineline cho máy RTX 5060 Ti + i9-14900K.

Khác backup.py thường:
  - Kèm giọng mẫu (voices/**/*.wav) để clone TTS chạy ngay
  - Ép pineline.config.json = profile 5060ti (CPU threads=2, low priority, batch=8)
  - Kèm dung-may-5060ti.bat + README máy đích
  - Vẫn LOẠI work/ (job video nặng), venv, cache, cookies

Chạy:  python backup_5060ti.py
       python backup_5060ti.py D:/Pineline_5060ti.zip
"""
from __future__ import annotations

import datetime
import fnmatch
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SKIP_DIRS = {
    "work", "__pycache__", "logs", "voice_samples", "cookies", ".git",
    "rvc_data", "piper_voices", ".cache", "node_modules",
    "pineline_env", "vieneu_env", ".venv", ".pip_tmp",
    "agent-transcripts",
}
SKIP_FILE_GLOBS = [
    "*.pyc", "*_cookies.txt", "*.log", "*.mp4", "*.mkv", "*.webm",
    "*.exe", "*.dll", "*.zip", "*.rar", "*.7z", "*.tar", "*.gz",
    "*.partial",
]
# Giọng: GIỮ wav/mp3 trong voices/ (máy mới cần để clone)
KEEP_VOICE_AUDIO = True


def skip_file(rel: Path) -> bool:
    name = rel.name
    if any(fnmatch.fnmatch(name, g) for g in SKIP_FILE_GLOBS):
        return True
    if not KEEP_VOICE_AUDIO:
        audio = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}
        if rel.suffix.lower() in audio and rel.parts and rel.parts[0] == "voices":
            return True
    return False


def main():
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        ROOT.parent / f"Pineline_5060ti_{stamp}.zip"

    profile = ROOT / "pineline.config.rtx5060ti.json"
    if not profile.exists():
        print("[err] thiếu pineline.config.rtx5060ti.json")
        sys.exit(1)
    cfg_5060 = json.loads(profile.read_text(encoding="utf-8"))

    readme = f"""# Pineline — gói máy RTX 5060 Ti / i9-14900K

Đóng gói: {stamp}

## Cài trên máy mới
1. Giải nén ra thư mục (vd `D:\\Pineline`)
2. Cài Python 3.11/3.12 + FFmpeg (PATH)
3. Chạy: `python install.py --gpu`  (hoặc theo INSTALL.md)
4. Nháy `dung-may-5060ti.bat`  — tự áp config chống treo rồi mở app
   (hoặc copy `pineline.config.rtx5060ti.json` → `pineline.config.json`)

## Profile máy này (đã nhét sẵn vào pineline.config.json)
- VIENEU_DEVICE=cuda, VIENEU_BATCH=8
- VIENEU_CPU_THREADS=2, VIENEU_LOW_PRIORITY=1  (14900K dễ đơ UI)
- VIENEU_STALL_SEC=600, ASR_STALL_SEC=900
- TRANSLATE_BATCH=50, LLM_NUM_CTX=8192 (Ollama không cấp KV 128k)
- Xem CHANGELOG_FIX.md (ASR Fun/Paraformer, khớp time, sub dài, VRAM, render/NVENC/lật)

## Lưu ý
- KHÔNG gồm thư mục `work/` (job video). Copy riêng nếu cần.
- KHÔNG gồm venv — chạy install.py để dựng.
- Sửa đường dẫn VIENEU_PY / OMNI_PY / HF_HOME trong pineline.config.json nếu ổ đĩa khác.
- Chỉ mở MỘT cửa sổ Pineline.
"""

    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in ROOT.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(ROOT)
            if any(part in SKIP_DIRS for part in rel.parts):
                continue
            if skip_file(rel):
                continue
            # Thay pineline.config.json bằng profile 5060ti
            if rel.as_posix() == "pineline.config.json":
                z.writestr("pineline.config.json",
                           json.dumps(cfg_5060, ensure_ascii=False, indent=2) + "\n")
                n += 1
                continue
            z.write(p, rel.as_posix())
            n += 1
        # đảm bảo có profile + bat + readme
        if "pineline.config.rtx5060ti.json" not in z.namelist():
            z.write(profile, "pineline.config.rtx5060ti.json")
            n += 1
        z.writestr("README_5060ti.txt", readme)
        n += 1
        # nếu zip chưa có config (bị skip?) — đã xử lý ở trên
        if "pineline.config.json" not in z.namelist():
            z.writestr("pineline.config.json",
                       json.dumps(cfg_5060, ensure_ascii=False, indent=2) + "\n")
            n += 1

    size = out.stat().st_size / 1e6
    print(f"[ok] Backup 5060 Ti: {n} entries -> {out}  ({size:.1f} MB)")
    print("     Giải nén trên máy kia + install.py + dung-may-5060ti.bat")


if __name__ == "__main__":
    main()
