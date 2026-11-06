# Restart hẹn giờ chết giữa chừng, server :8801 nằm chết

- **Ngày:** 2026-10-06
- **Phát hiện:** 14:31 (khi user nhắn tiếp)
- **Mức:** cao. Server không chạy khoảng 35 phút, hàng đợi trống.
- **Cập nhật 07/10 01:27:** lặp lại lần 2 → root cause thật khác với kết luận ban đầu (xem dưới).

## Triệu chứng

- `restart_server.py` (PID 20484, chạy từ 09:34) ghi `[13:58:41] job f9fe8deb4fa0 xong` rồi không ghi gì nữa.
- Server cũ PID 57336 đã bị kill: `server8801.log` dừng lúc 13:58:57, cổng 8801 không có ai nghe.
- Server mới không được start (không có dòng log nào). Sidecar 8802 vẫn chạy code cũ. Job 3a2e chưa được xếp lại.
- Không có log `KHÔNG restart` → precheck đã qua; tiến trình chết ở bước kill server.

## Root cause (đúng, xác nhận 07/10)

`restart_server.py` tìm server bằng `migrate_work.procs("server.py --host 127.0.0.1 --port 8801")`, so khớp chuỗi trong cmdline. `start_8801.py` chạy server qua `cmd.exe /c "title Pineline V2 :8801 && python -u server.py --host 127.0.0.1 --port 8801 ... >> log"`, nên `procs()` trả **hai** tiến trình: python và `cmd.exe` bọc nó. Kill python xong thì cmd tự thoát. Vòng lặp gọi tiếp `kill_with_parent_cmd(cmd)` → `p.children()` trên tiến trình đã chết → `psutil.NoSuchProcess` → `restart_server.py` văng exception sau dòng `kill server PID …`, trước khi start server mới.

Lần 07/10 01:27 (queue rảnh, chạy `restart_server.py --clean-env --sidecar` để kích hoạt đợt 7) có log từng bước và traceback nhờ bản sửa 6/10, nên thấy rõ: kill 2 PID (python + cmd) rồi `NoSuchProcess`. Lần 13:58 ngày 6/10 cũng là lỗi này (chưa có log/try nên chết im lặng).

Sửa: `kill_with_parent_cmd` bọc mọi lời gọi psutil (`parent()`, `children()`, `kill()`, `name()`/`cmdline()` của cha) trong `try/except psutil.Error` — tiến trình đã chết thì bỏ qua. Test: `test_kill_dead_process_is_noop`, `test_kill_wrapper_after_child` (dựng `cmd.exe /c python …` giống start_8801, kill python trước rồi cmd); cả hai đỏ với bản 6/10, xanh với bản mới.

## Giả thuyết ban đầu 6/10 (không phải nguyên nhân chính)

`migrate_work.kill_with_parent_cmd(p)` kill toàn bộ `p.children(recursive=True)`. Trong psutil 7.2.2, cách duyệt đệ quy chỉ so `create_time` của từng tiến trình với **gốc** (server), không so với cha trực tiếp. Trên Windows PID được tái dùng nhanh. Nếu tiến trình cha đã chết của restart_server có PID trùng với một worker của server (TTS/ASR/ffmpeg, sinh sau đó), thì restart_server (tạo lúc 09:34, sau server) bị tính là "cháu" của server và bị kill cùng server. Đó là lý do nó chết đúng ở bước kill, trước khi kịp start server mới.

Đã kiểm chứng: chạy `kill_with_parent_cmd` từ một tiến trình nằm trong cây con của tiến trình bị kill. Với bản cũ, tiến trình gọi bị kill (`D:\PinelineV2_tmp\check_old_kill.py` → `BỊ KILL`); với bản mới thì sống. Không còn dữ liệu để xác định chính xác PID nào bị trùng (cả hai tiến trình đã chết), lúc đó tưởng chỉ có nhánh này giải thích được việc chết im lặng — sai, nhánh `NoSuchProcess` ở trên cũng giải thích được và đã được log lần 2 xác nhận. Phần chặn tự kill vẫn giữ vì rủi ro PID tái dùng là có thật.

Thêm một lỗi phụ: sau `job xong`, restart không ghi log bước nào, kể cả nhánh "server không lên", và không có `try/except` ở `main`. Vì vậy chết giữa chừng không để lại dấu vết.

## Sửa

- `migrate_work.kill_with_parent_cmd`: không kill chính mình hoặc tổ tiên của mình.
- (07/10) `migrate_work.kill_with_parent_cmd`: bỏ qua tiến trình đã chết (`psutil.Error`) — sửa root cause thật.
- `restart_server.py`: ghi log `precheck ok`, `kill server PID …`, `đã gọi start server`, `server lên` / `server không lên`. `main` có `try/except` ghi traceback vào log và báo Telegram, kèm đường dẫn `restart_pending.json`.
- `D:\PinelineV2_tmp\snapshot.py` (công cụ, ngoài repo): bỏ qua file đang bị khoá (`.server_8801.lock`, `.sidecar_8802.lock`) thay vì dừng giữa chừng và để lại zip hỏng. Đã xoá 2 zip hỏng 1434/1435 (908 byte).

Backup bản gốc: `Z:\PinelineV2_codebak\2026-10-06_restartfix\` (`restart_server.py`, `migrate_work.py`, `snapshot.py`). Zip `Z:\PinelineV2_backup_2026-10-06_1435.zip`.
Lần 2 (07/10): `Z:\PinelineV2_codebak\2026-10-07_restartfix2\` (code), `2026-10-07_restartfix3\` (docs, test bản HEAD), zip 0135.

## Khôi phục tay (14:35–14:40)

1. Start server: `AGENT_QA_GATE=1`, `AGENT_WATCH=0`, `python D:\PinelineV2_tmp\start_8801.py` → PID 25032. `/api/agent/pending` có (code đợt 5), `.server_8801.lock` có.
2. Restart sidecar (kill 10836) → PID 13400, một bản, `/status` lên.
3. Xếp lại 3a2e với opts trong `work/logs/restart_pending.json` (`D:\PinelineV2_tmp\requeue_pending.py`) → 3a2e chạy ngay. Auto-pilot vẫn tắt như trước.

## Khôi phục tay lần 2 (07/10 01:27)

Start server bằng `start_8801.py` → PID 57476 (code đợt 7). Sidecar 13400 không bị đụng. Queue trống, Auto-pilot tắt.

Sau khi sửa: chạy lại `restart_server.py --clean-env --sidecar` lúc 01:33 → kill 57476 + cmd 58532, server lên 01:34 (PID 59488), sidecar một bản (PID 57748), exit 0. `/ui1` 404, `/ui3` 200, `/api/agent/pending` 200, Auto-pilot vẫn tắt.

## Recheck

```powershell
cd Z:\PinelineV2; python -m pytest tests/test_restart_guard.py -q   # 3 passed
python D:\PinelineV2_tmp\check_old_kill.py                          # bản cũ: BỊ KILL
```
