# V5 split hết ổ vẫn re-encode / thiếu ENOSPC guard

- **Date:** 2026-11-06
- **Job / khu vực:** `engines/split_parts.py`, `server.py` auto-split, `http_routes/routes_uploader_settings.py`
- **Status:** fixed

## Triệu chứng

Split part trên ổ gần đầy: ffmpeg copy fail → fallback re-encode phình GB thêm; partial `_split_parts` orphan; default PORT/uploader trỏ nhầm V4/8800.

## Root cause

V5 thiếu port từ V2: `DiskFullError` / `assert_enough_space_for_split` / no re-encode-on-ENOSPC / cleanup mid-fail; thiếu `_AUTO_SPLIT_ACTIVE`; `server.py` default `PORT=8800`; uploader defaults `D:\PinelineV4_*`.

## Evidence

- eng-swarm: `docs/reviews/2026-11-06-v5-eng-swarm.md` P0/P1 SAFE
- V2 đã có guard trong `Z:\PinelineV2\split_parts.py` + `tests/test_split_enospc_guard.py`

## Fix

- Backup: `Z:\PinelineV2_codebak\2026-11-06_v5-swarm-autofix\`
- `engines/split_parts.py`: port ENOSPC helpers + `split_video_to_parts` guard + cleanup-on-fail; `split_job_to_subjobs` raise `DiskFullError` + move/space-check
- `server.py`: `_AUTO_SPLIT_ACTIVE` + `_maybe_auto_split_guarded`; default PORT `8805`
- `http_routes/routes_uploader_settings.py`: `WORK_DIR`/`TEMP` → `D:\PinelineV5_work` / `D:\PinelineV5_tmp`
- `tests/test_split_enospc_guard.py` (import `engines.split_parts`)

## Recheck

1. `pytest tests/test_split_enospc_guard.py -q`
2. `rg "DiskFullError|assert_enough_space|_AUTO_SPLIT_ACTIVE|PORT.*8805|PinelineV5_work" engines/split_parts.py server.py http_routes/routes_uploader_settings.py`
3. **Pass nếu:** 3 tests OK; ENOSPC text match; PORT default 8805; WORK/TEMP V5 paths
4. **Fail nếu:** copy fail vẫn luôn re-encode khi stderr có ENOSPC; default vẫn 8800/V4

## Liên quan

- Swarm: `docs/reviews/2026-11-06-v5-eng-swarm.md`
- Không restart servers (user)
