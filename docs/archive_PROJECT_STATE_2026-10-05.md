# PinelineV2 — trạng thái dự án (cập nhật 2026-10-05 01:35)

## Dịch vụ đang chạy

| Dịch vụ | Cổng | Ghi chú |
|---|---|---|
| Pineline server (`server.py`) | 8801 | Không restart khi đang có job chạy (hỏi trước). Render/subs/config/assemble/media_ts được hot reload mỗi lần mux. |
| Sidecar (`agent_autopilot` + `agent_tele_cmd`) | 8802 | Restart thoải mái. Auto-pilot: không tự bật lại nếu user đã tắt. |
| llama-server qwen36-turbo | 8083 | Do `E:\models\presets\ui-server.ps1` quản lý. Không kill khi chưa được phép. |
| YT uploader | — | Restart mất danh sách upload → hỏi nếu đang upload. Upload YouTube cần user cho phép. |

Secret (không chia sẻ, đã gitignore, không đưa vào backup): `client_secret.json`, `token.json`, cookies.

## Job

| Job | Trạng thái | Lệch mốc audio nguồn | Việc còn lại |
|---|---|---|---|
| 2ef87bb930b1 | đã dừng lúc 01:28:54 ngày 5/10 (đang ở bước dịch/review) | +7,99 s | Chạy tiếp; render sẽ tự chỉnh mốc. |
| 0281a4c6ad6e | done (output cũ bị lệch tiếng/sub) | +25,37 s | Render lại rồi cắt lại part cho YouTube (hỏi trước). |
| dccc6a183bb8 | done (output cũ lệch) | +11,11 s | Render lại (hỏi trước). |
| 6e1d4fa8075a | done (output cũ lệch) | −2,55 s | Render lại (hỏi trước). |
| 7bbffd9e731a | done (output cũ lệch) | +1,01 s | Render lại (hỏi trước). |
| 35bf01a1b5ff | done (output cũ lệch) | −0,74 s | Render lại (hỏi trước). |
| 12032ca75fab | done | −0,03 s (không lệch) | Output render trước khi bỏ lớp đen hardsub. |

Thư mục job: `Z:\PinelineV2\work\` và `D:\PinelineV2_work\`.

## Thay đổi gần đây (4–5/10/2026)

### Lệch tiếng/sub do file nguồn ghép nhiều tập
- Nguyên nhân: file mp4 ghép copy giữ lại 1024 mẫu AAC priming ở mỗi chỗ nối tập; decode thường cộng dồn tiếng dư (0281: +25 s qua 1097 chỗ nối) → ASR, TTS, sub, nhạc nền trễ dần so với hình.
- Sửa: mọi chỗ đọc tiếng gốc dùng `AUDIO_TS_FIX = aresample=async=1:min_hard_comp=0.01:first_pts=0` (`media_ts.py`, dùng trong `asr.py`, `separate.py`, `mux.py`, `render.py`).
- Job cũ: `media_ts.ensure_job_audio_ts()` chạy đầu `run_render`: chỉnh mốc asr/script/tts/srt theo bản đồ lệch, backup vào `_pre_audio_ts/`, trích lại `audio.wav`, ghép lại dub, đánh dấu `.audio_ts_fixed.json`.
- CLI kiểm tra: `python media_ts.py --check <video>`.
- `agent_av_sync.py` có kiểm tra `audio_ts_drift`.

### Ghép giọng khớp thời gian thích ứng (`assemble.py`)
- Tốc độ nền 1,12×, tăng dần tới 1,30× khi bị trễ (hệ số 0,6), được vào sớm tối đa 0,15 s; câu TTS phình hoặc khe ASR bị nén cho phép tới 1,6×.
- Đánh dấu `.fit_mode`; job ghép bằng code cũ sẽ tự ghép lại khi render.
- `ASSEMBLE_FIT_MODE=off` để tắt.

### Che hardsub
- Mặc định `HARDSUB_MODE=track`: dò tọa độ hardsub theo từng đoạn (`hardsub_track.json`) rồi chỉ blur đúng vùng đó, trước bước zoom. Không còn lớp đen.
- `HARDSUB_MODE=bar` mới dùng lại dải blur + lớp đen bo góc cũ (`HARDSUB_BAR_ALPHA`, `HARDSUB_BAR_RADIUS`).

### Render chia khúc (`render.py`)
- Chỉ áp dụng render 2 bước (đã có mixed_audio). Khúc ~`RENDER_CHUNK_SEC` giây (mặc định 300), tối đa `RENDER_CHUNK_PAR` khúc chạy cùng lúc (mặc định 3, tối đa 6). Khúc xong thì khúc kế tiếp chạy ngay.
- Mỗi khúc: `-copyts -ss <đầu> -i source … -to <cuối>` nên filter/sub thấy mốc tuyệt đối; điểm cắt nằm giữa 2 khung; tránh vùng mốc nén; `-enc_time_base demux`; audio AAC encode song song; ghép concat demuxer + inpoint/outpoint, `-c copy`.
- Lỗi một khúc → dừng các khúc khác, render lại 1 lượt. `RENDER_CHUNK_SEC=0` để tắt.
- Đã test (job 12032, phút 30–45, 3 khúc 5 phút): 26.987/26.987 khung, mốc lệch ≤ 0,85 ms, PSNR theo thứ tự khung thấp nhất 39,6 dB, sub đúng ở chỗ nối, nhanh hơn 1,82× (142 s so với 259 s). Test hàng đợi 8 khúc × 2 phút, 3 song song: chạy đúng, đủ khung.
- `RENDER_CHUNKS` cũ đã bỏ.

### Khác
- `server.py`/`job_queue.py`: không tự load queue/khởi worker khi chạy dưới pytest (chỉ có hiệu lực sau lần restart server tới).

## Script chẩn đoán/test
`D:\PinelineV2_tmp\`: `chunk5_test.py` (test chia khúc 5 phút), `pool_test.py` (test hàng đợi khúc), `ts_verify.py`, `scan_drift.py`, `stts_scan.py`, `fit_sim*.py`, `split_pkt.py`, `mp4_elst.py`, `snapshot.py` (tạo backup).

## Backup
`python D:\PinelineV2_tmp\snapshot.py` → `Z:\PinelineV2_backup_<ngày_giờ>.zip`: code + config + file text nhỏ của job (json/srt/txt/log ≤ 5 MB) + script test. Không gồm media (mp4/wav) và secret.
