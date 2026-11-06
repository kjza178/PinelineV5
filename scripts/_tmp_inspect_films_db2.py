# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

for p in [
    Path(r"Z:\PinelineV5\data\films.db"),
    Path(r"Z:\PinelineV2\data\films.db"),
    Path(r"Z:\PinelineV4\data\films.db"),
]:
    print("==", p, "exists", p.exists())
    if not p.exists():
        continue
    con = sqlite3.connect(str(p))
    con.row_factory = sqlite3.Row
    n = con.execute("SELECT COUNT(*) FROM films").fetchone()[0]
    sid = con.execute(
        "SELECT COUNT(*) FROM films WHERE hg_series_id IS NOT NULL AND hg_series_id<>''"
    ).fetchone()[0]
    we = dict(con.execute("SELECT work_exists, COUNT(*) FROM films GROUP BY work_exists"))
    lb = con.execute("SELECT COUNT(*) FROM library_blocks").fetchone()[0]
    gl = con.execute("SELECT COUNT(*) FROM series_glossary").fetchone()[0]
    print(f" films={n} with_sid={sid} work_exists={we} blocks={lb} glossary={gl}")
    rows = con.execute(
        "SELECT title, series, season, hg_series_id, hg_name, work_exists, status FROM films LIMIT 8"
    ).fetchall()
    for r in rows:
        print(" ", dict(r))
    cores = [
        r[0]
        for r in con.execute(
            "SELECT DISTINCT core FROM library_blocks WHERE core IS NOT NULL AND core<>'' LIMIT 12"
        )
    ]
    print(" block cores sample", cores)
    con.close()
