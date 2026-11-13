"""Cấu hình luồng simple — mọi khoá prefix SIMPLE_ đọc qua config.get (env > pineline.config.json > mặc định).

Không sửa config.json. Khoá:
  TRANSLATE_PIPELINE       V5: trống/simple = luồng này (MẶC ĐỊNH); legacy = luồng cũ (rollback)
  SIMPLE_MODEL             model REVIEW cloud (trống = REVIEW model như luồng cũ: _resolve_review_model)
  SIMPLE_BATCH             số câu / lô review (30)
  SIMPLE_CTX               số câu ngữ cảnh chỉ đọc mỗi phía lô (4)
  SIMPLE_WORKERS           số lô gọi song song (8)
  SIMPLE_REPAIR_ROUNDS     số lượt vá câu bị cờ (2, tối đa 2)
  SIMPLE_CONF_MIN          ngưỡng conf (độ chắc spk/to) để kiểm xưng hô (0.7)
  SIMPLE_GATE_FLAG_RATIO   tỉ lệ câu còn cờ tối đa để qua cổng (0.03)
  SIMPLE_GATE_FLAG_MAX     số câu còn cờ tối đa tuyệt đối (trống = chỉ dùng tỉ lệ; tối thiểu 1)
  SIMPLE_MAX_TOKENS        max_tokens mỗi lần gọi (8192)
  SIMPLE_TIMEOUT           timeout giây mỗi lần gọi (300)
  SIMPLE_TEMPERATURE       (0.2)
  SIMPLE_PRONOUN_ANALYZE   1 = chạy pronoun_consistency.ensure_analyze_before_translate sau plan (0)
  SIMPLE_NMT_WAIT_PLAN     1 = NMT chờ plan (chọn đúng flavor base/QT) thay vì song song (0)
  SIMPLE_NMT_UNLOAD        1 = nhả model NMT sau khi nháp (1)
  SIMPLE_TRACE_MAX_MB      trace.jsonl vượt ngưỡng → xoay sang trace.1.jsonl (8; 0 = không xoay)
  SIMPLE_SUGGEST_PAIRS     1 = REVIEW được đề xuất cặp xưng hô thiếu → plan_suggestions.json (1)

Cờ thử nghiệm 2026-11-12 «next» (docs/fixes/2026-11-12-translate-simple-next.md) — MẶC ĐỊNH TẮT, tắt = y hệt trước:
  SIMPLE_LEXICON_EXCLUDE_GOLDEN 1 = bỏ mục lexicon src=golden_derived khỏi gợi ý (đo trung thực) (0)
  SIMPLE_PAIR_RULES        1 = điền cặp xưng hô CÒN TRỐNG theo bảng quan hệ data/lexicon/pronoun_rules_zh_vi.json (0)
  SIMPLE_PAIR_FILL         1 = sau review lượt 1: 1 lần gọi model bổ sung cặp thiếu (≥ SIMPLE_PAIR_FILL_MIN câu) (0)
  SIMPLE_PAIR_FILL_MIN     số câu tối thiểu của cặp spk→to thiếu để hỏi model (3)
  SIMPLE_PAIR_FILL_MODEL   model «mini» cho bước bổ sung cặp (trống = model REVIEW của simple)
  SIMPLE_PAIR_FILL_CONF    conf tối thiểu model trả để nhận cặp (0.6)
  SIMPLE_LEARN_INFERRED    1 = khi cổng done, cặp src rule/llm_fill được ghi vào glossary.json → bảng bộ (0)
  SIMPLE_ZH_SOURCE         1 = chọn nguồn ZH: phát hiện hardsub → OCR thắng ASR khi khớp; sửa tên gần đúng (0)
  SIMPLE_ZH_HS_SAMPLES     số khung lấy mẫu đều theo phim để phát hiện hardsub (24)
  SIMPLE_ZH_HS_MIN_RATIO   tỉ lệ khung có chữ ở dải phụ đề để coi là có hardsub (0.3)
  SIMPLE_ZH_NAMEFIX        1 = sửa tên ZH gần đúng theo hồ sơ phim khi SIMPLE_ZH_SOURCE=1 (1)
  SIMPLE_ZH_NAMEFIX_MIN    điểm giống tối thiểu để thay tên (0.75)
"""
from __future__ import annotations

import os


def get(key: str, default: str | None = None) -> str | None:
    try:
        from core.config import get as _g
        return _g(key, default)
    except Exception:  # noqa: BLE001
        return os.getenv(key, default)


def _int(key: str, default: int, lo: int | None = None, hi: int | None = None) -> int:
    try:
        v = int(float(str(get(key, str(default)) or default).strip()))
    except (TypeError, ValueError):
        v = default
    if lo is not None:
        v = max(lo, v)
    if hi is not None:
        v = min(hi, v)
    return v


