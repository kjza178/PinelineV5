#!/usr/bin/env python3
"""check_gpu_tts.py — Chẩn đoán vì sao clone TTS chạy CPU thay vì GPU.

Chạy trên MÁY ĐANG LỖI (cùng chỗ Pineline):
  python check_gpu_tts.py

Kiểm theo lớp (từ ngoài vào trong):
  1) Driver NVIDIA (nvidia-smi)
  2) pineline.config.json + biến môi trường (VIENEU_DEVICE / OMNI_DEVICE)
  3) Torch trong từng venv TTS: CUDA có thật không, build CPU-only?
  4) Job json lần chạy gần nhất (device ghi vào job là gì)
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OK, BAD, WARN = "[OK]", "[FAIL]", "[WARN]"


def say(tag: str, msg: str):
    try:
        print(f"{tag} {msg}", flush=True)
    except UnicodeEncodeError:
        print(f"{tag} {msg}".encode("ascii", "replace").decode("ascii"), flush=True)


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def load_cfg() -> dict:
    p = ROOT / "pineline.config.json"
    if not p.exists():
        say(WARN, f"Khong co {p.name} — app dung default/env.")
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        say(BAD, f"Doc pineline.config.json loi: {e}")
        return {}


def check_nvidia() -> bool:
    print("\n=== 1) Driver NVIDIA ===")
    if not shutil.which("nvidia-smi"):
        say(BAD, "Khong co nvidia-smi trong PATH -> khong detect GPU luc install / runtime.")
        return False
    r = run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader"])
    if r.returncode != 0:
        say(BAD, f"nvidia-smi loi:\n{r.stderr or r.stdout}")
        return False
    for line in (r.stdout or "").strip().splitlines():
        say(OK, f"GPU: {line.strip()}")
    r2 = run(["nvidia-smi"])
    for line in (r2.stdout or "").splitlines():
        if "CUDA Version" in line:
            say(OK, line.strip())
            break
    return True


def resolve_device(key: str, cfg: dict) -> tuple[str, str]:
    """Trả (giá trị, nguồn). Ưu tiên giống config.py: env > config > default cuda."""
    if os.getenv(key):
        return os.getenv(key), "env"
    if cfg.get(key):
        return str(cfg[key]), "pineline.config.json"
    return "cuda", "default"


def check_config(cfg: dict):
    print("\n=== 2) Config device (env > pineline.config.json > default) ===")
    for key in ("VIENEU_DEVICE", "OMNI_DEVICE"):
        val, src = resolve_device(key, cfg)
        tag = OK if val.lower() == "cuda" else BAD
        say(tag, f"{key}={val!r}  (source: {src})")
        if val.lower() != "cuda":
            say(WARN, f"  -> App se EP worker dung {val}. Sua config hoac set env {key}=cuda.")


def check_venv_torch(name: str, py: str | None):
    print(f"\n=== 3) Torch trong venv {name} ===")
    if not py:
        say(WARN, f"{name}: chua cau hinh duong dan python.")
        return
    p = Path(py)
    if not p.exists():
        say(BAD, f"{name}: khong tim thay python: {py}")
        return
    say(OK, f"{name} python: {py}")

    code = r"""
import json, sys
out = {"py": sys.executable}
try:
    import torch
    out["torch"] = torch.__version__
    out["cuda_built"] = bool(getattr(torch.version, "cuda", None))
    out["torch_cuda"] = torch.version.cuda
    out["is_available"] = torch.cuda.is_available()
    out["device_count"] = torch.cuda.device_count() if torch.cuda.is_available() else 0
    if torch.cuda.is_available():
        out["gpu_name"] = torch.cuda.get_device_name(0)
        try:
            x = torch.zeros(1, device="cuda")
            out["alloc_ok"] = True
            del x
        except Exception as e:
            out["alloc_ok"] = False
            out["alloc_err"] = repr(e)
except Exception as e:
    out["error"] = repr(e)
print(json.dumps(out))
"""
    r = run([str(p), "-c", code])
    if r.returncode != 0:
        say(BAD, f"Chay check torch that bai:\n{(r.stderr or r.stdout)[:500]}")
        return
    try:
        info = json.loads((r.stdout or "").strip().splitlines()[-1])
    except Exception:  # noqa: BLE001
        say(BAD, f"Output la:\n{r.stdout}\n{r.stderr}")
        return
    if info.get("error"):
        say(BAD, f"Import torch loi: {info['error']}")
        return
    say(OK, f"torch={info.get('torch')}  torch.version.cuda={info.get('torch_cuda')}")
    if not info.get("cuda_built") or info.get("torch_cuda") is None:
        say(BAD, "Day la ban torch CPU-only (khong co CUDA). Can cai lai torch CUDA vao venv nay.")
        say(WARN, "  VD: python install.py --gpu --cuda cu121   (hoac cu124/cu128 khop nvidia-smi)")
        return
    if info.get("is_available"):
        say(OK, f"cuda.is_available=True  GPU={info.get('gpu_name')}  count={info.get('device_count')}")
        if info.get("alloc_ok") is False:
            say(BAD, f"Cap phat tensor CUDA that bai: {info.get('alloc_err')}")
        # Smoke: matmul — bat loi 'no kernel image' (Blackwell / sai build)
        code2 = r"""
