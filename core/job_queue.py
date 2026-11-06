from __future__ import annotations

import json
import os
import sys
import threading
import time
from collections.abc import Callable
from pathlib import Path

from .job_meta import (
    info_from_film_row,
    info_from_manifest_dict,
    norm_series_key as _norm_series_key,
    parse_season_from_text as _parse_season_from_text,
)

WORK_ROOT = Path(__file__).resolve().parents[1] / "work"
WIRED = ("download", "asr", "translate", "tts", "mux")
_PERSIST_NAME = "_job_queue.json"


def get_job_info(job_id: str, *, prefer_db: bool = True) -> dict:
    """Metadata hàng chờ: ưu tiên films.db (series_ui/season_ui), fallback manifest."""
    jid = str(job_id or "").strip()
    fallback = {
        "job_id": jid,
        "title": jid,
        "series": jid,
        "season": 1,
        "group_id": None,
        "group_index": None,
        "group_title": None,
    }
    if not jid:
        return fallback

    if prefer_db:
        try:
            import core.film_db as film_db  # noqa: PLC0415
            row = film_db.get_lite(jid)
            if row and (row.get("series_ui") or row.get("season_ui") is not None):
                mapped = info_from_film_row(row)
                if mapped:
                    return mapped
        except Exception:
            pass

    wd = WORK_ROOT / jid
    mf = wd / "manifest.json"
    if not mf.is_file():
        # DB row thiếu UI cols nhưng có title
        try:
            import core.film_db as film_db  # noqa: PLC0415
            mapped = info_from_film_row(film_db.get_lite(jid))
            if mapped:
                return mapped
        except Exception:
            pass
        return fallback
    try:
        data = json.loads(mf.read_text(encoding="utf-8"))
    except Exception:
        return fallback
    info = info_from_manifest_dict(jid, data)
    # Lazy sync để lần sau đọc DB
    try:
        import core.film_db as film_db  # noqa: PLC0415
        film_db.sync_one(jid)
    except Exception:
        pass
    return {
        "job_id": info["job_id"],
        "title": info["title"],
        "series": info["series"],
        "season": info["season"],
        "group_id": info.get("group_id"),
        "group_index": info.get("group_index"),
        "group_title": info.get("group_title"),
    }


def get_jobs_info(job_ids: list[str]) -> dict[str, dict]:
    """Batch metadata cho nhiều job — 1 query DB + fallback file từng id thiếu."""
    ids = [str(x).strip() for x in (job_ids or []) if str(x).strip()]
    out: dict[str, dict] = {}
    if not ids:
        return out
    rows: dict[str, dict] = {}
    try:
        import core.film_db as film_db  # noqa: PLC0415
        rows = film_db.get_many(ids)
    except Exception:
        rows = {}
    missing: list[str] = []
    for jid in ids:
        row = rows.get(jid)
        mapped = info_from_film_row(row) if row else None
        if mapped and row and (row.get("series_ui") or row.get("season_ui") is not None):
            out[jid] = mapped
        else:
            missing.append(jid)
    for jid in missing:
        out[jid] = get_job_info(jid, prefer_db=False)
    return out


def job_sort_key(job_id: str) -> tuple:
    """Khóa sắp xếp: (group_id|series_norm, season P1..Pn, title)."""
    info = get_job_info(job_id)
    series_key = (info.get("group_id") or "").strip() or _norm_series_key(info.get("series") or "")
    return (series_key.lower(), int(info.get("season") or 1), (info.get("title") or "").lower())

_lock = threading.RLock()
_q: list[str] = []
_current: str | None = None
_opts: dict = {}  # fallback / last default (compat)
_opts_by_job: dict[str, dict] = {}
_hist: list[dict] = []
_stop = False
_thread: threading.Thread | None = None
_runner: Callable[[str, dict], tuple[str, str]] | None = None
_clear_stop_hook: Callable[[str], None] | None = None


