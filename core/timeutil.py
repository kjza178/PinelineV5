"""core/timeutil.py — MỘT kiểu mốc thời gian cho manifest (port từ V6).

Quy ước (fix 2026-11-14 R1.4): `started_at` / `finished_at` / `created_at` = ISO-8601 UTC.
`updated_at` của stage vẫn epoch float (nhịp tim).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def to_epoch(v: Any) -> float | None:
    if v is None or isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v) if v > 0 else None
    s = str(v).strip()
    if not s:
        return None
    try:
        f = float(s)
        return f if f > 0 else None
    except ValueError:
        pass
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def to_iso(v: Any) -> str | None:
    t = to_epoch(v)
    if t is None:
        return None
    try:
        return datetime.fromtimestamp(t, timezone.utc).isoformat()
    except (OverflowError, OSError, ValueError):
        return None
