# Part sau split dùng sai giọng (NgayCuoi thay vì v1)

- **Date:** 2026-11-05
- **Job / khu vực:** `_resolve_voice` / `split_job_to_subjobs` — V2/V4/V5
- **Status:** fixed (cần restart server)

## Triệu chứng

Video dài auto-split → part TTS giọng khác config batch/queue (vd set `v1` nhưng part đọc `NgayCuoi`).

## Root cause

`queue_opts.voice` được copy sang part, nhưng `_auto_gpu` gọi `_resolve_voice(wd, None)` chỉ đọc `stages.tts` / `tts_config` rồi **fallback `list_clone_voices()[0]`** (= `NgayCuoi`). Không đọc `queue_opts`.

## Evidence

- `d01dbbc2d703` queue_opts `v1`; p01–p04 `stages.tts.voice=NgayCuoi` speed 1.0; batch_config `voice=v1` speed 1.1.

## Fix

- `_resolve_voice` / speed / tts_engine: đọc `queue_opts`+`opts` trước list[0].
- `split_job_to_subjobs`: seed `stages.tts` + `tts_config.json` từ parent.
- Backup: `Z:\PinelineV2_codebak\2026-11-05_split-voice-queue-opts\`

## Recheck

1. Restart :8801/:8804/:8805.
2. Split job mới với voice `v1` → part `stages.tts.voice` / `tts_config` = `v1` trước khi TTS.
3. **Pass nếu:** log TTS / `tts_config.json` khớp queue_opts.
4. **Fail nếu:** vẫn `NgayCuoi` khi queue_opts=`v1`.

## Liên quan

- Job mẫu: `d01dbbc2d703_p01…p04` (đã render sai giọng — remux cần TTS lại nếu muốn sửa).
