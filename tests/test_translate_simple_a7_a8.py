from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from engines.translate_simple import cfg, plan_view, stage_draft, stage_review
from engines.translate_simple.plan_view import PlanView
from engines.translate_simple.script_store import ScriptStore


def test_cfg_a7_a8_defaults():
    assert cfg.full_plan_enabled() is True
    assert cfg.overlap_cues() == 3
    assert cfg.plan_model() is not None


def test_plan_view_header_summary_first():
    pv = PlanView({
        "summary": "Đây là câu chuyện về chàng trai tu tiên bảo vệ gia đình.",
        "genre": "Tu tiên",
        "tone": "Kịch tính",
    })
    headers = pv.header_lines()
    assert len(headers) >= 2
    assert headers[0].startswith("TÓM TẮT PHIM: Đây là câu chuyện về chàng trai")
    assert "thể loại: Tu tiên" in headers[1]


def test_make_jobs_with_overlap():
    rows = [
        {"i": idx, "zh": f"câu {idx}", "vi": f"bản dịch {idx}", "start": idx, "end": idx + 1}
        for idx in range(20)
    ]
    todo = list(range(20))
    # batch=5, ctx=2, overlap=3
    jobs = stage_review.make_jobs(rows, todo, batch=5, ctx=2, overlap=3)
    assert len(jobs) == 4

    # Job 0: pos 0..4, không có câu trước
    assert jobs[0]["pos"] == [0, 1, 2, 3, 4]
    assert jobs[0]["before"] == []
    assert len(jobs[0]["after"]) == 2

    # Job 1: pos 5..9, before lấy max(ctx=2, overlap=3) = 3 câu liền trước (2, 3, 4)
    assert jobs[1]["pos"] == [5, 6, 7, 8, 9]
    assert [r["i"] for r in jobs[1]["before"]] == [2, 3, 4]
    assert jobs[1]["overlap"] == 3


def test_build_prompt_overlap_labels():
    rows = [{"i": 10, "zh": "你好", "vi": "Chào bạn", "start": 10, "end": 11}]
    before = [{"i": 9, "zh": "早安", "vi": "Chào buổi sáng", "start": 9, "end": 10}]
    after = [{"i": 11, "zh": "再见", "vi": "", "start": 11, "end": 12}]
    pv = PlanView({"summary": "Tóm tắt mẫu", "characters": []})

    sys, user = stage_review.build_prompt(rows, before, after, pv)
    assert "TÓM TẮT PHIM: Tóm tắt mẫu" in user
    assert "NGỮ CẢNH TRƯỚC (CHỒNG LẤN · chỉ đọc · i | zh | vi):" in user
    assert "9 | 早安 | Chào buổi sáng" in user
    assert "NGỮ CẢNH SAU (NHÌN TRƯỚC · chỉ đọc · i | zh | nháp):" in user


def test_build_full_movie_plan_sampling(tmp_path: Path):
    # Test khi số ký tự > 26000 thì hàm tự lấy mẫu dày đều
    long_segs = [{"i": idx, "text": f"Đây là câu thoại dài số {idx} với rất nhiều chữ Hán 测试中文"} for idx in range(1000)]
    
    with patch("llm.chat") as mock_chat:
        mock_chat.return_value = json.dumps({
            "summary": "Phim võ hiệp tu tiên",
            "characters": [{"zh": "林凡", "vi": "Lâm Phàm", "role": "Nhân vật chính"}],
            "pronouns": [{"who": "Lâm Phàm", "to": "Sư phụ", "self": "đệ tử", "call": "sư phụ"}],
            "terms": [{"zh": "天宫", "vi": "Thiên Cung"}]
        })
        plan = stage_draft.build_full_movie_plan(tmp_path, long_segs, target="Tiếng Việt", model="dummy")
        assert plan is not None
        assert plan["plan_status"] == "ok"
        assert plan["plan_source"] == "full_movie_asr"
        assert plan["summary"] == "Phim võ hiệp tu tiên"
        assert len(plan["characters"]) == 1


def test_decode_handles_escape_tags_and_pairs():
    raw = (
        '{\n'
        '  "pairs": [\n'
        '    {\n'
        '      "who": "Chị Ba",\n'
        '      "to": "Lâm Phàm",\n'
        '      "self": "chị",\n'
        '      "call": "em",\n'
        '      "conf": 0.9,\n'
        '      "note": "tạo quan hệ chị-em"\n'
        '    }\n'
        '  ]\n'
        '}</escape>'
    )
    data = stage_review._decode(raw)
    assert isinstance(data, dict)
    assert len(data.get("pairs")) == 1
    assert data["pairs"][0]["who"] == "Chị Ba"
