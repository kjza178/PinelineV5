# Review V5 declutter — pass 2 (assets/fs + OpenAPI)

- **Date:** 2026-11-04
- **Scope:** Sau queue/jobs SSOT; không big-bang move pipeline

## Phát hiện

| Mục | Trạng thái trước | Hành động |
|---|---|---|
| `pineline.server.routes.assets` | stub rỗng | → LIVE `attach` (cookies…models) |
| FS `/api/fs/*` | `@app` trên `server.py` | → `routes.fs.attach` |
| Duplicate OpID GET+HEAD | `job_video`, `hg_library_preview` | tách `operation_id` |
| `scripts/_strip*` / `_extract*` | one-shot ở root | archive |
| `scripts/archive/.../node_modules` | ~16 MB | xoá nếu còn |

## Không làm (cố ý)

- Chuyển thân handler jobs/queue vào package (DECISIONS: extractor đã fail)
- Đổi `check_batch*` path V2
- Gộp `/films` + `/meta` process

## Recheck

1. `import server` — không Duplicate Operation ID cho job_video / hg_library_preview
2. OpenAPI có `/api/cookies`, `/api/fs/list-dirs`, `/api/models`
3. Restart :8805 — UI load voices/cookies
