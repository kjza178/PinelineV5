"""
Second Brain — daemon nền full-silent.

Sensors → incidents → policy → actuators.
Bật: AGENT_BRAIN=1 (hoặc pineline.config.json).
Telegram: AGENT_BRAIN_TELEGRAM=minimal|report|all|off (minimal=HOLD/L3; report/all=+digest định kỳ AGENT_BRAIN_TG_SEC).
"""
from __future__ import annotations

try:  # machine-config 11-11: key phụ thuộc máy (cổng/thư mục) — V5/V6 core/, V4 phẳng
    from core import machine as _machine
except ImportError:  # pragma: no cover
    import machine as _machine  # type: ignore
import json
import os
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


def _self_base() -> str:
    """URL server Pineline đang chạy brain (fix 2026-11-11: trước cứng :8801 → V4/V5 điều khiển nhầm V2)."""
    b = (os.getenv("PINELINE_BASE") or "").strip().rstrip("/")
    if b:
        return b
    port = (os.getenv("PINELINE_PORT") or "8801").strip() or "8801"
    return f"http://127.0.0.1:{port}"

# urllib dùng cho LLM HTTP fallback + infra ping


_lock = threading.Lock()
_thread: threading.Thread | None = None
_stop = threading.Event()


def _cfg(key: str, default: str = "") -> str:
    try:
        from core.config import get as _get
        v = _get(key)
        if v is not None and str(v).strip() != "":
            return str(v).strip()
    except Exception:  # noqa: BLE001
        pass
    return (os.getenv(key) or default).strip()


def _truthy(v: str) -> bool:
    return (v or "").strip().lower() in ("1", "true", "yes", "on")


def brain_enabled() -> bool:
    # Mặc định BẬT theo plan deploy; tắt tường minh AGENT_BRAIN=0
    raw = _cfg("AGENT_BRAIN", "1")
    if raw == "":
        return True
    return _truthy(raw)


def _interval_sec() -> int:
    try:
        return max(30, int(_cfg("AGENT_BRAIN_SEC", "60") or "60"))
    except ValueError:
        return 60


def _tg_mode() -> str:
    return (_cfg("AGENT_BRAIN_TELEGRAM", "minimal") or "minimal").lower()


def _log_dir(root: Path) -> Path:
    d = root / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def log_line(root: Path, msg: str) -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}\n"
    try:
        with (_log_dir(root) / "agent_brain.log").open("a", encoding="utf-8") as f:
            f.write(line)
    except Exception:  # noqa: BLE001
        pass
    print(f"[agent_brain] {msg}", flush=True)


def _state_path(root: Path) -> Path:
    return _log_dir(root) / "agent_brain_state.json"


def _load_state(root: Path) -> dict:
    p = _state_path(root)
    if not p.is_file():
        return {"fps": {}, "last_tick": None}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return {"fps": {}, "last_tick": None}


def _save_state(root: Path, state: dict) -> None:
    try:
        _state_path(root).write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8",
        )
    except Exception:  # noqa: BLE001
        pass


def _cooldown_ok(state: dict, fp: str, sec: float = 1800.0) -> bool:
    fps = state.setdefault("fps", {})
    prev = float((fps.get(fp) or {}).get("at") or 0)
    return (time.time() - prev) >= sec


def _mark_fp(state: dict, fp: str, note: str = "") -> None:
    fps = state.setdefault("fps", {})
    fps[fp] = {"at": time.time(), "note": note}


def _telegram(msg: str, *, level: str = "hold") -> None:
    mode = _tg_mode()
    if mode in ("0", "off", "none", "false"):
        return
    # minimal = chỉ HOLD/L3; report/all = thêm info/progress định kỳ
    if mode == "minimal" and level not in ("hold", "l3", "critical"):
        return
    if mode in ("report", "digest", "progress") and level not in (
        "hold", "l3", "critical", "info", "progress",
    ):
        return
    try:
        from agents.agent_watch import telegram_send
        telegram_send(msg, force=True, dedupe_key=f"brain:{level}:{msg[:120]}")
    except Exception as e:  # noqa: BLE001
        print(f"[agent_brain] tg skip: {e}", flush=True)


def _ping(url: str, timeout: float = 2.5) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            code = getattr(resp, "status", 200) or 200
            if 200 <= int(code) < 300:
                return True, f"ok:{code}"
            return False, f"http:{code}"
    except urllib.error.HTTPError as e:
        return False, f"http:{e.code}"
    except Exception as e:  # noqa: BLE001
        return False, str(e)[:80]


def sense_infra() -> list[dict]:
    out: list[dict] = []
    checks = [
        ("llama_8083", _machine.llama_base_url() + "/models"),
        ("chatgpt_3377", _machine.aurora_base_url() + "/models"),
        ("sidecar_8802", "http://127.0.0.1:8802/api/agent/status"),
    ]
    for name, url in checks:
        ok, detail = _ping(url)
        if not ok:
            sev = "l0"
            if name == "llama_8083" and "503" in detail:
                sev = "l0"
            out.append({
                "layer": "l0",
                "kind": "infra_down",
                "target": name,
                "detail": detail,
                "sev": sev,
            })
    return out


