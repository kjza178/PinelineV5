# Final whole-feature review — Job Queue Approach A

- **Date:** 2026-09-24
- **Scope:** all five tasks; design, plan/recheck, progress ledger, review package, and named spot-checks in `job_queue.py`, `server.py`, `index3.html`, and `index.html`
- **Verdict:** **Needs fixes**

## Executive summary

The core happy path is sound: the API surface exists, the worker blocks on `_gpu.submit(...)` via `Event.wait()`, the shared GPU executor defaults to one worker, done detection requires all five wired stages plus a non-empty output, stop is wired to `_stop_job`, persisted `current` is requeued after restart, and both UIs expose the queue controls.

The feature is not ready for use yet. A confirmed stop/enqueue race can accept a new job and then leave it permanently queued with no worker. A second enqueue can also silently replace options for jobs already waiting. Failure finalization/visibility does not meet the design: common runner failures have empty history details, can leave a manifest stage falsely `running`, and the UI never renders queue history. Persistence also uses a non-atomic overwrite despite crash resume being a core requirement.

## Findings

### Critical — enqueue immediately after Stop can strand accepted work

**Locations:** `job_queue.py:155-170`, `job_queue.py:182-191`, `job_queue.py:198-234`

`queue_stop()` sets `_stop = True` while the current worker is still alive. If `queue_add()` runs before that worker exits, `_ensure_worker_unlocked()` sees the live thread and returns without clearing `_stop` or arranging a successor. When the old runner returns, `_worker_loop()` exits because `_stop` is still true, even though the new queue is non-empty.

Confirmed repro:

```text
add_response: queued=['new'], queue=['new'], current='old'
final_state: queue=['new'], current=None, worker=False
```

This is a normal UI sequence—Stop, then retry—and the API falsely reports that the new job was accepted for execution.

**Required fix:** make stop/restart transitions generation-safe. At minimum, enqueueing new work while the old worker is winding down must either resume that worker after the current runner returns or start a successor. Add a deterministic regression test for Stop → immediate enqueue → new job runs.

### Important — later enqueue mutates options of already queued jobs

**Locations:** `job_queue.py:106-145`

`_opts` is global for the entire queue. Every `queue_add(..., opts=...)` replaces it before dedupe is applied. Therefore a duplicate request that adds no job can still change the voice/render settings used by all waiting jobs. The response also returns `cleaned` as `queued`, so it claims a duplicate was queued when it was not appended.

Confirmed repro:

```text
first queue: ['a', 'b'], voice='v1'
second request: ['b'], voice='v2'
second response queued: ['b']
actual queue unchanged: ['a', 'b']
effective queue voice changed to: 'v2'
```

This breaks the request contract: options submitted for one enqueue can silently alter earlier work.

**Required fix:** either persist options per queue entry/batch, or reject/serialize enqueues with different options while a queue is active. Return only IDs actually appended. Cover duplicate-current, duplicate-pending, and second-batch option behavior.

### Important — failures are neither finalized nor visible as specified

**Locations:** `server.py:2676-2800`, `job_queue.py:220-234`, `index3.html:2001-2016`, mirrored block in `index.html`

There are three connected problems:

1. `_queue_run_one()` returns only `"failed"` for missing voice, invalid voice, busy state, missing URL, download errors, executor submission errors, and incomplete output. The worker therefore records `detail: ""` for these expected failures. This does not satisfy the design rule `failed: chưa chọn giọng` or `failed: …`.
2. The runner marks the next stage `running` before download/preflight completes. Several later early returns release `__all__` but do not mark that stage failed/pending or heal it. A missing URL or download failure can leave the job appearing `running` after the queue has moved on.
3. `paintQueueStatus()` ignores `st.history` completely and clears the status when the worker becomes idle. The design explicitly requires current, remaining count, and history. A failed queue can therefore disappear from the UI with no explanation.

This elevates the deferred “empty history detail” and aspirational history text from minor documentation drift to a user-visible reliability gap.

**Required fix:** return a structured runner result containing status and detail; centrally finalize the manifest on every pre-submit failure; record bounded details; render at least the latest queue result/history in both UIs. Add tests for missing voice, invalid voice, missing URL, download failure, executor submission failure, and incomplete final output.

### Important — persistence overwrite is not crash-safe

**Location:** `job_queue.py:61-67`

`_save()` writes directly to `work/_job_queue.json`. Process termination, disk-full, or interruption during the write can leave partial JSON. `_load()` silently ignores malformed JSON, losing the entire persisted queue. Crash resume is a core acceptance requirement, so this is more than optional durability polish.

**Required fix:** write a sibling temporary file, flush/sync as appropriate, then atomically replace the target. Add a recovery test for malformed/interrupted state (and decide whether to preserve a last-known-good backup).

## Deferred-finding triage

- `_reset_for_tests` does not join the worker: **Minor, non-production**, but fix alongside new concurrency tests to prevent cross-test mutation/flakes. It should also reset hooks/runner deterministically.
- Non-atomic persistence: **Important, must fix** because restart recovery is a core feature.
- Limited `is_wired_done` branches: **Minor test gap**. Add malformed JSON, absent stage, empty output, and valid all-done cases; implementation itself is conservative.
- Empty history detail for failed voice: **Important, must fix**, as part of failure finalization/visibility.
- `skip_done=false` absent from API tests: **Minor test gap**. Implementation forwards the value correctly, but add the route-level regression test before merge.
- Broad API `except Exception` with `str(e)`: **Minor-to-important diagnostics issue**. It maps server/storage faults to HTTP 400 and exposes internal exception text. Log unexpected faults and return 500 with a stable message; reserve 400 for validated client errors.
- `runAll` not refactored to `collectRunAllOpts`: **No merge block**. The two paths intentionally have different voice/default behavior; forced DRY could obscure that distinction.
- History text is aspirational vs bare `"failed"`: **Important, must fix**; it reflects missing runtime/UI behavior, not merely wording.

