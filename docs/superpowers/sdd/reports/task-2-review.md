Spec Compliance

Verdict: **Approved**

Task 2 now satisfies the scoped requirements:

- Queue work remains sequential through `_gpu.submit(...)` plus `Event.wait()`.
- A queued job without an explicit or job-saved voice returns `failed`; the queue path no longer uses the global first-voice fallback.
- A stop issued after a job becomes current is not erased during runner startup.
- The existing single-job `/run-all` path is unchanged.
- Success still requires all wired stages to be `done` and a non-empty `output.mp4`.

### Important-fix verification

1. **Missing voice — fixed.**
   - `_queue_run_one` now calls `_resolve_queue_voice`.
   - That resolver only accepts `opts["voice"]`, the job manifest's TTS voice, or the job's `tts_config.json` voice.
   - It returns an empty string when none exists, and `_queue_run_one` returns `failed` before claiming `__all__`.
   - `test_missing_job_voice_fails_without_global_fallback` confirms that an available global clone voice is not selected implicitly.

2. **Stop race — fixed.**
   - `_queue_run_one` no longer calls `_clear_stop` after claiming the job.
   - The worker clears stale stop state before assigning `_current`, while holding the queue lock.
   - Therefore `queue_stop()` either runs before the worker takes the job, causing the worker to exit, or runs after `_current` is published and sets a stop that the runner cannot subsequently wipe.
   - `test_stop_after_claim_is_not_cleared` confirms a stop arriving at claim time remains set and returns `stopped`.
   - `test_worker_clears_stale_stop_before_runner` confirms stale-stop clearing precedes runner invocation.

3. **Focused tests — fixed.**
   - `tests/test_queue_run_one.py` directly exercises missing-voice failure, stop-after-claim behavior, and already-complete short-circuiting.
   - `tests/test_job_queue_worker.py` covers sequential order, queue stop, and stale-stop clearing order.
   - Scoped verification result: `9 passed, 4 warnings in 1.71s`.
   - `python -m py_compile server.py job_queue.py tests/test_queue_run_one.py tests/test_job_queue_worker.py` completed successfully.
   - IDE diagnostics report no linter errors in the scoped files.

### Strengths

- `_resolve_queue_voice` cleanly separates queue behavior from the existing global fallback used elsewhere.
- Moving stale-stop clearing into the worker closes the race without changing the single-job run-all path.
- The queue worker publishes `_current` only after stale state is cleared, making the stop ordering explicit.
- Pre-submit exits release the `__all__` claim in `finally`; submitted GPU work releases it in the GPU callback.
- Download cancellation now reports `stopped` when the stop flag is present.
- Final `done` remains guarded by `job_queue.is_wired_done`.

### Issues (Critical / Important / Minor)

**Critical**

- None.

**Important**

- None.

**Minor**

- The four test warnings are existing FastAPI `on_event` deprecation warnings and are unrelated to Task 2 behavior.
- Queue history still records an empty detail for status-only runner failures such as missing voice. This does not violate the Task 2 gate, which requires the job to be recorded as `failed`, but richer failure details would improve diagnostics.

### Assessment (Approved | Needs fixes)

**Approved.** Important issues #1, #2, and #3 are resolved, and the scoped verification passes without task-blocking findings.
