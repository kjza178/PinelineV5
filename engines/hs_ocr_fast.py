"""hs_ocr_fast.py — OCR hardsub NHANH cho luồng simple (SIMPLE_ZH_SOURCE) — fix 2026-11-13.

Vì sao: hardsub_asr.extract_hardsub_cues OCR MỌI khung 2 fps (≈16.700 khung / 2h19) trên CPU,
ghi JPG ra đĩa → hàng giờ. Phụ đề đứng yên 1–4 s nên phần lớn khung là đọc lại đúng câu cũ.

Cách làm (đo trên 1efd1014ac77_p03: nền phim chuyển động liên tục → so ảnh/mặt nạ chữ KHÔNG giảm được
số khung đáng tin cậy, nên tăng tốc bằng 3 việc chắc chắn):
  1. OCR_HS_FPS = 1 khung/s (cũ 2) — một nửa số khung; phụ đề thường hiện ≥ 1 s.
  2. ffmpeg giải mã DẢI phụ đề (crop theo hardsub_band.json, cả x), xám, đẩy qua pipe (không ghi JPG).
     Khung gần như giống hệt khung trước (MAD < OCR_HS_SAME, cảnh tĩnh) → dùng lại chữ, không OCR.
  3. OCR: RapidOCR trên GPU (CUDAExecutionProvider) khi OCR_HS_GPU=1 và onnxruntime có CUDA; không thì CPU.
  4. CHẠY NỀN song song Demucs/ASR (start_background) — bước dịch lấy kết quả, chờ tối đa SIMPLE_ZH_WAIT_SEC,
     quá hạn thì dịch bằng ASR (không treo).
  Mẫu (t, chữ) → cue bằng hardsub_asr._samples_to_cues (y hệt định dạng cũ: start,end,zh,n,source).

Chạy nền (song song ASR):  python hs_ocr_fast.py <work_dir>
  → hardsub_cues.json (atomic) + hardsub_cues.progress.json (tiến độ / trạng thái) + hardsub_ocr.log.
start_background(wd) do server gọi trước ASR; zh_source.prepare dùng get_cues(wd).
"""
from __future__ import annotations
import sys as _sync_sys  # sync_from_v2: bootstrap — chạy trực tiếp vẫn import được core.*/engines.*
from pathlib import Path as _SyncP
_SYNC_ROOT = str(_SyncP(__file__).resolve().parents[1])
if _SYNC_ROOT not in _sync_sys.path:
    _sync_sys.path.insert(0, _SYNC_ROOT)

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CUES = "hardsub_cues.json"
PROG = "hardsub_cues.progress.json"
LOG = "hardsub_ocr.log"


def _cfg(key: str, default: str) -> str:
    try:
        from core.config import get as _g
        v = _g(key, default)
    except Exception:  # noqa: BLE001
        v = os.getenv(key, default)
    return str(default if v is None or str(v).strip() == "" else v).strip()


def _cfg_f(key: str, default: float) -> float:
    try:
        return float(_cfg(key, str(default)))
    except ValueError:
        return default


def _atomic_json(path: Path, data) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, path)


