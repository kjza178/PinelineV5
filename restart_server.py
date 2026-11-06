"""Restart server Pineline (giữ sidecar), khôi phục hàng đợi + Auto-pilot.

Port mặc định V5: 8805 (env PORT / PINELINE_BASE). Legacy 8804/8801 nếu đặt env.

--after-current: rút job chờ, đợi job đang chạy xong rồi mới restart (không ngắt job nào).
--hold-file F:    sau khi job xong, chờ tới khi file F biến mất (code đang sửa dở). Chờ quá
                  --hold-max-h giờ → xếp lại job chờ trên server cũ, KHÔNG restart.
--clean-env:      start server bằng python server.py với env chụp từ process cũ
                  (giữ AGENT_WATCH/AGENT_QA_GATE…). Legacy start_8801.py chỉ khi PORT=8801.
--sidecar:        restart cả sidecar :8802 (run_tele_cmd.bat, env chụp từ sidecar cũ).
Trước khi kill luôn py_compile + import thử; lỗi → không restart, xếp lại job chờ."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import tools.migrate_work as mw  # noqa: E402
from agents.agent_autopilot import load_state, set_enabled  # noqa: E402

PORT = (os.getenv("PORT") or "8805").strip()
SERVER_CMDLINE = f"server.py --host 127.0.0.1 --port {PORT}"
START_LEGACY = Path(r"D:\PinelineV2_tmp\start_8801.py")
SIDECAR = "http://127.0.0.1:8802"
CHECK_MODULES = (
    "server.py",
    "core/job_queue.py", "core/config.py", "core/manifest.py",
    "core/batch_config.py", "core/fileio.py", "core/job_meta.py", "core/film_db.py",
    "tools/preset_switcher.py",
    "http_routes/routes_ui.py", "http_routes/routes_hg.py", "http_routes/routes_agent.py",
    "http_routes/routes_films.py", "http_routes/routes_uploader_settings.py",
    "engines/llm.py", "engines/translate.py", "engines/translate_alts.py",
    "engines/render.py", "engines/sfx_lib.py", "engines/assemble.py", "engines/media_ts.py",
    "engines/clone_tts.py", "engines/separate.py", "engines/split_parts.py",
    "engines/asr/asr.py", "engines/asr/fun_asr_nano.py", "engines/asr/nano_fa_asr.py",
    "engines/asr/hybrid_asr.py", "engines/asr/firered_asr.py", "engines/asr/sensevoice_asr.py",
    "engines/asr/paraformer_zh.py",
    "agents/hongguo_bridge.py", "agents/agent_core.py", "agents/agent_hongguo.py",
    "agents/agent_feeder.py", "agents/agent_tele_cmd.py", "agents/agent_autopilot.py",
)
# Giả "pytest" để import server không nạp hàng đợi thật / khởi worker song song server đang chạy.
SMOKE = (
    "import sys, types; sys.modules.setdefault('pytest', types.ModuleType('pytest')); "
    "import server; import agents.agent_tele_cmd as agent_tele_cmd; "
    "import engines.translate as translate; import engines.translate_alts as translate_alts; "
    "print('import ok')"
)


def _manifest_opts(job_id: str) -> dict:
    try:
        m = json.loads((ROOT / "work" / job_id / "manifest.json").read_text(encoding="utf-8"))
        return {k: v for k, v in (m.get("queue_opts") or {}).items() if k != "pin_opts"}
    except Exception:  # noqa: BLE001
        return {}


def _tg(msg: str) -> None:
    try:
        os.environ.setdefault("AGENT_TELEGRAM", "1")
        from agents.agent_watch import telegram_send
        telegram_send("Restart: " + msg, force=True)
    except Exception as e:  # noqa: BLE001
        mw.log(f"telegram lỗi: {e}")


def _proc_env(pattern: str) -> dict | None:
    for p in mw.procs(pattern):
        try:
            return dict(p.environ())
        except Exception:  # noqa: BLE001
            continue
    return None


def _precheck() -> str:
    """'' nếu code mới compile + import được; ngược lại là lỗi (không restart)."""
    r = subprocess.run([sys.executable, "-m", "py_compile", *CHECK_MODULES], cwd=str(ROOT),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        return "py_compile: " + (r.stderr or r.stdout)[-400:]
    r = subprocess.run([sys.executable, "-c", SMOKE], cwd=str(ROOT), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=300)
    if r.returncode or "import ok" not in (r.stdout or ""):
        return "import: " + (r.stderr or r.stdout)[-400:]
    return ""


def _requeue(order: list[str], opts: dict) -> list[str]:
    q2 = mw.api_retry("GET", mw.BASE + "/api/queue/jobs")
    have = set(([q2["current"]] if q2.get("current") else []) + [str(x) for x in (q2.get("queue") or [])])
    missing = [j for j in order if j not in have]
    i = 0
    while i < len(missing):
        o = opts[missing[i]]
        ids = [missing[i]]
        while i + len(ids) < len(missing) and opts[missing[i + len(ids)]] == o:
            ids.append(missing[i + len(ids)])
        mw.api_retry("POST", mw.BASE + "/api/queue/jobs", {"job_ids": ids, "skip_done": True, **o}, timeout=60)
        i += len(ids)
    return missing


def _start_server(clean_env: bool, env: dict | None) -> None:
    e = dict(env or os.environ)
    e.setdefault("PORT", PORT)
    e.pop("PYTHONPATH", None)
    if clean_env:
        # Prefer in-tree server (V4); legacy start_8801 only if still present
        if START_LEGACY.is_file() and PORT == "8801":
            subprocess.Popen([sys.executable, str(START_LEGACY)], cwd=str(ROOT), env=e,
                             creationflags=subprocess.CREATE_NEW_CONSOLE)
            return
        subprocess.Popen(
            [sys.executable, "server.py", "--host", "127.0.0.1", "--port", PORT],
            cwd=str(ROOT), env=e, creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        return
    bat = ROOT / "run_v5.bat"
    if not bat.is_file():
        raise SystemExit(f"Thiếu {bat} — không fallback run_v4/run_v2 (đã archive).")
    mw.start_bat(bat.name)


def _restart_sidecar(env: dict | None) -> bool:
    for p in mw.procs("agent_tele_cmd.py"):
        mw.kill_with_parent_cmd(p)
    time.sleep(3)
    subprocess.Popen(["cmd.exe", "/c", "start", "/min", "", str(ROOT / "run_tele_cmd.bat")], cwd=str(ROOT),
                     env=env or None, creationflags=subprocess.CREATE_NEW_CONSOLE)
    return mw.wait_http(SIDECAR + "/status", 90)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--after-current", action="store_true")
    ap.add_argument("--hold-file", default="")
    ap.add_argument("--hold-max-h", type=float, default=3.0)
    ap.add_argument("--clean-env", action="store_true")
    ap.add_argument("--sidecar", action="store_true")
    ap.add_argument("--ignore-hg", action="store_true",
                    help="restart dù hàng đợi gộp Hongguo đang chạy (series đang gộp sẽ làm lại từ đầu)")
    a = ap.parse_args()

    ap_was = bool(load_state().get("enabled"))
    set_enabled(False)
    q = mw.api_retry("GET", mw.BASE + "/api/queue/jobs")
    cur = q.get("current")
    pending = [str(x) for x in (q.get("queue") or [])]
    order = pending if a.after_current else ([cur] if cur else []) + pending
    snaps = q.get("opts_by_job") or {}
    opts = {j: snaps.get(j) or {**(q.get("opts") or {}), **_manifest_opts(j)} for j in order}
    mw.log(f"restart server · current={cur} · queue={order} · Auto-pilot={ap_was} · args={vars(a)}")
    (ROOT / "work" / "logs").mkdir(parents=True, exist_ok=True)
    (ROOT / "work" / "logs" / "restart_pending.json").write_text(
        json.dumps({"order": order, "opts": opts, "ap_was": ap_was, "at": time.time()}, ensure_ascii=False, indent=2),
        encoding="utf-8")

    def _abort(why: str) -> None:
        got = _requeue(order, opts)
        if ap_was:
            set_enabled(True)
        mw.log(f"KHÔNG restart: {why} · xếp lại {got}")
        _tg(f"không restart ({why[:200]}); đã xếp lại {len(got)} job trên server cũ")
        raise SystemExit(1)

    if not a.ignore_hg:
        try:
            mq = mw.api("GET", mw.BASE + "/api/hg/merge-queue")
        except Exception:  # noqa: BLE001
            mq = {}
        if mq.get("current") or (mq.get("worker") and mq.get("queue")):
            _abort(f"đang gộp Hongguo «{mq.get('current') or '?'}», còn {len(mq.get('queue') or [])} series chờ "
                   "(chờ xong hoặc chạy lại với --ignore-hg)")

    if a.after_current:
        if pending:
            mw.api_retry("POST", mw.BASE + "/api/queue/jobs/remove", {"job_ids": pending})
        _tg(f"hẹn: tạm rút {len(pending)} job chờ, đợi job {cur or '-'} xong rồi restart server")
        while True:
            q = mw.api_retry("GET", mw.BASE + "/api/queue/jobs", tries=40)
            if not q.get("current") and not q.get("worker") and not mw.running_stages() and not (q.get("queue") or []):
                break
            time.sleep(20)
        mw.log(f"job {cur} xong")

    if a.hold_file:
        hold = Path(a.hold_file)
        t0 = time.time()
        if hold.exists():
            _tg("job xong nhưng code còn đang sửa — chờ gỡ cờ hold")
        while hold.exists():
            if time.time() - t0 > a.hold_max_h * 3600:
                _abort(f"cờ {hold.name} còn sau {a.hold_max_h} giờ")
            time.sleep(30)

    err = _precheck()
    if err:
        _abort(err)
    mw.log("precheck ok")

    srv_env = _proc_env(SERVER_CMDLINE) if a.clean_env else None
    side_env = _proc_env("agent_tele_cmd.py") if a.sidecar else None
    for k in ("AGENT_BASE_URL", "AGENT_API_KEY"):   # key giờ chỉ lấy từ pineline.config.json
        (side_env or {}).pop(k, None)
    for p in mw.procs(SERVER_CMDLINE):
        mw.log(f"kill server PID {p.pid}")
        mw.kill_with_parent_cmd(p)
    time.sleep(4)
    _start_server(a.clean_env, srv_env)
    mw.log("đã gọi start server, chờ /api/agent/status")
    if not mw.wait_http(mw.BASE + "/api/agent/status", 180):
        mw.log("server không lên sau 3 phút")
        _tg(f"server không lên sau 3 phút — port {PORT}")
        raise SystemExit("server không lên")
    mw.log("server lên")
    side_ok = _restart_sidecar(side_env) if a.sidecar else None

    time.sleep(5)
    missing = _requeue(order, opts)
    if ap_was:
        set_enabled(True)
    q3 = mw.api("GET", mw.BASE + "/api/queue/jobs")
    mw.log(f"restart xong · current={q3.get('current')} · queue={q3.get('queue')} · xếp bù {len(missing)} · sidecar={side_ok}")
    if a.after_current or a.hold_file:
        _tg(f"xong, đã xếp lại {len(missing)} job, sidecar "
            f"{'-' if side_ok is None else ('lên' if side_ok else 'KHÔNG lên')}, Auto-pilot {'bật' if ap_was else 'tắt'}")
    print(json.dumps({"current": q3.get("current"), "queue": q3.get("queue"), "worker": q3.get("worker"),
                      "requeued": missing}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # noqa: BLE001
        import traceback
        mw.log("restart lỗi: " + traceback.format_exc()[-1500:])
        _tg(f"restart lỗi giữa chừng ({e!r:.200}) — job chờ lưu ở work/logs/restart_pending.json")
        raise
