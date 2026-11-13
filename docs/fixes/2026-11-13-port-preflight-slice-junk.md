# Port V2→V5: preflight/chuẩn hoá video nguồn + extract_pcm bền + FireRed slice khoảng lặng + câu rác «None.» / parent chờ part

- **Ngày:** 2026-11-13 · **Agent:** Q5 · **Cây:** `Z:\PinelineV5` (bố cục package) · **Nguồn:** `Z:\PinelineV2` (chỉ đọc)
- **Nguồn V2:** `docs/fixes/2026-11-12-video-preflight.md` (agent K + mục C agent K2), `2026-11-13-firered-slice-silence.md` (agent L), `2026-11-13-simple-junk-park.md` (agent M); `media_ts.extract_pcm_from_video` + chỗ gọi trong `asr.py`/`separate.py` (chủ dự án, 12/11 trước K); `server.py` cur_text parent «đã ghép từ N parts» (chủ dự án).
- **Backup:** `Z:\PinelineV5\.backup_edit_20261113_agentQ5\` (bản gốc từng file, giữ đường dẫn; `_md5_before.txt`, `_md5_after.txt`; `_transfer\` = gói chuyển). File mới không có bản gốc.
- **Status:** trên đĩa V5. **Cần restart :8805** (server: import/`_find_video`/part-parent, dịch simple). ASR/Demucs/OCR chạy tiến trình con → hiệu lực ngay job sau.

## Cách port
3-way merge (`git merge-file`) từng file: base = backup V2 trước thay đổi (đi qua `scripts/sync_from_v2.rewrite_imports` + `rewrite_file_paths` + `add_bootstrap`), ours = V5, theirs = V2 hiện tại (cùng biến đổi). 0 xung đột.

| V2 | V5 | Base | Ghi chú |
|---|---|---|---|
| `media_ts.py` | `engines/media_ts.py` | — | V5 = V2 trước `extract_pcm_from_video` (chỉ thiếu phần thêm) → lấy nguyên bản V2 (extract_pcm + fix K/K2: tol 1 s, overlong, `_force_wav_frames`, `_decode_errors`, `_dead_zero_run`, khúc con 5 s) |
| `asr.py`, `separate.py` | `engines/asr/asr.py`, `engines/separate.py` | `F5 _transfer/v2_src.tgz` | extract_pcm (chủ dự án) + resolver nguồn (K) |
| `ocr.py`, `hardsub_asr.py`, `render.py`, `mux.py`, `split_parts.py`, `download.py`, `agent_av_sync.py` | `engines/…`, `engines/asr/hardsub_asr.py`, `agents/agent_av_sync.py` | `.backup_edit_20261112_agentK` | `stage_source_video`/`resolve_source_video`; `download_video` → `after_download` |
| `firered_asr.py` | `engines/asr/firered_asr.py` | `.backup_edit_20261113_agentL` | slice tại khoảng lặng + đệm chồng lấn (L) + lọc câu rác (M) |
| `translate_simple/{cfg,pipeline,stage_review,validate}.py` | `engines/translate_simple/` | `.backup_edit_20261113_agentM` | `_mark_junk`, lượt review câu thiếu, `SIMPLE_UNREVIEWED_TOLERANCE`, `SIMPLE_MISSING_BATCH` (cfg giữ `pipeline_default`/`job_pipeline` của P5) |
| `server.py` | `server.py` | `.backup_edit_20261112_agentK` | `_finalize_imported_source` (`preflight_pending`), `_find_video` chỉ đọc qua resolver, `_SPLIT_WAIT`/`_split_wait_clear`/`_split_wait_parts`/`_split_wait_ready`, `_queue_park_ready`, `_check_and_run_auto_split_parts`, `_run_merge`; + hunk chủ dự án cur_text parent (chép tay — nằm trước mốc backup K) |
| MỚI `source_preflight.py`, `text_junk.py` | `engines/source_preflight.py`, `engines/text_junk.py` | — | |
| MỚI `tools/preflight_scan.py`, `tools/asr_boundary_scan.py` | `tools/` | — | `asr_boundary_scan` mặc định quét `work/` của V5 (V2: `D:/PinelineV2_work`) |
| tests | `tests/` | M (2 file cũ) | MỚI `test_video_preflight` (13), `test_extract_pcm_robust` (2), `test_extract_pcm_timing` (21), `test_firered_slice_silence` (9), `test_simple_junk_park` (43); `test_translate_simple.py` + `_scenarios.py` mỗi file 1 ca `SIMPLE_UNREVIEWED_TOLERANCE=0` |

**Không port (ngoài phạm vi, giữ hành vi V5):** translate-b2/b3 (`_translate_gate_action`, `_park_fill_pending`), `LIBRARY_DIR` khác biệt — đã có sẵn ở V5.
Ghi manifest trong code mới: `Manifest.update` (như V2). Nhánh heal parent cũ vẫn `m_fix.save()` (có sẵn).

## Cờ (env > `pineline.config.json` > mặc định, không đổi file config)
`VIDEO_PREFLIGHT=1`, `VIDEO_NORMALIZE=1`, `VIDEO_NORMALIZE_DRIFT=0`, `EXTRACT_FULL_TOL_SEC=1.0`; `FIRERED_SLICE_SEC=1200` (0 = 1 lượt), `FIRERED_CUT_SEARCH_SEC=60`, `FIRERED_SILENCE_DB=-40`, `FIRERED_MIN_SILENCE_SEC=0.3`, `FIRERED_SLICE_PAD_SEC=2`, `FIRERED_SLICE_PAD_NOSIL_SEC=10`; `SIMPLE_UNREVIEWED_TOLERANCE` (trống = max(3, 0.2 %); 0 = tắt), `SIMPLE_MISSING_BATCH=4`.
**Rollback:** `VIDEO_PREFLIGHT=0`; `SIMPLE_UNREVIEWED_TOLERANCE=0`; code: chép lại từ backup + chuyển file mới vào `_to_delete\`.

## Evidence / Recheck
- Bản sao Linux (Python 3.13, ffmpeg 6.1.1, stub fastapi/soundfile/yt_dlp/google): toàn bộ `tests/` trước **25 failed / 315 passed / 4 skipped / 3 errors** → sau **25 failed / 403 passed / 4 skipped / 3 errors**, danh sách FAILED/ERROR y hệt (môi trường stub/drift đã biết). 5 file mới: 88 passed.
- `py_compile` OK; `scripts/tree_audit.py` ERROR=0 (trước/sau như nhau); import smoke `server`, `engines.source_preflight`, `engines.text_junk`, mọi module đã sửa OK; `--help` của `tools/preflight_scan.py`, `engines/source_preflight.py`, `tools/asr_boundary_scan.py` chạy được.
- Windows: `Z:\PinelineV6\scripts\test_v5_simple_demucs.bat` (bản sao `%TEMP%\pv5_test`, ffmpeg 8.1.2 gyan.dev) — kỳ vọng [1] 14 file **248 passed / 4 skipped / 0 failed**; [2] FAILED không tăng.
- Recheck: **Pass** (bản sao) · **chờ** Windows + restart :8805.

## Recheck sau restart :8805
1. Import 1 video lành → manifest `download.preflight_pending=true`; chạy ASR → log `[preflight] nguồn lành`, không có `source_norm.*`.
2. `python tools\preflight_scan.py --quick` → bảng job, không file nào trong `work\` đổi.
3. ASR FireRed job dài → log `[firered] N slice, cắt tại khoảng lặng: …`; `python tools\asr_boundary_scan.py` cho job cũ.
4. Job split có part park (simple soát dở) → parent `agent.held_at=split_parts`, hàng đợi giữ ghế, không ghép hụt.

## Liên quan
V2: 3 file fix ở trên. V5: `docs/fixes/2026-11-12-port-simple-demucs.md`, `2026-11-12-port-brain-hold-pipeline.md`.