# ----------------------------------------------------------------------------- dải phụ đề
def band_rect(work_dir: Path, W: int, H: int) -> tuple[int, int, int, int]:
    """(x, y, w, h) pixel của dải phụ đề. Ưu tiên hardsub_band.json [y0,y1,x0,x1]; không có → 25% đáy."""
    y0, y1, x0, x1 = 0.75, 1.0, 0.0, 1.0
    try:
        from engines.asr.hardsub_asr import _band_y_frac
        y0, y1 = _band_y_frac(work_dir)
    except Exception:  # noqa: BLE001
        pass
    try:
        d = json.loads((work_dir / "hardsub_band.json").read_text(encoding="utf-8"))
        b = d.get("band") if isinstance(d, dict) else d
        if isinstance(b, (list, tuple)) and len(b) >= 4 and 0 <= float(b[2]) < float(b[3]) <= 1:
            x0, x1 = max(0.0, float(b[2]) - 0.02), min(1.0, float(b[3]) + 0.02)
    except Exception:  # noqa: BLE001
        pass
    x, y = int(W * x0) // 2 * 2, int(H * y0) // 2 * 2
    w = max(64, int(W * (x1 - x0)) // 2 * 2)
    h = max(32, int(H * (y1 - y0)) // 2 * 2)
    w, h = min(w, W - x), min(h, H - y)
    return x, y, w, h


# ----------------------------------------------------------------------------- OCR
_PRELOADED = {"done": False}


def _preload_cuda(ort) -> None:
    """Nạp CUDA/cuDNN cho onnxruntime-gpu. KHÔNG dùng preload_dlls() mặc định: server đã import torch (cu12)
    → ORT «skip vì torch đã nạp» nhưng ORT 1.3x build CUDA 13 → CUDA EP không đăng ký được (rơi về CPU).
    Nạp tường minh từ gói nvidia-* (pip onnxruntime-gpu[cuda,cudnn]); thiếu → thư mục CUDA_PATH."""
    if _PRELOADED["done"] or not hasattr(ort, "preload_dlls"):
        return
    _PRELOADED["done"] = True
    try:
        ort.preload_dlls(cuda=True, cudnn=True, msvc=False, directory="")
        return
    except Exception as e:  # noqa: BLE001
        print(f"[hs_ocr] nạp CUDA từ gói nvidia-* lỗi ({e}) → thử CUDA_PATH", flush=True)
    cp = os.environ.get("CUDA_PATH") or ""
    for sub in ("bin\\x64", "bin"):
        d = os.path.join(cp, sub)
        if cp and os.path.isdir(d):
            try:
                ort.preload_dlls(cuda=True, cudnn=False, msvc=False, directory=d)
                return
            except Exception as e:  # noqa: BLE001
                print(f"[hs_ocr] nạp CUDA từ {d} lỗi ({e})", flush=True)


def cuda_ok() -> bool:
    try:
        import onnxruntime as ort
        if "CUDAExecutionProvider" not in (ort.get_available_providers() or []):
            return False
        _preload_cuda(ort)
        return True
    except Exception:  # noqa: BLE001
        return False


def _active_providers(eng) -> set:
    """Provider THẬT của các phiên ONNX trong RapidOCR (tìm InferenceSession trong thuộc tính, sâu ≤ 4)."""
    found: set = set()
    seen: set = set()

    def walk(o, d):
        if d > 4 or id(o) in seen:
            return
        seen.add(id(o))
        gp = getattr(o, "get_providers", None)
        if callable(gp) and type(o).__name__ == "InferenceSession":
            try:
                found.update(gp())
            except Exception:  # noqa: BLE001
                pass
            return
        for v in list(getattr(o, "__dict__", {}).values()):
            if hasattr(v, "__dict__") or type(v).__name__ == "InferenceSession":
                walk(v, d + 1)

    walk(eng, 0)
    return found


def make_ocr(use_gpu: bool | None = None):
    """Trả (fn(img_gray)->str, mô tả). Không có RapidOCR → ném lỗi (caller giữ ASR)."""
    import numpy as np
    from rapidocr_onnxruntime import RapidOCR
    if use_gpu is None:
        use_gpu = _cfg("OCR_HS_GPU", "1").lower() not in ("0", "off", "false", "no")
    dev = "cpu"
    eng = None
    if use_gpu and cuda_ok():
        try:
            import onnxruntime as _ort
            _ort.set_default_logger_severity(3)   # ẩn cảnh báo «No registered plugin EP device» (vô hại, ORT 1.3x)
        except Exception:  # noqa: BLE001
            pass
        try:
            eng = RapidOCR(det_use_cuda=True, cls_use_cuda=True, rec_use_cuda=True)
            dev = "cuda"
        except Exception as e:  # noqa: BLE001
            print(f"[hs_ocr] RapidOCR GPU lỗi ({e}) → CPU", flush=True)
            eng = None
    elif use_gpu:
        print("[hs_ocr] onnxruntime không có CUDAExecutionProvider → OCR CPU "
              "(cài onnxruntime-gpu để chạy GPU)", flush=True)
    if eng is None:
        eng = RapidOCR()
    if dev == "cuda":
        prov = _active_providers(eng)
        if prov and "CUDAExecutionProvider" not in prov:
            dev = "cpu(cuda-lỗi)"
            print(f"[hs_ocr] CUDA không kích hoạt được (provider thật: {sorted(prov)}) → OCR đang chạy CPU", flush=True)
    conf_min = _cfg_f("OCR_HS_CONF", 0.5)

    def run(g) -> str:
        img = np.ascontiguousarray(np.stack([g, g, g], axis=-1))
        try:
            res, _ = eng(img, use_cls=False)
        except TypeError:
            res, _ = eng(img)
        parts: list[str] = []
        confs: list[float] = []
        run.last_conf = 0.0
        for _box, txt, conf in (res or []):
            tx = (txt or "").strip()
            try:
                c = float(conf)
            except (TypeError, ValueError):
                c = 0.0
            if not tx or c < conf_min:
                continue
            if sum(1 for ch in tx if "一" <= ch <= "鿿") < 1:
                continue
            parts.append(tx)
            confs.append(c)
        if not parts:
            return ""
        run.last_conf = min(confs)
        line = "".join(parts) if len(parts) > 1 and all(len(p) <= 4 for p in parts) else " ".join(parts)
        return re.sub(r"\s+", "", line)

    run.last_conf = 0.0
    return run, dev


# ----------------------------------------------------------------------------- trích cue
def extract_cues_fast(work_dir: str | Path, *, ocr=None, video: Path | None = None,
                      dur: float | None = None, fps: float | None = None, progress=None) -> tuple[list[dict], dict]:
    import numpy as np
    from engines.asr.hardsub_asr import _find_video, _probe_size, _samples_to_cues
    wd = Path(work_dir)
    video = Path(video) if video else _find_video(wd)
    if not video:
        raise RuntimeError("Chưa có video")
    fps = fps or _cfg_f("OCR_HS_FPS", 1.0)
    same_mad = _cfg_f("OCR_HS_SAME", 1.5)
    W, H = _probe_size(video)
    x, y, w, h = band_rect(wd, W, H)
    total = dur
    if total is None:
        try:
            total = float(subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)],
                capture_output=True, text=True, timeout=60).stdout.strip() or 0)
        except (ValueError, subprocess.TimeoutExpired):
            total = 0.0
    dev = "test"
    if ocr is None:
        ocr, dev = make_ocr()
    hw_want = _cfg("OCR_HS_HWDEC", "1").lower() not in ("0", "off", "false", "no")

    def _cmd(hw: bool) -> list[str]:
        c = ["ffmpeg", "-v", "error", "-nostdin"]
        if hw:
            c += ["-hwaccel", "cuda"]        # giải mã GPU (khung tự tải về RAM)
        c += ["-i", str(video)]
        if dur:
            c += ["-t", str(dur)]
        return c + ["-an", "-vf", f"fps={fps},crop={w}:{h}:{x}:{y},format=gray",
                    "-f", "rawvideo", "-pix_fmt", "gray", "-"]

    print(f"[hs_ocr] {video.name} {W}x{H} · dải {w}x{h}@({x},{y}) · {fps:g} khung/s · OCR={dev}", flush=True)
    fsz = w * h
    samples: list[tuple[float, str]] = []
    n_frames = n_ocr = n_same = 0
    t0 = time.time()
    hw_used = False
    for hw in ((True, False) if hw_want else (False,)):
        samples, prev, last_text = [], None, ""
        n_frames = n_ocr = n_same = 0
        last_prog = 0.0
        proc = subprocess.Popen(_cmd(hw), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=fsz * 8)
        try:
            while True:
                buf = proc.stdout.read(fsz)
                if not buf or len(buf) < fsz:
                    break
                g = np.frombuffer(buf, dtype=np.uint8).reshape(h, w)
                t = n_frames / fps
                n_frames += 1
                small = g[::4, ::4].astype(np.int16)
                if prev is not None and float(np.abs(small - prev).mean()) < same_mad:
                    n_same += 1
                    text = last_text
                else:
                    text = ocr(g)
                    n_ocr += 1
                    last_text = text
                prev = small
                if text:
                    samples.append((round(t, 3), text))
                if progress and time.time() - last_prog >= 5:
                    last_prog = time.time()
                    progress({"done_s": round(t, 1), "total_s": round(total or 0, 1), "n_frames": n_frames,
                              "n_ocr": n_ocr, "elapsed": round(time.time() - t0, 1)})
        finally:
            try:
                proc.stdout.close()
            except Exception:  # noqa: BLE001
                pass
            proc.wait()
        if n_frames > 0 or not hw:
            hw_used = hw
            break
        print("[hs_ocr] giải mã GPU (-hwaccel cuda) không ra khung → giải mã CPU", flush=True)
    cues = _samples_to_cues(samples, gap=1.0 / fps + 0.15)
    st = {"frames": n_frames, "ocr": n_ocr, "same": n_same, "cues": len(cues),
          "fps": fps, "device": dev, "hwdec": hw_used, "sec": round(time.time() - t0, 1), "band": [x, y, w, h]}
    print(f"[hs_ocr] xong: {st}", flush=True)
    return cues, st


