"""2026-11-18: soát bổ sung (_review_missing) — ≤5 câu lô nhỏ (4), nhiều câu (vd 81 câu OCR lượt B) lô thường."""
import os

try:
    from engines.translate_simple import cfg  # V5
except ImportError:
    from translate_simple import cfg


def test_small_left_uses_small_batch(monkeypatch):
    for k in ("SIMPLE_MISSING_BATCH", "SIMPLE_MISSING_SMALL_MAX", "SIMPLE_BATCH"):
        os.environ.pop(k, None)
    monkeypatch.setattr(cfg, "get", lambda k, d=None: d)
    assert cfg.missing_batch_for(1) == 4
    assert cfg.missing_batch_for(5) == 4


def test_many_left_uses_normal_batch(monkeypatch):
    monkeypatch.setattr(cfg, "get", lambda k, d=None: d)
    assert cfg.missing_batch_for(81) == cfg.batch() == 30
    assert -(-81 // cfg.missing_batch_for(81)) == 3          # 81 câu → 3 lô (trước 21 lô × 4)
