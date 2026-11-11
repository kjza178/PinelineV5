# Nới REVIEW Aurora — văn phong tự nhiên khi vá lỗi

- **Date:** 2026-11-10
- **Job / khu vực:** `review_batch` / `_style_voice_banner` · 60892 re-review
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-10_review-voice-loosen\`

## Triệu chứng

User muốn prompt kiểu biên dịch Donghua (nghĩa + sắc thái + xưng hô) nhưng pipeline là NMT chính + REVIEW vá lỗi — không dịch lại 100%.

## Root cause

REVIEW system prompt «TỐI THIỂU / GIỮ NGUYÊN» không nêu lớp văn phong tự nhiên khi *phải* sửa → dễ vá máy hoặc bỏ sót calque (脆皮/分手补偿…).

## Fix

- `review_batch` sys: biên tập Donghua; khi sửa → nghĩa + ngữ cảnh + sắc thái/xưng hô; ví dụ calque cứng; vẫn CẤM rewrite chỉ vì hay hơn.
- `_style_voice_banner`: thêm dòng «khi phải sửa → thoại phụ đề tự nhiên».
- Restart CLI REVIEW `chatgpt/gpt-6` p01/p02 với prompt mới.

## Recheck

1. Log `[review] Model=chatgpt/gpt-6`.
2. Sau vài lô: i≈15/47/50 không còn «Chia thường» / «da mỏng» / «vận hành viên».
3. **Pass nếu:** lỗi nghĩa được sửa tự nhiên; câu NMT ổn không bị đổi đồng nghĩa hàng loạt.
4. **Fail nếu:** rewrite hàng loạt hoặc vẫn để calque mẫu trên.

## Liên quan

- User chọn option 1. Model `chatgpt/gpt-6`.
