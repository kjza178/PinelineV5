# Hardsub bar xanh + encode chậm

- **Date:** 2026-09-24
- **Job / khu vực:** `render.py` hardsub + `-hwaccel cuda`
- **Status:** fixed (tối ưu)

## Triệu chứng

- Bar phụ đề output xanh `(0,G,0)`; source không xanh.
- Mux 2h phim ~0.3–0.5× realtime sau khi thêm geq desat.

## Root cause

1. **Xanh:** `-hwaccel cuda` decode + hardsub overlay/blur → chroma vỡ. Encode NVENC không hwaccel thì sạch. Job cũ “may” sạch vì đôi khi fallback bỏ hwaccel.
2. **Chậm:** vá triệu chứng bằng geq desat luma ×3 kênh/pixel + blur đôi + bar rộng → CPU filter rất nặng.

## Fix (phương án tối ưu)

1. Có `hardsub_blur` → **không** gắn `-hwaccel cuda` (vẫn `h264_nvenc`).
2. Bar: **1× boxblur + `drawbox` đen alpha ≥0.92** — bỏ geq/rgba/desat.
3. Giữ bar cố định giữa (`w≈0.90`) — không tin OCR `x0/x1`.

## Recheck

```bash
# 1) Filter mới không xanh (kể cả ép thử hwaccel)
ffmpeg -y -ss 30 -hwaccel cuda -i work/a948f052b724/source.mp4 \
  -filter_complex_script work/a948f052b724/_filter_complex.txt -map [vout] -t 2 \
  -c:v h264_nvenc -f null -

# 2) Sau remux: đếm pixel xanh đáy output (y>=0.88): expect 0
# 3) Log render có: "hardsub bật → bỏ -hwaccel" và enc=nvenc@… (không nvenc+hwaccel)
# 4) Tốc độ: expect gần ≥1× realtime trên NVENC (lọc nhẹ hơn desat)
```

**Pass nếu:** không còn dải xanh; log bỏ hwaccel khi hardsub; mux nhanh hơn bản desat.

## Follow-up — bo góc

- `drawbox` không bo góc → user thấy góc vuông.
- Đổi lại: blur 1× + `geq` đen `r=g=b=0` + `_rounded_bar_alpha` (radius config).
- Vẫn không desat ×3; vẫn tắt hwaccel khi hardsub.
