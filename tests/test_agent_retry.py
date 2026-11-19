"""2026-11-18: Agent chat — không fallback, nhưng thử lại cùng model khi lỗi tạm (Aurora 500 …)."""
import pytest

try:
    import agents.agent_core as ac  # V5
except ImportError:
    import agents.agent_core as ac


def _setup(monkeypatch, errors):
    calls = []

    def fake(messages, use_tools, model, tool_choice="auto"):
        calls.append(model)
        if errors:
            raise errors.pop(0)
        return {"content": "ok"}
    monkeypatch.setattr(ac, "_chat_turn_model", fake)
    monkeypatch.setattr(ac.time, "sleep", lambda s: None)
    monkeypatch.setenv("AGENT_RETRIES", "2")
    import core.config as config
    monkeypatch.setattr(config, "agent_llm", lambda: {"model": "chatgpt/gpt-5-6-mini", "fallback": "", "base": "x",
                                                       "key": "k"})
    return calls


def test_retry_on_aurora_stream_500(monkeypatch):
    calls = _setup(monkeypatch, [RuntimeError('LLM HTTP 500: {"error":"Error in message stream"}')])
    assert ac._chat_turn([{"role": "user", "content": "hi"}]) == {"content": "ok"}
    assert calls == ["chatgpt/gpt-5-6-mini"] * 2


def test_no_retry_on_4xx_and_gives_up(monkeypatch):
    calls = _setup(monkeypatch, [RuntimeError("LLM HTTP 400: bad tool")])
    with pytest.raises(RuntimeError):
        ac._chat_turn([{"role": "user", "content": "hi"}])
    assert len(calls) == 1
    calls = _setup(monkeypatch, [RuntimeError("LLM HTTP 502: x")] * 5)
    with pytest.raises(RuntimeError):
        ac._chat_turn([{"role": "user", "content": "hi"}])
    assert len(calls) == 3
