from pathlib import Path
import re

srv = Path("server.py").read_text(encoding="utf-8")
parts = ["# Task 3 Review Package", ""]
idx = srv.find("class JobQueueReq")
if idx < 0:
    parts.append("MISSING JobQueueReq")
else:
    m = re.search(r"\nclass |\ndef ", srv[idx + 5 :])
    parts += [
        "### JobQueueReq",
        "```python",
        srv[idx : idx + 5 + (m.start() if m else 400)],
        "```",
        "",
    ]
for m in re.finditer(r'@app\.(post|get)\("/api/queue/jobs[^"]*"\)', srv):
    start = m.start()
    chunk = srv[start : start + 900]
    parts += [f"### route {m.group(0)}", "```python", chunk, "```", ""]
api = Path("tests/test_queue_jobs_api.py")
if api.exists():
    parts += ["### test_queue_jobs_api.py", "```python", api.read_text(encoding="utf-8"), "```"]
out = Path("docs/superpowers/sdd/diffs/task-3-review-package.md")
out.write_text("\n".join(parts), encoding="utf-8")
print("routes", len(re.findall(r"/api/queue/jobs", srv)), "pkg", out.stat().st_size)