def _float(key: str, default: float, lo: float | None = None, hi: float | None = None) -> float:
    try:
        v = float(str(get(key, str(default)) or default).strip())
    except (TypeError, ValueError):
        v = default
    if lo is not None:
        v = max(lo, v)
    if hi is not None:
        v = min(hi, v)
    return v


def _flag(key: str, default: str) -> bool:
    return str(get(key, default) or default).strip().lower() in ("1", "true", "yes", "on")


# V5 port 2026-11-12 (agent F5): mặc định = simple; rollback = TRANSLATE_PIPELINE=legacy (env / pineline.config.json).
LEGACY_VALUES = ("legacy", "old")


def pipeline_is_simple() -> bool:
    return str(get("TRANSLATE_PIPELINE", "") or "").strip().lower() not in LEGACY_VALUES


def batch() -> int:
    return _int("SIMPLE_BATCH", 30, 4, 120)


def ctx() -> int:
    return _int("SIMPLE_CTX", 4, 0, 20)


def workers() -> int:
    return _int("SIMPLE_WORKERS", 8, 1, 32)


def repair_rounds() -> int:
    return _int("SIMPLE_REPAIR_ROUNDS", 2, 0, 2)


def conf_min() -> float:
    return _float("SIMPLE_CONF_MIN", 0.7, 0.0, 1.0)


def gate_flag_ratio() -> float:
    return _float("SIMPLE_GATE_FLAG_RATIO", 0.03, 0.0, 1.0)


def gate_flag_max(n_rows: int) -> int:
    raw = str(get("SIMPLE_GATE_FLAG_MAX", "") or "").strip()
    by_ratio = int(gate_flag_ratio() * max(0, n_rows))
    if raw:
        try:
            return max(0, int(raw))
        except ValueError:
            pass
    return max(1, by_ratio)


def max_tokens() -> int:
    return _int("SIMPLE_MAX_TOKENS", 8192, 512, 32768)


def timeout() -> int:
    return _int("SIMPLE_TIMEOUT", 300, 30, 1800)


def temperature() -> float:
    return _float("SIMPLE_TEMPERATURE", 0.2, 0.0, 1.0)


def pronoun_analyze() -> bool:
    return _flag("SIMPLE_PRONOUN_ANALYZE", "0")


def nmt_wait_plan() -> bool:
    return _flag("SIMPLE_NMT_WAIT_PLAN", "0")


def nmt_unload() -> bool:
    return _flag("SIMPLE_NMT_UNLOAD", "1")


def trace_max_bytes() -> int:
    return int(_float("SIMPLE_TRACE_MAX_MB", 8.0, 0.0, 512.0) * 1024 * 1024)


def suggest_pairs() -> bool:
    return _flag("SIMPLE_SUGGEST_PAIRS", "1")


# ------------------------------------------------------------------ cờ «next» (mặc định tắt)
def lexicon_exclude_golden() -> bool:
    return _flag("SIMPLE_LEXICON_EXCLUDE_GOLDEN", "0")


def pair_rules() -> bool:
    return _flag("SIMPLE_PAIR_RULES", "0")


def pair_fill() -> bool:
    return _flag("SIMPLE_PAIR_FILL", "0")


def pair_fill_min() -> int:
    return _int("SIMPLE_PAIR_FILL_MIN", 3, 1, 1000)


def pair_fill_conf() -> float:
    return _float("SIMPLE_PAIR_FILL_CONF", 0.6, 0.0, 1.0)


def pair_fill_model(work_dir=None) -> str | None:
    m = str(get("SIMPLE_PAIR_FILL_MODEL", "") or "").strip()
    return m or review_model(work_dir)


def learn_inferred() -> bool:
    return _flag("SIMPLE_LEARN_INFERRED", "0")


def zh_source() -> bool:
    return _flag("SIMPLE_ZH_SOURCE", "0")


def zh_hs_samples() -> int:
    return _int("SIMPLE_ZH_HS_SAMPLES", 24, 4, 400)


def zh_hs_min_ratio() -> float:
    return _float("SIMPLE_ZH_HS_MIN_RATIO", 0.3, 0.0, 1.0)


def zh_namefix() -> bool:
    return _flag("SIMPLE_ZH_NAMEFIX", "1")


def zh_namefix_min() -> float:
    return _float("SIMPLE_ZH_NAMEFIX_MIN", 0.75, 0.5, 1.0)


def review_model(work_dir=None) -> str | None:
    m = str(get("SIMPLE_MODEL", "") or "").strip()
    if m:
        return m
    try:
        import engines.translate as T
        return T._resolve_review_model(work_dir, None)
    except Exception:  # noqa: BLE001
        return get("REVIEW_MODEL") or get("TRANSLATE_MODEL") or None
