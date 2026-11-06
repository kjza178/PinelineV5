"""Cầu nối Hongguo Downloader (local :8000): /api/hg/*.

Tách từ server.py (đợt 7). Chỉ được nạp từ cuối server.py (sau khi mọi hàm/model lõi đã
định nghĩa): truy cập server qua `S.<tên>` để patch `server.<tên>` trong test vẫn có tác dụng."""
from __future__ import annotations

import json
from pathlib import Path
from fastapi.responses import FileResponse
from fastapi.responses import JSONResponse
from fastapi.responses import Response
from pydantic import BaseModel

from fastapi import APIRouter

router = APIRouter()

import server as S  # noqa: E402  — after router so server.include_router works if we imported first

__all__ = [
    "HgRankEpsIn",
    "HgTranslateTitlesIn",
    "_hg_base",
    "_hg_err",
    "hg_baike_info",
    "hg_baike_search",
    "hg_cancel",
    "hg_img",
    "hg_library",
    "hg_library_open",
    "hg_library_preview",
    "hg_merge",
    "hg_merge_queue",
    "hg_merge_queue_clear",
    "hg_ping",
    "hg_poster",
    "hg_preview",
    "hg_rank",
    "hg_rank_episodes",
    "hg_resolve",
    "hg_search",
    "hg_series",
    "hg_status",
    "hg_submit",
    "hg_translate_titles",
    "hg_web_search",
    "router",
]


def _hg_base(override: str | None = None) -> str:
    """Luôn DEFAULT_BASE: `base` từ client từng cho server gửi token Hongguo tới URL bất kỳ."""
    import agents.hongguo_bridge as hg
    return hg.DEFAULT_BASE


def _hg_err(e: Exception):
    msg = str(e)
    try:
        d = json.loads(msg)
        if isinstance(d, dict):
            return JSONResponse(d, status_code=int(d.get("http_status") or 502))
    except Exception:  # noqa: BLE001
        pass
    return JSONResponse({"error": msg}, status_code=502)


@router.get("/api/hg/ping")
def hg_ping(base: str | None = None):
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    return hg.ping(_hg_base(base))


@router.get("/api/hg/search")
def hg_search(q: str, base: str | None = None, expand: bool = True):
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    if not (q or "").strip():
        return JSONResponse({"error": "thiếu q"}, status_code=400)
    try:
        return hg.search(q.strip(), _hg_base(base), expand=bool(expand))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.post("/api/hg/resolve")
def hg_resolve(body: dict | None = None, base: str | None = None):
    """Dán link Hongguo / series_id → meta (khi search không ra, vd. 第十一季)."""
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    body = body or {}
    text = (body.get("text") or body.get("url") or body.get("q") or "").strip()
    b = _hg_base(body.get("base") or base)
    if not text:
        return JSONResponse({"error": "thiếu text/url/series_id"}, status_code=400)
    try:
        return hg.resolve_text(text, b)
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.get("/api/hg/baike-search")
def hg_baike_search(q: str, base: str | None = None):
    """Nhận diện trên duanjubaike → danh sách version → match Hongguo từng cái.
    Loại tên lạc họ / id lệch."""
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    if not (q or "").strip():
        return JSONResponse({"error": "thiếu q"}, status_code=400)
    try:
        return hg.search_via_baike(q.strip(), _hg_base(base))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.get("/api/hg/baike-info")
