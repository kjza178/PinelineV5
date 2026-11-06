# sfx_lib: audio trộn có lúc hụt đuôi (sidechaincompress kết thúc sớm)

- **Ngày:** 2026-10-07
- **Nguồn:** test `tests/test_sfx_lib.py::test_render_filter_sfx_lib_runs` chập chờn khi chỉnh âm lượng theo yêu cầu user.
- **Mức:** P1 cho `sfx_lib` (chưa job thật nào render bằng `sfx_lib`). Không ảnh hưởng `duck` (đã `duration=longest`); 4 job `duck` thật có `mixed_audio.wav` dài đúng bằng video.

## Triệu chứng

Cùng đầu vào (tiếng động 6 s, nhạc kho 6 s, dub 2 s, có input video không map), pass 1 `sfx_lib` lúc ra 6,0 s, lúc ra 4,8–5,9 s (khoảng 30% lần chạy, ffmpeg 8.1.2). Bản trước khi chỉnh cũng bị — test qua trước đó là do may.

## Root cause

`sidechaincompress` có lúc kết thúc sớm khi sidechain (dub đã `asplit` + `apad`) ngắn hơn input chính; riêng nhánh `[fxd]` hoặc `[bgd]` cũng hụt. `amix=duration=first` lấy `[fxd]` làm mốc nên hụt theo. Chỉ thấy khi có input video trong lệnh (đúng như pass 1 thật).

## Sửa

`render.py` `_build_audio_filter`, nhánh `sfx_lib`: dub `apad=whole_dur=<độ dài sfx_effect.flac>` trước `asplit` (cả 2 sidechain và nhánh giọng cùng dài bằng stem), `amix=duration=longest`. Độ dài vẫn có giới hạn kể cả không có `-t`.

Đo: 60/60 lần đủ 6,0 s, đuôi có tiếng (có và không `-t`). Test `test_render_filter_sfx_lib_runs` giờ chạy 8 lần liên tiếp không `-t`; lặp cả file 5 lần đều xanh. Pytest 93/93.

Cùng đợt (user chỉnh mẫu): limiter `alimiter=limit=0.89` sau `amix` (mẫu E peak −0,4 dBFS), mặc định `RENDER_SFX_VOL` 0,5→0,62, `RENDER_LIB_BGM_VOL` 0,35→0,25, key mới `RENDER_SFX_VOICE_BOOST` (1,25 × `RENDER_DUB_VOL`). Test mới `test_render_filter_sfx_lib_limits_peak`.

## Còn treo

`duck_bgm` cũng `amix=duration=first` sau `sidechaincompress` → cùng rủi ro; chưa sửa (không dùng trong CONFIG BATCH).

## Recheck

`python -m pytest -q tests/test_sfx_lib.py` lặp vài lần; với job thật: độ dài `work/<job>/mixed_audio.wav` = `source.mp4`.

Backup: `Z:\PinelineV2_codebak\2026-10-07_sfxlib_tune\` + zip `Z:\PinelineV2_backup_2026-10-07_0245.zip`.
