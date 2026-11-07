"""hongguo_rpc.py — JSON-RPC stdio client cho Hongguo WinUI 2.x helper.jar.

Không dùng HTTP :8000 (bản 1.x). Spawn engine local:

  …/HongguoWinUI/current/engine/runtime/bin/java.exe
  -cp lib\\* com.hongguo.helper.MainKt

Mỗi dòng stdin/stdout = 1 JSON-RPC 2.0 object.
"""
from __future__ import annotations

import atexit
import json
import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

DEFAULT_ENGINE_DIR = Path(
    os.environ.get("HG_ENGINE_DIR")
    or (Path(os.environ.get("LOCALAPPDATA", "")) / "HongguoWinUI" / "current" / "engine")
)

_PROTOCOL = 2
_IDLE_SEC = float(os.environ.get("HG_RPC_IDLE_SEC") or "600")
_CALL_TIMEOUT = float(os.environ.get("HG_RPC_TIMEOUT") or "60")

_lock = threading.RLock()
_proc: subprocess.Popen | None = None
_reader: threading.Thread | None = None
_pending: dict[int, dict[str, Any]] = {}
_notes: dict[str, Any] = {}  # method -> last params
_next_id = 1
_last_used = 0.0
_hello: dict[str, Any] | None = None
_stderr_tail: list[str] = []


class HgRpcError(RuntimeError):
    def __init__(self, message: str, *, code: int | None = None, data: Any = None):
        super().__init__(message)
        self.code = code
        self.data = data

    def as_dict(self) -> dict:
        d: dict[str, Any] = {"error": str(self)}
        if self.code is not None:
            d["rpc_code"] = self.code
        if self.data is not None:
            d["data"] = self.data
        return d


def engine_dir() -> Path:
    return Path(DEFAULT_ENGINE_DIR)


def helper_available(edir: Path | None = None) -> bool:
    d = Path(edir or engine_dir())
    java = d / "runtime" / "bin" / "java.exe"
    jar = d / "lib" / "helper.jar"
    return java.is_file() and jar.is_file()


def _java_cmd(d: Path) -> list[str]:
    java = d / "runtime" / "bin" / "java.exe"
    return [
        str(java),
        "-Xlog:disable",
        "-Xlog:all=warning:stderr",
        "-XX:+DisableAttachMechanism",
        "-Dhongguo.signer.dir=signer",
        "-Dhongguo.ffmpeg=ffmpeg\\ffmpeg.exe",
        "-Djna.boot.library.path=lib\\native",
        "-Djna.nosys=true",
        "-Djna.nounpack=true",
        "-Dfile.encoding=UTF-8",
        "-cp",
        "lib\\*",
        "com.hongguo.helper.MainKt",
    ]


def _on_line(line: str) -> None:
    line = (line or "").strip()
    if not line:
        return
    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        return
    if not isinstance(msg, dict):
        return
    mid = msg.get("id")
    if mid is not None and "method" not in msg:
        # response
        with _lock:
            slot = _pending.get(int(mid))
            if slot is not None:
                slot["msg"] = msg
                slot["ev"].set()
        return
    method = msg.get("method")
    if method:
        with _lock:
            _notes[str(method)] = msg.get("params") or {}


def _reader_loop(proc: subprocess.Popen) -> None:
    assert proc.stdout is not None
    try:
        for raw in proc.stdout:
            _on_line(raw)
    except Exception:  # noqa: BLE001
        pass
    finally:
        with _lock:
            for slot in _pending.values():
                if not slot["ev"].is_set():
                    slot["msg"] = {
                        "jsonrpc": "2.0",
                        "id": slot.get("id"),
                        "error": {"code": -32000, "message": "helper exited"},
                    }
                    slot["ev"].set()


def _stderr_loop(proc: subprocess.Popen) -> None:
    assert proc.stderr is not None
    try:
        for raw in proc.stderr:
            s = (raw or "").rstrip()
            if not s:
                continue
            with _lock:
                _stderr_tail.append(s)
                del _stderr_tail[:-30]
    except Exception:  # noqa: BLE001
        pass


def _kill_unlocked() -> None:
    global _proc, _reader, _hello
    proc = _proc
    _proc = None
    _reader = None
    _hello = None
    if proc is None:
        return
    try:
        if proc.stdin and proc.poll() is None:
            proc.stdin.write(
                json.dumps({"jsonrpc": "2.0", "id": 0, "method": "app.shutdown", "params": {}})
                + "\n"
            )
            proc.stdin.flush()
    except Exception:  # noqa: BLE001
        pass
    try:
        proc.terminate()
    except Exception:  # noqa: BLE001
        pass
    try:
        proc.wait(timeout=3)
    except Exception:  # noqa: BLE001
        try:
            proc.kill()
        except Exception:  # noqa: BLE001
            pass


