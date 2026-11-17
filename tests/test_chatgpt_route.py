"""Route chatgpt/aurora trong llm.chat + pass_llm_model."""
from __future__ import annotations

import core.config as config
import engines.llm as llm


def test_is_chatgpt_prefix():
    assert llm.is_chatgpt("chatgpt/gpt-5-6-mini")
    assert llm.is_chatgpt("aurora/auto")
    assert not llm.is_chatgpt("local")
    assert not llm.is_chatgpt("gpt-5-6-mini")  # thiếu tiền tố → không tự nhảy Aurora


def test_pass_llm_model_prefers_name_pronoun(monkeypatch):
    monkeypatch.setitem(config._CFG, "NAME_MODEL", "chatgpt/gpt-5-6-mini")
    monkeypatch.setitem(config._CFG, "PRONOUN_MODEL", "chatgpt/gpt-5-6")
    monkeypatch.setitem(config._CFG, "CHATGPT_MODEL", "gpt-4o")
    assert config.pass_llm_model("name") == "chatgpt/gpt-5-6-mini"
    assert config.pass_llm_model("pronoun") == "chatgpt/gpt-5-6"


def test_pass_llm_model_falls_back_chatgpt(monkeypatch):
    monkeypatch.setitem(config._CFG, "NAME_MODEL", "")
    monkeypatch.setitem(config._CFG, "PRONOUN_MODEL", "")
    monkeypatch.setitem(config._CFG, "CHATGPT_MODEL", "gpt-5-6-mini")
    assert config.pass_llm_model("name") == "chatgpt/gpt-5-6-mini"


def test_is_alibaba_prefix():
    assert llm.is_alibaba("alibaba/qwen-max")
    assert llm.is_alibaba("qwen/qwen-plus")
    assert llm.is_alibaba("dashscope/qwen3-235b-a22b")
    assert not llm.is_alibaba("chatgpt/gpt-5-6-mini")
    assert not llm.is_alibaba("ollama/gemma4:31b-cloud")


def test_chatgpt_chat_fallback_on_conn_refused_and_retry_400_pool(monkeypatch):
    import requests
    # 2026-11-17: không còn IP LAN mặc định (AURORA_FALLBACK_URLS=off) — test tự đặt 1 fallback giả
    monkeypatch.setenv("AURORA_FALLBACK_URLS", "http://10.255.0.9:5005/v1")
    llm._DEAD_BASES.clear()
    calls = []

    class FakeResp:
        def __init__(self, status_code: int, text: str = "", json_data: dict | None = None):
            self.status_code = status_code
            self.text = text
            self._json = json_data or {}

        def json(self):
            return self._json

        def raise_for_status(self):
            if self.status_code >= 400:
                raise requests.HTTPError(f"{self.status_code} {self.text}", response=self)

    def fake_post(url, headers=None, json=None, timeout=None):
        calls.append(url)
        if "127.0.0.1:3377" in url:
            raise requests.ConnectionError("[WinError 10061] Actively refused")
        if len([u for u in calls if "10.255.0.9" in u]) == 1:
            return FakeResp(400, '{"error":{"message":"no available account of the requested type"}}')
        return FakeResp(200, "", {"choices": [{"message": {"content": '{"lines":[]}'}}]})

    monkeypatch.setattr(llm.requests, "post", fake_post)
    monkeypatch.setattr(llm.time, "sleep", lambda _s: None)
    out = llm._chatgpt_chat("chatgpt/gpt-5-6-mini", [{"role": "user", "content": "hi"}], 0.1, 100, True, 3, 30)
    assert out == '{"lines":[]}'
    # :3377 chỉ bị gọi đúng 1 lần rồi chuyển ngay sang .247 (không tốn 3 lần retry trên port đóng)
    assert calls.count("http://127.0.0.1:3377/v1/chat/completions") == 1
    assert calls.count("http://10.255.0.9:5005/v1/chat/completions") == 2


def test_decode_aurora_image_rejects_echoed_ref():
    import base64
    import io
    from PIL import Image
    import agents.meta_studio as meta_studio

    im_ref = Image.new("RGB", (400, 534), (100, 50, 50))
    buf_ref = io.BytesIO()
    im_ref.save(buf_ref, format="JPEG")
    ref_bytes = buf_ref.getvalue()

    echo_resp = {"data": [{"b64_json": base64.b64encode(ref_bytes).decode("ascii")}]}
    assert meta_studio._decode_aurora_image_response(echo_resp, reject_list=[ref_bytes]) is None

    im_gen = Image.new("RGB", (1672, 941), (20, 120, 200))
    buf_gen = io.BytesIO()
    im_gen.save(buf_gen, format="PNG")
    gen_bytes = buf_gen.getvalue()

    valid_resp = {"data": [{"b64_json": base64.b64encode(gen_bytes).decode("ascii")}]}
    assert meta_studio._decode_aurora_image_response(valid_resp, reject_list=[ref_bytes]) == gen_bytes

