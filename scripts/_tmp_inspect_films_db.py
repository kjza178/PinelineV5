# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

p = Path(r"Z:\PinelineV2\data\films.db")
print("exists", p.exists(), "size", p.stat().st_size if p.exists() else 0)
con = sqlite3.connect(str(p))
con.row_factory = sqlite3.Row
cur = con.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY 1")]
print("tables", tables)
for t in tables:
    cols = [c[1] for c in cur.execute(f"PRAGMA table_info({t})")]
    n = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"--- {t} n={n}")
    print(" cols", cols)
if "films" in tables:
    print("hg_series_id filled", cur.execute("SELECT COUNT(*) FROM films WHERE hg_series_id IS NOT NULL AND hg_series_id<>''").fetchone()[0])
    print("distinct series", cur.execute("SELECT COUNT(DISTINCT series) FROM films WHERE series IS NOT NULL AND series<>''").fetchone()[0])
    print("sample", [dict(r) for r in cur.execute(
        "SELECT job_id, title, series, season, hg_series_id, hg_name, series_ui, status, yt_url FROM films WHERE hg_series_id<>'' LIMIT 5"
    )])
if "library_blocks" in tables:
    print("blocks sample", [dict(r) for r in cur.execute("SELECT * FROM library_blocks LIMIT 5")])
    print("blocks by status", list(cur.execute("SELECT status, COUNT(*) FROM library_blocks GROUP BY status")))
con.close()
