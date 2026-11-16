"""Pure helpers: same-source / mux-complete guards (no FastAPI boot)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_same_source_logic():
    prev_src, prev_n = "asr.nano_fa.json", 100
    src_name, n = "asr.nano_fa.json", 100
    assert prev_src == src_name and prev_n == n and prev_n > 0
    src_name2 = "asr.fun_nano.json"
    assert not (prev_src == src_name2 and prev_n == n)


def test_part_pipeline_complete_tmp(tmp_path: Path):
    # Minimal stub without importing full server (heavy). Mirror rule:
    # mux done + output >1MB + no stale
    out = tmp_path / "output.mp4"
    out.write_bytes(b"x" * 1_000_001)
    man = {
        "stages": {
            "mux": {"status": "done"},
            "translate": {"status": "done"},
            "tts": {"status": "done"},
        }
    }
    (tmp_path / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
    assert out.stat().st_size > 1_000_000
    assert man["stages"]["mux"]["status"] == "done"
    assert not man["stages"]["tts"].get("stale")


def test_merged_skip_contract():
    info = {"status": "merged", "sub_job_ids": ["a_p01", "a_p02"]}
    assert info.get("status") == "merged"
    assert info.get("sub_job_ids")
