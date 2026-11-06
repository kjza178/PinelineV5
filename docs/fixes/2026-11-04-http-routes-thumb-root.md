# Thumbnail meta 404 sau khi move routes_hg → http_routes/

- **Date:** 2026-11-04
- **Job / khu vực:** `http_routes/routes_hg.py` `meta_thumbnail_get`
- **Status:** fixed

## Triệu chứng

`GET /meta/thumbnail?file=…` có thể 404 dù file nằm ở `data/thumbnails/` (project root) — path resolve dưới `http_routes/data/`.

## Root cause

Sau Phase B, `Path(__file__).resolve().parent` = `http_routes/`, không còn là project root. `meta_studio` ghi thumb vào `ROOT/data/thumbnails` (đúng), còn route đọc từ `http_routes/data/thumbnails` (sai).

## Evidence

- Grep: `http_routes/routes_hg.py` dùng `.parent / "data" / "thumbnails"`
- `agents/meta_studio.py` `THUMB_DIR = ROOT / "data" / "thumbnails"` với `ROOT = parents[1]` từ `agents/`

## Fix

- `meta_thumbnail_get`: `parent.parent` → project root, cùng `data/thumbnails`
- Backup: zip `Z:\PinelineV2_backup_2026-11-04_2101.zip`; codebak `Z:\PinelineV2_codebak\2026-11-04_v5-layout-B-fix\`
- Test: `tests/test_layout_paths.py`

## Recheck

1. `pytest tests/test_layout_paths.py -q`
2. `python -c "from pathlib import Path; p=Path('http_routes/routes_hg.py').resolve(); assert (p.parent.parent/'data'/'thumbnails')!=(p.parent/'data'/'thumbnails')"`
3. **Pass nếu:** pytest layout OK; thumb_dir = `Z:\PinelineV5\data\thumbnails`
4. **Fail nếu:** path vẫn dưới `http_routes/data/`

## Liên quan

- Phase B layout; OpenAPI `/` + `/films/ui` vẫn xanh