def stop() -> None:
    with _lock:
        _kill_unlocked()


def _ensure_unlocked(edir: Path | None = None) -> subprocess.Popen:
    global _proc, _reader, _last_used, _hello
    d = Path(edir or engine_dir())
    if not helper_available(d):
        raise HgRpcError(f"không thấy Hongguo 2.x engine tại {d}")
    if _proc is not None and _proc.poll() is None:
        _last_used = time.time()
        return _proc
    _kill_unlocked()
    proc = subprocess.Popen(
        _java_cmd(d),
        cwd=str(d),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
    )
    _proc = proc
    _reader = threading.Thread(target=_reader_loop, args=(proc,), name="hg-rpc-out", daemon=True)
    _reader.start()
    threading.Thread(target=_stderr_loop, args=(proc,), name="hg-rpc-err", daemon=True).start()
    # chờ engine.ready
    deadline = time.time() + 8.0
    while time.time() < deadline:
        with _lock:
            if "engine.ready" in _notes:
                break
        if proc.poll() is not None:
            raise HgRpcError(
                "helper thoát ngay khi start"
                + (f": {_stderr_tail[-1]}" if _stderr_tail else "")
            )
        time.sleep(0.05)
    _last_used = time.time()
    return proc


def ensure(edir: Path | None = None) -> dict[str, Any]:
    """Đảm bảo helper sống; trả app.hello (cache)."""
    global _hello
    with _lock:
        _ensure_unlocked(edir)
    if _hello:
        return dict(_hello)
    hello = call("app.hello", {})
    with _lock:
        _hello = dict(hello or {})
    return dict(_hello)


def call(method: str, params: dict | None = None, *, timeout: float | None = None) -> Any:
    """Gọi method JSON-RPC; trả `result` hoặc raise HgRpcError."""
    global _next_id, _last_used
    timeout = float(_CALL_TIMEOUT if timeout is None else timeout)
    params = dict(params or {})
    with _lock:
        proc = _ensure_unlocked()
        _next_id += 1
        req_id = _next_id
        ev = threading.Event()
        _pending[req_id] = {"ev": ev, "msg": None, "id": req_id}
        line = json.dumps(
            {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params},
            ensure_ascii=False,
        )
        try:
            assert proc.stdin is not None
            proc.stdin.write(line + "\n")
            proc.stdin.flush()
        except Exception as e:  # noqa: BLE001
            _pending.pop(req_id, None)
            _kill_unlocked()
            raise HgRpcError(f"không ghi được stdin helper: {e}") from e
        _last_used = time.time()

    if not ev.wait(timeout):
        with _lock:
            _pending.pop(req_id, None)
        raise HgRpcError(f"timeout {timeout:.0f}s — {method}")

    with _lock:
        slot = _pending.pop(req_id, {}) or {}
        msg = slot.get("msg") or {}
        _last_used = time.time()

    if "error" in msg:
        err = msg.get("error") or {}
        raise HgRpcError(
            str(err.get("message") or err),
            code=err.get("code"),
            data=err.get("data"),
        )
    return msg.get("result")


def note(method: str) -> Any:
    with _lock:
        return _notes.get(method)


def license_status() -> dict:
    try:
        return dict(call("license.status", {}) or {})
    except HgRpcError:
        return {"state": "unknown"}


def ping() -> dict:
    """Shape gần hongguo_bridge.ping()."""
    try:
        hello = ensure()
        st = license_status()
        settings = call("settings.get", {}) or {}
        return {
            "ok": True,
            "backend": "rpc",
            "base": f"stdio:{engine_dir()}",
            "output_dir": settings.get("saveFolder"),
            "running": False,
            "mode": "rpc",
            "engineVersion": hello.get("engineVersion"),
            "protocol": hello.get("protocol") or _PROTOCOL,
            "capabilities": hello.get("capabilities") or [],
            "license": st.get("state"),
            "has_token": st.get("state") not in (None, "none", "unknown"),
        }
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "backend": "rpc", "error": str(e)}


def _card_to_result(c: dict) -> dict:
    sid = str(c.get("id") or c.get("seriesId") or c.get("series_id") or "")
    return {
        "series_id": sid,
        "title": c.get("title") or "",
        "cover": c.get("cover") or "",
        "episode_cnt": c.get("episodes") or c.get("episode_cnt"),
        "score": c.get("score"),
        "heat": c.get("heat"),
        "tags": c.get("tags") or [],
        "remarks": c.get("remarks"),
        "intro": c.get("intro"),
    }


