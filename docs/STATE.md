# Hiện trạng PinelineV4 (port từ V2)

_Cập nhật: 2026-11-11 ~00:10 — Studio SOP 1job + Aurora∥ (chờ restart :8801)_

## Dịch vụ

| Dịch vụ | Cổng | PID | Khởi động bằng | Ghi chú |
|---|---|---|---|---|
| Pineline V4 `server.py` / desktop | **8804** | — (không listening 21:43 5/11) | `run_v4.bat` / `server.py` | TEMP `D:\PinelineV4_tmp`. `llm.py` pool-first file upload. |
| Sidecar Auto-pilot + Telegram `agent_tele_cmd.py` | 8802 | (xem lock / netstat) | `run_tele_cmd.bat` cwd V2 | Nạp test-one `project_id` + keep-NMT unrelated. |
| Pineline V2 | **8801** | **4652** (restart ~00:36 10/11 `--clean-env`) | `restart_server.py --clean-env` | Brain C in-process. `05670` translate done + HOLD (TTS dừng lúc ~2.7%). Queue rỗng sau restart — cần xếp lại nếu còn job chờ. |
| Pineline V5 | **8805** | — (không listening 21:43 5/11) | `server.py --port 8805` | TEMP `D:\PinelineV5_tmp`. |
| Hongguo Downloader | 8000 | **20160** | app riêng | Cần UI token; API `/dl/*`. **Không kill.** |
| llama-server `qwen36-turbo` | 8083 | **22796** | `E:\models\presets\ui-server.ps1` | Type-C GPU; ~7 GB VRAM. **Không kill.** |
| 9router (LLM router) | 192.168.31.247:20128 | — | máy khác trong LAN | Model đang dùng: `ollama/gemma4:31b-cloud`. Combo `openclaw` hỏng. |
| YT uploader | — | — | `Z:\yt_uploader` (app desktop riêng) | Restart mất danh sách upload. Upload cần user cho phép. |

## Job

| Job | Phim | Trạng thái | Ghi chú |
|---|---|---|---|
| `60892cc63cb7_p01` | 造神… Phần 1/2 | translate=done, tts=pending, unrev=0 | Soát xong; **orphan TTS** vì queue đã nhảy `365baf`. Cần xếp lại + restart park. |
| `60892cc63cb7_p02` | 造神… Phần 2/2 | translate running / soát CLI | unrev còn; CLI ngoài queue. |
| `365baf19df54` | Tạo thần từ nhãn dán p2 | queue **current** translate | Nhảy vào vì ghế trống sau HOLD/soát p01. |
| `f9fe8deb4fa0` | 末世降临，我是末日生存方案供应商 (mùa 1, 9,6 h) | Done (13:58 ngày 6/10) | Tạo 6/10 từ file merged có sẵn, CONFIG BATCH. |
| `3a2e5a5f4337` | 末世降临…第二季 (mùa 2, 3,8 h) | Done | Gộp chuẩn hoá 1920x1080 lúc 04:37 (285 tập lẫn 1922x1080), đã xoá tập lẻ. |
| `05361da7c24c`, `77a8dd016e43` | (import local 14:35, 2,6 h mỗi job) | Done (77a8 đã upload 00:49 7/10, dính claim Content ID nhạc nền) | Tạo từ UI (`/api/jobs/local-path` + `/api/queue/group`), không phải feeder. |
| `2ef87bb930b1` | 每收一徒，我就增加炼气一万层第一季 (3,7 h) | Done (output 02:27 ngày 6/10) | Output dùng kiểu che **blur cũ**. 21/93 lô review lỗi (user chọn để nguyên). User **không** muốn render lại. |
| `0281a4c6ad6e` | (14,5 h) | Done + đã cắt `output_part1/2.mp4` cho YouTube | Output cũ lệch tiếng/sub (+25,37 s AAC priming). Render lại → hỏi trước. |
| `dccc6a183bb8`, `6e1d4fa8075a`, `7bbffd9e731a`, `35bf01a1b5ff` | — | Done (output cũ lệch tiếng) | Lệch +11,11 / −2,55 / +1,01 / −0,74 s. Render lại → hỏi trước. |
| `12032ca75fab` | — | Done | Output render trước khi bỏ lớp đen hardsub. |

