# Đợt 1 — chặn mất dữ liệu (review 6/10)

- **Date:** 2026-10-06
- **Job / khu vực:** `server.py`, `job_queue.py`, `restart_server.py`, `hongguo_bridge.py`, `agent_hongguo.py`, `agent_feeder.py`, `media_ts.py`, `assemble.py`
- **Status:** fixed. `assemble.py` + `media_ts.py` có hiệu lực ngay ở lần render kế (render.py reload); phần còn lại chờ restart server + sidecar.
- **Backup trước khi sửa:** `Z:\PinelineV2_backup_2026-10-06_0834.zip` (toàn bộ) + bản từng file `Z:\PinelineV2_codebak\2026-10-06_batch1\`.

## Triệu chứng / rủi ro

| Mã | Triệu chứng |
|---|---|
| S1 | Sau Stop/TTS lỗi, lần UI poll kế biến stage thành done (TTS có 1 `seg_*.wav` là "xong", mux có `output.mp4` cũ là "xong") → queue render thiếu câu. |
| S3 | Stop không kill ffmpeg render; heal xoá `output.partial.mp4` đang ghi. |
| S6 | Restart server giữa job → job đang chạy nhận opts toàn cục thay vì opts của nó. |
| S7 | Job chạy tiếp sau HOLD/QA render không watermark/logo/khung kênh. |
| H1 | `cleanup_fragments` xoá mọi video không có chữ "merged" (trailer, mùa khác, tập tải dở) chỉ cần có 1 file `(merged)`, không kiểm độ dài. |
| H2 | Tập tải sau khi đã gộp bị xoá mà không được gộp. |
| H3 | Poll gộp coi `done` của lần gộp series khác là xong → dọn tập trước khi Hongguo gộp. |
| H11 | Chuẩn hoá merged lỗi vẫn dọn tập. |
| A3 | "làm bộ số 3" khi chưa có danh sách → khớp chuỗi con "3" (第3季, 2023) → gộp + dọn nhầm bộ. Tên bộ gốc là chuỗi con của tên 第三季 → chọn nhầm mùa. |
| A4 | Hết 30 phút chờ tải vẫn gộp + dọn bản thiếu tập. |
| feeder | `agent_feeder` đọc `series_id` trong `/dl/status` (thật ra là `sid`) → không nhận ra bộ đang tải → có thể gộp sớm. |
| M2 | `ensure_job_audio_ts` chết giữa chừng → lần sau dời mốc lần 2 + đè backup gốc. |
| M5 | Câu TTS runaway bị nén rồi cắt theo độ dài trước nén → dài tới 1,6× kế hoạch, đẩy lệch câu sau. |

## Root cause

- S1: `read_job` (GET) gọi `_heal_stages_from_disk`; kiểm artifact chỉ là "file tồn tại"; salvage TTS/translate ghi file dở.
- S3: `WORK_ROOT/job.resolve()` ra `D:\PinelineV2_work\…`, `psutil.cwd()` trả `Z:\PinelineV2\work\…` (junction) → không bao giờ khớp.
- S6: worker `pop` opts của job khỏi `_opts_by_job` lúc bắt đầu → file hàng đợi không còn opts của job đang chạy.
- S7: stamp `queue_opts` chỉ liệt kê một số key, thiếu `brand*`, `logo`, `frame`.
- H1–H3, H11: không có điều kiện nội dung trước khi xoá; poll không phân biệt tên series.
- A3/A4: chọn folder bằng chuỗi con + cache theo tiến trình; vòng chờ không kiểm timeout.
- M2: ghi đè từng file tại chỗ, marker ghi cuối, `copy2` đè backup.
- M5: `wav[:dur*sr]` sau khi wav đã nén theo `ratio`.

## Fix

- **S1** `server.py`: `_stage_complete_on_disk()` — translate cần `script.display.json` không cũ hơn `script.json`; TTS cần số entry `tts.json` ≥ số câu có `vi`; mux cần `output.mp4` ≥ 1 MB và không cũ hơn `tts.json`. `read_job` chỉ đọc. `_heal_stale_running` + `_heal_stages_from_disk` (mark-done all) dùng kiểm tra chặt. Mark-done 1 bước giữ nguyên (thao tác chủ động).
- **S3** `server.py`: `_path_key()` = `os.path.realpath` + lower; dùng ở `_heal_stale_running` và `_kill_job_children`.
- **S6** `job_queue.py`: worker `get` thay `pop`, dọn sau khi job xong (trừ khi job đã được xếp lại). `restart_server.py`: thiếu snapshot → opts toàn cục + `queue_opts` trong manifest.
- **S7** `server.py` `_queue_run_one`: stamp `queue_opts` = toàn bộ opts (trừ `pin_opts`) + các key đã chuẩn hoá.
- **H1/H2/H3/H11** `hongguo_bridge.py`:
  - `merged_covers_fragments()`: merged mới hơn mọi tập (±60 s) và dài ≥ 98% tổng thời lượng tập (ffprobe); trả `stale`/`remerge`.
  - `cleanup_fragments()` chỉ dọn file đúng `_FRAG_RE`, chuyển vào `D:\Lib_trash\<bộ>\<thời điểm>\` (`_move_to_trash`), `purge_trash()` xoá lô > 7 ngày (`TRASH_KEEP_DAYS`).
  - Worker: merged cũ + tập mới mà tập lẻ đủ nội dung → cất merged cũ vào thùng rác, gộp lại; không đủ → báo lỗi, giữ nguyên.
  - Poll gộp: chỉ tin `done/pct` khi `name` trùng; phải thấy `running` đúng tên; 120 s không bắt đầu → lỗi. `mark_done` chỉ khi dọn ok. Chuẩn hoá lỗi → không dọn.
- **A3/A4** `agent_hongguo.py`: `_pick_lib_item()` (tên trùng → `series_id` → chuỗi con duy nhất, nhiều → hỏi lại); số trần không có danh sách → `select_rank`; hết giờ tải → `download_timeout`; thiếu tập → `download_incomplete`; `tool_hg_clean` dùng `_pick_lib_item`.
- **feeder** `agent_feeder.py`: `_downloading_sids()` đọc `sid` (fallback `series_id`), bỏ bộ `status=done`.
- **M2** `media_ts.py`: pha 1 tính ra `*.audio_ts.tmp` + `audio.ts.wav`, `_backup_once`; ghi `.audio_ts_pending.json`; pha 2 `_commit_retime()` thay file, mỗi bước chạy lại được; có pending → chỉ commit nốt.
- **M5** `assemble.py` `assemble_fit`: cắt `dur/ratio` khi đã nén.

## Recheck

1. `python Z:\PinelineV2\scripts\check_batch1.py` — **Pass nếu** in `ALL PASS 0` (44 kiểm tra; chỉ dùng thư mục tạm, cần ffmpeg).
2. `python -m pytest tests\test_job_queue.py tests\test_job_queue_worker.py tests\test_queue_run_one.py tests\test_queue_jobs_api.py -q -p no:cacheprovider` — 23 passed.
3. Sau restart server: bấm Stop giữa TTS một job → UI giữ TTS "dở", không tự thành done. Bấm Stop khi render → không còn `ffmpeg` có cwd là job.
4. Gộp một bộ Hongguo → tập lẻ nằm trong `D:\Lib_trash\<bộ>\…`, `trailer`/file khác tên giữ nguyên.
5. **Fail nếu:** job tự thành done sau Stop; tập lẻ bị xoá khi file gộp ngắn hơn tổng tập; agent chọn 第三季 khi nói tên bộ gốc.

## Liên quan

- Review: `docs/reviews/2026-10-06-code-review.md` (S1, S3, S6, S7, H1–H3, H11, A3, A4, M2, M5).
- Review ghi A4 "so `sid` sai" — thực tế `/dl/status` dùng `sid` (agent đúng); bên sai là `agent_feeder`.
