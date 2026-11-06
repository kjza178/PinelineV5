# Thumb AI chữ sai / không hợp lý — prompt đóng cứng

- **Date:** 2026-11-04
- **Job / khu vực:** `meta_studio.py` + `auto_publisher.py` (V2/V4/V5); mẫu `thumb_50ba645d468b.jpg`
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-04_thumb-prompt-fix\`

## Triệu chứng

Thumbnail upload nhiều ảnh lệch nghĩa: AI nung chữ Việt sai (vd «ẨN NHẪN THÀNH THÁNH» thay vì «Lão Lục…»), UI hologram/stat bar generic, hook sáo «THỨC TỈNH TUYỆT THẾ».

## Root cause

1. `master_image_prompt` JSON mẫu **bắt AI vẽ 3D Vietnamese typography** → model bịa chữ.
2. Fallback cứng `NGHỊCH THIÊN` / `THỨC TỈNH TUYỆT THẾ` + cyan energy.
3. `auto_publisher` lưu nguyên ảnh AI (đã có chữ sai), không overlay hook đã kiểm.

## Fix

- Giữ **AI nung chữ 3D** (không Pillow).
- Badge: chỉ `NEW` / `HOT` — cấm «TRỌN BỘ THUYẾT MINH» (`pick_badge_text`).
- Hook neo tên phim (`sanitize_hook_texts`); prompt ép đúng 2 dòng hook + banner tên.
- `auto_publisher`: lưu ảnh AI trực tiếp (crop 16:9).

## Follow-up (user 03:55)

- Bác scene-only + Pillow: quá tệ / lệch ý cũ.
- Đúng hướng: prompt AI typography như trước, chỉ đổi badge cứng → NEW/HOT.

## Recheck

1. `pytest Z:\PinelineV2\tests\test_meta_and_thumb.py -q`
2. Sinh lại thumb `50ba645d468b`.
3. **Pass nếu:** badge NEW hoặc HOT; headline neo tên (không «ẨN NHẪN»); không badge «TRỌN BỘ THUYẾT MINH».
4. **Fail nếu:** vẫn TRỌN BỘ… hoặc hook bịa.

## Follow-up (user ~04:00) — chữ Việt vỡ + title YT tệ

- **Triệu chứng thêm:** (1) AI nung dấu Việt vẫn sai chữ; (2) title YT khuôn sáo / lệch Baike.
- **Root cause thêm:** Image model không render ổn diacritics; prompt title còn dễ sinh cụm generic.
- **Fix thêm:**
  - `vi_to_image_latin()` — hook/subtitle nung ảnh = ASCII HOA không dấu (metadata/title vẫn giữ dấu).
  - `build_master_image_prompt`: «INTEGRATED 3D LATIN TYPOGRAPHY» + letter-check spell-out.
  - `generate_youtube_titles`: prompt CTR bám Baike, cấm template phim khác / cụm sáo rỗng; 5 góc bắt buộc; fallback neo tên phim.
- **Backup:** `Z:\PinelineV2_codebak\2026-11-04_thumb-latin-title\`
- **Recheck thêm:**
  1. `pytest tests/test_meta_and_thumb.py -q` → 5 passed (V2/V4/V5).
  2. Prompt ảnh chứa «LÃO LỤC…» mà «LAO LUC…»; title JSON không cụm «nghịch thiên cải mệnh» trống.
  3. **Pass nếu:** chữ trên thumb đọc đúng Latin; title có tên riêng + twist Baike.
  4. **Fail nếu:** dấu Việt vỡ trên ảnh hoặc 5 title paraphrase cùng 1 câu.

## Follow-up (user 04:18) — title phải «biết video nói gì»

- User bác ví dụ cũ (liệt kê từ khóa). Mẫu đúng: `Phần 1 | Xuyên Không Thành Nô Lệ: Thức Tỉnh Hệ Thống …, Ta …`.
- **Fix:** công thức `PREMISE : HOOK, Ta PAYOFF`; ví dụ đúng/sai trong prompt; fallback có `, Ta `.
- Backup `Z:\PinelineV2_codebak\2026-11-04_title-prompt-ta\`. Dump: `docs/prompts/title_youtube_prompt_filled.txt`.

## Follow-up (user 05:36) — không tên nhân vật trên title

- Cấm Hứa Hoa / Lão Lục… trong title; dùng thân phận + hệ thống + «Ta».
- Backup `Z:\PinelineV2_codebak\2026-11-04_title-no-charname\`.

## Liên quan

- File mẫu sai: `Z:\PinelineV2\data\thumbnails\thumb_50ba645d468b.jpg`
- Series meta: `data/series_meta/25c822cce9.json`
