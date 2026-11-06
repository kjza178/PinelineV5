# Films UI: Studio lỗi + SyntaxError Test + poster 404 + toolbar rối

- **Date:** 2026-11-06
- **Job / khu vực:** `:8802/films/ui` · `films_ui.html` · `agent_tele_cmd` · `test_channel`
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-06_films-ui-fix\`

## Triệu chứng

- «⬅ Quay lại Studio» trỏ `/` trên :8802 → JSON Auto-pilot, không vào Studio.
- Thiếu nav rõ sang Hongguo / UI3.
- Console `Uncaught SyntaxError: missing ) after argument list` khi bấm 🛡️ Test (và card render onclick vỡ).
- `/api/hg/poster?name=…` trên :8802 → 404.
- Toolbar nút xếp một hàng rối; Test All khó dùng.

## Root cause

1. Studio `href="/"` — sidecar root ≠ Studio `:8801`.
2. `esc()` không escape `'`; `block_reason` chứa `Command '['ffmpeg'…` → cắt chuỗi trong `onclick="openTestBlockModal('…','…')"`.
3. Sidecar không serve GET `/api/hg/poster` (chỉ :8801 có).
4. Toolbar gom selection + test + filter một hàng.

## Evidence

- Live `/` :8802 = JSON status; poster :8802 404; :8801 poster 200 với tên thật.
- Library `block_reason` có dấu `'` ffmpeg.

## Fix

- Header nav: Studio / UI3 / Hongguo → `:8801`; bỏ `href="/"`.
- Toolbar 3 hàng: Hàng chờ | Test YT | Lọc.
- `jq=JSON.stringify` cho onclick args (Test modal, delete, act cores, meta…).
- Poster: `POSTER` → `http://127.0.0.1:8801/api/hg/poster?name=`; sidecar proxy `/api/hg/poster`.
- `test_channel.stop_batch_test` + `POST /test-channel/batch-stop` + nút ⏹ Dừng test.
- Sync V2/V4/V5; restart sidecar.

## Recheck

1. Hard refresh `http://127.0.0.1:8802/films/ui`.
2. Bấm **Studio** → `:8801/`; **Hongguo** → `/hongguo`; **UI3** → `/ui3`.
3. Card có season `block_reason` ffmpeg → bấm 🛡️ Test → mở modal, **không** SyntaxError.
4. Poster img load (network 200 từ :8801 hoặc :8802 proxy).
5. **Pass nếu:** nav đúng + Test mở modal + poster hiện (hoặc ẩn onerror, không 404 spam nếu có file).
6. **Fail nếu:** Studio vẫn JSON; console SyntaxError khi Test; poster chỉ 404 tuyệt đối khi file tồn tại trên :8801.

## Liên quan

- Drop Hongguo2 trước đó; seasons tab vẫn dùng Hongguo `:8801`.
