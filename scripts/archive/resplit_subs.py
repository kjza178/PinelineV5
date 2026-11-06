"""
resplit_subs.py — Tách lại câu dài trong script.json (không dịch lại).

Dùng khi job đã dịch xong nhưng sub Việt quá dài / 1 dòng hiển thị quá lâu.
Sau khi chạy: cần TTS + assemble + render lại (index i đã đổi).

    python resplit_subs.py work/<job_id>
    python resplit_subs.py work/<job_id> --dry
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from subs import split_bilingual_rows, sub_split_cfg, to_srt


def resplit(work_dir: Path, dry: bool = False) -> int:
    script_path = work_dir / "script.json"
    if not script_path.exists():
        print(f"[err] Không có {script_path}")
        return 1
    rows = json.loads(script_path.read_text(encoding="utf-8"))
    max_zh, max_vi, max_dur = sub_split_cfg()
    out = split_bilingual_rows(rows, max_zh=max_zh, max_vi=max_vi, max_dur=max_dur)
    print(f"[resplit] {len(rows)} -> {len(out)} dòng "
          f"(zh≤{max_zh}, vi≤{max_vi}, max {max_dur}s/dòng)")
    if dry:
        for r in out[:12]:
            d = float(r.get("end", 0)) - float(r.get("start", 0))
            vi = (r.get("vi") or "")[:60]
            print(f"  {r.get('start', 0):6.1f}s +{d:.1f}s  {vi}")
        return 0
    script_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    (work_dir / "sub.vi.srt").write_text(to_srt(out, key="vi"), encoding="utf-8")
    print(f"[ok] Ghi {script_path.name}, sub.vi.srt — chạy lại TTS + render.")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="Tách lại sub dài trong script.json")
    ap.add_argument("work_dir")
    ap.add_argument("--dry", action="store_true", help="Chỉ in thống kê, không ghi file")
    args = ap.parse_args(argv)
    return resplit(Path(args.work_dir), dry=args.dry)


if __name__ == "__main__":
    sys.exit(main())
