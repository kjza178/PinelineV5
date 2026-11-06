"""
Chờ migrate_work.py xong → kiểm tra bản mới ở đích → xoá work_old_migrated.

Điều kiện xoá (đủ cả):
- work/ là junction trỏ tới đích và đọc được
- server :8801 trả lời, số job API = số job trong bản cũ
- mọi file trong bản cũ có ở đích; file media (mp4/wav/mkv) cùng dung lượng
Không đạt → giữ bản cũ, báo Telegram.
"""
from __future__ import annotations

import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
OLD = ROOT / "work_old_migrated"
DST = Path(sys.argv[1] if len(sys.argv) > 1 else r"D:\PinelineV2_work")
MIG_LOG = ROOT / "migrate_work.log"
LOG = ROOT / "cleanup_old_work.log"
MEDIA = {".mp4", ".wav", ".mkv", ".webm", ".mov", ".m4a"}

sys.path.insert(0, str(ROOT))


def log(msg: str) -> None:
    line = f"[{datetime.now():%H:%M:%S}] {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def tg(msg: str) -> None:
    try:
        os.environ.setdefault("AGENT_TELEGRAM", "1")
        from agent_watch import telegram_send
        telegram_send("Dọn work cũ: " + msg, force=True)
    except Exception as e:  # noqa: BLE001
        log(f"telegram lỗi: {e}")


def migration_state() -> str:
    if not MIG_LOG.is_file():
        return "running"
    txt = MIG_LOG.read_text(encoding="utf-8", errors="replace")
    if "LỖI:" in txt or "chuyển thất bại" in txt:
        return "failed"
    if "] xong · queue=" in txt:
        return "done"
    return "running"


def verify() -> str | None:
    if not (WORK.is_junction() and Path(os.path.realpath(WORK)).resolve() == DST.resolve()):
        return f"work/ không phải junction tới {DST}"
    if not OLD.is_dir():
        return "không thấy work_old_migrated"
    try:
        jobs = requests.get("http://127.0.0.1:8801/api/jobs", timeout=15).json()
        jobs = jobs if isinstance(jobs, list) else (jobs.get("jobs") or [])
    except Exception as e:  # noqa: BLE001
        return f"server không trả lời: {e}"
    old_jobs = [d for d in OLD.iterdir() if (d / "manifest.json").is_file()]
    if len(jobs) < len(old_jobs):
        return f"API có {len(jobs)} job, bản cũ có {len(old_jobs)}"
    missing, size_diff = [], []
    for f in OLD.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(OLD)
        g = DST / rel
        if not g.is_file():
            missing.append(str(rel))
        elif f.suffix.lower() in MEDIA and f.stat().st_size != g.stat().st_size and "partial" not in f.name:
            size_diff.append(str(rel))
    if missing:
        return f"thiếu {len(missing)} file ở đích, vd {missing[:3]}"
    if size_diff:
        return f"{len(size_diff)} file media lệch dung lượng, vd {size_diff[:3]}"
    return None


def main() -> None:
    log(f"chờ migrate_work xong… (đích {DST})")
    while True:
        st = migration_state()
        if st == "failed":
            log("migrate thất bại — không xoá gì")
            return
        if st == "done":
            break
        time.sleep(60)
    time.sleep(30)
    err = verify()
    if err:
        log(f"KHÔNG xoá: {err}")
        tg(f"giữ lại work_old_migrated vì kiểm tra không đạt: {err}")
        return
    size = sum(f.stat().st_size for f in OLD.rglob("*") if f.is_file())
    shutil.rmtree(OLD)
    log(f"đã xoá work_old_migrated ({size / 1e9:.1f}GB)")
    tg(f"kiểm tra OK, đã xoá bản cũ ({size / 1e9:.0f}GB) trên Z:")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        log(f"LỖI: {e}")
        tg(f"LỖI: {e} — bản cũ vẫn giữ")
