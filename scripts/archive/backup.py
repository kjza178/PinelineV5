#!/usr/bin/env python3
"""backup.py — Nén BỘ KHUNG Pineline (code + installer + config) ra 1 file .zip.

Chạy:  python backup.py                 -> ../Pineline_backup_YYYYMMDD_HHMM.zip
       python backup.py D:/nơi/khac.zip -> ghi ra đường dẫn chỉ định

LOẠI TRỪ: jobs (work/), cache, model, venv, audio nặng (dolly_refs/rvc_data...),
cookies, __pycache__. Chỉ giữ khung để bê sang máy khác + chạy install.py.
"""
from __future__ import annotations

import datetime
import fnmatch
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# Thư mục KHÔNG nén (data/cache/model/venv/jobs)
SKIP_DIRS = {
    "work", "__pycache__", "logs", "voice_samples", "cookies", ".git",
    "rvc_data", "piper_voices", ".cache", "node_modules",
    "pineline_env", "vieneu_env", ".venv", ".pip_tmp",
}
# Thư mục audio giọng: giữ JSON registry, BỎ file audio (nặng, là data)
AUDIO_EXT = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".pt", ".npy", ".index", ".pth"}
SKIP_FILE_GLOBS = ["*.pyc", "*_cookies.txt", "*.log", "*.mp4", "*.mkv", "*.webm",
                   "*.exe", "*.dll", "*.zip", "*.rar", "*.7z", "*.tar", "*.gz"]


def skip_file(rel: Path) -> bool:
    name = rel.name
    if any(fnmatch.fnmatch(name, g) for g in SKIP_FILE_GLOBS):
        return True
    # audio trong thư mục voices/ = data -> bỏ (giữ .json)
    if rel.suffix.lower() in AUDIO_EXT and rel.parts and rel.parts[0] == "voices":
        return True
    return False


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        ROOT.parent / f"Pineline_backup_{datetime.datetime.now():%Y%m%d_%H%M}.zip"
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in ROOT.rglob("*"):
            if p.is_dir():
                continue
            rel = p.relative_to(ROOT)
            if any(part in SKIP_DIRS for part in rel.parts):
                continue
            if skip_file(rel):
                continue
            z.write(p, rel.as_posix())
            n += 1
    size = out.stat().st_size / 1e6
    print(f"[ok] Backup {n} file -> {out}  ({size:.1f} MB)")


if __name__ == "__main__":
    main()
