# Auto-pub «Phần Cuối» thành «Phần 1 | Xuyên Không Thành Nô Lệ…» (+ nhiều draft YT)

- **Date:** 2026-11-07
- **Job:** `67c6385ce47e` (Võ Đạo… Phần Cuối)
- **Status:** fixed (parser + publish path); draft YT thừa — xoá tay trên Studio
- **Backup:** zip `Z:\PinelineV2_backup_2026-11-07_0842.zip`; codebak `Z:\PinelineV2_codebak\2026-11-07_season-cuoi\`

## Triệu chứng

Studio hiện ~4 video title gần giống `Phần 1 | Xuyên Không Thành Nô Lệ…` khi đang auto-pub Phần Cuối. Log upload: job `67c6385ce47e` gắn title Phần 1 (video `hBmqYaxxpUg`).

## Root cause

1. `job_queue._parse_season_from_text` không nhận «Phần Cuối» → default `season=1`.
2. Series `Võ Đạo Cộng Điểm` đã có shared meta premise «nô lệ / xuyên không» → `generate_part_metadata(season=1)` sinh title Phần 1.
3. GPT trả ~4–5 biến thể title; retry/resumable `videos.insert` mới có thể để lại draft «Processing» thừa trên Studio (Pineline chỉ log 1 URL thành công).

## Fix

- Parse `Phần Cuối` → `season=-1`.
- `format_youtube_title(..., -1)` → prefix `Phần Cuối |`.
- Auto-pub: nếu cuối → giữ `title_vi` + master thumb/tags, không gọi part-meta season 1.
- Sync V2→V4/V5.

## Recheck

1. `get_job_info('67c6385ce47e')['season'] == -1`
2. `format_youtube_title(..., season=-1)` bắt đầu `Phần Cuối |`
3. **Pass nếu:** publish lại Phần Cuối không ra «Phần 1 | Xuyên Không…»
4. **Fail nếu:** vẫn season=1 / title premise S1

## Liên quan

- Studio: xoá draft Pending trùng; sửa title video đã up nếu cần.
