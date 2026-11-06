# Hiện trạng PinelineV5 (dual-tree ops)

V5 là workspace chính của file này; bảng dưới vẫn liệt kê V2/V4/V5 vì sidecar và production còn dual-tree.

_Cập nhật: 2026-11-06 ~15:45 — SAFE autofix ENOSPC/PORT/uploader defaults trên disk; **không restart** :8805 (chờ user)_

## Dịch vụ

| Dịch vụ | Cổng | PID | Khởi động bằng | Ghi chú |
|---|---|---|---|---|
| Pineline V4 `server.py` / desktop | **8804** | **39588** (01:16 3/11) | `run_v4.bat` / `server.py` | TEMP `D:\PinelineV4_tmp`. `llm.py` pool-first file upload. |
| Sidecar Auto-pilot + Telegram `agent_tele_cmd.py` | 8802 | **41560** (19:25 4/11) | kill+start `agent_tele_cmd` (BASE :8801) | Ghost lock đã gỡ; đang publish `5223`. |
| Pineline V2 | **8801** | **15120** (01:16 3/11) | `restart_server.py --clean-env` | Queue rỗng sau restart. |
| Pineline V5 | **8805** | **21320** (00:09 5/11) | `PORT=8805 restart_server.py --ignore-hg --clean-env` | TEMP `D:\PinelineV5_tmp`. Đã nạp `core.*` (restart sau package move). |
| Hongguo Downloader | 8000 | — | app riêng | Cần UI token; API `/dl/*`. |
| llama-server `qwen36-turbo` | 8083 | 35080 | `E:\models\presets\ui-server.ps1` | Giữ ~7,7 GB VRAM. **Không kill khi chưa được phép.** |
| 9router (LLM router) | 192.168.31.247:20128 | — | máy khác trong LAN | Model đang dùng: `ollama/gemma4:31b-cloud`. Combo `openclaw` hỏng. |
| YT uploader | — | — | `Z:\yt_uploader` (app desktop riêng) | Restart mất danh sách upload. Upload cần user cho phép. |

## Job

| Job | Phim | Trạng thái | Ghi chú |
|---|---|---|---|
| `f9fe8deb4fa0` | 末世降临，我是末日生存方案供应商 (mùa 1, 9,6 h) | Done (13:58 ngày 6/10) | Tạo 6/10 từ file merged có sẵn, CONFIG BATCH. |
| `3a2e5a5f4337` | 末世降临…第二季 (mùa 2, 3,8 h) | Done | Gộp chuẩn hoá 1920x1080 lúc 04:37 (285 tập lẫn 1922x1080), đã xoá tập lẻ. |
| `05361da7c24c`, `77a8dd016e43` | (import local 14:35, 2,6 h mỗi job) | Done (77a8 đã upload 00:49 7/10, dính claim Content ID nhạc nền) | Tạo từ UI (`/api/jobs/local-path` + `/api/queue/group`), không phải feeder. |
| `2ef87bb930b1` | 每收一徒，我就增加炼气一万层第一季 (3,7 h) | Done (output 02:27 ngày 6/10) | Output dùng kiểu che **blur cũ**. 21/93 lô review lỗi (user chọn để nguyên). User **không** muốn render lại. |
| `0281a4c6ad6e` | (14,5 h) | Done + đã cắt `output_part1/2.mp4` cho YouTube | Output cũ lệch tiếng/sub (+25,37 s AAC priming). Render lại → hỏi trước. |
| `dccc6a183bb8`, `6e1d4fa8075a`, `7bbffd9e731a`, `35bf01a1b5ff` | — | Done (output cũ lệch tiếng) | Lệch +11,11 / −2,55 / +1,01 / −0,74 s. Render lại → hỏi trước. |
| `12032ca75fab` | — | Done | Output render trước khi bỏ lớp đen hardsub. |