def hg_baike_info(series_id: str | None = None, title: str | None = None,
                  translate: bool = True):
    """Chi tiết sâu từ duanjubaike (intro/tags/score/同系列).

    Tra theo series_id Hongguo/baike; nếu thiếu hoặc miss thì search theo title.
    """
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    sid = (series_id or "").strip() or None
    tit = (title or "").strip() or None
    if not sid and not tit:
        return JSONResponse({"error": "thiếu series_id hoặc title"}, status_code=400)
    try:
        info = hg.baike_deep(series_id=sid, title=tit)
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)
    if translate:
        try:
            import engines.title_mt as _tmt
            _tmt = importlib.reload(_tmt)
            pack = []
            if info.get("title"):
                pack.append({"series_id": info.get("series_id") or "", "title": info["title"]})
            if info.get("intro"):
                pack.append({"series_id": (info.get("series_id") or "") + ":intro",
                             "title": info["intro"][:180]})
            for r in (info.get("related") or [])[:12]:
                if r.get("title"):
                    pack.append({"series_id": r.get("series_id") or "", "title": r["title"]})
            tr = _tmt.translate_titles(pack)
            by = {str(x.get("series_id") or ""): x.get("title_vi") for x in tr.get("items") or []}
            if by.get(str(info.get("series_id") or "")):
                info["title_vi"] = by[str(info.get("series_id") or "")]
            intro_key = str(info.get("series_id") or "") + ":intro"
            if by.get(intro_key):
                info["intro_vi"] = by[intro_key]
            for r in (info.get("related") or []):
                vi = by.get(str(r.get("series_id") or ""))
                if vi:
                    r["title_vi"] = vi
        except Exception as e:  # noqa: BLE001
            info["translate_error"] = str(e)[:200]
    return info


@router.get("/api/hg/web-search")
def hg_web_search(q: str):
    """Scrape hongguoduanju.com/search — dùng khi API Downloader sót mùa."""
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    if not (q or "").strip():
        return JSONResponse({"error": "thiếu q"}, status_code=400)
    try:
        by_id: dict = {}
        n = hg.web_expand_into(by_id, q.strip(), workers=6)
        items = hg.order_franchise_items(list(by_id.values()))
        return {
            "results": items,
            "n": len(items),
            "added": n,
            "core": hg.franchise_core(q),
            "queries": hg.web_expand_queries(q),
        }
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.get("/api/hg/series/{series_id}")
def hg_series(series_id: str, base: str | None = None):
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    try:
        return hg.lookup_series(series_id, _hg_base(base))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.get("/api/hg/status")
def hg_status(base: str | None = None):
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    try:
        return hg.status(_hg_base(base))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.post("/api/hg/cancel")
def hg_cancel(body: S.HgBaseIn | None = None):
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    try:
        return hg.cancel(_hg_base((body.base if body else None)))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.post("/api/hg/submit")
def hg_submit(body: S.HgSubmitIn):
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    try:
        return hg.submit(body.series_ids, _hg_base(body.base), scores=body.scores)
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.get("/api/hg/rank")
def hg_rank(category: str = "all", board: str = "recommend",
            offset: int = 0, size: int = 100, base: str | None = None):
    """Bảng hot giống app Downloader (Leaderboard /dl/rank)."""
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    try:
        return hg.rank(category=category, board=board, offset=offset,
                       size=size, base=_hg_base(base))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


class HgRankEpsIn(BaseModel):
    series_ids: list[str] = []
    base: str | None = None


@router.post("/api/hg/rank-episodes")
def hg_rank_episodes(body: HgRankEpsIn):
    """Lazy fill episode_cnt cho series trên bảng hot."""
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    try:
        return hg.rank_episodes(body.series_ids, _hg_base(body.base))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


class HgTranslateTitlesIn(BaseModel):
    items: list[dict] = []   # [{series_id?, title}]


@router.post("/api/hg/translate-titles")
def hg_translate_titles(body: HgTranslateTitlesIn):
    """Dịch thô title Trung→Việt (Google gtx + cache) — chỉ để duyệt Hongguo."""
    import importlib
    import engines.title_mt as _tmt
    _tmt = importlib.reload(_tmt)
    try:
        return _tmt.translate_titles(list(body.items or []))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.get("/api/hg/library")
def hg_library(base: str | None = None):
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    try:
        return hg.library(_hg_base(base))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.get("/api/hg/preview")
