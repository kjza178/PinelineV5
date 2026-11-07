# Part mux hiện «Sẵn sàng» trong lúc dò hardsub OCR

- **Date:** 2026-11-07
- **Job / khu vực:** `d693187c7079_p03` (auto-split Part 3/3), `_heal_stale_running`, hardsub track OCR
- **Status:** fixed (code; cần restart :8801 khi idle để nạp heal)
- **Backup:** zip `Z:\PinelineV2_backup_2026-11-07_1817.zip` + `Z:\PinelineV2_codebak\2026-11-07_mux-heal-hstrack\`

## Triệu chứng

UI Part 3: bước Ghép+xuất = **Sẵn sàng**, status dịch = **Chờ**, overall ~80%, trong khi hàng chờ parent vẫn báo `mux 66% · Part 3/3`. User tưởng part không chạy.

## Root cause

1. `_do_render` / `run_render` đánh `mux=running` rồi mới `detect_hardsub_track` (~300 khung RapidOCR, part ~2.5h ≈ **23–26 phút** — đã đo P1/P2).
2. Trong khoảng đó chưa có `ffmpeg` / `output.mp4`.
3. `_heal_stale_running(p03)` chỉ check `_job_any_busy(p03)` — claim thực tế nằm ở **parent** `d693187c7079` (`__all__` / `_AUTO_SPLIT_ACTIVE`) → heal coi part mồ côi → `status=pending` + `healed=stale_running_no_artifact`.
4. Worker vẫn OCR/encode bình thường; UI đọc pending → «Sẵn sàng».

## Evidence

- P1: `hardsub_band` 10:13 → `hardsub_track` 10:39 (~26 phút).
- P2: 14:05 → 14:28 (~23 phút).
- P3: band 17:54:33, track xong 18:19:13 (~25 phút), ngay sau `encode×3` + 4 ffmpeg, progress tăng (16%→34%+).
- Manifest lúc OCR: `healed: stale_running_no_artifact` dù queue `busy=true` current=`d693187c7079`.

## Fix

- `server.py`: `_split_parent_id` + `_job_lineage_busy`; heal bỏ qua khi parent busy / auto-split / còn `_hstrack/hs_*.jpg`.
- `_do_render`: phase `hardsub_track` + `cur_text` trước OCR (không ghi `encode` sớm).
- `render.py` `run_render`: `_mux_phase` giữ `mux=running` lúc dò band/track.
- Sync `server.py` + `render.py` → V2/V4/V5.

## Recheck

1. Chạy mux part dài có hardsub blur (hoặc đợi job sau).
2. Trong ~20 phút OCR: `GET /api/jobs/<part>` → `stages.mux.status=running`, `phase` chứa `hardsub_*`, **không** `healed=stale_running_no_artifact`.
3. Gọi heal/watch trong lúc OCR: status vẫn running.
4. **Pass nếu:** UI Part không nhảy «Sẵn sàng» khi parent queue vẫn Part N; sau OCR thấy `encode×N` / ffmpeg.
5. **Fail nếu:** lại `pending`+`healed` trong khi `_hstrack` còn jpg hoặc parent `_AUTO_SPLIT_ACTIVE`.

## Liên quan

- Job: `d693187c7079` / `_p03`
- Config: `HARDSUB_MODE=track`, `HARDSUB_TRACK_MAX_SAMPLES=300`
- Chờ restart :8801 (cùng đợt hardsub_blur schema) — **không** restart giữa encode P3

## Follow-up — `No module named 'core'` (2026-11-07 ~21:18)

- **Triệu chứng:** mux job `ad50b61b4050_p01` failed: `No module named 'core'`.
- **Root cause:** sync nhầm `engines/render.py` (V5 `from core…`) đè `Z:\PinelineV2\render.py` (flat `from config` / `import assemble`). V2 không có package `core`.
- **Fix:** khôi phục `render.py` từ `…_mux-heal-hstrack\V2_render.py` (đã có `_mux_phase`); copy sang V4. Server reload `render` mỗi mux → **không cần restart**.
- **Recheck:** `python -c "import render"` cwd V2 → OK; bấm lại Ghép+xuất / queue remux `ad50b61b4050_p01`.
