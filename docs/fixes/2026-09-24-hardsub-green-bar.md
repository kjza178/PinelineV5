# Hardsub bar lộ xanh / lệch nửa khung

- **Date:** 2026-09-24
- **Job / khu vực:** `a948f052b724`, `render.py` hardsub blur bar
- **Status:** fixed (code cứng); remux full a948 chưa chạy lại sau khi user tắt build

## Triệu chứng

Output burn-in có dải xanh trong/cạnh bar phụ đề Việt; đôi khi chỉ nửa phải bar xanh + chữ TQ lộ. User khẳng định **file gốc không có nền xanh**.

## Root cause

1. **Xanh không có trong source** — filter tự sinh: `boxblur` + lớp đen alpha ~0.78 + `overlay:format=rgb` làm chroma vỡ → pixel kiểu `(0, 50, 0)`.
2. **Bar lệch/hẹp** — OCR `hardsub_band.json` tin `x0/x1` theo glyph CJK (vd a948: `x≈0.02–0.84`), không phủ hết vùng chữ → nửa bar “lòi”.

## Evidence

```text
# source @30s: green_hits = 0
# output cũ @30s: green_hits ~10k+, worst (0, 52, 0)
# band cache a948: y 0.82–0.99, x 0.02–0.84 (lệch)
```

Probe sau fix (desat + α≥0.94, bar cố định giữa): bottom bar ~`(2,2,2)`, `greenish_samples = 0`.

## Fix

- `render.py` `_hardsub_bar_filter`: blur **khử màu** (luma cap 48) + `HARDSUB_BAR_ALPHA` sàn **≥ 0.94**.
- Bar vị trí **code cứng**: `w_frac=0.90`, `h_frac=0.13`, `y1=0.985`, `fixed=True` — bỏ tin OCR ngang.
- `pineline.config.json`: alpha/w/h cập nhật tương ứng.

## Recheck

1. Remux 1 job có hardsub TQ đáy (vd `a948f052b724`) với code hiện tại.
2. So frame cùng timestamp:

```bash
ffmpeg -y -ss 30 -i work/<job>/source.mp4 -frames:v 1 -update 1 _src.jpg
ffmpeg -y -ss 30 -i work/<job>/output.mp4 -frames:v 1 -update 1 _out.jpg
```

3. Đếm pixel xanh đáy (`g > r+25 && g > b+25 && g > 40` trên y≥0.78).
4. Kiểm filter: `crop=…` rộng ~90% canvas, có `0.299*r` (desat), alpha black ≥ `242`.

**Pass nếu:** source và output đều không có cụm xanh thuần trong vùng bar; chữ TQ bị phủ; VI đọc được.

**Fail nếu:** còn `(0, G, 0)` trong bar, hoặc bar hẹp lệch phải/trái như band OCR cũ.

## Liên quan

- Job: `a948f052b724`
- Config: `HARDSUB_FIXED_BOTTOM`, `HARDSUB_BAR_ALPHA`, `HARDSUB_BLUR_W/H`
- Remux full bị user **tắt build** — cần remux lại khi muốn thay `output.mp4`
