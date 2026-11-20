# -*- coding: utf-8 -*-
"""Gộp job đã render (Films UI «Gộp job đã làm») — chạy NỀN + log/status.

POST /films/combine → start() xếp 1 lần gộp (1 luồng).
GET  /films/combine/status → phase / % / log / kết quả.

State/log bền trên đĩa (`work/logs/films_combine_state.json` + `.log`) để F5 / reload
module vẫn thấy tiến độ. Không phụ thuộc RAM sau `importlib.reload`.
"""
from __future__ import annotations

import collections
import json
import re
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

_lock = threading.Lock()
_state: dict[str, Any] = {
    "running": False,
    "phase": "idle",
    "text": "",
    "pct": 0,
    "job_ids": [],
    "started_at": None,
    "updated_at": None,
    "result": None,
    "error": None,
}
_logbuf: collections.deque = collections.deque(maxlen=400)
_worker: threading.Thread | None = None
_ROOT = Path(__file__).resolve().parents[1]
_log_path: Path = _ROOT / "work" / "logs" / "films_combine.log"
_state_path: Path = _ROOT / "work" / "logs" / "films_combine_state.json"

_RE_PHASE = re.compile(
    r"\[combine\]\s+(?:(?P<phase>validate|concat|scripts|manifest|publish|finalize|queued|done|failed):\s*)?(?P<text>.*)$"
)


def set_log_dir(d: Path) -> None:
    global _log_path, _state_path
    d = Path(d)
    _log_path = d / "films_combine.log"
    _state_path = d / "films_combine_state.json"


def _now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _combine_thread_alive() -> bool:
    for t in threading.enumerate():
        if t.name == "films-combine" and t.is_alive():
            return True
    return False


def _persist_unlocked() -> None:
    """Ghi state JSON (gọi trong _lock hoặc chấp nhận race nhẹ)."""
    try:
        _state_path.parent.mkdir(parents=True, exist_ok=True)
        payload = dict(_state)
        payload["log_tail"] = list(_logbuf)[-40:]
        tmp = _state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(_state_path)
    except OSError:
        pass


