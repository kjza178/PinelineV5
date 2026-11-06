"""Đọc HG_UI_TOKEN từ env của process Hongguo (Windows PEB)."""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import struct
import urllib.request

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
ntdll = ctypes.WinDLL("ntdll", use_last_error=True)

OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [wt.DWORD, wt.BOOL, wt.DWORD]
OpenProcess.restype = wt.HANDLE

ReadProcessMemory = kernel32.ReadProcessMemory
ReadProcessMemory.argtypes = [wt.HANDLE, wt.LPVOID, wt.LPVOID, ctypes.c_size_t, ctypes.POINTER(ctypes.c_size_t)]
ReadProcessMemory.restype = wt.BOOL

CloseHandle = kernel32.CloseHandle

NtQueryInformationProcess = ntdll.NtQueryInformationProcess
NtQueryInformationProcess.argtypes = [wt.HANDLE, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_ulong)]
NtQueryInformationProcess.restype = ctypes.c_ulong


def _read(h, addr, size):
    buf = (ctypes.c_char * size)()
    n = ctypes.c_size_t(0)
    if not ReadProcessMemory(h, ctypes.c_void_p(addr), buf, size, ctypes.byref(n)):
        return None
    return bytes(buf[: n.value])


def read_env(pid: int) -> dict[str, str]:
    h = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        raise OSError(f"OpenProcess failed: {ctypes.get_last_error()}")
    try:
        # PROCESS_BASIC_INFORMATION
        pbi = (ctypes.c_uint64 * 6)()
        retlen = ctypes.c_ulong(0)
        status = NtQueryInformationProcess(h, 0, ctypes.byref(pbi), ctypes.sizeof(pbi), ctypes.byref(retlen))
        if status != 0:
            raise OSError(f"NtQueryInformationProcess {status:#x}")
        peb = pbi[1]
        # PEB+0x20 = ProcessParameters (x64)
        pp_addr = struct.unpack_from("<Q", _read(h, peb + 0x20, 8))[0]
        # RTL_USER_PROCESS_PARAMETERS: Environment at +0x80 (x64)
        env_addr = struct.unpack_from("<Q", _read(h, pp_addr + 0x80, 8))[0]
        raw = _read(h, env_addr, 64 * 1024) or b""
        # UTF-16LE null-separated
        text = raw.decode("utf-16le", errors="ignore")
        out = {}
        for part in text.split("\x00"):
            if "=" in part:
                k, _, v = part.partition("=")
                if k:
                    out[k] = v
        return out
    finally:
        CloseHandle(h)


def main():
    # find hongguo pythonw
    import subprocess
    out = subprocess.check_output(
        ["powershell", "-NoProfile", "-Command",
         "Get-CimInstance Win32_Process -Filter \"name = 'pythonw.exe'\" | "
         "Where-Object { $_.ExecutablePath -like '*Hongguo*' } | "
         "Select-Object -ExpandProperty ProcessId"],
        text=True,
    )
    pids = [int(x) for x in out.split() if x.strip().isdigit()]
    print("pids", pids)
    for pid in pids:
        try:
            env = read_env(pid)
        except Exception as e:
            print(pid, "env fail", e)
            continue
        keys = {k: v for k, v in env.items() if "HG_" in k or "TOKEN" in k.upper() or "UI" in k.upper()}
        print(pid, "interesting", keys)
        tok = env.get("HG_UI_TOKEN") or env.get("ui_token")
        if tok:
            print("TOKEN", tok)
            # try API
            for path in ["/dl/config", "/dl/library", "/dl/search?q=a"]:
                req = urllib.request.Request(
                    "http://127.0.0.1:8000" + path,
                    headers={"Accept": "application/json", "x-hg-token": tok},
                )
                try:
                    with urllib.request.urlopen(req, timeout=5) as r:
                        print(" ", path, r.status, r.read()[:100])
                except Exception as e:
                    body = e.read()[:120] if hasattr(e, "read") else e
                    print(" ", path, "ERR", getattr(e, "code", None), body)


if __name__ == "__main__":
    main()
