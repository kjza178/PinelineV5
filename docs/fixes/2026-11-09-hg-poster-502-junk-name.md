# `/api/hg/poster` 502 với job_id / `downloads`

- **Date:** 2026-11-09
- **Job / khu vực:** Films UI poster + `film_db.hg_name` + `routes_hg.hg_poster`
- **Status:** fixed
- **Backup zip:** `Z:\PinelineV2_backup_2026-11-09_1402.zip`
- **Codebak:** `Z:\PinelineV2_codebak\2026-11-09_hg-poster-502\`

## Triệu chứng

Log :8801 spam `GET /api/hg/poster?name=1e2379edb4fe_p01` / `…_p02` / `9c3af…` / `downloads` → **502 Bad Gateway**, trong khi tên series Trung (Lib) vẫn 200.

## Root cause

1. `film_db.row_from_manifest` lấy `hg_name = Path(orig_path).parent.name`.
2. Split part: `orig_path = work/<job>_p01/….mp4` → `hg_name` = **job id**.
3. Import bilibili: `…\downloads\5.mp4` → `hg_name` = **`downloads`**.
4. Films UI: `posterName = f.hg_name || …` → gọi poster với tên junk → không có folder `D:\Lib\<name>` → `fetch_poster` raise → route trả **502** (lẽ ra 404).

## Evidence

- `films.db`: `1e2379edb4fe_p01.hg_name='1e2379edb4fe_p01'`; `9c3af49061a2.hg_name='downloads'`.
- Parent `1e2379edb4fe.hg_name='仙界归来家人竟护了我十年肉身第二季'` + `D:\Lib\…\poster.jpg` → 200.
- Probe: junk name → 502; series name → 200.

## Fix

- `film_db.derive_hg_name` / `is_junk_hg_name`: bỏ job folder / downloads / số ngắn; part kế thừa parent; strip ` - Phần N/M`.
- `split_parts`: ghi `request.hg_name` từ parent khi tạo sub-job.
- `routes_hg` + `hongguo_bridge.fetch_poster`: junk/missing → **404** (không 502).
- `films_ui.resolveFilmPosterName` + `auto_publisher` cùng logic.
- Heal DB: 6 hàng junk đã patch (`1e2379…_p*` → tên series; bilibili → `''`).

## Recheck

1. Hard refresh Films UI (`:8802/films/ui`).
2. `GET /api/hg/poster?name=1e2379edb4fe_p01` → **404** (sau restart :8801); `?name=仙界归来家人竟护了我十年肉身第二季` → **200**.
3. Hàng part `1e2379…_p01` hiện poster series (không broken-image spam 502).
4. **Pass nếu:** không còn 502 cho job_id/`downloads`; poster part = poster parent Lib.
5. **Fail nếu:** vẫn 502 junk, hoặc part vẫn `hg_name=…_p01` sau `film_db.sync_one`.

## Liên quan

- Cần **restart :8801** để nạp `routes_hg` 404 (đang có job `1e2379edb4fe_p01` running — chờ idle/yes).
- UI HTML sidecar đọc file mỗi request — hard refresh đủ cho `resolveFilmPosterName`.
