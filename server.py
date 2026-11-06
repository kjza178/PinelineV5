"""
server.py — Backend web Phase 1 (FastAPI).

Bọc engine (download -> asr -> translate) thành app web:
  - Phục vụ trang dashboard (index3.html)
  - Tạo job, chạy pipeline ở THREAD NỀN, đọc trạng thái từ manifest.json

Chạy:
    pip install -U fastapi "uvicorn[standard]"
    export LLM_API_KEY=...          # cần cho stage dịch
    python server.py
    # mở http://127.0.0.1:8000

LƯU Ý: đây là bản MVP — mỗi job chạy trong 1 thread daemon. Ổn để test 1-2
video. Lên nhiều job song song / nhiều máy GPU thì thay thread bằng Celery
+ Redis ở Phase 2 (engine giữ nguyên, chỉ đổi chỗ gọi).
"""
from __future__ import annotations

import os
# FS không hỗ trợ symlink (ổ exFAT/FAT32 / chưa bật Developer Mode) -> HF copy thay symlink,
# tránh 'OSError WinError 1' khi tải model. Đặt cho CẢ tiến trình con (asr/tts/vieneu... kế thừa env).
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# Nạp config -> env TRƯỚC khi import llm/translate (chúng đọc env lúc import; tiến trình con kế thừa).
import core.config as _config_boot  # noqa: E402
_config_boot.inject_env()
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import hashlib
import json
import shutil
import subprocess
import sys
sys.modules.setdefault("server", sys.modules[__name__])  # chạy `python server.py`: routes_* import cùng module
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import FastAPI, File, Form, Query, UploadFile
from fastapi.responses import (
    FileResponse, JSONResponse, PlainTextResponse, Response,
)
from pydantic import BaseModel

from core.manifest import Manifest
from engines.download import download_video, job_id_from_url
from engines.asr.asr import run_asr
from engines.vram import free_gpu_vram
from engines.translate import run_translate, run_review, count_script_missing
from engines.ocr import run_ocr
from engines.separate import run_separate
from engines.render import run_render
from engines.clone_tts import (
    run_clone_tts, list_clone_voices, synth_one, enroll_voice,
    resynth_clip as _clone_resynth,
)
from engines.playlist import expand, expand_meta
from engines.subs import to_srt

WORK_ROOT = Path("work")
_PROJ = Path(__file__).parent
WEB = _PROJ / "web"


# Đăng ký subprocess engine đang chạy theo job -> để "Dừng" kill được.
_PROCS: dict[str, "subprocess.Popen"] = {}
# Job đang bị yêu cầu DỪNG -> automation không chạy tiếp bước sau.
_STOP_JOBS: set[str] = set()
# Chặn double-click: (job_id, stage|"__all__") đang được xếp hàng / chạy.
_STAGE_BUSY: set[tuple[str, str]] = set()
_STAGE_BUSY_LOCK = threading.Lock()
# Chặn auto-split pass chồng trong cùng process (parent đã merged / đang chạy).
_AUTO_SPLIT_ACTIVE: set[str] = set()
_AUTO_SPLIT_LOCK = threading.Lock()


def _maybe_auto_split_guarded(job_id: str, **kwargs):
    """Wrap maybe_auto_split_job với lock chống gọi chồng cùng job_id."""
    with _AUTO_SPLIT_LOCK:
        if job_id in _AUTO_SPLIT_ACTIVE:
            print(
                f"[auto_split] {job_id}: đang chạy trong process này — skip chồng.",
                flush=True,
            )
            return {
                "ok": True,
                "split": False,
                "skipped": "auto_split_active",
                "job_ids": [job_id],
            }
        _AUTO_SPLIT_ACTIVE.add(job_id)
    try:
        from engines.split_parts import maybe_auto_split_job
        return maybe_auto_split_job(job_id, **kwargs)
    finally:
        with _AUTO_SPLIT_LOCK:
            _AUTO_SPLIT_ACTIVE.discard(job_id)


def _mux_output_ok(work_dir: Path, min_bytes: int = 1_000_000) -> bool:
    p = Path(work_dir) / "output.mp4"
    try:
        return p.is_file() and p.stat().st_size > min_bytes
    except OSError:
        return False


def _part_pipeline_complete(work_dir: Path) -> bool:
    """Part/job đã mux + output, không stale → không chạy lại GPU pipeline."""
    work_dir = Path(work_dir)
    if not _mux_output_ok(work_dir):
        return False
    try:
        m = Manifest(work_dir)
    except Exception:  # noqa: BLE001
        return False
    if not m.is_done("mux"):
        return False
    stages = m.data.get("stages") or {}
    tr = stages.get("translate") or {}
    tts = stages.get("tts") or {}
    if tr.get("stale") or tts.get("stale"):
        return False
    if tr.get("status") == "pending" and tr.get("stale_asr_source"):
        return False
    return True


def _ensure_parent_mux_merged_done(work_dir: Path, n_parts: int | None = None) -> None:
    """Heal UI parent: Full đã merge mà mux còn running@80%."""
    work_dir = Path(work_dir)
    try:
        m = Manifest(work_dir)
    except Exception:  # noqa: BLE001
        return
    si = m.data.get("split_info") or {}
    n = n_parts or len(si.get("sub_job_ids") or []) or 0
    st = m.data.setdefault("stages", {}).setdefault("mux", {})
    st["status"] = "done"
    st["progress"] = 100
    st["cur_text"] = (
        f"Hoàn tất bản Full ({n} parts ghép lại) ✓" if n else "Hoàn tất bản Full ✓"
    )
    st["from_split_merge"] = True
    st["is_full_merged"] = True
    st["updated_at"] = time.time()
    m.data["stages"]["mux"] = st
    if si.get("status") != "merged":
        si = dict(si)
        si["status"] = "merged"
        m.data["split_info"] = si
    m.save()
    try:
        _job_cache.pop(str(work_dir), None)
    except NameError:
        pass


def _job_any_busy(job_id: str) -> str | None:
    """Trả tên stage đang claim, hoặc None."""
    with _STAGE_BUSY_LOCK:
        for j, s in _STAGE_BUSY:
            if j == job_id:
                return s
    return None


def _claim_stage(job_id: str, stage: str) -> bool:
    """Giữ chỗ trước khi submit thread — chống bấm 2-3 lần tạo nhiều task."""
    with _STAGE_BUSY_LOCK:
        if any(j == job_id for j, _ in _STAGE_BUSY):
            return False
        _STAGE_BUSY.add((job_id, stage))
        return True


def _release_stage(job_id: str, stage: str) -> None:
    with _STAGE_BUSY_LOCK:
        _STAGE_BUSY.discard((job_id, stage))
        # dọn claim __all__ nếu stop
        _STAGE_BUSY.discard((job_id, "__all__"))


def _busy_response(job_id: str, work_dir: Path):
    """409 nếu job đang có claim hoặc stage 'running' trong manifest, ngược lại None."""
    busy = _job_any_busy(job_id) or _manifest_running(work_dir)
    if busy:
        return JSONResponse(
            {"error": f"job đang chạy bước '{busy}' — bấm Dừng hoặc đợi xong"},
            status_code=409,
        )
    return None


def _submit_claimed(executor, job_id: str, stage: str, fn, *args, **kwargs):
    """Claim (job, stage) rồi submit; nhả claim khi xong. Trả 409 nếu đã có claim."""
    if not _claim_stage(job_id, stage):
        return JSONResponse({"error": "đã nhận lệnh trước đó — không gửi trùng"}, status_code=409)

    def _wrapped():
        try:
            fn(*args, **kwargs)
        finally:
            _release_stage(job_id, stage)

    try:
        executor.submit(_wrapped)
    except Exception:
        _release_stage(job_id, stage)
        raise
    return None


def _manifest_running(work_dir: Path) -> str | None:
    """Stage đang 'running' trong manifest (nếu có)."""
    try:
        m = Manifest(work_dir)
        for s in RUNNABLE_STAGES:
            if (m.stage(s) or {}).get("status") == "running":
                return s
    except Exception:  # noqa: BLE001
        pass
    return None


def _job_proc_alive(job_id: str) -> bool:
    """True nếu còn subprocess engine/ffmpeg đăng ký cho job."""
    p = _PROCS.get(job_id)
    if p is not None and p.poll() is None:
        return True
    return False


def _path_key(p) -> str:
    """Khoá so đường dẫn: work là junction → D:, psutil.cwd() trả đường Z: chưa resolve."""
    s = str(p or "")
    if not s:
        return ""
    try:
        s = os.path.realpath(s)
    except OSError:
        pass
    return s.lower().replace("/", "\\").rstrip("\\")


def _json_rows(p: Path) -> list:
    try:
        rows = json.loads(p.read_text(encoding="utf-8"))
        return rows if isinstance(rows, list) else []
    except Exception:  # noqa: BLE001
        return []


def _stage_complete_on_disk(work_dir: Path, stage: str) -> bool:
    """Artifact ĐỦ (không phải bản dở sau Dừng/crash) — điều kiện để tự nâng stage lên done.

    translate: checkpoint/salvage chỉ ghi script.json; script.display.json chỉ ghi khi xong.
    tts: salvage ghi tts.json dở → số entry phải = số câu có vi trong script.json.
    mux: output.mp4 cũ hơn tts.json là bản render trước khi đọc lại giọng.
    """
    work_dir = Path(work_dir)
    if stage == "translate":
        sp, dp = work_dir / "script.json", work_dir / "script.display.json"
        if not (sp.exists() and dp.exists()):
            return False
        return dp.stat().st_mtime >= sp.stat().st_mtime - 5 and bool(_json_rows(sp))
    if stage == "tts":
        tp = work_dir / "tts.json"
        if not tp.exists():
            return False
        need = sum(1 for r in _json_rows(work_dir / "script.json")
                   if isinstance(r, dict) and (r.get("vi") or "").strip())
        return need > 0 and len(_json_rows(tp)) >= need
    if stage == "mux":
        outp, tp = work_dir / "output.mp4", work_dir / "tts.json"
        if not outp.exists() or outp.stat().st_size < 1_000_000:
            return False
        return not tp.exists() or outp.stat().st_mtime >= tp.stat().st_mtime
    return _stage_has_artifact(work_dir, stage)


def _stage_has_artifact(work_dir: Path, stage: str) -> bool:
    """Artifact đĩa đủ để coi stage đã xong (dùng heal stale running)."""
    work_dir = Path(work_dir)
    if stage == "download":
        return _find_video(work_dir) is not None
    if stage == "asr":
        p = work_dir / "asr.json"
        return p.exists() and p.stat().st_size > 50
    if stage == "translate":
        p = work_dir / "script.json"
        return p.exists() and p.stat().st_size > 50
    if stage == "tts":
        p = work_dir / "tts.json"
        return p.exists() and p.stat().st_size > 50
    if stage == "mux":
        p = work_dir / "output.mp4"
        return p.exists() and p.stat().st_size > 1_000_000
    if stage == "ocr":
        return (work_dir / "ocr.json").exists()
    if stage == "separate":
        return (work_dir / "no_vocals.wav").exists()
    return False


