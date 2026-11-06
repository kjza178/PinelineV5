"""Quét tất cả job trong work/ có tiêu đề CJK mà thiếu title_vi → dịch bổ sung."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")

from pathlib import Path
from manifest import Manifest
from llm import chat
from config import get as cfg_get
import re

WORK = Path(__file__).resolve().parent.parent / "work"


def has_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in (s or ""))


def extract_vi(raw: str) -> str:
    """Bóc tách tên tiếng Việt từ response LLM (bỏ dòng chứa CJK)."""
    if not raw:
        return ""
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^\s*[>\-\*\d.]+\s*", "", line)
        line = re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", line)
        line = line.strip().strip('"').strip("'").strip("\u201c").strip("\u201d")
        line = re.sub(
            r"^(?:Dịch[^:]{0,30}:|Bản dịch[^:]{0,15}:|Tiêu đề[^:]{0,15}:)\s*",
            "", line, flags=re.I,
        )
        line = line.strip().strip('"').strip("'")
        if not line:
            continue
        if not has_cjk(line):
            return line[:200]
    return ""


def main():
    jobs = sorted(
        (d for d in WORK.iterdir() if d.is_dir() and (d / "manifest.json").exists()),
        key=lambda p: p.name,
    )
    model = cfg_get("TRANSLATE_MODEL") or None
    missing = []
    for wd in jobs:
        m = Manifest(wd)
        if m.data.get("title_vi"):
            continue
        title = (m.stage("download") or {}).get("title") or ""
        if not title or not has_cjk(title):
            continue
        missing.append((wd, title))

    print(f"Tìm thấy {len(missing)} job thiếu title_vi:")
    for wd, title in missing:
        print(f"  {wd.name}: {title}")

    if not missing:
        print("Không có job nào cần dịch bổ sung.")
        return

    for wd, title in missing:
        print(f"\n--- Dịch: {wd.name} ({title}) ---")
        msgs = [{"role": "user", "content":
                 "Dịch tiêu đề video sau sang tiếng Việt tự nhiên, ngắn gọn. "
                 "CHỈ trả về bản dịch trên MỘT dòng, không giải thích, không ngoặc kép:\n\n" + title}]
        try:
            raw = (chat(msgs, model=model, temperature=0.3, max_tokens=200) or "").strip()
            vi = extract_vi(raw)
            if vi:
                m = Manifest(wd)
                m.data["title_vi"] = vi
                m.save()
                print(f"  ✅ {vi}")
            else:
                print(f"  ❌ Không bóc được tiếng Việt từ: {raw[:120]}")
        except Exception as e:
            print(f"  ❌ Lỗi: {e}")


if __name__ == "__main__":
    main()
