"""One-shot: bỏ @app còn lại trên /api/fs /api/cookies /api/voices /frames
/brand-logos /clone-voice /voice-sample /models /llm/models trong server.py.
"""
from __future__ import annotations

import re
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server.py"
_DECO = re.compile(
    r'^@app\.(?:get|post|delete|put|api_route)\([^\n]*'
    r'/(?:api/fs|api/cookies|api/voices|api/frames|api/brand-logos|'
    r'api/clone-voice|api/voice-sample|api/models|api/llm/models)'
)


def main() -> None:
    lines = SERVER.read_text(encoding="utf-8").splitlines(keepends=True)
    out: list[str] = []
    stripped = 0
    for line in lines:
        if line.startswith("@app.") and _DECO.match(line):
            stripped += 1
            continue
        out.append(line)
    SERVER.write_text("".join(out), encoding="utf-8")
    print(f"stripped {stripped} decorators from {SERVER}")


if __name__ == "__main__":
    main()
