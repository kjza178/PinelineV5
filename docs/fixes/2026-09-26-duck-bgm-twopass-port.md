# 2026-09-26 — Port duck/duck_bgm two-pass sang PinelineV2

## Root cause
`sidechaincompress` trong cùng `filter_complex` với encode video (ffmpeg 7.1.1)
→ audio EOF sớm (~1853s+) trong khi video đủ dài.

## Fix (V2 `render.py`)
1. `_uses_sidechain` + `_ensure_mixed_audio`: pass1 ghi `mixed_audio.wav` (audio-only).
2. Pass2 encode video + `-map 1:a` (không sidechain trên graph video).
3. `voice_bgm` / `duck_bgm`: `-stream_loop -1` + `amix duration=first` (bỏ `aloop` + `longest`).

## Agent
- `agent_av_sync`: invalidate `mixed_audio` khi heal; `scan_av_sync` / `heal_av_sync_batch`.
- `agent_core`: tools `pineline_av_sync_scan` / `pineline_av_sync_heal_batch`.

## Note
Job series S1–7 hiện nằm dưới `Z:\Pineline\work` (V1). Remux runtime có thể
`python -c "from render import run_render; run_render(r'Z:\\Pineline\\work\\<id>', force=True, ...)"`
từ cwd `Z:\PinelineV2` sau khi GPU rảnh.
