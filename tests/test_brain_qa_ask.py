"""2026-11-17 qaask: HOLD QA hỏi người qua Telegram (chi tiết + đề xuất + nút/reply) + xử lý quá hạn."""
import json
import time

import pytest

try:
    import agents.agent_brain as ab  # V5
    import agents.agent_qa_ask as qa
    import agents.agent_quality as aq
except ImportError:
    import agents.agent_brain as ab
    import agents.agent_qa_ask as qa
    import agents.agent_quality as aq


def _fake_scan(rows):
    out = []
    for r in rows:
        for k in r.get("bad") or []:
            if k in (r.get("qa_ack") or []):
                continue
            if k == "empty_vi" and (r.get("vi") or "").strip():
                continue
            out.append({"i": r["i"], "sev": "high", "kind": k, "note": f"lỗi {k}"})
    return out


@pytest.fixture
def job(tmp_path, monkeypatch):
    monkeypatch.setattr(aq, "scan_script", _fake_scan)
    monkeypatch.setattr(aq, "write_qa_brain", lambda wd, flags, **k: {})
    monkeypatch.setattr(ab, "_telegram", lambda *a, **k: None)
    monkeypatch.setattr(ab, "_emit", lambda *a, **k: None)
    monkeypatch.setattr(qa, "send", lambda *a, **k: 0)
    monkeypatch.setenv("QA_HOLD_MAX_MIN", "1")
    wd = tmp_path / "j1"
    wd.mkdir()
    (wd / "manifest.json").write_text(json.dumps({
        "job_id": "j1", "agent": {"qa_blocked": True, "held_at": "qa_brain"},
        "stages": {"translate": {"status": "done"}, "tts": {"status": "pending"}},
    }), encoding="utf-8")
    return wd


def _script(wd, rows):
    (wd / "script.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")


def _rows(wd):
    return {r["i"]: r for r in json.loads((wd / "script.json").read_text(encoding="utf-8"))}


def _props(monkeypatch, table):
    def fake(items):
        for it in items:
            p = table.get(it["i"])
            if p:
                it.update(p)
        return []
    monkeypatch.setattr(qa, "propose", fake)


def _run(st, hooks, tmp_path, wd, r, *, expire=False):
    if expire:
        st["qa_hold"]["j1"]["since"] = time.time() - 120
    ab._qa_hold_timeout(st, hooks, tmp_path, wd, "j1", r)


R = {"high_i": [1, 2]}


def test_ask_created_with_details(job, tmp_path, monkeypatch):
    _script(job, [{"i": 1, "zh": "你好", "vi": "chào chào", "bad": ["stutter"]},
                  {"i": 2, "zh": "走吧", "vi": "", "bad": ["empty_vi"]}])
    _props(monkeypatch, {1: {"prop_verdict": "fix", "prop_vi": "Chào", "prop_why": "lặp", "prop_conf": 0.9},
                         2: {"prop_verdict": "fix", "prop_vi": "Đi thôi", "prop_why": "trống", "prop_conf": 0.5}})
    st = {}
    _run(st, {}, tmp_path, job, R)
    ask = qa.load_ask(job)
    assert ask["sig"] == "1,2" and len(ask["items"]) == 2
    txt = qa.render_text(ask)
    assert "#1" in txt and "ZH: 你好" in txt and "Đề xuất (0.90): Chào" in txt and qa.MARK in txt
    assert "CỨNG" in txt and "mềm" in txt


def test_timeout_soft_and_sure_hard_applied_then_resume(job, tmp_path, monkeypatch):
    _script(job, [{"i": 1, "zh": "你好", "vi": "chào chào", "bad": ["stutter"]},
                  {"i": 2, "zh": "走吧", "vi": "", "bad": ["empty_vi"]}])
    _props(monkeypatch, {1: {"prop_verdict": "fix", "prop_vi": "Chào", "prop_why": "lặp", "prop_conf": 0.3},
                         2: {"prop_verdict": "fix", "prop_vi": "Đi thôi", "prop_why": "trống", "prop_conf": 0.95}})
    calls, st = [], {}
    hooks = {"resume": lambda j: calls.append(j) or {"ok": True}, "defer": lambda j: pytest.fail("defer")}
    _run(st, hooks, tmp_path, job, R)
    _run(st, hooks, tmp_path, job, R)
    assert calls == []
    _run(st, hooks, tmp_path, job, R, expire=True)
    assert calls == ["j1"]
    rows = _rows(job)
    assert rows[1]["vi"] == "Chào" and rows[2]["vi"] == "Đi thôi"
    assert _fake_scan(list(rows.values())) == []
    assert qa.load_ask(job)["status"] == "resolved"


