# Port V2→V5: luồng dịch `translate_simple` (mặc định) + Demucs trước ASR

- **Ngày:** 2026-11-12 · **Agent:** F5 · **Cây:** `Z:\PinelineV5` (bố cục package) · **Nguồn:** `Z:\PinelineV2` (chỉ đọc)
- **Backup:** `Z:\PinelineV5\.backup_edit_20261112_agentF5\` (giữ cấu trúc: `server.py`, `engines/separate.py`, `engines/asr/asr.py`, `tests/test_asr_demucs.py`, `tests/test_translate_force_default.py`, `docs/*`). File mới không có bản gốc. md5 trước/sau: `_transfer/f5_new_md5.txt`.
- **Cần restart:** :8805 (server V5) để nạp `server.py` + `engines.translate_simple`; tiến trình con ASR đọc `engines/asr/asr.py` mới ngay ở job sau.

## Triệu chứng
V5 chưa có luồng dịch mới (`translate_simple`) và vẫn ASR thẳng trên audio gốc (`ASR_USE_DEMUCS` mặc định 0, Demucs cắt cứng 60').
V2 đã có cả hai (2026-11-12) — chủ dự án chốt: dịch simple là mặc định, Demucs 1 lần/job trước ASR.

## Root cause
V5 sync lần cuối 11-11 (~03:00) bằng `scripts/sync_from_v2.py`; script chỉ đồng bộ module `.py` ở gốc V2, không có package con
(`translate_simple/`) và data (`data/lexicon/`). Thay đổi V2 sau mốc đó chưa sang V5.

## Fix
Không chạy `sync_from_v2.py --apply` toàn bộ (sẽ kéo cả translate-b2/b3 và mọi thay đổi khác của V2) — chỉ port phạm vi được giao,
dùng lại hàm biến đổi của chính `sync_from_v2.py` (`rewrite_imports`, `add_bootstrap`) để import đúng bố cục package.

| V2 | V5 | Ghi chú |
|---|---|---|
| `translate_simple/*.py` (16 file) | `engines/translate_simple/` | import phẳng → `core.config`, `core.manifest`, `core.fileio`, `engines.translate`, `engines.llm`, `engines.subs`, `engines.series_glossary`, `engines.mt_zh_vi`, `engines.pronoun_consistency`, `engines.ocr`, `engines.asr.hardsub_asr`, `tools.context_studio`, `engines.cloud_retry`; `ROOT=parents[2]` (lexicon, pair_rules) |
| `cloud_retry.py` | `engines/cloud_retry.py` | module mới; **legacy `engines/translate.py` KHÔNG dùng** (translate-b2/b3 chưa port) |
| `data/lexicon/{idioms_zh_vi,pronoun_rules_zh_vi}.json` | `data/lexicon/` | chép nguyên |
| `separate.py` | `engines/separate.py` | khúc theo khoảng lặng (`engines.split_parts.find_best_cut_point`) + cắt/ghép đúng số mẫu, `outputs_valid` |
| `asr.py` | `engines/asr/asr.py` | `asr_use_demucs()` mặc định 1, `resolve_asr_source` có FALLBACK audio gốc khi Demucs lỗi/OOM/thiếu gói |
| `server.py` nhánh simple | `server.py` | `_translate_pipeline_simple`, `_simple_translate_run`, `_auto_translate_simple` (mới); rẽ nhánh trong `_auto_gpu`, `_process_gpu`, `_run_stage("translate")`, `_translate_flow`; `_queue_park_ready` chờ `review_retry_at` khi `simple_park` |
| `tools/{collect_manual_edits,simple_stats}.py` | `tools/` | script độc lập (`--work` bắt buộc) |
| `tests/test_translate_simple*.py`, `test_separate_demucs_chunks.py`, `test_asr_demucs.py` | `tests/` | import + `mock.patch("engines.separate.…" / "engines.asr.asr.…")`; đường dẫn `engines/translate_simple`, `engines/translate.py` |

**Khác biệt so với V2 (cố ý):**
- **Mặc định:** `TRANSLATE_PIPELINE` trống/`simple` ⇒ simple; `legacy` (hoặc `old`) ⇒ luồng cũ. (`cfg.pipeline_is_simple`, `server._translate_pipeline_simple` cùng quy ước — khớp F2 ở V2.)
- `stage_draft`: chỉ truyền `before_local_llm` khi `engines.translate.build_plan` có tham số đó (V5 chưa có translate-b2).
- Không port: `_translate_gate_action`, `_park_fill_pending`, `FILL_PENDING_PARK` (translate-b2/b3) — nhánh legacy giữ nguyên hành vi V5.
- `tests/test_translate_force_default.py`: thêm fixture `TRANSLATE_PIPELINE=legacy` (file kiểm luồng cũ; 3 test vẫn fail vì drift đã biết `_run_translate_engine`).
- `tests/test_translate_simple.py`: `test_cfg_defaults` kỳ vọng simple=True; `test_server_default_is_simple_legacy_rollback` (mới); `test_server_legacy_calls_old_flow`; `_translate_flow` nhánh cũ đặt `legacy`.

**Mặc định sau port:** `TRANSLATE_PIPELINE`=simple · `SIMPLE_PAIR_RULES`/`SIMPLE_PAIR_FILL`/`SIMPLE_ZH_SOURCE`/`SIMPLE_LEARN_INFERRED`/`SIMPLE_LEXICON_EXCLUDE_GOLDEN`=0 · `ASR_USE_DEMUCS`=1 (fallback audio gốc).
Không đổi `pineline.config.json` / `config.json` — mặc định nằm trong code; khoá đọc qua `core.config.get` (env > file) như các khoá khác.

**Rollback:**
- Dịch: `"TRANSLATE_PIPELINE": "legacy"` trong `pineline.config.json` hoặc `set TRANSLATE_PIPELINE=legacy` trước `run_v5.bat` → restart :8805.
- ASR: `"ASR_USE_DEMUCS": "0"` (inject_env chép vào env → tiến trình con ASR) hoặc `set ASR_USE_DEMUCS=0` → restart :8805.
- Code: chép lại từ `.backup_edit_20261112_agentF5\`; chuyển `engines\translate_simple\`, `engines\cloud_retry.py`, `data\lexicon\`, `tools\{collect_manual_edits,simple_stats}.py`, test mới vào `_to_delete\`.

## Evidence / Recheck
- Bản sao Linux (stub fastapi/google/soundfile/yt_dlp, Python 3.13): trước **35 failed / 158 passed** → sau **35 failed / 256 passed / 4 skipped**, danh sách FAILED y hệt (toàn lỗi môi trường stub + drift đã biết).
- 6 file simple+demucs: **101 passed, 4 skipped** (skip: golden cần `Z:\PinelineV6\data\golden`+`D:\PinelineV2_work`; 3 test so bản gốc cần backup agentB của V2).
- `py_compile` OK trên máy; `scripts/tree_audit.py` ERROR=0 (trước/sau như nhau); import smoke `server`, `engines.translate_simple.*`, `engines.separate`, `engines.asr.asr` OK.
- Windows: chạy `Z:\PinelineV6\scripts\test_v5_simple_demucs.bat` — kỳ vọng [1] 101 passed / 4 skipped / 0 failed (golden có thể thành passed);
  [2] so với `Z:\PinelineV6\scratch\baseline_v5.log` (11-11: 18 failed / 175 passed) → 18 failed cùng tên / ~273 passed.
- Recheck: **Pass** (bản sao) · **chờ** Windows.

## Liên quan
- V2: `docs/design/2026-11-12-translate-simple.md`, `docs/fixes/2026-11-12-translate-simple*.md`, `docs/fixes/2026-11-12-asr-demucs-default.md`, `docs/reviews/2026-11-12-translate-simple*-review.md`.
- V5: `docs/fixes/2026-11-11-v5-package-sync.md` (`scripts/sync_from_v2.py`).
