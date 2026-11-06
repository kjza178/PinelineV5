# Task 2 Report: Worker gọi run-all thật + stop

## What was implemented

### Blocking queue runner

Added `server._queue_run_one(job_id, opts)`, a queue-specific synchronous path that:

- Rejects missing jobs and jobs without a valid clone voice.
- Heals stale `running` stages and skips jobs already complete.
- Persists queue-provided voice, speed, TTS engine, and ASR engine options.
- Claims `__all__` without changing the existing `/run-all` endpoint or `_auto_pipeline`.
- Downloads the source synchronously when it is missing.
- Submits `_auto_gpu` to the single-worker `_gpu` executor and waits on a `threading.Event`.
- Returns exactly `done`, `failed`, or `stopped`.
- Releases the `__all__` claim on GPU completion and on every pre-submit exit/error.
- Verifies all wired stages plus a non-empty `output.mp4` before returning `done`.

### Runtime wiring

Added the late `job_queue` wiring block before `if __name__ == "__main__"`:

- Sets `job_queue.WORK_ROOT = WORK_ROOT`.
- Reloads persisted queue state from the server work root.
- Registers `_queue_run_one` as runner.
- Registers `_stop_job` as stop hook.
- Restarts the worker when persisted queue items exist.

The import is deliberately late, after `_queue_run_one` and `_stop_job` exist, so `job_queue` does not need to import `server`.

### Worker tests

Created `tests/test_job_queue_worker.py` with the two brief-specified fake-runner tests:

1. Jobs execute sequentially in insertion order.
2. Stop clears remaining jobs and invokes the stop hook for the active job.

## TDD evidence

The new worker tests passed on their first run (`2 passed`). This is expected because Task 1 had already shipped the worker loop, ordering, and stop-hook behavior under test. Therefore this run did not provide a RED phase for those existing behaviors; it confirmed the Task 1 worker implementation already met the Task 2 test contract.

No full `server.py` import test was added because the brief explicitly keeps worker unit tests isolated from the full FastAPI/pipeline import graph. The integration code was validated by Python compilation and static diagnostics.

## Verification

```text
python -m pytest tests/test_job_queue_worker.py tests/test_job_queue.py -v
5 passed in 0.79s
```

```text
python -m py_compile server.py job_queue.py tests/test_job_queue_worker.py
exit code 0
```

IDE diagnostics for `server.py` and `tests/test_job_queue_worker.py`: no linter errors.

## Files changed

- `server.py` — added blocking runner and late queue wiring.
- `tests/test_job_queue_worker.py` — added order and stop tests.
- `docs/superpowers/sdd/reports/task-2-report.md` — this report.

`job_queue.py` required no changes.

## Concerns

- `_auto_gpu` catches and logs most internal pipeline exceptions instead of re-raising them. `_queue_run_one` therefore determines failure primarily from the final wired-stage/output check, which is correct but does not preserve a detailed exception string in queue history.
- The exact fake-runner tests could not demonstrate RED because their worker behavior was already implemented by Task 1.
- No git commands or commits were performed, per instruction.

## Follow-up fixes

- Added `_resolve_queue_voice` so queued jobs accept only `opts["voice"]` or the
  voice saved in that job's manifest/`tts_config.json`; the global first-voice
  fallback is no longer used by `_queue_run_one`.
- Added `job_queue.set_clear_stop_hook`. The worker clears stale stop state while
  popping a job and before publishing it as `_current`; `_queue_run_one` no
  longer clears stop state after claiming `__all__`.
- A download exception now returns `stopped` when the job stop flag is set.
- Added focused `_queue_run_one` tests for missing voice, stop-after-claim, and
  already-complete jobs, plus a worker ordering test for the clear-stop hook.

### Test commands/output

```text
python -m pytest tests/test_queue_run_one.py -q
3 passed, 4 warnings in 1.13s
```

```text
python -m pytest tests/test_queue_run_one.py tests/test_job_queue_worker.py tests/test_job_queue.py -q
9 passed, 4 warnings in 1.72s
```

```text
python -m py_compile server.py job_queue.py tests/test_queue_run_one.py tests/test_job_queue_worker.py
exit code 0
```

IDE diagnostics for all four changed Python files: no linter errors.