# ----------------------------------------------------------------------------- chạy nền
def _pid_alive(pid: int) -> bool:
    if not pid:
        return False
    if os.name == "nt":
        try:
            out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True,
                                 timeout=10).stdout
            return str(pid) in out
        except Exception:  # noqa: BLE001
            return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def status(work_dir: str | Path) -> dict:
    wd = Path(work_dir)
    if (wd / CUES).is_file():
        return {"state": "done"}
    try:
        p = json.loads((wd / PROG).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"state": "none"}
    if p.get("state") in ("running", "detect") and not _pid_alive(int(p.get("pid") or 0)):
        p["state"] = "dead"
    return p


def start_background(work_dir: str | Path) -> str:
    """Mở tiến trình OCR nền (thấp ưu tiên). Bỏ qua khi đã có cue / đang chạy / script đã soát đủ."""
    wd = Path(work_dir)
    st = status(wd)
    if st.get("state") in ("done", "running", "detect", "no_hardsub"):
        return st["state"]
    try:
        from translate_simple.pipeline import _script_all_reviewed
        if _script_all_reviewed(wd):
            return "reviewed"
    except Exception:  # noqa: BLE001
        pass
    env = dict(os.environ)
    env.setdefault("OMP_NUM_THREADS", _cfg("OCR_HS_THREADS", "4"))
    env["PYTHONIOENCODING"] = "utf-8"
    flags = 0
    if os.name == "nt":
        flags = 0x00004000 | 0x08000000  # BELOW_NORMAL_PRIORITY_CLASS | CREATE_NO_WINDOW
    log = open(wd / LOG, "a", encoding="utf-8")
    p = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), str(wd)], cwd=str(ROOT), env=env,
                         stdout=log, stderr=subprocess.STDOUT, creationflags=flags)
    _atomic_json(wd / PROG, {"state": "detect", "pid": p.pid, "started": time.time()})
    print(f"[hs_ocr] {wd.name}: mở OCR hardsub nền pid={p.pid} (song song ASR)", flush=True)
    return "started"


