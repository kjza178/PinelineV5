"""One-shot: bỏ @app.* trên /api/queue/* và /api/jobs/* trong server.py
để đăng ký qua pineline.server.routes.{queue,jobs}.attach + include_router.

Chạy: python scripts/_strip_app_queue_jobs.py
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "server.py"

# Decorator lines to strip (exact path prefixes)
_DECO = re.compile(
    r'^@app\.(?:post|get|delete|put|api_route)\('
    r'["\']/(?:api/queue|api/jobs)(?:/|["\'])'
)

# Also strip trailing comment-only continuation? no — each decorator is one line.
# api_route may span? In this file it's one line.


def main() -> None:
    text = SERVER.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    stripped = 0
    for line in lines:
        if _DECO.match(line.lstrip() if False else line):
            # Match from start of line (decorators are left-aligned)
            if line.startswith("@app.") and (
                "/api/queue" in line or "/api/jobs" in line
            ):
                stripped += 1
                continue
        out.append(line)
    SERVER.write_text("".join(out), encoding="utf-8")
    print(f"stripped {stripped} @app decorators from {SERVER}")


if __name__ == "__main__":
    main()