def sense_jobs(work_root: Path, *, max_jobs: int = 40) -> list[dict]:
    """Quét job có script / failed / stale cho quality + ops hints."""
    work_root = Path(work_root)
    incidents: list[dict] = []
    if not work_root.is_dir():
        return incidents
    dirs = sorted(
        [d for d in work_root.iterdir() if d.is_dir() and (d / "manifest.json").is_file()],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:max_jobs]
    for d in dirs:
        if (d / ".stop").exists():
            continue
        try:
            mf = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        stages = mf.get("stages") or {}
        agent = mf.get("agent") or {}
        # Ops: failed stages
        for name, st in stages.items():
            if not isinstance(st, dict):
                continue
            if st.get("status") == "failed":
                incidents.append({
                    "layer": "l1",
                    "kind": "stage_failed",
                    "job_id": d.name,
                    "stage": name,
                    "detail": (st.get("error") or st.get("cur_text") or "")[:200],
                })
        # Quality chỉ khi được đụng (không mid_review / post_tts)
        tr = stages.get("translate") or {}
        if (d / "script.json").is_file() and tr.get("status") in (
            "running", "done", "ok", "completed", "pending",
        ):
            phase = _qa_pipeline_phase(d)
            if phase["phase"] in ("mid_review", "post_tts"):
                continue
            incidents.append({
                "layer": "l2",
                "kind": "quality_scan",
                "job_id": d.name,
                "review": bool(tr.get("review")),
                "held": bool(agent.get("hold_after_translate") or agent.get("qa_blocked")),
                "phase": phase["phase"],
            })
    return incidents


def _qa_pipeline_phase(work_dir: Path) -> dict:
    """Perceive: job đang ở đâu — mid_review | pre_tts | post_tts | idle.

    Brain chỉ HOLD ở pre_tts (dịch/soát xong, TTS chưa chạy, còn high).
    """
    work_dir = Path(work_dir)
    out = {
        "phase": "idle",
        "busy": None,
        "tr_status": "",
        "tts_status": "",
        "mux_status": "",
        "review_progress": None,
        "can_touch_script": False,
        "can_hold": False,
    }
    try:
        from core.manifest import Manifest
        from agents.agent_hang_fix import _review_or_translate_busy
        m = Manifest(work_dir)
        stg = m.data.get("stages") or {}
        tr = stg.get("translate") or {}
        tts = stg.get("tts") or {}
        mux = stg.get("mux") or {}
        out["tr_status"] = str(tr.get("status") or "")
        out["tts_status"] = str(tts.get("status") or "")
        out["mux_status"] = str(mux.get("status") or "")
        try:
            out["review_progress"] = float(tr.get("review_progress")) if tr.get("review_progress") is not None else None
        except (TypeError, ValueError):
            out["review_progress"] = None
        busy = _review_or_translate_busy(work_dir)
        out["busy"] = busy
        tts_st = out["tts_status"].lower()
        mux_st = out["mux_status"].lower()
        if tts_st in ("done", "ok", "completed", "running") or mux_st in (
            "done", "ok", "completed", "running",
        ):
            out["phase"] = "post_tts"
            return out
        if busy:
            out["phase"] = "mid_review"
            return out
        tr_st = out["tr_status"].lower()
        rp = out["review_progress"]
        review_done = tr_st in ("done", "ok", "completed") or (
            bool(tr.get("reviewed") or tr.get("review"))
            and rp is not None
            and rp >= 99.5
        )
        if review_done or (tr_st in ("done", "ok", "completed")):
            out["phase"] = "pre_tts"
            out["can_touch_script"] = True
            out["can_hold"] = True
            return out
        # pending/idle có script nhưng chưa cửa TTS
        out["phase"] = "idle"
        out["can_touch_script"] = tr_st not in ("running",)
        return out
    except Exception as e:  # noqa: BLE001
        out["phase"] = "idle"
        out["busy"] = f"err:{e}"
        return out


def _gpu_or_queue_busy(work_root: Path) -> bool:
    try:
        import core.job_queue as _jq
        if _jq.queue_busy():
            return True
    except Exception:  # noqa: BLE001
        pass
    try:
        from agents.agent_watch import _gpu_busy
        return bool(_gpu_busy(work_root))
    except Exception:  # noqa: BLE001
        return False


def decide(incidents: list[dict], state: dict) -> list[dict]:
    """Policy full-silent → list actions."""
    actions: list[dict] = []
    for inc in incidents:
        layer = inc.get("layer")
        kind = inc.get("kind")
        if layer == "l0" and kind == "infra_down":
            fp = f"l0:{inc.get('target')}:{inc.get('detail')}"
            if not _cooldown_ok(state, fp, 600):
                continue
            actions.append({
                "type": "infra_recover",
                "target": inc.get("target"),
                "detail": inc.get("detail"),
                "fp": fp,
            })
        elif layer == "l1" and kind == "stage_failed":
            jid = inc.get("job_id")
            fp = f"l1:{jid}:{inc.get('stage')}:{inc.get('detail')[:40]}"
            if not _cooldown_ok(state, fp, 1800):
                continue
            actions.append({
                "type": "heal_job",
                "job_id": jid,
                "level": "safe",
                "fp": fp,
                "detail": inc.get("detail"),
            })
        elif layer == "l2" and kind == "quality_scan":
            jid = inc.get("job_id")
            fp = f"l2qual:{jid}"
            # quality scan mỗi tick OK; heal/HOLD có cooldown riêng trong apply
            actions.append({
                "type": "quality_job",
                "job_id": jid,
                "fp": fp,
                "held": inc.get("held"),
            })
    return actions


