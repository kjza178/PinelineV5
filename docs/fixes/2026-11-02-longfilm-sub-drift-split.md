# Phim dài ~12h lệch khung sub — nguyên nhân + split_parts

- **Date:** 2026-11-02
- **Job / khu vực:** ASR → assemble → mux; job merged nhiều tập 3–14h
- **Status:** fixed (công cụ + **auto-detect** trong queue/run-all; root cause lệch tích lũy đã biết từ trước)

## Triệu chứng

Phim dài (đặc biệt ~12h, thường là file gộp nhiều tập AAC) — phụ đề / tiếng Việt lệch khung hình, càng về cuối càng lệch nhiều.

## Root cause (không phải một bước duy nhất)

Lệch **tích lũy** theo thời gian; các nguồn đã chứng minh trên V2:

1. **Nguồn merged (AAC priming)** — mỗi chỗ nối tập giữ ~1024 mẫu mồi AAC (~23 ms). Giải mã không `aresample` → `audio.wav` dài hơn hình; lệch tăng theo số chỗ nối (job `0281` 14,5h: **+25 s** cuối). Module: `media_ts.py` (`AUDIO_TS_FIX`, `ensure_job_audio_ts`). **Stage bị ảnh hưởng:** mọi thứ đọc mốc từ audio (ASR → script → TTS → sub burn).
2. **ASR trên file siêu dài** — VAD/engine dễ lệch dần; SenseVoice từng có mốc giả (review 6/10). Demucs chunk 1h giảm OOM nhưng ranh giới khúc vẫn rủi ro nhỏ.
3. **Assemble FIT** — nén tốc độ câu để khớp khe; trên file dài sai số nhỏ cộng dồn (review M5/M6).
4. **Hardsub sample thưa** — stride lớn trên 12h (không phải lệch sub, nhưng che sai vị trí).

**Kết luận vận hành:** với phim ≥ ~3h (nhất là gộp nhiều tập), **đừng chạy 1 job 12h end-to-end** — chia part ~2–2.5h rồi merge.

## Evidence

- `docs/STATE.md`: `0281a4c6ad6e` +25,37 s AAC priming; job khác ±0,7–11 s.
- `docs/worklog/2026-10-05.md`, `media_ts.py` docstring.
- `split_parts.py` header: thiết kế chống lệch time trên 3–12h+.

## Fix (đợt này)

- Port `split_parts.py` + API:
  - `GET /api/jobs/{id}/split-plan` (+ `will_auto_split`)
  - `POST /api/jobs/{id}/split-parts?target_hours=2.5`
  - `POST /api/jobs/{id}/merge-parts`
- **Auto (03:21):** `batch_config.auto_split` (mặc định bật). Sau download/có source, `_queue_run_one` / `_auto_pipeline` gọi `maybe_auto_split_job`: ≥ `auto_split_min_h` (3h) → chia ~`auto_split_hours` (2.5h)/part, xếp sub-job, **không** ASR cả file 12h. Part mux xong + `auto_merge` → `try_auto_merge_parent` → `output_full.mp4`.
- Tắt: `/set auto_split=off` hoặc `auto_merge=off`.
- Cùng đợt: queue `sort|move|reorder`; `POST /meta/generate-title`.
- Vẫn dùng `AUDIO_TS_FIX` khi extract; job cũ có thể `python media_ts.py --check` / ensure khi render lại.

## Recheck

1. Job ~12h đã có video: `GET .../split-plan` → `will_auto_split: true`, ~5 part.
2. Xếp hàng job cha (hoặc run-all) với `auto_split=on` → lịch sử queue status `split`, xuất hiện `{id}_p01`…
3. Chạy hết part → tự có `output_full.mp4` trên job cha (`auto_merge`).
4. **Pass nếu:** không ASR nguyên 12h; part độc lập; merge OK.
5. **Fail nếu:** vẫn chạy 1 job 12h dù ≥3h; thiếu sub-job; merge không chạy khi đủ part.

## Liên quan

- Backup: `Z:\PinelineV2_codebak\2026-11-02_v4-split-queue\`
- `media_ts.py`, `agent_av_sync.py` (`audio_ts_drift`)
