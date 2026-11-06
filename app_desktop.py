"""
app_desktop.py — Desktop App Studio cho Pineline V4.
Sử dụng Microsoft Edge WebView2 (native engine siêu nhẹ, mượt mà, không phụ thuộc trình duyệt).
Tự động khởi động backend, hiển thị cửa sổ native, dọn dẹp sạch tiến trình khi đóng app.
"""
from __future__ import annotations

import os
import sys
import time
import socket
import subprocess
import threading
import webbrowser
from pathlib import Path

# Cấu hình encoding utf-8 an toàn cho Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", "8805"))
HOST = "127.0.0.1"
URL = f"http://{HOST}:{PORT}/"

# Tạo thư mục user data riêng biệt cho WebView2 để tránh lỗi 0x800700AA (Resource in use)
WEBVIEW_CACHE = Path(os.environ.get("TEMP", "C:/temp")) / f"PinelineV5_wv_{os.getpid()}"
try:
    WEBVIEW_CACHE.mkdir(parents=True, exist_ok=True)
except Exception:
    pass


def is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=0.8):
            return True
    except (OSError, ConnectionRefusedError):
        return False


def start_backend() -> subprocess.Popen | None:
    if is_port_open(HOST, PORT):
        print(f"[Desktop] Port {PORT} da co server chay san. Dung server hien co.")
        return None
    print(f"[Desktop] Dang khoi dong Pineline V5 backend tai {HOST}:{PORT} ...")
    cmd = [sys.executable, str(ROOT / "server.py"), "--host", HOST, "--port", str(PORT)]
    env = dict(os.environ, PYTHONIOENCODING="utf-8", PORT=str(PORT))
    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1
    )

    def _read_stdout():
        try:
            for line in proc.stdout:
                try:
                    sys.stdout.write(f"[Backend] {line}")
                    sys.stdout.flush()
                except Exception:
                    pass
        except Exception:
            pass

    threading.Thread(target=_read_stdout, daemon=True).start()
    return proc


def wait_for_server(timeout: int = 20) -> bool:
    start_t = time.time()
    while time.time() - start_t < timeout:
        if is_port_open(HOST, PORT):
            return True
        time.sleep(0.3)
    return False


def main():
    backend_proc = start_backend()
    if not wait_for_server(timeout=25):
        print("[Desktop] Canh bao: Backend khoi dong cham hoac co van de.")

    print(f"[Desktop] Mo cua so Desktop Studio tai: {URL}")

    # Thu mo bang WebView2 voi user data folder rieng
    try:
        import webview
        window = webview.create_window(
            title="PineLine Studio V4",
            url=URL,
            width=1520,
            height=940,
            min_size=(1100, 700),
            background_color="#111827",
            text_select=True,
        )

        def on_closed():
            print("[Desktop] Cua so dong -> Dang don dep backend...")
            if backend_proc and backend_proc.poll() is None:
                try:
                    backend_proc.terminate()
                    backend_proc.wait(timeout=3)
                except Exception:
                    try:
                        backend_proc.kill()
                    except Exception:
                        pass
            # Don dep thu muc cache tam
            try:
                import shutil
                if WEBVIEW_CACHE.exists():
                    shutil.rmtree(WEBVIEW_CACHE, ignore_errors=True)
            except Exception:
                pass
            print("[Desktop] Hoan tat.")
            os._exit(0)

        window.events.closed += on_closed
        # storage_path ngan chan loi 0x800700AA (The requested resource is in use)
        webview.start(gui="edgechromium", storage_path=str(WEBVIEW_CACHE), private_mode=False)

    except Exception as e_wv:
        print(f"\n[Desktop] WebView2 initialization issue: {e_wv}")
        print(f"[Desktop] Tu dong mo giao dien Studio tren trinh duyet mac dinh: {URL}")
        webbrowser.open(URL)
        print("[Desktop] Nhan Ctrl+C de dong Backend khi su dung xong.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            if backend_proc and backend_proc.poll() is None:
                backend_proc.terminate()
            os._exit(0)


if __name__ == "__main__":
    main()
