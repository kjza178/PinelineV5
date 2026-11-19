"""Films DB API trên :8801 — parity sidecar :8802.

Trước đây `routes_ui` gắn GET `/films` → HTML `films_ui.html`, nên
`fetch('/films?…')` trên Films UI (:8801) nhận HTML thay JSON → tab Đã làm
không load, không mở được Meta. Router này cung cấp JSON/CSV; UI HTML chỉ còn
`/films/ui` (và `/film`) trong `routes_ui`.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse, Response

import core.film_db as film_db

router = APIRouter(tags=["films"])


def _list_rows(
    q: str = "",
    status: str = "",
    limit: int = 5000,
    order: str = "recent",
    work_exists: Optional[str] = None,
    block_status: str = "",
) -> list[dict]:
    try:
        film_db.sync_uploads()
    except Exception:
        pass
    return film_db.query(
        q=q,
        status=status,
        limit=limit,
        order=order,
        work_exists=work_exists,
        block_status=block_status,
    )


@router.get("/api/films")
@router.get("/films")
def list_films(
    q: str = Query(""),
    status: str = Query(""),
    limit: int = Query(5000),
    order: str = Query("recent"),
    work_exists: Optional[str] = Query(None),
    block_status: str = Query(""),
):
    try:
        rows = _list_rows(q, status, limit, order, work_exists, block_status)
        return {"ok": True, "stats": film_db.stats(), "films": rows}
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.get("/api/films.csv")
@router.get("/films.csv")
def export_films_csv(
    q: str = Query(""),
    status: str = Query(""),
    limit: int = Query(5000),
    order: str = Query("recent"),
    work_exists: Optional[str] = Query(None),
    block_status: str = Query(""),
):
    try:
        rows = _list_rows(q, status, limit, order, work_exists, block_status)
        body = ("\ufeff" + film_db.to_csv(rows)).encode("utf-8")
        return Response(
            content=body,
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=films.csv"},
        )
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)
