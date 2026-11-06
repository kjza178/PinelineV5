# Hardsub chỗ có chỗ không — hở theo thời gian (OCR miss)

- **Date:** 2026-11-04
- **Job / khu vực:** `50ba645d468b` (武道加点：乱世老六成圣) + `render.py` track ranges; V2/V4/V5
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-04_hardsub-gap-fill\` (+ snapshot zip nếu chạy xong)

## Triệu chứng

Phim hardsub đáy gần như suốt tập; output nhiều đoạn chữ Trung vẫn rõ — không phải chỉ lộ 2 mép ngang.

## Root cause

1. `hardsub_track.json` bật che theo `ranges` quanh mẫu OCR. Job `50ba`: 142/300 hit, mỗi cửa sổ ~24s → **~42% thời lượng** có che, **~58% hở** (gap lớn tới ~3 phút).
2. Ngưỡng phủ full video cũ = **85%** mẫu — job này 47% nên không bao giờ full-cover.
3. Config `HARDSUB_FIXED_BOTTOM=1` **có trong JSON nhưng code không đọc** → không ép dải chính phủ cả phim.

## Evidence

- Track `D:\PinelineV2_work\50ba645d468b\hardsub_track.json`: `hits=142 n=300 stride≈27s`, `cov≈3408s / dur≈8166s`.
- Gap lớn: `(1631.7–1825.5)`, `(188.9–355.5)`, nhiều gap ~139s.
- Smoke sau fix: `_hardsub_track_boxes` → `(0,880,1920,106)` + `ranges=[]` (full time).

## Fix

- `_hardsub_track_boxes`: đọc `HARDSUB_FIXED_BOTTOM` — dải chính (`n` lớn nhất) `ranges=[]`.
- `detect_hardsub_track`: `HARDSUB_FULL_COVER_RATIO` mặc định **0.40**; pad/merge rộng hơn; `HARDSUB_GAP_FILL_SEC` (mặc định ~3×stride, cap 120s).
- Config V2/V4/V5: `HARDSUB_FULL_COVER_RATIO=0.40`, `HARDSUB_GAP_FILL_SEC=90`.
- Sync `render.py` 3 bản.

## Recheck

1. Restart server nạp `render.py` (hoặc CLI mux import mới).
2. Remux `50ba645d468b` (hoặc clip thử quanh t≈200s / t≈1700s — trước đây nằm trong gap).
3. **Pass nếu:** đáy full ngang bị che suốt đoạn có chữ Trung (kể cả chỗ OCR miss).
4. **Fail nếu:** vẫn còn đoạn dài chữ Trung rõ không bị stretch/blur.

## Liên quan

- Cùng cụm mép ngang: `docs/fixes/2026-11-04-hardsub-partial-cover.md`
- Jobs cùng series: `08b42394b0d8`, `9a8ef098d971` (cũng ~46% cover theo track cũ)
