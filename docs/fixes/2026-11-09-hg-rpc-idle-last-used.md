# hg-rpc-idle crash UnboundLocalError `_last_used`

- **Date:** 2026-11-09
- **Job / khu vực:** `hongguo_rpc._idle_watch` (thread `hg-rpc-idle`)
- **Status:** fixed

## Triệu chứng

Log server:

```
Exception in thread hg-rpc-idle:
UnboundLocalError: cannot access local variable '_last_used' where it is not associated with a value
```

Thread idle chết → không auto-kill helper Hongguo khi idle; server HTTP vẫn chạy.

## Root cause

Trong `_idle_watch`, gán `_last_used = time.time()` khi còn download active khiến Python coi `_last_used` là **local** trên cả hàm. Lần đọc `time.time() - _last_used` trước khi gán → `UnboundLocalError`. Thiếu `global _last_used`.

## Evidence

- Traceback: `Z:\PinelineV2\hongguo_rpc.py` line ~1431 (`if time.time() - _last_used <= _IDLE_SEC`).
- Module đã có `_last_used = 0.0` ở top-level (line ~48) nhưng không `global` trong `_idle_watch`.

## Fix

- Thêm `global _last_used` đầu `_idle_watch`.
- Sync: `Z:\PinelineV2\hongguo_rpc.py`, `Z:\PinelineV4\hongguo_rpc.py`, `Z:\PinelineV5\hongguo_rpc.py`, `Z:\PinelineV5\agents\hongguo_rpc.py`.
- Codebak: `Z:\PinelineV2_codebak\2026-11-09_hg-rpc-idle-last-used\`.

## Recheck

1. Restart :8801 (đã — PID mới sau mtime file).
2. Import / gọi soft: để idle thread chạy ≥30s không traceback.
3. **Pass nếu:** không còn `Exception in thread hg-rpc-idle` / `UnboundLocalError` sau boot; `threading` vẫn có tên `hg-rpc-idle`.
4. **Fail nếu:** traceback lặp lại trong vòng 1 phút sau start.

## Liên quan

- `_IDLE_SEC` / env `HG_RPC_IDLE_SEC` (mặc định 3600)
- OpenAPI duplicate operation-id + `GET /api/gpu` 404 trong cùng log paste = cảnh báo riêng, không cùng root cause
