"""fix 2026-11-18: job/part mới bị server đánh translate=running TRƯỚC khi hỏi luồng → không được suy «legacy»
(c7367a659c46_p01 chạy luồng cũ + upload Aurora)."""
import json

try:
    from engines.translate_simple import cfg  # V5
except ImportError:
    from translate_simple import cfg


def _wd(tmp_path, man, script=None):
    wd = tmp_path / "j"
    wd.mkdir()
    (wd / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
    if script is not None:
        (wd / "script.json").write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
    return wd


def test_running_mark_without_vi_is_not_legacy(tmp_path):
    wd = _wd(tmp_path, {"stages": {"translate": {"status": "running", "started_at": "2026-11-18T11:00:12",
                                                 "mode": "batch"}}})
    assert cfg._infer_job_pipeline(json.loads((wd / "manifest.json").read_text()), wd) is None


def test_zh_only_script_is_not_legacy(tmp_path):
    wd = _wd(tmp_path, {"stages": {"translate": {"status": "running"}}}, script=[{"i": 0, "zh": "你好", "vi": ""}])
    assert cfg._infer_job_pipeline({"stages": {"translate": {"status": "running"}}}, wd) is None


def test_real_legacy_traces_still_legacy(tmp_path):
    wd = _wd(tmp_path, {"stages": {}}, script=[{"i": 0, "zh": "你好", "vi": "xin chào"}])
    assert cfg._infer_job_pipeline({"stages": {"translate": {"status": "pending"}}}, wd) == cfg.PIPELINE_LEGACY
    wd2 = tmp_path / "k"
    wd2.mkdir()
    assert cfg._infer_job_pipeline({"stages": {"translate": {"status": "failed"}}}, wd2) == cfg.PIPELINE_LEGACY
    assert cfg._infer_job_pipeline({"stages": {"translate": {"status": "done", "mode": "simple"}}}, wd2) \
        == cfg.PIPELINE_SIMPLE
