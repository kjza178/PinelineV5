# 2026-10-06 — Đợt 4 review: tranh chấp ghi, một bản tiến trình, checkpoint an toàn

Review gốc: `docs/reviews/2026-10-06-code-review.md` (S2, S8, S9, S10, S11, A5, A6, X4, M10, M11, M12, M13).

Backup trước khi sửa:

- Zip: `Z:\PinelineV2_backup_2026-10-06_0944.zip`.
- Bản gốc từng file: `Z:\PinelineV2_codebak\2026-10-06_batch4\` — `manifest.py`, `server.py`, `job_queue.py`, `agent_tele_cmd.py`, `agent_autopilot.py`, `agent_core.py`, `clone_tts.py`, `render.py`, `assemble.py`, `asr.py`, `translate.py`, `agent_watch.py`, `restart_server.py`. Năm file `fileio.py`, `fun_asr_nano.py`, `firered_asr.py`, `sensevoice_asr.py`, `paraformer_zh.py` lấy từ zip 0944 (chụp trước khi sửa) vì sửa trước khi chép riêng.

Test: `scripts/check_batch4.py` 56/56 (thư mục tạm, cổng 18902, không đụng server/sidecar/hàng đợi thật). Đợt 1 ALL PASS, đợt 2 69/69, đợt 3 35/35 (chạy lặp 6 lần), pytest 39/40 — `test_hardsub_asr.py::test_merge_rejects_neighbor_line` hỏng từ trước (file 20/09, không bị đụng), để đợt 6.

## Triệu chứng

| Mã | Triệu chứng |
|---|---|
| S2 | Object `Manifest` sống lâu (render, TTS) `save()` cả snapshot cũ → xoá cờ HOLD/QA, `title_vi`, tiến độ do nơi khác vừa ghi. Server và subprocess asr/tts ghi cùng file không khoá liên tiến trình. `_patch_tts_fields` / `_patch_asr_fields` đọc-sửa-ghi không khoá. |
| S8 | `regen_tts`, `mux`, `translate` (dịch lại / soát), `translate/fill`, `assemble` không giữ chỗ (claim) → bấm khi job đang chạy trong hàng đợi tạo việc song song cùng thư mục. |
| S9 | `mark-done` khi job đang chạy trong hàng đợi thả claim `__all__` + xoá cờ Stop → bước thứ hai chạy song song. |
| S10 | Worker hàng đợi khởi động lúc import, trước khi startup reset stage treo + kill engine "orphan" → job vừa chạy bị reset/kill. |
| S11 | Không khoá một bản server: bản sau kill engine của bản đang chạy. Kill engine theo `job_id` trong cmdline → V1 (`Z:\Pineline`) cùng URL có cùng `job_id` bị kill nhầm. |
| A5 | `HTTPServer` trên Windows bật `SO_REUSEADDR` → sidecar thứ 2 bind trùng 8802 và cùng poll Telegram. Các loop chạy trước khi bind. |
| A6 | Auto-pilot xếp lại job `failed` mỗi tick (lặp lỗi vô hạn) và cả job HOLD / QA chặn đang chờ duyệt. |
| X4 | `sync_pending_to_batch` remove toàn bộ hàng chờ rồi add lại → worker có thể hết việc và thoát giữa chừng, thứ tự/opts lẫn. |
| M10 | Mỗi engine ASR có luật dùng lại `audio.wav` riêng (nano dùng lại cả khi force); trích dở vẫn bị dùng. |
| M11 | `asr.json`, `script.json` ghi thẳng mỗi 1,5 s; đọc hỏng thì im lặng làm lại từ đầu. `dub_fit.wav` ghi tại chỗ trong khi `.fit_mode` cũ còn → file dở được coi là hợp lệ. |
| M12 | TTS resume nhận `seg_{i}.wav` chỉ theo chỉ số → sửa lời / đổi giọng / tốc độ vẫn dùng clip cũ. |
| M13 | `mixed_audio.wav` chỉ so mtime với dub → đổi `audio_mode` / `orig_vol` / BGM vẫn ra bản trộn cũ. |

## Sửa

- **`manifest.py`**:
  - `_merge3(base, mine, theirs)`: key mình không đổi → lấy bản đĩa; chỉ mình đổi → của mình; cả hai đổi dict → gộp sâu; còn lại mình thắng; xoá key được giữ.
  - `save()`: trong khoá thread + `_xproc_lock` (file lock liên tiến trình, lỗi thì ghi không khoá như cũ), đọc lại đĩa, gộp 3 chiều với snapshot lúc load. Giữ chặn ghi đè khi load hỏng / stages rỗng.
  - `update(fn) -> bool`: đọc lại đĩa → `fn(data)` → ghi, trong cả hai khoá. Hỏng / thiếu stages / `fn` trả `False` → không ghi.
- **`server.py`**:
  - `_patch_tts_fields` / `_patch_asr_fields` dùng `Manifest.update`. TTS: giá trị không đổi vẫn ghi lại `tts_config.json` nếu thiếu.
  - `_busy_response`, `_submit_claimed`; `regen_tts`, `mux_job`, `retranslate_job`, `translate_fill`, `assemble_job` trả 409 khi job đang có claim hoặc stage `running`, giữ claim tới khi việc xong (kể cả lỗi). Agent gọi các hàm này cũng nhận 409.
  - `_iter_job_engine_procs`: chỉ khớp cmdline chứa đường dẫn `WORK_ROOT/job_id` (và realpath).
  - `_kill_job_children`: worker `vieneu_batch`/`omnivoice_batch` chỉ bị kill khi cmdline chứa đường dẫn job (worker nhận `work/<job>/tts/_<engine>_job.json`), không kill mọi worker.
  - `mark_job_done`: 409 khi `_job_in_pipeline`.
  - Worker hàng đợi khởi động trong `@app.on_event("startup")` sau `_reset_stale_running`; bỏ `_ensure_worker()` lúc import.
  - `__main__`: khoá `msvcrt` trên `.server_{port}.lock` → bản thứ 2 thoát ngay.
  - `POST /api/queue/jobs/opts` `{"opts_by_job": {...}}`: đổi opts job đang chờ tại chỗ (lọc field theo `JobQueueReq`, `resolve_job_opts`).
- **`job_queue.py`** `queue_update_opts`: đổi opts dưới khoá hàng đợi, giữ thứ tự, không đụng job đang chạy.
- **`agent_autopilot.py`**: `sync_pending_to_batch` gọi `/opts` (server cũ trả 404/405 → cách cũ); `tick_once` bỏ `failed_ids` khỏi danh sách xếp.
- **`agent_core.py`** `classify_jobs`: `need_queue` chỉ gồm job `pending` không HOLD, không QA chặn.
- **`agent_tele_cmd.py`**: `_single_instance_lock` (`.sidecar_{port}.lock`), `_ExclusiveHTTPServer` (`SO_EXCLUSIVEADDRUSE`, không reuse), bind trước khi chạy loop, thử bind 15 s (bản cũ đang chết dở lúc restart).
- **`fileio.py`**:
  - `atomic_write_json`, `read_json_checkpoint` (hỏng → đổi tên `.corrupt-<ts>`, log, trả mặc định);
  - `atomic_write_text(fsync=...)`;
  - **lỗi thật**: `file_lock` không bắt `PermissionError` — Windows trả lỗi này khi tạo `.lock` đúng lúc bản cũ đang chờ xoá → tiến trình văng lỗi. Test 3 tiến trình đợt 3 chập chờn (1/5 lần ra < 120). Đã bắt và thử lại.
- **`asr.py`**: `extract_audio` ghi `.partial.wav` rồi replace + marker `audio.wav.json` (tên/size/mtime nguồn + filter mốc). `audio_wav_stale` / `ensure_audio_wav`: có marker → so nguồn; chưa có marker → chỉ trích lại khi wav ngắn hơn nguồn > 1 s (wav dài hơn = trục dồn mẫu, `media_ts` cần để dời mốc). Resume Whisper giữ wav cũ chưa có marker. Checkpoint `asr.json` nguyên tử; đọc hỏng không còn im lặng.
- **`fun_asr_nano.py`, `firered_asr.py`**: `ensure_audio_wav(force=...)` (nano hết dùng lại khi force; chế độ sidecar giữ như cũ). **`sensevoice_asr.py`, `paraformer_zh.py`**: xoá wav cũ khi `audio_wav_stale`, phần còn lại giữ luật riêng.
- **`translate.py`**: mọi lần ghi `script.json` nguyên tử; resume đọc qua `read_json_checkpoint`.
- **`assemble.py`** `assemble_fit`: gỡ `.fit_mode` trước, ghi `dub_fit.partial.wav`, replace, rồi mới ghi `tts_fit.json` + stamp → crash giữa chừng thì lần sau ghép lại.
- **`clone_tts.py`**: key clip = sha1(lời, giọng, engine, tốc độ). Resume bỏ clip khác lời hoặc khác key (xoá wav). Clip cũ chưa có key vẫn nhận nếu lời khớp. `tts/_keys.json` ghi key các câu sắp đọc → quét wav trên đĩa bỏ wav có key khác. `tts.json` mới có trường `key`.
- **`render.py`** `_ensure_mixed_audio`: `mixed_audio.json` lưu filter + (đường dẫn, size, mtime) mọi input + độ dài; khác thì trộn lại. Bản trộn cũ chưa có json → luật mtime như trước rồi ghi json.
- **`restart_server.py`**: precheck thêm `fileio`, `clone_tts`, các engine ASR.

## Chưa làm trong đợt này

- X4: review đề xuất `POST /api/queue/replace`; đã làm `/api/queue/jobs/opts` (đổi opts tại chỗ — đủ cho `sync_pending_to_batch`). Các nơi ghi hàng đợi khác (feeder `_requeue_front`, `feed_tick`, `hg_auto_flow`) chưa chuyển.
- S5 (`_resolve_asr_engine` ghi lại `asr.json`), S12, S14 không thuộc đợt 4.

## Hiệu lực

- **Ngay** (server nạp lại mỗi lần mux): `render.py`, `assemble.py`. f9fe khi tới mux: chưa có `mixed_audio.json` → luật cũ; `dub_fit` ghép qua `.partial`.
- **Lần spawn subprocess kế tiếp**: `asr.py` + engine ASR, `manifest.py` trong subprocess.
- **Sau restart server**: `server.py`, `manifest.py`, `job_queue.py`, `clone_tts.py`, `translate.py`, `fileio.py`, `agent_core.py`. TTS f9fe đang chạy trong server cũ → `tts.json` của nó chưa có `key` (vẫn hợp lệ).
- **Sau restart sidecar**: `agent_tele_cmd.py`, `agent_autopilot.py`, `fileio.py`.

## Recheck

```powershell
cd Z:\PinelineV2
$env:PYTHONIOENCODING='utf-8'
python scripts\check_batch4.py        # 56 PASS
python scripts\check_batch3.py        # 35 PASS (chạy vài lần — kiểm file_lock)
python -m pytest -q -p no:cacheprovider
```

Sau restart: `Get-Content Z:\PinelineV2\.server_8801.lock` tồn tại; chạy `python server.py --port 8801` lần 2 phải in "Đã có server PinelineV2 khác giữ cổng 8801 — thoát."
