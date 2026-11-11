"""Ghi file an toàn giữa nhiều tiến trình (server :8801, sidecar :8802, script).

atomic_write_text: ghi temp riêng (pid+thread) rồi os.replace — người đọc không bao giờ thấy file dở.
file_lock: khoá liên tiến trình bằng file .lock tạo O_EXCL; khoá bỏ quên (tiến trình chết) quá
stale_sec giây thì gỡ."""
from __future__ import annotations

import contextlib
import json
import os
import threading
import time
from pathlib import Path


def atomic_write_text(path: str | Path, text: str, encoding: str = "utf-8", fsync: bool = True) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(f".{p.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    with open(tmp, "w", encoding=encoding, newline="") as f:
        f.write(text)
        f.flush()
        if fsync:
            os.fsync(f.fileno())
    # Windows: đích đang bị mở đọc → WinError 5/32 trong chốc lát
    for i in range(20):
        try:
            os.replace(tmp, p)
            return
        except PermissionError:
            time.sleep(0.05 * (i + 1))
    try:
        os.replace(tmp, p)
    finally:
        with contextlib.suppress(OSError):
            tmp.unlink()


def atomic_write_json(path: str | Path, obj, indent: int | None = 2, fsync: bool = True) -> None:
    atomic_write_text(path, json.dumps(obj, ensure_ascii=False, indent=indent), fsync=fsync)


def read_json_checkpoint(path: str | Path, default=None):
    """Đọc checkpoint JSON. Hỏng → đổi tên thành .corrupt-<ts> (giữ để cứu) và trả default,
    thay vì để caller ghi đè im lặng."""
    p = Path(path)
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        bad = p.with_name(f"{p.name}.corrupt-{int(time.time())}")
        with contextlib.suppress(OSError):
            os.replace(p, bad)
        print(f"[fileio] {p.name} hỏng ({e}) → giữ bản hỏng {bad.name}, làm lại phần này", flush=True)
        return default


@contextlib.contextmanager
def file_lock(path: str | Path, timeout: float = 15.0, stale_sec: float = 60.0):
    lock = Path(str(path) + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    fd = None
    while fd is None:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, f"{os.getpid()} {time.time():.0f}".encode())
        except (FileExistsError, PermissionError):
            # Windows: tạo lại đúng lúc bản cũ đang chờ xoá → PermissionError thay vì FileExistsError
            try:
                stale = time.time() - lock.stat().st_mtime > stale_sec
                dead_owner = False
                try:
                    # Nội dung thường: "<pid> <epoch>" — nếu PID chết thì coi lock stale
                    parts = lock.read_text(encoding="utf-8", errors="ignore").strip().split()
                    if parts and parts[0].isdigit():
                        opid = int(parts[0])
                        if opid > 0:
                            try:
                                import ctypes
                                h = ctypes.windll.kernel32.OpenProcess(0x1000, False, opid)
                                if h:
                                    ctypes.windll.kernel32.CloseHandle(h)
                                else:
                                    dead_owner = True
                            except Exception:
                                pass
                except Exception:
                    pass
                if stale or dead_owner:
                    lock.unlink()
                    continue
            except OSError:
                pass
            if time.time() - t0 > timeout:
                raise TimeoutError(f"không lấy được khoá {lock}")
            time.sleep(0.05)
    try:
        yield
    finally:
        os.close(fd)
        with contextlib.suppress(OSError):
            lock.unlink()