def _reset_for_tests(load_disk: bool = False) -> None:
    """Chỉ dùng trong pytest."""
    global _q, _current, _opts, _opts_by_job, _hist, _stop, _thread, _runner, _clear_stop_hook
    with _lock:
        _stop = True
        old_thread = _thread
    if old_thread and old_thread is not threading.current_thread():
        old_thread.join(timeout=2)
    with _lock:
        _q.clear()
        _current = None
        _opts = {}
        _opts_by_job = {}
        _hist = []
        _stop = True
        _thread = None
        _runner = None
        _clear_stop_hook = None
        set_stop_hook(None)
    if load_disk:
        _load()


def set_runner(fn: Callable[[str, dict], tuple[str, str]]) -> None:
    global _runner
    _runner = fn


def is_wired_done(work_dir: Path) -> bool:
    mf = work_dir / "manifest.json"
    out = work_dir / "output.mp4"
    if not mf.is_file() or not out.is_file() or out.stat().st_size <= 0:
        return False
    try:
        data = json.loads(mf.read_text(encoding="utf-8"))
    except Exception:
        return False
    stages = data.get("stages") or {}
    return all((stages.get(s) or {}).get("status") == "done" for s in WIRED)


def _persist_path() -> Path:
    return WORK_ROOT / _PERSIST_NAME


def _save() -> None:
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    payload = {
        "queue": list(_q),
        "opts": dict(_opts),
        "opts_by_job": {k: dict(v) for k, v in _opts_by_job.items()},
        "current": _current,
    }
    target = _persist_path()
    temp = target.with_name(f".{target.name}.tmp")
    with temp.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, target)


def _load() -> None:
    global _q, _opts, _opts_by_job, _current
    p = _persist_path()
    if not p.is_file():
        return
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return
    with _lock:
        _q = [str(x) for x in (data.get("queue") or []) if str(x).strip()]
        _opts = dict(data.get("opts") or {})
        raw_ob = data.get("opts_by_job") or {}
        _opts_by_job = {
            str(k): dict(v) for k, v in raw_ob.items() if isinstance(v, dict)
        }
        # Migrate: old persist only had global opts → apply to pending jobs
        if _opts and not _opts_by_job:
            for jid in _q:
                _opts_by_job[jid] = dict(_opts)
        cur = data.get("current")
        if cur and cur not in _q:
            _q.insert(0, str(cur))
            if _opts and str(cur) not in _opts_by_job:
                _opts_by_job[str(cur)] = dict(_opts)
        _current = None


def _hist_push(job_id: str, status: str, detail: str = "") -> None:
    _hist.append(
        {"job_id": job_id, "status": status, "detail": detail, "ts": time.time()}
    )
    del _hist[:-20]


def queue_busy() -> bool:
    """True nếu worker đang chạy hoặc còn job trong hàng — dùng GPU gate heal/watch."""
    with _lock:
        return bool(_current) or bool(_q) or bool(_thread and _thread.is_alive())


