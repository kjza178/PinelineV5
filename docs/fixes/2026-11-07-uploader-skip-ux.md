# Skip đang upload khó tìm — UX sticky + Done; cảnh báo file >11.5h

- **Date:** 2026-11-07
- **Job / khu vực:** Films UI (`/films/ui`), `/api/uploader/skip-current`, `yt_uploader` `skip_current.flag`, auto-publish oversized
- **Status:** fixed (UI live; Python API chờ restart :8802 khi idle)
- **Backup:** zip `Z:\PinelineV2_backup_2026-11-07_0109.zip` · codebak `Z:\PinelineV2_codebak\2026-11-07_skip-upload-ux\`

## Triệu chứng

User cần bỏ qua file đang upload (YouTube từ chối file quá dài) nhưng không thấy nút Skip — chỉ nằm trên tab **Đăng YouTube**. Khi `is_running=false` / `queue=[]` nút trên tab Uploader trông như «chết». Swarm trước đó tập trung blur, bỏ sót UX Skip.

## Root cause

1. **UX:** `⏭ Skip đang upload` chỉ render trong `#p-upload` — user ở tab Done / Lib không thấy.
2. **API path OK:** `uploader_settings_api.skip_current_upload` → ghi `Z:\yt_uploader\skip_current.flag`; `yt_uploader.consume_skip_flag()` trong vòng `next_chunk` đã có từ trước.
3. **Khi idle:** GET `/api/uploader/status` → `is_running=false`, `queue=[]` → skip trả 400 «Không có video đang upload» (đúng). Desktop GUI vẫn skip được qua flag nếu process đang chạy (kể cả queue trống).
4. **JS queue shape:** status dùng `queue` (không phải `items`) — `loadUploader` đã đọc `queue`; harden thêm `queue || items`.

## Evidence

- Live: `POST /api/uploader/skip-current` → `{"ok":false,"error":"Không có video đang upload"}` khi idle.
- `GET /films/ui` sau patch: chứa `up-skip-banner` + `hdr-skip-upload`.
- `yt_uploader.py`: `consume_skip_flag` + check trong upload loop (~L721).

## Fix

- **films_ui.html:** sticky `#up-skip-banner` (mọi tab); nút header `hdr-skip-upload`; Done auto-pub bar + batch bar Skip; poll `loadUploader` 4s; `queue||items`; enqueue/quickUpload/combine confirm file >11.5h / ≥64GiB.
- **uploader_settings_api.py:** `allow_huge` trên enqueue; skip message rõ khi GUI chạy / queue trống.
- **auto_publisher.py** (+ V5 `agents/`): refuse auto-publish oversized trừ `allow_oversized`; trigger API nhận flag.
- **agent_tele_cmd / agent_feeder / V5 routes:** wire `allow_oversized`.
- Sync UI → V4/V5 (+ `static/ui`).

## Recheck

1. Hard refresh `http://127.0.0.1:8802/films/ui`.
2. Khi yt_uploader đang upload: banner đỏ sticky hiện + header Skip + Done bar Skip; bấm → tạo `Z:\yt_uploader\skip_current.flag`, item → «bỏ qua».
3. Idle: Skip → toast lỗi rõ; banner ẩn.
4. Enqueue / auto-publish job `duration_sec > 41400`: toast + confirm (manual) hoặc refuse (auto).
5. **Pass nếu:** Skip thấy được ngoài tab Uploader khi đang upload; flag được yt_uploader consume.
6. **Fail nếu:** vẫn phải săn tab Uploader; hoặc skip không dừng upload khi process chạy.

## Liên quan

- Prior: `docs/fixes/2026-11-07-uploader-settings-8802.md`
- Keys: `skip_current.flag`, `YT_MAX_DURATION_SEC=41400`, `allow_oversized` / `allow_huge`
- **Chờ restart :8802** khi idle (auto-pub state từng báo `uploading`) để nạp Python API mới; UI HTML đã live.
