"""
preset_switcher.py — Tự động chuyển đổi Preset Model trên llama-server (:8083)
Quản lý bộ presets tại E:\\models\\presets (chạy script start-model.ps1).

Chức năng:
- Xác định model đang chạy thực tế trên cổng 8083 (qua /v1/models hoặc active.json).
- Tự động chuyển đổi model trước Lượt 1 (Dịch tốc độ cao) và Lượt 2 (Rà soát chuẩn xác).
- ĐẶC BIỆT: Chờ đợi kiên nhẫn (tối đa 180s) cho đến khi AI local nạp VRAM xong,
  vượt qua trạng thái "loading model", và test ping inference 1 token thành công 100%
  rồi mới cho phép pipeline tiếp tục chạy dịch.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
import requests

PRESET_DIR = Path(os.getenv("MODEL_PRESETS_DIR") or r"E:\models\presets")
ACTIVE_JSON = PRESET_DIR / "active.json"
MODELS_JSON = PRESET_DIR / "models.json"
START_SCRIPT = PRESET_DIR / "start-model.ps1"
LLAMA_PORT = 8083
LLAMA_HOST = "127.0.0.1"
BASE_URL = f"http://{LLAMA_HOST}:{LLAMA_PORT}"


def get_active_preset() -> str | None:
    """Trả về ID hoặc alias của model đang thực sự hoạt động trên llama-server (:8083)."""
    # 1. Ưu tiên kiểm tra trực tiếp từ server đang chạy trong RAM
    try:
        r = requests.get(f"{BASE_URL}/v1/models", headers={"Authorization": "Bearer sk-local"}, timeout=1.5)
        if r.status_code == 200:
            d = r.json()
            data_list = d.get("data") or d.get("models") or []
            if data_list and isinstance(data_list, list):
                mid = data_list[0].get("id") or data_list[0].get("name")
                if mid:
                    return str(mid).strip()
    except Exception:
        pass

    # 2. Đọc từ file active.json
    if ACTIVE_JSON.is_file():
        try:
            data = json.loads(ACTIVE_JSON.read_text(encoding="utf-8"))
            return str(data.get("id") or data.get("alias") or "").strip() or None
        except Exception:
            pass
    return None


def list_available_presets() -> list[dict]:
    """Trả về danh sách tất cả các preset có trong models.json."""
    if not MODELS_JSON.is_file():
        return []
    try:
        data = json.loads(MODELS_JSON.read_text(encoding="utf-8"))
        models = data.get("models") or []
        out = []
        for m in models:
            if isinstance(m, dict) and m.get("id"):
                out.append({
                    "id": m["id"],
                    "alias": m.get("alias") or m["id"],
                    "path": m.get("path") or "",
                })
        return out
    except Exception:
        return []


def is_model_ready(target_preset: str | None = None, ping_inference: bool = True) -> bool:
    """Kiểm tra toàn diện xem llama-server :8083 đã khởi động xong và sẵn sàng nhận prompt chưa.
    
    Các tiêu chí:
    1. /health trả về HTTP 200 và status == 'ok' (nếu là 'loading model' -> chưa xong).
    2. Nếu có target_preset: kiểm tra xem model đang nạp có đúng là target_preset không.
    3. Gửi test inference mini 1 token: server phải trả về kết quả thành công mà không lỗi.
    """
    # 1. Kiểm tra /health
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=2.0)
        if r.status_code != 200:
            return False
        hdata = r.json()
        if hdata.get("status") != "ok":
            return False
    except Exception:
        return False

    # 2. Kiểm tra đúng model mong muốn
    if target_preset:
        tgt_clean = target_preset.lower().strip()
        active = get_active_preset()
        if not active or tgt_clean not in active.lower():
            # Nếu tên model chưa khớp (có thể server cũ chưa tắt hoặc mới đang nạp dở)
            return False

    # 3. Test ping inference cực ngắn (1 token) để chắc chắn server không bị nghẽn hay out-of-memory
    if ping_inference:
        try:
            payload = {
                "model": target_preset or "local",
                "messages": [{"role": "user", "content": "1"}],
                "max_tokens": 1,
                "stream": False,
            }
            r = requests.post(
                f"{BASE_URL}/v1/chat/completions",
                headers={"Authorization": "Bearer sk-local", "Content-Type": "application/json"},
                json=payload,
                timeout=5.0,
            )
            if r.status_code != 200:
                return False
        except Exception:
            return False

    return True


def switch_preset(preset_id: str, max_wait_sec: int = 180) -> bool:
    """Chuyển đổi llama-server sang preset mong muốn và CHỜ ĐỢI cho đến khi AI mở lại hoàn toàn.
    
    Args:
        preset_id: ID của preset (vd: 'gemma4-12b-qat-mtp-fast', 'gemma4-26b-qat-uncen-mtp')
        max_wait_sec: Thời gian tối đa kiên nhẫn chờ server khởi động và nạp VRAM (mặc định 180s = 3 phút).
        
    Returns:
        True nếu chuyển thành công và AI local đã OPEN hoàn toàn, sẵn sàng dịch.
        False nếu hết thời gian chờ hoặc gặp lỗi.
    """
    preset_id = (preset_id or "").strip()
    if not preset_id:
        return False

    # Kiểm tra nếu preset mong muốn đã đang chạy sẵn và hoạt động trơn tru
    if is_model_ready(target_preset=preset_id, ping_inference=True):
        print(f"[preset_switcher] ✅ Model '{preset_id}' đã đang mở sẵn sàng trên port {LLAMA_PORT}.", flush=True)
        return True

    if not START_SCRIPT.is_file():
        print(f"[preset_switcher] ❌ Không tìm thấy script khởi động: {START_SCRIPT}", flush=True)
        return False

    current = get_active_preset() or "chưa rõ"
    print(f"\n[preset_switcher] 🔄 Đang kích hoạt chuyển AI Local: '{current}' ➔ '{preset_id}'...", flush=True)

    cmd = [
        "powershell",
        "-ExecutionPolicy", "Bypass",
        "-File", str(START_SCRIPT),
        preset_id,
    ]

    try:
        # Chạy script PowerShell chuyển model (chạy async không chặn để Python chủ động loop thăm dò)
        subprocess.Popen(
            cmd,
            cwd=str(PRESET_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[preset_switcher] ❌ Lỗi khi gọi script khởi động model: {e}", flush=True)
        return False

    # Chờ đợi kiên nhẫn: server cũ tắt -> server mới bật -> nạp VRAM -> /health ok -> test ping ok
    t0 = time.time()
    # Chờ 3s đầu tiên để tiến trình cũ bị kill và giải phóng port
    time.sleep(3.0)

    print(f"[preset_switcher] ⏳ Đang chờ AI Local '{preset_id}' khởi động và nạp vào VRAM (tối đa {max_wait_sec}s)...", flush=True)

    last_log_time = t0
    while time.time() - t0 < max_wait_sec:
        time.sleep(2.5)
        elapsed = time.time() - t0

        # Kiểm tra xem AI local đã hoàn toàn mở và sẵn sàng nhận prompt chưa
        if is_model_ready(target_preset=preset_id, ping_inference=True):
            print(f"\n[preset_switcher] 🚀 AI Local '{preset_id}' ĐÃ MỞ THÀNH CÔNG VÀ SẴN SÀNG! (Mất {elapsed:.1f}s)", flush=True)
            print("[preset_switcher] Bắt đầu chạy tiến trình dịch...\n", flush=True)
            return True

        # Log tiến trình mỗi 8 giây để người dùng nắm được trạng thái
        if time.time() - last_log_time >= 8.0:
            last_log_time = time.time()
            # Xem server đã phản hồi ở mức nào
            state_desc = "đang khởi tạo tiến trình"
            try:
                r = requests.get(f"{BASE_URL}/health", timeout=1.0)
                if r.status_code == 200:
                    status_text = r.json().get("status", "")
                    if status_text == "ok":
                        state_desc = "đang nạp trọng số model vào VRAM"
                    else:
                        state_desc = f"trạng thái: {status_text}"
                else:
                    state_desc = f"HTTP {r.status_code} (đang nạp GGUF)"
            except Exception:
                state_desc = "đang giải phóng VRAM / mở port"
            print(f"  [chờ AI Local] {elapsed:.0f}s / {max_wait_sec}s — {state_desc}...", flush=True)

    print(f"\n[preset_switcher] ❌ Quá thời gian chờ ({max_wait_sec}s) cho model '{preset_id}'!", flush=True)
    return False