def current_detail(job_id: str | None, *, work_root: Path | None = None) -> dict | None:
    """Stage/progress/ETA thô — đọc manifest của đúng 1 job (live)."""
    if not job_id:
        return None
    root = work_root if work_root is not None else WORK_ROOT
    wd = root / job_id
    mf = wd / "manifest.json"
    if not mf.is_file():
        return {"job_id": job_id, "error": "no manifest"}
    try:
        data = json.loads(mf.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return {"job_id": job_id, "error": str(e)}
    stages = data.get("stages") or {}
    running = None
    for name in ("mux", "tts", "translate", "asr", "download", "ocr", "separate"):
        st = stages.get(name) or {}
        if st.get("status") == "running":
            running = name
            break
    if running is None:
        for name, st in stages.items():
            if isinstance(st, dict) and st.get("status") == "running":
                running = name
                break
    st = (stages.get(running) or {}) if running else {}
    prog = st.get("progress")
    try:
        prog_f = float(prog) if prog is not None else None
    except (TypeError, ValueError):
        prog_f = None
    updated = st.get("started_at") or st.get("updated_at")
    eta_sec = None
    if prog_f is not None and updated and prog_f > 5:
        try:
            elapsed = time.time() - float(updated)
            if elapsed > 30 and prog_f < 99:
                eta_sec = int(elapsed * (100.0 - prog_f) / max(prog_f, 1.0))
                eta_sec = max(0, min(eta_sec, 48 * 3600))
        except (TypeError, ValueError, ZeroDivisionError):
            eta_sec = None
    req = data.get("request") or {}
    return {
        "job_id": job_id,
        "title": data.get("title_vi") or req.get("title") or job_id,
        "group_id": req.get("group_id"),
        "group_index": req.get("group_index"),
        "group_title": req.get("group_title"),
        "stage": running,
        "progress": prog_f,
        "cur_text": st.get("cur_text") or st.get("phase"),
        "eta_sec": eta_sec,
        "audio_mode": st.get("audio_mode") if running == "mux" else None,
    }


def build_queue_items(job_ids: list[str]) -> list[dict]:
    """Metadata pending — 1 batch films.db (+ fallback), không N lần parse manifest."""
    pending = [str(x).strip() for x in (job_ids or []) if str(x).strip()]
    infos = get_jobs_info(pending)
    items: list[dict] = []
    for jid in pending:
        info = infos.get(jid) or get_job_info(jid)
        gi = info.get("group_index")
        if gi in (None, ""):
            gi = info.get("season")
        items.append({
            "job_id": jid,
            "title": info.get("title") or jid,
            "series": info.get("series") or info.get("group_title") or "",
            "season": info.get("season") or gi or 1,
            "group_id": info.get("group_id"),
            "group_index": info.get("group_index"),
            "group_title": info.get("group_title"),
        })
    return items


def queue_state(*, enrich: bool = True) -> dict:
    """Trạng thái hàng chờ. enrich=True → queue_items/current_info qua batch DB."""
    with _lock:
        pending = list(_q)
        cur = _current
        st = {
            "queue": pending,
            "queue_items": [],
            "current": cur,
            "current_info": None,
            "history": list(_hist[-20:]),
            "worker": bool(_thread and _thread.is_alive()),
            "opts": dict(_opts),
            "opts_by_job": {k: dict(v) for k, v in _opts_by_job.items()},
            "busy": bool(cur) or bool(pending) or bool(_thread and _thread.is_alive()),
        }
    if enrich:
        st["queue_items"] = build_queue_items(pending)
        if cur:
            infos = get_jobs_info([cur])
            st["current_info"] = infos.get(cur) or get_job_info(cur)
    return st


def http_queue_state(*, work_root: Path | None = None) -> dict:
    """Payload GET /api/queue/jobs: state + live current_detail + labels ngắn."""
    st = queue_state(enrich=True)
    cur = st.get("current")
    st["current_detail"] = current_detail(cur, work_root=work_root)
    items = st.get("queue_items") or []
    labels = []
    for it in items[:12]:
        jid = it.get("job_id") or ""
        gi = it.get("group_index")
        if gi in (None, ""):
            gi = it.get("season")
        prefix = f"P{gi} " if gi not in (None, "") else ""
        title = it.get("title") or jid
        labels.append({"job_id": jid, "label": f"{prefix}{str(title)[:40]}"})
    st["queue_labels"] = labels
    return st


def queue_add(
    job_ids: list[str],
    opts: dict | None = None,
    skip_done: bool = True,
    sort_first: bool = True,
) -> dict:
    global _opts, _stop
    cleaned: list[str] = []
    skipped_done: list[str] = []
    skipped_missing: list[str] = []
    seen: set[str] = set()
    for raw in job_ids or []:
        jid = str(raw or "").strip()
        if not jid or jid in seen:
            continue
        seen.add(jid)
        wd = WORK_ROOT / jid
        if not (wd / "manifest.json").is_file():
            skipped_missing.append(jid)
            continue
        if skip_done and is_wired_done(wd):
            skipped_done.append(jid)
            continue
        cleaned.append(jid)
    if sort_first and len(cleaned) > 1:
        cleaned.sort(key=job_sort_key)
    with _lock:
        appended: list[str] = []
        for jid in cleaned:
            if jid not in _q and jid != _current:
                _q.append(jid)
                appended.append(jid)
                if opts is not None:
                    _opts_by_job[jid] = dict(opts)
        if appended:
            if opts is not None:
                # fallback default cho job cũ chưa có snapshot
                _opts = dict(opts)
            _stop = False
        _save()
        if appended:
            _ensure_worker_unlocked()
        return {
            "ok": True,
            "queued": appended,
            "skipped_done": skipped_done,
            "skipped_missing": skipped_missing,
            "queue": list(_q),
            "current": _current,
        }


def queue_sort(by: str = "series_season") -> dict:
    """Sắp xếp lại các job đang chờ trong hàng:
    - 'series_season': Nhóm theo tên bộ + Phần 1, 2, 3..
    - 'name': Theo tên tiêu đề A-Z
    - 'reverse': Đảo ngược thứ tự
    """
    with _lock:
        if by == "series_season":
            _q.sort(key=job_sort_key)
        elif by == "name":
            _q.sort(key=lambda jid: get_job_info(jid)["title"].lower())
        elif by == "reverse":
            _q.reverse()
        _save()
    return {"ok": True, "by": by, **queue_state()}


def queue_move(job_id: str, action: str) -> dict:
    """Di chuyển vị trí của 1 job trong hàng chờ:
    action: 'top' (lên đầu), 'up' (lên 1 nấc), 'down' (xuống 1 nấc), 'bottom' (xuống cuối)
    """
    jid = str(job_id or "").strip()
    with _lock:
        if jid not in _q:
            err = f"Job '{jid}' không có trong hàng chờ"
            return {"ok": False, "error": err, **queue_state()}
        idx = _q.index(jid)
        if action == "top":
            if idx > 0:
                _q.pop(idx)
                _q.insert(0, jid)
        elif action == "up":
            if idx > 0:
                _q[idx - 1], _q[idx] = _q[idx], _q[idx - 1]
        elif action == "down":
            if idx < len(_q) - 1:
                _q[idx], _q[idx + 1] = _q[idx + 1], _q[idx]
        elif action == "bottom":
            if idx < len(_q) - 1:
                _q.pop(idx)
                _q.append(jid)
        else:
            return {"ok": False, "error": f"Hành động không hợp lệ: {action}", **queue_state()}
        _save()
    return {"ok": True, "moved": jid, "action": action, **queue_state()}


def queue_reorder(new_order: list[str]) -> dict:
    """Gán lại toàn bộ thứ tự cho hàng chờ theo danh sách client gửi."""
    with _lock:
        clean_order = [str(x).strip() for x in (new_order or []) if str(x).strip()]
        order_set = set(clean_order)
        reordered = [j for j in clean_order if j in _q]
        leftover = [j for j in _q if j not in order_set]
        _q[:] = reordered + leftover
        _save()
    return {"ok": True, **queue_state()}


def queue_add_group(
    group_id: str,
    opts: dict | None = None,
    skip_done: bool = True,
) -> dict:
    """Enqueue mọi member của group theo group_index tăng dần."""
    gid = str(group_id or "").strip()
    if not gid:
        return {"ok": False, "error": "thiếu group_id", "queued": []}
    members: list[tuple[int, str]] = []
    if WORK_ROOT.is_dir():
        for d in WORK_ROOT.iterdir():
            mf = d / "manifest.json"
            if not mf.is_file():
                continue
            try:
                data = json.loads(mf.read_text(encoding="utf-8"))
                req = data.get("request") or {}
                if req.get("group_id") != gid:
                    continue
                idx = int(req.get("group_index") or 9999)
                members.append((idx, d.name))
            except Exception:  # noqa: BLE001
                continue
    members.sort(key=lambda x: (x[0], x[1]))
    ids = [jid for _, jid in members]
    if not ids:
        return {
            "ok": False,
            "error": f"không có job nào thuộc group {gid}",
            "queued": [],
            "group_id": gid,
        }
    r = queue_add(ids, opts=opts, skip_done=skip_done)
    r["group_id"] = gid
    r["group_order"] = ids
    return r


def queue_front(job_id: str) -> None:
    with _lock:
        if job_id in _q:
            _q.remove(job_id)
            _q.insert(0, job_id)
            _save()


def queue_remove(job_ids: list[str]) -> dict:
    """Bỏ job khỏi hàng chờ (không stop current)."""
    want = {str(x).strip() for x in (job_ids or []) if str(x).strip()}
    with _lock:
        kept = [j for j in _q if j not in want]
        removed = [j for j in _q if j in want]
        _q[:] = kept
        for jid in removed:
            _opts_by_job.pop(jid, None)
        _save()
        return {"ok": True, "removed": removed, "queue": list(_q), "current": _current}


def queue_update_opts(updates: dict[str, dict]) -> dict:
    """Đổi opts của job ĐANG CHỜ tại chỗ (giữ thứ tự, không đụng current) — thay cho remove+add."""
    with _lock:
        updated = [j for j in _q if j in updates]
        for jid in updated:
            _opts_by_job[jid] = dict(updates[jid])
        skipped = [j for j in updates if j not in updated]
        if updated:
            _save()
        return {"ok": True, "updated": updated, "skipped": skipped, "queue": list(_q), "current": _current}


def queue_clear() -> dict:
    with _lock:
        _q.clear()
        _opts_by_job.clear()
        _save()
    return {"ok": True, **queue_state()}


def queue_stop() -> dict:
    """Clear queue + báo worker dừng; gọi _stop_job(current) nếu server đã wire."""
    global _stop, _current
    with _lock:
        _stop = True
        _q.clear()
        # giữ opts_by_job của current để runner còn đọc; dọn pending
        cur = _current
        pending_opts = {k: v for k, v in _opts_by_job.items() if k == cur}
        _opts_by_job.clear()
        _opts_by_job.update(pending_opts)
        _save()
    if cur and _runner is not None:
        stop_hook = getattr(queue_stop, "_hook", None)
        if callable(stop_hook):
            try:
                stop_hook(cur)
            except Exception:
                pass
    return {"ok": True, "stopped_job": cur}


def set_stop_hook(fn: Callable[[str], None] | None) -> None:
    queue_stop._hook = fn  # type: ignore[attr-defined]


def set_clear_stop_hook(fn: Callable[[str], None] | None) -> None:
    global _clear_stop_hook
    _clear_stop_hook = fn


def _ensure_worker_unlocked() -> None:
    global _thread, _stop
    if _thread and _thread.is_alive():
        return
    _stop = False
    _thread = threading.Thread(
        target=_worker_loop, daemon=True, name="pineline-job-queue"
    )
    _thread.start()


def _ensure_worker() -> None:
    with _lock:
        _ensure_worker_unlocked()


def _worker_loop() -> None:
    global _current, _stop, _thread
    while True:
        with _lock:
            if _stop:
                _current = None
                _thread = None
                _save()
                return
            if not _q:
                _current = None
                _thread = None
                _save()
                return
            job_id = _q.pop(0)
            if _clear_stop_hook is not None:
                try:
                    _clear_stop_hook(job_id)
                except Exception:
                    pass
            _current = job_id
            # get (không pop): server chết giữa job → _load đưa current lại đầu hàng với đúng opts
            opts = dict(_opts_by_job.get(job_id) or _opts)
            _save()
        status = "failed"
        detail = ""
        try:
            if _runner is None:
                status, detail = "failed", "no runner"
            else:
                result = _runner(job_id, opts)
                if isinstance(result, tuple):
                    status, detail = result
                else:
                    status = result or "failed"
        except Exception as e:  # noqa: BLE001
            status, detail = "failed", str(e)[:200]
        with _lock:
            _hist_push(job_id, status, detail)
            _current = None
            if job_id not in _q:
                _opts_by_job.pop(job_id, None)
            _save()
            if _stop:
                _thread = None
                return


# Load persist khi import (server có thể set WORK_ROOT trước — xem Task 2).
# Dưới pytest không nạp hàng chờ thật: worker test sẽ chạy job thật song song server.
if "pytest" not in sys.modules:
    _load()
