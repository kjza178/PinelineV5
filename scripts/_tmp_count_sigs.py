import re
from pathlib import Path

d = Path(r"Z:\PinelineV5\docs\reviews\func-sigs")
rows = []
for p in sorted(d.glob("*.md")):
    if p.name == "README.md":
        continue
    text = p.read_text(encoding="utf-8")
    m = re.search(r"\*\*Module:\*\* `([^`]+)`", text)
    c = re.search(r"\*\*Count:\*\* (\d+)", text)
    heads = len(re.findall(r"^### `", text, re.M))
    mod = m.group(1) if m else "?"
    count = int(c.group(1)) if c else heads
    rows.append((p.name, mod, count, heads))
    print(f"{p.name}\t{mod}\t{count}\t{heads}")
print("TOTAL", len(rows), sum(r[2] for r in rows))