def get_cues(work_dir: str | Path, *, wait_sec: float | None = None, progress=None) -> list[dict] | None:
    """Cho zh_source.prepare: có cue → trả; đang chạy nền → chờ ≤ wait_sec (SIMPLE_ZH_WAIT_SEC, 900);
    quá hạn → None (dịch bằng ASR, KHÔNG treo). Chưa từng chạy → chạy NGAY (bản nhanh) rồi trả."""
    wd = Path(work_dir)
    if wait_sec is None:
        wait_sec = _cfg_f("SIMPLE_ZH_WAIT_SEC", 900)
    deadline = time.time() + max(0.0, wait_sec)
    while True:
        st = status(wd)
        if st.get("state") == "done":
            return json.loads((wd / CUES).read_text(encoding="utf-8"))
        if st.get("state") == "no_hardsub":
            return []
        if st.get("state") in ("running", "detect"):
            if time.time() >= deadline:
                print(f"[hs_ocr] {wd.name}: OCR nền chưa xong sau {wait_sec:.0f}s → dịch bằng ASR", flush=True)
                return None
            if progress:
                progress(st)
            time.sleep(10)
            continue
        break  # none / dead / error → chạy ngay tại chỗ
    cues, rep = extract_cues_fast(wd)
    _atomic_json(wd / CUES, cues)
    _atomic_json(wd / PROG, {"state": "done", **rep})
    return cues


def _main(argv: list[str]) -> int:
    wd = Path(argv[0])
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    pid = os.getpid()
    _atomic_json(wd / PROG, {"state": "detect", "pid": pid, "started": time.time()})
    try:
        from translate_simple import zh_source
        det = zh_source.detect(wd)
        if not det.get("has_hardsub"):
            _atomic_json(wd / PROG, {"state": "no_hardsub", "detect": det})
            print(f"[hs_ocr] {wd.name}: không có hardsub ({det}) → không OCR", flush=True)
            return 0

        def prog(d: dict) -> None:
            _atomic_json(wd / PROG, {"state": "running", "pid": pid, **d})

        prog({"done_s": 0})
        cues, rep = extract_cues_fast(wd, progress=prog)
        _atomic_json(wd / CUES, cues)
        _atomic_json(wd / PROG, {"state": "done", **rep})
        return 0
    except Exception as e:  # noqa: BLE001
        _atomic_json(wd / PROG, {"state": "error", "error": f"{type(e).__name__}: {str(e)[:300]}"})
        print(f"[hs_ocr] lỗi: {e}", flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(_main(sys.argv[1:]))