def _load_disk_state() -> dict[str, Any] | None:
    try:
        if not _state_path.is_file():
            return None
        return json.loads(_state_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _tail_log_file(n: int = 80) -> list[str]:
    try:
        if not _log_path.is_file():
            return []
        lines = _log_path.read_text(encoding="utf-8", errors="replace").splitlines()
        return lines[-max(1, int(n or 80)) :]
    except OSError:
        return []


def _infer_from_log(lines: list[str]) -> dict[str, Any]:
    """Khôi phục phase/text/job_ids từ log file khi RAM bị reload xoá."""
    out: dict[str, Any] = {}
    if not lines:
        return out
    for line in reversed(lines):
        if " [combine] start " in line and "jobs:" in line:
            try:
                part = line.split("jobs:", 1)[1].strip()
                ids = [x.strip() for x in part.replace("…", "").split(",") if x.strip()]
                if ids:
                    out["job_ids"] = ids
            except Exception:  # noqa: BLE001
                pass
            break
    last = lines[-1]
    m = _RE_PHASE.search(last)
    if m:
        ph = (m.group("phase") or "").strip()
        tx = (m.group("text") or "").strip()
        if ph:
            out["phase"] = ph
        if tx:
            out["text"] = tx if not ph else f"{ph}: {tx}" if not tx.startswith(ph) else tx
            if ph and ": " in (m.group(0) or ""):
                out["text"] = tx
    # pct heuristic
    pct = None
    blob = "\n".join(lines[-15:])
    if "done job_id=" in blob or "\ndone " in last or (out.get("phase") == "done"):
        pct = 100
        out["phase"] = "done"
        out["running"] = False
    elif "failed:" in blob or out.get("phase") == "failed":
        out["phase"] = "failed"
        out["running"] = False
        pct = out.get("pct")
    elif "reencode" in blob or "copy " in blob or "TS copy" in blob or "Chuẩn hoá" in blob:
        pct = 35
        out["phase"] = out.get("phase") or "concat"
        out["running"] = True
    elif "Nối" in blob or "concat" in blob.lower():
        pct = 55
        out["phase"] = "concat"
        out["running"] = True
    elif "validate" in blob:
        pct = 10
        out["phase"] = "validate"
        out["running"] = True
    elif "start " in blob:
        pct = 5
        out["running"] = True
        out["phase"] = out.get("phase") or "queued"
    if pct is not None:
        out["pct"] = pct
    # mtime gần → còn sống
    try:
        age = time.time() - _log_path.stat().st_mtime
        if out.get("running") is None and age < 180 and out.get("phase") not in ("done", "failed", "idle", None):
            out["running"] = True
        if age > 900 and out.get("phase") not in ("done", "failed") and not _combine_thread_alive():
            # log cũ, không thread → coi như chết giữa chừng
            if out.get("running"):
                out["running"] = False
                out["phase"] = "failed"
                out["error"] = "tiến trình gộp mất (sidecar reload/restart?) — xem log"
    except OSError:
        pass
    return out


def _log(msg: str) -> None:
    line = f"{_now()} [combine] {msg}"
    print(line, flush=True)
    _logbuf.append(line)
    try:
        _log_path.parent.mkdir(parents=True, exist_ok=True)
        with _log_path.open("a", encoding="utf-8") as f:
            f.write(f"{datetime.now():%Y-%m-%d} {line}\n")
    except OSError:
        pass
    with _lock:
        _persist_unlocked()


def _set(**kw: Any) -> None:
    with _lock:
        _state.update(kw)
        _state["updated_at"] = time.time()
        _persist_unlocked()


def _progress(info: dict[str, Any]) -> None:
    phase = str(info.get("phase") or _state.get("phase") or "")
    text = str(info.get("text") or "")
    pct = info.get("pct")
    kw: dict[str, Any] = {"phase": phase, "text": text}
    if pct is not None:
        try:
            kw["pct"] = max(0, min(100, int(pct)))
        except (TypeError, ValueError):
            pass
    _set(**kw)
    if text:
        _log(f"{phase}: {text}" if phase else text)


def _is_busy() -> tuple[bool, dict[str, Any]]:
    alive = _combine_thread_alive() or bool(_worker and _worker.is_alive())
    with _lock:
        mem = dict(_state)
    if mem.get("running") or alive:
        return True, mem
    disk = _load_disk_state() or {}
    if disk.get("running") and (disk.get("phase") not in ("done", "failed", "idle")):
        # xác nhận thread/log còn sống
        if alive or _combine_thread_alive():
            return True, disk
        log_lines = _tail_log_file(30)
        inferred = _infer_from_log(log_lines)
        if inferred.get("running"):
            return True, {**disk, **inferred}
    log_lines = _tail_log_file(20)
    inferred = _infer_from_log(log_lines)
    if inferred.get("running") and _combine_thread_alive():
        return True, inferred
    if _combine_thread_alive():
        return True, {**mem, **inferred, "running": True}
    return False, mem


def status(*, log_lines: int = 80) -> dict[str, Any]:
    n = max(1, int(log_lines or 80))
    file_log = _tail_log_file(n)
    disk = _load_disk_state() or {}
    alive = _combine_thread_alive() or bool(_worker and _worker.is_alive())
    with _lock:
        mem = dict(_state)
        mem_log = list(_logbuf)

    # Ưu tiên: memory nếu đang chạy; không thì disk; luôn bổ sung log file (survives reload).
    st: dict[str, Any] = dict(disk)
    st.update({k: v for k, v in mem.items() if v not in (None, "", [], {}) or k in ("running", "phase", "pct")})
    if mem.get("running") or (mem.get("phase") and mem.get("phase") != "idle"):
        st.update(mem)
    inferred = _infer_from_log(file_log)
    if (not st.get("running") and st.get("phase") in (None, "", "idle")) or not mem_log:
        for k, v in inferred.items():
            if v is not None and (not st.get(k) or st.get("phase") in (None, "", "idle") or k in ("running", "phase", "text", "pct", "job_ids")):
                if k == "running" and st.get("phase") in ("done", "failed") and not alive:
                    continue
                st[k] = v
    if alive:
        st["running"] = True
        if st.get("phase") in (None, "", "idle"):
            st["phase"] = inferred.get("phase") or st.get("phase") or "concat"
    # log: memory + file (file thắng nếu dài hơn — sau reload)
    log = mem_log[-n:] if len(mem_log) >= len(file_log) and mem_log else file_log[-n:]
    if file_log and (not log or len(file_log) > len(log)):
        log = file_log[-n:]
    st["ok"] = True
    st["log"] = log
    st["worker"] = alive
    st["persisted"] = bool(disk) or bool(file_log)
    return st


def _load_feeder():
    """Tách để test monkeypatch; production vẫn reload agent_feeder."""
    import importlib
    import agents.agent_feeder as feeder

    return importlib.reload(feeder)


def start(
    base: str,
    job_ids: list[str],
    *,
    custom_title_vi: str | None = None,
    auto_publish: bool = False,
    preserve_order: bool = False,
    allow_oversized: bool = False,
) -> dict[str, Any]:
    """Xếp gộp nền. Một lần một job gộp — nếu đang chạy → busy."""
    global _worker
    clean = [str(x).strip() for x in (job_ids or []) if str(x).strip()]
    if len(clean) < 2:
        return {"ok": False, "error": "Cần chọn ít nhất 2 job đã xong để gộp"}

    busy, cur = _is_busy()
    if busy:
        return {
            "ok": False,
            "busy": True,
            "error": f"Đang gộp ({cur.get('phase')}: {cur.get('text') or '…'}) — đợi xong rồi thử lại",
            "status": status(),
        }

    _set(
        running=True,
        phase="queued",
        text=f"Xếp gộp {len(clean)} job…",
        pct=1,
        job_ids=clean,
        started_at=time.time(),
        result=None,
        error=None,
    )
    _log(f"start {len(clean)} jobs: {', '.join(clean[:8])}{'…' if len(clean)>8 else ''}")

    def _run() -> None:
        try:
            feeder = _load_feeder()
            _progress({"phase": "validate", "text": f"Kiểm {len(clean)} job + output.mp4…", "pct": 5})

            def on_progress(info: dict[str, Any]) -> None:
                _progress(info if isinstance(info, dict) else {"text": str(info)})

            r = feeder.combine_rendered_jobs(
                base,
                job_ids=clean,
                custom_title_vi=custom_title_vi,
                auto_publish=auto_publish,
                preserve_order=preserve_order,
                allow_oversized=allow_oversized,
                on_progress=on_progress,
            )
            if r.get("ok"):
                title = r.get("title_vi") or r.get("title") or r.get("job_id")
                _progress(
                    {
                        "phase": "done",
                        "text": f"Xong «{title}» ({r.get('job_id')})",
                        "pct": 100,
                    }
                )
                _set(running=False, result=r, error=None)
                _log(f"done job_id={r.get('job_id')} mode={r.get('mode')} size_mb={r.get('size_mb')}")
            else:
                err = str(r.get("error") or "thất bại")
                _progress({"phase": "failed", "text": err, "pct": _state.get("pct") or 0})
                _set(running=False, result=r, error=err)
                _log(f"failed: {err}")
        except Exception as e:  # noqa: BLE001
            err = str(e)
            _progress({"phase": "failed", "text": err, "pct": 0})
            _set(running=False, result={"ok": False, "error": err}, error=err)
            _log(f"exception: {err}")

    t = threading.Thread(target=_run, name="films-combine", daemon=True)
    _worker = t
    t.start()
    return {"ok": True, "started": True, "job_ids": clean, "status": status()}