def search(q: str, *, page: int = 0) -> dict:
    q = (q or "").strip()
    raw = call("search.page", {"query": q, "page": int(page)}) or {}
    cards = list(raw.get("cards") or [])
    results = [_card_to_result(c) for c in cards if str(c.get("id") or "")]
    return {
        "results": results,
        "groups": [],
        "queries": [q],
        "expand": False,
        "core": "",
        "hasMore": bool(raw.get("hasMore")),
        "nextOffset": raw.get("nextOffset"),
        "searchId": raw.get("searchId"),
        "backend": "rpc",
        "raw_keys": list(raw.keys()),
    }


def rank(*, chart: str | None = None, board: str | None = None,
         category: str | None = None, offset: int = 0, limit: int = 100) -> dict:
    params: dict[str, Any] = {}
    if chart:
        params["chart"] = chart
    if board:
        params["board"] = board
    if category and category not in ("all", ""):
        params["category"] = category
    if offset:
        params["offset"] = int(offset)
    if limit:
        params["limit"] = int(limit)
    raw = call("rank.page", params) or {}
    cards = list(raw.get("cards") or [])
    results = [_card_to_result(c) for c in cards if str(c.get("id") or "")]
    return {
        "results": results,
        "charts": raw.get("charts"),
        "chart": raw.get("chart"),
        "board": raw.get("board"),
        "hasMore": bool(raw.get("hasMore")),
        "backend": "rpc",
    }


def feed(
    *,
    offset: int = 0,
    select: dict[str, str] | None = None,
    panel: bool = False,
    session_id: str = "",
) -> dict:
    """Browse landpage — feed.page.

    select: map FilterRow.type → FilterItem.id (vd genre=short_play).
    panel=True: kèm selector rows (7 facet giống WinUI 2.x).
    """
    params: dict[str, Any] = {}
    if offset:
        params["offset"] = int(offset)
    if panel:
        params["panel"] = True
    if select:
        # chỉ giữ id khác rỗng
        clean = {str(k): str(v) for k, v in select.items() if str(v or "").strip()}
        if clean:
            params["select"] = clean
    sid = (session_id or "").strip()
    if sid:
        params["sessionId"] = sid
    raw = call("feed.page", params) or {}
    cards = list(raw.get("cards") or [])
    return {
        "results": [_card_to_result(c) for c in cards if str(c.get("id") or "")],
        "hasMore": bool(raw.get("hasMore")),
        "nextOffset": raw.get("nextOffset"),
        "rows": raw.get("rows") or [],
        "sessionId": raw.get("sessionId") or "",
        "backend": "rpc",
    }


def library() -> dict:
    raw = call("library.get", {}) or {}
    entries = list(raw.get("entries") or [])
    # Lần đầu helper thường trả entries=[] — đợi/refresh lấy snapshot
    if not entries:
        try:
            call("library.refresh", {}, timeout=30)
        except HgRpcError:
            pass
        deadline = time.time() + 8.0
        while time.time() < deadline:
            ch = note("library.changed") or {}
            if ch.get("entries") is not None and not ch.get("scanning"):
                entries = list(ch.get("entries") or [])
                raw = {**raw, **{k: ch.get(k) for k in ("folder", "newSeasons") if k in ch}}
                break
            time.sleep(0.2)
        if not entries:
            raw = call("library.get", {}) or {}
            entries = list(raw.get("entries") or [])
    items = []
    for e in entries:
        sid = str(e.get("seriesId") or e.get("series_id") or "")
        title = e.get("title") or ""
        folder = e.get("folder") or ""
        name = Path(folder).name if folder else title
        eps = int(e.get("episodes") or 0)
        items.append({
            "name": name,
            "series_id": sid,
            "title": title,
            "local": eps,
            "total": eps,
            "new": 0,
            "fresh": 0,
            "score": "",
            "updated": e.get("updatedAt"),
            "size": e.get("bytes") or 0,
            "poster": bool(e.get("cover")),
            "cover": e.get("cover") or "",
            "folder": folder,
        })
    note_ch = note("library.changed") or {}
    return {
        "items": items,
        "folder": raw.get("folder"),
        "newSeasons": note_ch.get("newSeasons"),
        "backend": "rpc",
    }


def library_refresh() -> dict:
    call("library.refresh", {})
    # events may follow
    time.sleep(0.3)
    return library()


def status() -> dict:
    snap = call("downloads.snapshot", {}) or {}
    jobs = list(snap.get("jobs") or [])
    active = [j for j in jobs if str(j.get("status") or "").upper() in
              ("DOWNLOADING", "QUEUED", "RUNNING", "PENDING", "WAITING")]
    return {
        "running": bool(active),
        "mode": "rpc",
        "series": jobs,
        "jobs": jobs,
        "active": len(active),
        "backend": "rpc",
        "source": "downloads.snapshot",
    }


