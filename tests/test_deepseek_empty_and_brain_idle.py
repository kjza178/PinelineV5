"""2026-11-18: DeepSeek 200 + content rỗng → lỗi rõ ràng, không lặp cloud_retry; A7 length → x2 max_tokens;
brain không quét QA khi chưa dịch xong."""
import json
import os

import pytest

import engines.cloud_retry as cloud_retry
import engines.llm as llm


class _R:
    def __init__(self, data, status=200):
        self._d, self.status_code, self.text = data, status, json.dumps(data)

    def json(self):
        return self._d

    def raise_for_status(self):
        pass


def _ds(monkeypatch, responses):
    calls = []
    monkeypatch.setattr(llm, "_deepseek_settings", lambda: ("http://x", "k", "deepseek-flash"))
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)

    def post(url, headers=None, json=None, timeout=None):
        calls.append(dict(json))
        return _R(responses[min(len(calls) - 1, len(responses) - 1)])
    monkeypatch.setattr(llm.requests, "post", post)
    return calls


def _empty(fin="stop"):
    return {"choices": [{"message": {"content": ""}, "finish_reason": fin}],
            "usage": {"prompt_tokens": 50000, "completion_tokens": 8192}}


def test_empty_twice_raises_clear_error_no_none(monkeypatch):
    calls = _ds(monkeypatch, [_empty()])
    with pytest.raises(llm.LLMEmptyResponse) as ei:
        llm._deepseek_chat("deepseek-flash", [{"role": "user", "content": "x"}], 0.1, 100, True, 4, 10)
    assert len(calls) == 2 and "response_format" in calls[0] and "response_format" not in calls[1]
    msg = str(ei.value)
    assert "None" not in msg and "finish_reason=stop" in msg and "prompt_tokens=50000" in msg
    assert cloud_retry.classify_cloud_retry(ei.value) is None


def test_length_raises_immediately(monkeypatch):
    calls = _ds(monkeypatch, [_empty("length")])
    with pytest.raises(llm.LLMEmptyResponse) as ei:
        llm._deepseek_chat("deepseek-flash", [{"role": "user", "content": "x"}], 0.1, 100, True, 4, 10)
    assert len(calls) == 1 and ei.value.finish_reason == "length" and "max_tokens" in str(ei.value)


def test_empty_then_ok(monkeypatch):
    _ds(monkeypatch, [_empty(), {"choices": [{"message": {"content": "{\"a\":1}"}}]}])
    assert llm._deepseek_chat("deepseek-flash", [{"role": "user", "content": "x"}], 0.1, 100, True, 4, 10) == '{"a":1}'


def test_exhausted_network_still_transient():
    assert cloud_retry.classify_cloud_retry(llm.LLMUnavailable("DeepSeek (x) thất bại sau 4 lần: timeout")) == "transient"


def test_a7_length_doubles_max_tokens(monkeypatch, tmp_path):
    from engines.translate_simple import stage_draft
    seen = []

    def fake_chat(msgs, model=None, max_tokens=None, **k):
        seen.append(max_tokens)
        if len(seen) == 1:
            raise llm.LLMEmptyResponse("rỗng", finish_reason="length")
        return json.dumps({"characters": [{"name": "A"}], "terms": [], "pronouns": []})
    monkeypatch.setattr(llm, "chat", fake_chat)
    segs = [{"text": f"台词{i}"} for i in range(30)]
    plan = stage_draft.build_full_movie_plan(tmp_path, segs, model="deepseek-flash")
    assert plan and plan["characters"] and seen[1] == 2 * seen[0]


def test_brain_skips_qual_when_not_translated(tmp_path, monkeypatch):
    try:
        import agents.agent_brain as ab
    except ImportError:
        import agents.agent_brain as ab
    wd = tmp_path / "j1"
    wd.mkdir()
    (wd / "manifest.json").write_text(json.dumps({"job_id": "j1", "agent": {},
                                                  "stages": {"translate": {"status": "running"}}}), encoding="utf-8")
    (wd / "script.json").write_text(json.dumps([{"i": 0, "zh": "你好", "vi": ""}]), encoding="utf-8")
    ph = ab._qa_pipeline_phase(wd)
    assert ph["phase"] == "idle" and not ph.get("held")


def test_thinking_disabled_by_default_and_env_enable(monkeypatch):
    monkeypatch.setattr(llm, "_cfg_get", lambda k, *a, **kw: None)
    os.environ.pop("DEEPSEEK_THINKING", None)
    calls = _ds(monkeypatch, [{"choices": [{"message": {"content": "ok"}}]}])
    llm._deepseek_chat("deepseek-flash", [{"role": "user", "content": "x"}], 0.1, 100, False, 1, 10)
    assert calls[-1]["thinking"] == {"type": "disabled"} and calls[-1]["max_tokens"] == 100
    monkeypatch.setenv("DEEPSEEK_THINKING", "enabled")
    llm._deepseek_chat("deepseek-flash", [{"role": "user", "content": "x"}], 0.1, 100, False, 1, 10)
    assert calls[-1]["thinking"] == {"type": "enabled"} and calls[-1]["max_tokens"] == 100 + 8192
