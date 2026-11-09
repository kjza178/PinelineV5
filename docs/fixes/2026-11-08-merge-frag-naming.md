# Merge queue: «need at least 2 episodes» + NVENC -22 ep 第013集

- **Date:** 2026-11-08
- **Job / khu vực:** `hongguo_bridge` merge queue / normalize
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-08_merge-frag-re\`

## Triệu chứng

Log gộp:
- `毒帝无双3D版第五季` — `normalize merge: ep 第013集.mp4` + `h264_nvenc` error -22 / nothing written
- Nhiều series (天羽…, 摊牌…) — `need at least 2 downloaded episodes to merge` dù folder đã có hàng trăm tập / `merged.mp4`

## Root cause

1. `_FRAG_RE` không khớp `S01E001` / `S06E155` (WinUI `fileNames`) → 0 mảnh → gọi Hongguo merge → lỗi «need at least 2…».
2. `_MERGED_RE` chỉ khớp `(merged).mp4`, không khớp `merged.mp4` → không nhận đã gộp.
3. `第013集.mp4` **corrupt** (`Invalid data found when processing input`) → NVENC -22; thiếu `S01E013`.

## Evidence

- ffprobe `第013集.mp4` → Invalid data; `第012/014` OK
- `天羽寿元第6季`: 155×`S06E*.mp4` + `merged.mp4` — trước fix frags=0, merged=False

## Fix

- `_FRAG_RE` + `S\d{1,2}E\d{1,4}`; `_MERGED_RE` + `^merged.(mp4|…)`
- `_list_episode_frags`: dedupe theo số tập, ưu tiên `SxxExxx` + file probe được
- `merge_series_normalized`: bỏ tập unreadable; fallback libx264 nếu NVENC fail

## Recheck

1. `inspect_series_folder(D:\Lib\天羽寿元第6季)` → `merged_file=merged.mp4`, `fragments=155`
2. `inspect(…毒帝…)` → frags dedupe ~226; ep13 corrupt bị skip khi normalize
3. Re-queue gộp 天羽* → không còn «need at least 2…» (đã merged → dọn hoặc done)
4. Re-queue 毒帝 → normalize/merge không chết ngay ở ep13

## Liên quan

- User log 08:55 gộp
