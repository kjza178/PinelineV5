# -*- coding: utf-8 -*-
"""Chuẩn hóa video thư viện (D:\\Lib\\<mùa>) — hàng đợi NỀN trong sidecar :8802 (2026-11-17/18).

Vì sao: file gộp cũ (`-c copy` từ các tập tải lẻ lệch tiếng/codec/độ phân giải, gói hỏng) làm Pineline báo
lỗi giải mã (h264 «Invalid data… no frame…»). Nút 📐 trên Films UI chuẩn hóa 1 mùa; nút «Chuẩn hóa đã tick»
xếp nhiều mùa — mỗi mùa được KIỂM trước:
  - có metadata comment `pineline_norm_v1` (đã qua chuẩn hóa này)            → bỏ qua;
  - `merge_check.json` ok (gộp mới đã kiểm tập + mối nối, hg_merge_check)    → bỏ qua;
  - còn lại (gộp cũ / gộp lỗi / không rõ)                                     → chuẩn hóa.
Chạy LẦN LƯỢT (1 ffmpeg / lúc). Mùa không chuẩn hóa được → state=failed + dòng lỗi ffmpeg.
Log: console :8802 (không làm rối :8801) + `work/logs/lib_normalize.log` + `log` trong status (Films UI).
"""
from __future__ import annotations

import collections
import json
import os
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any

MARK = "pineline_norm_v1"
_lock = threading.Lock()
_items: dict[str, dict[str, Any]] = {}      # name → trạng thái
_order: list[str] = []                       # thứ tự hiển thị (mới nhất cuối)
_queue: list[str] = []
_worker: threading.Thread | None = None
_logbuf: collections.deque = collections.deque(maxlen=400)
_log_path: Path | None = Path(__file__).resolve().parents[1] / "work" / "logs" / "lib_normalize.log"
_NOWIN = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def lib_root() -> Path:
    return Path(os.getenv("PINELINE_LIB_ROOT") or r"D:\Lib")


def set_log_dir(d: Path) -> None:
    global _log_path
    _log_path = Path(d) / "lib_normalize.log"


def _log(name: str, msg: str) -> None:
    line = f"{datetime.now():%H:%M:%S} [normalize] {name}: {msg}"
    print(line, flush=True)
    _logbuf.append(line)
    if _log_path:
        try:
            _log_path.parent.mkdir(parents=True, exist_ok=True)
            with _log_path.open("a", encoding="utf-8") as f:
                f.write(f"{datetime.now():%Y-%m-%d} {line}\n")
        except OSError:
            pass


def _fmt_sec(s: float) -> str:
    s = int(max(0, s))
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}"


# ---------------------------------------------------------------------------
# Tìm file + kiểm
# ---------------------------------------------------------------------------
def find_merged(name: str) -> tuple[Path | None, str]:
    """→ (file gộp, lỗi). Chặn tên có `..` / `\\` (chỉ 1 cấp dưới thư viện)."""
    name = (name or "").strip()
    root = lib_root()
    if not name or name in (".", "..") or any(c in name for c in "/\\:") or ".." in name:
        return None, "tên mùa không hợp lệ"
    folder = root / name
    if not folder.is_dir():
        return None, f"không thấy thư mục trong {root}"
    for c in (folder / "merged.mp4", *sorted(folder.glob("*(merged).mp4"))):
        if c.is_file():
            return c, ""
    mp4s = [f for f in folder.glob("*.mp4") if not f.name.startswith(("S01E", "第"))
            and ".norm." not in f.name and f.stat().st_size > 50 * 1024 * 1024]
    if mp4s:
        return max(mp4s, key=lambda f: f.stat().st_size), ""
    return None, "chưa có file gộp (cần ghép trước)"


def _probe(path: Path) -> dict:
    try:
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration:format_tags=comment:stream=codec_type,codec_name,width,height,sample_rate,channels,"
             "avg_frame_rate", "-of", "json", str(path)],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60,
            creationflags=_NOWIN)
        return json.loads(r.stdout or "{}") or {}
    except Exception:  # noqa: BLE001
        return {}


def _brief(pr: dict) -> str:
    bits = []
    for st in pr.get("streams") or []:
        if st.get("codec_type") == "video":
            bits.append(f"{st.get('codec_name')} {st.get('width')}x{st.get('height')}")
        elif st.get("codec_type") == "audio":
            bits.append(f"{st.get('codec_name')} {st.get('sample_rate')}Hz {st.get('channels')}ch")
    return " · ".join(bits) or "ffprobe không đọc được"


