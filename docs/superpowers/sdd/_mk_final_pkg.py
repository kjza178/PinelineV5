from pathlib import Path

files = [
    "job_queue.py",
    "tests/test_job_queue.py",
    "tests/test_job_queue_worker.py",
    "tests/test_queue_run_one.py",
    "tests/test_queue_jobs_api.py",
    "docs/superpowers/specs/2026-09-24-job-queue-design.md",
    "docs/fixes/2026-09-24-queue-voice-stop-race.md",
]
parts = [
    "# Whole-branch review package — Job Queue Approach A",
    "",
    "**Note:** Workspace has no git; this package lists new/changed artifacts.",
    "",
    "## New / primary files",
]
for f in files:
    p = Path(f)
    if p.exists():
        parts.append(f"- `{f}` ({p.stat().st_size} bytes, {len(p.read_text(encoding='utf-8').splitlines())} lines)")
    else:
        parts.append(f"- MISSING `{f}`")
# server excerpts
srv = Path("server.py").read_text(encoding="utf-8")
for needle in ["class JobQueueReq", "def _queue_run_one", "def _resolve_queue_voice", "/api/queue/jobs", "job_queue.set_runner"]:
    parts.append(f"- server.py contains `{needle}`: {needle in srv}")
i3 = Path("index3.html").read_text(encoding="utf-8")
for needle in ["runJobQueue", "Chạy hàng chờ", "collectRunAllOpts"]:
    parts.append(f"- index3.html contains `{needle}`: {needle in i3}")
# include job_queue full
parts += ["", "## job_queue.py", "```python", Path("job_queue.py").read_text(encoding="utf-8"), "```"]
out = Path("docs/superpowers/sdd/diffs/whole-branch-review-package.md")
out.write_text("\n".join(parts), encoding="utf-8")
print("wrote", out, out.stat().st_size)