def apply_actions(
    work_root: Path,
    actions: list[dict],
    state: dict,
    *,
    hooks: dict[str, Callable[..., Any]] | None = None,
) -> list[dict]:
    hooks = hooks or {}
    results: list[dict] = []
    work_root = Path(work_root)

    for act in actions:
        typ = act.get("type")
        try:
            if typ == "infra_recover":
                target = act.get("target")
                detail = str(act.get("detail") or "")
                note = f"infra {target} {detail}"
                if target == "llama_8083":
                    # Đợi load / thử switch REVIEW_PRESET nếu không phải đang loading ngắn
                    preset = _cfg("REVIEW_PRESET") or _cfg("TRANSLATE_PRESET") or ""
                    if "503" in detail or "Loading" in detail:
                        log_line(work_root, f"infra: {target} loading/503 — chờ (không spam switch)")
                    elif preset:
                        try:
                            import tools.preset_switcher as preset_switcher
                            ok = preset_switcher.switch_preset(preset, max_wait_sec=120)
                            note = f"switch {preset} ok={ok}"
                            log_line(work_root, note)
                            if ok:
                                _telegram(f"Brain L3: nạp lại llama {preset}", level="l3")
                        except Exception as e:  # noqa: BLE001
                            note = f"switch fail: {e}"
                            log_line(work_root, note)
                    _mark_fp(state, act["fp"], note)
                    results.append({"ok": True, "action": act, "note": note})
                else:
                    log_line(work_root, f"infra down: {target} {detail}")
                    _mark_fp(state, act["fp"], detail)
                    results.append({"ok": True, "action": act, "note": "logged"})

            elif typ == "heal_job":
                jid = str(act.get("job_id") or "")
                if not jid or (work_root / jid / ".stop").exists():
                    continue
                from agents.agent_heal import heal_job
                level = act.get("level") or "safe"
                r = heal_job(work_root, jid, apply=True, level=level, hooks=hooks)
                # escalate một lần nếu safe không đủ và không stopped
                if (
                    isinstance(r, dict)
                    and not r.get("healed")
                    and level == "safe"
                    and _cooldown_ok(state, f"l1agg:{jid}", 3600)
                ):
                    r2 = heal_job(
                        work_root, jid, apply=True, level="aggressive", hooks=hooks,
                    )
                    r = {"safe": r, "aggressive": r2}
                    _mark_fp(state, f"l1agg:{jid}", "aggressive")
                    _telegram(f"Brain L3: heal aggressive {jid}", level="l3")
                _mark_fp(state, act["fp"], "heal")
                results.append({"ok": True, "action": act, "result": r})

            elif typ == "quality_job":
                jid = str(act.get("job_id") or "")
                if not jid or (work_root / jid / ".stop").exists():
                    continue
                wd = work_root / jid
                phase = _qa_pipeline_phase(wd)
                # 1) Perceive — đang mid_review / post_tts → không đụng, không HOLD
                if phase["phase"] == "mid_review":
                    log_line(
                        work_root,
                        f"qual {jid} skip — đang {phase.get('busy')} (phase=mid_review)",
                    )
                    results.append({"ok": True, "action": act, "skipped": "mid_review", "phase": phase})
                    continue
                if phase["phase"] == "post_tts":
                    log_line(
                        work_root,
                        f"qual {jid} skip — TTS/mux đã chạy (phase=post_tts)",
                    )
                    results.append({"ok": True, "action": act, "skipped": "post_tts", "phase": phase})
                    continue

                # 2) Act — sửa/ack khi được đụng script
                from agents.agent_quality import scan_and_heal_job
                r = scan_and_heal_job(wd, write=bool(phase.get("can_touch_script", True)))
                high = int(r.get("high_open") or 0)
                healed = int(r.get("healed") or 0)
                hang = r.get("hang_fix") or {}
                n_fixed = int(hang.get("n_fixed") or hang.get("n_fixed_cues") or 0)
                n_cases = int(hang.get("n_cases") or 0)
                skipped_hang = bool(hang.get("skipped"))
                note = (
                    f"qual {jid} phase={phase['phase']} healed={healed} "
                    f"hang_cases={n_cases} fixed={n_fixed} high={high}"
                    + (f" hang_skip={hang.get('reason')}" if skipped_hang else "")
                )
                log_line(work_root, note)
                results.append({"ok": bool(r.get("ok")), "action": act, "result": r, "phase": phase})

                # Báo kết quả xử lý (không chỉ HOLD)
                if healed or n_fixed or n_cases:
                    _telegram(
                        f"Brain ACT {jid}: healed={healed} hang_fix={n_fixed}/{n_cases} "
                        f"high_left={high} phase={phase['phase']}",
                        level="info",
                    )

                set_hold = hooks.get("set_hold") or hooks.get("set_hold_after_translate")

                # 3) Rule path: chỉ CLEAR khi sạch. HOLD/phương án lỗi → LLM agent quyết.
                if high == 0:
                    try:
                        from core.manifest import Manifest
                        m = Manifest(wd)
                        agent = dict(m.data.get("agent") or {})
                        was_held = bool(
                            agent.get("held_at") == "qa_brain" or agent.get("qa_blocked")
                        )
                        if was_held or act.get("held"):
                            agent["qa_blocked"] = False
                            agent.pop("held_at", None)
                            agent.pop("hold_reason", None)
                            agent["hold_after_translate"] = False
                            m.data["agent"] = agent
                            m.save()
                            if set_hold:
                                set_hold(jid, False)
                            log_line(work_root, f"CLEAR HOLD {jid} (qa clean → pipeline)")
                            _telegram(
                                f"Brain CLEAR {jid}: high=0 sau ACT — mở TTS/mux",
                                level="info",
                            )
                    except Exception as e:  # noqa: BLE001
                        log_line(work_root, f"clear hold fail: {e}")
                elif high > 0:
                    # Ghi phiếu cho LLM — không tự HOLD (mọi quyết định HOLD phải qua agent)
                    try:
                        pend = _log_dir(work_root) / "brain_pending_decisions.json"
                        items = []
                        if pend.is_file():
                            try:
                                items = json.loads(pend.read_text(encoding="utf-8")) or []
                            except Exception:  # noqa: BLE001
                                items = []
                        if not isinstance(items, list):
                            items = []
                        items = [x for x in items if not (
                            isinstance(x, dict) and x.get("job_id") == jid
                        )]
                        items.append({
                            "at": time.time(),
                            "job_id": jid,
                            "phase": phase.get("phase"),
                            "high": high,
                            "healed": healed,
                            "hang_fixed": n_fixed,
                            "need": "llm_decide",
                            "hint": (
                                "pre_tts+high → cân nhắc HOLD sau pineline_job"
                                if phase.get("phase") == "pre_tts"
                                else f"phase={phase.get('phase')} high={high} — đừng HOLD nếu mid_review"
                            ),
                        })
                        pend.write_text(
                            json.dumps(items[-30:], ensure_ascii=False, indent=2),
                            encoding="utf-8",
                        )
                    except Exception as e:  # noqa: BLE001
                        log_line(work_root, f"pending decision write: {e}")
                    log_line(
                        work_root,
                        f"qual {jid} high={high} phase={phase['phase']} — chờ LLM agent quyết "
                        f"(không auto-HOLD)",
                    )
                    if _cooldown_ok(state, f"needllm:{jid}:{high}", 600):
                        _mark_fp(state, f"needllm:{jid}:{high}", "pending")
                        _telegram(
                            f"Brain NEED-LLM {jid}: high={high} phase={phase['phase']} "
                            f"healed={healed} — agent phải đọc job rồi chọn plan",
                            level="info",
                        )
            else:
                results.append({"ok": False, "action": act, "error": "unknown type"})
        except Exception as e:  # noqa: BLE001
            log_line(work_root, f"action lỗi {typ}: {e}")
            results.append({"ok": False, "action": act, "error": str(e)})
    return results


