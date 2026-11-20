"""Cấu hình luồng simple — mọi khoá prefix SIMPLE_ đọc qua config.get (env > pineline.config.json > mặc định).

Không sửa config.json. Khoá:
  TRANSLATE_PIPELINE       trống/simple = luồng này (MẶC ĐỊNH từ 2026-11-12 F2); legacy/old/off/0/false/no
                           = luồng cũ run_translate + run_review. Job đã bắt đầu luồng nào thì giữ luồng đó
                           (manifest.translate_pipeline) — xem job_pipeline().
  SIMPLE_MODEL             model REVIEW cloud (trống = REVIEW model như luồng cũ: _resolve_review_model)
  SIMPLE_PLAN_MODEL        model lập plan A7 (trống = PLAN_MODEL trong config -> SIMPLE_MODEL)
  PLAN_MODEL_BACKUP        model dự phòng khi plan chính lỗi (trống = AURORA_REVIEW_MODEL → chatgpt/gpt-6)
  SIMPLE_FULL_PLAN         1 = A7 lập plan đọc toàn bộ phim ASR bằng context lớn LLM (1)
  SIMPLE_OVERLAP_CUES      số câu chồng lấn liền trước cho lô review A8 (3)
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
  SIMPLE_ZH_OCR_MODE       targeted = OCR CÓ CHỌN LỌC 1 khung giữa câu (lượt A: 他/她/它, tên, số; lượt B: câu kém
                           chắc người nói/nghe ±1) — mặc định; full = OCR cả phim nền (hs_ocr_fast) — 2026-11-14
  SIMPLE_ZH_OCR_PASS_B     1 = chạy lượt B sau review (1)
  SIMPLE_UNREVIEWED_TOLERANCE  số câu CHƯA SOÁT tối đa được nhận bản nháp (cờ unreviewed_accepted) thay vì park
                           (trống = max(3, 0.2% số câu); 0 = tắt, park như cũ) — fix 2026-11-13 agentM
  SIMPLE_MISSING_BATCH     cỡ lô của lượt review bổ sung CHỈ câu chưa soát trước khi park (4) — chỉ khi còn
                           ≤ SIMPLE_MISSING_SMALL_MAX (5) câu; nhiều hơn → lô thường SIMPLE_BATCH (2026-11-18)
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path


def get(key: str, default: str | None = None) -> str | None:
    try:
        from config import get as _g
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


# ------------------------------------------------------------------ chọn luồng (MỘT nguồn sự thật)
# 2026-11-12 F2: chủ dự án chọn simple làm MẶC ĐỊNH (A/B golden: xưng hô 92% vs 35%, held-out 98.2%,
# nhanh 2–3×). Quay về luồng cũ: TRANSLATE_PIPELINE=legacy (env hoặc pineline.config.json).
PIPELINE_SIMPLE = "simple"
PIPELINE_LEGACY = "legacy"
JOB_PIPELINE_KEY = "translate_pipeline"          # manifest.json (cấp gốc): luồng job đã dùng


# Cùng quy ước V4/V5 (F4/F5): trống/simple (và giá trị lạ) = simple; các giá trị dưới = luồng cũ.
LEGACY_VALUES = ("legacy", "old", "off", "0", "false", "no")


def pipeline_default() -> str:
    """Luồng mặc định cho job MỚI: TRANSLATE_PIPELINE ∈ LEGACY_VALUES → legacy; trống/simple/khác → simple."""
    v = str(get("TRANSLATE_PIPELINE", "") or "").strip().lower()
    return PIPELINE_LEGACY if v in LEGACY_VALUES else PIPELINE_SIMPLE


def pipeline_is_simple() -> bool:
    return pipeline_default() == PIPELINE_SIMPLE


def _infer_job_pipeline(d: dict, wd: Path) -> str | None:
    """Job chưa đóng dấu (tạo trước F2): suy luồng đã dùng. None = chưa bắt đầu dịch."""
    st = (d.get("stages") or {}).get("translate") or {}
    ag = d.get("agent") or {}
    if not isinstance(st, dict):
        st = {}
    if str(st.get("mode") or "").lower() == PIPELINE_SIMPLE or (isinstance(ag, dict) and ag.get("simple_park")):
        return PIPELINE_SIMPLE
    # fix 2026-11-18: server đánh translate=running (mark_running, started_at) TRƯỚC khi hỏi luồng → job/part
    # mới tinh bị suy «legacy» rồi khoá luôn (c7367a659c46_p01 chạy luồng cũ + upload Aurora). Chỉ tính
    # dấu vết THẬT: script.json đã có câu VI, hoặc stage translate đã xong/lỗi.
    if _script_has_vi(wd) or str(st.get("status") or "").lower() in ("done", "error", "failed"):
        return PIPELINE_LEGACY
    return None


def _script_has_vi(wd: Path) -> bool:
    sp = wd / "script.json"
    if not sp.is_file():
        return False
    try:
        rows = json.loads(sp.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return True                      # có file mà không đọc được → coi như có dấu vết (an toàn như cũ)
    return isinstance(rows, list) and any(isinstance(r, dict) and (r.get("vi") or "").strip() for r in rows)


def job_pipeline(work_dir, *, fresh: bool = False, stamp: bool = True) -> str:
    """Luồng dịch cho 1 job — mọi đường gọi dịch trong server hỏi hàm này.

    - Đã đóng dấu manifest.translate_pipeline → giữ nguyên (job dở luồng cũ hoàn tất bằng luồng cũ).
    - Chưa đóng dấu: có dấu vết dịch luồng cũ (script.json / stage translate đã chạy, mode≠simple) → legacy;
      dấu vết simple (mode=simple / agent.simple_park) → simple; chưa dịch → pipeline_default().
    - fresh=True (bấm «Dịch LẠI» từ đầu — force, không phải soát lại) → pipeline_default() và đóng dấu lại.
    stamp=True: ghi dấu qua Manifest.update khi đổi (lỗi ghi → bỏ qua, vẫn trả luồng)."""
    wd = Path(work_dir)
    mp = wd / "manifest.json"
    try:
        d = json.loads(mp.read_text(encoding="utf-8"))
        if not isinstance(d, dict):
            d = {}
    except Exception:  # noqa: BLE001
        d = {}
    cur = str(d.get(JOB_PIPELINE_KEY) or "").strip().lower()
    if not fresh and cur in (PIPELINE_SIMPLE, PIPELINE_LEGACY):
        return cur
    if fresh:
        p, why = pipeline_default(), "fresh"
    else:
        inf = _infer_job_pipeline(d, wd)
        p, why = (inf, "inferred") if inf else (pipeline_default(), "default")
    if stamp and p != cur and mp.exists():
        def _fn(dd):
            dd[JOB_PIPELINE_KEY] = p
            dd[JOB_PIPELINE_KEY + "_why"] = why
            dd[JOB_PIPELINE_KEY + "_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
        try:
            from manifest import Manifest
            Manifest(wd).update(_fn)
        except Exception as e:  # noqa: BLE001
            print(f"[simple] đóng dấu translate_pipeline={p} lỗi: {e}", flush=True)
    return p


SIMPLE_BATCH_MIN = 40
SIMPLE_BATCH_MAX = 200


def deepseek_concurrency() -> int:
    """Số request song song cho DeepSeek Official API (mặc định 32, kẹp [1, 64])."""
    return _int("DEEPSEEK_CONCURRENCY", 32, 1, 64)


def batch() -> int:
    return _int("SIMPLE_BATCH", 30, 4, 120)


def batch_for_rows(n_rows: int, workers_count: int = 1, explicit: int | None = None) -> int:
    """Tự chọn cỡ lô review theo số câu và mức song song:
    - Nếu explicit > 0 hoặc user có cấu hình cứng SIMPLE_BATCH trong config/env: tôn trọng giá trị đó.
    - Tự động: ceil(n_rows / workers_count), kẹp trong [SIMPLE_BATCH_MIN (40), SIMPLE_BATCH_MAX (200)].
    """
    if explicit is not None and explicit > 0:
        return explicit
    raw = str(get("SIMPLE_BATCH", "") or "").strip()
    if raw:
        try:
            return max(4, min(300, int(float(raw))))
        except ValueError:
            pass
    if n_rows <= 0 or workers_count <= 0:
        return SIMPLE_BATCH_MIN
    import math
    calc = math.ceil(n_rows / workers_count)
    return max(SIMPLE_BATCH_MIN, min(SIMPLE_BATCH_MAX, calc))


def ctx() -> int:
    return _int("SIMPLE_CTX", 4, 0, 20)


def workers(model: str | None = None) -> int:
    """Số worker song song cho review: DeepSeek dùng DEEPSEEK_CONCURRENCY (32), khác (Aurora/local) dùng SIMPLE_WORKERS (8)."""
    m = (model or "").strip().lower()
    if m and (m.startswith("deepseek/") or m.startswith("deepseek-")):
        return deepseek_concurrency()
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


def unreviewed_tolerance(n_rows: int) -> int:
    """fix 2026-11-13 agentM: số câu chưa soát được nhận bản nháp (thay vì park). Trống = max(3, 0.2% số câu)."""
    raw = str(get("SIMPLE_UNREVIEWED_TOLERANCE", "") or "").strip()
    if raw:
        try:
            return max(0, int(float(raw)))
        except ValueError:
            pass
    return max(3, int(0.002 * max(0, n_rows)))


def missing_batch() -> int:
    return _int("SIMPLE_MISSING_BATCH", 4, 1, 30)


def missing_small_max() -> int:
    """2026-11-18: soát bổ sung còn ≤ N câu → lô nhỏ SIMPLE_MISSING_BATCH (câu khó / rác hay bị model lờ);
    nhiều hơn (vd 81 câu OCR lượt B vừa đổi chữ) → lô thường SIMPLE_BATCH (trước: luôn lô 4 → 21 lần gọi)."""
    return _int("SIMPLE_MISSING_SMALL_MAX", 5, 0, 1000)


def missing_batch_for(n_left: int) -> int:
    return missing_batch() if n_left <= missing_small_max() else max(missing_batch(), batch())


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


def zh_ocr_mode() -> str:
    v = str(get("SIMPLE_ZH_OCR_MODE", "targeted") or "targeted").strip().lower()
    return "full" if v == "full" else "targeted"


def zh_ocr_pass_b() -> bool:
    return _flag("SIMPLE_ZH_OCR_PASS_B", "1")


def zh_hs_samples() -> int:
    return _int("SIMPLE_ZH_HS_SAMPLES", 24, 4, 400)


def zh_hs_min_ratio() -> float:
    return _float("SIMPLE_ZH_HS_MIN_RATIO", 0.3, 0.0, 1.0)


def zh_namefix() -> bool:
    return _flag("SIMPLE_ZH_NAMEFIX", "1")


def zh_namefix_min() -> float:
    return _float("SIMPLE_ZH_NAMEFIX_MIN", 0.75, 0.5, 1.0)


def full_plan_enabled() -> bool:
    """A7: Lập plan đọc cả phim từ toàn bộ thoại ASR bằng LLM context lớn."""
    return _flag("SIMPLE_FULL_PLAN", "1")


def overlap_cues() -> int:
    """A8: Số câu ngữ cảnh chồng lấn liền trước cho mỗi lô review (0-10, mặc định 3)."""
    return _int("SIMPLE_OVERLAP_CUES", 3, 0, 10)


def plan_model(work_dir=None) -> str | None:
    """Model LLM CHÍNH cho bước lập plan A7."""
    m = str(get("SIMPLE_PLAN_MODEL", "") or "").strip()
    if m:
        return m
    pm = str(get("PLAN_MODEL", "") or "").strip()
    if pm:
        return pm
    return review_model(work_dir)


def plan_backup_model(work_dir=None) -> str | None:
    """2026-11-20: model DỰ PHÒNG khi plan chính lỗi (DS hết token / 429 / rỗng).

    `PLAN_MODEL_BACKUP` (hoặc `SIMPLE_PLAN_BACKUP`) → không set thì `AURORA_REVIEW_MODEL` → `chatgpt/gpt-6`.
    None nếu trùng model chính (không có lớp dự phòng thật).
    """
    m = str(get("PLAN_MODEL_BACKUP", "") or get("SIMPLE_PLAN_BACKUP", "") or "").strip()
    if not m:
        m = str(get("AURORA_REVIEW_MODEL", "") or "").strip() or "chatgpt/gpt-6"
    primary = plan_model(work_dir) or ""
    return None if (not m or m == primary) else m


def plan_models(work_dir=None) -> list[str | None]:
    """Danh sách model plan theo thứ tự: main → backup (bỏ trùng)."""
    out: list[str | None] = []
    for m in (plan_model(work_dir), plan_backup_model(work_dir)):
        if m and m not in out:
            out.append(m)
    return out or [None]


def review_model(work_dir=None) -> str | None:
    """Model soát CHÍNH của luồng simple. 2026-11-18: KHÔNG còn bị `review_backup=aurora_parallel` ép sang Aurora
    (trước: bật «backup» = Aurora soát toàn bộ, DeepSeek không chạy) — Aurora giờ là DỰ PHÒNG (backup_model)."""
    m = str(get("SIMPLE_MODEL", "") or "").strip()
    if m:
        return m
    try:
        import translate as T
        return T._resolve_review_model(None, None)      # = REVIEW_MODEL (không đọc queue_opts)
    except Exception:  # noqa: BLE001
        return get("REVIEW_MODEL") or get("TRANSLATE_MODEL") or None


def _queue_review_backup(work_dir) -> str:
    """off | aurora_parallel. 2026-11-20: thiếu key / work_dir=None → aurora_parallel (luôn có backup)."""
    if work_dir is None:
        return "aurora_parallel"
    try:
        d = json.loads((Path(work_dir) / "manifest.json").read_text(encoding="utf-8"))
        raw = ((d.get("queue_opts") or {}) if isinstance(d, dict) else {}).get("review_backup")
        if raw is None or str(raw).strip() == "":
            return "aurora_parallel"
        v = str(raw).strip().lower()
        return v if v in ("off", "aurora_parallel") else "aurora_parallel"
    except Exception:  # noqa: BLE001
        return "aurora_parallel"


def backup_model(work_dir=None) -> str | None:
    """Model DỰ PHÒNG soát (DeepSeek lỗi → Aurora). 2026-11-20: mặc định BẬT (aurora_parallel);
    chỉ tắt khi job/`review_backup=off`. None nếu trùng model chính."""
    if _queue_review_backup(work_dir) != "aurora_parallel":
        return None
    m = str(get("AURORA_REVIEW_MODEL", "") or "").strip() or "chatgpt/gpt-6"
    return None if m == (review_model(work_dir) or "") else m


def backup_batch() -> int:
    """Cỡ lô khi làm lại bằng model dự phòng (Aurora chịu lô vừa) — SIMPLE_BACKUP_BATCH (30)."""
    return _int("SIMPLE_BACKUP_BATCH", 30, 4, 120)