def test_timeout_hard_unsure_defers_and_reminds(job, tmp_path, monkeypatch):
    _script(job, [{"i": 1, "zh": "你好", "vi": "chào chào", "bad": ["stutter"]},
                  {"i": 2, "zh": "走吧", "vi": "đi", "bad": ["vi_pattern"]}])
    _props(monkeypatch, {1: {"prop_verdict": "false_positive", "prop_vi": "", "prop_why": "ok", "prop_conf": 0.6},
                         2: {"prop_verdict": "fix", "prop_vi": "Đi thôi", "prop_why": "?", "prop_conf": 0.5}})
    calls, defers, sent, st = [], [], [], {}
    def fake_send(wr, wd, ask, text, **k):
        sent.append(text)
        ask.setdefault("msgs", []).append({"chat_id": "1", "message_id": len(sent)})
        qa.save_ask(wd, ask)
        return 1
    monkeypatch.setattr(qa, "send", fake_send)
    hooks = {"resume": lambda j: calls.append(j), "defer": lambda j: defers.append(j) or {"ids": [j]}}
    _run(st, hooks, tmp_path, job, R)
    assert len(sent) == 1
    _run(st, hooks, tmp_path, job, R, expire=True)
    assert calls == [] and defers == ["j1"]
    ask = qa.load_ask(job)
    assert ask["status"] == "deferred" and [it["i"] for it in qa.open_items(ask)] == [2]
    assert "stutter" in _rows(job)[1]["qa_ack"]            # mềm đã xử lý
    assert json.loads((job / "manifest.json").read_text(encoding="utf-8"))["agent"]["qa_deferred"]["left"] == [2]
    _run(st, hooks, tmp_path, job, R)                        # chưa tới giờ nhắc
    assert len(sent) == 1 and defers == ["j1"]
    ask["reminded_at"] = 0
    qa.save_ask(job, ask)
    _run(st, hooks, tmp_path, job, R)
    assert len(sent) == 2 and "Nhắc" in sent[-1] and defers == ["j1"]


def test_answer_buttons_and_reply(job, tmp_path, monkeypatch):
    _script(job, [{"i": 1, "zh": "你好", "vi": "chào chào", "bad": ["vi_pattern"]},
                  {"i": 2, "zh": "走吧", "vi": "đi", "bad": ["calque"]}])
    _props(monkeypatch, {1: {"prop_verdict": "fix", "prop_vi": "Chào", "prop_why": "lặp", "prop_conf": 0.5}})
    qa.create_ask(job, "j1", "1,2")
    r = qa.answer(tmp_path, job_id="j1", text="câu mới")       # 2 câu mở, không số → hỏi lại
    assert not r["ok"] and "#1" in r["error"]
    r = qa.answer(tmp_path, job_id="j1", text="#2: Đi nào")
    assert r["ok"] and not r["release"] and r["left"] == 1
    rows = _rows(job)
    assert rows[2]["vi"] == "Đi nào" and rows[2]["manual"] == 1 and "calque" in rows[2]["qa_ack"]
    r = qa.answer(tmp_path, job_id="j1", action="apply")
    assert r["release"] and _rows(job)[1]["vi"] == "Chào"
    assert qa.answer(tmp_path, job_id="j1", action="go")["release"] is False


def test_skip_keeps_vi_but_empty_vi_stays_open(job, tmp_path, monkeypatch):
    _script(job, [{"i": 1, "zh": "你好", "vi": "xin chào", "bad": ["vi_pattern"]},
                  {"i": 2, "zh": "走吧", "vi": "", "bad": ["empty_vi"]}])
    _props(monkeypatch, {})
    qa.create_ask(job, "j1", "1,2")
    r = qa.answer(tmp_path, job_id="j1", action="skip")
    assert r["left"] == 1 and not r["release"] and _rows(job)[1]["vi"] == "xin chào"
    r = qa.answer(tmp_path, job_id="j1", text="Đi thôi")       # còn 1 câu → cả tin là câu mới
    assert r["release"] and _rows(job)[2]["vi"] == "Đi thôi"


def test_reply_lookup_by_message(job, tmp_path, monkeypatch):
    _script(job, [{"i": 7, "zh": "走", "vi": "", "bad": ["empty_vi"]}])
    _props(monkeypatch, {})
    qa.create_ask(job, "j1", "7")
    qa._index_add(tmp_path, "42", 555, "j1")
    assert qa.answer(tmp_path, chat_id="42", reply_to=999, text="x") == {"ok": True, "matched": False}
    r = qa.answer(tmp_path, chat_id="42", reply_to=555, text="Đi")
    assert r["release"] and r["job_id"] == "j1"


def test_parse_reply_formats():
    its = [{"i": 3}, {"i": 12}]
    assert qa.parse_reply("#3: A\n12. B\n99: C", its) == {3: "A", 12: "B"}
    assert qa.parse_reply("chỉ một câu", [{"i": 5}]) == {5: "chỉ một câu"}


