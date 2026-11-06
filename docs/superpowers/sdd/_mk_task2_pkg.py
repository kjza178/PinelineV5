from pathlib import Path
import re

parts = ["# Task 2 Review Package", "", "**Base:** after Task 1", "**Head:** after Task 2", ""]
p = Path("tests/test_job_queue_worker.py")
text = p.read_text(encoding="utf-8")
parts += [f"### {p} ({len(text.splitlines())} lines)", "", "```python", text, "```", ""]
jq = Path("job_queue.py").read_text(encoding="utf-8")
parts += ["### job_queue.py (full)", "", "```python", jq, "```", ""]
srv = Path("server.py").read_text(encoding="utf-8")
idx = srv.find("def _queue_run_one")
if idx < 0:
    parts.append("MISSING _queue_run_one")
else:
    m = re.search(r"\n(?:def |@app|class )", srv[idx + 10 :])
    chunk = srv[idx : idx + 10 + (m.start() if m else 8000)]
    parts += ["### server.py — _queue_run_one", "", "```python", chunk, "```", ""]
i = srv.find("job_queue.set_runner")
if i < 0:
    i = srv.find("import core.job_queue as job_queue")
if i >= 0:
    win = srv[max(0, i - 400) : i + 900]
    parts += ["### server.py — wire block", "", "```python", win, "```", ""]
else:
    parts.append("MISSING wire block")
out = Path("docs/superpowers/sdd/diffs/task-2-review-package.md")
out.write_text("\n".join(parts), encoding="utf-8")
print("ok", out.stat().st_size, "has_runner", "set_runner" in srv, "has_fn", idx >= 0)
