"""
app.py — Pineline DESKTOP APP.

Chạy FastAPI (server.py) ở luồng nền + mở giao diện trong 1 CỬA SỔ desktop
(PyWebView, dùng WebView2 có sẵn trên Windows 10/11) — không cần trình duyệt,
không cần bật server thủ công. Tái dùng 100% UI (index.html) + engine hiện có.

Chạy:  nháy đúp Pineline.bat   (hoặc: python app.py)
Cấu hình (endpoint LLM, model, GPU...) đọc từ config.json.
"""
from __future__ import annotations

import json
import os
import socket
import threading
import time
from pathlib import Path

HERE = Path(__file__).parent

# 1) Nạp config -> biến môi trường (PHẢI trước khi import server/engine,
#    vì llm/translate/tts đọc env lúc import). Ưu tiên pineline.config.json (tên mới).
import config as _config_boot  # noqa: E402

_config_boot.inject_env()
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS", "1")          # FS không symlink -> HF copy
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")


def _pick_port(preferred: int = 8800) -> int:
    """Dùng cổng ưu tiên nếu rảnh, không thì xin cổng tự do."""
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", preferred))
        return preferred
    except OSError:
        s2 = socket.socket()
        s2.bind(("127.0.0.1", 0))
        port = s2.getsockname()[1]
        s2.close()
        return port
    finally:
        s.close()


PORT = _pick_port(int(os.getenv("PORT", "8800")))
os.environ["PORT"] = str(PORT)
URL = f"http://127.0.0.1:{PORT}"

import uvicorn  # noqa: E402
import webview  # noqa: E402
from server import app  # noqa: E402


class _ThreadServer(uvicorn.Server):
    # uvicorn mặc định cài signal handler (chỉ chạy ở main thread) -> tắt đi.
    def install_signal_handlers(self) -> None:  # noqa: D401
        pass


def _serve() -> None:
    _ThreadServer(uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning")).run()


def _wait_server(timeout: float = 60.0) -> bool:
    import urllib.request
    end = time.time() + timeout
    while time.time() < end:
        try:
            urllib.request.urlopen(URL + "/", timeout=1)
            return True
        except Exception:  # noqa: BLE001
            time.sleep(0.4)
    return False


def main() -> None:
    threading.Thread(target=_serve, daemon=True).start()
    if not _wait_server():
        print("[app] Server không lên được. Kiểm tra log.")
    webview.create_window(
        "Pineline — Lồng tiếng",
        URL,
        width=1280,
        height=860,
        min_size=(900, 600),
    )
    webview.start()   # chặn tới khi đóng cửa sổ

    # Đóng cửa sổ -> THOÁT NGAY. Nếu để Python tắt "bình thường", atexit của
    # ThreadPoolExecutor sẽ set executor=shutdown rồi KẸT chờ join thread đang
    # tải/dịch dở -> uvicorn (daemon) vẫn sống, mọi request kế tiếp văng
    # "cannot schedule new futures after shutdown", tiến trình treo nửa vời.
    # os._exit cắt sạch tức thì; việc nền có checkpoint nên mở lại resume được.
    os._exit(0)


if __name__ == "__main__":
    main()