def check(path: Path) -> dict[str, Any]:
    """{need: bool, why: str, info: str}."""
    path = Path(path)
    pr = _probe(path)
    info = _brief(pr)
    comment = str(((pr.get("format") or {}).get("tags") or {}).get("comment") or "")
    if MARK in comment:
        return {"need": False, "why": "đã chuẩn hóa trước đó", "info": info}
    mc = path.parent / "merge_check.json"
    if mc.is_file():
        try:
            rep = json.loads(mc.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            rep = {}
        same = (not rep.get("merged_file")) or rep.get("merged_file") == path.name
        fresh = mc.stat().st_mtime >= path.stat().st_mtime - 120
        if rep.get("ok") is True and same and fresh:
            return {"need": False, "why": f"gộp mới đã kiểm tập + mối nối ({rep.get('policy') or '?'})",
                    "info": info}
        if rep.get("ok") is False:
            return {"need": True, "why": f"lần gộp báo lỗi: {str(rep.get('error') or '')[:120]}", "info": info}
    if not pr.get("streams"):
        return {"need": True, "why": "ffprobe không đọc được stream", "info": info}
    return {"need": True, "why": "gộp cũ chưa kiểm/chuẩn hóa", "info": info}


# ---------------------------------------------------------------------------
# Hàng đợi
# ---------------------------------------------------------------------------
def enqueue(names: list[str], *, force: bool = False, front: bool = False) -> dict[str, Any]:
    added, already = [], []
    with _lock:
        for n in [str(x).strip() for x in names if str(x).strip()]:
            cur = _items.get(n)
            if cur and cur.get("state") in ("queued", "checking", "running"):
                already.append(n)
                continue
            _items[n] = {"name": n, "state": "queued", "force": bool(force), "queued_at": time.time(),
                         "pct": 0.0, "n_err": 0}
            if n in _order:
                _order.remove(n)
            _order.append(n)
            if front:
                _queue.insert(0, n)
            else:
                _queue.append(n)
            added.append(n)
        del _order[:-200]
        _ensure_worker_locked()
    if added:
        _log("hàng đợi", f"+{len(added)} mùa{' (bắt buộc chạy)' if force else ''}: {', '.join(added[:10])}"
             + (" …" if len(added) > 10 else ""))
    return {"ok": True, "added": added, "already": already, "queue": len(_queue)}


def cancel_queued() -> dict[str, Any]:
    with _lock:
        gone = list(_queue)
        _queue.clear()
        for n in gone:
            if n in _items:
                _items[n].update(state="cancelled", why="huỷ khỏi hàng đợi")
    if gone:
        _log("hàng đợi", f"huỷ {len(gone)} mùa chưa chạy")
    return {"ok": True, "cancelled": gone}


def _ensure_worker_locked() -> None:
    global _worker
    if _queue and not (_worker and _worker.is_alive()):
        _worker = threading.Thread(target=_work_loop, name="lib-normalize", daemon=True)
        _worker.start()


def _set(name: str, **kw: Any) -> dict:
    with _lock:
        st = _items.setdefault(name, {"name": name})
        st.update({k: v for k, v in kw.items() if v is not None})
        return dict(st)


def _work_loop() -> None:
    while True:
        with _lock:
            if not _queue:
                return
            name = _queue.pop(0)
            force = bool((_items.get(name) or {}).get("force"))
        try:
            _process(name, force)
        except Exception as e:  # noqa: BLE001
            _set(name, state="failed", error=str(e)[:300], ended=time.time())
            _log(name, f"❌ lỗi: {e}")


def _process(name: str, force: bool) -> None:
    _set(name, state="checking", started=time.time())
    path, err = find_merged(name)
    if path is None:
        _set(name, state="failed", error=err, ended=time.time())
        _log(name, f"❌ {err}")
        return
    ck = check(path)
    _set(name, file=path.name, info=ck["info"], why=ck["why"])
    if not ck["need"] and not force:
        _set(name, state="skipped", ended=time.time())
        _log(name, f"⏭ bỏ qua — {ck['why']} [{ck['info']}]")
        return
    _log(name, f"▶ chuẩn hóa {path.name} — {ck['why']}{' (bắt buộc)' if force and not ck['need'] else ''} "
               f"[{ck['info']}]")
    _set(name, state="running", phase="start", started=time.time())
    last = {"pct": -100.0, "t": 0.0, "phase": ""}

    def on_progress(d: dict) -> None:
        snap = _set(name, **d)
        pct = float(snap.get("pct") or 0)
        now = time.time()
        ph = str(d.get("phase") or "")
        if ph != last["phase"] or pct - last["pct"] >= 10 or now - last["t"] >= 120:
            last.update(pct=pct, t=now, phase=ph)
            _log(name, f"[{ph}] {describe(_with_eta(snap))}")

    import agents.hongguo_bridge as hg
    res = hg.normalize_merged_file(path, target_wh=(1920, 1080), on_progress=on_progress, auto_orient=True)
    if res.get("ok"):
        st = _set(name, state="done", phase="done", pct=100.0, encoder=res.get("encoder"),
                  target=res.get("target"), n_err=res.get("n_err", 0), ended=time.time())
        _log(name, f"✅ {describe(_with_eta(st))}")
    else:
        tail = res.get("error_tail") or []
        st = _set(name, state="failed", error=res.get("error") or "thất bại", error_tail=tail,
                  last_err=tail[-1] if tail else "", ended=time.time())
        _log(name, f"❌ {describe(st)}")
        for ln in tail[-8:]:
            _log(name, f"   ffmpeg: {ln}")


# ---------------------------------------------------------------------------
# Trạng thái
# ---------------------------------------------------------------------------
def _with_eta(st: dict) -> dict:
    st = dict(st)
    end = st.get("ended") or time.time()
    st["elapsed"] = round(end - float(st.get("started") or end), 1)
    pct = float(st.get("pct") or 0)
    if st.get("state") == "running" and pct >= 1 and st["elapsed"] >= 5:
        st["eta_sec"] = round(st["elapsed"] * (100 - pct) / pct)
    return st


def describe(st: dict) -> str:
    s = st.get("state")
    if s == "queued":
        return "⏳ chờ tới lượt"
    if s == "checking":
        return "🔎 đang kiểm file…"
    if s == "skipped":
        return f"⏭ bỏ qua — {st.get('why') or ''}"
    if s == "cancelled":
        return "🚫 đã huỷ"
    if s == "done":
        return (f"✅ xong sau {_fmt_sec(st.get('elapsed') or 0)} → {st.get('target') or ''} "
                f"({st.get('encoder') or '?'})" + (f" · bỏ qua {st['n_err']} dòng lỗi giải mã" if st.get("n_err") else ""))
    if s == "failed":
        return f"❌ {st.get('error') or '?'}" + (f" — {st['last_err']}" if st.get("last_err") else "")
    ph = st.get("phase") or ""
    if ph in ("probe", "start"):
        return "đang đọc thông tin file…"
    if ph == "replace":
        return "encode xong — đang thay file gốc…"
    bits = [("🔁 libx264 · " if ph == "retry" else "") + f"{float(st.get('pct') or 0):.1f}%"]
    if st.get("out_sec") is not None and st.get("dur"):
        bits.append(f"{_fmt_sec(st['out_sec'])}/{_fmt_sec(st['dur'])}")
    if st.get("speed"):
        bits.append(f"tốc độ {st['speed']}")
    if st.get("eta_sec"):
        bits.append(f"còn ~{_fmt_sec(st['eta_sec'])}")
    if st.get("n_err"):
        bits.append(f"{st['n_err']} lỗi giải mã")
    return " · ".join(bits)


def status(name: str | None = None, *, log_lines: int = 80) -> dict[str, Any]:
    with _lock:
        items = [_with_eta(_items[n]) for n in _order if n in _items]
        qn = len(_queue)
        running = bool(_worker and _worker.is_alive())
    for it in items:
        it["text"] = describe(it)
        it.pop("force", None)
    if name is not None:
        st = next((x for x in items if x["name"] == name), None)
        return {"ok": True, "name": name, "found": bool(st), **(st or {"state": "none"})}
    cnt = collections.Counter(x["state"] for x in items)
    return {"ok": True, "worker": running, "queue": qn, "counts": dict(cnt), "items": items,
            "log": list(_logbuf)[-log_lines:]}
