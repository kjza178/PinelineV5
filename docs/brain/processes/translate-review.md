# Quy trình: Dịch → REVIEW → QA

_Cập nhật: 2026-11-11. Nguồn: `translate.py`, DECISIONS 11-09…11-11, fix 11-09 `mt-draft-slim-gloss`, `review-keep-nmt`, `hv-auditor`, 11-10 `review-gpt6-aurora`, 11-11 `pass1-upload-size`, `studio-1job-pipeline`._

## Luồng

```mermaid
flowchart TB
  ZH[sub.zh.srt] --> PLAN[build_plan<br/>PLAN_MODE=file: LLM đọc file → nhân vật, xưng hô, cảnh<br/>ensure_hard_terms → hv_auditor.audit_and_fix_plan]
  PLAN --> GL[series_glossary + hard_term_lock_map]
  ZH --> NMT[run_translate → mt_zh_vi.draft_rows<br/>MT_ZH_VI=1, primary_mode]
  GL --> NMT
  NMT --> POST[apply_hard_term_locks · apply_pronoun_postpass · apply_style_polish]
  POST --> SJ[(script.json)]
  SJ --> P1[run_review: Pass1 run_review_pass1_full_vi<br/>GPT đọc FULL SRT VI, chunk nếu lớn]
  P1 --> RB[review_batch theo lô — Aurora∥ REVIEW_PARALLEL worker<br/>lỗi → _review_chunk_with_fallback local<br/>_filter_cosmetic_nmt_fixes giữ NMT nếu GPT chỉ đánh bóng]
  RB --> HF[cuối run_review: series_glossary.save_from<br/>agent_hang_fix.fix_hang_job — sau review để tránh race ghi script]
  HF --> SJ2[(script.json rv=1)]
  SJ2 --> RQ[server._run_requested_review<br/>chỉ khi manifest.agent.review_request: agent_name_pass + agent_pronoun_pass]
  RQ --> QA[server: agent_qa_gate.run_qa_gate nếu AGENT_QA_GATE=1<br/>+ agent_quality / agent_brain quét qa_brain.json]
  QA -->|pass| TTS
  QA -->|high| HOLD
```

## Hàm & key chính

| Bước | Hàm | Key |
|---|---|---|
| Plan | `translate.build_plan`, `_build_plan_from_file` | `PLAN_MODE`, `PLAN_MODEL` |
| Nháp | `translate.run_translate`, `mt_zh_vi` | `MT_ZH_VI`, `TRANSLATE_PRESET` |
| Hậu xử lý | `apply_hard_term_locks`, `apply_pronoun_postpass`, `apply_style_polish` | `PRONOUN_TITLE_POLICY` |
| Pass1 | `run_review_pass1_full_vi`, `_pass1_upload_full_via_chunks` | `REVIEW_PASS1_MAX_UPLOAD_BYTES`, `REVIEW_PASS1_CHUNK_CUES`, `REVIEW_PASS1_ALLOW_CHAT_FALLBACK=0` |
| REVIEW lô | `run_review`, `review_batch`, `_review_parallel_workers`, `_resolve_review_model` | `REVIEW_MODEL`, `AURORA_REVIEW_MODEL`, `REVIEW_BACKUP`, `REVIEW_PARALLEL(_MAX)`, `REVIEW_PRESET`, `REVIEW_PRONOUN_MASK` |
| Sẵn sàng TTS? | `translate_ready_for_tts`, `count_script_missing`, `translate_coverage_gap` | — |

Danh sách key đầy đủ + nơi đọc: [../generated/config-keys.md](../generated/config-keys.md). Lưu ý `config.LLM_FILE_FIRST_KEYS`: các key LLM/REVIEW đọc **file trước env** — sửa `pineline.config.json` có hiệu lực ngay, không cần restart.

## Quyết định user cần tôn trọng (xem DECISIONS)

- NMT là bản chính; GPT chỉ sửa lỗi thật, không "đánh bóng" (11-09 keep-NMT).
- REVIEW được nới văn phong khi vá, không dịch lại toàn bộ (11-10).
- Pass1 phải đọc full file, không chat mẫu (11-11).
- Hang high → LLM trace + chọn phương án rồi mới mở HOLD (11-10, phương án B).

## Đo chất lượng

Bench/so sánh model: `docs/reviews/2026-11-09-mt-*`, `2026-11-09-ab-nmt-primary-vs-old.md`, `2026-11-10-review-parallel-aurora.md`. Đổi model/prompt → chạy lại bench tương tự trước khi đổi mặc định (xem [../workflows/ai-change.md](../workflows/ai-change.md)).
