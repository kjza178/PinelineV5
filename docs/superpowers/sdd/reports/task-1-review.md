### Spec Compliance
Verdict: Compliant. The implementation provides every Task 1 interface, persists `queue`, `opts`, and `current` to `work/_job_queue.json`, and defines completion as all five `WIRED` stages being `done` plus a non-empty `output.mp4`. The worker skeleton executes one runner call at a time, and the review package contains no `server.py` or UI changes.

### Strengths
- `is_wired_done` faithfully encodes the required five-stage and output-size completion rule, including safe handling of missing or invalid manifests.
- Queue admission handles missing jobs, completed jobs, duplicate input IDs, already queued IDs, and the current job.
- Shared queue state is copied at API boundaries and guarded by a lock; the runner executes outside the lock while queue progression remains serial.
- Crash recovery moves a persisted `current` job back to the front of the queue.
- The implementation corrected the brief sketch's missing `global _opts`, and the focused tests cover the specified add/skip/dedupe, clear, and persistence behavior.
- Scope discipline is good: no pipeline wiring, voice-resolution logic, `server.py`, or UI changes were introduced.

### Issues (Critical / Important / Minor)

**Critical:** None.

**Important:** None.

**Minor:**
- `_reset_for_tests()` discards the `_thread` reference without joining a potentially live worker. Current state-only tests avoid this by disabling worker startup, so Task 1 is unaffected, but future worker tests could leak an old daemon that mutates newly reset globals.
- Persistence uses a direct `write_text()` rather than a temporary-file-and-replace pattern. A process interruption during writing can leave invalid JSON; `_load()` then silently ignores it and loses the recoverable queue. This is acceptable for the requested lightweight persistence, but it is a durability limitation.
- The tests follow the brief exactly but do not directly pin the zero-byte-output and one-missing-stage branches of `is_wired_done`; regressions in the key completion predicate would therefore have limited focused coverage.

### Assessment (Task quality: Approved)
Task 1 matches its requirements and is sufficiently well-built for its intended boundary. The noted items are hardening opportunities rather than blockers.
