"""Ghi lại tiến trình gây tải khi ổ C/Z (PhysicalDrive2) bận vọt lên.

python disk_spike_watch.py [phút=60] [ngưỡng_bận_%=60]
Log: D:\\PinelineV2_tmp\\disk_spikes.log
"""
from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

import psutil
import win32pdh

DISK = "PhysicalDrive2"
LOG = Path(r"D:\PinelineV2_tmp\disk_spikes.log")
# psutil read_time/write_time trên Windows không phản ánh Active time của Task Manager
IDLE_COUNTER = r"\PhysicalDisk(2 C: Z:)\% Idle Time"


def proc_io() -> dict[int, tuple]:
    out = {}
    for p in psutil.process_iter(["pid", "name"]):
        try:
            io = p.io_counters()
            out[p.pid] = (p.info["name"], io.read_bytes, io.write_bytes, io.read_count, io.write_count)
        except Exception:  # noqa: BLE001
            pass
    return out


def cmd(pid: int) -> str:
    try:
        return " ".join(psutil.Process(pid).cmdline())[:140]
    except Exception:  # noqa: BLE001
        return ""


def main() -> None:
    minutes = float(sys.argv[1]) if len(sys.argv) > 1 else 60
    thresh = float(sys.argv[2]) if len(sys.argv) > 2 else 60
    LOG.parent.mkdir(parents=True, exist_ok=True)
    end = time.time() + minutes * 60
    q = win32pdh.OpenQuery()
    ctr = win32pdh.AddEnglishCounter(q, IDLE_COUNTER)
    win32pdh.CollectQueryData(q)
    d0 = psutil.disk_io_counters(perdisk=True)[DISK]
    p0 = proc_io()
    t0 = time.time()
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"\n=== bắt đầu {datetime.now():%H:%M:%S} · {minutes:g} phút · ngưỡng {thresh:g}%\n")
        f.flush()
        while time.time() < end:
            time.sleep(1)
            d1 = psutil.disk_io_counters(perdisk=True)[DISK]
            p1 = proc_io()
            t1 = time.time()
            dt = t1 - t0
            win32pdh.CollectQueryData(q)
            idle = win32pdh.GetFormattedCounterValue(ctr, win32pdh.PDH_FMT_DOUBLE)[1]
            busy = max(0.0, 100.0 - idle)
            if busy >= thresh:
                rmb = (d1.read_bytes - d0.read_bytes) / dt / 1e6
                wmb = (d1.write_bytes - d0.write_bytes) / dt / 1e6
                ops = (d1.read_count - d0.read_count + d1.write_count - d0.write_count) / dt
                rows = []
                for pid, v in p1.items():
                    if pid in p0:
                        a = p0[pid]
                        rows.append((v[1] - a[1] + v[2] - a[2], v[3] - a[3] + v[4] - a[4],
                                     (v[1] - a[1]) / dt / 1e6, (v[2] - a[2]) / dt / 1e6, pid, v[0]))
                f.write(f"[{datetime.now():%H:%M:%S}] bận ~{busy:.0f}% · R {rmb:.1f} W {wmb:.1f} MB/s · {ops:.0f} op/s\n")
                for _, n_ops, r, w, pid, name in sorted(rows, key=lambda x: -x[1])[:6]:
                    f.write(f"    {name:<20}{pid:>6} ops {n_ops:>7} R {r:6.1f} W {w:6.1f}  {cmd(pid)}\n")
                f.flush()
            d0, p0, t0 = d1, p1, t1
        f.write(f"=== kết thúc {datetime.now():%H:%M:%S}\n")


if __name__ == "__main__":
    main()
