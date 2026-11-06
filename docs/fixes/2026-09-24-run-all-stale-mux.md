# 1-click (run-all) lỗi liên tục / kẹt mux running

- **Date:** 2026-09-24
- **Job / khu vực:** `server.py` run-all / `_do_render` / claim `__all__`
- **Status:** fixed

## Triệu chứng

Bấm **Chạy tự động** nhiều lần hoặc sau khi Dừng giữa encode → báo lỗi kiểu “job đang chạy bước mux” (409), hoặc pipeline chồng (2 ffmpeg), hoặc UI nhảy lại ASR dù đã done.

## Root cause

1. **Claim `__all__` nhả sớm** — `_wrapped_all` release ngay sau `_auto_pipeline` chỉ mới `_gpu.submit(_auto_gpu)` → suốt ASR→mux không còn lock → double-click xếp thêm pipeline.
2. **`mux=running` mồ côi** — `_do_render` `mark_running("mux")` rồi kill / `run_render` skip → không `mark_done` → manifest kẹt running → mọi run-all sau bị 409.
3. **Mark sai bước đầu** — run-all luôn `mark_running("asr")` dù ASR đã done → UI loạn.

## Evidence

- a948 sau kill remux: `mux.status == "running"` trong khi `output.mp4` ~3.9GB vẫn còn, không còn ffmpeg.
- Hai `ffmpeg` cùng ghi `output.partial.mp4` (parent uvicorn + script remux).

## Fix

- `_auto_pipeline`: release `__all__` trong `finally` của `_gpu_wrapped` (hoặc nếu không submit GPU).
- `_heal_stale_running` + gọi ở `run-all` (trước busy-check) và `stop`.
- `_next_incomplete_stage`: chỉ mark bước chưa done.
- `_do_render`: skip sớm nếu mux done; try/except `mark_failed`; nếu vẫn `running` sau skip → trả `done`.

## Recheck

1. Job đã đủ `download…tts` + `output.mp4`, cố tình ghi manifest `mux.status=running`, **không** có ffmpeg.
2. `POST /api/jobs/<id>/run-all` (có voice) — **không** được 409 vì mux; heal → done hoặc chạy tiếp đúng.
3. Trong lúc 1-click đang ASR/TTS: bấm run-all lần 2 → 409 / “đã nhận” / busy (không xếp pipeline thứ hai).
4. Dừng giữa mux: sau stop, nếu còn `output.mp4` đủ lớn → mux về `done` (hoặc pending nếu không có artifact); run-all sau không kẹt 409 mãi.
5. Job all-done: run-all không được `mark_running(asr)` — bước early phải là thiếu thật (thường `mux` nếu remux) hoặc skip nhanh.

**Pass nếu:** không còn 409 giả; không 2 ffmpeg một job; stop không để mux running mãi khi đã có output.

**Fail nếu:** click 1-click lần 2 vẫn spawn thêm `_auto_gpu`, hoặc mux stuck running sau kill.

## Liên quan

- `server.py`: `_auto_pipeline`, `_do_render`, `run_all`, `stop_job`, `_heal_stale_running`
- Job chứng minh: `a948f052b724`
