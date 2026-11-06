Spec Compliance

Verdict: **Approved**

Task 3 satisfies the scoped API requirements:

- `JobQueueReq(RunAllReq)` adds `job_ids: list[str]` and `skip_done: bool = True`, inheriting every `RunAllReq` pipeline/render field.
- Four routes under `/api/queue/jobs*`: `POST` add, `GET` state, `POST` stop, `POST` clear — each a thin delegate to `job_queue.queue_*`.
- Routes are placed immediately after `/api/queue/group` (lines 1636–1660) and before `/api/jobs/local-path`; the group route body is unchanged.
- `job_queue.py` and worker wiring at module bottom (`set_runner`, `set_stop_hook`, `_ensure_worker`) are untouched.
- POST add validates non-empty `job_ids` (400 `"chọn ≥1 job"`), strips blanks, dumps opts via `model_dump(exclude={"job_ids", "skip_done"})`, and forwards to `queue_add`.

### Verification

```text
python -m pytest tests/test_queue_jobs_api.py tests/test_job_queue.py tests/test_job_queue_worker.py -q
8 passed, 4 warnings in 1.79s
```

Scoped checks:

- Enqueue → GET state shows queue + opts (`voice`, `audio_mode`).
- Stop and clear return `ok: true`; clear empties queue.
- Empty `job_ids` → 400 with `"chọn"` in error body.

### Strengths

- Handler logic matches the brief verbatim — no scope creep into runner or worker semantics.
- Model placement next to `RunAllReq` keeps request types discoverable and ensures UI opts reuse the same field set.
- API tests use `TestClient` with worker disabled and queue reset, isolating HTTP contract from background execution.
- Whitespace-only IDs are filtered before the empty-list guard, so `"  "` / `[""]` correctly yield 400 instead of a no-op 200.

### Issues (Critical / Important / Minor)

**Critical**

- None.

**Important**

- None.

**Minor**

- API tests do not exercise `skip_done=false` or the exception→400 path on POST add; skip/dedupe behavior is covered at module level in `tests/test_job_queue.py`, not through the HTTP layer.
- No regression test asserts `/api/queue/group` still responds; safe because the route block is unmodified and new paths are distinct (`/api/queue/jobs` vs `/api/queue/group`).
- Broad `except Exception` on add matches the brief but returns raw `str(e)` to clients; acceptable for v1, slightly leaky for unexpected internal errors.
- Four FastAPI `on_event` deprecation warnings are pre-existing and unrelated to Task 3.

### Assessment (Approved | Needs fixes)

**Approved.** All four endpoints, the request model, group-route isolation, and worker non-regression constraints are met; scoped tests pass with no task-blocking findings.