Thư mục job: `D:\PinelineV2_work\` (`Z:\PinelineV2\work` là junction trỏ sang D). Database phim: `Z:\PinelineV2\data\films.db` (87 job, 74 bộ, 8 đã upload tính đến 6/10).

## Cấu hình mặc định đang dùng

- **LLM** (`pineline.config.json`): `CHATGPT_BASE_URL=http://127.0.0.1:3377/v1` (`sk-local`); `CHATGPT_TIMEOUT=900`; `PLAN_MODE=file` + `PLAN_MODEL=chatgpt/gpt-5-6-mini`; **Pronoun mix #1+#3** (PRONOUN_TITLE_POLICY/REVIEW_PRONOUN_MASK=1); UI review_backup default off; **NMT primary** `MT_ZH_VI=1` `ROLE=primary` `MODEL=auto`; **`REVIEW_MODEL=chatgpt/gpt-6`** (Aurora/:3377; `AURORA_REVIEW_MODEL` cùng); `TRANSLATE_PRESET` vẫn `gemma4-12b-qat-mtp-fast`; **`AGENT_BRAIN=1` `MODE=hybrid`** + **`BRAIN_HANG_FIX=1`** (`HANG_FIX_MODEL=chatgpt/gpt-5-6-mini`); standalone brain tới restart :8801; `NAME`/`PRONOUN` vẫn `chatgpt/gpt-5-6-mini`.
- **CONFIG BATCH** (`work/logs/batch_config.json`): voice v2, speed 1.1, TTS vieneu, ASR fun_asr_nano, audio **sfx_lib** (từ 07/10 02:52: giọng Việt + tiếng động gốc CDX23 + nhạc kho YouTube theo mức; trước đó duck voice 0.2 / gốc 0.28), dịch batch, OCR tắt, fit bật, resolution source, zoom 1.1, lật ngang, grain weak, LUT/motion tắt, 4M, brand corners "SageReview".
- **Che hardsub**: `HARDSUB_MODE=track`, `HARDSUB_STYLE=stretch`, không làm mềm (0/0), phủ hết ngang, đệm 15/13 px.
- **Render**: NVENC, chia khúc 300 s × 3 song song (chỉ khi render 2 bước).

## Code đã có hiệu lực (restart 03:22 ngày 7/10)

Server :8801 (PID 32156, restart 04:32 7/10 nạp hàng đợi gộp Hongguo lưu file + hiện tiến độ) và sidecar :8802 (PID 27392, restart 03:22), chạy code mới nhất: parser `tool(...)`, `hg_library`/`hg_merge`, đợt 1–7 (`fixes/2026-10-06-batch*.md`), M20 `voice_bgm` apad, chế độ audio `sfx_lib`, không còn `/ui1` `/ui2`. Kiểm nhanh: `GET :8801/api/agent/pending` trả `{"ok":true,...}`; có `Z:\PinelineV2\.server_8801.lock` và `.sidecar_8802.lock`.

Restart từng văng sau bước kill (13:58 6/10 và 01:27 7/10) vì `NoSuchProcess` trên `cmd.exe` bọc server (`fixes/2026-10-06-restart-killed-itself.md`). Đã sửa; lần chạy 01:33 7/10 qua trọn vẹn.

Restart chỉ khi hàng đợi rảnh, hoặc user đồng ý (yes/no).

Đợt 7 (`fixes/2026-10-06-batch7-ui-split.md`): `server.py` tách `routes_ui.py`/`routes_hg.py`/`routes_agent.py` — đã có hiệu lực.

## Việc còn treo / cần user quyết

