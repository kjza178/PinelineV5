# -*- coding: utf-8 -*-
from pathlib import Path
import re

v5 = Path(r"Z:\PinelineV5\core\film_db.py").read_text(encoding="utf-8")
m = re.search(
    r"(CREATE TABLE IF NOT EXISTS hg_watchlist \(.*?)(?=\n\"\"\")",
    v5,
    re.S,
)
m2 = re.search(
    r"(# ─── Hongguo watchlist.*?)(?=\ndef sync_library_blocks_from_yt_queue)",
    v5,
    re.S,
)
if not m or not m2:
    raise SystemExit(f"extract fail m={bool(m)} m2={bool(m2)}")
schema_add = m.group(1).rstrip() + "\n"
helpers = m2.group(1)

anchor = "CREATE INDEX IF NOT EXISTS series_glossary_core ON series_glossary(core);\n\"\"\""
for path in (Path(r"Z:\PinelineV2\film_db.py"), Path(r"Z:\PinelineV4\film_db.py")):
    t = path.read_text(encoding="utf-8")
    if "hg_watchlist" in t and "upsert_hg_watchlist" in t:
        print(path, "already ok")
        continue
    if anchor not in t:
        raise SystemExit(f"anchor missing in {path}")
    if "hg_watchlist" not in t:
        t = t.replace(anchor, "CREATE INDEX IF NOT EXISTS series_glossary_core ON series_glossary(core);\n\n" + schema_add + "\"\"\"", 1)
    needle = "def sync_library_blocks_from_yt_queue"
    if "upsert_hg_watchlist" not in t:
        if needle not in t:
            raise SystemExit(f"no {needle} in {path}")
        t = t.replace(needle, helpers + "\n" + needle, 1)
    path.write_text(t, encoding="utf-8")
    print("patched", path)
print("ok")
