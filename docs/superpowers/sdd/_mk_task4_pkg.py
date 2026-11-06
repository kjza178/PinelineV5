from pathlib import Path
import re

parts = ["# Task 4 Review Package", ""]
for fname in ("index3.html", "index.html"):
    text = Path(fname).read_text(encoding="utf-8")
    parts.append(f"## {fname}")
    for pat in [
        r"Chạy hàng chờ",
        r"btn-queue-run",
        r"function collectRunAllOpts",
        r"function runJobQueue",
        r"function stopJobQueue",
        r"function paintQueueStatus",
        r"paintQueueStatus\(\)",
    ]:
        parts.append(f"- match `{pat}`: {bool(re.search(pat, text))}")
    # extract qbar snippet
    m = re.search(r'html\+=`<div class="qbar"[\s\S]{0,800}`', text)
    if m:
        parts += ["### qbar snippet", "```javascript", m.group(0)[:700], "```", ""]
    for name in ("collectRunAllOpts", "runJobQueue", "stopJobQueue", "paintQueueStatus"):
        m = re.search(rf"function {name}\([\s\S]*?\n\}}", text)
        if m:
            parts += [f"### function {name}", "```javascript", m.group(0)[:2500], "```", ""]
        else:
            # async function
            m = re.search(rf"async function {name}\([\s\S]*?\n\}}", text)
            if m:
                parts += [f"### async function {name}", "```javascript", m.group(0)[:2500], "```", ""]
            else:
                parts.append(f"MISSING {name} in {fname}")
    parts.append("")
out = Path("docs/superpowers/sdd/diffs/task-4-review-package.md")
out.write_text("\n".join(parts), encoding="utf-8")
print("wrote", out.stat().st_size)
