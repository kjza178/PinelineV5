# Helper Pineline leak / lệch WinUI (spawn riêng)

- **Date:** 2026-11-08
- **Job / khu vực:** `hongguo_rpc` / `/hongguo2` / `:8801`
- **Status:** fixed

## Triệu chứng

Attach chung helper WinUI không được → giữ spawn riêng. Nhiều `MainKt` orphan (tele/powershell/reload) + hongguo2 chưa luôn lấy `settings` (saveFolder/quality) như WinUI.

## Root cause

1. `importlib.reload(hongguo_rpc)` / mất handle stdin → orphan JVM.
2. `_ensure_unlocked` khi helper đã sống **không** reap orphan máy → tele/powershell giữ MainKt thứ 2+.
3. Idle mặc định ngắn / kill khi đang tải lệch WinUI (đã siết trước); quality submit không luôn lấy từ `settings.get`.

## Evidence

- Trước: ~104 MainKt parent `agent_tele_cmd` / powershell + 1 WinUI.
- Probe attach: stdio-only, `-XX:+DisableAttachMechanism` (DECISIONS 11-08 FAIL).
- Sau cleanup + singleton: 1× `HongguoWinUI.exe` + 1× `python.exe` (`server.py` :8801).

## Fix

- `hongguo_rpc.py`: `HG_HELPER_SINGLETON` (mặc định 1); reap non-WinUI mỗi `ensure` (kể cả khi helper sống); idle 3600s; không kill khi downloading; pidfile; không reload module từ bridge.
- `hongguo_bridge.py`: `_rpc_mod()` không reload; `settings()` wrapper.
- `routes_hg.py`: `GET /api/hg/settings`.
- `hongguo2.html`: boot `loadHgSettings()` → quality + `libRoot` từ helper (cùng `D:\Lib` / 1080p như WinUI).
- `server.py`: `HG_HELPER_SINGLETON=1`, `HG_BACKEND=rpc`.
- `agent_tele_cmd.py`: bỏ `reload(hongguo_bridge)` ở `/library`.

Backup: `Z:\PinelineV2_backup_2026-11-08_0428.zip`, `Z:\PinelineV2_codebak\2026-11-08_helper-singleton\`.

## Recheck

1. Mở `/hongguo2` (hard refresh) — Browse/Ranking/Downloads; Settings quality khớp helper.
2. `Invoke-RestMethod http://127.0.0.1:8801/api/hg/ping` → `backend=rpc`, `output_dir=D:\Lib`.
3. `…/api/hg/settings` → `saveFolder` / `quality` giống WinUI.
4. Liệt kê MainKt: chỉ WinUI + 1 python (`server.py`). Gọi ping lần nữa — không tăng số helper Pineline.
5. **Pass nếu:** 1 helper Pineline; feed/rank/library/status OK; settings path/quality đúng.
6. **Fail nếu:** >1 MainKt không phải WinUI sau vài lần `/api/hg/*`; hoặc saveFolder ≠ WinUI.

## Liên quan

- DECISIONS 11-08 attach FAIL; keep separate spawn + WinUI-parity behavior.
- Không chia sẻ live download queue với WinUI (stdio riêng).
