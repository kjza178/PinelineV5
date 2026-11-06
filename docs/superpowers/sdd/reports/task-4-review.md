Spec Compliance

Verdict: **Approved**

Task 4 satisfies the scoped UI requirements on `/ui3` (primary) with a full mirror in `index.html`:

- **Reuse `listSel` / `.jchk`:** Queue enqueue reads `[...listSel]`; sidebar job rows still use the existing `.jchk` checkbox and `toggleListSel()`. No second selection set or queue-only checkbox was added.
- **`#qbar` controls:** `renderList` injects `btn-queue-run` (▶ Chạy hàng chờ), `btn-queue-stop` (⏹ Dừng hàng chờ), and `#queue-status` immediately after the selection-count hint — matches the brief HTML/JS contract.
- **Opts + guards:** `collectRunAllOpts()` reads the full 1-click run-all field set, including `auto-ovol` → `orig_vol`. `runJobQueue()` requires ≥1 ticked job, `confirm(...)`, voice on `#auto-voice`, then POST `/api/queue/jobs` with `skip_done: true` and spread opts. `stopJobQueue()` POST `/api/queue/jobs/stop`.
- **Poll when queue active:** `paintQueueStatus()` GET `/api/queue/jobs`, paints `#queue-status`, and starts a 2s interval (calling `paintQueueStatus` + `refresh`) while `st.worker || st.current || st.queue.length`; timer cleared when idle. Invoked at end of `refresh()` in both HTML files.
- **Mirror:** Queue block (`collectRunAllOpts` through `stopJobQueue` + `_queuePollTimer`) is byte-identical between `index3.html` and `index.html`; qbar markup matches in both.

### Verification

```text
node -e "… extract queue JS from index3.html / index.html …"
index3.html: syntax OK
index.html: syntax OK
queue block identical: true
```

Scoped grep (via review package): all required symbols present in both files — `Chạy hàng chờ`, `btn-queue-run`, `collectRunAllOpts`, `runJobQueue`, `stopJobQueue`, `paintQueueStatus`, `paintQueueStatus()` call in `refresh()`.

Reported manual path (not re-run in this review): tick ≥2 `.jchk` → Chạy hàng chờ → confirm → status `Queue: … · còn …` → Dừng hàng chờ.

### Strengths

- Implementation matches the brief snippet verbatim — low drift risk against Task 3 API (`JobQueueReq` / `/api/queue/jobs*`).
- `orig_vol` from `auto-ovol` ensures queue runs honor **Tiếng gốc nền**, aligned with design spec user flow step 2.
- Polling tied to `refresh()` keeps sidebar/detail in sync while the worker runs, not just the status span.
- Existing `.btn.stop` styling reused; no new CSS surface.

### Issues (Critical / Important / Minor)

**Critical**

- None.

**Important**

- None.

**Minor**

- Optional DRY refactor (`runAll` → `collectRunAllOpts()`) not done; `runAll` still inlines opts with different fallbacks (`translate_mode` default `oneshot` vs queue `batch`, richer voice resolution). Acceptable — brief marks refactor optional; queue path intentionally requires `#auto-voice` only.
- Poll condition is `worker || current || queue.length`, slightly broader than “worker active” alone; matches brief and is needed to show queued jobs before/at worker start.
- `runJobQueue` / `stopJobQueue` are not wrapped in `guardAct` (unlike `runAll`); double-click could issue duplicate POSTs — backend dedupe limits harm; not in Task 4 scope.
- No automated browser/integration test for enqueue → sequential run → stop; reliance on manual check and JS syntax compile.
- Git commit (brief Step 5) intentionally skipped per implementer note.

### Assessment (Approved | Needs fixes)

**Approved.** All task-scoped UI constraints are met in `index3.html` with a matching `index.html` mirror; no blocking gaps against the Task 4 brief or review package.