def _llm_enabled() -> bool:
    mode = (_cfg("AGENT_BRAIN_MODE", "hybrid") or "hybrid").lower()
    if mode in ("llm", "hybrid", "agent"):
        return True
    if mode in ("rules", "rule", "off"):
        return False
    return _truthy(_cfg("AGENT_BRAIN_LLM", "1"))


def _llm_interval_sec() -> int:
    try:
        return max(60, int(_cfg("AGENT_BRAIN_LLM_SEC", "180") or "180"))
    except ValueError:
        return 180


def _http_json(method: str, url: str, body: dict | None = None, timeout: float = 60) -> Any:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"} if body is not None else {},
        method=method,
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def _ensure_brain_runtime(work_root: Path) -> str:
    """Bind agent_core Runtime nếu chưa có — FS + HTTP proxy (không cần restart :8801)."""
    import agents.agent_core as agent_core

    if getattr(agent_core, "_rt", None) is not None:
        return "already_bound"

    work_root = Path(work_root)

    def list_jobs() -> list[dict]:
        jobs: list[dict] = []
        if not work_root.is_dir():
            return jobs
        for d in work_root.iterdir():
            if not d.is_dir():
                continue
            mf = d / "manifest.json"
            if not mf.is_file():
                continue
            try:
                data = json.loads(mf.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                continue
            req = data.get("request") or {}
            jobs.append({
                "job_id": d.name,
                "title": data.get("title") or req.get("title") or d.name,
                "status": data.get("status") or "unknown",
                "overall": data.get("overall") or 0,
                "stages": data.get("stages") or {},
                "group_id": data.get("group_id"),
                "group_title": data.get("group_title"),
                "group_index": data.get("group_index"),
                "agent": data.get("agent") or {},
            })
        jobs.sort(key=lambda j: str(j.get("job_id")))
        return jobs

    def get_job(job_id: str) -> dict:
        mf = work_root / job_id / "manifest.json"
        if not mf.is_file():
            raise FileNotFoundError(f"job {job_id} không tồn tại")
        data = json.loads(mf.read_text(encoding="utf-8"))
        req = data.get("request") or {}
        return {
            "job_id": job_id,
            "title": data.get("title") or req.get("title") or job_id,
            "status": data.get("status") or "unknown",
            "overall": data.get("overall") or 0,
            "stages": data.get("stages") or {},
            "group_id": data.get("group_id"),
            "group_title": data.get("group_title"),
            "group_index": data.get("group_index"),
            "agent": data.get("agent") or {},
            "request": req,
        }

    def queue_state() -> dict:
        try:
            return _http_json("GET", _self_base() + "/api/queue/jobs", timeout=8)
        except Exception as e:  # noqa: BLE001
            return {"error": str(e), "queue": [], "current": None}

    def queue_add(job_ids: list[str], opts: dict) -> dict:
        body = {"job_ids": job_ids, **(opts or {})}
        try:
            return _http_json("POST", _self_base() + "/api/queue/jobs", body, timeout=30)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}

    def queue_stop() -> dict:
        try:
            return _http_json("POST", _self_base() + "/api/queue/jobs/stop", {}, timeout=15)
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}

    def get_hold(job_id: str) -> dict:
        mf = work_root / job_id / "manifest.json"
        if not mf.is_file():
            return {}
        try:
            return dict(json.loads(mf.read_text(encoding="utf-8")).get("agent") or {})
        except Exception:  # noqa: BLE001
            return {}

    def set_hold(job_id: str, enabled: bool) -> dict:
        mf = work_root / job_id / "manifest.json"
        if not mf.is_file():
            return {"ok": False, "error": "job không tồn tại"}
        data = json.loads(mf.read_text(encoding="utf-8"))
        agent = dict(data.get("agent") or {})
        agent["hold_after_translate"] = bool(enabled)
        if enabled:
            agent.pop("held_at", None)
            agent["hold_reason"] = "brain: dừng sau translate để duyệt"
        else:
            agent.pop("held_at", None)
            agent.pop("hold_reason", None)
        data["agent"] = agent
        mf.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "job_id": job_id, "hold_after_translate": bool(enabled)}

    def edit_line(job_id: str, i: int, vi: str | None, zh: str | None) -> dict:
        body = {"i": i}
        if vi is not None:
            body["vi"] = vi
        if zh is not None:
            body["zh"] = zh
        try:
            return _http_json(
                "POST",
                f"{_self_base()}/api/jobs/{job_id}/script-line",
                body,
                timeout=30,
            )
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}

    def run_stage(job_id: str, stage: str, opts: dict) -> dict:
        try:
            return _http_json(
                "POST",
                f"{_self_base()}/api/jobs/{job_id}/run/{stage}",
                opts or {},
                timeout=30,
            )
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}

    def stop_job(job_id: str) -> dict:
        try:
            return _http_json(
                "POST", f"{_self_base()}/api/jobs/{job_id}/stop", {}, timeout=20,
            )
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}

    def notify(text: str) -> None:
        try:
            from agents.agent_watch import telegram_send
            if not telegram_send(text, force=True):
                print(f"[agent_brain] {text}", flush=True)
        except Exception:  # noqa: BLE001
            print(f"[agent_brain] {text}", flush=True)

    def heal_stale(job_id: str) -> dict:
        try:
            return _http_json(
                "POST",
                f"{_self_base()}/api/agent/jobs/{job_id}/reset-state",
                {"stages": ["*"], "keep_asr": True, "restart": False},
                timeout=60,
            )
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "error": str(e)}

    agent_core.bind(agent_core.Runtime(
        work_root=work_root,
        list_jobs=list_jobs,
        get_job=get_job,
        queue_state=queue_state,
        queue_add=queue_add,
        queue_stop=queue_stop,
        list_voices=lambda: [],
        edit_script_line=edit_line,
        set_hold_after_translate=set_hold,
        get_hold=get_hold,
        run_stage=run_stage,
        stop_job=stop_job,
        notify=notify,
        heal_hooks={
            "heal_stale": heal_stale,
            "run_stage": lambda jid, st: run_stage(jid, st, {}),
            "stop_job": stop_job,
        },
    ))
    return "bound_fs_http"


