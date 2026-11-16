import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
import engines.translate as translate


def test_translate_batch_raises_on_dropped_lines():
    """
    Test that if LLM drops sentences from a batch (e.g. returns 1 item instead of 5),
    translate_batch raises ValueError so _translate_safe can divide and conquer.
    """
    rows = [
        {"i": 1, "sec": 2.0, "text": "你好"},
        {"i": 2, "sec": 2.0, "text": "世界"},
        {"i": 3, "sec": 2.0, "text": "再见"},
        {"i": 4, "sec": 2.0, "text": "明天见"},
        {"i": 5, "sec": 2.0, "text": "早上好"},
    ]
    # LLM drops items 2, 3, 4, 5 and only returns item 1
    fake_llm_out = json.dumps({"items": [{"i": 1, "vi": "Xin chào"}]})
    
    with patch("translate.chat", return_value=fake_llm_out):
        with pytest.raises(ValueError, match="LLM bỏ sót"):
            translate.translate_batch(rows, plan_block="", prev_ctx=[])


def test_translate_safe_splits_and_recovers_when_dropped():
    """
    Test that _translate_safe catches dropped lines and subdivides until full recovery.
    """
    rows = [
        {"i": 1, "sec": 2.0, "text": "你好"},
        {"i": 2, "sec": 2.0, "text": "世界"},
        {"i": 3, "sec": 2.0, "text": "再见"},
        {"i": 4, "sec": 2.0, "text": "明天见"},
    ]

    def mock_chat(messages, model=None, **kwargs):
        content = messages[1]["content"]
        # If batch contains all 4 items, simulate LLM dropping items 3 and 4
        if '"i": 4' in content and '"i": 1' in content:
            return json.dumps({"items": [{"i": 1, "vi": "Xin chào"}, {"i": 2, "vi": "Thế giới"}]})
        # If sub-batch of 2 items [1, 2], return both
        if '"i": 1' in content:
            return json.dumps({"items": [{"i": 1, "vi": "Xin chào"}, {"i": 2, "vi": "Thế giới"}]})
        # If sub-batch of 2 items [3, 4], return both
        if '"i": 3' in content:
            return json.dumps({"items": [{"i": 3, "vi": "Tạm biệt"}, {"i": 4, "vi": "Hẹn gặp lại mai"}]})
        return "{}"

    with patch("translate.chat", side_effect=mock_chat):
        res = translate._translate_safe(rows, plan_block="", prev_ctx=[], target="Tiếng Việt", model=None)
        assert len(res) == 4
        assert res[1] == "Xin chào"
        assert res[2] == "Thế giới"
        assert res[3] == "Tạm biệt"
        assert res[4] == "Hẹn gặp lại mai"


def test_run_review_auto_fills_missing_before_review(tmp_path):
    """
    Test that run_review automatically fills missing rows if script.json has empty lines.
    """
    script_rows = [
        {"i": 0, "start": 0.0, "end": 2.0, "zh": "你好", "vi": "Xin chào", "rv": 1},
        {"i": 1, "start": 2.0, "end": 4.0, "zh": "世界", "vi": ""}, # missing
    ]
    script_file = tmp_path / "script.json"
    script_file.write_text(json.dumps(script_rows, ensure_ascii=False), encoding="utf-8")

    manifest_file = tmp_path / "manifest.json"
    manifest_file.write_text(json.dumps({"stages": {"translate": {"status": "done"}}}, ensure_ascii=False), encoding="utf-8")

    with patch("translate._cfg_get", return_value="0"), \
         patch("translate._translate_safe", return_value={1: "Thế giới"}), \
         patch("translate.review_batch", return_value={}):

        res = translate.run_review(tmp_path, batch=20)
        updated_rows = json.loads(script_file.read_text(encoding="utf-8"))
        assert updated_rows[1]["vi"] == "Thế giới"
        assert res.get("n_missing") == 0
