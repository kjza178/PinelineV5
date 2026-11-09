# Library hongguo2 lệch WinUI

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo2` Library
- **Status:** fixed

## Triệu chứng

Library chỉ grid card browse-style + «Update library»; thiếu Update info / Select / Open folder, chip All downloads / New seasons / Lib path, hover Folder+Play, meta `N eps · size`.

## Root cause

UI chưa map WinUI Library; poster `file:…` không qua `/api/hg/poster`; thiếu `library.updateInfo`.

## Evidence

- Screenshot WinUI Library (49 dramas, New seasons 11, hover Folder/Play).
- `GET /api/hg/library` có `items`, `newSeasons`, `folder`.

## Fix

- UI WinUI: actions + chips + lib cards (badge/hover/meta).
- `POST /api/hg/library/update-info` → `library.updateInfo`.
- Poster local qua `/api/hg/poster?name=`.
- Backup: `Z:\PinelineV2_codebak\2026-11-08_library-winui\`

## Recheck

1. Hard refresh `/hongguo2` → Library.
2. Thấy Update info / Select / Open folder; chips All / New seasons / `D:\Lib`.
3. Poster + `N eps · size`; hover Folder mở Explorer, Play preview.
4. **Pass nếu:** khớp screenshot WinUI.
5. **Fail nếu:** vẫn «Update library» / card browse thường.
