# -*- coding: utf-8 -*-
from pathlib import Path
import re

v5 = Path(r"Z:\PinelineV5\agents\hongguo_bridge.py").read_text(encoding="utf-8")
m = re.search(
    r"\ndef _film_db\(\):.*?\n\n\n# ---------- merge queue",
    v5,
    re.S,
)
if not m:
    raise SystemExit("extract fail from V5 bridge")
block = m.group(0).rsplit("# ---------- merge queue", 1)[0]

old_pat = re.compile(
    r"\ndef delete_library_series\(names: list\[str\], base: str = DEFAULT_BASE\) -> dict:.*?"
    r"\n    return \{\n"
    r'        "ok": len\(errors\) == 0 or len\(deleted\) > 0,\n'
    r'        "deleted": deleted,\n'
    r'        "errors": errors,\n'
    r'        "count": len\(deleted\),\n'
    r'        "freed_mb": round\(freed_bytes / \(1024 \* 1024\), 1\),\n'
    r"    \}\n",
    re.S,
)

for path in (
    Path(r"Z:\PinelineV2\hongguo_bridge.py"),
    Path(r"Z:\PinelineV4\hongguo_bridge.py"),
):
    t = path.read_text(encoding="utf-8")
    if "def discover_new_seasons" in t and "watchlist_saved" in t:
        print(path, "already")
        continue
    m2 = old_pat.search(t)
    if not m2:
        raise SystemExit(f"delete block not found in {path}")
    t2 = t[: m2.start()] + block + t[m2.end() :]
    path.write_text(t2, encoding="utf-8")
    print("patched", path)
print("ok chars", len(block))
