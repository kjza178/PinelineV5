# Hiện trạng PinelineV4 (port từ V2)

_Cập nhật: 2026-11-20 ~22:15 — CJK backup-repair; 233da4 resume; chờ restart :8801_

## Dịch vụ

| Dịch vụ | Cổng | PID | Khởi động bằng | Ghi chú |
|---|---|---|---|---|
| Pineline V4 `server.py` / desktop | **8804** | — (không listening 21:43 5/11) | `run_v4.bat` / `server.py` | TEMP `D:\PinelineV4_tmp`. `llm.py` pool-first file upload. |
| Sidecar Auto-pilot + Telegram `agent_tele_cmd.py` | 8802 | (xem lock / netstat) | `run_tele_cmd.bat` cwd V2 | Nạp test-one `project_id` + keep-NMT unrelated. |
| Pineline V2 | **8801** | **30576** (restart ~19:24 14/11 `--clean-env`) | `restart_server.py --clean-env` | R1.1–R1.5 + seat-lock. Current `08ab_p02` (OCR/dịch); queue `e00_p01` → `e00_p02`. |
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

- **2026-11-20 Publish ask phần 1** — `/publish` + `ask_before_upload`. **Restart :8802 + :8801** (yes/no). Fix `docs/fixes/2026-11-20-publish-ask-telegram.md`.
- **2026-11-20 Prompt thumb đơn giản** — `meta_studio.build_master_image_prompt` ngắn (ref+title+typo nền). **Restart :8801** nếu muốn auto-publish in-process (yes/no). Fix `docs/fixes/2026-11-20-thumb-prompt-simple.md`.
- **2026-11-20 Queue Stop treo ghế `_gpu` pending** — code đã vá (`_queue_run_one` cancel future). Live: ghost `d386` đã clear; TTS `72450cea31aa_p01` (~15%+, queue trống). **Restart :8801** khi TTS xong / user yes. Fix `docs/fixes/2026-11-20-queue-stop-gpu-wait.md`.
- **2026-11-19 Xoá job/part sót work/** — ĐÃ restart :8802 + purge 19 orphan (~175 GB, 0 fail). Fix `docs/fixes/2026-11-19-films-delete-orphan-work.md`. Hard refresh Films UI.
- **2026-11-19 Films gộp job: log/tiến độ** — ĐÃ restart :8802. Hard refresh Films UI. Fix `docs/fixes/2026-11-19-films-combine-progress-log.md`.
- **2026-11-13 Parent đã ghép Full mà part chạy lại ASR** (agent S) — chờ restart :8801 (server chạy từ 13:38 UTC 12/11, chưa restart lần nào sau đó). 60892cc63cb7: Full 07:12 VN dùng được (mối nối giải mã OK); KHÔNG xếp lại parent/part; thư mục `_p01/_p02` đã biến khỏi D:\PinelineV2_work lúc ~01:24 UTC (không do agent S). Port V4/V5/V6 chưa. `docs/fixes/2026-11-13-parent-rerun-after-done.md`.
- **2026-11-13 Brain: job xong không heal + park ≠ HOLD** (agent N) — chờ restart :8801. Sau restart: 2493d3/ae9956/ec10e4 (và mọi job có output/đã đăng/part của parent đã ghép) không còn «🩹 heal thất bại»; park simple/B2 báo «⏸ … tự thử lại lúc HH:MM (lần k/max)» 1 lần, chỉ «⛔ HOLD … Cần bạn» khi review_failed/QA/hold tay. Dry-run: 11 job finished, 1 park (`60892cc63cb7_p01`), 0 HOLD. Port V4/V5/V6 chưa. `docs/fixes/2026-11-13-brain-finished-hold.md`.
- **2026-11-18 Auto-publish thumb poster-only + title hooks** — chỉ poster (không frame); chữ neo title; đã invalidate master series Nguyên Anh lệch. **Restart :8801** (yes/no). Đổi thumb YT `F5EfDJ5UAa0`? Fix `docs/fixes/2026-11-18-thumb-poster-only-title-hooks.md`.
- **2026-11-18 Meta thumb + Up ảnh gốc** — code đã vá (`routes_films`, nút Up ảnh gốc, `poster_b64`). Hard refresh Films UI → Done list qua fallback :8802. **Restart :8801 + :8802** để `/films` JSON native trên 8801 + nhận `poster_b64` (yes/no). Fix `docs/fixes/2026-11-18-meta-thumb-upload-ref.md`.
- **2026-11-13 Meta AI thumb trên :8801** — `routes_hg` đã thêm `/api/meta/ai-image`; hard refresh Films UI → fallback :8802 đã dùng được. **Restart :8801** để route native (yes/no). Fix `docs/fixes/2026-11-13-meta-ai-image-8801.md`.
- **2026-11-13 Câu ASR rác «None.» / part park kẹt** (agent M) — chờ restart :8801. Job `60892cc63cb7_p01` park «còn 1 câu chưa soát» (i=1039 zh «None.»): sau restart xếp lại / «Chạy tự động» parent `60892cc63cb7` (nếu đã rời hàng đợi) → p01 tự qua cổng (câu rác → «…», slot im lặng), p02 đã xong được bỏ qua, ghép Full tự động. Không sửa dữ liệu work. Mới: `SIMPLE_UNREVIEWED_TOLERANCE` (mặc định max(3, 0.2 %)), parent auto-split giữ ghế khi part park (`held_at=split_parts`). Port V4/V5/V6 chưa. `docs/fixes/2026-11-13-simple-junk-park.md`.
- **2026-11-13 Preflight + chuẩn hoá nguồn video** (agent K) — chờ restart :8801 (import/download/render). Job mới: kiểm sau download/import, AAC hỏng → `source_norm.*` trong work dir. Job cũ KHÔNG tự chạy: user chạy `python tools/preflight_scan.py --quick` (hoặc không `--quick`) để xem job nào nguồn lỗi, rồi `python source_preflight.py work/<job> --run` nếu muốn. Port V4/V5/V6 chưa. `docs/fixes/2026-11-12-video-preflight.md`.
- **2026-11-13 FireRed slice tại khoảng lặng** (agent L): có hiệu lực lần ASR kế tiếp. 10 job cũ nghi câu bị cắt ở biên 1200 s (`python tools/asr_boundary_scan.py D:/PinelineV2_work`): `2493d3c7cb29_p01..p04`, `2d3316593ea9`, `32da3d8f225b`, `365baf19df54`, `60892cc63cb7_p01/p02`, `9dedde16e35b` → cần user quyết chạy lại ASR (+dịch/TTS). Port V4/V5/V6 chưa. `docs/fixes/2026-11-13-firered-slice-silence.md`.
- **11-12 — Second Brain tin theo MẪU + gỡ HOLD khi chạy tay + hoãn heal 180 s (agent H) — chờ restart :8801:** tin Telegram do code dựng (vd «❌ Lớp học huyền thoại bị lộ P3 (2937ff) / ASR lỗi (firered mã 1) lúc 05:57. / Brain: … / Cần bạn: …»), không còn «Brain DECISION»/văn LLM; cùng lỗi nhắc ≤ 2 h. Chạy tay TTS/mux/dịch trên job HOLD → tự gỡ HOLD (`agent.hold_override`) + 1 tin; brain/auto không HOLD lại nếu QA không có high mới. Watcher/brain hoãn heal 180 s sau start, không heal job đang chạy; engine lỗi → `engine_fail_*.log` trong thư mục job. Port V4/V5/V6 chưa làm. Fix `docs/fixes/2026-11-12-brain-notify-v2.md`.
- **11-12 — Second Brain Telegram theo sự kiện + gỡ HOLD cũ (agent G) — chờ restart :8801:** sau restart chỉ còn tin khi stage bắt đầu/xong/lỗi, job xong, brain HOLD/CLEAR/heal (1 tin/tick); tick đầu sẽ gỡ HOLD cũ của `f0834acf0cc0` (job đã xong) + 1 tin «CLEAR HOLD». Muốn digest lại: `AGENT_BRAIN_TELEGRAM=report` (≥10'). Job `2937ffd7989f` ASR failed 4 s lúc restart 05:57 12/11 — nghi bị watcher heal kill lúc khởi động (video OK); user xếp lại queue khi GPU rảnh. HOLD không chặn nút chạy tay TTS/mux — cần user chọn cách xử lý. Fix `docs/fixes/2026-11-12-brain-telegram-hold.md`.
- **11-12 — translate-simple là MẶC ĐỊNH (agent F2, chờ restart :8801):** không đặt `TRANSLATE_PIPELINE` = luồng simple; rollback `TRANSLATE_PIPELINE=legacy` (env hoặc `pineline.config.json`, job mới; job đã đóng dấu giữ luồng của nó). Job dở luồng cũ (park/review) hoàn tất bằng luồng cũ (`manifest.translate_pipeline`). Trước restart: `Z:\PinelineV6\scripts\test_v2_translate_simple.bat` (kỳ vọng simple 88 pass). Fix `docs/fixes/2026-11-12-translate-simple-default.md`. Các mục «MẶC ĐỊNH TẮT» của translate-simple bên dưới đã cũ về điểm này.
- **11-12 — ASR mặc định trên giọng tách Demucs (agent E) — ĐÃ CÓ HIỆU LỰC cho ASR mới (không cần restart):** mọi job/part chạy Demucs 1 lần trước ASR (`vocals.wav` → `audio.wav` 16k), dùng lại cho render. Rollback: `"ASR_USE_DEMUCS": "0"` trong `pineline.config.json` + restart :8801. Demucs lỗi → tự fallback audio gốc (log `[asr] CẢNH BÁO: Demucs lỗi`). Cần làm khi V2 rảnh: `Z:\PinelineV6\scripts\asr_demucs_compare.bat run` (A/B FireRed gốc vs vocals, nghe clip) → `Z:\PinelineV6\docs\reviews\2026-11-12-asr-demucs-compare.md`; `asr_demucs_compare.bat golden` → CAM++ trên vocals. Port V4/V5/V6 chưa sửa. Fix `docs/fixes/2026-11-12-asr-demucs-default.md`.
- **11-12 — translate-simple trên đĩa (chờ restart :8801, MẶC ĐỊNH TẮT):** luồng dịch mới `translate_simple/` bật bằng `TRANSLATE_PIPELINE=simple` (env hoặc `pineline.config.json`). Trước restart: `Z:\PinelineV6\scripts\test_v2_translate_simple.bat`. Thử chất lượng khi V2 rảnh: `python Z:\PinelineV6\scripts\golden_ab.py --variants base,simple --yes` (GPU + GPT). Thiết kế `docs/design/2026-11-12-translate-simple.md`, fix `docs/fixes/2026-11-12-translate-simple.md`.
- **11-12 — translate-simple «next» trên đĩa (chờ restart :8801, MỌI cờ mới TẮT):** `SIMPLE_LEXICON_EXCLUDE_GOLDEN`, `SIMPLE_PAIR_RULES`, `SIMPLE_PAIR_FILL` (+`_MIN` 3), `SIMPLE_LEARN_INFERRED`, `SIMPLE_ZH_SOURCE` = 0; sửa gỡ lặp ASR (không cờ, chỉ luồng simple). Trước restart: `Z:\PinelineV6\scripts\test_v2_translate_simple.bat` (kỳ vọng 74 pass). A/B khi V2 rảnh: `Z:\PinelineV6\scripts\golden_ab_simple.bat next`. Thống kê: `python tools\simple_stats.py --work D:\PinelineV2_work`. Fix `docs/fixes/2026-11-12-translate-simple-next.md`.
- **11-12 — translate-simple đã REVIEW độc lập (sẵn sàng A/B, vẫn TẮT):** sửa 2 lỗi cao (bảng bộ không học tập mới; lexicon 我去 ép sai nghĩa) + 4 trung bình — `docs/reviews/2026-11-12-translate-simple-review.md`. Trước A/B: `Z:\PinelineV6\scripts\test_v2_translate_simple.bat` (kỳ vọng simple 45 pass). A/B khi V2 rảnh: `Z:\PinelineV6\scripts\golden_ab_simple.bat` (thử nhỏ 1 job) → `golden_ab_simple.bat full`. Cặp xưng hô thiếu: xem `<work>\plan_suggestions.json`.
- **11-12 — translate-b3 trên đĩa (chờ restart :8801, cờ mặc định TẮT = như cũ):** `PRONOUN_REGEX_MIXED` (1), `REVIEW_PRONOUN_MASK` (1) + `REVIEW_PRONOUN_PLAN_GUIDE` (1), `HALFCUE_MERGE` (0), `FILL_PENDING_PARK` (0). Trước restart: `Z:\PinelineV6\scripts\test_v2_translate_b3.bat`. Thử chất lượng: `Z:\PinelineV6\scripts\golden_ab.bat` (dry-run) → `golden_ab.bat run` khi V2 rảnh (GPU + GPT) → `docs\reviews\2026-11-12-golden-ab.md` ở V6. Fix `docs/fixes/2026-11-12-translate-b3.md`.
- **11-12 — Review translate-b2 xong: AN TOÀN restart :8801** (điều kiện: queue rảnh, KHÔNG bấm translate-fill trước restart, chạy `Z:\PinelineV6\scripts\test_v2_translate_b2.bat` → 0 fail). Đã sửa cửa chờ cloud trong `cloud_retry.py` (ngân sách chờ chung ≈577 s/đợt limit — trước đó chờ nhân theo số luồng). Còn mở: Aurora chết hẳn → câu NMT sót không vá local, job dừng «còn N câu VI trống» chờ bấm vá (`TRANSLATE_FILL_MODEL=local` để giữ gemma). Review `docs/reviews/2026-11-12-translate-b2-review.md`.
- **11-12 — Chờ restart :8801 nạp translate-b2** (retry cloud khi Aurora limit trước khi đổi local/park; NMT primary + REVIEW cloud → bước dịch không nạp gemma, câu sót vá bằng GPT; cổng sau dịch không gọi lại dịch local). File: `translate.py`, `cloud_retry.py` (mới), `llm.py`, `server.py`. Trước restart: `Z:\PinelineV6\scripts\test_v2_translate_b2.bat`. Quay lại hành vi cũ: `REVIEW_CLOUD_RETRY=0`, `TRANSLATE_FILL_MODEL=local`. Fix `docs/fixes/2026-11-11-translate-b2.md` (mục Recheck: log cần kiểm).
- **11-11 ~19:00 — Review translate-b1 xong: AN TOÀN restart :8801** (điều kiện: queue rảnh, KHÔNG bấm translate-fill trước restart — trạng thái trộn có thể làm REVIEW failed/ghi đè manual). Thêm sửa R1–R4 (`translate.py`, `pronoun_register_policy.py`) + `tests/test_translate_b1_scenarios.py`. Trước restart: `python -m pytest -q tests\test_translate_b1.py tests\test_translate_b1_scenarios.py` (130 pass). Review `docs/reviews/2026-11-11-translate-b1-review.md`.
- **11-11 ~18:25 — Chờ restart :8801 nạp translate-b1** (C1 lô REVIEW rỗng/cụt không rv · C2 giữ câu sửa tay · C3 «cậu» ngôi 3 · C9 fallback local 1 lần/lượt + 413 chia lô · T18 giữ trường ASR). File: `translate.py`, `pronoun_register_policy.py`, `agent_pronoun_pass.py`, `agent_name_pass.py`, `pronoun_consistency.py`, `preset_switcher.py`. Trước restart: chạy `python -m pytest -q tests\test_translate_b1.py` (+ test review/pronoun cũ). Chỉ `translate_fill` mới reload `translate.py` (trạng thái trộn) — restart mới chắc. Fix `docs/fixes/2026-11-11-translate-b1.md`.
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
- **Chờ restart :8801** — `PLAN_MODEL_BACKUP` + CJK/empty vá bằng Aurora sau DeepSeek (`2026-11-20-cjk-backup-repair`).
- **Chờ restart :8801 + :8802** — agent resolve short job id (`9aa089_p01`→full) + `script_peek` CJK; publish ask Telegram (`ask_before_upload`). Fix `2026-11-20-agent-resolve-short-job-id` + `2026-11-20-publish-ask-telegram`.
- **Chờ restart :8801** — DeepSeek thinking TẮT + DeepSeek rỗng (`LLMEmptyResponse`, cloud_retry không lặp, A7 ×2 max_tokens) + brain bỏ quét QA job chưa dịch.
- **Chờ restart :8802** (+ :8801) — chuẩn hóa Films UI: 📐 từng mùa + «Chuẩn hóa đã tick» (bỏ qua mùa đã chuẩn), chạy + log trong sidecar (`lib_normalize`).
- **Chờ restart :8801 + :8802** — HOLD QA hỏi qua Telegram (`agent_qa_ask`, `/api/agent/qa-answer`, `/qa-show`, nút/reply/`?`, `/qa <job>`, tool agent `pineline_qa_flags`). Chưa port V4/V5/V6.
- **Chờ restart :8801** — nạp FIRERED_ROOT mới + _check_stopped.

- **Chờ restart :8801** — nạp mix13 pronoun/review mask + UI review_backup.

- **Chờ restart :8801** — nạp MT_ZH_VI_DEVICE=cuda nếu process đã load NMT trên CPU (model <100MB, VRAM ~0).\n
