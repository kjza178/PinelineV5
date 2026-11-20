"""resolve_job: agent hay cắt id thành «9aa089_p01» trong khi folder «9aa0891fbfd1_p01»."""
from __future__ import annotations

import json
from pathlib import Path

import agent_core as ac
import agent_qa_ask as qa


def _mk_job(root: Path, jid: str, *, script: list | None = None, agent: dict | None = None) -> Path:
    wd = root / jid
    wd.mkdir(parents=True)
    mf = {"job_id": jid, "stages": {"translate": {"status": "done"}}, "agent": agent or {}}
    (wd / "manifest.json").write_text(json.dumps(mf, ensure_ascii=False), encoding="utf-8")
    if script is not None:
        (wd / "script.json").write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
    return wd


def test_resolve_prefix_pnn(tmp_path: Path):
    _mk_job(tmp_path, "9aa0891fbfd1_p01")
    _mk_job(tmp_path, "9aa0891fbfd1_p02")
    assert qa.resolve_job(tmp_path, "9aa089_p01") == "9aa0891fbfd1_p01"
    assert qa.resolve_job(tmp_path, "9aa089_p02") == "9aa0891fbfd1_p02"
    assert qa.resolve_job(tmp_path, "9aa0891fbfd1_p01") == "9aa0891fbfd1_p01"
    assert qa.resolve_job(tmp_path, "9aa089") is None  # 2 part → mơ hồ nếu chỉ prefix


def test_resolve_plain_prefix_unique(tmp_path: Path):
    _mk_job(tmp_path, "abcdef123456")
    assert qa.resolve_job(tmp_path, "abcd") == "abcdef123456"


def test_script_peek_short_id_cjk(tmp_path: Path):
    rows = [
        {"i": 1, "zh": "你好", "vi": "Xin chào"},
        {"i": 187, "zh": "我可是C位啊。", "vi": "Tôi là C位 đấy."},
    ]
    _mk_job(
        tmp_path,
        "9aa0891fbfd1_p01",
        script=rows,
        agent={"held_at": "review_failed", "hold_reason": "còn chữ Hán"},
    )
    out = ac.script_peek(tmp_path, "9aa089_p01", sample=2)
    assert out["job_id"] == "9aa0891fbfd1_p01"
    assert out["n_cjk_in_vi"] == 1
    assert out["cjk_in_vi_sample"][0]["i"] == 187
    assert "C位" in out["cjk_in_vi_sample"][0]["vi"]
    assert out["hold_reason"] == "còn chữ Hán"


def test_resolve_job_id_hint_candidates(tmp_path: Path):
    _mk_job(tmp_path, "deadbeef0001_p01")
    try:
        ac.resolve_job_id(tmp_path, "zzzz_p01")
        assert False, "expected FileNotFoundError"
    except FileNotFoundError as e:
        assert "zzzz_p01" in str(e)
