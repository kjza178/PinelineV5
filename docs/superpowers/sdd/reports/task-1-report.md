# Task 1 Report: Module queue + persist

## What was implemented

Created `job_queue.py` — the state module for Approach A sequential run-all queue:

- **Constants:** `WORK_ROOT` (monkeypatchable, default `Path("work")`), `WIRED` tuple of 5 stages
- **`is_wired_done(work_dir)`** — checks manifest stages + non-empty `output.mp4`
- **State API:** `queue_state()`, `queue_add()`, `queue_clear()`, `queue_stop()`
- **Persist:** `_save()` / `_load()` to `work/_job_queue.json` (queue + opts + current); crash recovery re-queues interrupted `current`
- **Worker skeleton:** `_ensure_worker()`, `_ensure_worker_unlocked()`, `_worker_loop()` with `set_runner()` / `set_stop_hook()` hooks (not wired to pipeline in Task 1)
- **Test helper:** `_reset_for_tests(load_disk=False)`

Created unit tests in `tests/test_job_queue.py` (3 tests) and empty `tests/__init__.py`.

**Small fix vs brief sketch:** Added `global _opts` in `queue_add()` — without it, `_opts = dict(opts)` was a local assignment and persist roundtrip failed.

**Flake guard:** All 3 state-only tests monkeypatch `_ensure_worker_unlocked` to no-op after `_reset_for_tests()`.

## TDD Evidence

### RED (Step 2)

```bash
Set-Location z:\Pineline; python -m pytest tests/test_job_queue.py -v
```

```
ERROR collecting tests/test_job_queue.py
E   ModuleNotFoundError: No module named 'job_queue'
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
```

### GREEN (Step 4, after fix)

```bash
python -m pytest tests/test_job_queue.py -v
```

```
tests/test_job_queue.py::test_add_skips_missing_done_dedupe PASSED       [ 33%]
tests/test_job_queue.py::test_clear_empties_queue PASSED                 [ 66%]
tests/test_job_queue.py::test_persist_roundtrip PASSED                   [100%]

============================== 3 passed in 0.16s ==============================
```

Intermediate run after initial implementation: 2 passed, 1 failed (`test_persist_roundtrip` KeyError on `raw["opts"]["voice"]`) — fixed with `global _opts`.

## Files changed

| File | Action |
|------|--------|
| `job_queue.py` | Created |
| `tests/test_job_queue.py` | Created |
| `tests/__init__.py` | Created (empty) |

No changes to `server.py`, UI, or pipeline wiring (Task 2 scope).

## Self-review

- **Interfaces match brief:** All specified exports present; `_load()` runs at import.
- **Skip/dedupe logic:** Missing manifest → `skipped_missing`; all WIRED done + output → `skipped_done`; duplicate IDs deduped; existing queue/current not re-added.
- **Persist format:** JSON with `queue`, `opts`, `current`; indent=2; written on every state change.
- **Thread safety:** `_lock` guards shared state reads/writes; worker pops outside runner call.
- **Task 1 boundary respected:** No server routes, no `_auto_gpu`, no pipeline calls.
- **Commit skipped:** Workspace has no git repository (per instructions).

## Concerns

1. **`global _opts` fix** — Brief sketch omitted `global _opts` in `queue_add`; worth noting for Task 2 copy-paste.
2. **Import-time `_load()`** — Uses default `WORK_ROOT = Path("work")` until server overwrites in Task 2; may load stale queue from real `work/` if module imported before server sets path (expected Task 2 fix).
3. **Worker tests deferred** — `tests/test_job_queue_worker.py` not in Task 1 scope; worker behavior only covered indirectly via no-op patch.
