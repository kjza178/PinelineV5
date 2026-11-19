# -*- coding: utf-8 -*-
"""Gộp job đã render (Films UI «Gộp job đã làm») — chạy NỀN + log/status.

POST /films/combine → start() xếp 1 lần gộp (1 luồng).
GET  /films/combine/status → phase / % / log / kết quả.

Log: console :8802 + `work/logs/films_combine.log` + `log` trong status (Films UI).
"""
from __future__ import annotations

import collections
import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable

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
_log_path: Path = Path(__file__).resolve().parents[1] / "work" / "logs" / "films_combine.log"


def set_log_dir(d: Path) -> None:
    global _log_path
    _log_path = Path(d) / "films_combine.log"


def _now() -> str:
    return datetime.now().strftime("%H:%M:%S")


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


def _set(**kw: Any) -> None:
    with _lock:
        _state.update(kw)
        _state["updated_at"] = time.time()


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


def status(*, log_lines: int = 80) -> dict[str, Any]:
    with _lock:
        st = dict(_state)
        log = list(_logbuf)[-max(1, int(log_lines or 80)) :]
    st["ok"] = True
    st["log"] = log
    st["worker"] = bool(_worker and _worker.is_alive())
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

    with _lock:
        if _state.get("running") or (_worker and _worker.is_alive()):
            return {
                "ok": False,
                "busy": True,
                "error": f"Đang gộp ({_state.get('phase')}: {_state.get('text') or '…'}) — đợi xong rồi thử lại",
                "status": dict(_state),
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
