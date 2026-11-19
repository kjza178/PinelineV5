# -*- coding: utf-8 -*-
"""delete_films: expand parts + robust work delete + orphan list."""
from __future__ import annotations

from pathlib import Path

import core.film_db as fd


def _empty_db(monkeypatch):
    class _Cur:
        def execute(self, *a, **k):
            return self

        def fetchall(self):
            return []

    class _Con:
        def __enter__(self):
            return _Cur()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(fd, "connect", lambda: _Con())


def test_expand_parent_pulls_parts(tmp_path, monkeypatch):
    work = tmp_path / "work"
    work.mkdir()
    (work / "abc123").mkdir()
    (work / "abc123_p01").mkdir()
    (work / "abc123_p02").mkdir()
    (work / "other_p01").mkdir()
    monkeypatch.setattr(fd, "WORK", work)
    _empty_db(monkeypatch)
    out = fd.expand_delete_ids(["abc123"], include_parts=True)
    assert "abc123" in out
    assert "abc123_p01" in out
    assert "abc123_p02" in out
    assert "other_p01" not in out


def test_expand_part_does_not_pull_parent(tmp_path, monkeypatch):
    work = tmp_path / "work"
    work.mkdir()
    (work / "abc123").mkdir()
    (work / "abc123_p01").mkdir()
    monkeypatch.setattr(fd, "WORK", work)
    _empty_db(monkeypatch)
    out = fd.expand_delete_ids(["abc123_p01"], include_parts=True)
    assert out == ["abc123_p01"]


def test_delete_work_reports_failure(tmp_path, monkeypatch):
    work = tmp_path / "work"
    work.mkdir()
    jid = "deadbeef01"
    (work / jid).mkdir()
    monkeypatch.setattr(fd, "WORK", work)

    def boom(_p):
        return False, "locked"

    monkeypatch.setattr(fd, "_delete_work_dir", boom)
    # avoid touching real DB: patch connect used inside delete_films
    deleted = []

    class _Cur:
        rowcount = 1

        def execute(self, *a, **k):
            deleted.append(a)
            return self

        def fetchall(self):
            return []

    class _Con:
        def __enter__(self):
            return _Cur()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(fd, "connect", lambda: _Con())
    monkeypatch.setattr(fd, "_lock", __import__("threading").Lock())
    r = fd.delete_films([jid], delete_work=True, include_parts=False)
    assert r["ok"] is True
    assert r["work_failed_count"] == 1
    assert r["work_failed"][0]["job_id"] == jid


def test_list_orphan_skips_db_jobs(tmp_path, monkeypatch):
    work = tmp_path / "work"
    work.mkdir()
    (work / "keep_me").mkdir()
    (work / "orphan_p01").mkdir()
    (work / "logs").mkdir()
    monkeypatch.setattr(fd, "WORK", work)

    class _Cur:
        def execute(self, *a, **k):
            return self

        def fetchall(self):
            return [("keep_me",)]

    class _Con:
        def __enter__(self):
            return _Cur()

        def __exit__(self, *a):
            return False

    monkeypatch.setattr(fd, "connect", lambda: _Con())
    r = fd.list_orphan_work_dirs()
    assert r["ok"]
    ids = {x["job_id"] for x in r["items"]}
    assert "orphan_p01" in ids
    assert "keep_me" not in ids
    assert "logs" not in ids
