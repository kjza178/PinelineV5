"""2026-11-16: Hongguo classic (HTTP :8000) đã bỏ — mọi namespace/UI chạy RPC (hongguo2). HG_CLASSIC=1 = quay lại."""
import agents.hg_ui_ctx as ctx


def test_classic_namespace_forced_to_rpc(monkeypatch):
    monkeypatch.delenv("HG_CLASSIC", raising=False)
    monkeypatch.setattr(ctx, "classic_enabled", lambda: False)
    assert ctx.force("http") == "rpc"
    assert ctx.apply("1") == "rpc"
    assert ctx.apply(None, "http://127.0.0.1/hongguo") == "rpc"
    assert ctx.apply("2") == "rpc"
    assert ctx.force("auto") == "auto"


def test_classic_rollback_flag(monkeypatch):
    monkeypatch.setenv("HG_CLASSIC", "1")
    assert ctx.classic_enabled() is True
    assert ctx.force("http") == "http"
    assert ctx.apply("classic") == "http"
    assert ctx.apply("hongguo2") == "rpc"