def test_not_held_closes_open_ask(job, tmp_path, monkeypatch):
    _script(job, [{"i": 1, "zh": "你好", "vi": "", "bad": ["empty_vi"]}])
    _props(monkeypatch, {})
    st = {}
    _run(st, {}, tmp_path, job, {"high_i": [1]})
    assert qa.load_ask(job)["status"] == "open"
    (job / "manifest.json").write_text(json.dumps({"job_id": "j1", "agent": {}}), encoding="utf-8")
    _run(st, {}, tmp_path, job, {"high_i": [1]})
    assert qa.load_ask(job)["status"] == "closed"


# --- 2026-11-17 qaask2: «?» ngữ cảnh, /qa <job>, agent sửa câu ---------------------------
def _ten_rows():
    rows = [{"i": k, "zh": f"中{k}", "vi": f"câu {k}"} for k in range(10)]
    rows[5]["bad"] = ["vi_pattern"]
    return rows


def test_context_query_patterns():
    assert qa.is_context_query("?") and qa.is_context_query("#380 ?") and qa.is_context_query("12? 13?")
    assert not qa.is_context_query("#380: câu mới?") and not qa.is_context_query("Đi đâu?")
    assert qa.context_nums("#4 ? #7?", [{"i": 1}]) == [4, 7]
    assert qa.context_nums("?", [{"i": 1}, {"i": 2}]) == [1, 2]


def test_reply_question_mark_returns_context_no_change(job, tmp_path, monkeypatch):
    _script(job, _ten_rows())
    _props(monkeypatch, {})
    qa.create_ask(job, "j1", "5")
    r = qa.answer(tmp_path, job_id="j1", text="?")
    assert r["ok"] and r["context"] and not r["release"]
    msg = r["message"]
    assert "▶#5" in msg and "#2 ZH: 中2" in msg and "#8 ZH: 中8" in msg and "#1 " not in msg and "#9 " not in msg
    assert qa.load_ask(job)["status"] == "open" and _rows(job)[5]["vi"] == "câu 5"


def test_qa_show_creates_ask_and_prefix(job, tmp_path, monkeypatch):
    _script(job, _ten_rows())
    _props(monkeypatch, {5: {"prop_verdict": "fix", "prop_vi": "Câu năm", "prop_why": "x", "prop_conf": 0.7}})
    assert not qa.show(tmp_path, "zz")["ok"]
    d = qa.show(tmp_path, "j1")
    assert d["ok"] and d["held"] and "#5" in d["text"] and "Câu năm" in d["text"]
    assert d["keyboard"]["inline_keyboard"][0][0]["callback_data"] == "qa:apply:j1"
    assert qa.load_ask(job)["sig"] == "5"
    (job / "manifest.json").write_text(json.dumps({"job_id": "j1", "agent": {}}), encoding="utf-8")
    assert "KHÔNG bị HOLD" in qa.show(tmp_path, "j1")["text"]


def test_qa_show_no_flags(job, tmp_path, monkeypatch):
    _script(job, [{"i": 1, "zh": "a", "vi": "b"}])
    d = qa.show(tmp_path, "j1")
    assert d["ok"] and d.get("empty")


def test_agent_edit_marks_done_and_releases(job, tmp_path, monkeypatch):
    rows = _ten_rows()
    rows[7]["bad"] = ["calque"]
    _script(job, rows)
    _props(monkeypatch, {})
    qa.create_ask(job, "j1", "5,7")
    fl = qa.flags_for_agent(tmp_path, "j1")
    assert fl["source"] == "qa_ask" and [x["i"] for x in fl["items"]] == [5, 7]
    r = qa.mark_edited(job, [5])
    assert r["acked"] == 1 and r["left"] == 1 and not r["release"]
    assert "vi_pattern" in _rows(job)[5]["qa_ack"]
    r = qa.mark_edited(job, [7])
    assert r["release"] and qa.load_ask(job)["status"] == "resolved"
    assert _fake_scan(list(_rows(job).values())) == []


def test_agent_core_edit_hook_calls_release(job, tmp_path, monkeypatch):
    try:
        import agents.agent_core as ac
    except ImportError:
        import agents.agent_core as ac
    _script(job, _ten_rows())
    _props(monkeypatch, {})
    qa.create_ask(job, "j1", "5")
    calls = []

    class RT:
        work_root = tmp_path
        heal_hooks = {"qa_release": lambda jid, ids: calls.append((jid, ids)) or {"ok": True}}
    r = ac._qa_after_edit(RT, "j1", [5])
    assert r["release"] and calls == [("j1", [])]
    assert ac._edit_ok({"ok": True}) and not ac._edit_ok({"error": "x"})