def hg_preview(series_id: str, ep: int = 1, fresh: int = 0, base: str | None = None):
    """URL MP4 tập miễn phí (hongguoduanju /dl/preview) — không cần tải về."""
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    sid = (series_id or "").strip()
    if not sid:
        return JSONResponse({"ok": False, "error": "thiếu series_id"}, status_code=400)
    try:
        return hg.preview_series(sid, ep=ep, fresh=bool(fresh), base=_hg_base(base))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.get("/api/hg/library/preview", operation_id="hg_library_preview")
@router.head("/api/hg/library/preview", operation_id="hg_library_preview_head")
def hg_library_preview(name: str, base: str | None = None):
    """Stream video thư viện Hongguo (merged hoặc tập đầu) — tua được (Range)."""
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    name = (name or "").strip()
    if not name:
        return JSONResponse({"error": "thiếu name"}, status_code=400)
    try:
        p = hg.resolve_preview_path(name, _hg_base(base))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)
    if not p:
        return JSONResponse({"error": "chưa có file xem thử (cần tải / merge)"}, status_code=404)
    suffix = p.suffix.lower()
    media = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mkv": "video/x-matroska",
        ".mov": "video/quicktime",
    }.get(suffix, "application/octet-stream")
    return FileResponse(str(p), media_type=media, filename=p.name)


@router.get("/api/hg/img")
def hg_img(url: str, base: str | None = None):
    """Proxy ảnh cover qua Hongguo /img (HEIC → JPEG) — kèm UI token."""
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    if not (url or "").strip():
        return JSONResponse({"error": "thiếu url"}, status_code=400)
    try:
        data, ctype = hg.fetch_img_proxy(url.strip(), _hg_base(base))
        return Response(content=data, media_type=ctype, headers={
            "Cache-Control": "public, max-age=86400",
        })
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=502)


@router.get("/api/hg/poster")
def hg_poster(name: str, base: str | None = None):
    """Poster thư viện: /dl/poster (auth) hoặc file local poster.jpg."""
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    if not (name or "").strip():
        return JSONResponse({"error": "thiếu name"}, status_code=400)
    try:
        data, ctype = hg.fetch_poster(name.strip(), _hg_base(base))
        return Response(content=data, media_type=ctype, headers={
            "Cache-Control": "public, max-age=3600",
        })
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=502)


@router.post("/api/hg/merge")
def hg_merge(body: S.HgMergeIn):
    """Enqueue merge tuần tự (Hongguo chỉ chạy 1 merge / lúc)."""
    import agents.hongguo_bridge as hg
    try:
        return hg.merge_queue_add(
            body.names, _hg_base(body.base), skip_done=not body.force,
        )
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.get("/api/hg/merge-queue")
def hg_merge_queue(base: str | None = None):
    import agents.hongguo_bridge as hg
    return hg.merge_queue_state(_hg_base(base))


@router.post("/api/hg/merge-queue/clear")
def hg_merge_queue_clear():
    import agents.hongguo_bridge as hg
    return hg.merge_queue_clear()


@router.post("/api/hg/library/open")
def hg_library_open(body: dict | None = None):
    import agents.hongguo_bridge as hg
    body = body or {}
    try:
        return hg.open_library(body.get("name"), _hg_base(body.get("base")))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.post("/api/hg/library/delete")
def hg_library_delete(body: dict | None = None):
    import agents.hongguo_bridge as hg
    body = body or {}
    names = list(body.get("names") or [])
    if not names:
        return JSONResponse({"ok": False, "error": "Chưa chọn series để xoá"}, status_code=400)
    try:
        return hg.delete_library_series(names, _hg_base(body.get("base")))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.post("/api/hg/library/update")