def _heal_stale_running(work_dir: Path) -> list[str]:
    """Sửa stage status=running mồ côi (kill/crash/skip không mark_done).

    Triệu chứng 1-click: mux=running dù đã tắt encode → mọi lần Chạy tự động
    trả 409 'đang chạy mux'. Có artifact → trả done; không → pending.
    """
    work_dir = Path(work_dir)
    jid = work_dir.name
    if _job_any_busy(jid) or _job_proc_alive(jid):
        return []
    # partial đang ghi + ffmpeg sống → đang encode thật (không heal)
    partial = work_dir / "output.partial.mp4"
    if partial.exists() and (time.time() - partial.stat().st_mtime) < 30:
        # Chỉ tin partial nếu thật sự còn ffmpeg (cwd = job) — tránh wmic chậm
        alive_ff = False
        try:
            import psutil
            job_key = _path_key(work_dir)
            for p in psutil.process_iter(["pid", "name"]):
                try:
                    if not (p.info.get("name") or "").lower().startswith("ffmpeg"):
                        continue
                    cwd = _path_key(p.cwd() or "")
                    if cwd == job_key or cwd.startswith(job_key + "\\"):
                        alive_ff = True
                        break
                except Exception:  # noqa: BLE001
                    continue
        except Exception:  # noqa: BLE001
            alive_ff = False
        if alive_ff:
            return []
        # partial mồ côi → xoá để khỏi chặn lần sau
        try:
            partial.unlink(missing_ok=True)
        except OSError:
            pass
    healed: list[str] = []
    try:
        m = Manifest(work_dir)
        changed = False
        for s in RUNNABLE_STAGES:
            st = m.stage(s) or {}
            if st.get("status") != "running":
                continue
            prev = dict(st)
            if _stage_complete_on_disk(work_dir, s):
                keep = {k: v for k, v in prev.items()
                        if k not in ("status", "error", "cur_text", "started_at")}
                m.data.setdefault("stages", {})[s] = {
                    **keep, "status": "done", "finished_at": time.time(),
                    "healed": "stale_running",
                }
                healed.append(f"{s}->done")
            else:
                keep = {k: v for k, v in prev.items()
                        if k not in ("status", "error", "cur_text", "started_at")}
                m.data.setdefault("stages", {})[s] = {
                    **keep, "status": "pending",
                    "healed": "stale_running_no_artifact",
                }
                healed.append(f"{s}->pending")
            changed = True
        if changed:
            m.save()
            print(f"[heal] {jid}: {', '.join(healed)}", flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[heal] {jid} lỗi: {e}", flush=True)
    return healed


def _next_incomplete_stage(work_dir: Path) -> str | None:
    """Bước WIRED đầu tiên chưa done (để mark_running đúng — không ép lại ASR)."""
    work_dir = Path(work_dir)
    m = Manifest(work_dir)
    for s in WIRED_STAGES:
        if not m.is_done(s) or not _stage_has_artifact(work_dir, s):
            return s
    return None


def _run_engine(script: str, work_dir: Path, *args: str) -> None:
    """Chạy engine NẶNG (ASR/TTS) ở TIẾN TRÌNH RIÊNG.

    Vì sao: ASR (Whisper) & TTS (F5) là torch chạy trong-tiến-trình sẽ GIỮ GIL ở
    phần Python/CPU -> bỏ đói các luồng phục vụ HTTP -> UI khựng/freeze suốt lúc
    chạy. Tách ra subprocess: web server rảnh GIL (UI mượt), VRAM tự nhả sạch khi
    con thoát. Engine tự ghi tiến độ vào manifest.json nên UI vẫn thấy % như cũ.

    Chống nhân bản: trước khi spawn, kill process cũ cùng job (kể cả orphan từ
    lần server trước) — tránh 2–3 firered_asr cùng work/<id>.
    """
    jid = Path(work_dir).name
    if jid in _STOP_JOBS:
        raise _Stopped(jid)
    script_name = Path(script).name
    # Kill process cũ đăng ký trong _PROCS (cùng job)
    old = _PROCS.get(jid)
    if old is not None and old.poll() is None:
        print(f"[proc] kill _PROCS cũ trước khi spawn {script_name} {jid} pid={old.pid}")
        try:
            old.terminate()
        except Exception:  # noqa: BLE001
            pass
        try:
            old.wait(timeout=3)
        except Exception:  # noqa: BLE001
            try:
                old.kill()
            except Exception:  # noqa: BLE001
                pass
    # Kill orphan / duplicate hệ thống (parent server cũ, double-submit…)
    n = _kill_job_engine_procs(jid, script_name)
    if n:
        print(f"[proc] đã dọn {n} process trùng trước khi chạy {script_name} {jid}")

    if jid in _STOP_JOBS:
        raise _Stopped(jid)

    cmd = [sys.executable, str(_PROJ / script), str(Path(work_dir).resolve()), *args]
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    # Lọc PYTHONHASHSEED lỗi: nếu env cha có giá trị rỗng/không hợp lệ, Python CON
    # sẽ "Fatal error ... must be random or int" NGAY lúc khởi động -> gỡ nó ra
    # (để con dùng mặc định 'random'). Đây là bug làm asr/TTS subprocess chết.
    _hs = env.get("PYTHONHASHSEED")
    if _hs is not None and not (_hs == "random" or (_hs.isdigit() and 0 <= int(_hs) <= 4294967295)):
        env.pop("PYTHONHASHSEED", None)
    env["TQDM_DISABLE"] = "1"        # tắt thanh tiến độ tqdm của F5 (bớt spam log)
    print(f"[proc] {script} {jid} {' '.join(args)}")
    proc = subprocess.Popen(cmd, cwd=str(_PROJ), env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, encoding="utf-8", errors="replace", bufsize=1)
    _PROCS[jid] = proc
    try:
        for line in proc.stdout:
            if jid in _STOP_JOBS:
                try:
                    proc.terminate()
                except Exception:  # noqa: BLE001
                    pass
                break
            if _noisy_log(line):     # bỏ dòng rác của F5 (ref_text dài, tqdm...)
                continue
            print(f"[{script}:{jid}] {line.rstrip()}")
        proc.wait()
    finally:
        if _PROCS.get(jid) is proc:
            _PROCS.pop(jid, None)
    if jid in _STOP_JOBS:
        raise _Stopped(jid)
    if proc.returncode != 0:
        # bị "Dừng" kill -> không coi là lỗi thật
        if jid in _STOP_JOBS:
            raise _Stopped(jid)
        raise RuntimeError(f"{script} lỗi (mã {proc.returncode})")


# Script engine nặng — dùng để nhận diện/kill orphan (không chỉ children của server hiện tại).
_HEAVY_ENGINE_SCRIPTS = (
    "asr.py", "nano_fa_asr.py", "fun_asr_nano.py", "paraformer_zh.py", "firered_asr.py",
    "sensevoice_asr.py",
    "clone_tts.py", "ocr.py",
)


def _iter_job_engine_procs(job_id: str, script_name: str | None = None):
    """Quét toàn hệ thống process Python đang chạy engine cho job_id (kể cả orphan)."""
    try:
        import psutil
    except Exception:  # noqa: BLE001
        return
    me = os.getpid()
    # Khớp đường dẫn work tuyệt đối (engine nhận work_dir.resolve()), không chỉ job_id —
    # V1 (Z:\Pineline) cùng URL có cùng job_id.
    _wd = WORK_ROOT / str(job_id)
    needles = {str(_wd).lower().replace("\\", "/")}
    try:
        needles.add(os.path.realpath(_wd).lower().replace("\\", "/"))
    except OSError:
        pass
    script_l = (script_name or "").lower()
    asr_family = {s.lower() for s in _HEAVY_ENGINE_SCRIPTS if "asr" in s.lower() or s == "asr.py"}
    for p in psutil.process_iter(["pid", "name"]):
        try:
            if p.info["pid"] == me:
                continue
            pname = (p.info.get("name") or "").lower()
            if not ("python" in pname or "ffmpeg" in pname or "aria2" in pname):
                continue
            cmd = p.cmdline()
            if not cmd:
                continue
            joined = " ".join(str(x) for x in cmd)
            low = joined.lower().replace("\\", "/")
            if not any(n in low for n in needles):
                continue
            # khớp script cụ thể, hoặc cùng họ ASR khi spawn ASR (tránh whisper+firered song song)
            hit = False
            if script_l:
                if script_l in low:
                    hit = True
                elif script_l in asr_family and any(a in low for a in asr_family):
                    hit = True
            else:
                hit = any(s.lower() in low for s in _HEAVY_ENGINE_SCRIPTS)
            if hit:
                yield p
        except Exception:  # noqa: BLE001
            continue


def _kill_job_engine_procs(job_id: str, script_name: str | None = None, exclude_pid: int | None = None) -> int:
    """Kill process engine trùng job (system-wide). Trả số process đã kill."""
    n = 0
    for p in list(_iter_job_engine_procs(job_id, script_name)):
        try:
            if exclude_pid and p.pid == exclude_pid:
                continue
            print(f"[proc] kill duplicate pid={p.pid} job={job_id} script={script_name or '*'}")
            p.kill()
            n += 1
        except Exception:  # noqa: BLE001
            pass
    return n


def _kill_all_orphan_engine_procs() -> int:
    """Kill toàn bộ orphan engine process trong WORK_ROOT (1 lượt quét duy nhất system-wide)."""
    try:
        import psutil
    except Exception:  # noqa: BLE001
        return 0
    me = os.getpid()
    work_str = str(WORK_ROOT).lower().replace("\\", "/")
    try:
        work_real = os.path.realpath(WORK_ROOT).lower().replace("\\", "/")
    except OSError:
        work_real = work_str
    needles = {work_str, work_real}

    n = 0
    for p in psutil.process_iter(["pid", "name"]):
        try:
            if p.info["pid"] == me:
                continue
            pname = (p.info.get("name") or "").lower()
            if not ("python" in pname or "ffmpeg" in pname or "aria2" in pname):
                continue
            cmd = p.cmdline()
            if not cmd:
                continue
            joined = " ".join(str(x) for x in cmd)
            low = joined.lower().replace("\\", "/")
            if not any(wn in low for wn in needles):
                continue
            if any(s.lower() in low for s in _HEAVY_ENGINE_SCRIPTS) or "ffmpeg" in pname:
                print(f"[proc] kill orphan pid={p.pid} cmd={cmd[:3]}")
                p.kill()
                n += 1
        except Exception:  # noqa: BLE001
            continue
    return n


import re as _re
_NOISE = _re.compile(r"^\s*(ref_text\b|\d+%\||\s*$)")


def _noisy_log(line: str) -> bool:
    """Lọc log rác TTS (ref_text dài, tqdm...). Giữ gen_text + [ok]/[tts]/lỗi."""
    s = line.strip()
    if not s:
        return True
    return bool(_NOISE.match(line)) or ("it/s]" in s and "%" in s)


class _Stopped(Exception):
    """Người dùng bấm Dừng — không phải lỗi."""


def _kill_job_children(job_id: str) -> None:
    """Kill MỌI tiến trình liên quan job (asr/clone_tts/demucs/ffmpeg/aria2c),
    gồm cả orphan từ lần server trước (không chỉ children của PID hiện tại).

    Mux ffmpeg thường cmdline = `ffmpeg -i source.mp4 … output.partial.mp4`
    (KHÔNG có job_id) — chỉ nhận diện bằng cwd = work/<job_id>.
    """
    _kill_job_engine_procs(job_id, None)
    try:
        import psutil
    except Exception:  # noqa: BLE001
        return
    job_dir_key = _path_key(WORK_ROOT / job_id)
    _wd = WORK_ROOT / str(job_id)
    needles = {str(_wd).lower().replace("\\", "/")}
    try:
        needles.add(os.path.realpath(_wd).lower().replace("\\", "/"))
    except OSError:
        pass

    def _cwd_is_job(proc) -> bool:
        try:
            cwd = _path_key(proc.cwd() or "")
        except Exception:  # noqa: BLE001
            return False
        if not cwd:
            return False
        return cwd == job_dir_key or cwd.startswith(job_dir_key + "\\")

    def _should_kill(proc, cmd: str) -> bool:
        name = ""
        try:
            name = (proc.name() or "").lower()
        except Exception:  # noqa: BLE001
            name = ""
        if job_id in cmd:
            return True
        if "vieneu_batch" in cmd or "omnivoice_batch" in cmd:
            # worker TTS nhận work/<job>/tts/_<engine>_job.json — chỉ kill worker của job này
            low = cmd.lower().replace("\\", "/")
            return any(n in low for n in needles)
        # ffmpeg / aria2: nhận diện theo cwd (cmdline thường không chứa job_id)
        if name.startswith("ffmpeg") or name.startswith("aria2c"):
            return _cwd_is_job(proc)
        return False

    # 1) children của server
    try:
        me = psutil.Process()
        for ch in me.children(recursive=True):
            try:
                cmd = " ".join(ch.cmdline() or [])
                if _should_kill(ch, cmd):
                    print(f"[proc] kill child pid={ch.pid} name={ch.name()} job={job_id}",
                          flush=True)
                    ch.kill()
            except Exception:  # noqa: BLE001
                pass
    except Exception:  # noqa: BLE001
        pass

    # 2) orphan system-wide (server cũ / remux tay)
    for p in psutil.process_iter(["pid", "name"]):
        try:
            name = (p.info.get("name") or "").lower()
            if not (name.startswith("ffmpeg") or name.startswith("aria2c")):
                continue
            if not _cwd_is_job(p):
                continue
            print(f"[proc] kill orphan {name} pid={p.pid} job={job_id}", flush=True)
            p.kill()
        except Exception:  # noqa: BLE001
            continue


def _stop_job(job_id: str) -> None:
    """Dừng mọi việc đang chạy của 1 job + đưa stage 'running' về 'pending'."""
    import engines.download as _dlmod
    wd = WORK_ROOT / job_id
    _STOP_JOBS.add(job_id)
    # Cờ file: render._ffmpeg_progress đọc được dù không cùng _PROCS
    try:
        (wd / ".stop").write_text("1", encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    with _STAGE_BUSY_LOCK:
        for key in [k for k in _STAGE_BUSY if k[0] == job_id]:
            _STAGE_BUSY.discard(key)
    try:
        _dlmod._request_stop(wd)
        _dlmod._kill_job_aria2c(wd)
    except Exception:  # noqa: BLE001
        pass
    p = _PROCS.get(job_id)
    if p:
        try:
            p.terminate()
        except Exception:  # noqa: BLE001
            pass
        try:
            p.kill()
        except Exception:  # noqa: BLE001
            pass
    _kill_job_children(job_id)
    try:
        m = Manifest(wd)
        ch = False
        si = m.data.get("split_info") or {}
        out_full = wd / "output_full.mp4"
        full_ok = False
        try:
            full_ok = out_full.is_file() and out_full.stat().st_size > 1_000_000
        except OSError:
            full_ok = False
        already_merged = si.get("status") == "merged" and (_mux_output_ok(wd) or full_ok)
        for name, st in list((m.data.get("stages") or {}).items()):
            if not isinstance(st, dict) or st.get("status") != "running":
                continue
            if name == "mux" and already_merged:
                n = len(si.get("sub_job_ids") or []) or 0
                st["status"] = "done"
                st["progress"] = 100
                st["cur_text"] = (
                    f"Hoàn tất bản Full ({n} parts ghép lại) ✓" if n else "Hoàn tất bản Full ✓"
                )
                st["from_split_merge"] = True
                st["is_full_merged"] = True
                st["updated_at"] = time.time()
            else:
                st["status"] = "pending"
                st.pop("updated_at", None)
            ch = True
        if ch:
            m.save()
            try:
                _job_cache.pop(str(wd), None)
            except NameError:
                pass
        parent_id = (m.data.get("request") or {}).get("parent_job_id")
        if parent_id:
            try:
                pwd = WORK_ROOT / str(parent_id)
                pm = Manifest(pwd)
                psi = pm.data.get("split_info") or {}
                pmux = (pm.data.get("stages") or {}).get("mux") or {}
                pout = pwd / "output.mp4"
                pfull = pwd / "output_full.mp4"
                pok = psi.get("status") == "merged" and (
                    (pout.is_file() and pout.stat().st_size > 1_000_000)
                    or (pfull.is_file() and pfull.stat().st_size > 1_000_000)
                )
                if pok and pmux.get("status") == "running":
                    _ensure_parent_mux_merged_done(
                        pwd, len(psi.get("sub_job_ids") or []) or None
                    )
            except Exception:  # noqa: BLE001
                pass
    except Exception:  # noqa: BLE001
        pass


def _clear_stop(job_id: str) -> None:
    _STOP_JOBS.discard(job_id)
    try:
        (WORK_ROOT / job_id / ".stop").unlink(missing_ok=True)
    except Exception:  # noqa: BLE001
        pass

# Chuỗi BẮT BUỘC (tính % tổng): tải -> nhận diện -> dịch -> lồng tiếng -> ghép/xuất.
WIRED_STAGES = ["download", "asr", "translate", "tts", "mux"]
# Bước TÙY CHỌN (nâng chất lượng, không chặn hoàn thành): OCR chữ trên hình, tách nền.
OPTIONAL_STAGES = ["ocr", "separate"]
RUNNABLE_STAGES = WIRED_STAGES + OPTIONAL_STAGES


def _stage_artifact_payload(work_dir: Path, stage: str) -> dict | None:
    """Nếu đĩa đã có kết quả bước → payload để mark_done. None = chưa có artifact."""
    work_dir = Path(work_dir)
    if stage == "download":
        vid = _find_video(work_dir)
        if not vid:
            return None
        return {"video_path": str(vid), "source": "marked"}
    if stage == "asr":
        p = work_dir / "asr.json"
        if not p.exists():
            return None
        try:
            rows = json.loads(p.read_text(encoding="utf-8"))
            n = len(rows) if isinstance(rows, list) else 0
        except Exception:  # noqa: BLE001
            n = 0
        return {"asr_path": str(p), "n_segments": n, "marked": True}
    if stage == "translate":
        p = work_dir / "script.json"
        if not p.exists():
            return None
        try:
            rows = json.loads(p.read_text(encoding="utf-8"))
            n = len(rows) if isinstance(rows, list) else 0
            miss = sum(1 for r in rows if isinstance(r, dict) and not (r.get("vi") or "").strip()) if isinstance(rows, list) else 0
        except Exception:  # noqa: BLE001
            n, miss = 0, 0
        return {"script_path": str(p), "n_segments": n, "n_missing": miss, "marked": True}
    if stage == "tts":
        tdir = work_dir / "tts"
        n_wav = len([f for f in tdir.glob("seg_*.wav") if f.stat().st_size > 1000]) if tdir.exists() else 0
        if n_wav <= 0 and not (work_dir / "tts.json").exists() and not (work_dir / "dub_fit.wav").exists():
            return None
        out = {"n_clips": n_wav, "n_done": n_wav, "n_missing": 0, "marked": True}
        if (work_dir / "tts.json").exists():
            out["tts_path"] = str(work_dir / "tts.json")
        return out
    if stage == "mux":
        outp = work_dir / "output.mp4"
        if not outp.exists() or outp.stat().st_size < 1000:
            return None
        return {"output_path": str(outp), "marked": True}
    if stage == "ocr":
        p = work_dir / "ocr.json"
        if not p.exists():
            return None
        try:
            rows = json.loads(p.read_text(encoding="utf-8"))
            n = len(rows) if isinstance(rows, list) else 0
        except Exception:  # noqa: BLE001
            n = 0
        return {"n_texts": n, "marked": True}
    if stage == "separate":
        if not any((work_dir / n).exists() for n in ("vocals.wav", "no_vocals.wav", "bgm.wav")):
            return None
        return {"marked": True}
    return None


def _heal_stages_from_disk(m: Manifest) -> list[str]:
    """Misclick/Dừng giữa chừng: file đã ĐỦ mà status còn pending/failed → đánh done.
    Chỉ gọi từ thao tác chủ động (mark-done all), không gọi khi đọc trạng thái."""
    healed: list[str] = []
    for stage in RUNNABLE_STAGES:
        st = m.stage(stage) or {}
        if st.get("status") in ("done", "running"):
            continue
        if not _stage_complete_on_disk(m.work_dir, stage):
            continue
        payload = _stage_artifact_payload(m.work_dir, stage)
        if not payload:
            continue
        # Giữ engine/voice đã lưu
        for k in ("voice", "speed", "tts_engine", "asr_engine", "engine", "model"):
            if k in st and k not in payload:
                payload[k] = st[k]
        m.mark_done(stage, **payload)
        healed.append(stage)
    return healed


def _force_mark_stage(m: Manifest, stage: str, require_artifact: bool = False) -> dict:
    """Đánh dấu 1 bước done ngay (không chạy lại)."""
    if stage not in RUNNABLE_STAGES:
        raise ValueError(f"bước '{stage}' không hợp lệ")
    payload = _stage_artifact_payload(m.work_dir, stage) or {}
    if require_artifact and not payload:
        raise FileNotFoundError(f"chưa có file kết quả cho bước '{stage}'")
    st = m.stage(stage) or {}
    for k in ("voice", "speed", "tts_engine", "asr_engine", "engine", "model",
              "n_segments", "n_clips", "n_done", "video_path", "output_path"):
        if k in st and k not in payload:
            payload[k] = st[k]
    payload["marked"] = True
    payload["progress"] = 100
    return m.mark_done(stage, **payload)

# HAI hàng đợi tách biệt:
#  _dl  : TẢI (mạng) — chạy SONG SONG nhiều job (tải link 2 trong khi link 1 Whisper).
#  _gpu : ASR/Dịch/TTS/Mux (GPU/LLM nặng) — chạy TUẦN TỰ (JOB_WORKERS=1) tránh OOM.
DL_WORKERS = int(os.getenv("DL_WORKERS", "2"))
JOB_WORKERS = int(os.getenv("JOB_WORKERS", "1"))
_dl = ThreadPoolExecutor(max_workers=DL_WORKERS)
_gpu = ThreadPoolExecutor(max_workers=JOB_WORKERS)
_misc = ThreadPoolExecutor(max_workers=1)   # việc lặt vặt: dịch tiêu đề...

app = FastAPI(title="Lồng Tiếng Studio")

_LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _url_host(v: str) -> str:
    from urllib.parse import urlsplit
    try:
        return (urlsplit(v if "//" in v else "//" + v).hostname or "").lower()
    except ValueError:
        return "\0"


@app.middleware("http")
async def _local_only_guard(request, call_next):
    """Chỉ phục vụ máy này: Host lạ = DNS rebinding; Origin/Referer lạ trên /api = trang web
    khác gọi ngầm (CSRF). Script/sidecar/curl không gửi Origin nên vẫn qua."""
    host = request.headers.get("host") or ""
    if host and _url_host(host) not in _LOCAL_HOSTS:
        return JSONResponse({"error": "host không được phép"}, status_code=403)
    if request.url.path.startswith("/api/"):
        origin = request.headers.get("origin")
        if origin is not None and _url_host(origin) not in _LOCAL_HOSTS:
            return JSONResponse({"error": "origin không được phép"}, status_code=403)
        referer = request.headers.get("referer")
        if origin is None and referer and _url_host(referer) not in _LOCAL_HOSTS:
            return JSONResponse({"error": "referer không được phép"}, status_code=403)
    return await call_next(request)


@app.on_event("startup")
async def _quiet_conn_reset():
    """Trên Windows, khi client (UI poll) đóng kết nối đột ngột giữa request, event
    loop Proactor của uvicorn văng traceback 'ConnectionResetError WinError 10054'
    trong _call_connection_lost. Hoàn toàn vô hại nhưng làm rác log -> lọc bỏ."""
    import asyncio
    loop = asyncio.get_running_loop()

    def handler(loop, context):
        exc = context.get("exception")
        if isinstance(exc, ConnectionResetError):
            return                       # client ngắt giữa chừng — bỏ qua
        loop.default_exception_handler(context)

    loop.set_exception_handler(handler)


@app.on_event("startup")
def _reset_stale_running():
    """Khi server khởi động, KHÔNG có thread nào đang chạy. Vậy mọi stage còn ghi
    'running' trong manifest là tàn dư của lần tắt đột ngột (treo/đóng app giữa
    chừng) -> đưa về 'pending' để UI hiện nút ▶ Tiếp tục.

    Đồng thời kill orphan engine (firered_asr/…) còn sót từ PID server cũ.

    TTS: đếm lại seg_*.wav + khôi phục voice từ tts_config.json nếu mất."""
    # Dọn orphan ASR/TTS toàn hệ thống theo work/ (1 lượt quét duy nhất)
    if WORK_ROOT.exists():
        n = _kill_all_orphan_engine_procs()
        if n:
            print(f"[startup] kill {n} orphan engine toàn hệ thống")
    if not WORK_ROOT.exists():
        return
    for d in WORK_ROOT.iterdir():
        if not (d / "manifest.json").exists():
            continue
        try:
            m = Manifest(d)
            changed = False
            for name, st in list(m.data.get("stages", {}).items()):
                if not isinstance(st, dict) or st.get("status") != "running":
                    continue
                st["status"] = "pending"
                st.pop("updated_at", None)
                st["cur_text"] = "đứt giữa chừng — bấm Tiếp tục"
                changed = True
                if name == "tts":
                    _startup_fix_tts(d, st)
            if changed:
                m.save()
                print(f"[startup] reset stage treo của job {d.name}")
        except Exception as e:  # noqa: BLE001
            print(f"[startup] không reset được {d.name}: {e}")


@app.on_event("startup")
def _start_queue_worker():
    """Worker hàng đợi chỉ chạy SAU khi reset stage treo + kill engine orphan; chạy lúc import
    thì job vừa đánh running bị reset/kill ngay."""
    if not _UNDER_PYTEST and job_queue.queue_state()["queue"]:
        job_queue._ensure_worker()


@app.on_event("startup")
def _resume_hg_merge():
    """Hàng đợi gộp Hongguo nạp lại từ work/logs/hg_merge_state.json → chạy tiếp nếu Hongguo đang mở
    (không thì UI/feeder poll /api/hg/merge-queue sẽ tự chạy tiếp khi Hongguo lên)."""
    if _UNDER_PYTEST:
        return
    try:
        import agents.hongguo_bridge as _hgb
        _hgb.merge_resume()
    except Exception as e:  # noqa: BLE001
        print(f"[startup] chạy tiếp hàng đợi gộp lỗi: {e}", flush=True)


def _startup_fix_tts(work_dir: Path, st: dict) -> None:
    """Khôi phục voice/progress TTS sau crash — không mất cấu hình."""
    tts_dir = work_dir / "tts"
    n_wav = len(list(tts_dir.glob("seg_*.wav"))) if tts_dir.exists() else 0
    n_total = st.get("n_total")
    if not n_total and (work_dir / "script.json").exists():
        try:
            segs = json.loads((work_dir / "script.json").read_text(encoding="utf-8"))
            n_total = sum(1 for s in segs if s.get("vi"))
        except Exception:  # noqa: BLE001
            n_total = 0
    if n_wav:
        st["n_done"] = n_wav
        st["n_clips"] = n_wav
        if n_total:
            st["n_total"] = n_total
            st["n_missing"] = max(0, int(n_total) - n_wav)
            st["progress"] = round(n_wav / int(n_total) * 100, 1)
    # Voice: manifest -> sidecar
    if not st.get("voice"):
        side = work_dir / "tts_config.json"
        if side.exists():
            try:
                cfg = json.loads(side.read_text(encoding="utf-8"))
                for k in ("voice", "speed", "tts_engine", "engine"):
                    if cfg.get(k) is not None and not st.get(k):
                        st[k] = cfg[k]
            except Exception:  # noqa: BLE001
                pass
    if st.get("engine") and not st.get("tts_engine"):
        st["tts_engine"] = st["engine"]


class NewJob(BaseModel):
    url: str
    target: str = "Tiếng Việt"
    cookies_from_browser: str | None = None


class LocalJobIn(BaseModel):
    """Tạo job từ video local — không cần URL.
    path có thể là 1 file HOẶC 1 folder (quét video bên trong)."""
    path: str
    target: str = "Tiếng Việt"
    move: bool = False
    title: str | None = None
    recursive: bool = True          # folder: quét cả thư mục con
    group_folder: bool = True       # folder có ≥2 video → gom 1 group


class LocalBatchIn(BaseModel):
    """Import nhiều path (file và/hoặc folder), 1 dòng = 1 path."""
    paths: list[str]
    target: str = "Tiếng Việt"
    move: bool = False
    recursive: bool = True
    group_folder: bool = True
    max_files: int = 500


class HgSubmitIn(BaseModel):
    series_ids: list[str]
    base: str | None = None
    scores: dict[str, str] | None = None


class HgMergeIn(BaseModel):
    names: list[str]
    base: str | None = None
    force: bool = False  # True = enqueue cả series đã DONE


class JobGroupReq(BaseModel):
    """Gom / sửa nhóm series trên hàng chờ.
    action: create | add | rename | ungroup | dissolve
    """
    action: str = "create"
    job_ids: list[str] = []
    group_id: str | None = None
    title: str | None = None


class HgBaseIn(BaseModel):
    base: str | None = None


class TTSReq(BaseModel):
    engine: str | None = None     # vieneu | omnivoice (None -> giữ engine đã lưu / mặc định)
    voice: str | None = None
    speed: float | None = None    # tốc độ đọc (1.0 chuẩn, <1 chậm, >1 nhanh)
    force: bool = False           # False=resume (giữ clip đã có); True=xoá hết đọc lại


class ClipReq(BaseModel):
    i: int
    voice: str | None = None      # None -> dùng đúng giọng job đang dùng
    engine: str | None = None     # vieneu | omnivoice


class MuxReq(BaseModel):
    # voice_bgm: giọng Việt + BGM thư viện assets/bgm (không dùng nhạc gốc)
    # duck_bgm: BGM thư viện + duck tiếng gốc thấp (át BGM gốc / giữ SFX)
    # voice_only: CHỈ giọng Việt
    # duck / demucs_*: giữ nền gốc (có rủi ro bản quyền BGM)
    audio_mode: str = "voice_bgm"
    voice_vol: float = 0.2        # âm lượng giọng Trung khi demucs_keep (0-1)
    orig_vol: float = 0.6         # âm lượng nền tiếng gốc khi duck (0-1)
    add_sub: bool = True          # burn phụ đề Việt
    fit: bool = True              # khớp time (nén câu lố); False = giọng tốc độ tự nhiên
    resolution: str = "source"    # source | 1080 (1K)
    flip: str = ""                # "" | h | v | hv  (lật video lúc render)
    zoom: float = 1.12            # 1.10 | 1.12 | 1.15
    motion: bool = True           # Ken Burns + Drift
    lut: bool = True
    grain: str = "weak"           # off | weak | medium | strong
    brand: bool = False           # legacy: bật brand
    brand_mode: str = "off"       # off | drift | corners | drift_seed
    brand_text: str = ""          # tên kênh
    brand_logo: str = "off"       # off | auto | filename
    frame: str = "off"            # off | auto | filename
    vbitrate: str = "8M"          # H264: 2M | 4M | 8M


class TranslateReq(BaseModel):
    model: str | None = None          # model DỊCH NHÁP (None -> TRANSLATE_MODEL)
    review_model: str | None = None   # có -> SOÁT lại lượt 2 bằng model này
    review_only: bool = False         # chỉ soát bản dịch có sẵn (không dịch lại)
    mode: str | None = None           # oneshot | batch | auto


class ScriptLineEdit(BaseModel):
    """Sửa tay 1 câu trong script.json (zh và/hoặc vi)."""
    i: int
    vi: str | None = None
    zh: str | None = None


class TTSVoiceReq(BaseModel):
    voice: str | None = None
    speed: float | None = None    # lưu tốc độ đọc kèm giọng
    engine: str | None = None     # vieneu | omnivoice


class RunAllReq(BaseModel):
    voice: str | None = None      # giọng TTS cho cả pipeline
    speed: float | None = None    # tốc độ đọc
    tts_engine: str | None = None # vieneu | omnivoice
    asr_engine: str | None = None # fun_asr_nano | sensevoice | paraformer_zh | firered_asr
    audio_mode: str = "voice_bgm"  # voice_bgm | duck_bgm | voice_only | duck | demucs_*
    voice_vol: float = 0.2
    orig_vol: float = 0.6
    ocr: bool = False             # chạy OCR chữ trên hình
    fit: bool = True              # khớp time (nén câu lố cho khớp phim)
    resolution: str = "source"    # source | 1080
    translate_mode: str | None = None  # oneshot | batch | auto
    # Cùng opt render như Mux (1-click truyền xuống _do_render)
    flip: str = ""
    zoom: float = 1.12
    motion: bool = True
    lut: bool = True
    grain: str = "weak"
    brand: bool = False
    brand_mode: str = "off"
    brand_text: str = ""
    brand_logo: str = "off"
    frame: str = "off"
    vbitrate: str = "8M"          # H264: 2M | 4M | 8M


class JobQueueReq(RunAllReq):
    job_ids: list[str]
    skip_done: bool = True
    opts: dict | None = None


class JobQueueGroupReq(RunAllReq):
    """Enqueue cả series theo group_id (sort group_index)."""
    group_id: str
    skip_done: bool = True


class JobQueueRemoveReq(BaseModel):
    job_ids: list[str]


class AgentChatReq(BaseModel):
    """Pineline V4 — chat với AI Agent nhúng."""
    message: str
    history: list[dict] | None = None   # [{role, content}]
    allow_mutate: bool = False          # cho phép queue add/stop
    max_steps: int = 8
    require_confirm: bool = False       # Telegram: tool phá huỷ đỗ lại chờ ✅/❌


class AgentConfirmReq(BaseModel):
    id: str
    approve: bool = False


class AsrEngineReq(BaseModel):
    engine: str                   # fun_asr_nano | sensevoice | paraformer_zh | firered_asr


class AsrSelectReq(BaseModel):
    """Chọn file ASR sidecar → promote thành asr.json (vd asr.fun_nano.json)."""
    source: str                   # tên file trong work/<job>/ (asr.*.json)


class ContextStudioReq(BaseModel):
    """PRE-SCAN Context Studio trước dịch."""
    llm: bool = True
    force: bool = False


class TranslateAltsReq(BaseModel):
    """Quét câu → phương án dịch tối ưu (ngữ cảnh + văn phong)."""
    force: bool = False
    limit: int | None = 120
    apply_pick: bool = False


class ApplyAltReq(BaseModel):
    i: int
    pick: int = 0  # index trong alts[]


class MarkDoneReq(BaseModel):
    stage: str | None = None
    all: bool = False
    force: bool = False


def _process_gpu(job_id: str, target: str):
    """Phần NẶNG (GPU/LLM): ASR -> Dịch. Chạy ở hàng đợi _gpu (tuần tự)."""
    work_dir = WORK_ROOT / job_id
    try:
        if job_id in _STOP_JOBS:
            print(f"[gpu] {job_id}: đã DỪNG — bỏ qua (task xếp hàng trước khi bấm Dừng)")
            return
        free_gpu_vram("trước ASR — nhường GPU")
        eng = _resolve_asr_engine(work_dir, None)
        _run_engine(_asr_script(eng), work_dir)  # subprocess -> UI không khựng
        if job_id in _STOP_JOBS:
            raise _Stopped(job_id)
        _run_translate_engine(work_dir, target=target)  # subprocess riêng -> không giữ GIL
        # Kiểm tra missing trên disk (run_translate đã tự vá; còn sót → vá thêm 1 lượt)
        n_miss = count_script_missing(work_dir)
        if n_miss > 0:
            if job_id in _STOP_JOBS:
                raise _Stopped(job_id)
            print(f"[gpu] {job_id}: sau dịch còn {n_miss} trống -> vá batch")
            _run_translate_engine(work_dir, batch=25, target=target, mode="batch")
        # TTS KHÔNG tự chạy: người dùng chọn giọng rồi bấm "Tạo giọng".
    except _Stopped:
        print(f"[gpu] {job_id}: đã DỪNG theo yêu cầu")
    except Exception as e:  # noqa: BLE001
        print(f"[gpu] job {job_id} dừng: {e}")


def run_pipeline(job_id: str, url: str, target: str, cookies_from_browser: str | None):
    """TẢI (hàng đợi _dl, song song). Tải xong -> đẩy ASR+Dịch sang hàng đợi _gpu
    (tuần tự) -> link 2 tải được TRONG KHI link 1 chạy Whisper."""
    work_dir = WORK_ROOT / job_id
    try:
        if job_id in _STOP_JOBS:
            print(f"[download] {job_id}: đã DỪNG — không tải")
            return
        download_video(url, work_dir, cookies_from_browser=cookies_from_browser)
    except Exception as e:  # noqa: BLE001
        print(f"[download] job {job_id} dừng: {e}")
        return
    if job_id in _STOP_JOBS:
        print(f"[download] {job_id}: đã DỪNG sau tải — không xếp ASR")
        return
    _gpu.submit(_process_gpu, job_id, target)


def _auto_pipeline(job_id: str, audio_mode: str, voice_vol: float, orig_vol: float,
                   use_ocr: bool, fit: bool = True, resolution: str = "source",
                   translate_mode: str | None = None, render_kw: dict | None = None,
                   asr_engine: str | None = None):
    """1-CLICK (chạy ở hàng _dl): tải (nếu cần) -> đẩy phần GPU sang hàng _gpu.

    Claim __all__ chỉ nhả khi _auto_gpu xong (không nhả lúc mới submit) —
    tránh double-click xếp 2 pipeline cùng job.
    """
    wd = WORK_ROOT / job_id
    submitted = False
    try:
        if job_id in _STOP_JOBS:
            return
        m = Manifest(wd)
        req = m.data.get("request", {})
        target = req.get("target", "Tiếng Việt")
        if not _find_video(wd):
            url = req.get("url")
            if not url:
                print(f"[auto] {job_id}: job local chưa có source")
                return
            try:
                download_video(url, wd, cookies_from_browser=req.get("cookies_from_browser"))
            except Exception as e:  # noqa: BLE001
                print(f"[auto] {job_id} tải lỗi: {e}")
                return
        if job_id in _STOP_JOBS or not _find_video(wd):
            return

        # Auto-detect phim dài → chia part, xếp hàng sub-job (không ASR cả 12h)
        try:
            bc = batch_config.load()
            if bool(bc.get("auto_split", True)):
                sp = _maybe_auto_split_guarded(
                    job_id,
                    work_root=WORK_ROOT,
                    enabled=True,
                    target_hours=float(bc.get("auto_split_hours") or 2.5),
                    min_hours=float(bc.get("auto_split_min_h") or 3.0),
                )
                if sp.get("split") and sp.get("sub_job_ids"):
                    opts = {
                        "audio_mode": audio_mode, "voice_vol": voice_vol, "orig_vol": orig_vol,
                        "ocr": use_ocr, "fit": fit, "resolution": resolution,
                        "translate_mode": translate_mode, "asr_engine": asr_engine,
                        **(render_kw or {}),
                    }
                    # Giọng từ manifest
                    try:
                        qo = (Manifest(wd).data.get("queue_opts") or {})
                        if qo.get("voice"):
                            opts["voice"] = qo["voice"]
                        if qo.get("speed") is not None:
                            opts["speed"] = qo["speed"]
                        if qo.get("tts_engine"):
                            opts["tts_engine"] = qo["tts_engine"]
                    except Exception:  # noqa: BLE001
                        pass
                    # Giữ đúng thứ tự p01 → p02 → … (queue chạy 1 job/lần = lần lượt từng part)
                    job_queue.queue_add(
                        list(sp["sub_job_ids"]), opts=opts, skip_done=True, sort_first=False,
                    )
                    print(
                        f"[auto_split] run-all {job_id}: đã chia {sp.get('total_parts')} part "
                        f"→ xếp hàng lần lượt {sp['sub_job_ids']}",
                        flush=True,
                    )
                    return
        except Exception as e_as:  # noqa: BLE001
            print(f"[auto_split] run-all {job_id} bỏ qua: {e_as}", flush=True)

        def _gpu_wrapped():
            try:
                _auto_gpu(job_id, target, audio_mode, voice_vol, orig_vol, use_ocr,
                          fit, resolution, translate_mode, render_kw or {},
                          asr_engine=asr_engine)
            finally:
                _release_stage(job_id, "__all__")

        _gpu.submit(_gpu_wrapped)
        submitted = True
    finally:
        if not submitted:
            _release_stage(job_id, "__all__")


def _run_requested_review(wd: Path, target: str) -> dict | None:
    """Rà soát do Agent/user yêu cầu (manifest.agent.review_request): rà tên nhân vật theo bảng
    rồi rà văn phong toàn bộ. Chạy 1 lần/yêu cầu; None nếu không có yêu cầu đang chờ."""
    m = Manifest(wd)
    agent = dict(m.data.get("agent") or {})
    rq = dict(agent.get("review_request") or {})
    if not rq or rq.get("done_at"):
        return None
    from agents.agent_name_pass import run_name_pass
    from engines.translate import run_review as _run_review_sync

    pre = wd / "script.pre_agent_review.json"
    try:
        shutil.copyfile(wd / "script.json", pre)
    except Exception:  # noqa: BLE001
        pass
    print(f"[auto] {wd.name}: Agent yêu cầu rà soát — tên → xưng hô → văn phong", flush=True)
    res: dict = {}
    try:
        res["names"] = run_name_pass(wd, model=rq.get("model"))
    except Exception as e:  # noqa: BLE001
        res["names"] = {"ok": False, "error": str(e)}
    try:
        from agents.agent_pronoun_pass import run_pronoun_pass
        res["pronouns"] = run_pronoun_pass(wd, model=rq.get("model"))
    except Exception as e:  # noqa: BLE001
        res["pronouns"] = {"ok": False, "error": str(e)}
    try:
        _run_review_sync(wd, target=target, model=rq.get("model"), force=True)
        res["style"] = {"ok": True}
    except Exception as e:  # noqa: BLE001
        res["style"] = {"ok": False, "error": str(e)}
    n_changed = 0
    try:
        before = {r.get("i"): (r.get("vi") or "") for r in json.loads(pre.read_text(encoding="utf-8"))}
        after = json.loads((wd / "script.json").read_text(encoding="utf-8"))
        n_changed = sum(1 for r in after if before.get(r.get("i")) != (r.get("vi") or ""))
    except Exception:  # noqa: BLE001
        pass
    res["n_changed"] = n_changed
    m = Manifest(wd)
    agent = dict(m.data.get("agent") or {})
    rq.update({"done_at": time.strftime("%Y-%m-%d %H:%M:%S"), "result": res})
    agent["review_request"] = rq
    m.data["agent"] = agent
    tr = m.data.setdefault("stages", {}).setdefault("translate", {})
    nm = res.get("names") or {}
    tr["cur_text"] = (f"Agent đã rà: sửa tên {nm.get('n_fixed', 0)}/{nm.get('n_issues', 0)} câu nghi sai · "
                      f"tổng {n_changed} câu đổi")
    m.save()
    try:
        from agents.agent_watch import telegram_send
        title = (m.data.get("request") or {}).get("title") or wd.name
        telegram_send(f"✅ Rà soát xong trước lồng tiếng: {title}\n{tr['cur_text']}"
                      + ("" if res["style"].get("ok") else f"\n⚠ rà văn phong lỗi: {res['style'].get('error')}"),
                      force=True)
    except Exception:  # noqa: BLE001
        pass
    return res


def _save_series_glossary(wd: Path) -> None:
    try:
        import engines.series_glossary as series_glossary
        r = series_glossary.save_from(wd)
        if r.get("ok"):
            print(f"[auto] {wd.name}: lưu bảng nhân vật bộ «{r['core']}» ({r['n_characters']} nhân vật)",
                  flush=True)
    except Exception as e:  # noqa: BLE001
        print(f"[auto] {wd.name}: lưu bảng bộ lỗi: {e}", flush=True)


def _auto_gpu(job_id: str, target: str, audio_mode: str, voice_vol: float,
              orig_vol: float, use_ocr: bool, fit: bool = True,
              resolution: str = "source", translate_mode: str | None = None,
              render_kw: dict | None = None, asr_engine: str | None = None):
    """Phần GPU của 1-click (hàng _gpu, tuần tự): ASR -> Dịch -> TTS -> [Tách nền]
    -> [OCR] -> Render. Mỗi engine tự SKIP nếu đã xong -> resume được. Kiểm tra cờ
    Dừng giữa các bước."""
    wd = WORK_ROOT / job_id
    rkw = dict(render_kw or {})

    def stopped() -> bool:
        return job_id in _STOP_JOBS

    try:
        if stopped():
            return
        if _part_pipeline_complete(wd):
            print(
                f"[auto] {job_id}: skip GPU pipeline — mux/output đã xong, không stale.",
                flush=True,
            )
            return
        free_gpu_vram("trước ASR — nhường GPU")
        # Ưu tiên engine từ opts hàng chờ — không lấy “leftover” lệch giữa các job
        asr_eng = _resolve_asr_engine(wd, asr_engine)
        _run_engine(_asr_script(asr_eng), wd)
        if stopped():
            return
        _run_translate_engine(wd, target=target, mode=translate_mode)
        # TỰ KIỂM TRA missing trên disk (không tin n_missing cũ trong manifest)
        n_miss = count_script_missing(wd)
        if n_miss > 0:
            print(f"[auto] {job_id}: dịch còn {n_miss} câu trống -> vá lô nhỏ")
            _run_translate_engine(wd, batch=25, target=target, mode="batch")
            n_miss = count_script_missing(wd)
            if n_miss > 0:
                print(f"[auto] {job_id}: vẫn còn {n_miss} trống sau vá — TTS sẽ bỏ qua câu thiếu")
        if stopped():
            return
        # Pineline V4 Agent: HOLD sau translate — không TTS đến khi duyệt script
        m_hold = Manifest(wd)
        agent_cfg = m_hold.data.get("agent") or {}
        if agent_cfg.get("hold_after_translate"):
            agent_cfg = dict(agent_cfg)
            agent_cfg["held_at"] = "after_translate"
            agent_cfg["hold_reason"] = "chờ duyệt script (Agent/UI) trước TTS"
            m_hold.data["agent"] = agent_cfg
            tr = m_hold.data.setdefault("stages", {}).setdefault("translate", {})
            tr["cur_text"] = "HOLD — chờ duyệt script trước TTS"
            m_hold.save()
            print(f"[auto] {job_id}: HOLD after translate — bỏ qua TTS/mux đến khi clear hold + chạy tiếp")
            return
        _run_requested_review(wd, target)
        if stopped():
            return
        agent_cfg = Manifest(wd).data.get("agent") or {}
        # B: QA gate — review → diff → mới TTS (mặc định bật nếu AGENT_QA_GATE=1)
        qa_default = (os.getenv("AGENT_QA_GATE") or "1").strip().lower() in ("1", "true", "yes")
        qa_on = agent_cfg.get("qa_gate") if "qa_gate" in agent_cfg else qa_default
        if qa_on and not agent_cfg.get("qa_override"):
            from agents.agent_qa_gate import run_qa_gate
            from engines.translate import run_review as _run_review_sync

            def _rev(work_dir, target="Tiếng Việt", model=None):
                _run_review_sync(work_dir, target=target, model=model)

            print(f"[auto] {job_id}: QA gate — snapshot + review…")
            gate = run_qa_gate(wd, run_review_fn=_rev, target=target)
            if not gate.get("pass"):
                print(
                    f"[auto] {job_id}: QA BLOCK — "
                    f"{(gate.get('diff') or {}).get('fail_reasons') or gate.get('error')}"
                )
                return
            print(f"[auto] {job_id}: QA pass — tiếp TTS")
            if stopped():
                return
        # yêu cầu rà gửi tới lúc QA gate đang chạy → vẫn rà trước khi lồng tiếng
        if _run_requested_review(wd, target) is not None and stopped():
            return
        _save_series_glossary(wd)
        v = _resolve_voice(wd, None)
        if not v:
            # Lưới an toàn: run_all đã chặn, nhưng nếu voice bị xóa giữa chừng thì dừng.
            raise RuntimeError(
                "chưa chọn giọng clone — dừng 1-click (không render tiếng gốc)."
            )
        free_gpu_vram("trước TTS")
        sp = _resolve_speed(wd, None)
        eng = _resolve_tts_engine(wd, None)
        _do_tts(wd, v, sp, eng, force=False)
        # TỰ KIỂM TRA: còn câu thiếu audio -> đọc bù 1 lượt (resume)
        if (Manifest(wd).stage("tts") or {}).get("n_missing"):
            n = (Manifest(wd).stage("tts") or {}).get("n_missing")
            print(f"[auto] {job_id}: TTS còn {n} câu thiếu -> đọc bù")
            _do_tts(wd, v, sp, eng, force=False)
        if stopped():
            return
        if audio_mode in ("demucs_keep", "demucs_clean"):   # cần tách nền
            free_gpu_vram("trước tách nền")
            run_separate(wd)
            if stopped():
                return
        if use_ocr:
            free_gpu_vram("trước OCR")
            run_ocr(wd)
            if stopped():
                return
        free_gpu_vram("trước render")
        _do_render(
            wd, force=False, audio_mode=audio_mode, voice_vol=voice_vol,
            orig_vol=orig_vol, fit=fit, resolution=resolution,
            flip=str(rkw.get("flip") or ""),
            zoom=float(rkw.get("zoom") or 1.12),
            motion=bool(rkw.get("motion", True)),
            lut=bool(rkw.get("lut", True)),
            grain=str(rkw.get("grain") or "weak"),
            brand=bool(rkw.get("brand", False)),
            brand_text=str(rkw.get("brand_text") or ""),
            frame=str(rkw.get("frame") or "off"),
            brand_mode=str(rkw.get("brand_mode") or "off"),
            brand_logo=str(rkw.get("brand_logo") or "off"),
            vbitrate=str(rkw.get("vbitrate") or "8M"),
        )
        print(f"[auto] {job_id}: HOÀN TẤT toàn bộ pipeline ✓")
    except _Stopped:
        print(f"[auto] {job_id}: đã DỪNG theo yêu cầu")
    except Exception as e:  # noqa: BLE001
        print(f"[auto] {job_id} lỗi: {e}")
        if "chưa chọn giọng" in str(e):
            try:
                m = Manifest(wd)
                st = m.data.setdefault("stages", {}).setdefault("tts", {})
                st["status"] = "failed"
                st["cur_text"] = str(e)[:200]
                m.save()
            except Exception:  # noqa: BLE001
                pass


# ===== Dịch tiêu đề job sang tiếng Việt (hiện ở Hàng chờ) =====
_title_pending: set[str] = set()   # đang dịch
_title_tried: dict[str, int] = {}  # job_id → số lần đã thử (cho phép thử lại tối đa _TITLE_MAX_RETRY)
_TITLE_MAX_RETRY = 3               # thử tối đa 3 lần trước khi bỏ cuộc


def _has_cjk(s: str) -> bool:
    return any("\u4e00" <= c <= "\u9fff" for c in (s or ""))


def _extract_vi_title(raw: str) -> str:
    """Bóc tách tên tiếng Việt từ response LLM có thể dài dòng / giải thích.

    Chiến lược:
      1. Dọn dẹp markdown (**text**, "text", > text).
      2. Lấy dòng đầu tiên KHÔNG chứa ký tự CJK (bỏ qua dòng LLM trích lại
         tiêu đề gốc bằng Hán tự).
      3. Cắt 200 ký tự.
    """
    import re as _re
    if not raw:
        return ""
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # Bỏ markdown bold/italic, blockquote prefix, bullet
        line = _re.sub(r"^\s*[>\-\*\d.]+\s*", "", line)
        line = _re.sub(r"\*{1,2}(.*?)\*{1,2}", r"\1", line)
        line = line.strip().strip('"').strip("'").strip('"').strip('"')
        # Bỏ prefix kiểu "Dịch sát nghĩa:", "Bản dịch:"
        line = _re.sub(r"^(?:Dịch[^:]{0,30}:|Bản dịch[^:]{0,15}:|Tiêu đề[^:]{0,15}:)\s*", "", line, flags=_re.I)
        line = line.strip().strip('"').strip("'")
        if not line:
            continue
        if not _has_cjk(line):
            return line[:200]
    return ""


def _translate_title(job_id: str) -> None:
    """Dịch tiêu đề gốc (Trung) sang tiếng Việt bằng gemma4 local, lưu title_vi."""
    ok = False
    try:
        from engines.llm import chat
        wd = WORK_ROOT / job_id
        m = Manifest(wd)
        if m.data.get("title_vi"):
            ok = True  # đã có rồi, không cần retry
            return
        title = (m.stage("download") or {}).get("title") or ""
        if not title or not _has_cjk(title):
            ok = True  # không cần dịch
            return
        from core.config import get as _cfg_get
        model = _cfg_get("TRANSLATE_MODEL") or None
        msgs = [{"role": "user", "content":
                 "Dịch tiêu đề video sau sang tiếng Việt tự nhiên, ngắn gọn. "
                 "CHỈ trả về bản dịch trên MỘT dòng, không giải thích, không ngoặc kép:\n\n" + title}]
        raw = (chat(msgs, model=model, temperature=0.3, max_tokens=200) or "").strip()
        vi = _extract_vi_title(raw)
        if vi:
            m2 = Manifest(wd)
            m2.data["title_vi"] = vi
            m2.save()
            _job_cache.pop(str(wd), None)      # ép list_jobs dựng lại -> hiện bản Việt
            print(f"[title] {job_id}: {vi}")
            ok = True
        else:
            print(f"[title] {job_id} không bóc được tiếng Việt từ LLM: {raw[:120]}")
    except Exception as e:  # noqa: BLE001
        print(f"[title] {job_id} lỗi dịch tiêu đề: {e}")
    finally:
        _title_pending.discard(job_id)
        if ok:
            # Thành công hoặc không cần dịch → đánh dấu xong
            _title_tried[job_id] = _TITLE_MAX_RETRY
        else:
            # Thất bại → tăng đếm, nhịp poll sau sẽ thử lại nếu chưa vượt max
            _title_tried[job_id] = _title_tried.get(job_id, 0) + 1
            n = _title_tried[job_id]
            if n < _TITLE_MAX_RETRY:
                print(f"[title] {job_id} sẽ thử lại (lần {n}/{_TITLE_MAX_RETRY})")
            else:
                print(f"[title] {job_id} bỏ cuộc sau {n} lần thử")


def _maybe_translate_title(job_id: str, title: str) -> None:
    """Kích hoạt dịch tiêu đề (lazy) nếu còn tiếng Trung. Bỏ qua khi ASR/TTS đang
    chạy (tránh nạp gemma4 chồng lên -> OOM VRAM) — sẽ thử lại ở nhịp poll sau."""
    if not _has_cjk(title):
        return
    if job_id in _title_pending:
        return
    if _title_tried.get(job_id, 0) >= _TITLE_MAX_RETRY:
        return
    if _PROCS:                       # có asr/TTS subprocess đang chạy -> để sau
        return
    _title_pending.add(job_id)
    _misc.submit(_translate_title, job_id)


_job_cache: dict[str, tuple] = {}   # work_dir -> (mtime_ns, size, kết quả read_job)


def _asr_labels_from_source(src_name: str) -> tuple[str | None, str]:
    """Suy engine + model từ tên file sidecar (nguồn sự thật)."""
    n = (src_name or "").lower()
    if "nano_fa" in n:
        return "nano_fa", "Nano+Direct FA"
    if "fun_nano" in n:
        return "fun_asr_nano", "Fun-ASR-Nano"
    if "firered" in n:
        return "firered_asr", "FireRedASR2-AED"
    if "paraformer" in n:
        return "paraformer_zh", "Paraformer-zh"
    if "sensevoice" in n:
        return "sensevoice", "SenseVoiceSmall"
    if any(x in n for x in ("aligned", "consensus", "repaired")):
        return "hybrid_fa", "Hybrid FA"
    return None, ""


def _sync_asr_labels(work_dir: Path, asr: dict | None = None) -> dict:
    """Ép engine/model khớp asr_source (+ n_segments từ asr.json nếu có).

    Tránh UI: «2060 câu · fun_asr_nano» khi nội dung thực là FireRed.
    """
    if not isinstance(asr, dict):
        asr = {}
    src = str(asr.get("asr_source") or "")
    eng, model = _asr_labels_from_source(src)
    changed = False
    out = dict(asr)
    if eng and (out.get("asr_engine") != eng or out.get("engine") != eng):
        out["asr_engine"] = eng
        out["engine"] = eng
        changed = True
    if model and out.get("model") != model:
        out["model"] = model
        changed = True
    asr_path = work_dir / "asr.json"
    if asr_path.exists():
        try:
            rows = json.loads(asr_path.read_text(encoding="utf-8"))
            if isinstance(rows, list) and rows:
                n = len(rows)
                if out.get("n_segments") != n:
                    out["n_segments"] = n
                    changed = True
        except Exception:  # noqa: BLE001
            pass
    if changed:
        patch = {"asr_engine": out.get("asr_engine"), "engine": out.get("engine"),
                 "model": out.get("model"), "n_segments": out.get("n_segments")}
        if src:
            patch["asr_source"] = src
        _patch_asr_fields(work_dir, **{k: v for k, v in patch.items() if v is not None})
    return out


def _apply_hybrid_asr_overlay(work_dir: Path, result: dict) -> dict:
    """Hybrid FA: UI đọc stages.asr — overlay % từ asr.*.progress.json nếu sidecar đang chạy.
    Đồng thời sync engine/model theo asr_source (chống lệch nhãn)."""
    try:
        out = dict(result)
        stages = dict(out.get("stages") or {})
        asr = dict(stages.get("asr") or {})
        if asr:
            asr = _sync_asr_labels(work_dir, asr)
            stages["asr"] = asr
            out["stages"] = stages
        if asr.get("status") == "running":
            eng = asr.get("asr_engine") or asr.get("engine") or ""
            if eng == "hybrid_fa":
                from engines.asr.asr_hybrid_progress import overlay_job_asr
                over = overlay_job_asr(work_dir, asr)
                if over is not asr:
                    stages = dict(out.get("stages") or {})
                    stages["asr"] = over
                    out["stages"] = stages
        return out
    except Exception:  # noqa: BLE001
        return result


def read_job(work_dir: Path) -> dict:
    # Cache theo (mtime,size) của manifest.json: job KHÔNG đổi (đã xong/đang chờ) ->
    # trả cache, KHÔNG đọc đĩa/parse lại. Chỉ job ĐANG CHẠY (mtime nhảy ~1.5s) mới
    # đọc lại. Giảm mạnh I/O + va chạm khoá khi list_jobs quét mọi job mỗi vài giây.
    mpath = work_dir / "manifest.json"
    stt = None
    try:
        stt = mpath.stat()
        c = _job_cache.get(str(work_dir))
        if c and c[0] == stt.st_mtime_ns and c[1] == stt.st_size:
            cached = dict(c[2])
            # Cache theo manifest — script.json có thể đã vá missing mà UI vẫn báo thiếu
            try:
                sp = work_dir / "script.json"
                if sp.exists():
                    rows = json.loads(sp.read_text(encoding="utf-8"))
                    miss = sum(
                        1 for r in rows
                        if isinstance(r, dict) and not (r.get("vi") or "").strip()
                    )
                    tr_st = dict(cached.get("stages", {}).get("translate") or {})
                    tr_st["n_missing"] = miss
                    tr_st["n_segments"] = tr_st.get("n_segments") or len(rows)
                    if miss <= 0 and tr_st.get("status") == "done":
                        tr_st["cur_text"] = "đủ bản dịch"
                    cached.setdefault("stages", {})["translate"] = tr_st
            except Exception:  # noqa: BLE001
                pass
            _maybe_translate_title(work_dir.name, cached["title"])   # còn Trung -> dịch
            # Hybrid: sidecar progress đổi mà manifest chưa → vẫn overlay mỗi lần poll
            return _apply_hybrid_asr_overlay(work_dir, cached)
    except OSError:
        pass

    m = Manifest(work_dir)
    stages = m.data.get("stages", {})
    req = m.data.get("request", {})
    dl = stages.get("download", {})

    done = sum(1 for s in WIRED_STAGES if stages.get(s, {}).get("status") == "done")
    overall = int(done / len(WIRED_STAGES) * 100)

    if any(stages.get(s, {}).get("status") == "failed" for s in WIRED_STAGES):
        status = "failed"
    elif done == len(WIRED_STAGES):
        status = "done"
    elif any(stages.get(s, {}).get("status") == "running" for s in WIRED_STAGES):
        status = "running"
    else:
        status = "pending"

    result = {
        "job_id": work_dir.name,
        # ưu tiên: tiêu đề Việt (đã dịch) -> tiêu đề tải được -> tiêu đề phần (lúc bóc) -> url
        "title": (m.data.get("title_vi") or dl.get("title") or req.get("title")
                  or req.get("part_title")
                  or req.get("url") or work_dir.name),
        "title_zh": dl.get("title") or req.get("part_title") or req.get("title"),
        "platform": dl.get("platform") or ("local" if req.get("local") else None),
        "local": bool(req.get("local")),
        "duration_sec": dl.get("duration_sec"),
        "height": dl.get("height"),
        "target": req.get("target"),
        "overall": overall,
        "status": status,
        "started": bool(stages),    # đã bấm Bắt đầu chưa (có stage nào chạy chưa)
        "stages": {s: stages.get(s, {}) for s in RUNNABLE_STAGES},
        "dub": m.data.get("dub"),   # audio ngoài đã nhập (nếu có)
        # nhóm (multi-P/playlist) -> UI gom lại
        "group_id": req.get("group_id"),
        "group_title": req.get("group_title"),
        "group_index": req.get("group_index"),
        "group_total": req.get("group_total"),
    }
    # Context Studio (PRE) — không thuộc WIRED nhưng UI cần status
    try:
        cs = stages.get("context_studio")
        if cs:
            result["stages"]["context_studio"] = cs
        elif (work_dir / "context_pack.json").exists():
            result["stages"]["context_studio"] = {"status": "done", "ready": True}
    except Exception:  # noqa: BLE001
        pass
    # TTS: bổ sung số wav trên đĩa (tts.json có thể chưa kịp ghi → UI đừng báo thiếu hết)
    try:
        tts_st = dict(result["stages"].get("tts") or {})
        tdir = work_dir / "tts"
        n_wav = len([f for f in tdir.glob("seg_*.wav") if f.stat().st_size > 1000]) if tdir.exists() else 0
        tts_st["n_wav"] = n_wav
        if n_wav and tts_st.get("status") != "running":
            tts_st["n_done"] = max(int(tts_st.get("n_done") or 0), n_wav)
            tts_st["n_clips"] = max(int(tts_st.get("n_clips") or 0), n_wav)
        result["stages"]["tts"] = tts_st
    except Exception:  # noqa: BLE001
        pass
    # Dịch: đếm thật câu trống trong script.json (manifest hay để n_missing=0 sai)
    try:
        tr_st = dict(result["stages"].get("translate") or {})
        sp = work_dir / "script.json"
        if sp.exists():
            rows = json.loads(sp.read_text(encoding="utf-8"))
            miss = sum(1 for r in rows if isinstance(r, dict) and not (r.get("vi") or "").strip())
            tr_st["n_missing"] = miss
            tr_st["n_segments"] = tr_st.get("n_segments") or len(rows)
            if miss <= 0 and tr_st.get("status") in ("done", "pending", None, ""):
                tr_st["cur_text"] = tr_st.get("cur_text") if tr_st.get("status") == "running" else "đủ bản dịch"
            result["stages"]["translate"] = tr_st
            # Đồng bộ manifest để nút «Dịch vá» / badge không kẹt số cũ
            try:
                old = (m.stage("translate") or {}).get("n_missing")
                if old != miss:
                    st = m.data.setdefault("stages", {}).setdefault("translate", {})
                    st["n_missing"] = miss
                    if miss <= 0 and st.get("status") == "done":
                        st["cur_text"] = "đủ bản dịch"
                    m.data["stages"]["translate"] = st
                    m.save()
            except Exception:  # noqa: BLE001
                pass
        sync = _translate_asr_sync_info(work_dir)
        tr_st = dict(result["stages"].get("translate") or {})
        tr_st["asr_sync"] = sync
        if sync.get("stale"):
            tr_st["stale"] = True
        result["stages"]["translate"] = tr_st
    except Exception:  # noqa: BLE001
        pass
    if stt is not None:
        _job_cache[str(work_dir)] = (stt.st_mtime_ns, stt.st_size, result)
    _maybe_translate_title(work_dir.name, result["title"])
    return _apply_hybrid_asr_overlay(work_dir, result)


# static/app.js + assets cho UI variants
try:
    from fastapi.staticfiles import StaticFiles
    _static = Path(__file__).parent / "static"
    _static.mkdir(exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(_static)), name="static")
except Exception as _e:  # noqa: BLE001
    print(f"[warn] không mount /static: {_e}")


def _create(url: str, target: str, cookies_from_browser: str | None,
            group: dict | None = None) -> str:
    """Tạo 1 job ở trạng thái CHỜ (chưa chạy). Người dùng bấm ▶ Bắt đầu mới chạy.
    group: {id, title, index, total, part_title} khi job thuộc nhóm (multi-P/playlist)."""
    job_id = job_id_from_url(url)
    work_dir = WORK_ROOT / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    m = Manifest(work_dir)
    req = {"url": url, "target": target, "cookies_from_browser": cookies_from_browser}
    if group:
        req.update(group)
    m.data["request"] = req
    m.save()
    return job_id


def _job_id_local(key: str) -> str:
    return hashlib.sha1(f"local:{key}".encode("utf-8")).hexdigest()[:12]


def _create_local_shell(target: str, *, job_key: str, title: str | None = None,
                        orig_path: str | None = None,
                        group: dict | None = None) -> tuple[str, Path]:
    """Tạo job local (không URL). job_key ổn định theo path để resume cùng file."""
    job_id = _job_id_local(job_key)
    work_dir = WORK_ROOT / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    m = Manifest(work_dir)
    req = {
        "url": None,
        "local": True,
        "target": target,
        "title": title,
        "orig_path": orig_path,
    }
    if group:
        req.update(group)
    m.data["request"] = req
    m.save()
    return job_id, work_dir


def _list_local_videos(root: Path, *, recursive: bool = True, limit: int = 500) -> list[Path]:
    """Liệt kê file video trong folder (sắp tên tự nhiên)."""
    if not root.is_dir():
        return []
    found: list[Path] = []
    try:
        it = root.rglob("*") if recursive else root.iterdir()
        for p in it:
            try:
                if p.is_file() and p.suffix.lower() in _VIDEO_EXT:
                    found.append(p)
                    if len(found) >= limit:
                        break
            except OSError:
                continue
    except OSError:
        return []
    def _key(p: Path):
        # natural-ish: tách số trong tên
        import re as _re
        parts = _re.split(r"(\d+)", p.name.lower())
        return [int(x) if x.isdigit() else x for x in parts]
    found.sort(key=_key)
    return found


def _import_local_video_file(
    src: Path,
    *,
    target: str,
    move: bool = False,
    title: str | None = None,
    group: dict | None = None,
) -> dict:
    """Copy/move 1 file video → job local. Trả dict ok/job_id hoặc error."""
    if not src.is_file():
        return {"ok": False, "error": f"không phải file: {src}"}
    ext = src.suffix.lower()
    if ext not in _VIDEO_EXT:
        return {"ok": False, "error": f"định dạng {ext or '?'} không hỗ trợ"}
    title = (title or src.stem).strip() or src.stem
    job_id, work_dir = _create_local_shell(
        target, job_key=str(src.resolve()), title=title, orig_path=str(src), group=group,
    )
    # Job đã có source? skip copy (resume)
    existing = next((work_dir / f"source{e}" for e in _VIDEO_EXT if (work_dir / f"source{e}").exists()), None)
    if existing and existing.stat().st_size > 0:
        return {"ok": True, "job_id": job_id, "skipped": True, "title": title, "path": str(src)}
    vp = (Manifest(work_dir).stage("download") or {}).get("video_path")
    if vp and Path(vp).is_file() and Path(vp).resolve() == src.resolve():
        return {"ok": True, "job_id": job_id, "skipped": True, "title": title, "path": str(src)}
    try:
        dest, how = _place_source(src, work_dir, move)
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": f"copy/move lỗi: {e}", "job_id": job_id}
    info = _finalize_imported_source(
        work_dir, dest, orig_name=src.name, source_kind="imported_path", source_mode=how,
    )
    m = Manifest(work_dir)
    dl = m.stage("download") or {}
    if title and dl.get("title") != title:
        m.mark_done("download", **{**dl, "title": title})
        meta_p = work_dir / "meta.json"
        if meta_p.exists():
            try:
                meta = json.loads(meta_p.read_text(encoding="utf-8"))
                meta["title"] = title
                meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:  # noqa: BLE001
                pass
    return {"ok": True, "job_id": job_id, "title": title, "path": str(src), **info}


def create_job(job: NewJob):
    """Thêm link -> tạo job CHỜ. 1 link ra NHIỀU video (multi-P/playlist) -> gom
    thành 1 NHÓM (group_id chung) để Hàng chờ không bị loạn/nhầm."""
    try:
        meta = expand_meta(job.url, cookies_from_browser=job.cookies_from_browser)
        parts = meta.get("parts") or [{"url": job.url, "title": None}]
    except Exception as e:  # noqa: BLE001
        print(f"[expand] lỗi bóc playlist, coi như 1 video: {e}")
        meta, parts = {"title": None}, [{"url": job.url, "title": None}]

    group = None
    if len(parts) > 1:
        gid = hashlib.sha1(job.url.encode("utf-8")).hexdigest()[:10]
        group = {"group_id": gid, "group_title": meta.get("title") or job.url,
                 "group_total": len(parts)}

    job_ids = []
    for i, p in enumerate(parts, 1):
        g = None
        if group:
            g = {**group, "group_index": i, "part_title": p.get("title")}
        job_ids.append(_create(p["url"], job.target, job.cookies_from_browser, g))
    return {"job_ids": job_ids, "count": len(job_ids),
            "group": bool(group), "group_title": (group or {}).get("group_title")}


def _patch_job_group(job_id: str, *, group_id: str | None,
                     group_title: str | None = None,
                     group_index: int | None = None,
                     group_total: int | None = None,
                     part_title: str | None = None) -> bool:
    """Ghi/xoá group_* trong manifest.request. Trả False nếu job không tồn tại."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return False
    m = Manifest(work_dir)
    req = m.data.setdefault("request", {})
    if not group_id:
        for k in ("group_id", "group_title", "group_index", "group_total", "part_title"):
            req.pop(k, None)
    else:
        req["group_id"] = group_id
        if group_title is not None:
            req["group_title"] = group_title
        if group_index is not None:
            req["group_index"] = int(group_index)
        if group_total is not None:
            req["group_total"] = int(group_total)
        if part_title is not None:
            req["part_title"] = part_title
    m.data["request"] = req
    m.save()
    _job_cache.pop(str(work_dir), None)
    return True


def _renumber_group(group_id: str, title: str | None = None) -> list[str]:
    """Sắp lại group_index 1..N theo index cũ (hoặc created). Trả job_ids còn trong nhóm."""
    members: list[tuple[int, str, dict]] = []
    for d in WORK_ROOT.iterdir() if WORK_ROOT.exists() else []:
        if not d.is_dir():
            continue
        mp = d / "manifest.json"
        if not mp.exists():
            continue
        try:
            m = Manifest(d)
        except Exception:  # noqa: BLE001
            continue
        req = m.data.get("request") or {}
        if req.get("group_id") != group_id:
            continue
        members.append((int(req.get("group_index") or 9999), d.name, req))
    members.sort(key=lambda t: (t[0], t[1]))
    n = len(members)
    gt = title
    if gt is None and members:
        gt = members[0][2].get("group_title") or "Series"
    out: list[str] = []
    for i, (_, jid, req) in enumerate(members, 1):
        _patch_job_group(
            jid, group_id=group_id, group_title=gt,
            group_index=i, group_total=n,
            part_title=req.get("part_title"),
        )
        out.append(jid)
    return out


def jobs_group(body: JobGroupReq):
    """Gom job thành series / thêm vào nhóm / đổi tên / tách."""
    act = (body.action or "create").strip().lower()
    ids = [str(x).strip() for x in (body.job_ids or []) if str(x).strip()]
    gid = (body.group_id or "").strip() or None
    title = (body.title or "").strip() or None

    if act == "create":
        if len(ids) < 1:
            return JSONResponse({"error": "chọn ≥1 job để gom nhóm"}, status_code=400)
        # Lọc id tồn tại
        ids = [i for i in ids if (WORK_ROOT / i / "manifest.json").exists()]
        if not ids:
            return JSONResponse({"error": "không thấy job hợp lệ"}, status_code=404)
        gt = title or "Series"
        # lấy title từ job đầu nếu user không đặt
        if not title:
            try:
                m0 = Manifest(WORK_ROOT / ids[0])
                gt = (m0.data.get("title_vi")
                      or (m0.stage("download") or {}).get("title")
                      or (m0.data.get("request") or {}).get("title")
                      or "Series")
            except Exception:  # noqa: BLE001
                gt = "Series"
        new_gid = hashlib.sha1(
            f"manual:{gt}:{time.time()}:{','.join(ids)}".encode("utf-8")
        ).hexdigest()[:10]
        for i, jid in enumerate(ids, 1):
            # bỏ khỏi nhóm cũ nếu có
            m = Manifest(WORK_ROOT / jid)
            old = (m.data.get("request") or {}).get("group_id")
            _patch_job_group(
                jid, group_id=new_gid, group_title=gt,
                group_index=i, group_total=len(ids),
            )
            if old and old != new_gid:
                _renumber_group(old)
        return {"ok": True, "action": "create", "group_id": new_gid,
                "group_title": gt, "job_ids": ids, "count": len(ids)}

    if act == "add":
        if not gid:
            return JSONResponse({"error": "thiếu group_id"}, status_code=400)
        if not ids:
            return JSONResponse({"error": "chọn job để thêm vào nhóm"}, status_code=400)
        # lấy title hiện có
        gt = title
        if not gt:
            for d in WORK_ROOT.iterdir() if WORK_ROOT.exists() else []:
                if not (d / "manifest.json").exists():
                    continue
                m = Manifest(d)
                req = m.data.get("request") or {}
                if req.get("group_id") == gid:
                    gt = req.get("group_title") or "Series"
                    break
        gt = gt or "Series"
        for jid in ids:
            if not (WORK_ROOT / jid / "manifest.json").exists():
                continue
            m = Manifest(WORK_ROOT / jid)
            old = (m.data.get("request") or {}).get("group_id")
            # tạm gắn, renumber sau
            _patch_job_group(jid, group_id=gid, group_title=gt, group_index=9999, group_total=9999)
            if old and old != gid:
                _renumber_group(old)
        members = _renumber_group(gid, gt)
        return {"ok": True, "action": "add", "group_id": gid,
                "group_title": gt, "job_ids": members, "count": len(members)}

    if act == "rename":
        if not gid:
            return JSONResponse({"error": "thiếu group_id"}, status_code=400)
        if not title:
            return JSONResponse({"error": "thiếu title"}, status_code=400)
        members = _renumber_group(gid, title)
        if not members:
            return JSONResponse({"error": "không thấy nhóm"}, status_code=404)
        return {"ok": True, "action": "rename", "group_id": gid,
                "group_title": title, "count": len(members)}

    if act == "ungroup":
        if not ids:
            return JSONResponse({"error": "chọn job để tách"}, status_code=400)
        touched: set[str] = set()
        for jid in ids:
            if not (WORK_ROOT / jid / "manifest.json").exists():
                continue
            m = Manifest(WORK_ROOT / jid)
            old = (m.data.get("request") or {}).get("group_id")
            _patch_job_group(jid, group_id=None)
            if old:
                touched.add(old)
        for og in touched:
            _renumber_group(og)
        return {"ok": True, "action": "ungroup", "job_ids": ids}

    if act == "dissolve":
        if not gid:
            return JSONResponse({"error": "thiếu group_id"}, status_code=400)
        removed: list[str] = []
        for d in list(WORK_ROOT.iterdir()) if WORK_ROOT.exists() else []:
            if not (d / "manifest.json").exists():
                continue
            m = Manifest(d)
            req = m.data.get("request") or {}
            if req.get("group_id") == gid:
                _patch_job_group(d.name, group_id=None)
                removed.append(d.name)
        return {"ok": True, "action": "dissolve", "group_id": gid, "job_ids": removed}

    return JSONResponse({"error": f"action '{act}' không hỗ trợ"}, status_code=400)


def api_queue_jobs_add(req: JobQueueReq):
    ids = [str(x).strip() for x in (req.job_ids or []) if str(x).strip()]
    if not ids:
        return JSONResponse({"error": "chọn ≥1 job"}, status_code=400)
    # Trường client không gửi lấy theo config batch (không phải mặc định cứng voice_bgm/0.6/8M của model)
    opts = batch_config.resolve_job_opts(
        req.model_dump(exclude_unset=True, exclude={"job_ids", "skip_done", "opts"}),
        req.opts if isinstance(req.opts, dict) else None,
        fill_voice=False,
    )
    try:
        return job_queue.queue_add(ids, opts=opts, skip_done=bool(req.skip_done))
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=400)


def api_queue_jobs_add_group(req: JobQueueGroupReq):
    gid = (req.group_id or "").strip()
    if not gid:
        return JSONResponse({"error": "thiếu group_id"}, status_code=400)
    opts = batch_config.resolve_job_opts(req.model_dump(exclude_unset=True, exclude={"group_id", "skip_done"}),
                                         fill_voice=False)
    try:
        r = job_queue.queue_add_group(gid, opts=opts, skip_done=bool(req.skip_done))
        if not r.get("ok") and r.get("error"):
            return JSONResponse(r, status_code=400)
        return r
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=400)


def api_queue_jobs_opts(body: dict):
    """{"opts_by_job": {job_id: opts}} — đổi opts job đang chờ tại chỗ (nguyên tử, giữ thứ tự)."""
    raw = body.get("opts_by_job") if isinstance(body, dict) else None
    if not isinstance(raw, dict) or not raw:
        return JSONResponse({"error": "thiếu opts_by_job"}, status_code=400)
    skip = {"job_ids", "skip_done", "opts"}
    fields = set(JobQueueReq.model_fields) - skip
    updates: dict[str, dict] = {}
    try:
        for jid, o in raw.items():
            if not isinstance(o, dict):
                continue
            req = JobQueueReq(job_ids=[str(jid)], **{k: v for k, v in o.items() if k in fields})
            updates[str(jid)] = batch_config.resolve_job_opts(
                req.model_dump(exclude_unset=True, exclude=skip), fill_voice=False)
        return job_queue.queue_update_opts(updates)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=400)


def api_queue_jobs_remove(req: JobQueueRemoveReq):
    try:
        return job_queue.queue_remove(req.job_ids or [])
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=400)


def _queue_current_detail(job_id: str | None) -> dict | None:
    """Alias → job_queue.current_detail (giữ tên cũ cho test/monkeypatch)."""
    return job_queue.current_detail(job_id, work_root=WORK_ROOT)


def api_queue_jobs_sort(body: dict | None = None):
    by = (body or {}).get("by") if isinstance(body, dict) else "series_season"
    try:
        return job_queue.queue_sort(by=by or "series_season")
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=400)


def api_queue_jobs_move(body: dict):
    if not isinstance(body, dict):
        return JSONResponse({"error": "body phải là json object"}, status_code=400)
    jid = str(body.get("job_id") or "").strip()
    action = str(body.get("action") or "").strip()
    if not jid:
        return JSONResponse({"error": "thiếu job_id"}, status_code=400)
    if action not in ("top", "up", "down", "bottom"):
        return JSONResponse({"error": "action phải là top|up|down|bottom"}, status_code=400)
    try:
        return job_queue.queue_move(jid, action)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=400)


def api_queue_jobs_reorder(body: dict):
    if not isinstance(body, dict):
        return JSONResponse({"error": "body phải là json object"}, status_code=400)
    order = body.get("order")
    if not isinstance(order, list):
        return JSONResponse({"error": "thiếu mảng order"}, status_code=400)
    try:
        return job_queue.queue_reorder(order)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=400)


def api_queue_jobs_state():
    return job_queue.http_queue_state(work_root=WORK_ROOT)


def api_queue_jobs_stop():
    return job_queue.queue_stop()


def api_queue_jobs_clear():
    return job_queue.queue_clear()


def create_local_job_path(body: LocalJobIn):
    """Tạo job từ file HOẶC folder video local.
    Folder: quét *.mp4/mkv/webm/mov → nhiều job; ≥2 file → gom group theo tên folder.
    """
    raw = body.path.strip().strip('"')
    try:
        src = Path(raw).expanduser().resolve(strict=True)
    except FileNotFoundError:
        return JSONResponse({"error": f"không thấy path: {body.path}"}, status_code=400)
    except OSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)

    if src.is_file():
        r = _import_local_video_file(
            src, target=body.target, move=body.move, title=body.title,
        )
        if not r.get("ok"):
            return JSONResponse({"error": r.get("error") or "lỗi"}, status_code=400)
        return {"ok": True, "job_ids": [r["job_id"]], "job_id": r["job_id"], "count": 1, **r}

    if not src.is_dir():
        return JSONResponse({"error": "path không phải file/folder"}, status_code=400)

    videos = _list_local_videos(src, recursive=bool(body.recursive), limit=500)
    if not videos:
        return JSONResponse(
            {"error": f"folder không có video ({', '.join(sorted(_VIDEO_EXT))}): {src}"},
            status_code=400,
        )

    group = None
    if body.group_folder and len(videos) > 1:
        gid = hashlib.sha1(str(src).encode("utf-8")).hexdigest()[:10]
        group = {
            "group_id": gid,
            "group_title": body.title or src.name,
            "group_total": len(videos),
        }

    job_ids: list[str] = []
    errors: list[str] = []
    for i, vp in enumerate(videos, 1):
        g = None
        if group:
            g = {**group, "group_index": i, "part_title": vp.stem}
        r = _import_local_video_file(
            vp, target=body.target, move=body.move, title=vp.stem, group=g,
        )
        if r.get("ok") and r.get("job_id"):
            job_ids.append(r["job_id"])
        else:
            errors.append(f"{vp.name}: {r.get('error') or 'fail'}")

    if not job_ids:
        return JSONResponse(
            {"error": "không tạo được job nào", "details": errors[:10]},
            status_code=400,
        )
    return {
        "ok": True,
        "job_ids": job_ids,
        "job_id": job_ids[0],
        "count": len(job_ids),
        "folder": str(src),
        "group": bool(group),
        "group_title": (group or {}).get("group_title"),
        "errors": errors[:20] or None,
    }


def create_local_job_batch(body: LocalBatchIn):
    """Import nhiều path (file + folder). Mỗi folder → 1 group riêng."""
    paths = [p.strip().strip('"') for p in (body.paths or []) if p and p.strip()]
    if not paths:
        return JSONResponse({"error": "paths trống"}, status_code=400)
    max_files = max(1, min(2000, int(body.max_files or 500)))
    all_ids: list[str] = []
    folders: list[dict] = []
    errors: list[str] = []
    n_files = 0
    for raw in paths:
        try:
            src = Path(raw).expanduser().resolve(strict=True)
        except (FileNotFoundError, OSError) as e:
            errors.append(f"{raw}: {e}")
            continue
        if src.is_file():
            if n_files >= max_files:
                errors.append(f"đạt max_files={max_files}, bỏ qua còn lại")
                break
            r = _import_local_video_file(
                src, target=body.target, move=body.move, title=src.stem,
            )
            n_files += 1
            if r.get("ok") and r.get("job_id"):
                all_ids.append(r["job_id"])
            else:
                errors.append(f"{src.name}: {r.get('error') or 'fail'}")
            continue
        if not src.is_dir():
            errors.append(f"{raw}: không phải file/folder")
            continue
        remain = max_files - n_files
        if remain <= 0:
            errors.append(f"đạt max_files={max_files}, bỏ qua {src}")
            break
        videos = _list_local_videos(src, recursive=bool(body.recursive), limit=remain)
        if not videos:
            errors.append(f"{src}: không có video")
            continue
        group = None
        if body.group_folder and len(videos) > 1:
            gid = hashlib.sha1(str(src).encode("utf-8")).hexdigest()[:10]
            group = {
                "group_id": gid,
                "group_title": src.name,
                "group_total": len(videos),
            }
        folder_ids: list[str] = []
        for i, vp in enumerate(videos, 1):
            g = {**group, "group_index": i, "part_title": vp.stem} if group else None
            r = _import_local_video_file(
                vp, target=body.target, move=body.move, title=vp.stem, group=g,
            )
            n_files += 1
            if r.get("ok") and r.get("job_id"):
                folder_ids.append(r["job_id"])
                all_ids.append(r["job_id"])
            else:
                errors.append(f"{vp.name}: {r.get('error') or 'fail'}")
        folders.append({
            "folder": str(src),
            "count": len(folder_ids),
            "group_id": (group or {}).get("group_id"),
            "group_title": (group or {}).get("group_title"),
            "job_ids": folder_ids,
        })
    if not all_ids:
        return JSONResponse(
            {"error": "không tạo được job nào", "details": errors[:20]},
            status_code=400,
        )
    return {
        "ok": True,
        "job_ids": all_ids,
        "job_id": all_ids[0],
        "count": len(all_ids),
        "folders": folders,
        "errors": errors[:30] or None,
    }


def api_fs_list_dirs(
    path: str = Query(..., description="Thư mục gốc, vd D:\\Lib"),
    count_videos: bool = Query(True),
    only_with_video: bool = Query(False),
):
    """Liệt kê folder con trực tiếp (1 cấp) để tick chọn import.
    Ví dụ path=D:\\Lib → 万妖图录传第一季 … 第四季 + số video mỗi folder.
    """
    raw = (path or "").strip().strip('"')
    if not raw:
        return JSONResponse({"error": "path trống"}, status_code=400)
    try:
        root = Path(raw).expanduser().resolve(strict=True)
    except FileNotFoundError:
        return JSONResponse({"error": f"không thấy: {path}"}, status_code=404)
    except OSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    if not root.is_dir():
        return JSONResponse({"error": "không phải thư mục"}, status_code=400)

    def _nat_key(name: str):
        import re as _re
        parts = _re.split(r"(\d+)", name.lower())
        return [int(x) if x.isdigit() else x for x in parts]

    dirs: list[dict] = []
    try:
        children = [p for p in root.iterdir() if p.is_dir()]
    except OSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    children.sort(key=lambda p: _nat_key(p.name))
    for d in children:
        n_vid = None
        if count_videos:
            try:
                n_vid = len(_list_local_videos(d, recursive=True, limit=500))
            except Exception:  # noqa: BLE001
                n_vid = 0
            if only_with_video and not n_vid:
                continue
        dirs.append({
            "name": d.name,
            "path": str(d),
            "videos": n_vid,
        })
    return {
        "ok": True,
        "root": str(root),
        "count": len(dirs),
        "dirs": dirs,
    }


def api_fs_pick_dir(
    title: str = Query("Chọn thư mục", description="Tiêu đề hộp thoại"),
    initial: str | None = Query(None, description="Thư mục mở sẵn, vd D:\\Lib"),
):
    """Mở hộp thoại Windows chọn folder (native). Chạy process riêng để không kẹt uvicorn."""
    import subprocess
    import sys
    import tempfile

    init = (initial or "").strip().strip('"')
    if init:
        try:
            p0 = Path(init).expanduser()
            if p0.is_dir():
                init = str(p0.resolve())
            else:
                init = ""
        except OSError:
            init = ""

    # Script nhỏ: tkinter askdirectory → in path ra stdout
    script = (
        "import sys\n"
        "from pathlib import Path\n"
        "import tkinter as tk\n"
        "from tkinter import filedialog\n"
        f"title = {title!r}\n"
        f"initial = {init!r}\n"
        "root = tk.Tk()\n"
        "root.withdraw()\n"
        "try:\n"
        "    root.attributes('-topmost', True)\n"
        "except Exception:\n"
        "    pass\n"
        "root.update()\n"
        "kw = {'title': title, 'mustexist': True}\n"
        "if initial:\n"
        "    kw['initialdir'] = initial\n"
        "path = filedialog.askdirectory(**kw)\n"
        "root.destroy()\n"
        "sys.stdout.write(path or '')\n"
    )
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(script)
            tmp = f.name
        r = subprocess.run(
            [sys.executable, tmp],
            capture_output=True,
            text=True,
            timeout=300,
        )
        try:
            Path(tmp).unlink(missing_ok=True)
        except OSError:
            pass
    except subprocess.TimeoutExpired:
        return JSONResponse({"error": "hết thời gian chờ chọn folder"}, status_code=408)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": f"không mở được dialog: {e}"}, status_code=500)

    path = (r.stdout or "").strip()
    if not path:
        return {"ok": False, "cancelled": True, "path": None}
    try:
        p = Path(path).resolve(strict=True)
    except (FileNotFoundError, OSError) as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    if not p.is_dir():
        return JSONResponse({"error": "không phải thư mục"}, status_code=400)
    return {"ok": True, "path": str(p), "name": p.name}


def api_fs_pick_dirs(
    initial: str | None = Query(None, description="Root mở sẵn, vd D:\\Lib"),
):
    """Hộp thoại chọn NHIỀU folder cùng lúc (Ctrl/Shift). Trả paths[]."""
    import subprocess
    import sys

    init = (initial or "").strip().strip('"') or "D:\\Lib"
    try:
        p0 = Path(init).expanduser()
        if p0.is_dir():
            init = str(p0.resolve())
    except OSError:
        init = "D:\\Lib"

    script = Path(__file__).resolve().parent / "tools" / "pick_dirs_dialog.py"
    if not script.is_file():
        return JSONResponse({"error": f"thiếu {script.name}"}, status_code=500)
    try:
        r = subprocess.run(
            [sys.executable, str(script), init],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )
    except subprocess.TimeoutExpired:
        return JSONResponse({"error": "hết thời gian chờ chọn folder"}, status_code=408)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": f"không mở được dialog: {e}"}, status_code=500)

    if r.returncode not in (0, None) and not (r.stdout or "").strip():
        err = (r.stderr or "").strip()[:300]
        return JSONResponse({"error": err or "dialog lỗi"}, status_code=500)

    paths: list[str] = []
    for line in (r.stdout or "").splitlines():
        s = line.strip().strip('"')
        if not s:
            continue
        try:
            p = Path(s).resolve(strict=True)
        except (FileNotFoundError, OSError):
            continue
        if p.is_dir():
            paths.append(str(p))
    # unique keep order
    seen: set[str] = set()
    uniq: list[str] = []
    for p in paths:
        if p in seen:
            continue
        seen.add(p)
        uniq.append(p)
    if not uniq:
        return {"ok": False, "cancelled": True, "paths": [], "count": 0}
    return {
        "ok": True,
        "paths": uniq,
        "count": len(uniq),
        "names": [Path(p).name for p in uniq],
    }


async def create_local_job_upload(
    file: UploadFile = File(...),
    target: str = Form("Tiếng Việt"),
):
    """Tạo job từ upload video (không cần link). File lớn nên dùng /local-path."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in _VIDEO_EXT:
        return JSONResponse(
            {"error": f"định dạng {ext or '?'} không hỗ trợ (dùng {', '.join(sorted(_VIDEO_EXT))})"},
            status_code=400,
        )
    title = Path(file.filename or "video").stem
    job_key = f"upload:{file.filename}:{time.time_ns()}"
    job_id, work_dir = _create_local_shell(target, job_key=job_key, title=title)
    _clear_job_sources(work_dir)
    dest = work_dir / f"source{ext}"
    try:
        with dest.open("wb") as out:
            while True:
                chunk = await file.read(8 * 1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
    except Exception as e:  # noqa: BLE001
        try:
            dest.unlink(missing_ok=True)
        except OSError:
            pass
        return JSONResponse({"error": f"ghi file lỗi: {e}"}, status_code=500)
    if not dest.exists() or dest.stat().st_size < 1024:
        return JSONResponse({"error": "file rỗng / quá nhỏ"}, status_code=400)
    info = _finalize_imported_source(
        work_dir, dest, orig_name=file.filename, source_kind="imported_upload",
    )
    return {"ok": True, "job_ids": [job_id], "job_id": job_id, "count": 1, **info}


def start_job(job_id: str):
    """Chạy tự động các bước còn lại (download -> asr -> dịch) cho 1 job.

    Nếu ĐÃ tải xong -> nhảy thẳng sang hàng đợi GPU (ASR/dịch), KHÔNG chiếm hàng
    đợi tải nữa (tránh kẹt phía sau các job đang tải dở)."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    m = Manifest(work_dir)
    req = m.data.get("request", {})
    target = req.get("target", "Tiếng Việt")
    busy = _job_any_busy(job_id) or _manifest_running(work_dir)
    if busy:
        return JSONResponse(
            {"error": f"job đang chạy bước '{busy}' — bấm Dừng hoặc đợi xong"},
            status_code=409,
        )
    if not _claim_stage(job_id, "__all__"):
        return JSONResponse({"error": "đã nhận lệnh trước đó — không gửi trùng"}, status_code=409)
    _clear_stop(job_id)

    # Đánh dấu running NGAY — nhưng KHÔNG đè stage đã done (tránh UI báo
    # 'đang nhận diện' trong khi TTS đang chạy / ASR bị spawn lại).
    asr_ok = (work_dir / "asr.json").exists()
    script_ok = (work_dir / "script.json").exists()
    try:
        if not _find_video(work_dir):
            early = "download"
        elif not asr_ok:
            early = "asr"
        elif not script_ok and not m.is_done("translate"):
            early = "translate"
        else:
            early = None  # ASR+dịch đã có → không mark giả
        if early:
            m.mark_running(early)
    except Exception:  # noqa: BLE001
        pass

    def _wrapped_start():
        try:
            if job_id in _STOP_JOBS:
                print(f"[start] {job_id}: đã DỪNG — bỏ qua")
                return
            if _find_video(work_dir):
                # Đã có asr+script → không xếp lại hàng GPU (tránh đè TTS)
                if asr_ok and script_ok:
                    print(f"[start] {job_id}: ASR+dịch đã có — bỏ qua _process_gpu")
                    return
                _process_gpu(job_id, target)
            else:
                url = req.get("url")
                if not url:
                    raise RuntimeError("job local chưa có source — import file trước")
                run_pipeline(job_id, url, target, req.get("cookies_from_browser"))
        finally:
            _release_stage(job_id, "__all__")

    if _find_video(work_dir):
        if asr_ok and script_ok:
            _release_stage(job_id, "__all__")
            return {"started": True, "skipped": "asr+translate already done"}
        _gpu.submit(_wrapped_start)
        return {"started": True}
    url = req.get("url")
    if not url:
        _release_stage(job_id, "__all__")
        return JSONResponse(
            {"error": "job local chưa có source — import file trước"},
            status_code=400,
        )
    _dl.submit(_wrapped_start)
    return {"started": True}


def _run_stage(job_id: str, stage: str, target: str, force: bool,
               voice: str | None = None, speed: float | None = None,
               engine: str | None = None):
    """Chạy ĐÚNG 1 bước (người dùng tự chọn). download -> hàng _dl; còn lại -> _gpu."""
    work_dir = WORK_ROOT / job_id
    _clear_stop(job_id)          # bắt đầu chạy -> xoá cờ dừng cũ
    try:
        if stage == "download":
            req = Manifest(work_dir).data.get("request", {})
            url = req.get("url")
            if not url:
                raise RuntimeError(
                    "Job local — không có URL. Dùng Import source / Path thay vì Chạy tải."
                )
            # force=True ở bước download nghĩa là TẢI LẠI TỪ ĐẦU (xoá data cũ hỏng).
            download_video(url, work_dir,
                           cookies_from_browser=req.get("cookies_from_browser"), fresh=force)
        elif stage == "asr":
            # engine param = ASR engine (fun_asr_nano | sensevoice | …)
            free_gpu_vram("trước ASR — nhường GPU")
            asr_eng = _resolve_asr_engine(work_dir, engine)
            _run_engine(_asr_script(asr_eng), work_dir, *(["--force"] if force else []))
        elif stage == "translate":
            # CASCADE RESET: Reset TTS & MUX de khong hien thi done cu
            m_curr = Manifest(work_dir)
            stg = m_curr.data.setdefault("stages", {})
            if "tts" in stg and stg["tts"].get("status") == "done":
                stg["tts"]["status"] = "pending"
                stg["tts"]["cur_text"] = "Chờ bản dịch mới"
            if "mux" in stg and stg["mux"].get("status") in ("done", "running"):
                stg["mux"]["status"] = "pending"
                stg["mux"]["cur_text"] = "Chờ lồng tiếng mới"
            m_curr.save()
            _run_translate_engine(work_dir, target=target, force=force)
        elif stage == "tts":
            m_curr = Manifest(work_dir)
            tr_st = (m_curr.stage("translate") or {}).get("status")
            if tr_st in ("running", "pending"):
                print(f"[stage tts] CHẶN: translate đang '{tr_st}' -> không chạy tts song song", flush=True)
                return
            free_gpu_vram("trước TTS để nhường GPU")
            eng = _resolve_tts_engine(work_dir, engine)
            v = _resolve_voice(work_dir, voice)
            if not v:
                print(f"[stage tts] job {job_id}: chưa có giọng -> bỏ qua", flush=True)
                return
            sp = _resolve_speed(work_dir, speed)
            _do_tts(work_dir, v, sp, eng, force)
        elif stage == "ocr":
            free_gpu_vram("trước OCR")
            run_ocr(work_dir, force=force)
        elif stage == "separate":
            free_gpu_vram("trước tách nền")
            run_separate(work_dir, force=force)
        elif stage == "mux":
            m_curr = Manifest(work_dir)
            tr_st = (m_curr.stage("translate") or {}).get("status")
            tts_st = (m_curr.stage("tts") or {}).get("status")
            if tr_st in ("running", "pending"):
                print(f"[stage mux] CHẶN: translate đang '{tr_st}' -> không chạy mux song song", flush=True)
                return
            if tts_st in ("running", "pending"):
                print(f"[stage mux] CHẶN: tts đang '{tts_st}' -> không chạy mux khi chưa lồng tiếng xong", flush=True)
                return
            free_gpu_vram("trước render")
            qo = Manifest(work_dir).data.get("queue_opts") or {}
            _do_render(work_dir, force=force, **batch_config.render_kwargs(batch_config.resolve_job_opts(qo)))
    except _Stopped:
        print(f"[stage {stage}] job {job_id}: đã DỪNG theo yêu cầu")
    except Exception as e:  # noqa: BLE001
        print(f"[stage {stage}] job {job_id} lỗi: {e}")


def _save_tts_voice(work_dir: Path, voice: str) -> None:
    """Lưu giọng vào manifest + sidecar — KHÔNG được wipe stages khác."""
    _patch_tts_fields(work_dir, voice=voice)


def _save_tts_speed(work_dir: Path, speed: float) -> None:
    _patch_tts_fields(work_dir, speed=float(speed))


def _save_tts_engine(work_dir: Path, engine: str) -> None:
    _patch_tts_fields(work_dir, tts_engine=engine, engine=engine)


def _patch_tts_fields(work_dir: Path, **fields) -> None:
    """Ghi field TTS an toàn: đọc đĩa trực tiếp, merge, atomic write. Không dùng
    Manifest() khi load fail (tránh save data rỗng xoá cả job)."""
    path = Path(work_dir) / "manifest.json"
    if not path.exists():
        return

    got: dict = {}

    def _apply(data: dict):
        st_ = data["stages"].setdefault("tts", {})
        changed = False
        for k, v in fields.items():
            if v is not None and st_.get(k) != v:
                st_[k] = v
                changed = True
        got.update(st_)
        return changed

    try:
        if not Manifest(work_dir).update(_apply) and not got:
            return
    except Exception as e:  # noqa: BLE001
        print(f"[tts-config] ghi fail: {e}")
        return
    st = got
    # Sidecar backup — sống sót nếu manifest bị đụng
    try:
        side = Path(work_dir) / "tts_config.json"
        cur = {}
        if side.exists():
            try:
                cur = json.loads(side.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                cur = {}
        for k in ("voice", "speed", "tts_engine", "engine"):
            if k in st and st[k] is not None:
                cur[k] = st[k]
        side.write_text(json.dumps(cur, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass


def _job_cfg_opts(work_dir: Path) -> dict:
    """Gộp opts + queue_opts (queue_opts thắng) — resolve voice/speed/engine."""
    try:
        m = Manifest(work_dir)
        opts = dict(m.data.get("opts") or {})
        qo = dict(m.data.get("queue_opts") or {})
        return {**opts, **qo}
    except Exception:  # noqa: BLE001
        return {}


def _resolve_voice(work_dir: Path, voice: str | None) -> str:
    """Giọng: arg → stages.tts → tts_config → queue_opts/opts → list[0]."""
    if voice:
        _save_tts_voice(work_dir, voice)
        return voice
    st = Manifest(work_dir).stage("tts") or {}
    if st.get("voice"):
        return st["voice"]
    side = Path(work_dir) / "tts_config.json"
    if side.exists():
        try:
            v = json.loads(side.read_text(encoding="utf-8")).get("voice")
            if v:
                _save_tts_voice(work_dir, v)
                return v
        except Exception:  # noqa: BLE001
            pass
    v = (_job_cfg_opts(work_dir).get("voice") or "").strip()
    if v:
        _save_tts_voice(work_dir, v)
        return v
    avail = list_clone_voices()
    return avail[0] if avail else ""


def _resolve_queue_voice(work_dir: Path, voice: str | None) -> str:
    """Queue chỉ dùng giọng được chọn rõ ràng hoặc đã lưu cho chính job."""
    if voice:
        _save_tts_voice(work_dir, voice)
        return voice
    st = Manifest(work_dir).stage("tts") or {}
    if st.get("voice"):
        return st["voice"]
    side = Path(work_dir) / "tts_config.json"
    if side.exists():
        try:
            saved = json.loads(side.read_text(encoding="utf-8")).get("voice")
            if saved:
                _save_tts_voice(work_dir, saved)
                return saved
        except Exception:  # noqa: BLE001
            pass
    v = (_job_cfg_opts(work_dir).get("voice") or "").strip()
    if v:
        _save_tts_voice(work_dir, v)
        return v
    return ""


def _resolve_speed(work_dir: Path, speed: float | None) -> float:
    if speed and speed > 0:
        _save_tts_speed(work_dir, speed)
        return speed
    st = Manifest(work_dir).stage("tts") or {}
    if st.get("speed"):
        return float(st["speed"])
    side = Path(work_dir) / "tts_config.json"
    if side.exists():
        try:
            sp = json.loads(side.read_text(encoding="utf-8")).get("speed")
            if sp:
                return float(sp)
        except Exception:  # noqa: BLE001
            pass
    sp = _job_cfg_opts(work_dir).get("speed")
    try:
        if sp is not None and float(sp) > 0:
            _save_tts_speed(work_dir, float(sp))
            return float(sp)
    except (TypeError, ValueError):
        pass
    return 1.0


TTS_ENGINES = ("vieneu", "omnivoice")
TTS_ENGINE_DEFAULT = "vieneu"

# ASR: Nano+Direct FA (SOTA chuẩn V2) | Hybrid | Nano | SenseVoice | Paraformer | FireRed
ASR_ENGINES = ("nano_fa", "hybrid_fa", "fun_asr_nano", "sensevoice", "paraformer_zh", "firered_asr")
ASR_ENGINE_DEFAULT = "nano_fa"  # Fun-ASR-Nano + Direct Qwen3-ForcedAligner
ASR_SCRIPTS = {
    "nano_fa": "engines/asr/nano_fa_asr.py",
    "hybrid_fa": "engines/asr/hybrid_asr.py",
    "fun_asr_nano": "engines/asr/fun_asr_nano.py",
    "sensevoice": "engines/asr/sensevoice_asr.py",
    "paraformer_zh": "engines/asr/paraformer_zh.py",
    "firered_asr": "engines/asr/firered_asr.py",
}


def _asr_script(engine: str) -> str:
    return ASR_SCRIPTS.get(engine, ASR_SCRIPTS[ASR_ENGINE_DEFAULT])


def _patch_asr_fields(work_dir: Path, **fields) -> None:
    """Ghi field ASR an toàn (không wipe stages khác).

    `model=""` (chuỗi rỗng) → xoá model cũ (tránh sót FireRed khi chọn Nano).
    """
    path = Path(work_dir) / "manifest.json"
    if not path.exists():
        return

    def _apply(data: dict):
        st = data["stages"].setdefault("asr", {})
        changed = False
        for k, v in fields.items():
            if v is None:
                continue
            if v == "" and k in st:
                del st[k]
                changed = True
                continue
            if v != "" and st.get(k) != v:
                st[k] = v
                changed = True
        return changed

    try:
        if not Manifest(work_dir).update(_apply):
            return
    except Exception as e:  # noqa: BLE001
        print(f"[asr-config] ghi lỗi: {e}")
        return
    _job_cache.pop(str(work_dir), None)


def _save_asr_engine(work_dir: Path, engine: str) -> None:
    """Lưu engine. Nếu đã có sidecar tương ứng → promote luôn (tránh lệch nhãn/nội dung)."""
    map_src = {
        "nano_fa": "asr.nano_fa.json",
        "fun_asr_nano": "asr.fun_nano.json",
        "firered_asr": "asr.firered.json",
        "paraformer_zh": "asr.paraformer_zh.json",
        "sensevoice": "asr.sensevoice.json",
        "hybrid_fa": "asr.aligned_fa.json",
    }
    src = map_src.get(engine)
    if src and (work_dir / src).exists():
        try:
            _promote_asr_source(work_dir, src)
            return
        except Exception as e:  # noqa: BLE001
            print(f"[asr-engine] promote {src} lỗi: {e} → chỉ lưu engine", flush=True)
    elif engine == "hybrid_fa":
        for alt in ("asr.aligned_fa.json", "asr.aligned_repaired.json",
                    "asr.aligned.json", "asr.consensus.json"):
            if (work_dir / alt).exists():
                try:
                    _promote_asr_source(work_dir, alt)
                    return
                except Exception:  # noqa: BLE001
                    break
    _patch_asr_fields(work_dir, asr_engine=engine, engine=engine)



def _run_translate_engine(
    work_dir: Path,
    batch: int | None = None,
    target: str | None = None,
    force: bool = False,
    model: str | None = None,
    mode: str | None = None,
    review_only: bool = False,
    review_force: bool = False,
) -> None:
    """Chạy stage dịch ở TIẾN TRÌNH RIÊNG (subprocess) giống như ASR và TTS.
    
    Tách ra subprocess:
    - Web server hoàn toàn rảnh GIL -> API và UI siêu mượt, không bao giờ bị khựng.
    - Dễ dàng stop/kill tiến trình ngay lập tức khi người dùng bấm Dừng.
    - Bộ nhớ và VRAM tự động giải phóng sạch sẽ khi tiến trình kết thúc.
    """
    args = []
    if batch:
        args.extend(["--batch", str(batch)])
    if target:
        args.extend(["--target", str(target)])
    if force:
        args.append("--force")
    if model:
        args.extend(["--model", str(model)])
    if mode:
        args.extend(["--mode", str(mode)])
    if review_only:
        args.append("--review")
    if review_force:
        args.append("--review-force")
    _run_engine("engines/translate.py", work_dir, *args)


def _resolve_asr_engine(work_dir: Path, engine: str | None) -> str:
    if engine in ASR_ENGINES:
        _save_asr_engine(work_dir, engine)
        return engine
    st = Manifest(work_dir).stage("asr") or {}
    saved = st.get("asr_engine") or st.get("engine")
    if saved in ASR_ENGINES:
        return saved
    # engine cũ đã gỡ (whisper / qwen3_asr) → mặc định
    return ASR_ENGINE_DEFAULT


def _resolve_tts_engine(work_dir: Path, engine: str | None) -> str:
    if engine in TTS_ENGINES:
        _save_tts_engine(work_dir, engine)
        return engine
    st = Manifest(work_dir).stage("tts") or {}
    saved = st.get("tts_engine") or st.get("engine")
    if saved in TTS_ENGINES:
        return saved
    side = Path(work_dir) / "tts_config.json"
    if side.exists():
        try:
            e = json.loads(side.read_text(encoding="utf-8"))
            saved = e.get("tts_engine") or e.get("engine")
            if saved in TTS_ENGINES:
                return saved
        except Exception:  # noqa: BLE001
            pass
    qo = _job_cfg_opts(work_dir)
    saved = qo.get("tts_engine") or qo.get("engine")
    if saved in TTS_ENGINES:
        _save_tts_engine(work_dir, saved)
        return saved
    return TTS_ENGINE_DEFAULT


def _do_tts(work_dir: Path, voice: str, speed: float, engine: str, force: bool):
    """Chạy TTS clone tiếng Việt (vieneu/omnivoice). Điều phối worker venv riêng
    (in-process) — orchestrator ghi tts.json + mark_done."""
    import time as _t
    # Thread GPU thật sự bắt đầu (không còn xếp hàng) — cập nhật UI khỏi "starting"
    try:
        _patch_tts_fields(work_dir, cur_text=f"{engine}: chuan bi (kiem tra python/voice)...",
                          updated_at=_t.time())
        _job_cache.pop(str(work_dir), None)
    except Exception:  # noqa: BLE001
        pass
    print(f"[tts] _do_tts START job={work_dir.name} engine={engine} voice={voice} force={force}",
          flush=True)
    run_clone_tts(work_dir, engine, voice, speed=speed, force=force)


def _do_render(work_dir: Path, force: bool = True, audio_mode: str = "voice_bgm",
               voice_vol: float = 0.2, orig_vol: float = 0.6, add_sub: bool = True,
               fit: bool = True, resolution: str = "source", flip: str = "",
               zoom: float = 1.12, motion: bool = True, lut: bool = True,
               grain: str = "weak", brand: bool = False, brand_text: str = "",
               frame: str = "off", brand_mode: str = "off", brand_logo: str = "off",
               vbitrate: str = "8M", speed_factor: float = 1.0):
    """Ghép giọng (assemble nếu chưa) rồi render video localize (che+sub+trộn nền).

    fit=True: khớp time (nén câu lố cho khớp phim). fit=False: giọng tốc độ tự nhiên
    (đặt tại mốc SRT, có thể lệch/đè nhưng nghe thoải mái).
    resolution: source = giữ gốc; 1080/1k = xuất Full HD.
    audio voice_bgm/voice_only: không dùng BGM gốc (an toàn bản quyền hơn demucs/duck)."""
    work_dir = Path(work_dir)
    out_mp4 = work_dir / "output.mp4"
    m_early = Manifest(work_dir)

    # Không mark running nếu sẽ skip — trước đây mark_running rồi run_render skip
    # → mux kẹt 'running' → 1-click 409 mãi.
    if (not force and m_early.is_done("mux") and out_mp4.exists()
            and out_mp4.stat().st_size > 1_000_000):
        tts_json = work_dir / "tts.json"
        dub = work_dir / "dub_fit.wav"
        dub_ok = dub.exists() and dub.stat().st_size > 1000
        stale_dub = False
        if tts_json.exists() and dub_ok:
            stale_dub = dub.stat().st_mtime < tts_json.stat().st_mtime
        if not stale_dub and dub_ok:
            print(f"[render] skip — mux đã done: {out_mp4}", flush=True)
            return

    m_early.mark_running("mux")
    try:
        st = m_early.data["stages"].get("mux", {})
        st["progress"] = 0
        st["phase"] = "prepare"
        st["updated_at"] = time.time()
        m_early.data["stages"]["mux"] = st
        m_early.save()
    except Exception:  # noqa: BLE001
        pass

    try:
        # Chọn chế độ Demucs mà CHƯA tách nền -> TỰ chạy Tách nền trước (đỡ phải nhớ
        # bấm bước riêng; chọn Demucs ở Render là ra đúng Demucs, không âm thầm ducking).
        if audio_mode in ("demucs_keep", "demucs_clean") and not (work_dir / "no_vocals.wav").exists():
            print(f"[render] chế độ {audio_mode} nhưng chưa tách nền -> tự chạy Demucs trước")
            try:
                st = m_early.data["stages"].get("mux", {})
                st["phase"] = "separate"
                st["updated_at"] = time.time()
                m_early.data["stages"]["mux"] = st
                m_early.save()
            except Exception:  # noqa: BLE001
                pass
            run_separate(work_dir)
        # Ghép lại dub_fit.wav nếu THIẾU hoặc CŨ HƠN tts.json (giọng vừa tạo lại) —
        # chặn bug render xài lại audio lỗi thời.
        # Video dài (>30 phút): assemble() naive KHÔNG ghi file — luôn dùng assemble_fit.
        tts_json = work_dir / "tts.json"
        if tts_json.exists():
            from engines.assemble import assemble, assemble_fit, NAIVE_MAX_SEC
            # Ước lượng độ dài từ clip cuối trong tts.json
            long_job = True
            try:
                clips = json.loads(tts_json.read_text(encoding="utf-8"))
                if clips:
                    long_job = float(max(c.get("end", 0) for c in clips)) > NAIVE_MAX_SEC
            except Exception:  # noqa: BLE001
                long_job = True
            use_fit = bool(fit) or long_job
            if long_job and not fit:
                print("[render] video dài: buộc ghép KHỚP TIME (naive không tạo dub_*.wav)",
                      flush=True)
            target = work_dir / ("dub_fit.wav" if use_fit else "dub_tts.wav")
            other = work_dir / ("dub_tts.wav" if use_fit else "dub_fit.wav")
            stale = (not target.exists()) or (target.stat().st_mtime < tts_json.stat().st_mtime)
            if stale:
                print(f"[render] ghép {'KHỚP TIME' if use_fit else 'TỰ NHIÊN'} -> {target.name}",
                      flush=True)
                try:
                    st = m_early.data["stages"].get("mux", {})
                    st["phase"] = "assemble"
                    st["updated_at"] = time.time()
                    m_early.data["stages"]["mux"] = st
                    m_early.save()
                except Exception:  # noqa: BLE001
                    pass
                (assemble_fit if use_fit else assemble)(work_dir)
                force = True     # dub vừa đổi -> BẮT BUỘC render lại (không trả output.mp4 cũ)
            if not target.exists() or target.stat().st_size < 1000:
                raise RuntimeError(
                    f"Chưa có track giọng Việt ({target.name}). "
                    "Ghép TTS thất bại — không render chỉ tiếng gốc.")
            try:
                other.unlink(missing_ok=True)   # bỏ bản kia để _pick_dub dùng đúng track
            except OSError:
                pass
        try:
            st = m_early.data["stages"].get("mux", {})
            st["phase"] = "encode"
            st["updated_at"] = time.time()
            m_early.data["stages"]["mux"] = st
            m_early.save()
        except Exception:  # noqa: BLE001
            pass
        # Reload mỗi lần mux — WrapStyle/CUT/config SUB_* đổi mà không cần restart server
        import importlib
        import core.config as _cfg_mod
        import engines.subs as _subs_mod
        import engines.render as _render_mod
        importlib.reload(_cfg_mod)
        importlib.reload(_subs_mod)
        _render_mod = importlib.reload(_render_mod)
        _render_mod.run_render(
            work_dir, force=force, audio_mode=audio_mode, voice_vol=voice_vol,
            orig_vol=orig_vol, add_sub=add_sub, resolution=resolution or "source",
            flip=flip or "", zoom=zoom, motion=motion, lut=lut, grain=grain,
            brand=bool(brand), brand_text=(brand_text or None),
            brand_mode=(brand_mode or None), brand_logo=(brand_logo or None),
            frame=(frame or None), vbitrate=(vbitrate or "8M"),
            speed_factor=speed_factor,
        )
        # Nếu run_render skip (done) sau khi ta đã mark_running → trả lại done
        m_chk = Manifest(work_dir)
        if ((m_chk.stage("mux") or {}).get("status") == "running"
                and out_mp4.exists() and out_mp4.stat().st_size > 1_000_000):
            prev = dict(m_chk.stage("mux") or {})
            keep = {k: v for k, v in prev.items()
                    if k not in ("status", "error", "cur_text", "started_at")}
            m_chk.data.setdefault("stages", {})["mux"] = {
                **keep, "status": "done", "finished_at": time.time(),
                "output_path": str(out_mp4),
            }
            m_chk.save()
    except Exception as e:  # noqa: BLE001
        try:
            Manifest(work_dir).mark_failed("mux", e)
        except Exception:  # noqa: BLE001
            pass
        raise


def run_stage(job_id: str, stage: str, force: bool = False, voice: str | None = None,
              speed: float | None = None, engine: str | None = None):
    """Chạy riêng 1 bước của job (chủ động chọn bước nào làm). Kiểm tra điều kiện
    tiên quyet trước; download đi hàng đợi tải, các bước GPU đi hàng đợi GPU."""
    if stage not in RUNNABLE_STAGES:
        return JSONResponse({"error": f"bước '{stage}' không hợp lệ"}, status_code=400)
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    m = Manifest(work_dir)
    # điều kiện tiên quyết: bước trước phải có kết quả
    if stage == "asr" and not _find_video(work_dir):
        return JSONResponse({"error": "chưa tải video xong"}, status_code=400)
    if stage == "translate" and not (work_dir / "asr.json").exists():
        return JSONResponse({"error": "chưa nhận diện lời (thiếu asr.json)"}, status_code=400)
    if stage == "ocr" and not _find_video(work_dir):
        return JSONResponse({"error": "chưa tải video xong"}, status_code=400)
    if stage == "separate" and not _find_video(work_dir):
        return JSONResponse({"error": "chưa tải video xong"}, status_code=400)
    # BỘ QUY TẮC BẢO VỆ PIPELINE V4: Khóa tuần tự nghiêm ngặt (Sequential Stage Guard)
    tr_status = (m.stage("translate") or {}).get("status")
    tts_status = (m.stage("tts") or {}).get("status")
    asr_status = (m.stage("asr") or {}).get("status")

    if stage == "tts":
        if tr_status in ("running", "pending"):
            return JSONResponse({"error": f"CẤM CHẠY: Không thể Lồng tiếng khi bước Dịch đang ở trạng thái '{tr_status}'"}, status_code=409)
        if not (work_dir / "script.json").exists():
            return JSONResponse({"error": "chưa dịch xong (thiếu script.json)"}, status_code=400)
        if not (voice or (m.stage("tts") or {}).get("voice") or list_clone_voices()):
            return JSONResponse({"error": "chưa có giọng clone — thêm giọng trước"}, status_code=400)

    if stage == "mux":
        if tr_status in ("running", "pending"):
            return JSONResponse({"error": f"CẤM CHẠY: Không thể Ghép video khi bước Dịch đang ở trạng thái '{tr_status}'"}, status_code=409)
        if tts_status in ("running", "pending"):
            return JSONResponse({"error": f"CẤM CHẠY: Không thể Ghép video khi bước Lồng tiếng đang ở trạng thái '{tts_status}'"}, status_code=409)
        if not ((work_dir / "tts.json").exists() or m.data.get("dub")):
            return JSONResponse({"error": "chưa có audio (tạo giọng / nhập audio trước)"}, status_code=400)

    # BẬC THANG CASCADE RESET: Khi chạy lại stage N, tự động reset các stage sau về pending
    if stage == "translate":
        stages_data = m.data.setdefault("stages", {})
        if "tts" in stages_data and stages_data["tts"].get("status") == "done":
            stages_data["tts"]["status"] = "pending"
            stages_data["tts"]["cur_text"] = "Chờ bản dịch mới"
        if "mux" in stages_data:
            stages_data["mux"]["status"] = "pending"
            stages_data["mux"]["cur_text"] = "Chờ hoàn tất lồng tiếng"
        m.save()
    elif stage == "asr":
        stages_data = m.data.setdefault("stages", {})
        for s_after in ("translate", "tts", "mux"):
            if s_after in stages_data:
                stages_data[s_after]["status"] = "pending"
                stages_data[s_after]["cur_text"] = "Chờ bóc chữ mới"
        m.save()

    target = m.data.get("request", {}).get("target", "Tiếng Việt")
    # Chặn double-click / gửi lại khi đang chạy
    busy = _job_any_busy(job_id) or _manifest_running(work_dir)
    if busy:
        return JSONResponse(
            {"error": f"job đang chạy bước '{busy}' — bấm Dừng hoặc đợi xong"},
            status_code=409,
        )
    if not _claim_stage(job_id, stage):
        return JSONResponse(
            {"error": "đã nhận lệnh trước đó — không gửi trùng"},
            status_code=409,
        )
    # Đánh dấu running NGAY (trước khi vào hàng đợi) để UI khoá nút
    try:
        m.mark_running(stage)
    except Exception:  # noqa: BLE001
        pass
    _clear_stop(job_id)

    def _wrapped():
        try:
            if job_id in _STOP_JOBS:
                print(f"[stage] {job_id}/{stage}: đã DỪNG — bỏ qua")
                return
            _run_stage(job_id, stage, target, force, voice, speed, engine)
        except _Stopped:
            print(f"[stage] {job_id}/{stage}: đã DỪNG theo yêu cầu")
        finally:
            _release_stage(job_id, stage)

    (_dl if stage == "download" else _gpu).submit(_wrapped)
    return {"started": True, "stage": stage}


def stop_job(job_id: str):
    """DỪNG mọi việc đang chạy của job (kill subprocess asr/tts/demucs/ffmpeg/aria2c
    + đưa stage 'running' về 'pending')."""
    if not (WORK_ROOT / job_id / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    _stop_job(job_id)
    # Heal nhanh, không quét wmic (tránh API stop timeout khi ffmpeg vừa kill)
    try:
        partial = WORK_ROOT / job_id / "output.partial.mp4"
        if partial.exists():
            try:
                partial.unlink(missing_ok=True)
            except OSError:
                pass
        _heal_stale_running(WORK_ROOT / job_id)
    except Exception:  # noqa: BLE001
        pass
    return {"stopped": True}


def mark_job_done(job_id: str, body: MarkDoneReq | None = None):
    """Đánh dấu bước (hoặc cả job) = done NGAY — không chạy lại / không chờ.

    Body:
      { "stage": "asr" }           — 1 bước (ưu tiên nếu đĩa đã có file kết quả)
      { "stage": "asr", "force": true } — ép done dù thiếu artifact (misclick)
      { "all": true }              — heal mọi bước đã có file trên đĩa
    """
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    body = body or MarkDoneReq()
    if _job_in_pipeline(job_id):
        # thả claim __all__ + xoá cờ Stop khi pipeline đang chạy → stage thứ 2 chạy song song
        return JSONResponse({"error": "job đang chạy trong hàng đợi — Dừng trước rồi mới đánh dấu xong"},
                            status_code=409)
    m = Manifest(work_dir)
    # Nếu đang claim busy — thả để UI không kẹt
    for s in list(RUNNABLE_STAGES) + ["__all__"]:
        _release_stage(job_id, s)
    _clear_stop(job_id)

    stage = (body.stage or "").strip() or None
    mark_all = bool(body.all)
    force = bool(body.force)

    if mark_all or not stage:
        healed = _heal_stages_from_disk(m)
        # Ép các wired còn thiếu nếu force + all
        if force:
            for s in WIRED_STAGES:
                st = m.stage(s) or {}
                if st.get("status") != "done":
                    try:
                        _force_mark_stage(m, s, require_artifact=False)
                        if s not in healed:
                            healed.append(s)
                    except Exception:  # noqa: BLE001
                        pass
        return {"ok": True, "healed": healed,
                "stages": {s: (m.stage(s) or {}).get("status") for s in RUNNABLE_STAGES}}

    if stage not in RUNNABLE_STAGES:
        return JSONResponse({"error": f"bước '{stage}' không hợp lệ"}, status_code=400)
    try:
        st = _force_mark_stage(m, stage, require_artifact=not force)
    except FileNotFoundError as e:
        return JSONResponse(
            {"error": str(e) + " — gửi force:true nếu chắc đã xong"},
            status_code=400,
        )
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    return {"ok": True, "stage": stage, "status": st.get("status"),
            "stages": {s: (m.stage(s) or {}).get("status") for s in RUNNABLE_STAGES}}


def translate_fill(job_id: str):
    """VÁ câu trống ở bước Dịch: chạy lại dịch với LÔ NHỎ (25) — run_translate tự
    resume đúng câu chưa có bản dịch (đỡ lỗi JSON lô lớn làm rớt câu)."""
    import importlib
    import engines.translate as _tr
    _tr = importlib.reload(_tr)
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "script.json").exists():
        return JSONResponse({"error": "chưa dịch lần nào"}, status_code=400)
    try:
        rows = json.loads((work_dir / "script.json").read_text(encoding="utf-8"))
        n_miss = sum(1 for r in rows if isinstance(r, dict) and not (r.get("vi") or "").strip())
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": f"đọc script.json lỗi: {e}"}, status_code=400)
    if n_miss <= 0:
        return {"started": False, "n_missing": 0, "msg": "không còn câu trống"}
    busy = _busy_response(job_id, work_dir)
    if busy:
        return busy
    if not _claim_stage(job_id, "translate"):
        return JSONResponse({"error": "đã nhận lệnh trước đó — không gửi trùng"}, status_code=409)
    try:
        m = Manifest(work_dir)

        def _mark(d):
            st = d.setdefault("stages", {}).setdefault("translate", {})
            st.update({"status": "running", "n_missing": n_miss,
                       "cur_text": f"vá {n_miss} câu trống…"})
        m.update(_mark)
        _job_cache.pop(str(work_dir), None)
        target = m.data.get("request", {}).get("target", "Tiếng Việt")
        _clear_stop(job_id)
    except Exception:
        _release_stage(job_id, "translate")
        raise

    def _run():
        try:
            # mode=batch: vá chắc, không oneshot sót
            _run_translate_engine(work_dir, batch=25, target=target, mode="batch")
        finally:
            _release_stage(job_id, "translate")
    _gpu.submit(_run)
    return {"started": True, "n_missing": n_miss}


def edit_script_line(job_id: str, req: ScriptLineEdit):
    """Sửa tay zh và/hoặc vi: ghi script.json + regen SRT. Không đụng TTS clip
    (user bấm đọc lại câu đó ở bước Giọng nếu cần)."""
    work_dir = WORK_ROOT / job_id
    sp = work_dir / "script.json"
    if not sp.exists():
        return JSONResponse({"error": "chưa có script.json"}, status_code=404)
    try:
        rows = json.loads(sp.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": f"đọc script.json lỗi: {e}"}, status_code=400)
    if not isinstance(rows, list):
        return JSONResponse({"error": "script.json không phải list"}, status_code=400)
    if req.vi is None and req.zh is None:
        return JSONResponse({"error": "cần vi hoặc zh"}, status_code=400)
    hit = None
    for r in rows:
        if not isinstance(r, dict):
            continue
        if int(r.get("i", -1)) == int(req.i):
            hit = r
            break
    if hit is None and 0 <= int(req.i) < len(rows) and isinstance(rows[int(req.i)], dict):
        hit = rows[int(req.i)]
        hit.setdefault("i", int(req.i))
    if hit is None:
        return JSONResponse({"error": f"không thấy câu i={req.i}"}, status_code=404)

    changed = False
    out_vi = (hit.get("vi") or "").strip()
    out_zh = (hit.get("zh") or "").strip()

    if req.zh is not None:
        zh = (req.zh or "").strip()
        # Rút spam cười/ư khi lưu tay (ASR hay dính hàng trăm 哈/呃)
        try:
            from engines.translate import clean_zh_spam
            zh = clean_zh_spam(zh)
        except Exception:  # noqa: BLE001
            pass
        if zh != (hit.get("zh") or "").strip():
            hit["zh"] = zh
            changed = True
            out_zh = zh

    if req.vi is not None:
        vi = (req.vi or "").strip()
        if vi != (hit.get("vi") or "").strip():
            hit["vi"] = vi
            changed = True
            out_vi = vi

    if not changed:
        return {
            "ok": True, "changed": False,
            "i": int(hit.get("i", req.i)), "vi": out_vi, "zh": out_zh,
        }

    if "rv" in hit:
        hit.pop("rv", None)
    hit["manual"] = 1
    try:
        sp.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": f"ghi script.json lỗi: {e}"}, status_code=500)

    if req.vi is not None:
        _write_srt(work_dir, "vi")
    if req.zh is not None:
        # sub.zh.srt mặc định lấy asr.json — khi sửa tay ở bước dịch thì ghi từ script
        try:
            from engines.subs import to_srt
            (work_dir / "sub.zh.srt").write_text(to_srt(rows, key="zh"), encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass

    _job_cache.pop(str(work_dir), None)
    tts_stale = False
    if req.vi is not None:
        tp = work_dir / "tts.json"
        if tp.exists():
            try:
                tts = json.loads(tp.read_text(encoding="utf-8"))
                if isinstance(tts, list):
                    for e in tts:
                        if isinstance(e, dict) and int(e.get("i", -1)) == int(hit.get("i", req.i)):
                            e["stale"] = True
                            tts_stale = True
                            break
                    if tts_stale:
                        tp.write_text(json.dumps(tts, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:  # noqa: BLE001
                pass
    return {
        "ok": True,
        "changed": True,
        "i": int(hit.get("i", req.i)),
        "vi": out_vi,
        "zh": out_zh,
        "tts_stale": tts_stale,
    }


def clean_script_spam(job_id: str):
    """Rút chuỗi 哈/呃 spam trong script.json (ASR lỗi) + prefill vi trivial nếu trống."""
    from engines.translate import clean_zh_spam, _trivial_vi
    from engines.subs import to_srt

    work_dir = WORK_ROOT / job_id
    sp = work_dir / "script.json"
    if not sp.exists():
        return JSONResponse({"error": "chưa có script.json"}, status_code=404)
    try:
        rows = json.loads(sp.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=400)
    n_zh = n_vi = 0
    for r in rows:
        if not isinstance(r, dict):
            continue
        zh0 = r.get("zh") or ""
        zh1 = clean_zh_spam(zh0)
        if zh1 != zh0:
            r["zh"] = zh1
            n_zh += 1
            r["manual"] = 1
        if not (r.get("vi") or "").strip():
            tv = _trivial_vi(r.get("zh") or "")
            if tv:
                r["vi"] = tv
                n_vi += 1
    try:
        sp.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        (work_dir / "sub.vi.srt").write_text(to_srt(rows, key="vi"), encoding="utf-8")
        (work_dir / "sub.zh.srt").write_text(to_srt(rows, key="zh"), encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=500)
    _job_cache.pop(str(work_dir), None)
    return {"ok": True, "n_zh_cleaned": n_zh, "n_vi_filled": n_vi}


def set_tts_voice(job_id: str, req: "TTSVoiceReq"):
    """Lưu giọng TTS đã chọn vào manifest (để nút Chạy / tự động dùng đúng giọng)."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    if req.voice:
        _save_tts_voice(work_dir, req.voice)
    if req.speed and req.speed > 0:
        _save_tts_speed(work_dir, req.speed)
    if req.engine:
        _save_tts_engine(work_dir, req.engine)
    return {"ok": True, "voice": req.voice, "speed": req.speed, "engine": req.engine}


def run_all(job_id: str, req: "RunAllReq"):
    """1-CLICK: chạy tự động toàn bộ pipeline từ bước còn thiếu tới hết.

    Bắt buộc có giọng clone — không cho chạy rồi render tiếng gốc (dễ tưởng đã lồng).
    """
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    # Heal trước busy-check — mux=running mồ côi sau kill khiến 1-click lỗi 409 mãi
    _heal_stale_running(work_dir)
    if req.voice:
        _save_tts_voice(work_dir, req.voice)
    if req.speed and req.speed > 0:
        _save_tts_speed(work_dir, req.speed)
    if req.tts_engine:
        _save_tts_engine(work_dir, req.tts_engine)
    if req.asr_engine:
        _resolve_asr_engine(work_dir, req.asr_engine)
    voice = _resolve_voice(work_dir, req.voice)
    if not voice:
        return JSONResponse(
            {"error": "chưa chọn giọng — hãy chọn giọng (hoặc Thêm giọng) trước khi Chạy tự động"},
            status_code=400,
        )
    if voice not in list_clone_voices():
        return JSONResponse(
            {"error": f"giọng '{voice}' không có file mẫu — chọn giọng khác hoặc Thêm giọng"},
            status_code=400,
        )
    busy = _job_any_busy(job_id) or _manifest_running(work_dir)
    if busy:
        return JSONResponse(
            {"error": f"job đang chạy bước '{busy}' — bấm Dừng hoặc đợi xong"},
            status_code=409,
        )
    if not _claim_stage(job_id, "__all__"):
        return JSONResponse({"error": "đã nhận Chạy tự động — không gửi trùng"}, status_code=409)
    _clear_stop(job_id)
    # Chỉ mark bước CÒN THIẾU — không ép asr=running khi đã done
    early = "mux"
    try:
        early = _next_incomplete_stage(work_dir) or early
        Manifest(work_dir).mark_running(early)
    except Exception:  # noqa: BLE001
        pass
    brand_mode = (getattr(req, "brand_mode", None) or "off").strip() or "off"
    brand_on = bool(getattr(req, "brand", False)) or brand_mode not in ("off", "", "0", "false")
    render_kw = {
        "flip": (getattr(req, "flip", None) or "").strip(),
        "zoom": float(getattr(req, "zoom", None) or 1.12),
        "motion": bool(getattr(req, "motion", True)),
        "lut": bool(getattr(req, "lut", True)),
        "grain": (getattr(req, "grain", None) or "weak"),
        "brand": brand_on,
        "brand_mode": brand_mode,
        "brand_text": (getattr(req, "brand_text", None) or ""),
        "brand_logo": (getattr(req, "brand_logo", None) or "off"),
        "frame": (getattr(req, "frame", None) or "off"),
        "vbitrate": (getattr(req, "vbitrate", None) or "8M"),
    }

    def _wrapped_all():
        # Claim __all__ giữ đến hết _auto_gpu (release trong _auto_pipeline/_gpu_wrapped)
        _auto_pipeline(job_id, req.audio_mode, req.voice_vol, req.orig_vol,
                       bool(req.ocr), req.fit, getattr(req, "resolution", None) or "source",
                       getattr(req, "translate_mode", None), render_kw,
                       asr_engine=getattr(req, "asr_engine", None))

    _dl.submit(_wrapped_all)
    return {"started": True, "voice": voice}


def _queue_run_one(job_id: str, opts: dict) -> tuple[str, str]:
    """Run one queued job synchronously through mux and return status + detail."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return "failed", "không tìm thấy manifest"
    _heal_stale_running(work_dir)
    if job_queue.is_wired_done(work_dir):
        return "done", "đã hoàn tất trước đó"

    # Thiếu key → theo config batch (một nguồn với agent/run_stage), không kế thừa leftover trên disk
    opts = batch_config.resolve_job_opts(opts, fill_voice=False)
    voice = opts.get("voice")
    try:
        speed_f = float(opts["speed"]) if opts.get("speed") not in (None, "") else 1.0
    except (TypeError, ValueError):
        speed_f = 1.0
    if speed_f <= 0:
        speed_f = 1.0
    tts_engine = opts.get("tts_engine") or "vieneu"
    if tts_engine not in TTS_ENGINES:
        tts_engine = "vieneu"
    asr_engine = opts.get("asr_engine") or ASR_ENGINE_DEFAULT
    if asr_engine not in ASR_ENGINES:
        asr_engine = ASR_ENGINE_DEFAULT
    translate_mode = opts.get("translate_mode") or "batch"
    audio_mode = str(opts.get("audio_mode") or "duck_bgm")
    voice_vol = float(opts["voice_vol"]) if opts.get("voice_vol") is not None else 0.2
    orig_vol = float(opts["orig_vol"]) if opts.get("orig_vol") is not None else 0.22

    if voice:
        _save_tts_voice(work_dir, voice)
    _save_tts_speed(work_dir, speed_f)
    _save_tts_engine(work_dir, tts_engine)
    _resolve_asr_engine(work_dir, asr_engine)
    try:
        m_stamp = Manifest(work_dir)
        m_stamp.data["queue_opts"] = {
            # brand*/logo/frame… phải theo job qua HOLD/QA → resume dùng lại nguyên bộ
            **{k: v for k, v in opts.items() if k != "pin_opts"},
            "voice": voice, "speed": speed_f, "tts_engine": tts_engine,
            "asr_engine": asr_engine, "audio_mode": audio_mode,
            "voice_vol": voice_vol, "orig_vol": orig_vol,
            "ocr": bool(opts.get("ocr")), "fit": bool(opts.get("fit", True)),
            "resolution": str(opts.get("resolution") or "source"),
            "translate_mode": translate_mode,
            "zoom": float(opts.get("zoom") or 1.12),
            "motion": bool(opts.get("motion", True)),
            "lut": bool(opts.get("lut", True)),
            "grain": str(opts.get("grain") or "weak"),
            "flip": str(opts.get("flip") or ""),
            "vbitrate": str(opts.get("vbitrate") or "8M"),
        }
        m_stamp.save()
    except Exception as e:  # noqa: BLE001
        print(f"[queue] stamp opts {job_id}: {e}", flush=True)

    resolved = _resolve_queue_voice(work_dir, voice)
    if not resolved:
        return "failed", "chưa chọn giọng"
    if resolved not in list_clone_voices():
        return "failed", f"giọng '{resolved}' không tồn tại"

    if _job_any_busy(job_id) or _manifest_running(work_dir):
        _heal_stale_running(work_dir)
        busy = _job_any_busy(job_id) or _manifest_running(work_dir)
        if busy:
            return "failed", f"job đang chạy bước '{busy}'"

    if not _claim_stage(job_id, "__all__"):
        return "failed", "job đã được tiến trình khác nhận"

    use_ocr = bool(opts.get("ocr"))
    fit = bool(opts.get("fit", True))
    resolution = str(opts.get("resolution") or "source")
    brand_mode = str(opts.get("brand_mode") or "off").strip() or "off"
    brand_on = bool(opts.get("brand")) or brand_mode not in ("off", "", "0", "false")
    render_kw = {
        "flip": str(opts.get("flip") or "").strip(),
        "zoom": float(opts.get("zoom") or 1.12),
        "motion": bool(opts.get("motion", True)),
        "lut": bool(opts.get("lut", True)),
        "grain": str(opts.get("grain") or "weak"),
        "brand": brand_on,
        "brand_mode": brand_mode,
        "brand_text": str(opts.get("brand_text") or ""),
        "brand_logo": str(opts.get("brand_logo") or "off"),
        "frame": str(opts.get("frame") or "off"),
        "vbitrate": str(opts.get("vbitrate") or "8M"),
    }

    try:
        early = _next_incomplete_stage(work_dir) or "mux"
        Manifest(work_dir).mark_running(early)
    except Exception:  # noqa: BLE001
        pass

    def _failed(detail: str) -> tuple[str, str]:
        try:
            Manifest(work_dir).mark_failed(early, detail)
        except Exception:  # noqa: BLE001
            pass
        return "failed", detail[:200]

    submitted = False
    try:
        if job_id in _STOP_JOBS:
            return "stopped", "đã dừng trước khi chạy"
        manifest = Manifest(work_dir)
        request = manifest.data.get("request", {})
        target = request.get("target", "Tiếng Việt")
        if not _find_video(work_dir):
            if request.get("local") or request.get("orig_path") or (manifest.stage("download") or {}).get("video_path"):
                orig = request.get("orig_path") or (manifest.stage("download") or {}).get("video_path") or "không xác định"
                return _failed(f"không tìm thấy video nguồn local (file đã bị xoá hoặc di chuyển): {orig}")
            url = request.get("url")
            if not url:
                return _failed("manifest không có URL nguồn")
            try:
                download_video(
                    url,
                    work_dir,
                    cookies_from_browser=request.get("cookies_from_browser"),
                )
            except Exception as exc:  # noqa: BLE001
                if job_id in _STOP_JOBS:
                    return "stopped", "đã dừng khi tải nguồn"
                return _failed(f"tải nguồn lỗi: {exc}")
        if job_id in _STOP_JOBS or not _find_video(work_dir):
            if job_id in _STOP_JOBS:
                return "stopped", "đã dừng sau khi tải nguồn"
            return _failed("tải nguồn xong nhưng không tìm thấy video")

        # Auto-detect duration → chia part (phim ≥ auto_split_min_h) trước ASR/GPU
        try:
            bc = batch_config.load()
            if bool(bc.get("auto_split", True)):
                sp = _maybe_auto_split_guarded(
                    job_id,
                    work_root=WORK_ROOT,
                    enabled=True,
                    target_hours=float(bc.get("auto_split_hours") or 2.5),
                    min_hours=float(bc.get("auto_split_min_h") or 3.0),
                )
                if sp.get("split") and sp.get("sub_job_ids"):
                    sub_ids = list(sp["sub_job_ids"])  # đã p01..pN
                    job_queue.queue_add(sub_ids, opts=opts, skip_done=True, sort_first=False)
                    n = sp.get("total_parts") or len(sub_ids)
                    hrs = sp.get("duration_hours")
                    msg = (
                        f"auto-split {hrs}h → {n} part (Phần 1→{n}), "
                        f"chạy lần lượt rồi ghép output.mp4: {', '.join(sub_ids)}"
                    )
                    print(f"[auto_split] queue {job_id}: {msg}", flush=True)
                    try:
                        # Parent chờ part — không để stage early=running/failed (UI báo lỗi giả)
                        def _mark_parent_waiting(d: dict) -> bool:
                            stages = d.setdefault("stages", {})
                            changed = False
                            for name in ("asr", "translate", "tts", "mux"):
                                st = stages.setdefault(name, {})
                                if st.get("status") in ("running", "failed", None, ""):
                                    st["status"] = "pending"
                                    st.pop("error", None)
                                    st.pop("last_error", None)
                                    st["cur_text"] = (
                                        f"Chờ {n} part render xong rồi ghép Full"
                                    )
                                    stages[name] = st
                                    changed = True
                            si = d.setdefault("split_info", {})
                            if si.get("status") != "split_done":
                                si["status"] = "split_done"
                                changed = True
                            return changed
                        Manifest(work_dir).update(_mark_parent_waiting)
                    except Exception:  # noqa: BLE001
                        pass
                    # "split" = thành công ủy quyền cho part (không phải failed)
                    return "split", msg
        except Exception as e_as:  # noqa: BLE001
            print(f"[auto_split] queue {job_id} bỏ qua (chạy nguyên job): {e_as}", flush=True)

        done_event = threading.Event()
        error: list[Exception] = []

        def _gpu_job() -> None:
            try:
                _auto_gpu(
                    job_id,
                    target,
                    audio_mode,
                    voice_vol,
                    orig_vol,
                    use_ocr,
                    fit,
                    resolution,
                    translate_mode,
                    render_kw,
                    asr_engine=asr_engine,
                )
            except Exception as exc:  # noqa: BLE001
                error.append(exc)
            finally:
                _release_stage(job_id, "__all__")
                done_event.set()

        _gpu.submit(_gpu_job)
        submitted = True
        done_event.wait()
        if job_id in _STOP_JOBS:
            return "stopped", "đã dừng"
        if error:
            return _failed(f"pipeline lỗi: {error[0]}")
        if job_queue.is_wired_done(work_dir):
            try:
                bc2 = batch_config.load()
                if bool(bc2.get("auto_merge", True)):
                    from engines.split_parts import try_auto_merge_parent
                    mr = try_auto_merge_parent(job_id, work_root=WORK_ROOT, enabled=True)
                    if mr and mr.get("ok") and mr.get("ready"):
                        print(
                            f"[auto_merge] {job_id}: full → {mr.get('output_path')} "
                            f"({mr.get('size_mb')} MB, {mr.get('n_parts')} part)",
                            flush=True,
                        )
            except Exception as e_mg:  # noqa: BLE001
                print(f"[auto_merge] {job_id}: {e_mg}", flush=True)
            try:
                import agents.auto_publisher as auto_publisher
                threading.Thread(target=auto_publisher.publish_job, args=(job_id,), daemon=True).start()
            except Exception as e_pub:
                print(f"[auto-publish] Lỗi trigger tự động: {e_pub}", flush=True)
            return "done", "hoàn tất"
        # Parent đã merge Full nhưng stage asr/… còn failed/pending (bug cũ) → heal
        if not job_queue.is_wired_done(work_dir):
            try:
                m_fix = Manifest(work_dir)
                si = m_fix.data.get("split_info") or {}
                outp = work_dir / "output.mp4"
                mux_st = (m_fix.stage("mux") or {})
                if (
                    si.get("sub_job_ids")
                    and outp.is_file()
                    and outp.stat().st_size > 100_000
                    and (
                        mux_st.get("status") == "done"
                        or mux_st.get("is_full_merged")
                        or si.get("status") == "merged"
                    )
                ):
                    now = time.time()
                    stages = m_fix.data.setdefault("stages", {})
                    for name in ("download", "asr", "translate", "tts", "mux"):
                        st = stages.setdefault(name, {})
                        st.pop("error", None)
                        st.pop("last_error", None)
                        st["status"] = "done"
                        st["updated_at"] = now
                        st.setdefault("from_split_merge", True)
                        stages[name] = st
                    m_fix.save()
            except Exception as e_heal:  # noqa: BLE001
                print(f"[auto-split] heal parent stages {job_id}: {e_heal}", flush=True)
        if job_queue.is_wired_done(work_dir):
            return "done", "hoàn tất (split parent healed)"
        held = (Manifest(work_dir).data.get("agent") or {}).get("held_at")
        if held:
            return "held", f"dừng chờ duyệt ({held}) — duyệt xong gọi «chạy tiếp»"
        # Bóc tách lỗi cụ thể từ stage bị dừng (vd dịch hết quota LLM) để báo chính xác
        m_curr = Manifest(work_dir)
        for stg in ("download", "asr", "translate", "tts", "mux"):
            stg_info = m_curr.stage(stg) or {}
            if stg_info.get("status") == "failed" and stg_info.get("error"):
                return _failed(f"bước {stg} lỗi: {stg_info.get('error')}")
            if stg == "translate" and stg_info.get("last_error"):
                return _failed(f"dịch lỗi: {stg_info.get('last_error')[:150]}")
        return _failed("pipeline kết thúc nhưng output chưa hoàn chỉnh")
    except Exception as exc:  # noqa: BLE001
        return _failed(f"không thể gửi/chạy pipeline: {exc}")
    finally:
        if not submitted:
            _release_stage(job_id, "__all__")
            _heal_stale_running(work_dir)


def set_asr_engine(job_id: str, req: AsrEngineReq):
    """Lưu engine ASR (hybrid_fa / fun_asr_nano / …) cho job."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    if req.engine not in ASR_ENGINES:
        return JSONResponse({"error": f"engine '{req.engine}' không hợp lệ"}, status_code=400)
    eng = _resolve_asr_engine(work_dir, req.engine)
    return {"ok": True, "engine": eng}


# Nhãn gọn cho sidecar ASR (UI chọn nguồn chữ)
_ASR_SOURCE_LABELS = {
    "asr.json": "Hiện tại (asr.json)",
    "asr.fun_nano.json": "Fun-ASR-Nano ⭐",
    "asr.fun_nano_retry.json": "Fun-ASR-Nano (retry)",
    "asr.firered.json": "FireRedASR2",
    "asr.paraformer_zh.json": "Paraformer",
    "asr.sensevoice.json": "SenseVoice",
    "asr.consensus.json": "Consensus (compare)",
    "asr.aligned.json": "Aligned (Nano+Para)",
    "asr.aligned_n1.json": "Aligned n1 (Nano+Para, no repair)",
    "asr.aligned_fa.json": "Aligned + ForcedAlign",
    "asr.aligned_fix.json": "Aligned + FA fix",
    "asr.aligned_repaired.json": "Aligned + Repair",
    "asr.hardsub.json": "Hardsub OCR",
}


def _list_asr_sources(work_dir: Path) -> list[dict]:
    """Liệt kê asr.json + asr.*.json có dữ liệu (bỏ progress/meta/chars/bak)."""
    out: list[dict] = []
    seen: set[str] = set()
    candidates: list[Path] = []
    main = work_dir / "asr.json"
    if main.exists():
        candidates.append(main)
    for p in sorted(work_dir.glob("asr.*.json")):
        name = p.name.lower()
        if any(x in name for x in (
            ".progress.", ".meta.", ".chars.", ".bak", "compare", "before_",
        )):
            continue
        if name.endswith(".bak.json"):
            continue
        candidates.append(p)
    active_src = ""
    try:
        m = Manifest(work_dir)
        active_src = str((m.stage("asr") or {}).get("asr_source") or "")
    except Exception:  # noqa: BLE001
        active_src = ""
    for p in candidates:
        if p.name in seen:
            continue
        seen.add(p.name)
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if not isinstance(data, list) or len(data) < 1:
            continue
        n = len(data)
        label = _ASR_SOURCE_LABELS.get(p.name) or p.name.replace("asr.", "").replace(".json", "")
        out.append({
            "file": p.name,
            "label": label,
            "n": n,
            "active": (p.name == "asr.json") or (p.name == active_src),
            "is_nano": "fun_nano" in p.name.lower() or p.name == "asr.fun_nano.json",
            "mtime": p.stat().st_mtime,
        })
    # active: nếu asr.json tồn tại → đánh dấu bản hiện tại; sidecar trùng nội dung vẫn list
    if any(x["file"] == "asr.json" for x in out):
        for x in out:
            if x["file"] == "asr.json":
                x["active"] = True
            elif x["file"] == active_src:
                x["active"] = True  # nguồn vừa promote
    return out


def _promote_asr_source(work_dir: Path, source: str) -> dict:
    """Copy sidecar → asr.json + sub.zh.srt; backup asr.json cũ."""
    import shutil
    from engines.subs import to_srt

    src_name = Path(source).name  # chống path traversal
    if not src_name.startswith("asr") or not src_name.endswith(".json"):
        raise ValueError(f"file không hợp lệ: {source}")
    if any(x in src_name.lower() for x in (".progress", ".meta", ".chars", "compare")):
        raise ValueError(f"không dùng file phụ: {src_name}")
    src = work_dir / src_name
    if not src.exists():
        raise FileNotFoundError(f"không có {src_name}")
    rows = json.loads(src.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{src_name} rỗng / không phải list")
    # chuẩn hoá key text
    norm = []
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            continue
        text = (r.get("text") or r.get("zh") or "").strip()
        if not text:
            continue
        norm.append({
            "i": r.get("i", len(norm)),
            "start": float(r.get("start", 0) or 0),
            "end": float(r.get("end", 0) or 0),
            "text": text,
        })
    if not norm:
        raise ValueError(f"{src_name} không có câu text")
    # Tự rút spam tiếng nền + vá từ sidecar khác (không cần check tay)
    try:
        from engines.asr.asr_spam import sanitize_asr_rows
        norm, spam_info = sanitize_asr_rows(
            norm, work_dir=work_dir, source_path=src, heal=True)
        if spam_info.get("n_cleaned") or spam_info.get("n_healed"):
            print(
                f"[asr-select] spam: cleaned={spam_info['n_cleaned']} "
                f"healed={spam_info['n_healed']}",
                flush=True,
            )
            # ghi lại sidecar đã sạch
            try:
                src.write_text(json.dumps(norm, ensure_ascii=False, indent=2), encoding="utf-8")
            except OSError:
                pass
    except Exception as _se:  # noqa: BLE001
        print(f"[asr-select] asr_spam skip: {_se}", flush=True)
    asr_path = work_dir / "asr.json"
    if asr_path.exists() and src.resolve() != asr_path.resolve():
        bak = work_dir / "asr.json.bak_before_select"
        try:
            shutil.copy2(asr_path, bak)
        except OSError:
            pass
    asr_path.write_text(json.dumps(norm, ensure_ascii=False, indent=2), encoding="utf-8")
    (work_dir / "sub.zh.srt").write_text(to_srt(norm, key="text"), encoding="utf-8")
    # sidecar SRT đồng bộ
    tag = src_name[len("asr."):-len(".json")] if src_name.startswith("asr.") and src_name.endswith(".json") else ""
    if tag and tag != "json":
        try:
            (work_dir / f"sub.zh.{tag}.srt").write_text(to_srt(norm, key="text"), encoding="utf-8")
        except OSError:
            pass
    eng_hint = "nano_fa" if "nano_fa" in src_name else (
        "fun_asr_nano" if "fun_nano" in src_name else (
        "firered_asr" if "firered" in src_name else (
        "paraformer_zh" if "paraformer" in src_name else (
        "sensevoice" if "sensevoice" in src_name else (
        "hybrid_fa" if ("aligned" in src_name or "consensus" in src_name or "repaired" in src_name)
        else None)))))
    model_hint = {
        "nano_fa": "Nano+Direct FA",
        "fun_asr_nano": "Fun-ASR-Nano",
        "firered_asr": "FireRedASR2-AED",
        "paraformer_zh": "Paraformer-zh",
        "sensevoice": "SenseVoiceSmall",
        "hybrid_fa": "Hybrid FA",
    }.get(eng_hint or "", "")
    if "fun_nano" in src_name:
        model_hint = "Fun-ASR-Nano"
    elif "firered" in src_name:
        model_hint = "FireRedASR2-AED"
    fields = {
        "asr_source": src_name,
        "n_segments": len(norm),
        "status": "done",
        "progress": 100,
        "cur_text": f"đã chọn {src_name}",
        "model": model_hint or None,
    }
    if eng_hint:
        fields["asr_engine"] = eng_hint
        fields["engine"] = eng_hint
    try:
        m_prev = Manifest(work_dir)
        prev_asr = (m_prev.data.get("stages") or {}).get("asr") or {}
        prev_src = prev_asr.get("asr_source")
        prev_n = int(prev_asr.get("n_segments") or 0)
    except Exception:  # noqa: BLE001
        prev_src, prev_n = None, 0
    same_source = (prev_src == src_name and prev_n == len(norm) and prev_n > 0)
    _patch_asr_fields(work_dir, **fields)
    if same_source:
        print(
            f"[asr-select] {work_dir.name}: cùng nguồn {src_name} n={len(norm)} — "
            f"không invalidate translate/TTS",
            flush=True,
        )
        stale = False
    else:
        # Đổi nguồn ASR → bản dịch cũ lệch ZH/i — đánh dấu phải dịch lại
        stale = _invalidate_translate_for_asr(work_dir, src_name, len(norm))
    return {"ok": True, "source": src_name, "n_segments": len(norm),
            "engine": eng_hint, "model": model_hint or None,
            "translate_stale": stale}


def _invalidate_translate_for_asr(work_dir: Path, asr_source: str, n_asr: int) -> bool:
    """Backup script + đánh dấu translate lệch khi đổi asr_source."""
    import shutil
    script = work_dir / "script.json"
    if not script.exists():
        return False
    try:
        rows = json.loads(script.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        rows = []
    n_script = len(rows) if isinstance(rows, list) else 0
    # luôn stale nếu đổi nguồn (kể cả cùng số câu — cắt ZH khác)
    bak = work_dir / "script.json.bak_before_asr_select"
    try:
        shutil.copy2(script, bak)
    except OSError:
        pass
    m = Manifest(work_dir)
    st = m.data.setdefault("stages", {}).setdefault("translate", {})
    st.update({
        "status": "pending",
        "progress": 0,
        "n_missing": n_asr,
        "n_segments": n_asr,
        "cur_text": f"cần dịch lại (ASR → {asr_source})",
        "stale_asr_source": asr_source,
        "stale_reason": f"script {n_script} câu ≠ ASR {n_asr} / đổi nguồn",
        "reviewed": False,
        "updated_at": time.time(),
    })
    m.data["stages"]["translate"] = st
    # TTS cũng lệch timeline
    tts = m.data.get("stages", {}).get("tts")
    if isinstance(tts, dict) and tts.get("status") == "done":
        tts = dict(tts)
        tts["status"] = "pending"
        tts["cur_text"] = "cần tạo giọng lại (ASR/dịch đã đổi)"
        tts["stale"] = True
        m.data["stages"]["tts"] = tts
    m.save()
    _job_cache.pop(str(work_dir), None)
    return True


def _translate_asr_sync_info(work_dir: Path) -> dict:
    """UI: script có khớp asr.json không?"""
    asr_path = work_dir / "asr.json"
    script_path = work_dir / "script.json"
    info = {"ok": False, "n_asr": 0, "n_script": 0, "zh_match": 0, "stale": True, "reason": ""}
    if not asr_path.exists():
        info["reason"] = "chưa có asr.json"
        return info
    try:
        asr = json.loads(asr_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        info["reason"] = "asr.json hỏng"
        return info
    if not isinstance(asr, list):
        return info
    info["n_asr"] = len(asr)
    if not script_path.exists():
        info["reason"] = "chưa dịch"
        return info
    try:
        script = json.loads(script_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        info["reason"] = "script.json hỏng"
        return info
    if not isinstance(script, list):
        return info
    info["n_script"] = len(script)
    by_i = {r.get("i"): r for r in script if isinstance(r, dict)}
    match = 0
    for s in asr:
        r = by_i.get(s.get("i"))
        if not r:
            continue
        if (r.get("zh") or "") == (s.get("text") or ""):
            match += 1
    info["zh_match"] = match
    if info["n_script"] != info["n_asr"]:
        info["reason"] = f"script {info['n_script']} câu ≠ ASR {info['n_asr']}"
        info["stale"] = True
    elif match < max(1, int(info["n_asr"] * 0.85)):
        info["reason"] = f"ZH lệch ({match}/{info['n_asr']} khớp)"
        info["stale"] = True
    else:
        info["ok"] = True
        info["stale"] = False
        info["reason"] = "khớp ASR"
    return info


def list_asr_sources(job_id: str):
    """Danh sách file ASR có sẵn để chọn (Nano / FireRed / …)."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    items = _list_asr_sources(work_dir)
    active = next((x["file"] for x in items if x.get("active") and x["file"] != "asr.json"), None)
    # nếu có asr_source trong manifest
    try:
        m = Manifest(work_dir)
        active = (m.stage("asr") or {}).get("asr_source") or active
    except Exception:  # noqa: BLE001
        pass
    return {"items": items, "active": active, "n": len(items),
            "translate": _translate_asr_sync_info(work_dir)}


def select_asr_source(job_id: str, req: AsrSelectReq):
    """Promote file ASR (vd asr.fun_nano.json) → asr.json + sub.zh.srt."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    try:
        return _promote_asr_source(work_dir, req.source)
    except FileNotFoundError as e:
        return JSONResponse({"error": str(e)}, status_code=404)
    except ValueError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=500)


def _context_studio_input(work_dir: Path) -> Path | None:
    """Ưu tiên asr.json → sub.zh.srt."""
    for name in ("asr.json", "sub.zh.srt", "asr.aligned_repaired.json"):
        p = work_dir / name
        if p.exists() and p.stat().st_size > 20:
            return p
    return None


def _do_context_studio(work_dir: Path, use_llm: bool = True) -> dict:
    """Chạy PRE-SCAN → ghi pack vào work_dir."""
    from tools.context_studio.analyzer import analyze, summarize
    from tools.context_studio.character_mapper import enrich_characters, validate_pronouns
    from tools.context_studio.exporter import write_pack
    from tools.context_studio.schema import scan_number_flags
    from tools.context_studio.srt_io import load_segments

    m = Manifest(work_dir)
    st = m.data.setdefault("stages", {}).setdefault("context_studio", {})
    st.update({
        "status": "running", "progress": 5, "cur_text": "PRE-SCAN…",
        "llm": bool(use_llm), "updated_at": time.time(),
    })
    m.data["stages"]["context_studio"] = st
    m.save()
    try:
        src = _context_studio_input(work_dir)
        if not src:
            raise FileNotFoundError("Chưa có asr.json / sub.zh.srt — chạy Nhận diện lời trước")
        st.update({"cur_text": f"đọc {src.name}…", "progress": 15, "input": src.name})
        m.save()
        segs = load_segments(src)
        st.update({
            "cur_text": f"analyze {len(segs)} câu" + (" · LLM…" if use_llm else " · heuristic…"),
            "progress": 30, "n_segments": len(segs),
        })
        m.save()
        glossary = analyze(segs, use_llm=bool(use_llm))
        glossary = enrich_characters(glossary, segments=segs)
        warns = validate_pronouns(glossary)
        flags = scan_number_flags(segs)
        st.update({"cur_text": "ghi context pack…", "progress": 85})
        m.save()
        paths = write_pack(work_dir, glossary, flags)
        sm = summarize(glossary)
        n_sus = sum(1 for f in flags if f.get("suspicious"))
        result = {
            "status": "done", "progress": 100,
            "cur_text": f"{sm.get('genre') or '?'} · {sm.get('style') or '?'}",
            "summary": sm,
            "n_flags": len(flags), "n_suspicious": n_sus,
            "n_warns": len(warns),
            "paths": {k: Path(v).name for k, v in paths.items()},
            "input": src.name, "llm": bool(use_llm),
            "updated_at": time.time(),
        }
        st.update(result)
        m.data["stages"]["context_studio"] = st
        m.save()
        print(f"[context_studio] {work_dir.name} done · {sm}", flush=True)
        return result
    except Exception as e:  # noqa: BLE001
        st.update({
            "status": "failed", "error": str(e)[:400],
            "cur_text": str(e)[:120], "updated_at": time.time(),
        })
        m.data["stages"]["context_studio"] = st
        m.save()
        print(f"[context_studio] {work_dir.name} lỗi: {e}", flush=True)
        raise


def get_context_studio(job_id: str):
    """Xem pack Context Studio (summary + style_lock + characters)."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    m = Manifest(work_dir)
    st = dict(m.stage("context_studio") or {})
    pack = work_dir / "context_pack.json"
    gloss_p = work_dir / "glossary.json"
    out: dict = {"job_id": job_id, "stage": st, "ready": pack.exists()}
    if pack.exists():
        try:
            out["pack"] = json.loads(pack.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            out["pack"] = None
    if gloss_p.exists():
        try:
            g = json.loads(gloss_p.read_text(encoding="utf-8"))
            lock = g.get("style_lock") or {}
            out["preview"] = {
                "genre": g.get("genre"),
                "tone": (g.get("tone") or "")[:200],
                "style": lock.get("mode"),
                "forbid": (lock.get("forbid") or [])[:12],
                "prefer": (lock.get("prefer") or [])[:12],
                "characters": [
                    {"zh": c.get("zh"), "vi": c.get("vi"), "role": c.get("role"),
                     "self_ref": c.get("self_ref")}
                    for c in (g.get("characters") or [])[:20]
                    if isinstance(c, dict)
                ],
                "terms": [
                    {"zh": t.get("zh"), "vi": t.get("vi"), "type": t.get("type")}
                    for t in (g.get("terms") or [])[:25]
                    if isinstance(t, dict)
                ],
                "n_pronouns": len(g.get("pronouns") or []),
                "source": (g.get("_meta") or {}).get("source"),
            }
        except Exception as e:  # noqa: BLE001
            out["preview_error"] = str(e)
    flags_p = work_dir / "qa_flags.json"
    if flags_p.exists():
        try:
            fl = json.loads(flags_p.read_text(encoding="utf-8"))
            out["flags"] = {
                "n_total": fl.get("n_total"),
                "n_suspicious": fl.get("n_suspicious"),
                "sample": (fl.get("flags") or [])[:8],
            }
        except Exception:  # noqa: BLE001
            pass
    return out


def run_context_studio_api(job_id: str, req: ContextStudioReq):
    """Chạy Context Studio PRE-SCAN → glossary/style_lock/qa_flags trong work/<job>."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    if not _context_studio_input(work_dir):
        return JSONResponse(
            {"error": "chưa có asr.json / sub.zh.srt — chạy Nhận diện lời trước"},
            status_code=400,
        )
    pack = work_dir / "context_pack.json"
    if pack.exists() and not req.force:
        st = (Manifest(work_dir).stage("context_studio") or {})
        if st.get("status") == "running":
            return {"started": False, "already": "running", "stage": st}
        return {
            "started": False, "already": "ready",
            "hint": "đã có context_pack.json — bấm force để chạy lại",
            "pack": True,
        }
    st0 = Manifest(work_dir).stage("context_studio") or {}
    if st0.get("status") == "running":
        return {"started": False, "already": "running", "stage": st0}

    def _wrapped():
        try:
            _do_context_studio(work_dir, use_llm=bool(req.llm))
        except Exception:  # noqa: BLE001
            pass

    _misc.submit(_wrapped)
    return {"started": True, "llm": bool(req.llm)}


def get_translate_alts(job_id: str):
    """Pack analyze checklist + danh sách câu đa nghĩa (vi_alts.json)."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    from engines.translate_alts import analyze_pack_report
    out: dict = {"report": analyze_pack_report(work_dir)}
    st = Manifest(work_dir).stage("translate_alts") or {}
    out["stage"] = st
    ap = work_dir / "vi_alts.json"
    if ap.exists():
        try:
            out["alts"] = json.loads(ap.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            out["alts_error"] = str(e)
    return out


def run_translate_alts_api(job_id: str, req: TranslateAltsReq):
    """Quét câu đa nghĩa theo chunk + pack analyze → vi_alts.json."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "script.json").exists():
        return JSONResponse({"error": "chưa có bản dịch (script.json)"}, status_code=400)
    st0 = Manifest(work_dir).stage("translate_alts") or {}
    if st0.get("status") == "running":
        return {"started": False, "already": "running"}

    def _wrapped():
        try:
            from engines.translate_alts import run_ambiguous_alts
            run_ambiguous_alts(
                work_dir,
                force=bool(req.force),
                limit=req.limit,
                apply_pick=bool(req.apply_pick),
            )
        except Exception as e:  # noqa: BLE001
            print(f"[translate-alts] {job_id} lỗi: {e}", flush=True)

    _gpu.submit(_wrapped)
    return {"started": True, "limit": req.limit, "force": req.force}


def apply_alt_pick(job_id: str, req: ApplyAltReq):
    """Chốt một phương án alts[pick] → vi (+ regen SRT)."""
    work_dir = WORK_ROOT / job_id
    sp = work_dir / "script.json"
    if not sp.exists():
        return JSONResponse({"error": "chưa có script.json"}, status_code=404)
    rows = json.loads(sp.read_text(encoding="utf-8"))
    hit = next((r for r in rows if isinstance(r, dict) and int(r.get("i", -1)) == int(req.i)), None)
    if hit is None:
        return JSONResponse({"error": f"không thấy i={req.i}"}, status_code=404)
    alts = hit.get("alts") if isinstance(hit.get("alts"), list) else []
    if not alts:
        # thử vi_alts.json
        ap = work_dir / "vi_alts.json"
        if ap.exists():
            data = json.loads(ap.read_text(encoding="utf-8"))
            for it in data.get("items") or []:
                if int(it.get("i", -1)) == int(req.i):
                    alts = it.get("alts") or []
                    hit["alts"] = alts
                    break
    if not alts:
        return JSONResponse({"error": "câu chưa có alts"}, status_code=400)
    pick = int(req.pick)
    if pick < 0 or pick >= len(alts):
        return JSONResponse({"error": f"pick={pick} ngoài 0..{len(alts)-1}"}, status_code=400)
    hit["vi"] = str(alts[pick]).strip()
    hit["alt_pick"] = pick
    hit["manual"] = True
    sp.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    try:
        from engines.subs import to_srt
        (work_dir / "sub.vi.srt").write_text(to_srt(rows, key="vi"), encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    # sync vi_alts.json pick
    ap = work_dir / "vi_alts.json"
    if ap.exists():
        try:
            data = json.loads(ap.read_text(encoding="utf-8"))
            for it in data.get("items") or []:
                if int(it.get("i", -1)) == int(req.i):
                    it["pick"] = pick
                    it["vi"] = hit["vi"]
                    it["alts"] = alts
            ap.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
    return {"ok": True, "i": req.i, "pick": pick, "vi": hit["vi"]}


class HardsubAsrReq(BaseModel):
    dur: float | None = None
    fps: float = 2.0
    apply: bool = False
    force: bool = False


def run_hardsub_asr_api(job_id: str, req: HardsubAsrReq):
    """OCR hardsub → rà/sửa chữ ZH trên ASR (giữ timing). Không thay bước dịch."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "asr.json").exists():
        return JSONResponse({"error": "chưa có asr.json"}, status_code=400)
    if not (work_dir / "source.mp4").exists() and not list(work_dir.glob("source.*")):
        # vẫn cho chạy nếu manifest có video_path
        pass
    st0 = Manifest(work_dir).stage("hardsub_asr") or {}
    if st0.get("status") == "running":
        return {"started": False, "already": "running"}

    def _wrapped():
        try:
            from engines.asr.hardsub_asr import run_hardsub_asr
            run_hardsub_asr(
                work_dir,
                dur=req.dur,
                fps=float(req.fps or 2.0),
                apply=bool(req.apply),
                force=bool(req.force),
            )
        except Exception as e:  # noqa: BLE001
            print(f"[hardsub-asr] {job_id} lỗi: {e}", flush=True)

    _gpu.submit(_wrapped)
    return {"started": True, "dur": req.dur, "apply": req.apply}


def get_hardsub_asr(job_id: str):
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    st = Manifest(work_dir).stage("hardsub_asr") or {}
    out: dict = {"stage": st}
    for name in ("hardsub_cues.json", "asr.hardsub.json"):
        p = work_dir / name
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                out[name] = {"n": len(data) if isinstance(data, list) else data}
            except Exception:  # noqa: BLE001
                out[name] = {"path": str(p)}
    return out


# ===== Cookies (import + trạng thái) =====
COOKIES_DIR = Path("cookies")


def _cookie_info(path: Path) -> dict:
    """Đếm cookie + kiểm định dạng Netscape của 1 file cookie."""
    try:
        txt = path.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        return {"exists": False}
    lines = [l for l in txt.splitlines() if l.strip() and not l.startswith("#")]
    n = sum(1 for l in lines if "\t" in l)
    head = txt.lstrip()[:40]
    valid = path.stat().st_size > 0 and (head.startswith("# Netscape") or head.startswith("# HTTP") or n > 0)
    return {"exists": True, "size": path.stat().st_size, "n_cookies": n,
            "valid": valid, "mtime": path.stat().st_mtime}


def cookies_status():
    COOKIES_DIR.mkdir(exist_ok=True)
    return {p.name: _cookie_info(p) for p in sorted(COOKIES_DIR.glob("*cookie*.txt"))}


_COOKIE_DOMAIN = {"bilibili": ".bilibili.com", "douyin": ".douyin.com",
                  "tiktok": ".tiktok.com"}


def _header_to_netscape(header: str, plat: str) -> str:
    """Chuyển chuỗi header 'name=value; name2=value2' (copy từ DevTools) -> Netscape."""
    dom = _COOKIE_DOMAIN.get(plat, ".bilibili.com")
    out = ["# Netscape HTTP Cookie File"]
    for pair in header.split(";"):
        pair = pair.strip()
        if "=" not in pair:
            continue
        name, val = pair.split("=", 1)
        name = name.strip()
        if not name:
            continue
        out.append(f"{dom}\tTRUE\t/\tFALSE\t0\t{name}\t{val.strip()}")
    return "\n".join(out) + "\n"


async def import_cookies(file: UploadFile = File(None), text: str = Form(None),
                         platform: str = Form("auto")):
    """Nhập cookies bằng FILE (.txt Netscape từ extension) HOẶC dán TEXT vào popup.
    Text nhận 2 dạng: Netscape đầy đủ, hoặc chuỗi header 'a=b; c=d' copy từ DevTools
    (tự chuyển sang Netscape theo nền tảng). Kiểm tra hợp lệ + tự nhận nền tảng ->
    lưu cookies/<nền tảng>_cookies.txt (ghi đè). Sửa nỗi đau cookies rỗng làm DL fail."""
    if text and text.strip():
        txt = text
    elif file is not None:
        raw = await file.read()
        if not raw:
            return JSONResponse({"error": "file cookies RỖNG"}, status_code=400)
        txt = raw.decode("utf-8", errors="replace")
    else:
        return JSONResponse({"error": "chưa có cookies (chọn file hoặc dán text)"},
                            status_code=400)

    low = txt.lower()
    plat = platform if platform in _COOKIE_DOMAIN else (
        "bilibili" if "bilibili" in low else "douyin" if "douyin" in low
        else "tiktok" if "tiktok" in low else "bilibili")

    head = txt.lstrip()[:40]
    is_netscape = head.startswith("# Netscape") or head.startswith("# HTTP") \
        or any("\t" in l for l in txt.splitlines() if l.strip() and not l.startswith("#"))
    if not is_netscape:
        # thử coi như chuỗi header 'a=b; c=d'
        if "=" in txt and ";" in txt:
            txt = _header_to_netscape(txt, plat)
        else:
            return JSONResponse(
                {"error": "không nhận ra cookies — dán dạng Netscape (.txt) hoặc 'name=value; name2=value2'"},
                status_code=400)

    n = sum(1 for l in txt.splitlines() if l.strip() and not l.startswith("#") and "\t" in l)
    if n == 0:
        return JSONResponse({"error": "không tìm thấy cookie nào trong nội dung"}, status_code=400)

    COOKIES_DIR.mkdir(exist_ok=True)
    dest = COOKIES_DIR / f"{plat}_cookies.txt"
    dest.write_text(txt, encoding="utf-8")
    print(f"[cookies] updated {dest.name}: {n} cookies ({plat})")
    return {"ok": True, "platform": plat, "n_cookies": n, "file": dest.name}


def list_jobs():
    if not WORK_ROOT.exists():
        return []
    jobs = []
    for d in sorted(WORK_ROOT.iterdir()):
        if (d / "manifest.json").exists():
            jobs.append(read_job(d))
    # job đang chạy lên đầu, rồi tới chờ, rồi xong
    rank = {"running": 0, "pending": 1, "failed": 2, "done": 3}
    jobs.sort(key=lambda j: rank.get(j["status"], 9))
    return jobs


def job_detail(job_id: str):
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    return read_job(work_dir)


_VIDEO_EXT = {".mp4", ".mkv", ".webm", ".mov"}
_AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac", ".opus"}


def _audio_dur(path: Path) -> float:
    """Đo độ dài audio (giây) bằng ffprobe. Lỗi -> 0."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", str(path)],
            check=True, capture_output=True, text=True,
        )
        return round(float(out.stdout.strip()), 3)
    except Exception:  # noqa: BLE001
        return 0.0


def _probe_video(path: Path) -> dict:
    """Rút width/height/duration/vcodec bằng ffprobe. Lỗi -> {}."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height,codec_name:format=duration",
             "-of", "json", str(path)],
            check=True, capture_output=True, text=True,
        )
        data = json.loads(out.stdout or "{}")
        stream = (data.get("streams") or [{}])[0]
        fmt = data.get("format") or {}
        dur_raw = fmt.get("duration")
        dur = round(float(dur_raw), 3) if dur_raw not in (None, "") else None
        return {
            "width": stream.get("width"),
            "height": stream.get("height"),
            "vcodec": stream.get("codec_name"),
            "duration_sec": dur,
        }
    except Exception:  # noqa: BLE001
        return {}


def _clear_job_sources(work_dir: Path) -> None:
    """Xoá source.* / mảnh .part cũ trước khi import."""
    for pat in ("source.*", "*.part", "*.part.aria2"):
        for old in work_dir.glob(pat):
            if old.suffix.lower() in {".json", ".jpg", ".jpeg", ".png", ".webp"}:
                continue
            try:
                old.unlink()
            except OSError:
                pass


def _link_or_copy(src: Path, dest: Path) -> str:
    """Hard link nếu được (cùng ổ — không tốn thêm dung lượng); khác ổ / FS không hỗ trợ mới copy."""
    try:
        os.link(str(src), str(dest))
        return "link"
    except OSError as e:
        print(f"[import] không hard link được {src} ({e}) → copy", flush=True)
    shutil.copy2(str(src), str(dest))
    return "copy"


def _direct_source_roots() -> list[Path]:
    raw = _config_boot.get("SOURCE_DIRECT_ROOTS", r"D:\Lib") or ""
    return [Path(p.strip()) for p in raw.split(";") if p.strip()]


def _is_direct_source(src: Path) -> bool:
    """File trong thư viện (SOURCE_DIRECT_ROOTS) → job đọc thẳng video_path, không đặt file vào job."""
    try:
        s = src.resolve()
    except OSError:
        return False
    for root in _direct_source_roots():
        try:
            s.relative_to(root.resolve())
            return True
        except (ValueError, OSError):
            continue
    return False


def _place_source(src: Path, work_dir: Path, move: bool) -> tuple[Path, str]:
    """Trả (đường dẫn video job dùng, cách đặt: direct/move/link/copy)."""
    if not move and _is_direct_source(src):
        _clear_job_sources(work_dir)
        return src.resolve(), "direct"
    _clear_job_sources(work_dir)
    dest = work_dir / f"source{src.suffix.lower()}"
    if move:
        shutil.move(str(src), str(dest))
        return dest, "move"
    return dest, _link_or_copy(src, dest)


def _finalize_imported_source(
    work_dir: Path, dest: Path, *, orig_name: str | None = None, source_kind: str = "imported",
    source_mode: str | None = None,
) -> dict:
    """Ghi meta + mark download done. `dest` có thể nằm ngoài job (source_mode=direct: file thư viện)."""
    probe = _probe_video(dest)
    try:
        st = dest.stat()
        sig = {"video_size": st.st_size, "video_mtime": int(st.st_mtime)}
    except OSError:
        sig = {}
    if source_mode:
        sig["source_mode"] = source_mode
    m = Manifest(work_dir)
    req = m.data.get("request") or {}
    meta = {
        "platform": "local",
        "source_url": req.get("url"),
        "title": Path(orig_name or dest.name).stem,
        "id": work_dir.name,
        "duration_sec": probe.get("duration_sec"),
        "uploader": None,
        "width": probe.get("width"),
        "height": probe.get("height"),
        "vcodec": probe.get("vcodec"),
        "webpage_url": req.get("url"),
        "imported": True,
        "orig_name": orig_name or dest.name,
    }
    (work_dir / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    result = m.mark_done(
        "download",
        video_path=str(dest.resolve()),
        source=source_kind,
        **sig,
        **meta,
    )
    print(f"[import] {work_dir.name}: {dest.name} ({source_mode or source_kind}) "
          f"| {meta.get('height') or '?'}p | {meta.get('duration_sec')}s | {meta.get('vcodec')}")
    return {"ok": True, "file": dest.name, "video_path": str(dest.resolve()), **meta}


def _find_video(work_dir: Path) -> Path | None:
    """Tìm file video đã tải: ưu tiên video_path trong manifest, fallback glob."""
    m = Manifest(work_dir)
    dl = m.stage("download") or {}
    vp = dl.get("video_path")
    if vp and Path(vp).exists():
        return Path(vp)
    cands = [c for c in sorted(work_dir.glob("source.*"))
             if c.suffix.lower() in _VIDEO_EXT]
    return cands[0] if cands else None


def job_video(job_id: str):
    """Stream video đã tải để preview. FileResponse tự xử lý Range -> tua được.

    Nhận cả HEAD để client lấy Content-Length (dung lượng) mà không tải cả file.
    """
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    p = _find_video(work_dir)
    if not p:
        return JSONResponse({"error": "video chưa tải xong"}, status_code=404)
    return FileResponse(str(p), media_type="video/mp4", filename=p.name)


# lang -> (file nguồn, key text). zh lấy từ ASR, vi lấy từ bản dịch.
_SRT_SRC = {"zh": ("script.json", "zh"), "vi": ("script.json", "vi")}
# fallback khi chưa có script (mới ASR xong)
_SRT_SRC_FALLBACK = {"zh": ("asr.json", "text")}
# tên file .srt -> lang (để reveal biết cần sinh gì)
_SRT_FILES = {f"sub.{lang}.srt": lang for lang in _SRT_SRC}


def _write_srt(work_dir: Path, lang: str) -> tuple[Path, str] | None:
    """Sinh .srt từ json nguồn, ghi ra sub.<lang>.srt. Trả (path, nội dung) hoặc
    None nếu thiếu file nguồn. Dùng chung cho endpoint tải và reveal.
    zh ưu tiên script.json (đã sửa/rút spam); fallback asr.json nếu chưa dịch.
    vi: ưu tiên script.display.json (đã CUT); không có thì tách on-the-fly từ script."""
    if lang == "vi":
        disp_p = work_dir / "script.display.json"
        script_p = work_dir / "script.json"
        segs = None
        if disp_p.exists():
            try:
                segs = json.loads(disp_p.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001
                segs = None
        if not segs and script_p.exists():
            try:
                from engines.subs import split_bilingual_rows, sub_split_cfg, to_srt as _to_srt
                rows = json.loads(script_p.read_text(encoding="utf-8"))
                mz, mv, md = sub_split_cfg()
                segs = split_bilingual_rows(
                    [dict(r) for r in rows], max_zh=mz, max_vi=mv, max_dur=md
                )
                disp_p.write_text(json.dumps(segs, ensure_ascii=False, indent=2), encoding="utf-8")
            except Exception:  # noqa: BLE001
                segs = json.loads(script_p.read_text(encoding="utf-8"))
        if not segs:
            return None
        from engines.subs import to_srt as _to_srt
        srt = _to_srt(segs, key="vi")
        out = work_dir / "sub.vi.srt"
        try:
            out.write_text(srt, encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
        return out, srt

    src, key = _SRT_SRC[lang]
    p = work_dir / src
    if not p.exists() and lang in _SRT_SRC_FALLBACK:
        src, key = _SRT_SRC_FALLBACK[lang]
        p = work_dir / src
    if not p.exists():
        return None
    segs = json.loads(p.read_text(encoding="utf-8"))
    # script.json dùng key zh; asr.json dùng text
    if key == "zh" and segs and isinstance(segs, list) and segs and "zh" not in segs[0] and "text" in segs[0]:
        key = "text"
    srt = to_srt(segs, key=key)
    out = work_dir / f"sub.{lang}.srt"
    try:
        out.write_text(srt, encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    return out, srt


def _clone_voice_list() -> list[dict]:
    """Giọng clone dùng chung cho cả 2 engine (registry voices/f5_voices.json)."""
    return [{"id": n, "label": f"🎙️ {n}"} for n in list_clone_voices()]


def list_voices():
    """Giọng clone (ref audio + lời) dùng chung — cả vieneu lẫn omnivoice đều
    zero-shot clone từ cùng 1 file mẫu, nên danh sách giống nhau."""
    voices = _clone_voice_list()
    return {"vieneu": voices, "omnivoice": voices}


def list_frames():
    """Danh sách PNG khung trong assets/overlays/frames."""
    try:
        from engines.render_fx import list_frame_files
        return {"frames": [p.name for p in list_frame_files()]}
    except Exception as e:  # noqa: BLE001
        return {"frames": [], "error": str(e)}


def list_brand_logos():
    """Logo kênh (assets/overlays/logos hoặc brand)."""
    try:
        from engines.render_fx import list_brand_logo_files
        return {"logos": [p.name for p in list_brand_logo_files()]}
    except Exception as e:  # noqa: BLE001
        return {"logos": [], "error": str(e)}


# ===== Thêm giọng clone (upload mẫu 3-8s -> đăng ký registry dùng chung) =====
_AUDIO_UP_EXT = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


_WH_REF = None


def _ref_asr_enabled() -> bool:
    """ASR mẫu: mặc định tắt nếu chưa có model (tránh treo tải Whisper 2GB lúc Thêm giọng).
    Bật: REF_ASR=1 hoặc REF_ASR_MODEL đã nằm trong HF cache."""
    v = (os.getenv("REF_ASR", "") or "").strip().lower()
    if v in ("0", "false", "no", "off"):
        return False
    if v in ("1", "true", "yes", "on"):
        return True
    # auto: chỉ chạy nếu snapshot model đã có local
    name = os.getenv("REF_ASR_MODEL", "base")
    try:
        from huggingface_hub import try_to_load_from_cache
        # faster-whisper dùng Systran/faster-whisper-{size}
        repo = f"Systran/faster-whisper-{name}"
        p = try_to_load_from_cache(repo, "model.bin")
        if p is None:
            p = try_to_load_from_cache(repo, "model.safetensors")
        return p is not None
    except Exception:  # noqa: BLE001
        return False


def _probe_audio_dur(path: Path) -> float:
    try:
        outp = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nk=1:nw=1", str(path)],
            capture_output=True, text=True, check=False,
        ).stdout.strip()
        return float(outp or 0)
    except Exception:  # noqa: BLE001
        return 0.0


def _transcribe_ref(path: Path) -> str:
    """Lấy transcript của clip mẫu (F5 cần ref_text). Model medium int8 nhẹ VRAM."""
    global _WH_REF
    from faster_whisper import WhisperModel
    if _WH_REF is None:
        _WH_REF = WhisperModel(
            os.getenv("REF_ASR_MODEL", "base"),
            device=os.getenv("REF_ASR_DEVICE", "cpu"),
            compute_type="int8",
        )
    segs, _ = _WH_REF.transcribe(str(path), language="vi")
    return " ".join(s.text.strip() for s in segs).strip()


def _prep_ref(raw: Path, max_dur: float = 8.0) -> tuple[Path, str, float]:
    """Chuẩn hoá clip mẫu: cắt ≤max_dur, xuất wav 24k mono. Trả (wav, ref_text, dur).

    ASR (faster-whisper) chỉ chạy khi model đã có local hoặc REF_ASR=1 — tránh treo
    UI '⏳ clone...' vì tải Whisper medium ~2GB lần đầu.
    """
    global _WH_REF
    words = []
    total = _probe_audio_dur(raw)
    text_asr = ""

    if _ref_asr_enabled():
        try:
            from faster_whisper import WhisperModel
            if _WH_REF is None:
                # Clone ref: ưu tiên CPU (tránh thiếu cublas) + model nhỏ
                name = os.getenv("REF_ASR_MODEL", "base")
                dev = os.getenv("REF_ASR_DEVICE", "cpu")
                ct = "int8" if dev == "cpu" else "int8_float16"
                print(f"[clone] ASR mẫu model={name} device={dev}...", flush=True)
                _WH_REF = WhisperModel(name, device=dev, compute_type=ct)
            segs, _ = _WH_REF.transcribe(str(raw), language="vi", word_timestamps=True)
            words = [w for s in segs for w in (s.words or [])]
            if words:
                total = words[-1].end
            text_asr = " ".join(w.word.strip() for w in words).strip()
        except Exception as e:  # noqa: BLE001
            print(f"[clone] ASR mẫu lỗi ({e}) -> convert ffmpeg, text trống", flush=True)
            words = []
    else:
        print("[clone] bỏ ASR mẫu (chưa có model / REF_ASR off) → enroll nhanh", flush=True)

    cut = 0.0
    if total > max_dur and words:
        trim_to = min(max_dur - 0.5, 7.5)
        for w in words:
            if w.end <= trim_to and w.word.strip().endswith((".", "!", "?")):
                cut = w.end
        if cut < 2.0:
            for w in words:
                if w.end <= trim_to:
                    cut = w.end
        cut = round(cut + 0.15, 2)
    elif total > max_dur:
        cut = round(min(max_dur - 0.5, 7.5), 2)

    out = raw.with_name(raw.stem + "_f5.wav")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw)]
    if cut > 0:
        cmd += ["-t", str(cut)]
    cmd += ["-ac", "1", "-ar", "24000", str(out)]
    subprocess.run(cmd, check=True)

    keep = cut if cut > 0 else total
    if words:
        text = " ".join(w.word.strip() for w in words
                        if cut <= 0 or w.end <= cut).strip()
    else:
        text = text_asr
    return out, text, round(keep or total or 0.0, 1)


def clone_voice(name: str = Form(...), file: UploadFile = File(...)):
    """Clone 1 giọng từ file mẫu (3-8s). Đăng ký vào registry chung (VieNeu/OmniVoice)."""
    name = (name or "").strip()
    if not name:
        return JSONResponse({"error": "thiếu tên giọng"}, status_code=400)
    ext = Path(file.filename or "").suffix.lower()
    if ext not in _AUDIO_UP_EXT:
        return JSONResponse({"error": f"định dạng {ext or '?'} không hỗ trợ"}, status_code=400)
    ref_dir = Path("voices") / "clone_refs"
    ref_dir.mkdir(parents=True, exist_ok=True)
    safe = hashlib.sha1(name.encode("utf-8")).hexdigest()[:10]
    ref = ref_dir / f"{safe}{ext}"
    ref.write_bytes(file.file.read())

    # Chuẩn hoá mẫu (auto-cắt ≤8s ở ranh giới câu) + transcript rồi enroll (ref+text)
    try:
        prepped, text, dur = _prep_ref(ref)
        enroll_voice(name, prepped, text)
        print(f"[clone] {name}: mẫu {dur}s" + (" (đã tự cắt ≤8s)" if dur <= 8 else ""))
    except Exception as e:  # noqa: BLE001
        import traceback
        traceback.print_exc()
        print(f"[clone] FAIL {name}: {e}", flush=True)
        return JSONResponse({"error": f"clone thất bại: {e}"}, status_code=500)
    return {"ok": True, "voice": name, "ref_sec": dur}


# Câu mẫu để nghe thử giọng + thư mục cache mẫu (đọc 1 lần, nghe lại tức thì).
SAMPLE_TEXT = "Xin chào, đây là giọng đọc thử của Pineline. Một câu tiếng Việt để bạn nghe thử chất giọng."
SAMPLE_DIR = Path("voice_samples")


def voice_sample(engine: str = TTS_ENGINE_DEFAULT, voice: str = "",
                 speed: float = 1.0):
    """Đọc câu mẫu bằng engine+giọng (+ tốc độ) để nghe thử. Cache trên đĩa.

    Lần đầu (chưa nạp model) có thể chờ ~vài chục giây; sau đó tức thì.
    """
    if engine not in TTS_ENGINES:
        return JSONResponse({"error": f"engine '{engine}' không có"}, status_code=400)
    if not voice:
        return JSONResponse({"error": "chưa chọn giọng"}, status_code=400)
    try:
        speed = float(speed or 1.0)
    except (TypeError, ValueError):
        speed = 1.0
    speed = max(0.5, min(speed, 2.0))
    SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(f"{engine}|{voice}|{speed:.2f}".encode("utf-8")).hexdigest()[:12]
    out = SAMPLE_DIR / f"{key}.wav"
    # LÀM MỚI nếu preview cũ hơn mẫu ref (đổi/lọc lại mẫu -> preview cũ lỗi thời).
    stale = False
    if out.exists():
        try:
            from engines.clone_tts import voice_ref_text
            vr = voice_ref_text(voice)
            if vr and vr[0].exists() and out.stat().st_mtime < vr[0].stat().st_mtime:
                stale = True
        except Exception:  # noqa: BLE001
            pass
    if not out.exists() or stale:
        try:
            out.unlink(missing_ok=True)
            print(f"[preview] synth {engine}/{voice} speed={speed}", flush=True)
            synth_one(engine, voice, SAMPLE_TEXT, out, speed=speed)
        except Exception as e:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            return JSONResponse({"error": str(e)}, status_code=500)
    return FileResponse(str(out), filename=out.name, media_type="audio/wav")


def tts_wav_ok(job_id: str):
    """Danh sách index seg_*.wav còn trên đĩa (size OK) — UI khỏi báo thiếu oan khi chưa có tts.json."""
    work_dir = WORK_ROOT / job_id
    tdir = work_dir / "tts"
    ids = []
    if tdir.exists():
        for f in tdir.glob("seg_*.wav"):
            try:
                if f.stat().st_size > 1000:
                    ids.append(int(f.stem.split("_")[1]))
            except Exception:  # noqa: BLE001
                pass
    return {"ids": sorted(ids), "n": len(ids)}


def regen_tts(job_id: str, req: TTSReq):
    """Lồng tiếng: mặc định RESUME (chỉ đọc câu thiếu). force=true -> đọc lại toàn bộ."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "script.json").exists():
        return JSONResponse({"error": "chưa dịch xong (thiếu script.json)"}, status_code=400)
    if req.voice:
        _save_tts_voice(work_dir, req.voice)
    sp = _resolve_speed(work_dir, req.speed)
    eng = _resolve_tts_engine(work_dir, req.engine)
    v = _resolve_voice(work_dir, req.voice)
    if not v:
        return JSONResponse({"error": "chưa chọn giọng"}, status_code=400)

    # Kiểm tra python engine TRƯỚC khi xếp hàng — tránh kẹt "starting" mãi
    try:
        from engines.clone_tts import resolve_engine_python
        py = resolve_engine_python(eng)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=400)

    # Chỉ kill worker cũ khi thật sự treo — KHÔNG kill lúc đang load/enroll bình thường
    # (trước đây "loading|enroll" trong cur_text → kill nhầm → 2 worker / mất tiến độ).
    try:
        import time as _t
        m0 = Manifest(work_dir)
        st0 = m0.stage("tts") or {}
        age = _t.time() - float(st0.get("updated_at") or 0)
        cur0 = str(st0.get("cur_text") or "").lower()
        booting = any(k in cur0 for k in (
            "starting", "xep hang", "chuan bi", "spawn", "loading", "enroll"))
        boot_limit = int(os.getenv("VIENEU_BOOT_SEC", "180"))
        # boot: cho tới boot_limit; đang đọc: 90s không cập nhật mới coi treo
        limit = boot_limit if booting else 90
        if st0.get("status") == "running" and age > limit:
            print(f"[tts] kill worker treo (age={age:.0f}s>{limit} cur={cur0[:40]!r})", flush=True)
            _kill_job_children(job_id)
            _clear_stop(job_id)
            _t.sleep(1.5)
        elif st0.get("status") == "running":
            # Đang chạy khỏe → từ chối enqueue trùng (tránh 2 vieneu_batch)
            return JSONResponse({
                "error": "TTS đang chạy",
                "progress": st0.get("progress"),
                "n_done": st0.get("n_done"),
                "cur_text": st0.get("cur_text"),
            }, status_code=409)

    except Exception as e:  # noqa: BLE001
        print(f"[tts] kill cu: {e}", flush=True)

    if not _claim_stage(job_id, "tts"):
        return JSONResponse(
            {"error": f"job đang chạy bước '{_job_any_busy(job_id)}' — bấm Dừng hoặc đợi xong"},
            status_code=409,
        )

    # Đánh running NGAY (trước queue)
    try:
        import time as _t
        m = Manifest(work_dir)
        st = m.data.setdefault("stages", {}).setdefault("tts", {})
        n_wav = len(list((work_dir / "tts").glob("seg_*.wav"))) if (work_dir / "tts").exists() else 0
        n_total = st.get("n_total")
        if not n_total and (work_dir / "script.json").exists():
            try:
                segs = json.loads((work_dir / "script.json").read_text(encoding="utf-8"))
                n_total = sum(1 for s in segs if s.get("vi"))
            except Exception:  # noqa: BLE001
                n_total = 0
        st.update({
            "status": "running", "voice": v, "speed": sp, "engine": eng, "tts_engine": eng,
            "cur_text": f"xep hang GPU… ({Path(py).name})",
            "progress": st.get("progress") or 0,
            "n_done": n_wav, "n_total": n_total or st.get("n_total"),
            "updated_at": _t.time(),
        })
        m.data["stages"]["tts"] = st
        m.save()
        _job_cache.pop(str(work_dir), None)
    except Exception as e:  # noqa: BLE001
        print(f"[tts] mark running som: {e}")
    _clear_stop(job_id)

    def _run_tts():
        try:
            _do_tts(work_dir, v, sp, eng, bool(req.force))
        finally:
            _release_stage(job_id, "tts")
    _gpu.submit(_run_tts)
    return {"started": True, "engine": eng, "voice": v, "speed": sp, "force": bool(req.force),
            "py": py}


def regen_clip(job_id: str, req: ClipReq):
    """Đọc lại DUY NHẤT 1 câu (index i) khi clip đó lỗi. Nhanh, không đụng câu khác."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "script.json").exists():
        return JSONResponse({"error": "chưa dịch xong"}, status_code=400)
    # giọng: ưu tiên yêu cầu, không thì lấy đúng giọng job đang dùng
    m = Manifest(work_dir)
    voice = req.voice or (m.stage("tts") or {}).get("voice", "") or _resolve_voice(work_dir, None)
    engine = _resolve_tts_engine(work_dir, getattr(req, "engine", None))
    try:
        entry = _clone_resynth(work_dir, req.i, engine, voice or "")
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=500)
    return {"ok": True, "clip": entry}


def job_srt(job_id: str, lang: str):
    """Sinh .srt từ asr.json (zh) / script.json (vi), ghi ra file trong job rồi
    trả về cho tải. Chạy được cả với job cũ."""
    if lang not in _SRT_SRC:
        return JSONResponse({"error": "lang phải là zh hoặc vi"}, status_code=400)
    res = _write_srt(WORK_ROOT / job_id, lang)
    if res is None:
        return JSONResponse({"error": f"chưa có nguồn cho .srt {lang}"}, status_code=404)
    _, srt = res
    return PlainTextResponse(
        srt, media_type="application/x-subrip",
        headers={"Content-Disposition": f'attachment; filename="sub.{lang}.srt"'},
    )


def _reveal_path(target: Path) -> None:
    """Mở trình quản lý file, bôi sẵn đúng file (nếu target là file) hoặc mở thư mục."""
    is_file = target.is_file()
    if sys.platform == "win32":
        if is_file:
            subprocess.Popen(["explorer", "/select,", str(target)])
        else:
            os.startfile(str(target))  # noqa: S606
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-R", str(target)] if is_file else ["open", str(target)])
    else:
        subprocess.Popen(["xdg-open", str(target if not is_file else target.parent)])


class SourcePathIn(BaseModel):
    path: str
    move: bool = False  # True = move thay vì copy (tiết kiệm ổ với file lớn)


async def upload_source(job_id: str, file: UploadFile = File(...)):
    """Import source video qua upload (stream, không nhét cả file vào RAM).

    Thay bước download: ghi work/<job>/source.<ext>, mark download=done.
    File lớn (>~1GB) nên dùng /source-path thay vì upload HTTP.
    """
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    ext = Path(file.filename or "").suffix.lower()
    if ext not in _VIDEO_EXT:
        return JSONResponse(
            {"error": f"định dạng {ext or '?'} không hỗ trợ (dùng {', '.join(sorted(_VIDEO_EXT))})"},
            status_code=400,
        )
    _clear_job_sources(work_dir)
    dest = work_dir / f"source{ext}"
    try:
        with dest.open("wb") as out:
            while True:
                chunk = await file.read(8 * 1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
    except Exception as e:  # noqa: BLE001
        try:
            dest.unlink(missing_ok=True)
        except OSError:
            pass
        return JSONResponse({"error": f"ghi file lỗi: {e}"}, status_code=500)
    if not dest.exists() or dest.stat().st_size < 1024:
        return JSONResponse({"error": "file rỗng / quá nhỏ"}, status_code=400)
    return _finalize_imported_source(
        work_dir, dest, orig_name=file.filename, source_kind="imported_upload",
    )


def import_source_path(job_id: str, body: SourcePathIn):
    """Import source từ đường dẫn local (cùng máy server) — phù hợp file multi-GB."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    src = Path(body.path.strip().strip('"')).expanduser()
    try:
        src = src.resolve(strict=True)
    except FileNotFoundError:
        return JSONResponse({"error": f"không thấy file: {body.path}"}, status_code=400)
    except OSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    if not src.is_file():
        return JSONResponse({"error": "path không phải file"}, status_code=400)
    ext = src.suffix.lower()
    if ext not in _VIDEO_EXT:
        return JSONResponse(
            {"error": f"định dạng {ext or '?'} không hỗ trợ (dùng {', '.join(sorted(_VIDEO_EXT))})"},
            status_code=400,
        )
    # Không cho path nằm trong chính folder job (tránh copy đè chính nó)
    try:
        src.relative_to(work_dir.resolve())
        # đã là file trong job -> chỉ mark done
        return _finalize_imported_source(
            work_dir, src, orig_name=src.name, source_kind="imported_inplace",
        )
    except ValueError:
        pass

    try:
        dest, how = _place_source(src, work_dir, bool(body.move))
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": f"copy/move lỗi: {e}"}, status_code=500)
    return _finalize_imported_source(
        work_dir, dest, orig_name=src.name, source_kind="imported_path", source_mode=how,
    )


async def upload_audio(job_id: str, file: UploadFile = File(...)):
    """Nhập 1 file audio lồng tiếng LÀM SẴN ở ngoài (từ SRT) để dùng cho mux.

    Lưu thành work/<job>/dub.<ext>, ghi manifest['dub'] source=imported. Đây là
    nguồn audio thay thế cho TTS nội bộ — mux sẽ ưu tiên track này nếu có.
    """
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    ext = Path(file.filename or "").suffix.lower()
    if ext not in _AUDIO_EXT:
        return JSONResponse(
            {"error": f"định dạng {ext or '?'} không hỗ trợ (dùng {', '.join(sorted(_AUDIO_EXT))})"},
            status_code=400,
        )
    # xoá dub cũ (mọi đuôi) trước khi ghi mới
    for old in work_dir.glob("dub.*"):
        try:
            old.unlink()
        except Exception:  # noqa: BLE001
            pass
    dest = work_dir / f"dub{ext}"
    dest.write_bytes(await file.read())
    dur = _audio_dur(dest)
    m = Manifest(work_dir)
    m.data["dub"] = {
        "source": "imported", "file": dest.name,
        "orig_name": file.filename, "dur": dur,
    }
    m.save()
    return {"ok": True, "file": dest.name, "dur": dur}


def delete_audio(job_id: str):
    """Bỏ audio ngoài đã nhập -> quay lại dùng TTS nội bộ."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "manifest.json").exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    for old in work_dir.glob("dub.*"):
        try:
            old.unlink()
        except Exception:  # noqa: BLE001
            pass
    m = Manifest(work_dir)
    m.data.pop("dub", None)
    m.save()
    return {"ok": True}


def _translate_batch_size() -> int:
    """Cỡ lô dịch — đọc TRANSLATE_BATCH (mặc định 20). Không hardcode 100."""
    try:
        from core.config import get as _cfg_get
        return max(5, int(_cfg_get("TRANSLATE_BATCH", "20") or 20))
    except Exception:  # noqa: BLE001
        try:
            return max(5, int(os.getenv("TRANSLATE_BATCH") or 20))
        except Exception:  # noqa: BLE001
            return 20


def _translate_flow(work_dir: Path, target: str, model: str | None,
                    review_model: str | None, review_only: bool,
                    mode: str | None = None):
    """Luồng dịch: (tùy chọn) DỊCH NHÁP rồi (tùy chọn) SOÁT lại lượt 2.

    - review_only=True: chỉ soát bản dịch có sẵn (bằng review_model).
    - review_model có, review_only=False: DỊCH 2 LƯỢT (nháp bằng model, soát bằng
      review_model — vd gemini nháp nhanh -> minimax soát chính xác).
    - còn lại: dịch 1 lượt bằng model."""
    try:
        batch = _translate_batch_size()
        if not review_only:
            _run_translate_engine(work_dir, batch=batch, target=target, force=True, model=model or None, mode=mode)
        if review_only or review_model:
            _run_translate_engine(work_dir, batch=min(40, max(batch, 20)), target=target, review_only=True, model=review_model or None)
    except Exception as e:  # noqa: BLE001
        print(f"[translate flow] job {work_dir.name} lỗi: {e}")


def retranslate_job(job_id: str, req: TranslateReq):
    """Dịch job: 1 lượt, HOẶC 2 lượt (nháp + soát), HOẶC chỉ soát bản có sẵn.
    Chạy nền. Lưu ý: dịch/soát lại xong thì TTS cũ lỗi thời -> Tạo giọng lại."""
    work_dir = WORK_ROOT / job_id
    if req.review_only:
        if not (work_dir / "script.json").exists():
            return JSONResponse({"error": "chưa có bản dịch để soát"}, status_code=400)
    elif not (work_dir / "asr.json").exists():
        return JSONResponse({"error": "chưa có asr.json (nhận diện trước)"}, status_code=400)
    target = Manifest(work_dir).data.get("request", {}).get("target", "Tiếng Việt")
    busy = _busy_response(job_id, work_dir)
    if busy:
        return busy
    if not _claim_stage(job_id, "translate"):
        return JSONResponse({"error": "đã nhận lệnh trước đó — không gửi trùng"}, status_code=409)
    # Đánh running NGAY (trước hàng _gpu) — JOB_WORKERS=1 hay xếp sau fill/TTS
    # khiến UI tưởng nút chết trong khi task còn pending trong queue.
    try:
        m = Manifest(work_dir)
        st = m.data.setdefault("stages", {}).setdefault("translate", {})
        mode_s = (req.mode or "batch") if not req.review_only else "review"
        batch = _translate_batch_size()
        st.update({
            "status": "running",
            "progress": 0,
            "cur_text": (
                f"xếp hàng · {mode_s}"
                + (f" lô {batch}" if not req.review_only else "")
                + "…"
            ),
            "mode": mode_s,
            "model": req.model,
            "updated_at": time.time(),
        })
        m.data["stages"]["translate"] = st
        m.save()
    except Exception as e:  # noqa: BLE001
        print(f"[translate] mark queued lỗi: {e}", flush=True)

    def _run_translate():
        try:
            _translate_flow(work_dir, target, req.model, req.review_model,
                            req.review_only, req.mode)
        finally:
            _release_stage(job_id, "translate")
    _gpu.submit(_run_translate)
    return {"started": True, "model": req.model, "review_model": req.review_model,
            "mode": req.mode, "review_only": req.review_only,
            "batch": _translate_batch_size()}


def mux_job(job_id: str, req: MuxReq):
    """Render video localize -> output.mp4 (che watermark/hardsub + sub Việt + OCR
    overlay + trộn nền Demucs/giọng Việt). Chạy nền."""
    work_dir = WORK_ROOT / job_id
    has_dub = (work_dir / "tts.json").exists() or bool(Manifest(work_dir).data.get("dub"))
    if not has_dub:
        return JSONResponse({"error": "chưa có audio (tạo giọng / nhập audio trước)"}, status_code=400)
    busy = _busy_response(job_id, work_dir)
    if busy:
        return busy
    _clear_stop(job_id)
    res = _submit_claimed(
        _gpu, job_id, "mux", _do_render, work_dir, True, req.audio_mode, req.voice_vol, req.orig_vol,
        req.add_sub, req.fit, req.resolution or "source", (req.flip or "").strip(),
        float(req.zoom or 1.12), bool(req.motion), bool(req.lut),
        (req.grain or "weak"), bool(getattr(req, "brand", False)),
        (getattr(req, "brand_text", None) or ""),
        (getattr(req, "frame", None) or "off"),
        (getattr(req, "brand_mode", None) or "off"),
        (getattr(req, "brand_logo", None) or "off"),
        (getattr(req, "vbitrate", None) or "8M"))
    return res or {"started": True}


def assemble_job(job_id: str, fit: bool = True, max_speed: float = 1.0):
    """Ghép clip TTS thành 1 track.
    fit=True: đủ câu, ghép cạnh, bắt kịp khoảng trống (max_speed=1 = không nén).
    fit=False: naive (có thể đè) -> dub_tts.wav."""
    work_dir = WORK_ROOT / job_id
    if not (work_dir / "tts.json").exists():
        return JSONResponse({"error": "chưa có audio (tạo giọng trước)"}, status_code=400)
    busy = _busy_response(job_id, work_dir)
    if busy:
        return busy
    if not _claim_stage(job_id, "assemble"):
        return JSONResponse({"error": "đã nhận lệnh trước đó — không gửi trùng"}, status_code=409)
    from engines.assemble import assemble, assemble_fit
    try:
        return assemble_fit(work_dir, max_speed=max_speed) if fit else assemble(work_dir)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=500)
    finally:
        _release_stage(job_id, "assemble")


def get_split_plan(job_id: str, target_hours: float | None = None):
    """Xem trước kế hoạch chia part + cờ will_auto_split theo batch_config."""
    work_dir = WORK_ROOT / job_id
    video = _find_video(work_dir)
    if not video or not video.exists():
        return JSONResponse({"error": "chưa có video nguồn"}, status_code=400)
    from engines.split_parts import MIN_SPLIT_HOURS, compute_smart_plan, probe_duration
    try:
        bc = batch_config.load()
        th = float(target_hours if target_hours is not None else (bc.get("auto_split_hours") or 2.5))
        min_h = float(bc.get("auto_split_min_h") or MIN_SPLIT_HOURS)
        dur = probe_duration(video)
        plan = compute_smart_plan(video, target_hours=th)
        will = bool(bc.get("auto_split", True)) and dur >= min_h * 3600.0
        return {
            "job_id": job_id,
            "duration_sec": dur,
            "duration_hours": round(dur / 3600.0, 2),
            "total_parts": len(plan),
            "parts": plan,
            "auto_split_enabled": bool(bc.get("auto_split", True)),
            "auto_split_min_h": min_h,
            "auto_split_hours": th,
            "will_auto_split": will,
            "message": (
                f"Xếp hàng/run-all sẽ TỰ chia {len(plan)} part (~{th}h/part)"
                if will else
                f"Dưới ngưỡng {min_h}h hoặc auto_split tắt — chạy 1 job"
            ),
        }
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=500)


def api_split_job_parts(job_id: str, target_hours: float = 2.5):
    """Chia video dài thành các sub-jobs (Part 1, Part 2...) chạy pipeline độc lập chống lệch time."""
    from engines.split_parts import split_job_to_subjobs
    try:
        return split_job_to_subjobs(job_id, target_hours=target_hours, work_root=WORK_ROOT)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=500)


def api_merge_job_parts(job_id: str):
    """Ghép các sub-jobs đã render xong thành output_full.mp4 (concat lossless)."""
    from engines.split_parts import merge_job_parts
    try:
        return merge_job_parts(job_id, work_root=WORK_ROOT)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=500)


def reveal_job(job_id: str, file: str | None = None):
    """Mở thư mục job trong Explorer, chọn sẵn 1 file. Không truyền file -> chọn
    video. file=sub.zh.srt/sub.vi.srt mà chưa có -> tự sinh trước rồi mới mở.

    Chỉ hợp lý vì server chạy CÙNG MÁY người dùng (bản dùng riêng, localhost).
    """
    root = WORK_ROOT.resolve()
    work_dir = (WORK_ROOT / job_id).resolve()
    if work_dir.parent != root or not work_dir.is_dir():
        return JSONResponse({"error": "not found"}, status_code=404)

    if file:
        if file in _SRT_FILES and not (work_dir / file).exists():
            _write_srt(work_dir, _SRT_FILES[file])   # sinh .srt nếu chưa có
        target = (work_dir / file).resolve()
        if work_dir not in target.parents or not target.is_file():
            return JSONResponse({"error": "file not found"}, status_code=404)
    else:
        target = _find_video(work_dir) or work_dir

    try:
        _reveal_path(target)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=500)
    return {"ok": True, "path": str(target)}


def job_file(job_id: str, path: str):
    """Phục vụ 1 file BÊN TRONG work/<job_id>/ (asr.json, script.json, mp3...).

    Chặn path traversal: file phải nằm trong đúng thư mục job. FileResponse tự
    đoán media-type + hỗ trợ Range (nghe/tua audio được).

    Khi đang render: không stream output.mp4 (file đang ghi/đổi size -> ASGI
    Content-Length lỗi). Trả 409 để UI biết chờ.

    JSON/text (script.json, asr.json…): đọc snapshot vào RAM rồi trả Response —
    tránh race khi stage dịch/ASR đang ghi đè file (Content-Length lệch).
    """
    root = WORK_ROOT.resolve()
    work_dir = (WORK_ROOT / job_id).resolve()
    if work_dir.parent != root or not work_dir.is_dir():
        return JSONResponse({"error": "not found"}, status_code=404)
    # chặn file tạm / partial
    if path.startswith(".") or path.endswith(".partial") or ".partial." in path.lower():
        return JSONResponse({"error": "not found"}, status_code=404)
    target = (work_dir / path).resolve()
    if work_dir not in target.parents or not target.is_file():
        return JSONResponse({"error": "not found"}, status_code=404)
    if target.name.lower() == "output.mp4":
        try:
            st = (Manifest(work_dir).stage("mux") or {})
            if st.get("status") == "running":
                return JSONResponse(
                    {"error": "đang render — mở lại output sau khi xong"},
                    status_code=409)
        except Exception:  # noqa: BLE001
            pass
    # Snapshot text/json — không stream FileResponse trên file đang lớn dần
    suffix = target.suffix.lower()
    if suffix in {".json", ".txt", ".srt", ".csv", ".log", ".md"}:
        try:
            data = target.read_bytes()
        except OSError as e:
            return JSONResponse({"error": str(e)}, status_code=409)
        media = "application/json" if suffix == ".json" else "text/plain; charset=utf-8"
        return Response(
            content=data, media_type=media,
            headers={
                "Content-Disposition": f'inline; filename="{target.name}"',
                # UI poll script.json/asr.json khi đang dịch — cấm cache trình duyệt
                # (cache cũ hay hiện sai "575 câu trống" dù file đã đủ).
                "Cache-Control": "no-store, no-cache, must-revalidate",
                "Pragma": "no-cache",
            },
        )
    return FileResponse(str(target), filename=target.name)


def delete_job(job_id: str):
    """Xoá 1 job = xoá cả thư mục work/<job_id>/ (video, audio, manifest...).

    An toàn: chỉ cho xoá thư mục nằm NGAY trong WORK_ROOT (chặn '..'/đường dẫn lạ).
    LƯU Ý: xoá vĩnh viễn, không phục hồi được.
    """
    root = WORK_ROOT.resolve()
    work_dir = (WORK_ROOT / job_id).resolve()
    # chặn path traversal: work_dir phải là con trực tiếp của root
    if work_dir.parent != root or not work_dir.is_dir():
        return JSONResponse({"error": "not found"}, status_code=404)
    try:
        shutil.rmtree(work_dir)
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=500)
    return {"deleted": job_id}


# ===== Hongguo Downloader bridge (local :8000) =====


import core.job_queue as job_queue
import core.batch_config as batch_config

job_queue.WORK_ROOT = WORK_ROOT
_UNDER_PYTEST = "pytest" in sys.modules
if not _UNDER_PYTEST:
    job_queue._load()
job_queue.set_runner(_queue_run_one)
job_queue.set_stop_hook(_stop_job)
job_queue.set_clear_stop_hook(_clear_stop)


# ===== Route tách file (đợt 7): UI, Hongguo, Agent =====
# Phải nạp sau mọi hàm/model lõi ở trên; các module này đọc server qua `import server as S`.
# Re-export cycle-safe: nếu routes_* import server trước khi tự định nghĩa xong symbol,
# bỏ qua from-import (tránh ImportError); include_router vẫn dùng .router đã có sớm.
import http_routes.routes_ui as routes_ui  # noqa: E402
import http_routes.routes_hg as routes_hg  # noqa: E402
import http_routes.routes_agent as routes_agent  # noqa: E402


def _reexport_route_symbols(mod, names: tuple[str, ...]) -> bool:
    missing = [n for n in names if not hasattr(mod, n)]
    if missing:
        return False
    g = globals()
    for n in names:
        g[n] = getattr(mod, n)
    return True


_reexport_route_symbols(routes_ui, (
    "_html_file",
    "find_index",
    "index",
    "ui3",
    "ui_hongguo",
    "ui_hongguo2",
))
_reexport_route_symbols(routes_hg, (
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
))
_reexport_route_symbols(routes_agent, (
    "AgentAvSyncHealReq",
    "AgentAvSyncScanReq",
    "AgentHealBatchReq",
    "AgentQaGateReq",
    "_AV_SYNC_HOOKS",
    "_HEAL_HOOKS",
    "_agent_asr_force",
    "_agent_asr_set_engine",
    "_agent_assemble_fit",
    "_agent_core",
    "_agent_edit_line",
    "_agent_get_hold",
    "_agent_get_job",
    "_agent_heal_stale",
    "_agent_mux_force_av",
    "_agent_mux_retry",
    "_agent_mux_run",
    "_agent_notify",
    "_agent_queue_add",
    "_agent_reset_state",
    "_agent_resume",
    "_agent_run_stage",
    "_agent_script_review",
    "_agent_script_review_legacy",
    "_agent_set_hold",
    "_agent_stop_job",
    "_agent_translate_fill",
    "_agent_translate_rerun",
    "_agent_tts_run_simple",
    "_agent_tts_set_voice",
    "_job_in_pipeline",
    "api_agent_av_sync",
    "api_agent_av_sync_heal",
    "api_agent_av_sync_heal_batch",
    "api_agent_av_sync_scan",
    "api_agent_chat",
    "api_agent_confirm",
    "api_agent_heal_failed",
    "api_agent_pending",
    "api_agent_qa_gate",
    "api_agent_reset_state",
    "api_agent_resume",
    "api_agent_review",
    "api_agent_review_diff",
    "api_agent_scan_failed",
    "api_agent_status",
    "api_agent_watch_once",
))

app.include_router(routes_ui.router)
app.include_router(routes_hg.router)
app.include_router(routes_agent.router)
try:
    import http_routes.routes_films as routes_films
    app.include_router(routes_films.router)
except Exception as _e_films:
    print(f"[warning] Khong nap duoc routes_films: {_e_films}")

try:
    import http_routes.routes_uploader_settings as routes_uploader_settings
    app.include_router(routes_uploader_settings.router)
except Exception as _e_up:
    print(f"[warning] Khong nap duoc routes_uploader_settings: {_e_up}")


@app.on_event("startup")
def _start_agent_watch():
    try:
        from agents.agent_watch import start_watcher
        on = start_watcher(WORK_ROOT, list_jobs=list_jobs, hooks=_HEAL_HOOKS)
        if on:
            print("[startup] Agent watcher ON (AGENT_WATCH=1)")
        else:
            print("[startup] Agent watcher OFF (set AGENT_WATCH=1 để bật)")
    except Exception as e:  # noqa: BLE001
        print(f"[startup] agent watch lỗi: {e}")


@app.on_event("startup")
def _start_auto_publisher():
    try:
        import agents.auto_publisher as auto_publisher
        auto_publisher.start_worker()
        print("[startup] Auto-publisher worker started")
    except Exception as e:  # noqa: BLE001
        print(f"[startup] auto-publisher lỗi: {e}")


def get_available_llm_models():
    """Trả về danh sách toàn bộ các model LLM khả dụng (llama-server :8083, Ollama, 9router)."""
    try:
        from engines.llm import list_available_models
        return list_available_models()
    except Exception as e:
        return {"models": [], "default": "", "error": str(e)}


# Queue / jobs / assets / fs: SSOT path map (attach sau khi mọi handler đã định nghĩa).
from pineline.server.routes import queue as _pineline_queue  # noqa: E402
from pineline.server.routes import jobs as _pineline_jobs  # noqa: E402
from pineline.server.routes import assets as _pineline_assets  # noqa: E402
from pineline.server.routes import fs as _pineline_fs  # noqa: E402

_HERE = sys.modules[__name__]
_pineline_queue.attach(_HERE)
_pineline_jobs.attach(_HERE)
_pineline_assets.attach(_HERE)
_pineline_fs.attach(_HERE)
app.include_router(_pineline_queue.router)
app.include_router(_pineline_jobs.router)
app.include_router(_pineline_assets.router)
app.include_router(_pineline_fs.router)


if __name__ == "__main__":
    import argparse
    import os

    import uvicorn

    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.getenv("PORT", "8805")))
    args = ap.parse_args()

    # 1 bản / cổng: bản thứ 2 sẽ chạy startup (kill engine "orphan" = engine của bản đang chạy).
    import msvcrt
    _inst_lock = open(Path(__file__).resolve().parent / f".server_{args.port}.lock", "a+")
    _inst_lock.seek(0)
    try:
        msvcrt.locking(_inst_lock.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        print(f"Đã có server PinelineV4 khác giữ cổng {args.port} — thoát.", flush=True)
        raise SystemExit(1)

    print(f"Mở http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)