Thư mục job: `D:\PinelineV2_work\` (`Z:\PinelineV2\work` là junction trỏ sang D). Database phim: `Z:\PinelineV2\data\films.db` (87 job, 74 bộ, 8 đã upload tính đến 6/10).

## Cấu hình mặc định đang dùng

- **LLM** (`pineline.config.json`): `TRANSLATE_MODEL=local` (:8083); `NAME`/`PRONOUN=chatgpt/gpt-5-6-mini` (Aurora); `REVIEW_MODEL=ollama/gemma4:31b-cloud` qua 9router (`CLOUD_LLM_*`). Agent: `LLM_MODEL` / `AGENT_*`.
- **CONFIG BATCH** (`work/logs/batch_config.json`): voice v2, speed 1.1, TTS vieneu, ASR fun_asr_nano, audio **sfx_lib** (từ 07/10 02:52: giọng Việt + tiếng động gốc CDX23 + nhạc kho YouTube theo mức; trước đó duck voice 0.2 / gốc 0.28), dịch batch, OCR tắt, fit bật, resolution source, zoom 1.1, lật ngang, grain weak, LUT/motion tắt, 4M, brand corners "SageReview".
- **Che hardsub**: `HARDSUB_MODE=track`, `HARDSUB_STYLE=stretch`, không làm mềm (0/0), phủ hết ngang, đệm 15/13 px.
- **Render**: NVENC, chia khúc 300 s × 3 song song (chỉ khi render 2 bước).

## Code đã có hiệu lực (restart 03:22 ngày 7/10)

Server :8801 (PID 32156, restart 04:32 7/10 nạp hàng đợi gộp Hongguo lưu file + hiện tiến độ) và sidecar :8802 (PID 27392, restart 03:22), chạy code mới nhất: parser `tool(...)`, `hg_library`/`hg_merge`, đợt 1–7 (`fixes/2026-10-06-batch*.md`), M20 `voice_bgm` apad, chế độ audio `sfx_lib`, không còn `/ui1` `/ui2`. Kiểm nhanh: `GET :8801/api/agent/pending` trả `{"ok":true,...}`; có `Z:\PinelineV2\.server_8801.lock` và `.sidecar_8802.lock`.

Restart từng văng sau bước kill (13:58 6/10 và 01:27 7/10) vì `NoSuchProcess` trên `cmd.exe` bọc server (`fixes/2026-10-06-restart-killed-itself.md`). Đã sửa; lần chạy 01:33 7/10 qua trọn vẹn.

Restart chỉ khi hàng đợi rảnh, hoặc user đồng ý (yes/no).

Đợt 7 (`fixes/2026-10-06-batch7-ui-split.md`): `server.py` tách `routes_ui.py`/`routes_hg.py`/`routes_agent.py` — đã có hiệu lực.

## Việc còn treo / cần user quyết

- **Chờ hard refresh `/hongguo` + `/hongguo2`** — seasons board + trang Hongguo2 (HTML static).
- **Chờ restart :8805** — nạp ENOSPC split guard + `_AUTO_SPLIT_ACTIVE` + PORT/uploader defaults; thêm `_plan_block_for_qa` + llm no-retry 413 + route `ui_hongguo2` / seasons / merge no-dup. Hỏi yes/no xoá part `*_p0N/output.mp4` (~23 GB trên d01).
- ~~Chờ restart :8805 (`core/` package)~~ — restart 00:09 PID 38920→21320; smoke `/` `/films/ui` `/api/queue/jobs` `/api/voices` `/api/cookies` 200.
- Unity 23:55: docs + xoá TARGET shells; đã xong (superseded bởi `core/` 11-05).
- ~~Chờ restart :8805 (Phase F — `tools.*`)~~ — restart 23:49 PID 27296→38920; smoke `/` `/films/ui` `/api/queue/jobs` `/api/voices` 200.
- ~~Chờ restart :8805 (Phase E — xoá shim / rewrite import)~~ — restart 22:33 PID 21536→27296; smoke `/` `/films/ui` `/api/voices` `/api/cookies` `/api/queue/jobs` + OpenAPI 177 OK.
- ~~Chờ restart :8805 (layout A–D + assets/fs)~~ — restart 21:11 PID 41048→21536; smoke `/` `/films/ui` `/api/voices` `/api/cookies` `/api/queue/jobs` + OpenAPI `/api/jobs`+`/api/queue/jobs` OK.

- Launcher thật: `apps/run_v5.bat` / `apps/run_tele_cmd.bat`; root chỉ stub `call apps\…`.
- ~~Chờ restart :8805 (queue/jobs SSOT)~~ — đã restart 19:18; smoke `/api/queue/jobs` + OpenAPI OK.
- ~~Ghost auto-publish lock~~ — restart :8802 19:25; lock mới cho `5223c2a43053`.
- ~~`ce42` force trong auto-publish queue~~ — đã dequeue 19:32 (đã có YT).

- ~~Restart :8804~~ — đã lên 01:16 3/11 (cùng :8801/:8805); Aurora pool-file + pronoun/review lock đã trong process.

- API `/films/*` + `/meta/*` song song :8804 ↔ :8802 (Telegram) — giữ trừ khi gộp process.
- RUNBOOK/ARCHITECTURE đã viết lại cho V4 (2026-11-02). Đoạn job/history dưới đây vẫn mang số liệu V2 cũ (tham khảo).
- Attic: `scripts/archive/{launchers_legacy,tauri_desktop,ui_legacy,scratch_oneshot,docs_stale}/` — **Tauri live** lại ở root (`run_tauri.bat`); archive chỉ đối chiếu.
- Render lại các job có output lệch tiếng (0281, dccc, 6e1d, 7bbf, 35bf) và 2ef87 (kiểu che mới) — user chưa yêu cầu.
- Nhạc nền gốc gây claim Content ID — **đã chuyển CONFIG BATCH sang `sfx_lib`** (07/10 02:52, user duyệt). Chưa render job thật nào bằng `sfx_lib`; job đã render trước vẫn còn nhạc gốc (render lại khi user yêu cầu). `duck_bgm` còn rủi ro hụt đuôi giống lỗi `sfx_lib` đã sửa (chưa dùng). Hướng đã chọn: giọng Việt + SFX gốc (CDX23) + nhạc YouTube Audio Library theo mức êm/vừa/dồn dập; kho 45 bài ở `assets/bgm_yt/`; chế độ `sfx_lib` đã có trong code/UI (07/10 02:36), mẫu `E_sfx_lib.mp4`/`E2_sfx_lib_chinh.mp4`. Đã có 4 mẫu nghe so sánh ở `D:\PinelineV2_tmp\audio_samples\77a8dd016e43\` (worklog 07/10 01:47).
- 2 job cũ giữ bản sao video nguồn riêng: 0281 (23,7 GiB) và dccc (13,0 GiB) trùng file `(merged)` trong `D:\Lib` — user quyết **giữ nguyên job cũ**, đọc thẳng `D:\Lib` chỉ áp dụng cho job mới (`fixes/2026-10-07-source-duplicate-copy.md`). 5 job hard link (05361, 2ef87, 3a2e, 77a8, f9fe) không tốn thêm ổ.
- Combo `openclaw` trên 9router hỏng; vẫn để làm fallback trong `run_tele_cmd.bat`/`run_v2.bat`.
- VRAM gần đầy (11,6/12 GB) do llama-server giữ model trong lúc job ASR/TTS chạy — đã hỏi tắt llama-server, user chưa trả lời.
- Review code toàn bộ: xem `docs/reviews/2026-10-06-code-review.md`. Đợt 1–7 đã sửa xong; M17–M23 (addendum 07/10) chưa sửa.
- Key 9router từng nằm trong zip backup cũ (05/10 01:33, 06/10 08:34, 09:08) và lịch sử chat — nên đổi key; zip cũ chưa sửa.
- Tập lẻ Hongguo sau khi gộp nằm ở `D:\Lib_trash\<bộ>\<thời điểm>\`, tự xoá sau 7 ngày (đã có hiệu lực).

## Repo / test

- Git local tại `Z:\PinelineV2` (đợt 6; không remote). `pineline.config.json`, `work/`, `data/`, voices, lock, log không vào git. Trước khi commit chạy `D:\PinelineV2_tmp\git_b6_real.py` (phải ra "tổng file lộ: 0").
- `python -m pytest -q` = toàn bộ test, gồm `check_batch1–5` (~30 s); bỏ các bộ đó bằng `-m "not batches"`.
- Script một lần đã dọn: `Z:\PinelineV2_codebak\2026-10-06_batch6\attic\`.

## Ràng buộc vận hành (user đặt)

- Không restart :8801 khi đang có job nếu chưa hỏi yes/no. Sidecar :8802 restart thoải mái nhưng chỉ chạy 1 bản.
- Không dừng job đang chạy, không kill llama-server, không tắt Auto-pilot thay user nếu chưa được phép.
- Upload YouTube cần cho phép. Restart YT uploader khi đang upload → hỏi.
- Secret (`client_secret.json`, `token.json`, cookies, API key) không chia sẻ, không đưa vào backup/markdown. Không gắn tài khoản Google với IP proxy khi chưa đồng ý.
- Trả lời đúng câu hỏi; không tự render khi user chỉ hỏi nguyên nhân.
