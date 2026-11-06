# Task 5 Review — Docs sync (job queue)

- **Reviewer scope:** Documentation sync only (spec, report, ledger vs code). No code changes.
- **Date:** 2026-09-24
- **Inputs:** `briefs/task-5-brief.md`, `reports/task-5-report.md`, `specs/2026-09-24-job-queue-design.md`

## Spec Compliance

**Verdict: Approved**

Task 5 correctly closes the SDD loop: the design spec reflects implemented behavior, deviations are documented in § Implementation notes, and the report/ledger align with verifiable code.

### Status

| Artifact | Claimed | Verified |
|----------|---------|----------|
| Design spec | `Status: implemented (Tasks 1–4)` | ✅ Matches code presence (`job_queue.py`, 4 API routes, UI qbar, tests) |
| Progress ledger | Task 5 ✅ complete | ✅ `2026-09-24-job-queue-progress.md` |
| Task 5 report | Status: complete | ✅ Accurate for docs-sync task (terminology differs from spec “implemented” — acceptable) |

### Spec ↔ code (core)

| Spec item | Match |
|-----------|-------|
| 4 endpoints `POST/GET /api/queue/jobs`, `…/stop`, `…/clear` | ✅ `server.py` routes + `JobQueueReq` |
| Persist `work/_job_queue.json` (`queue`, `opts`, `current`) | ✅ `job_queue._save` / `_load` |
| Worker sequential blocking via `_queue_run_one` + `_gpu.submit` + `Event.wait()` | ✅ `server.py` ~2676–2800 |
| UI `/ui3` reuse `listSel` / `.jchk`, `#qbar`, `#queue-status` | ✅ `index3.html`; mirror ✅ `index.html` |
| Single-job `POST /api/jobs/{id}/run-all` unchanged | ✅ Separate `_queue_run_one` path; `set_runner` at import |
| Non-goals (no cron, no parallel GPU, user tick required) | ✅ Global constraints honored in worker model |
| Restart resume when `queue` non-empty | ✅ `job_queue._load()` + `server.py` `_ensure_worker()` on startup |

### Documented deviations vs reality

| Deviation (spec § Implementation notes) | Verified |
|----------------------------------------|----------|
| **Workspace not a git repo** — no commit; track via progress ledger | ✅ `git status` → `fatal: not a git repository`; ledger + report both note this; brief Step 2 commit skipped appropriately |
| **`_resolve_queue_voice`** — no `list_clone_voices()[0]` fallback | ✅ `server.py` `_resolve_queue_voice` returns `""` when unset; `_queue_run_one` fails if missing/invalid (lines ~1961–1978, 2698–2700). Contrast: single-path `_resolve_voice` still falls back to `avail[0]` |
| **Stop hooks split:** `set_stop_hook(_stop_job)` on `queue_stop`; `set_clear_stop_hook(_clear_stop)` on worker pop before `_current` | ✅ `job_queue.py` `queue_stop` + `_worker_loop` lines ~155–216; wired at `server.py` import ~4793–4794; covered by `tests/test_job_queue_worker.py` |
| **Crash resume:** persisted `current` re-queued at head, not kept as `current` | ✅ `job_queue._load` lines ~81–85 |
| **`POST …/clear` returns `queue_state`** (not bare `{ok}`) | ✅ `queue_clear()` → `{"ok": True, **queue_state()}` |
| **Extra tests** beyond plan | ✅ `tests/test_queue_run_one.py`, `tests/test_queue_jobs_api.py` exist |

Fix log cross-reference (`docs/fixes/2026-09-24-queue-voice-stop-race.md`) matches the voice/stop-hook deviation narrative.

### Automated recheck (reviewer-run)

```text
python -m pytest tests/test_job_queue.py tests/test_job_queue_worker.py tests/test_queue_run_one.py tests/test_queue_jobs_api.py -q
11 passed in 1.41s
```

Matches report claim (11 passed).

### Minor doc gaps (non-blocking)

- **Skip/fail table** (spec § Skip / fail rules) still says history `failed: chưa chọn giọng`; `_queue_run_one` returns status `"failed"` without that detail string (Task 2 deferred “empty failure detail”). Behavior (pop, continue queue) is correct; only the history message text is aspirational in the table.
- **Brief Task 5** checkboxes remain `- [ ]` and still list a git commit step — superseded by ledger/report “no git” note; optional hygiene only.
- **Plan path** in spec header (`docs/superpowers/plans/2026-09-24-job-queue-sequential.md`) exists; brief references same plan — no drift found.

### Issues (Critical / Important / Minor)

**Critical**

- None.

**Important**

- None.

**Minor**

- Spec § API row for `clear` still shows `{ok}` in the main table; deviation is documented only in Implementation notes — consider merging into the table in a future doc pass (out of Task 5 scope if code unchanged).
- History detail for missing voice not localized; already tracked from Task 2.

## Assessment

**Approved.**

Task 5 docs sync is complete and accurate: spec status **implemented** is justified, reported deviations (**no git**, **`_resolve_queue_voice`**, **`set_clear_stop_hook` / `set_stop_hook`**, crash re-queue, clear response shape) all match the codebase. Queue test suite passes at reported count. No code changes required for this review.