import json, torch
out = {}
try:
    a = torch.randn(1024, 1024, device='cuda', dtype=torch.bfloat16)
    b = torch.randn(1024, 1024, device='cuda', dtype=torch.bfloat16)
    c = a @ b
    torch.cuda.synchronize()
    out['matmul_ok'] = True
    out['cap'] = torch.cuda.get_device_capability(0)
except Exception as e:
    out['matmul_ok'] = False
    out['err'] = repr(e)
print(json.dumps(out))
"""
        r2 = run([str(p), "-c", code2])
        try:
            m = json.loads((r2.stdout or "").strip().splitlines()[-1])
            if m.get("matmul_ok"):
                say(OK, f"cuda matmul bf16 OK  capability={m.get('cap')}")
            else:
                say(BAD, f"cuda matmul FAIL (GPU se khong chay model): {m.get('err')}")
                say(WARN, "  RTX 50-series can torch cu128+. Thu: pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu128")
        except Exception:  # noqa: BLE001
            say(WARN, f"matmul smoke khong parse duoc: {(r2.stderr or r2.stdout)[:200]}")
    else:
        say(BAD, "torch co CUDA nhung cuda.is_available()=False.")
        say(WARN, "  Thuong do: driver cu / sai CUDA build / thieu DLL / GPU bi chiem.")


def check_recent_jobs():
    print("\n=== 4) Job TTS gần nhất (device thật gửi vào worker) ===")
    work = ROOT / "work"
    if not work.exists():
        say(WARN, "Chua co thu muc work/.")
        return
    jobs = sorted(work.glob("**/_*_job.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:5]
    if not jobs:
        say(WARN, "Chua thay *_job.json — chay 1 lan clone TTS roi check lai.")
        return
    for j in jobs[:3]:
        try:
            data = json.loads(j.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            say(WARN, f"{j}: doc loi {e}")
            continue
        dev = data.get("device", "?")
        tag = OK if str(dev).lower() == "cuda" else BAD
        say(tag, f"{j.relative_to(ROOT)}  device={dev!r}")


def main():
    print("=" * 64)
    print(" PINELINE — check GPU cho clone TTS")
    print("=" * 64)
    cfg = load_cfg()
    if cfg:
        say(OK, f"pineline.config.json keys: {', '.join(k for k in cfg if not k.startswith('_'))}")

    has_gpu = check_nvidia()
    check_config(cfg)

    vieneu_py = os.getenv("VIENEU_PY") or cfg.get("VIENEU_PY")
    omni_py = os.getenv("OMNI_PY") or cfg.get("OMNI_PY")
    check_venv_torch("VieNeu", vieneu_py)
    if omni_py:
        check_venv_torch("OmniVoice", omni_py)
    else:
        print("\n=== 3b) OmniVoice ===")
        say(WARN, "OMNI_PY trong — bo qua (engine tuy chon).")

    # VieNeu: device=cuda -> pytorch/GPU; device=cpu -> onnx/CPU (ke ca khi may co GPU)
    v_dev, _ = resolve_device("VIENEU_DEVICE", cfg)
    print("\n=== 3c) VieNeu backend (logic, khong load model) ===")
    if str(v_dev).lower() == "cuda":
        say(OK, f"VIENEU_DEVICE={v_dev!r} -> VieNeu se chon backend=pytorch/GPU")
    else:
        say(BAD, f"VIENEU_DEVICE={v_dev!r} -> VieNeu se chon backend=onnx/CPU")

    check_recent_jobs()

    print("\n=== KET LUAN NHANH ===")
    if not has_gpu:
        print("- May khong thay nvidia-smi -> TTS se chay CPU, hoac cai driver NVIDIA.")
    elif str(v_dev).lower() != "cuda":
        print(f"- Config dang ep VIENEU_DEVICE={v_dev!r}. Doi thanh cuda trong pineline.config.json.")
    else:
        print("- Config + torch CUDA OK. Neu van nghi la CPU: xem LOG luc chay TTS:")
        print("    'Loading VieNeu-TTS v3 Turbo (PyTorch)'  = dang dung GPU")
        print("    'Loading VieNeu-TTS v3 Turbo (ONNX/CPU)' = dang dung CPU")
        print("- Trong luc TTS: nvidia-smi  (cot Memory / python.exe phai tang VRAM)")
        print("- Task Manager CPU cao VAN BINH THUONG: G2P + speaker ONNX van chay CPU.")
        print("- OmniVoice FAIL chi anh huong neu chon engine omnivoice (khong anh huong vieneu).")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