- **11-11 ~03:05 — Chờ restart nạp fix B1–B10:** :8801 (V2), :8804 (V4), :8805 (V5 — lần đầu sau khi chuyển package). Chạy pytest trước (xem `docs/fixes/2026-11-11-*`). V2 đang chạy production → restart khi queue rảnh / user đồng ý.
- **Restart :8801 nạp queue-park + Studio SOP / Aurora∥ REVIEW** — process cũ chưa có. Restart cắt `365baf` nếu đang dịch → hỏi yes/no. Sau: xếp `60892_p01` đầu hàng TTS; không CLI review song song queue.
- **Job `9c3af49061a2` (video 5)** — VI hiện tại kém (audit); sandbox 6×90s NMT **149/194 improved, 0 worse** (docs/reviews/2026-11-09-job5-retranslate-compare.md). Remake full ASR+dịch+TTS+mux → hỏi yes/no. Caveat: SenseVoice/NMT còn lệch số.

- **Chờ restart :8801** — nạp `translate.py` mới: REVIEW duty E + filter giữ merge; `apply_asr_stutter_heal` trước LLM + post-pass; không cắt `叮当叮当`. Fix `docs/fixes/2026-11-09-review-asr-merge.md`.
- server :8801 — `firered_asr` BF16 default
- **Chờ restart :8801** — nạp `routes_hg` poster junk/missing → 404 (+ timeout ChatGPT 900 nếu chưa). Job `1e2379edb4fe_p01` đang running. Fix `docs/fixes/2026-11-09-hg-poster-502-junk-name.md`. Hard refresh Films UI cho `resolveFilmPosterName`.
- server :8801 — `firered_asr` BF16 default
- ~~**Chờ restart :8801**~~ — đã restart ~05:16 9/11 (`--clean-env`). Nạp keep-NMT + NMT primary + PLAN file + hv_auditor. Fix `docs/fixes/2026-11-09-review-keep-nmt.md`.
- server :8801 — `firered_asr` BF16 default
- ~~Chờ restart :8801 (split parent merge heal)~~ — đã restart ~19:21. Fix `docs/fixes/2026-11-08-split-parent-merge-heal.md`.
- server :8801 — `firered_asr` BF16 default
- ~~Chờ restart :8801 (hardsub_blur)~~ — xem CHANGELOG 07/11; OpenAPI/live tùy lần restart gần nhất.
- server :8801 — `firered_asr` BF16 default
- ~~Chờ restart :8802~~ — đã restart ~01:40 (PID 28936). Fix skip-ux + combine preserve_order.
- server :8801 — `firered_asr` BF16 default
- ~~Chờ restart :8801 (hongguo2)~~ — đã restart 15:13 6/11; `/hongguo2` 200 + body Hongguo2.
- server :8801 — `firered_asr` BF16 default
- **Hard refresh `/hongguo` + `/hongguo2`** — seasons board + trang Hongguo2 (HTML static) nếu browser còn cache cũ.
- ~~Restart :8804~~ — đã lên 01:16 3/11 (cùng :8801/:8805); Aurora pool-file + pronoun/review lock đã trong process.
- API `/films/*` + `/meta/*` song song :8804 ↔ :8802 (Telegram) — giữ trừ khi gộp process.
- RUNBOOK/ARCHITECTURE đã viết lại cho V4 (2026-11-02). Đoạn job/history dưới đây vẫn mang số liệu V2 cũ (tham khảo).
- Attic: `scripts/archive/{launchers_legacy,tauri_desktop,ui_legacy,scratch_oneshot,docs_stale}/`.
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

## Việc treo
- **Chờ restart :8801** — nạp FIRERED_ROOT mới + _check_stopped.

- **Chờ restart :8801** — nạp mix13 pronoun/review mask + UI review_backup.

- **Chờ restart :8801** — nạp MT_ZH_VI_DEVICE=cuda nếu process đã load NMT trên CPU (model <100MB, VRAM ~0).\n
