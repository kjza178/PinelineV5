# -*- coding: utf-8 -*-
"""Snippet appended into film_db.py — hg_watchlist helpers."""

WATCHLIST_SCHEMA = """
CREATE TABLE IF NOT EXISTS hg_watchlist (
    sid          TEXT PRIMARY KEY,
    core         TEXT,
    title        TEXT,
    name         TEXT,
    season       INTEGER,
    eps          INTEGER,
    score        TEXT,
    album        TEXT,
    source       TEXT,
    on_disk      INTEGER DEFAULT 1,
    deleted_at   TEXT,
    seen_at      TEXT,
    updated_at   TEXT
);
CREATE INDEX IF NOT EXISTS hg_watch_core ON hg_watchlist(core);
CREATE INDEX IF NOT EXISTS hg_watch_name ON hg_watchlist(name);
CREATE INDEX IF NOT EXISTS hg_watch_disk ON hg_watchlist(on_disk);
"""

# In connect(), after executescript(SCHEMA), also executescript(WATCHLIST_SCHEMA)
# Or add WATCHLIST_SCHEMA into SCHEMA string.
