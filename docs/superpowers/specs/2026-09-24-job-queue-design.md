# Job Queue tuần tự (Approach A) — Design

- **Date:** 2026-09-24
- **Status:** implemented (Tasks 1–4, 2026-09-24)
- **Plan:** `docs/superpowers/plans/2026-09-24-job-queue-sequential.md`
- **Report:** `docs/superpowers/sdd/reports/task-5-report.md`

## Goal

User tick nhiều job chưa hoàn thành trên sidebar → bấm **Chạy hàng chờ** → server chạy **run-all đủ pipeline** (bước thiếu → mux có `output.mp4`) **một job xong mới tới job tiếp**, đến hết list hoặc bị Dừng.

## Motivation

Hiện chỉ có 1-click cho **một** job. Khi có nhiều phần series / nhiều video chờ, user phải ngồi bấm từng cái. Queue tuần tự tận dụng GPU 1 job/lần (không OOM), giống hàng merge Hồng Quả (`hongguo_bridge.merge_queue_*`).

## Non-goals (v1)

- Không hẹn giờ ban đêm / cron / schedule window.
- Không chạy song song 2 job GPU (ASR/TTS/mux).
- Không tự lấy mọi job pending — **user phải tick** (reuse checkbox `listSel` / `.jchk` trên `/ui3`).
- Không đổi semantics `POST /api/jobs/{id}/run-all` cho single-job (vẫn `_dl` + `_gpu.submit` như hiện tại).

## User flow

1. Sidebar: tick N job (checkbox đã có cho gom nhóm).
2. Chọn opt trên thanh 1-click đang chọn (giọng, ASR, Âm nền, **Tiếng gốc nền**, render…) — cùng field `RunAllReq`.
3. Bấm **▶ Chạy hàng chờ (N)** → `POST /api/queue/jobs` với `job_ids` + opts.
4. Server: skip job mux đã done (`skip_done=true`); enqueue phần còn lại; worker chạy tuần tự.
5. UI poll `GET /api/queue/jobs` → hiện `đang chạy {id} · còn N · history`.
6. **⏹ Dừng hàng chờ** → clear queue + `_stop_job(current)` (cùng cơ chế stop ffmpeg/cwd như stop 1 job).

## Done criteria (một job)

Job coi là xong khi:

- `Manifest` mọi stage trong `WIRED_STAGES` = `done` (`download`, `asr`, `translate`, `tts`, `mux`), **và**
- `work/<job_id>/output.mp4` tồn tại và size > 0.

## Skip / fail rules

| Case | Hành vi |
|------|---------|
| Job không có `manifest.json` | skip vào `skipped_missing` |
| Mux done + có `output.mp4` và `skip_done` | `skipped_done`, không enqueue |
| Trùng id trong request / đã trong queue / đang `current` | dedupe, không double-queue |
| Thiếu giọng clone (body + job đều không có) | history `failed: chưa chọn giọng`, pop, tiếp job sau |
| Job bị stop giữa chừng | history `stopped`; queue đã clear → worker thoát |
| Exception trong pipeline | history `failed: …`; tiếp job sau (không kẹt) |

## API

| Method | Path | Body / response |
|--------|------|-----------------|
| `POST` | `/api/queue/jobs` | `JobQueueReq` (= `job_ids` + mirror `RunAllReq` + `skip_done`) → `{ok, queued, skipped_done, skipped_missing, queue, current}` |
| `GET` | `/api/queue/jobs` | `{queue, current, history[-20], worker, opts}` |
| `POST` | `/api/queue/jobs/stop` | clear queue + stop current → `{ok, stopped_job}` |
| `POST` | `/api/queue/jobs/clear` | chỉ clear list (không stop job đang chạy) → `{ok}` |

**Lưu ý path:** đã có `POST /api/queue/group` (gom nhóm). Path mới là `/api/queue/jobs` — không đụng group.

## Persist

File: `work/_job_queue.json`

```json
{
  "queue": ["abc", "def"],
  "opts": { "voice": "v5", "audio_mode": "duck_bgm", "orig_vol": 0.22 },
  "current": null
}
```

- Ghi sau mọi `add` / `pop` / `clear` / `stop`.
- Load khi server import `job_queue` (hoặc `server` startup): nếu `queue` còn phần tử → restart worker.
- `history` **không** persist (chỉ memory, tối đa 20).

## Concurrency model

```
UI ──POST──► queue_add ──► list[_q]
                              │
                         worker thread (daemon)
                              │
                    for each job_id:
                      claim __all__
                      download sync (nếu cần)
                      _gpu.submit(_auto_gpu) + Event.wait()   ← GPU vẫn 1 hàng
                      release __all__
                      pop next
```

- Worker **không** gọi `_auto_pipeline` non-blocking (vì nó return ngay sau `_gpu.submit` → chồng job).
- Single-job `run-all` giữ nguyên; queue dùng path blocking riêng (`_queue_run_one` trong `server.py`).

## UI (primary: `/ui3` → `index3.html`)

- Reuse `listSel` / `.jchk` — **không** thêm checkbox thứ hai.
- Thêm vào `#qbar` (cạnh Gom nhóm):
  - `▶ Chạy hàng chờ`
  - `⏹ Dừng hàng chờ`
  - `#queue-status` text
- Opts lấy từ `#auto-*` giống `runAll()` (gồm `auto-ovol`).
- Mirror tối thiểu trên `index.html` nếu còn dùng `/` (cùng API).

## Out of scope follow-ups (ghi nhận, không làm v1)

- Approach B: hẹn giờ / night window.
- Pause/resume mid-queue (chỉ stop + clear).
- Per-job override opts khác nhau trong cùng một enqueue.

## Implementation notes (vs spec draft)

Khớp spec: 4 API `/api/queue/jobs*`, persist `work/_job_queue.json`, worker tuần tự blocking (`_queue_run_one`), UI `/ui3` reuse `listSel`, mirror `index.html`.

Lệch / bổ sung nhỏ:

- **Workspace không phải git repo** — không có commit; theo dõi qua `docs/superpowers/sdd/2026-09-24-job-queue-progress.md`.
- **`_resolve_queue_voice`** — resolver riêng cho queue (không fallback `list_clone_voices()[0]` như single run-all); thiếu giọng → runner trả `failed`, worker pop tiếp (fix: `docs/fixes/2026-09-24-queue-voice-stop-race.md`).
- **Stop hooks tách đôi:** `set_stop_hook(_stop_job)` khi `queue_stop`; `set_clear_stop_hook(_clear_stop)` khi worker pop job (trước `_current`) — tránh race xóa cờ dừng.
- **Crash resume:** nếu persist còn `current` khi restart, id đó được **đẩy lại đầu queue** (không persist `current` qua restart).
- **`POST …/clear`:** response trả thêm `queue_state` (không chỉ `{ok}`).
- **Tests:** ngoài plan — `tests/test_queue_run_one.py`, `tests/test_queue_jobs_api.py` (11 tests queue suite pass).
