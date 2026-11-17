# -*- coding: utf-8 -*-
"""Second Brain — tự thử lại stage FAILED (2026-11-17).

Vì sao: L1 heal của brain chỉ chạy khi hàng đợi RẢNH, mà hàng đợi gần như luôn bận
(log: 6071/6071 tick «tick busy — skip L1 heal») → job failed nằm đó mãi, không ai thử lại.

Cách làm (không cần GPU ngay, không giết engine đang chạy):
  job có stage failed, KHÔNG đang chạy, KHÔNG trong hàng đợi, KHÔNG .stop (người dừng)
  → phân loại lỗi (agent_error_class): notify_only/none (thiếu giọng, đầy đĩa, source hỏng, user dừng)
    → chỉ báo 1 lần, không thử lại;
  → còn lại: đặt stage lỗi về pending, GIỮ artifact (clip TTS đã đọc, script đã dịch…; chỉ xoá
    output.partial.mp4) + xếp lại hàng đợi (hook resume)
    — pipeline bỏ qua bước đã xong. Backoff RETRY_BACKOFF_MIN (mặc định 5,15,45 phút),
    tối đa RETRY_MAX (3) lần / (job, stage); quá → báo người xem.
Tắt: AGENT_RETRY=0.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable

WIRED = ("download", "asr", "translate", "tts", "mux")


def _cfg(key: str, default: str) -> str:
    try:
        from core.config import get
        v = get(key, None)
    except Exception:  # noqa: BLE001
        v = os.getenv(key)
    return default if v is None or str(v).strip() == "" else str(v).strip()


def enabled() -> bool:
    return _cfg("AGENT_RETRY", "1").lower() in ("1", "true", "yes", "on")


def _backoff() -> list[float]:
    try:
        return [max(1.0, float(x)) * 60 for x in _cfg("RETRY_BACKOFF_MIN", "5,15,45").split(",") if x.strip()]
    except ValueError:
        return [300.0, 900.0, 2700.0]


def _max_tries() -> int:
    try:
        return max(0, int(_cfg("RETRY_MAX", "3")))
    except ValueError:
        return 3


def _queued_ids() -> set[str]:
    try:
        import core.job_queue as jq
        st = jq.queue_state() or {}
        ids = {str(x if isinstance(x, str) else (x or {}).get("job_id") or "") for x in (st.get("queue") or [])}
        if st.get("current"):
            ids.add(str(st.get("current")))
        return ids
    except Exception:  # noqa: BLE001
        return set()


def _classify(stage: str, st: dict) -> dict:
    try:
        from agents.agent_error_class import classify_stage_status
        return classify_stage_status(stage, st) or {}
    except Exception:  # noqa: BLE001
        return {}


def _soft_reset(d: Path, failed: list[str]) -> dict:
    """failed → pending, giữ mọi artifact (pipeline tự bỏ qua / đọc bù phần đã có)."""
    try:
        from core.manifest import Manifest
    except ImportError:  # V5
        from core.manifest import Manifest  # type: ignore

    def _fn(data: dict) -> None:
        stg = data.setdefault("stages", {})
        for s in failed:
            st = dict(stg.get(s) or {})
            st["retry_prev_error"] = str(st.get("error") or st.get("cur_text") or "")[:300]
            st["status"] = "pending"
            st.pop("error", None)
            st["cur_text"] = "Brain: thử lại"
            stg[s] = st
    Manifest(d).update(_fn)
    if "mux" in failed:
        try:
            (d / "output.partial.mp4").unlink(missing_ok=True)
        except OSError:
            pass
    return {"ok": True, "pending": failed}


def retry_failed_jobs(
    work_root: Path,
    state: dict,
    hooks: dict[str, Callable[..., Any]],
    *,
    log: Callable[[str], None] = print,
    notify: Callable[[str], None] | None = None,
    is_finished: Callable[[Path, dict], bool] | None = None,
    max_jobs: int = 40,
    now: float | None = None,
) -> list[dict]:
    if not enabled():
        return []
    now = time.time() if now is None else now
    work_root = Path(work_root)
    track: dict = state.setdefault("retry", {})
    out: list[dict] = []
    try:
        dirs = sorted([d for d in work_root.iterdir() if d.is_dir() and (d / "manifest.json").is_file()],
                      key=lambda p: p.stat().st_mtime, reverse=True)[:max_jobs]
    except OSError:
        return out
    queued = _queued_ids()
    backoff, max_n = _backoff(), _max_tries()
    for d in dirs:
        jid = d.name
        try:
            mf = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        stages = mf.get("stages") or {}
        failed = [s for s in WIRED if (stages.get(s) or {}).get("status") == "failed"]
        # stage đã hết failed → xoá bộ đếm của stage đó
        for k in [k for k in track if k.startswith(jid + ":")]:
            if k.split(":", 1)[1] not in failed:
                track.pop(k, None)
        if not failed or (d / ".stop").exists():
            continue
        if is_finished and is_finished(d, mf):
            continue
        if jid in queued:
            continue
        ag = mf.get("agent") or {}
        if ag.get("qa_blocked") or ag.get("held_at"):
            continue   # HOLD (QA/duyệt/park) có đường xử lý riêng — retry không được gỡ HOLD
        try:
            from agents.agent_heal import job_active
            if job_active(jid, hooks):
                continue
        except Exception:  # noqa: BLE001
            pass
        stage = failed[0]
        st = stages.get(stage) or {}
        err = str(st.get("error") or st.get("cur_text") or "")[:200]
        key = f"{jid}:{stage}"
        rec = track.setdefault(key, {"n": 0, "first": now, "last": 0.0, "err": err})
        cls = _classify(stage, st)
        if cls.get("safe_action") in ("notify_only", "none"):
            if not rec.get("notified"):
                rec["notified"] = now
                msg = (f"Brain: {jid} {stage} lỗi «{cls.get('class')}» — không tự thử lại. "
                       f"{cls.get('hint') or ''} ({err[:120]})")
                log(msg)
                if notify:
                    notify(msg)
            continue
        if rec["n"] >= max_n:
            if not rec.get("gave_up"):
                rec["gave_up"] = now
                msg = f"Brain: {jid} {stage} đã tự thử lại {rec['n']} lần vẫn lỗi — cần người xem: {err[:160]}"
                log(msg)
                if notify:
                    notify(msg)
            continue
        wait = backoff[min(rec["n"], len(backoff) - 1)] if backoff else 300.0
        since = rec["last"] or rec["first"]
        if now - since < wait:
            continue
        # Thử lại: reset stage lỗi (+ downstream do reset_job_state tự xử lý) rồi xếp hàng
        res: dict[str, Any] = {"job_id": jid, "stage": stage, "try": rec["n"] + 1, "err": err,
                               "class": cls.get("class") or "unknown"}
        try:
            res["reset"] = _soft_reset(d, failed)
            fn_resume = hooks.get("resume")
            res["resume"] = fn_resume(jid) if fn_resume else {"skipped": "no resume hook"}
        except Exception as e:  # noqa: BLE001
            res["error"] = str(e)[:200]
        rec["n"] += 1
        rec["last"] = now
        rec["err"] = err
        msg = (f"Brain RETRY {jid} {stage} lần {rec['n']}/{max_n} (lỗi: {res['class']} — {err[:100]}) → "
               f"{'xếp lại hàng đợi' if (res.get('resume') or {}).get('ok') else json.dumps(res.get('resume') or res.get('error'), ensure_ascii=False)[:120]}")
        log(msg)
        if notify:
            notify(msg)
        out.append(res)
    return out
