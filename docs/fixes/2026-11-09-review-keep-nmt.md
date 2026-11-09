# GPT review viết lại NMT đã tốt (Lão tử…)

- **Date:** 2026-11-09
- **Job / khu vực:** `translate.review_batch` / `_filter_cosmetic_nmt_fixes`; sandbox `D:\PinelineV2_tmp\mt_sandbox_job` i=48
- **Status:** fixed
- **Backup zip:** `Z:\PinelineV2_backup_2026-11-09_0452.zip`
- **Codebak:** `Z:\PinelineV2_codebak\2026-11-09_review-keep-nmt2\`

## Triệu chứng

NMT đã thoại miệng ổn (`Lão tử trước kia viết tiểu thuyết…`) nhưng GPT rà vẫn đổi sang bản «hay hơn» (`Ngày trước… tôi còn chẳng dám…` / rút viết lại). User: NMT rất tốt rồi — không cần sửa.

## Root cause

1. Prompt review vẫn bị model bỏ qua → trả polish đồng nghĩa.
2. Bộ lọc hậu kỳ quá lỏng: mọi bản **ngắn hơn** NMT so với `sec` đều bị giữ như «TTS rút» → polish lọt.

## Evidence

- `NMT_vs_GPT.md` i≈48: ZH「老子过去写小说…」 / NMT「Lão tử…」 / GPT「Ngày trước… tôi…」
- Probe trước siết: `final_fixes {48: ...}` dù prompt cấm đổi xưng hô.
- Unit filter cũ: `raw={48: polish}` vẫn `kept`.

## Fix

- `translate.py` `review_batch`: prompt tối thiểu A–D, mặc định giữ NMT; temp 0.1.
- `_filter_cosmetic_nmt_fixes`: **mặc định DROP**; chỉ giữ
  - (C) còn CJK → hết CJK
  - (A) chèn tên `characters` / `type=lock`
  - (D) TTS chỉ khi vượt budget mạnh **và** rút từ (từ mới ≤15%, overlap cao) — không chấp nhận viết lại đồng nghĩa
  - Đổi xưng hô miệng (`Lão tử`…) → `tôi`/`chúng ta`: luôn bỏ
- Sync V2/V4/V5.

## Recheck

1. `cd Z:\PinelineV2` → `python D:\PinelineV2_tmp\mt_sandbox_job\_probe_review.py`
2. **Pass nếu:** `final_fixes {}` (hoặc không có 48); NMT i=48 giữ «Lão tử…»; `filter_only {}` + `filter-ok`
3. **Fail nếu:** GPT polish i=48 vẫn apply vào script

## Liên quan

- Config: `MT_ZH_VI_ROLE=primary`, `REVIEW_MODEL=chatgpt/gpt-5-6-mini`
- Docs: `docs/reviews/2026-11-09-mt-sandbox-job.md`, `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`
- **Cần restart :8801** để worker dịch nạp filter mới
