# REVIEW bỏ sót ASR cắt lặp / chồng câu

- **Date:** 2026-11-09
- **Job / khu vực:** `translate.py` — `review_batch`, `_filter_cosmetic_nmt_fixes`, `apply_style_polish`; sandbox `D:\PinelineV2_tmp\mt_sandbox_job` i=17; full-job sample i=582
- **Status:** fixed
- **Backup zip:** `Z:\PinelineV2_backup_2026-11-09_2016.zip`
- **Codebak:** `Z:\PinelineV2_codebak\2026-11-09_review-asr-merge\`

## Triệu chứng

ASR cắt thời gian tạo câu lặp trong một cue (`不对不对` → `Không đúng không đúng`) hoặc lặp đuôi–đầu giữa hai cue. REVIEW giữ nguyên NMT hoặc bản Gemma đã gộp lại bị hậu lọc coi là cosmetic và loại bỏ.

Luật `吃醋` đồng thời coi `uống giấm` là lỗi cứng tuyệt đối dù một số ngữ cảnh chơi chữ / cách nói tự nhiên vẫn chấp nhận được.

## Root cause

- Prompt `review_batch` chỉ cho phép lỗi A–D, không giao nhiệm vụ nhận diện stutter/overlap do biên ASR.
- `_filter_cosmetic_nmt_fixes` chỉ giữ CJK, tên lock và rút TTS; không có nhánh chứng minh ASR-repeat nên mọi bản gộp/tối ưu bị drop.
- `_meaning_rules` và mục C của review ghi `吃醋` theo hướng bắt buộc `ghen`, cấm tuyệt đối `uống giấm`.
- Post-pass chưa có helper an toàn cho mẫu lặp sát nhau rõ ràng.

## Evidence

- Trước fix, sandbox i=17: ZH `不对不对，`; VI `Không đúng không đúng,`.
- Full-job sample i=582: ZH `殿主属下属下…`; NMT có `thuộc hạ ... thuộc hạ`; bản gộp cũ tự nhiên hơn nhưng filter cũ không có lý do giữ.
- Filter cũ mặc định tăng biến `dropped` cho mọi sửa không thuộc CJK/name/TTS, kể cả sửa ASR overlap.

## Fix

- `translate.py`:
  - làm mềm hướng dẫn `吃醋`: `ghen` là nghĩa thường; `uống giấm` / biến thể tự nhiên, chơi chữ không tự động là lỗi cứng;
  - thêm duty (E) cho REVIEW Gemma: rà lặp nội câu và tail→head giữa cue liên tiếp, gộp/tối ưu đúng cue mà không rewrite NMT tốt;
  - thêm bằng chứng ASR-stutter/overlap vào `_filter_cosmetic_nmt_fixes`, chỉ giữ fix còn lõi từ, sạch Hán và không phình câu;
  - thêm `heal_obvious_internal_stutter` + `apply_asr_stutter_heal`, gọi từ style post-pass; bỏ lặp cụm VI từ hai từ trở lên và mẫu Hán rõ ràng, bỏ qua dòng `manual`.
- Không đổi vai trò NMT primary; không gộp fill và review.

## Recheck

1. `cd Z:\PinelineV2`
2. `python -m py_compile translate.py`
3. Chạy focused probe import `translate` trên sandbox i=17 và sample i=582:
   - `heal_obvious_internal_stutter("不对不对，") == "不对，"`
   - `heal_obvious_internal_stutter("Không đúng không đúng,") == "Không đúng,"`
   - filter giữ fix i=17, i=582 và tail→head; filter vẫn bỏ cosmetic `Lão tử` → `tôi`.
4. `python -m pytest tests/test_translate_missing.py::test_translate_batch_raises_on_dropped_lines tests/test_translate_missing.py::test_translate_safe_splits_and_recovers_when_dropped -q`
5. **Pass nếu:** probe in `KNOWN_STUTTER_PROBES=PASS i=17 i=582 tail-head`; pytest `2 passed`; prompt mock có duty E và `吃醋` mềm.
6. **Fail nếu:** i=17 vẫn còn hai lần `Không đúng`, filter trả `{}` cho fix ASR có bằng chứng, hoặc cosmetic không liên quan lọt qua.

## Liên quan

- Backup: `Z:\PinelineV2_backup_2026-11-09_2016.zip`
- Codebak: `Z:\PinelineV2_codebak\2026-11-09_review-asr-merge\`
- Config giữ nguyên: `REVIEW_MODEL=llama/gemma4-12b-qat-mtp-fast`
- Cần restart server `:8801` khi hàng đợi rảnh để process nạp `translate.py` mới.

## Follow-up

- **Date:** 2026-11-09 ~20:40
- **Issue:** `heal_obvious_internal_stutter` cắt nhầm tượng thanh sandbox i=109 `叮当叮当，` → `叮当，`. Smoke Gemma duty E trên batch stutter vẫn bỏ sót i=17 (trả no-op / polish 109–110); filter drop cosmetic đúng.
- **Fix:** allowlist nửa câu chỉ gồm ký tự tượng thanh/cười (`叮当`/`哈哈`…) → giữ nguyên; `apply_asr_stutter_heal` chạy **trước** vòng LLM trong `run_review` (vẫn giữ trong `apply_style_polish`); prompt E thêm ví dụ `不对不对` + cấm cắt `叮当叮当`; `review_batch` mặc định `_rmodel()`.
- **Evidence:** dry-run sandbox heal N=1 chỉ i=17; i=109 giữ `叮当叮当，`; filter `SYNTH_KEEP` i=17; pre-heal rồi review không đụng ding; pytest 2 passed.
- **Recheck thêm:**
  1. `heal_obvious_internal_stutter("叮当叮当，") == "叮当叮当，"`
  2. Copy sandbox → `run_review` (hoặc import `apply_asr_stutter_heal`) → i=17 còn một bản; i=109 không rút.
  3. **Pass nếu:** stutter nội bộ rõ bị gỡ trước LLM; tượng thanh giữ; cosmetic Gemma vẫn drop.
  4. **Fail nếu:** `叮当叮当` bị còn một `叮当`, hoặc i=17 vẫn hai lần `Không đúng` sau heal.