def _run_agent_llm(
    message: str,
    *,
    work_root: Path,
    max_steps: int = 10,
    force_first_tool: str = "pineline_status",
    force_first_args: dict | None = None,
) -> dict:
    """Gọi agent_core tool-loop in-process (bind FS/HTTP nếu cần) hoặc fallback HTTP chat."""
    inproc_err = "skip"
    try:
        import agents.agent_core as agent_core
        via_bind = _ensure_brain_runtime(Path(work_root))
        kwargs: dict[str, Any] = {
            "history": None,
            "allow_mutate": True,
            "max_steps": max_steps,
            "require_confirm": False,
        }
        try:
            res = agent_core.run_agent(
                message,
                force_first_tool=force_first_tool or None,
                force_first_args=force_first_args,
                **kwargs,
            )
        except TypeError:
            try:
                res = agent_core.run_agent(
                    message,
                    force_first_tool=force_first_tool or None,
                    **kwargs,
                )
            except TypeError:
                res = agent_core.run_agent(message, **kwargs)
        return {
            "ok": True,
            "via": f"inprocess:{via_bind}",
            "reply": res.reply,
            "steps": res.steps,
            "model": res.model,
            "confirms": res.confirms,
        }
    except Exception as e:  # noqa: BLE001
        inproc_err = str(e)

    try:
        payload = json.dumps({
            "message": message,
            "allow_mutate": True,
            "require_confirm": False,
            "max_steps": max_steps,
            "history": [],
            "force_first_tool": force_first_tool or None,
        }).encode("utf-8")
        req = urllib.request.Request(
            _self_base() + "/api/agent/chat",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        data["via"] = "http"
        data.setdefault("ok", True)
        return data
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "error": f"llm_tick fail inproc={inproc_err}; http={e}",
        }


