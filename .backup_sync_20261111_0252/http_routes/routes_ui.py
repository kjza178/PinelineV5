"""Trang UI chính thức V5: /, /ui3, /hongguo, /hongguo2, /workflow, /v5-map.

/hongguo2 = skin WinUI 2.x (Browse/Ranking/New/Library).

UI chính: static/ui/index3.html.
(index.html / static/app.js đã archive → scripts/archive/ui_legacy/)
"""
from __future__ import annotations

from pathlib import Path
from fastapi.responses import HTMLResponse
from fastapi import APIRouter

router = APIRouter()

__all__ = [
    "_html_file",
    "find_index",
    "index",
    "ui3",
    "ui4",
    "ui_hongguo",
    "ui_hongguo2",
    "ui_v5_map",
    "router",
]

_HERE = Path(__file__).resolve().parent.parent  # project root (file lives in http_routes/)
_UI = _HERE / "static" / "ui"


def find_index() -> Path | None:
    """UI chính: static/ui/index3.html (fallback root / cwd)."""
    for p in (
        _UI / "index3.html",
        _HERE / "index3.html",
        Path("static") / "ui" / "index3.html",
        Path("index3.html"),
    ):
        if p.exists():
            return p
    return None


@router.get("/", response_class=HTMLResponse)
def index():
    p = find_index()
    if not p:
        return HTMLResponse(
            "<h2>Không tìm thấy index3.html</h2>"
            "<p>Đặt file tại static/ui/index3.html (cạnh server.py).</p>",
            status_code=500,
        )
    return HTMLResponse(p.read_text(encoding="utf-8"))


@router.get("/ui3", response_class=HTMLResponse)
@router.get("/index3.html", response_class=HTMLResponse)
def ui3():
    return index()


@router.get("/ui4", response_class=HTMLResponse)
@router.get("/index4.html", response_class=HTMLResponse)
def ui4():
    # Alias lịch sử → UI chính
    return index()


def _html_file(name: str) -> HTMLResponse:
    for p in (
        _UI / name,
        _HERE / name,
        Path("static") / "ui" / name,
        Path(name),
    ):
        if p.exists():
            return HTMLResponse(p.read_text(encoding="utf-8"))
    return HTMLResponse(f"<h2>Không tìm thấy {name}</h2>", status_code=404)


@router.get("/hongguo", response_class=HTMLResponse)
@router.get("/ui-hg", response_class=HTMLResponse)
def ui_hongguo():
    return _html_file("hongguo.html")


@router.get("/hongguo2", response_class=HTMLResponse)
def ui_hongguo2():
    """Hongguo Downloader 2.x skin (Browse / Ranking / New / Library)."""
    return _html_file("hongguo2.html")


@router.get("/workflow", response_class=HTMLResponse)
def ui_workflow():
    return _html_file("workflow.html")


@router.get("/v5-map", response_class=HTMLResponse)
def ui_v5_map():
    """Interactive module/call graph — curated ~40–60 nodes (not full catalog)."""
    return _html_file("v5-map.html")
