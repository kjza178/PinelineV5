# Job Queue (Approach A) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tick nhiều job chưa xong → chạy run-all đủ pipeline **tuần tự** đến hết hàng, có Dừng và persist nhẹ.

**Architecture:** Module `job_queue.py` (state + worker daemon, pattern `hongguo_bridge.merge_queue_*`). Runner blocking inject từ `server.py`: download sync + `_gpu.submit(_auto_gpu)` + `Event.wait()` (không chồng GPU). API `/api/queue/jobs*`. UI `/ui3` reuse checkbox `listSel`.

**Tech Stack:** Python 3.11+, FastAPI/`server.py`, threading, `Manifest`, `_auto_gpu`, pytest.

## Global Constraints

- Một job GPU tại một thời điểm (queue worker chờ `_gpu`; không gọi `_auto_gpu` song song).
- Mỗi job: resume bước thiếu; xong = 5 stage `WIRED_STAGES` done **và** `output.mp4` size > 0.
- Job thiếu giọng → history failed, không kẹt queue.
- Persist: `work/_job_queue.json` (queue + opts + current); history chỉ RAM.
- Không phá `POST /api/jobs/{id}/run-all` / claim `__all__` hiện tại.
- Primary UI: `index3.html` (`/ui3`).

## File map

| File | Responsibility |
|------|----------------|
| `job_queue.py` | State, persist, worker loop, `set_runner` |
| `server.py` | `_queue_run_one`, `JobQueueReq`, 4 routes, wire `set_runner` |
| `tests/test_job_queue.py` | Unit queue add/skip/clear/order |
| `tests/test_job_queue_worker.py` | Worker order + stop với fake runner |
| `index3.html` | qbar buttons + JS enqueue/stop/poll |
| `index.html` | Mirror tối thiểu (cùng API) |
| Spec (đã có) | `docs/superpowers/specs/2026-09-24-job-queue-design.md` |

---


---

### Task 5: Docs sync (spec đã viết)

**Files:**
- Verify: `z:\Pineline\docs\superpowers\specs\2026-09-24-job-queue-design.md`
- Verify: plan này

- [ ] **Step 1:** Đọc lại spec — API / persist / non-goals khớp code.
- [ ] **Step 2:** Commit docs nếu còn dirty

```bash
git add docs/superpowers/specs/2026-09-24-job-queue-design.md docs/superpowers/plans/2026-09-24-job-queue-sequential.md
git commit -m "docs: job queue sequential design and implementation plan"
```

*(Fix-log `docs/fixes/` chỉ tạo khi implement gặp/sửa bug runtime — không bắt buộc ở phase plan.)*

---

## Recheck (end-to-end)

1. 2 job chỉ `download=done`, cùng voice clone hợp lệ.
2. Tick cả hai → Chạy hàng chờ (`voice_bgm` hoặc `duck_bgm` + Tiếng gốc nền).
3. Job1 chạy ASR…mux; job2 **không** `running`/`__all__` đến khi job1 `mux=done` + có `output.mp4`.
4. Dừng giữa TTS job1 → queue trống; job2 không start; process ffmpeg/ASR theo cwd job1 chết.
5. Enqueue job 5/5 done + `output.mp4` → `skipped_done`.
6. Restart server khi `work/_job_queue.json` còn id → worker tự resume.

**Pass:** tuần tự đúng, stop dứt, skip done, persist resume.  
**Fail:** 2 ffmpeg/ASR cùng lúc; queue bỏ sót job chưa xong; 1-click single-job 409/regress.

---

## Spec coverage checklist

| Spec item | Task |
|-----------|------|
| Enqueue tick + opts 1-click | T3 + T4 |
| Skip mux done | T1 `is_wired_done` |
| Worker sequential blocking | T2 |
| Stop = clear + `_stop_job` | T1/T2 `queue_stop` + hook |
| Persist `_job_queue.json` | T1 |
| API 4 endpoints | T3 |
| UI `/ui3` listSel | T4 |
| Non-goal: no cron / no parallel | Global Constraints |
| Không phá `run_all` | T2 path riêng `_queue_run_one` |