def hg_library_update(body: dict | None = None):
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    body = body or {}
    names = body.get("names")
    try:
        return hg.library_update(_hg_base(body.get("base")), names=names)
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.post("/api/hg/library/seasons/decline")
def hg_seasons_decline(body: dict | None = None):
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    body = body or {}
    series_ids = list(body.get("series_ids") or [])
    try:
        return hg.seasons_decline(series_ids, _hg_base(body.get("base")))
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.post("/api/hg/library/seasons/discover")
def hg_seasons_discover(body: dict | None = None):
    """Chỉ tìm mùa mới theo watchlist+films+lib — không tải / không gọi Update all."""
    import importlib
    import agents.hongguo_bridge as hg
    hg = importlib.reload(hg)
    body = body or {}
    try:
        max_cores = int(body.get("max_cores") or 16)
    except (TypeError, ValueError):
        max_cores = 16
    expand = bool(body.get("expand") or False)
    try:
        return hg.discover_new_seasons(
            _hg_base(body.get("base")), max_cores=max_cores, expand=expand
        )
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.get("/api/hg/library/watchlist")
def hg_library_watchlist(include_deleted: bool = True):
    """Danh sách meta watchlist (sau xoá Lib vẫn còn) — không tải."""
    try:
        from core import film_db as fdb  # type: ignore
    except Exception:  # noqa: BLE001
        import film_db as fdb  # type: ignore
    try:
        rows = fdb.list_hg_watchlist(include_deleted=bool(include_deleted))
        return {
            "ok": True,
            "n": len(rows),
            "items": rows,
            "on_disk": sum(1 for r in rows if int(r.get("on_disk") or 0) == 1),
            "deleted": sum(1 for r in rows if int(r.get("on_disk") or 0) == 0),
        }
    except Exception as e:  # noqa: BLE001
        return _hg_err(e)


@router.post("/api/meta/generate")
@router.post("/meta/generate")
def meta_generate(body: dict):
    import agents.meta_studio as meta_studio
    try:
        r = meta_studio.generate_metadata(
            title_vi=str(body.get("title_vi") or ""),
            title_zh=str(body.get("title_zh") or ""),
            info_text=str(body.get("info_text") or ""),
            prompt_guide=str(body.get("prompt_guide") or ""),
            tone=str(body.get("tone") or "giật gân, kịch tính"),
        )
        if not r.get("ok"):
            return JSONResponse(r, status_code=500)
        return r
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.post("/api/meta/generate-title")
@router.post("/meta/generate-title")
def meta_generate_title(body: dict):
    """Sinh tiêu đề YouTube (port từ V2) — giữ nguyên meta/ai-image + meta/baike của V4."""
    import agents.meta_studio as meta_studio
    try:
        job_id = str(body.get("job_id") or "").strip()
        series_name = str(body.get("series_name") or body.get("title_vi") or body.get("title") or "").strip()
        title_zh = str(body.get("title_zh") or body.get("title") or "").strip()
        season = int(body.get("season") or 1)
        info_text = str(body.get("info_text") or "").strip()
        summary = str(body.get("summary") or "").strip()
        tone = str(body.get("tone") or "").strip()
        count = int(body.get("count") or 5)
        r = meta_studio.generate_youtube_titles(
            series_name=series_name,
            season=season,
            episode_info=info_text,
            summary=summary,
            job_id=job_id,
            tone=tone,
            count=count,
            title_zh=title_zh,
        )
        if not r.get("ok"):
            return JSONResponse(r, status_code=500)
        return r
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.post("/api/meta/thumbnail")
@router.post("/meta/thumbnail")
def meta_thumbnail(body: dict):
    import agents.meta_studio as meta_studio
    try:
        poster_src = body.get("poster_url") or body.get("poster_path")
        if not poster_src and body.get("poster_name"):
            try:
                import agents.hongguo_bridge as hg
                data, _ = hg.fetch_poster(str(body["poster_name"]).strip(), _hg_base(body.get("base")))
                if data:
                    poster_src = data
            except Exception:
                pass
        if not poster_src:
            return JSONResponse({"ok": False, "error": "Thiếu nguồn ảnh poster hoặc không tìm thấy poster"}, status_code=400)
        out = meta_studio.create_thumbnail(
            poster_source=poster_src,
            hook_text_1=str(body.get("hook_text_1") or ""),
            hook_text_2=str(body.get("hook_text_2") or ""),
            badge_text=str(body.get("badge_text") or "TRỌN BỘ THUYẾT MINH"),
            sub_text=str(body.get("sub_text") or ""),
            style=str(body.get("style") or "fire_gold"),
            out_filename=str(body.get("out_filename") or ""),
        )
        return {"ok": True, "path": str(out), "filename": out.name, "url": f"/api/meta/thumbnail?file={out.name}"}
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)


