# output.mp4 hết tiếng giữa chừng (A/V gap) — duck_bgm

- **Date:** 2026-09-25
- **Job / khu vực:** `87499c18fdc5` (cũng `a948f052b724`, `d1b54f72eeed`) · mux/`render.py` duck_bgm
- **Status:** fixed (code); remux job cũ — chờ user

## Triệu chứng

`output.mp4` status mux=`done` nhưng **mất tiếng sau ~31 phút** trong khi hình vẫn chạy tới hết (~2h). API overall 100% nên dễ tưởng ổn.

## Root cause

1. `duck_bgm` / `voice_bgm` dùng `-stream_loop -1` trên file BGM ngắn (~371s) + `amix=duration=first` + **`-shortest`** trên encode.
2. Trên phim dài, audio stream trong container bị cắt sớm; gap khớp ~N× độ dài BGM (`1852 ≈ 5×371` trên job 87499).
3. `dub_fit.wav` vẫn đủ dài (~7268s) — lỗi ở bước mux, không phải TTS.

Evidence (87499c18fdc5):

| Stream | Duration |
|--------|----------|
| source | 7271.7s |
| dub_fit.wav | 7267.7s |
| output video | 7248.0s |
| output audio | **1852.2s** |

Cùng pattern: `a948` gap~3022s, `d1b5` gap~6121s (cũng duck_bgm).

## Fix

- `render.py`: bỏ `-stream_loop`; loop BGM bằng `aloop` trong filter; `amix=duration=longest`; bỏ `-shortest`; thêm `-t` = độ dài video nguồn.
- Áp cả `voice_bgm` và `duck_bgm`; path retry NVENC tương tự.

## Recheck

1. Remux 1 job ngắn hoặc `87499c18fdc5` với `audio_mode=duck_bgm` (force).
2. `ffprobe` so sánh `stream=video/audio duration` — gap < 1s.
3. Nghe sau mốc ~40 phút (trước đây im).

**Pass nếu:** `|dur_v - dur_a| < 2s` và có tiếng tới cuối.  
**Fail nếu:** audio vẫn cắt sớm ≈ N× BGM.

## Liên quan

- Jobs: `87499c18fdc5`, `a948f052b724`, `d1b54f72eeed`
- BGM: `assets/bgm/su_thanh_hoa_segmented_layered.m4a` (~371s)
- Config mux lúc đó: duck_bgm, orig~0.28, bgm0.14, dub1.55, flip=h, zoom=1.1, 4M
