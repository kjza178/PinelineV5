#!/usr/bin/env python3
"""backup_voices.py — Đóng gói THƯ VIỆN GIỌNG (voices/) để bê sang máy khác.

Chạy:  python backup_voices.py            -> ../Pineline_voices_YYYYMMDD.zip
       python backup_voices.py D:/x.zip   -> ghi ra đường dẫn chỉ định

Giải nén ở máy mới: bung vào thư mục Pineline (đè lên voices/). Xong app tự nhận
đủ giọng (registry voices/f5_voices.json + audio mẫu).
"""
import datetime
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VOICES = ROOT / "voices"


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else \
        ROOT.parent / f"Pineline_voices_{datetime.datetime.now():%Y%m%d}.zip"
    n = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for p in VOICES.rglob("*"):
            if p.is_file():
                z.write(p, ("voices/" + p.relative_to(VOICES).as_posix()))
                n += 1
    print(f"[ok] {n} file giọng -> {out}  ({out.stat().st_size/1e6:.0f} MB)")


if __name__ == "__main__":
    main()