def llm_tick(work_root: Path) -> dict:
    """LLM Second Brain: đọc snapshot toàn hệ → tool-loop quyết định."""
    from agents.agent_brain_context import (
        BRAIN_LLM_INSTRUCTION,
        build_system_snapshot,
        snapshot_to_prompt,
    )

    work_root = Path(work_root)
    snap = build_system_snapshot(work_root, max_jobs=30)
    # ghi snapshot để audit
    try:
        sp = _log_dir(work_root) / "agent_brain_last_snapshot.json"
        sp.write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    # Snapshot ngắn: ưu tiên — LLM phải tool-verify rồi mới HOLD/heal
    msg = BRAIN_LLM_INSTRUCTION + snapshot_to_prompt(snap, max_chars=4500)
    focus: list[str] = []
    focus_meta: dict[str, dict] = {}
    for j in snap.get("jobs_focus") or []:
        if not isinstance(j, dict) or j.get("stop"):
            continue
        jid = str(j.get("job_id") or "")
        if not jid:
            continue
        ag = j.get("agent") or {}
        qb = j.get("qa_brain") or {}
        st = j.get("stages") or {}
        phase = (j.get("phase") or {}).get("name") or ""
        failed = any(
            str((st.get(s) or {}).get("status") or "") == "failed"
            for s in st
        )
        running = any(
            str((st.get(s) or {}).get("status") or "") == "running"
            for s in st
        )
        if (
            ag.get("qa_blocked")
            or ag.get("hold")
            or qb.get("high_open")
            or failed
            or running
            or phase == "pre_tts"
        ):
            focus.append(jid)
            focus_meta[jid] = {
                "phase": phase,
                "high": qb.get("high_open"),
                "failed": failed,
                "running": running,
            }
    # phiếu rule path để lại
    try:
        pend = _log_dir(work_root) / "brain_pending_decisions.json"
        if pend.is_file():
            for it in json.loads(pend.read_text(encoding="utf-8")) or []:
                if isinstance(it, dict) and it.get("job_id"):
                    jid = str(it["job_id"])
                    if jid not in focus:
                        focus.append(jid)
                    focus_meta.setdefault(jid, {})["pending"] = it
    except Exception:  # noqa: BLE001
        pass
    if focus:
        lines = []
        for jid in focus[:8]:
            meta = focus_meta.get(jid) or {}
            lines.append(
                f"- {jid}: phase={meta.get('phase')} high={meta.get('high')} "
                f"failed={meta.get('failed')} running={meta.get('running')}"
            )
        msg += (
            "\n\nJOB CẦN QUYẾT ĐỊNH (bắt buộc pineline_job từng cái → DECISION):\n"
            + "\n".join(lines)
        )
    log_line(work_root, "LLM tick start (agent_core tool-loop)")
    max_steps = int(_cfg("AGENT_BRAIN_LLM_STEPS", "12") or "12")
    out = _run_agent_llm(
        msg,
        work_root=work_root,
        max_steps=max_steps,
        force_first_tool="pineline_status",
    )
    # Ép deep tick: mỗi job ưu tiên phải được agent đọc + quyết
    steps0 = list(out.get("steps") or []) if out.get("ok") else []
    tools0 = [s.get("tool") for s in steps0 if isinstance(s, dict)]
    deep_jobs = list(focus[:3])
    for jid0 in deep_jobs:
        meta = focus_meta.get(str(jid0)) or {}
        already = any(
            isinstance(s, dict)
            and s.get("tool") in ("pineline_job", "pineline_diagnose_job", "diagnose_job")
            and str((s.get("args") or {}).get("job_id") or "") == str(jid0)
            for s in steps0
        )
        if already and len(tools0) > 2 and jid0 == focus[0]:
            # đã đụng job đầu trong tick chính — vẫn deep nếu failed/high
            if not (meta.get("failed") or meta.get("high") or meta.get("pending")):
                continue
        follow = (
            f"SECOND BRAIN — quyết định THẬT cho job {jid0}. allow_mutate=ON.\n"
            f"Meta gợi ý (phải xác minh bằng tool): {json.dumps(meta, ensure_ascii=False)}\n"
            f"1) Gọi pineline_job job_id={jid0}.\n"
            f"2) Nếu failed/treo: pineline_diagnose_job rồi heal_job apply=true level=safe.\n"
            f"3) Trả lời đủ: đang làm gì / ổn? / lỗi đâu / plan / tool đã gọi.\n"
            f"4) Chỉ hold_after_translate enabled=true nếu phase=pre_tts và còn high "
            f"SAU khi đã đọc job. mid_review → CẤM HOLD.\n"
            f"5) Nếu high=0 mà đang HOLD qa_brain → hold enabled=false (CLEAR).\n"
            f"Kết thúc 1 khối: DECISION {jid0}: stage=… | ok=… | issue=… | plan=… | tools=…"
        )
        log_line(work_root, f"LLM deep tick job={jid0} phase={meta.get('phase')}")
        out2 = _run_agent_llm(
            follow,
            work_root=work_root,
            max_steps=max(8, max_steps // 2),
            force_first_tool="pineline_job",
            force_first_args={"job_id": str(jid0)},
        )
        if out2.get("ok"):
            steps0 = steps0 + list(out2.get("steps") or [])
            out = {
                **out2,
                "steps": steps0,
                "via": f"{out.get('via')}+deep:{jid0}",
                "reply": ((out.get("reply") or "") + "\n" + (out2.get("reply") or "")).strip(),
            }
            tools0 = [s.get("tool") for s in steps0 if isinstance(s, dict)]
            reply2 = (out2.get("reply") or "").strip()
            if reply2:
                _telegram(
                    f"Brain DECISION {jid0}: {reply2[:400].replace(chr(10), ' | ')}",
                    level="info",
                )
            # xóa pending đã xử lý
            try:
                pend = _log_dir(work_root) / "brain_pending_decisions.json"
                if pend.is_file():
                    items = [
                        x for x in (json.loads(pend.read_text(encoding="utf-8")) or [])
                        if not (isinstance(x, dict) and x.get("job_id") == jid0)
                    ]
                    pend.write_text(
                        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
            except Exception:  # noqa: BLE001
                pass
        else:
            log_line(work_root, f"LLM deep tick fail {jid0}: {out2.get('error')}")

    if out.get("ok"):
        steps = out.get("steps") or []
        tools = [s.get("tool") for s in steps if isinstance(s, dict)]
        log_line(
            work_root,
            f"LLM tick ok via={out.get('via')} model={out.get('model')} "
            f"tools={tools[:12]}",
        )
        reply = (out.get("reply") or "")[:500]
        if reply:
            log_line(work_root, f"LLM reply: {reply.replace(chr(10), ' | ')}")
        mutate = [
            s for s in steps
            if isinstance(s, dict)
            and s.get("tool")
            and s["tool"] not in (
                "pineline_status", "pineline_job", "queue_status", "running_check",
                "config_get", "films", "library", "diagnose_job", "scan_failed",
                "review_diff", "stage_peek", "stage_peek_all", "style_pack_peek",
                "script_get", "av_sync_check", "av_sync_scan", "hg_status",
                "hg_library", "feed", "pineline_diagnose_job", "pineline_running_check",
                "pineline_queue_status", "pineline_config_get",
            )
        ]
        if mutate:
            _telegram(
                "Brain LLM: " + ", ".join(
                    f"{s.get('tool')}" for s in mutate[:6]
                ),
                level="l3",
            )
    else:
        log_line(work_root, f"LLM tick fail: {out.get('error')}")
    return out



def _tg_report_sec() -> int:
    try:
        return max(60, int(_cfg("AGENT_BRAIN_TG_SEC", "120") or "120"))
    except ValueError:
        return 120


def _progress_digest(work_root: Path) -> str:
    """Tóm tắt ngắn running/queue cho Telegram."""
    lines: list[str] = []
    running: list[str] = []
    failed: list[str] = []
    held: list[str] = []
    try:
        import urllib.request
        with urllib.request.urlopen(_self_base() + "/api/jobs", timeout=8) as resp:
            jobs = json.loads(resp.read().decode("utf-8", "replace"))
        if not isinstance(jobs, list):
            jobs = []
    except Exception as e:  # noqa: BLE001
        return f"Brain: không đọc được /api/jobs ({e})"

    for j in jobs:
        if not isinstance(j, dict):
            continue
        jid = str(j.get("job_id") or "")[:12]
        title = (j.get("title") or "")[:28]
        stages = j.get("stages") or {}
        run_st = [
            k for k, st in stages.items()
            if isinstance(st, dict) and st.get("status") == "running"
        ]
        fail_st = [
            k for k, st in stages.items()
            if isinstance(st, dict) and st.get("status") == "failed"
        ]
        agent = j.get("agent") or {}
        if run_st:
            cur = ""
            st0 = stages.get(run_st[0]) or {}
            if isinstance(st0, dict):
                cur = (st0.get("cur_text") or "")[:40]
                pct = st0.get("progress")
                if pct is not None:
                    cur = f"{pct}% {cur}".strip()
            running.append(f"• {jid} [{'/'.join(run_st)}] {title} {cur}".strip())
        if fail_st:
            failed.append(f"• {jid} fail:{'/'.join(fail_st[:3])} {title}".strip())
        if agent.get("hold_after_translate") or agent.get("qa_blocked"):
            held.append(f"• {jid} HOLD {title}".strip())

    qnote = ""
    try:
        import urllib.request
        with urllib.request.urlopen(_self_base() + "/api/queue/jobs", timeout=5) as resp:
            q = json.loads(resp.read().decode("utf-8", "replace"))
        if isinstance(q, dict):
            n = len(q.get("jobs") or q.get("queue") or [])
            qnote = f"queue≈{n}"
        elif isinstance(q, list):
            qnote = f"queue≈{len(q)}"
    except Exception:  # noqa: BLE001
        pass

    lines.append("🧠 Brain báo cáo")
    if qnote:
        lines.append(qnote)
    if running:
        lines.append("RUNNING:")
        lines.extend(running[:8])
    else:
        lines.append("RUNNING: (không)")
    if failed:
        lines.append("FAILED:")
        lines.extend(failed[:5])
    if held:
        lines.append("HOLD:")
        lines.extend(held[:5])
    return "\n".join(lines)


def _maybe_tg_progress(work_root: Path, state: dict) -> None:
    mode = _tg_mode()
    if mode not in ("all", "report", "digest", "progress", "on"):
        return
    last = float(state.get("last_tg_report") or 0)
    if time.time() - last < _tg_report_sec():
        return
    msg = _progress_digest(work_root)
    _telegram(msg, level="info")
    state["last_tg_report"] = time.time()
    log_line(work_root, "tg progress report sent")


def tick(
    work_root: Path,
    *,
    hooks: dict[str, Callable[..., Any]] | None = None,
    list_jobs: Callable[[], list] | None = None,  # noqa: ARG001 — reserved
) -> dict:
    work_root = Path(work_root)
    state = _load_state(work_root)
    incidents: list[dict] = []
    incidents.extend(sense_infra())
    # Nhường GPU khi queue bận — vẫn chạy quality nhẹ? Plan: giống watch skip heal nặng
    busy = _gpu_or_queue_busy(work_root)
    mode = (_cfg("AGENT_BRAIN_MODE", "hybrid") or "hybrid").lower()
    run_rules = mode in ("hybrid", "rules", "rule", "agent", "llm")
    # llm-only: vẫn giữ quality scan nhẹ làm safety net
    if busy:
        # Vẫn quality_scan jobs gần đây (deterministic, không LLM)
        incidents.extend(sense_jobs(work_root, max_jobs=15))
        # Lọc bỏ heal_job khi busy
        actions = [a for a in decide(incidents, state) if a.get("type") != "heal_job"]
        log_line(work_root, f"tick busy — skip L1 heal; actions={len(actions)}")
    else:
        # L1 từ agent_heal.scan nếu có
        try:
            from agents.agent_heal import scan_problem_jobs
            scan = scan_problem_jobs(work_root, list_jobs=list_jobs)
            for p in (scan.get("problems") or [])[:10]:
                incidents.append({
                    "layer": "l1",
                    "kind": "stage_failed",
                    "job_id": p.get("job_id"),
                    "stage": ",".join(p.get("failed_stages") or []) or "unknown",
                    "detail": ",".join(p.get("issue_codes") or [])[:120],
                })
        except Exception as e:  # noqa: BLE001
            log_line(work_root, f"scan_problem_jobs: {e}")
        incidents.extend(sense_jobs(work_root, max_jobs=40))
        actions = decide(incidents, state)

    results = []
    if run_rules:
        results = apply_actions(work_root, actions, state, hooks=hooks)

    llm_out = None
    if _llm_enabled():
        last = float(state.get("last_llm_tick") or 0)
        if time.time() - last >= _llm_interval_sec():
            try:
                llm_out = llm_tick(work_root)
                state["last_llm_tick"] = time.time()
            except Exception as e:  # noqa: BLE001
                log_line(work_root, f"llm_tick exception: {e}")
                llm_out = {"ok": False, "error": str(e)}

    try:
        _maybe_tg_progress(work_root, state)
    except Exception as e:  # noqa: BLE001
        log_line(work_root, f"tg progress skip: {e}")
    state["last_tick"] = time.time()
    state["last_n_incidents"] = len(incidents)
    state["last_n_actions"] = len(actions)
    state["mode"] = mode
    _save_state(work_root, state)
    return {
        "ok": True,
        "mode": mode,
        "n_incidents": len(incidents),
        "n_actions": len(actions),
        "n_results": len(results),
        "busy": busy,
        "results": results,
        "llm": llm_out,
    }


def _loop(work_root: Path, hooks, list_jobs, interval: int) -> None:
    log_line(work_root, f"brain start interval={interval}s policy=full_silent tg={_tg_mode()}")
    while not _stop.is_set():
        pause = Path(work_root) / "logs" / "brain_pause"
        if pause.exists() or not brain_enabled():
            log_line(work_root, "brain paused (brain_pause hoặc AGENT_BRAIN=0) — skip tick")
            _stop.wait(interval)
            continue
        try:
            tick(work_root, hooks=hooks, list_jobs=list_jobs)
        except Exception as e:  # noqa: BLE001
            log_line(work_root, f"tick lỗi: {e}")
        _stop.wait(interval)
    log_line(work_root, "brain stop")


def start_brain(
    work_root: Path,
    *,
    hooks: dict[str, Callable[..., Any]] | None = None,
    list_jobs: Callable[[], list] | None = None,
) -> bool:
    global _thread
    if not brain_enabled():
        return False
    interval = _interval_sec()
    with _lock:
        if _thread and _thread.is_alive():
            return True
        _stop.clear()
        _thread = threading.Thread(
            target=_loop,
            args=(Path(work_root), hooks or {}, list_jobs, interval),
            name="agent_brain",
            daemon=True,
        )
        _thread.start()
    return True


def stop_brain() -> None:
    _stop.set()


def brain_once(
    work_root: Path,
    *,
    hooks: dict[str, Callable[..., Any]] | None = None,
    list_jobs: Callable[[], list] | None = None,
) -> dict:
    """API/ops: chạy 1 tick thủ công."""
    return tick(Path(work_root), hooks=hooks, list_jobs=list_jobs)