@router.get("/api/meta/thumbnail")
@router.get("/meta/thumbnail")
def meta_thumbnail_get(file: str):
    # project root (file lives in http_routes/)
    root = Path(__file__).resolve().parent.parent
    thumb_dir = (root / "data" / "thumbnails").resolve()
    p = (thumb_dir / file).resolve()
    if p.is_file() and p.parent == thumb_dir:
        return Response(content=p.read_bytes(), media_type="image/jpeg", headers={"Cache-Control": "public, max-age=3600"})
    return JSONResponse({"error": "not found"}, status_code=404)


@router.get("/api/meta/series-info")
@router.get("/meta/series-info")
def meta_series_info(job_id: str = ""):
    import agents.meta_studio as meta_studio
    series_key, series_name = meta_studio.get_series_key(job_id)
    shared_meta = meta_studio.get_series_meta(series_key, series_name=series_name)
    shared_thumb = meta_studio.get_series_thumbnail(series_key, series_name=series_name)
    return {
        "ok": True,
        "has_shared": bool(shared_meta and shared_thumb and shared_thumb.is_file()),
        "series_key": series_key,
        "series_name": series_name,
        "shared_meta": shared_meta,
        "thumb_url": f"/meta/thumbnail?file={shared_thumb.name}" if (shared_thumb and shared_thumb.is_file()) else None,
    }


@router.post("/api/meta/ai-image")
@router.post("/meta/ai-image")
def meta_ai_image(body: dict):
    import io
    import time
    from PIL import Image
    import agents.meta_studio as meta_studio
    prompt = str(body.get("prompt") or "").strip()
    job_id = str(body.get("job_id") or f"gen_{int(time.time())}").strip()
    if not prompt:
        return JSONResponse({"ok": False, "error": "Thiếu prompt"}, status_code=400)
    img_bytes = meta_studio.generate_ai_image(prompt, timeout=120)
    if not img_bytes:
        return JSONResponse({"ok": False, "error": "AI không sinh được ảnh (timeout hoặc lỗi)"}, status_code=500)
    out_name = f"thumb_{job_id}_ai.png"
    out_p = meta_studio.THUMB_DIR / out_name
    out_p.write_bytes(img_bytes)
    try:
        jpg_name = f"thumb_{job_id}.jpg"
        jpg_p = meta_studio.THUMB_DIR / jpg_name
        im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        im.save(jpg_p, format="JPEG", quality=92, optimize=True)
    except Exception:
        pass
    return {
        "ok": True,
        "path": str(out_p),
        "filename": out_name,
        "url": f"/meta/thumbnail?file={out_name}",
        "jpg_url": f"/meta/thumbnail?file=thumb_{job_id}.jpg",
    }


@router.get("/api/meta/baike")
@router.get("/meta/baike")
def meta_baike(q: str = "", title: str = ""):
    tit = (q or title).strip()
    if not tit:
        return JSONResponse({"ok": False, "error": "thiếu tên phim"}, status_code=400)
    try:
        import agents.hongguo_bridge as hg
        info = hg.baike_deep(title=tit)
        intro_vi = ""
        try:
            import engines.title_mt as tmt
            if info.get("intro"):
                tr = tmt.translate_titles([{"series_id": "intro", "title": info["intro"][:300]}])
                if tr.get("items"):
                    intro_vi = tr["items"][0].get("title_vi", "")
        except Exception:
            pass
        return {
            "ok": True,
            "title": info.get("title") or tit,
            "tags": info.get("tags") or [],
            "intro": info.get("intro") or "",
            "intro_vi": intro_vi,
            "actors": info.get("actors") or [],
            "roles": info.get("roles") or [],
        }
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)