def cancel() -> dict:
    return call("downloads.cancelAll", {}) or {"ok": True}


def _ensure_licensed_quiet() -> None:
    try:
        import hongguo_license_ensure as _lic  # noqa: PLC0415

        _lic.ensure_or_raise()
    except HgRpcError:
        raise
    except Exception as e:  # noqa: BLE001
        raise HgRpcError(
            f"Hongguo license ensure lỗi: {e}",
            code=-32010,
            data={"reason": "need_license"},
        ) from e


def submit(
    series_ids: list[str],
    scores: dict | None = None,
    quality: str | None = None,
) -> dict:
    ids = [str(x).strip() for x in series_ids if str(x).strip()]
    if not ids:
        raise HgRpcError("series_ids trống")
    _ensure_licensed_quiet()
    q = (quality or "").strip() or None
    requests = []
    for sid in ids:
        req: dict[str, Any] = {"seriesId": sid}
        if scores and sid in scores:
            req["score"] = scores[sid]
        if q:
            req["quality"] = q
        requests.append(req)
    try:
        return call("downloads.add", {"requests": requests}) or {}
    except HgRpcError as e:
        # license chưa inject vào helper spawn riêng
        if e.code == -32010 or "licence" in str(e).lower() or "license" in str(e).lower():
            raise HgRpcError(
                "Hongguo 2.x RPC cần license proof để tải "
                f"(license.status có thể đang 'none'). Chi tiết: {e}",
                code=e.code,
                data={"reason": "need_license", **(e.data or {} if isinstance(e.data, dict) else {})},
            ) from e
        raise


def library_download_new_seasons() -> dict:
    _ensure_licensed_quiet()
    try:
        return call("library.downloadNewSeasons", {}) or {}
    except HgRpcError as e:
        if e.code == -32010 or "key" in str(e).lower() or "proof" in str(e).lower():
            raise HgRpcError(
                "downloadNewSeasons cần Hongguo key/license proof trên helper RPC. "
                f"{e}",
                code=e.code,
                data={"reason": "need_license"},
            ) from e
        raise


def resolve_link(text: str) -> dict:
    return call("links.resolve", {"text": text}) or {}


def series_detail(series_id: str) -> dict:
    sid = str(series_id or "").strip()
    if not sid:
        raise HgRpcError("thiếu series id")
    raw = call("series.detail", {"id": sid}) or {}
    eps = raw.get("episodes")
    if isinstance(eps, list):
        episode_cnt: int | list | None = eps  # bridge normalize → int + giữ list
    elif isinstance(eps, (int, float)):
        episode_cnt = int(eps)
    else:
        episode_cnt = eps
    return {
        "series_id": str(raw.get("id") or sid),
        "title": raw.get("title"),
        "cover": raw.get("cover"),
        "intro": raw.get("intro"),
        "complete": raw.get("complete"),
        "tags": raw.get("tags"),
        "cast": raw.get("cast"),
        "episode_cnt": episode_cnt,
        "folderName": raw.get("folderName"),
        "backend": "rpc",
        "raw": raw,
    }


def series_seasons(series_id: str) -> dict:
    sid = str(series_id or "").strip()
    if not sid:
        raise HgRpcError("thiếu series id")
    raw = call("series.seasons", {"id": sid}) or {}
    seasons = []
    for s in (raw.get("seasons") or []):
        seasons.append({
            "series_id": str(s.get("id") or ""),
            "title": s.get("title") or "",
            "season": s.get("season"),
            "episodes": s.get("episodes") or 0,
            "cover": s.get("cover") or "",
            "upcoming": bool(s.get("upcoming")),
        })
    return {"series_id": sid, "seasons": seasons, "backend": "rpc"}


def series_qualities(series_id: str) -> dict:
    sid = str(series_id or "").strip()
    if not sid:
        raise HgRpcError("thiếu series id")
    raw = call("series.qualities", {"id": sid}) or {}
    qualities = []
    for q in (raw.get("qualities") or []):
        qualities.append({
            "quality": q.get("quality") or q.get("uses") or "",
            "plays": bool(q.get("plays", True)),
            "uses": q.get("uses") or q.get("quality") or "",
            "bytesPerSecond": q.get("bytesPerSecond") or 0,
        })
    return {"series_id": sid, "qualities": qualities, "backend": "rpc"}


def settings_get() -> dict:
    return call("settings.get", {}) or {}


def _idle_watch() -> None:
    while True:
        time.sleep(30)
        with _lock:
            if _proc is None or _proc.poll() is not None:
                continue
            if time.time() - _last_used > _IDLE_SEC:
                _kill_unlocked()


threading.Thread(target=_idle_watch, name="hg-rpc-idle", daemon=True).start()
atexit.register(stop)