## Requirement coverage

### Satisfied

- Four `/api/queue/jobs*` endpoints are present.
- `/ui3` and `index.html` reuse `listSel`/`.jchk` and expose Run/Stop controls.
- Queue execution is sequential at the queue-worker level and waits for the GPU future to finish.
- Default `_gpu` executor is single-worker (`JOB_WORKERS=1`).
- Done detection requires all wired stages and an output file.
- Missing manifests and already-done jobs are filtered.
- Current work is stopped through `_stop_job`; pending work is cleared.
- Persisted `current` is reinserted at the queue head on load.
- Single-job `/api/jobs/{id}/run-all` remains a separate path.

### Not fully satisfied

- Stop followed immediately by a new run is not reliable.
- Enqueue options are not isolated from later requests.
- Failure history lacks required reasons.
- UI does not display history.
- Some failed runners leave stale `running` manifest state.
- Persisted state is not protected against interrupted writes.
- End-to-end recheck items (real two-job sequencing, mid-TTS stop, and restart resume) are documented but not evidenced by automated integration tests in this package.

## Verification

Executed:

```text
python -m pytest tests/test_job_queue.py tests/test_job_queue_worker.py tests/test_queue_run_one.py tests/test_queue_jobs_api.py -q
11 passed, 4 pre-existing FastAPI on_event deprecation warnings
```

Additional targeted repros confirmed:

1. Stop → immediate enqueue leaves `queue=['new']`, `worker=False`.
2. Duplicate enqueue reports the duplicate as queued and changes `_opts` for existing pending work.
3. IDE diagnostics report no linter errors in the reviewed runtime/UI files.

The existing 11 tests validate the happy path but do not exercise the two confirmed concurrency/state-corruption cases.

## Must fix before use

1. Fix the Stop → immediate enqueue stranded-queue race and add a regression test.
2. Prevent later/duplicate enqueues from changing options of already queued jobs; report only actually appended IDs.
3. Finalize failed runner state, preserve actionable failure details, and display queue history in both UIs.
4. Make `_job_queue.json` persistence atomic and test interrupted/corrupt-state handling.

**Ready for use: no**

## Follow-up fixes

- **Date:** 2026-09-24
- **Status:** all four “Must fix before use” findings resolved.
- Stop → immediate enqueue now clears stop intent, and every worker exit clears
  its thread reference under lock so a doomed-but-still-alive worker cannot
  strand newly accepted work.
- Enqueue responses report only newly appended IDs; duplicate-only requests do
  not replace active queue options.
- Queue runners return `(status, detail)`, pre-submit failures finalize/heal the
  manifest, worker history preserves details, and both UIs show the latest
  three history entries.
- Queue persistence writes `._job_queue.json.tmp`, flushes/fsyncs it, then uses
  `os.replace` for an atomic update.
- Verification:
  `python -m pytest tests/test_job_queue.py tests/test_job_queue_worker.py tests/test_queue_run_one.py tests/test_queue_jobs_api.py -q`
  → **19 passed**, 4 pre-existing FastAPI deprecation warnings.

**Ready for use: yes**

## Re-review after fixes

- **Date:** 2026-09-24
- **Scope:** re-verified the four must-fix items against `job_queue.py`,
  `server.py::_queue_run_one`, `index3.html::paintQueueStatus`, the mirrored
  `index.html` queue status block, and the targeted regression tests.

1. **Stop → enqueue: confirmed fixed.** `queue_add()` sets `_stop = False`
   whenever it actually appends new work. A still-running worker therefore
   continues into the newly queued job after its current runner returns.
   `test_stop_then_immediate_enqueue_runs_new_job` deterministically covers
   Stop followed by immediate enqueue and passed.
2. **Options and queued IDs: confirmed fixed.** `_opts` changes only inside
   `if appended`, and the response's `queued` field is exactly `appended`, so
   duplicate/current/pending IDs are not reported as newly queued.
   `test_duplicate_enqueue_does_not_change_options_or_report_queued` covers
   the duplicate-only regression and passed.
3. **Failure finalization and visibility: confirmed fixed.**
   `_queue_run_one()` returns `(status, detail)`, routes pre-submit failures
   through `_failed()` to mark the active manifest stage failed, releases the
   aggregate claim and heals stale running state when submission does not
   complete, and reports actionable details for missing/invalid voice,
   missing URL, download errors, executor errors, and incomplete output.
   The worker stores the detail in bounded history. `paintQueueStatus()` in
   both UIs renders the latest three history records even when no live queue
   remains. The targeted runner/history tests passed.
4. **Atomic persistence: confirmed fixed.** `_save()` writes the sibling
   `._job_queue.json.tmp`, flushes and `fsync`s it, then atomically publishes
   it with `os.replace`. `test_save_uses_atomic_sibling_replace` passed.

Verification command:

```text
python -m pytest tests/test_job_queue.py tests/test_job_queue_worker.py tests/test_queue_run_one.py tests/test_queue_jobs_api.py -q
```

Result: **19 passed**, with 4 pre-existing FastAPI `on_event` deprecation
warnings.

**Ready for use: yes**
