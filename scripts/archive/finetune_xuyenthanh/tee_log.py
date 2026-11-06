# -*- coding: utf-8 -*-
"""Stdout tee -> console + append log (tránh lỗi CMD/PowerShell với tqdm %%)."""
import sys
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: tee_log.py LOGFILE", file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        for line in sys.stdin:
            sys.stdout.write(line)
            sys.stdout.flush()
            f.write(line)
            f.flush()


if __name__ == "__main__":
    main()
