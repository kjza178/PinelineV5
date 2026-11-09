# NMT draft + glossary gầy + REVIEW GPT mini

- **Date:** 2026-11-09
- **Job / khu vực:** translate / glossary / review — V2 + sync V4/V5
- **Status:** fixed

## Triệu chứng

NMT thô (HachimiMT) dịch nghĩa danh hiệu / lệch tên (vd 逆天而行 → «Nghịch thiên hành động»). Glossary cũ khóa cứng quá nhiều terms → gate/name-pass ồn. REVIEW cloud Gemma chậm khi soát/thiếu.

## Root cause

1. Pipeline trước đó chưa có lớp nháp NMT có kiểm soát — hoặc gắn thẳng MT làm VI (đã revert).
2. `hard_term_lock_map` + `agent_name_pass._names` + series terms merge khóa cả chengyu/idiom → quá cứng.
3. `REVIEW_MODEL` = `ollama/gemma4:31b-cloud` không tối ưu tốc độ soát/fill.

## Evidence

- Sandbox `D:\PinelineV2_tmp\mt_bench\` job `0a5f60aead18`: QT nháp ổn nhịp, **không** đủ làm `sub.vi`.
- Smoke: `mt_zh_vi.draft_rows([逆天而行])` → «Nghịch thiên hành động»; seed lock vẫn «Nghịch Thiên Nhi Hành».
- `hard_term_lock_map`: chỉ `type=lock` (+ seed lock); chengyu glossary không vào map.

## Fix

- `mt_zh_vi.py` — CT2 INT8 QT; `MT_ZH_VI=1` draft mode gắn `mt_vi` vào batch LLM.
- `translate.py` — slim `hard_term_lock_map`; payload `mt_vi` + note; prefill NMT trước todo.
- `agent_name_pass.py` — chỉ characters + terms `lock`.
- `series_glossary.py` — series terms chỉ giữ `type=lock`.
- Config: `MT_ZH_VI=1`, `MT_ZH_VI_MODEL=ngocdang83/HachimiMT-60-QT`, `REVIEW_MODEL=chatgpt/gpt-5-6-mini`.
- Sync V4/V5 (+ `engines/` / `agents/` khi có twin).

Backup: `Z:\PinelineV2_codebak\2026-11-09_mt-draft-slim-gloss\`

## Recheck

1. Restart server :8801 (nạp config + module).
2. Job dịch có ASR: log phải có `[mt-zh-vi] draft …` rồi `[trans] …`.
3. Cue nguyên «逆天而行» → VI = seed/glossary lock (không «hành động»).
4. `REVIEW_MODEL` log dùng `chatgpt/gpt-5-6-mini` khi auto-review/fill.
5. **Pass nếu:** nháp MT có mặt trong prompt; lock tên đúng; review Aurora mini.
6. **Fail nếu:** `MT_ZH_VI_ONLY=1` ghi VI thô; hoặc terms chengyu vẫn ép name-pass hàng loạt.

## Liên quan

- Review: `docs/reviews/2026-11-09-mt-bench-verdict.md`
- Config keys: `MT_ZH_VI*`, `REVIEW_MODEL`, `CHATGPT_MODEL`

## Follow-up — auto genre (~02:45)

- **User chọn:** modern→base (`ngocdang83/HachimiMT-60-zh-vi`), xianxia→QT; hỏi flow dịch.
- **Fix:** `MT_ZH_VI_MODEL=auto`; `mt_zh_vi.resolve_model_id(plan)`; local base fallback `robebo116/60-zh-vi` nếu chưa tải repo ngocdang83 base.
- **Recheck:** log `[mt-zh-vi] draft … · base|QT · <repo>`; modern plan → base; xianxia → QT.
- Backup: `Z:\PinelineV2_codebak\2026-11-09_mt-genre-auto\`

## Follow-up — NMT dịch chính / LLM rà (~03:35)

- **User:** «KO, nmt dich chính, llm rà soát» — đảo so với draft-hint cũ.
- **Fix:** `MT_ZH_VI_ROLE=primary` (mặc định): NMT ghi `vi` + hard-lock; LLM translate chỉ vá CJK/trống; `AUTO_REVIEW` + `REVIEW_MODEL=chatgpt/gpt-5-6-mini` = lượt rà. `ROLE=hint` giữ hành vi cũ.
- **Recheck:** log `[mt-zh-vi] PRIMARY …`; sau dịch hầu hết câu có `"mt": 1`; review log dùng GPT mini; cue lock đúng tên.
- Backup: `Z:\PinelineV2_codebak\2026-11-09_mt-primary-llm-review\`

## Follow-up — plan file + review style (~04:05)

- **User:** glossary upload full SRT (OCR soft); siết `run_review` style_lock + mẫu thoại; bench A/B NMT primary vs cũ.
- **Fix:** `PLAN_MODE=file` / `PLAN_MODEL=chatgpt/gpt-5-6-mini` — `_build_plan_from_file` (Aurora upload `sub.zh.srt`); OCR seed mềm; fallback sample. Review: `_style_voice_banner` + `_style_exemplars` trong `review_batch`.
- **Recheck:** log `[plan] upload full ZH SRT` / `file-mode OK`; review prompt có «KHÓA VĂN PHONG» + «MẪU THOẠI». A/B: `docs/reviews/2026-11-09-ab-nmt-primary-vs-old.md`.
- Backup: `Z:\PinelineV2_codebak\2026-11-09_plan-file-review-style\`

## Follow-up — GPT rà tối thiểu (~04:46)

- **User:** NMT đã tốt (vd «Lão tử trước kia viết tiểu thuyết…») mà GPT vẫn đổi → thừa.
- **Fix:** `review_batch` mặc định GIỮ NMT; chỉ sửa A–D (tên/lock, sai nghĩa rõ, Hán thô, quá dài TTS); CẤM đổi đồng nghĩa/xưng hô «hay hơn»; temp 0.1. Soften `review_lock_rules`.
- Backup: `Z:\PinelineV2_codebak\2026-11-09_review-keep-nmt\`
- **Recheck:** review lô chứa i=48 — NMT «Lão tử…» không vào fixes (hoặc tỷ lệ sửa << 87%).

## Follow-up — flex style + NMT primary (~04:15)

- **User:** không khóa văn phong (đô thị↔tu tiên); NMT dịch chính.
- **Fix:** review banner linh hoạt; bỏ CẤM đổi register; detox/`filter_review` nới khi mixed; MT auto default base (QT chỉ xianxia thuần); giữ `ROLE=primary`.
- Backup: `Z:\PinelineV2_codebak\2026-11-09_flex-style-nmt-primary\`
- **Recheck:** review prompt có «VĂN PHONG LINH HOẠT»; `resolve_model_id(mixed)` → base; `primary_mode()` True.

## Follow-up — P1 harden + A/B (~04:10)

- **A/B** ([review](ec2ac74e-33b5-47d0-be78-9bcf34d1de40)): old 14 / NMT 3 / tie 22 → **CONDITIONAL GO draft**, NO-GO NMT làm final không GPT+lock. Report `docs/reviews/2026-11-09-ab-nmt-primary-vs-old.md`.
- **Code review** ([review](bc4f2964-369f-4a47-bafd-38ddbafe3b88)): vá P1 — `_normalize_plan_data` null-list; SRT `[i=N]` + remap scenes; `PLAN_MODEL` thắng + `PLAN_FILE_TIMEOUT=180`; style helpers không crash → `rv=1` mù.
- **Recheck:** `terms:null` → `[]`; scene range cue→i; banner rỗng khi plan trống.
