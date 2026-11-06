# V5 function catalog — definitive per-function map

- **Date:** 2026-11-06
- **Root:** `Z:\PinelineV5`
- **Nguồn:** merge AST partials `_atoms_*.md` + spine đọc live code
- **Scope:** module-level defs + class methods (nested skipped); UI = unique JS names (cap 200/`index3.html`)

## Stats

| Bucket | Functions |
|---|---:|
| core/ + `server.py` | 279 |
| `engines/**` | 538 |
| http_routes + agents + pineline.server.routes | 567 |
| tools + desktop/restart + static UI JS | 734 |
| **TOTAL** | **2118** |

Sum check: 279+538+567+734 = **2118**.

## Mục lục

1. [Spine gọi từng hàm](#1-spine-gọi-từng-hàm)
2. [core/ + server.py — per-function](#2-coreserverpy--per-function)
3. [engines — per-function](#3-engines--per-function)
4. [http_routes / agents / pineline.server.routes](#4-httproutes--agents--pinelineserverroutes)
5. [tools / desktop / UI JS](#5-tools--desktop--ui-js)
6. [How to navigate](#6-how-to-navigate--muốn-hiểu-x-thì-mở-y)

---

## 1. Spine gọi từng hàm

Happy path **queue** (UI/API xếp hàng → worker → mux → artifacts). Không đi nhánh HOLD/QA-block (ghi chú nhánh phụ). Nguồn: AST/read `server.py`, `core/job_queue.py`, `engines/{download,asr,translate,clone_tts,assemble,mux,render,split_parts,separate,ocr}.py`.

Ghi chú: `_auto_pipeline` là đường **1-click / run-all** (submit GPU sau download). **Queue happy path** gọi thẳng `_auto_gpu` từ `_queue_run_one` (không qua `_auto_pipeline`).

### 1.0 CALL ORDER (tóm tắt)

```
create_job → expand_meta → _create
  → api_queue_jobs_add → batch_config.resolve_job_opts → job_queue.queue_add
  → _ensure_worker_unlocked → _worker_loop → _runner=_queue_run_one
  → _heal_stale_running → is_wired_done? → resolve_job_opts → stamp queue_opts
  → _resolve_queue_voice → _claim_stage(__all__) → _find_video?
       → download_video (nếu thiếu) → source.* + manifest.download
  → maybe_auto_split? (nếu dài → queue_add parts + return "split")
  → _gpu.submit(_auto_gpu)
       → free_gpu_vram → _resolve_asr_engine → _run_engine(ASR script)
            → (subprocess) run_asr_* → asr.json + audio.wav + sub.zh.srt
       → _run_translate_engine → (subprocess) run_translate → script.json + glossary.json + sub.vi.srt
       → count_script_missing → (fill) _run_translate_engine(batch=25)
       → [HOLD?] return | [_run_requested_review?] | [run_qa_gate?]
       → _save_series_glossary → _resolve_voice/speed/tts_engine
       → _do_tts → run_clone_tts → tts/seg_*.wav + tts.json
       → [demucs?] run_separate → no_vocals.wav
       → [ocr?] run_ocr → ocr.json
       → _do_render → assemble(_fit) → run_render → output.mp4
  → try_auto_merge_parent? → auto_publisher.publish_job?
  → return "done"
```

### 1.1 Tạo job

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 1 | `server.py:1997` | `create_job(job: NewJob)` | `expand_meta(url, cookies…)` → loop `_create(url, target, cookies, group?)` | — (delegate) |
| 2 | `engines/playlist.py:53` | `expand_meta(url, …)` | yt-dlp playlist probe | — (meta in-memory) |
| 3 | `engines/download.py:252` | `job_id_from_url(url)` (via `_create`) | hashlib | — |
| 4 | `server.py:1882` | `_create(url, target, cookies_from_browser, group=None)` | `Manifest.save()` | `work/<job_id>/` mkdir; **`manifest.json`** (`request.url/target/cookies/group_*`) |

Local import (song song, không URL): `_create_local_shell` → `_place_source` → `_finalize_imported_source` → `source.*` + `meta.json` + `stages.download=done`.

### 1.2 Xếp hàng

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 5 | `server.py:2201` | `api_queue_jobs_add(req: JobQueueReq)` | `batch_config.resolve_job_opts(…)` → `job_queue.queue_add(ids, opts, skip_done)` | — |
| 6 | `core/batch_config.py:141` | `resolve_job_opts(opts, …)` | `load()` + merge layers | — (in-memory opts) |
| 7 | `core/job_queue.py:350` | `queue_add(job_ids, opts, skip_done=True, sort_first=True)` | `is_wired_done(wd)`; `job_sort_key`; `_save()`; `_ensure_worker_unlocked()` | **`work/.job_queue.json`** (`queue`, `opts`, `opts_by_job`, `current`) |
| 8 | `core/job_queue.py:154` | `is_wired_done(work_dir)` | read manifest + `output.mp4` size; stages in `WIRED` all `done` | — |
| 9 | `core/job_queue.py:171` | `_save()` | atomic json | **`work/.job_queue.json`** |
| 10 | `core/job_queue.py:572` | `_ensure_worker_unlocked()` | `Thread(target=_worker_loop)` | — |

Wire tại import: `server.py:5784` `job_queue.set_runner(_queue_run_one)`.

### 1.3 Worker → runner

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 11 | `core/job_queue.py:588` | `_worker_loop()` | pop `_q`; `_clear_stop_hook?`; `_save()`; `_runner(job_id, opts)` → `_hist_push` | **`.job_queue.json`** (current); history RAM |
| 12 | `core/job_queue.py:216` | `_hist_push(job_id, status, detail)` | ring buffer | — |

### 1.4 `_queue_run_one` (orchestrator)

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 13 | `server.py:3737` | `_queue_run_one(job_id, opts)` | (bảng dưới) | nhiều (qua helpers) |
| 14 | `server.py:309` | `_heal_stale_running(work_dir)` | kill orphan engines; reset `stages.*.status=running→pending` | **`manifest.json`** |
| 15 | `core/batch_config.py:141` | `resolve_job_opts(opts, fill_voice=False)` | — | — |
| 16 | `server.py:2839/2844/2848` | `_save_tts_voice/_speed/_engine(work_dir, …)` | Manifest stage tts / sidecar | **`manifest.json`**; often **`tts_config.json`** |
| 17 | `server.py:3098` | `_resolve_asr_engine(work_dir, asr_engine)` | `_save_asr_engine` | **`manifest.json` stages.asr** |
| 18 | `server.py:3033` | `_save_asr_engine(work_dir, engine)` | `_promote_asr_source?` / `_patch_asr_fields` | **`manifest.json`**; maybe promote **`asr.json`** |
| 19 | `core/manifest.py` | `Manifest.save()` / stamp `queue_opts` | — | **`manifest.json`** (`queue_opts` full snapshot) |
| 20 | `server.py:2931` | `_resolve_queue_voice(work_dir, voice)` | list clone voices | — |
| 21 | `server.py:162` | `_job_any_busy(job_id)` | `_STAGE_BUSY` set | — |
| 22 | `server.py:217` | `_manifest_running(work_dir)` | scan stages status | — |
| 23 | `server.py:171` | `_claim_stage(job_id, "__all__")` | `_STAGE_BUSY` | — (RAM) |
| 24 | `server.py:380` | `_next_incomplete_stage(work_dir)` | — | — |
| 25 | Manifest | `mark_running(early)` | — | **`manifest.json`** |
| 26 | `server.py:4906` | `_find_video(work_dir)` | manifest `video_path` / glob `source.*` | — |

### 1.5 Download (nếu chưa có video)

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 27 | `engines/download.py:305` | `download_video(url, work_dir, cookies_from_browser=…)` | `normalize_url`, `detect_platform`, `find_cookie_file`, `apply_speed_opts`, `_probe_duration`, `_auto_height_for_duration`, yt-dlp(+aria2c), Manifest mark | **`source.%(ext)s`**, **`source.info.json`**, thumbnail; **`manifest.json` stages.download=done** (`video_path`, title…) |
| 28 | helpers | `_format_sel`, `_cfg_max_height`, `_cfg_prefer_hevc`, `_clean_incomplete_fragments`, `_delete_sources` (fresh) | — | mảnh `.part` / clean |

### 1.6 Auto-split (optional, phim dài)

Happy path **không split** nếu `< auto_split_min_h`. Nếu split:

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 29 | `server.py:80` | `_maybe_auto_split_guarded(job_id, …)` | `maybe_auto_split_job` | lock RAM |
| 30 | `engines/split_parts.py:688` | `maybe_auto_split_job(…)` | `probe_duration` → `split_job_to_subjobs` | parent **`manifest.split_info`** |
| 31 | `engines/split_parts.py:412` | `split_job_to_subjobs(job_id, …)` | `compute_smart_plan` → `split_video_to_parts` → create sub jobs | **`work/<parent>_pNN/`** + part videos; parent/sub **`manifest.json`** |
| 32 | `core/job_queue.py:350` | `queue_add(sub_ids, opts, …)` | (as above) | **`.job_queue.json`** |
| — | `_queue_run_one` | return `"split"` | parent stages → pending “Chờ N part…” | **`manifest.json`** |

### 1.7 Submit GPU → `_auto_gpu`

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 33 | `_gpu.submit(_gpu_job)` | thread pool | `_auto_gpu(…)` then `_release_stage` | — |
| 34 | `server.py:1413` | `_auto_gpu(job_id, target, audio_mode, voice_vol, orig_vol, use_ocr, fit, resolution, translate_mode, render_kw, asr_engine)` | full stage chain below | stage artifacts |

Alt path (không phải queue): `server.py:1254` `_auto_pipeline` = download + optional split + `_gpu.submit(_auto_gpu)` (claim `__all__` tới khi GPU xong).

### 1.8 ASR

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 35 | `engines/vram.py:56` | `free_gpu_vram("trước ASR…")` | torch empty / GC | — |
| 36 | `server.py:3098` | `_resolve_asr_engine(wd, asr_engine)` | (again) | **`manifest.json`** |
| 37 | `server.py:2996` | `_asr_script(engine)` | map `ASR_SCRIPTS` | — |
| 38 | `server.py:390` | `_run_engine(script, wd)` | `_kill_job_engine_procs`; `subprocess.Popen([python, script, work_dir])` | engine writes; server streams logs |
| 39a | default map | e.g. `engines/asr/fun_asr_nano.py` / `nano_fa_asr.py` / `firered_asr.py` / `paraformer_zh.py` / `sensevoice_asr.py` / `hybrid_asr.py` | each `run_asr_*` / `main` | typically **`audio.wav`**, sidecar `asr.*.json`, promote **`asr.json`**, **`sub.zh.srt`**, **`manifest.stages.asr=done`** |
| 39b | `engines/asr/asr.py:247` | `run_asr(work_dir, …)` (Whisper path if used) | `resolve_asr_source` → `ensure_audio_wav` → `extract_audio` → Whisper → `to_srt` | **`audio.wav`**, **`asr.json`**, **`sub.zh.srt`**, manifest |

Common ASR helpers on happy path: `resolve_asr_source` → `ensure_audio_wav` → (`extract_audio` ffmpeg) → model generate → Manifest `mark_done`.

### 1.9 Translate (+ fill)

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 40 | `server.py:3063` | `_run_translate_engine(wd, target=…, mode=…)` | `_run_engine("engines/translate.py", …)` | via subprocess |
| 41 | `engines/translate.py:1989` | `run_translate(work_dir, batch, target, force, model, mode)` | LLM batches; glossary; optional preset_switcher | **`script.json`**, **`glossary.json`**, **`sub.vi.srt`**, **`manifest.stages.translate`** |
| 42 | `engines/translate.py:1894` | `count_script_missing(wd)` | read `script.json` | — |
| 43 | fill | `_run_translate_engine(wd, batch=25, mode="batch")` | same | update **`script.json`** |

### 1.10 Gates trước TTS (happy = pass-through)

| # | `file:line` | `func(args)` | calls | writes / branch |
|---|---|---|---|---|
| 44 | HOLD | if `agent.hold_after_translate` | Manifest update | **`manifest.json`** HOLD; **return** (không TTS) |
| 45 | `server.py:1341` | `_run_requested_review(wd, target)` | `run_name_pass`, `run_pronoun_pass`, `run_review` | may rewrite **`script.json`**; `script.pre_agent_review.json` |
| 46 | `agents/agent_qa_gate.py:123` | `run_qa_gate(wd, run_review_fn, target)` | `snapshot_pre_review` → review → `review_diff` → `evaluate_qa_gate` | **`script.pre_review.json`**; may rewrite **`script.json`**; if fail **return** |
| 47 | `server.py:1402` | `_save_series_glossary(wd)` | `series_glossary.save_from` | series glossary store |

### 1.11 TTS

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 48 | `server.py:2906` | `_resolve_voice(wd, None)` | manifest / queue_opts / voices | — |
| 49 | `server.py:2955` | `_resolve_speed(wd, None)` | — | — |
| 50 | `server.py:3110` | `_resolve_tts_engine(wd, None)` | tts_config / queue_opts | may **`tts_config.json`** |
| 51 | `engines/vram.py:56` | `free_gpu_vram("trước TTS")` | — | — |
| 52 | `server.py:3135` | `_do_tts(wd, voice, speed, engine, force=False)` | `_patch_tts_fields` → `run_clone_tts` | manifest tts cur_text |
| 53 | `engines/clone_tts.py:462` | `run_clone_tts(work_dir, engine, voice, speed, force)` | voice refs; worker venv; resume scan | **`tts/seg_XXXX.wav`**, **`tts.json`**, **`manifest.stages.tts`** |
| 54 | refill | if `n_missing` → `_do_tts` again | same | fill missing segs |

### 1.12 Separate / OCR (opts)

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 55 | `engines/separate.py:194` | `run_separate(wd)` if `audio_mode in demucs_*` | demucs | **`no_vocals.wav`** (+ vocals); **`manifest.stages.separate`** |
| 56 | `engines/ocr.py:128` | `run_ocr(wd)` if `use_ocr` | OCR engine | **`ocr.json`**; **`manifest.stages.ocr`** |

### 1.13 Assemble + Render (mux stage)

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 57 | `server.py:3151` | `_do_render(wd, force=False, audio_mode, voice_vol, orig_vol, fit, resolution, …)` | optional `run_separate`; `assemble`/`assemble_fit`; `engines.render.run_render` | see below |
| 58 | `engines/assemble.py:238` | `assemble(wd)` (short / fit=False) | `_load_clips`, `_read_mono` | **`dub_tts.wav`** (if ≤ NAIVE_MAX_SEC) |
| 59 | `engines/assemble.py:284` | `assemble_fit(wd)` (default / long) | `compute_fit_placements`, write wav | **`dub_fit.wav`**, **`tts_fit.json`** / fit stamp |
| 60 | `engines/render.py:2518` | `run_render(work_dir, …)` | `_find_video`; `ensure_job_audio_ts`; `write_fit_timings`; subs (`sub.vi.srt` / display); ffmpeg filtergraph (hardsub/blur/brand/lut/grain…) | **`output.mp4`**, updated **`sub.vi.srt`**, **`script.display.json`**, **`manifest.stages.mux=done`** (`output_path`) |

Note: `engines/mux.py:72` `run_mux` = simple ffmpeg A/V mux (copy video); **queue 1-click dùng `run_render` qua `_do_render`**, không gọi `run_mux` trực tiếp.

### 1.14 Artifacts sau done

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 61 | `core/job_queue.py:154` | `is_wired_done(wd)` | check mux+wired stages + `output.mp4` | — |
| 62 | `engines/split_parts.py:792` | `try_auto_merge_parent(job_id, …)` (nếu part) | `merge_job_parts` → `merge_parts_to_full` | parent **`output.mp4` / `output_full.mp4`**, **`split_info.status=merged`** |
| 63 | `agents/auto_publisher.py` | `publish_job(job_id)` (daemon thread) | uploader / Canva paths | upload side-effects (outside work/) |
| 64 | `_queue_run_one` | return `("done", "hoàn tất")` | `_hist_push` via worker | **`.job_queue.json`** clear current |

### 1.15 Artifact checklist (job thường, không split)

| File | Stage ghi chính |
|---|---|
| `manifest.json` | mọi stage |
| `source.*` (+ `source.info.json`) | download |
| `audio.wav` | ASR |
| `asr.json` (+ sidecars) | ASR |
| `sub.zh.srt` | ASR |
| `script.json` / `glossary.json` / `sub.vi.srt` | translate |
| `tts/seg_*.wav` / `tts.json` | TTS |
| `no_vocals.wav` | separate (opt) |
| `ocr.json` | OCR (opt) |
| `dub_fit.wav` / `tts_fit.json` | assemble |
| `output.mp4` | render/mux |

---

## 2. core/+server.py — per-function

### core/ + server.py (atoms)

### core/__init__.py
- (no functions)

### core/batch_config.py
- _now — (no doc) — L90
- _coerce — (no doc) — L94
- load — File hỏng/đang ghi dở → trả bản đọc tốt gần nhất (không rơi về DEFAULTS: Auto-pilot — L117
- resolve_job_opts — Opts của 1 job = config batch hiện tại ⊕ từng lớp (lớp sau đè lớp trước, bỏ None/pin_opts). — L141
- _norm_zoom — (no doc) — L155
- render_kwargs — Tham số render (_do_render / MuxReq) từ opts đã resolve. — L168
- meta — (no doc) — L194
- _write — (no doc) — L204
- update — Gộp patch vào config hiện tại. Key lạ / giá trị sai → ValueError. — L213
- reset — (no doc) — L233
- parse_kv — 'audio_mode=voice_bgm orig_vol=0.3 brand_text="Kênh A"' → dict. — L239
- describe — (no doc) — L251

### core/config.py
- _load_cfg — Nạp lại pineline.config.json khi file đổi (tránh setdefault env khóa giá trị cũ). — L20
- save_config — Cập nhật pineline.config.json an toàn + đồng bộ runtime. — L44
- _from_file_keys — (no doc) — L85
- inject_env — Chép pineline.config.json (rồi config.json) vào os.environ để tiến trình con kế thừa. — L89
- get — env var  >  config.json  >  default. — L115
- llm_settings — LLM cho job (dịch/review) — đọc lúc gọi để sửa pineline.config.json có hiệu lực không cần restart. — L140
- pass_llm_model — Model cho pass ngắn (name/pronoun). Ưu tiên NAME_MODEL/PRONOUN_MODEL → CHATGPT_* → REVIEW → LLM. — L155
- agent_llm — LLM cho agent chat / feeder: AGENT_* rồi LLM_* (cả hai file trước env). — L172
- venv_python — Đường dẫn python trong venv, đúng theo OS. — L185

### core/fileio.py
- atomic_write_text — (no doc) — L16
- atomic_write_json — (no doc) — L39
- read_json_checkpoint — Đọc checkpoint JSON. Hỏng → đổi tên thành .corrupt-<ts> (giữ để cứu) và trả default, — L43
- file_lock — (no doc) — L60

### core/film_db.py
- _utc — (no doc) — L109
- norm_path — (no doc) — L113
- connect — (no doc) — L117
- log_event — (no doc) — L153
- _status_of — (no doc) — L163
- _series_season — (no doc) — L177
- _num — (no doc) — L187
- _is_upload_lock_active — Kiểm tra nhanh xem .upload.lock của job còn thuộc về tiến trình đang sống không. — L194
- row_from_manifest — (no doc) — L216
- sync_one — Đồng bộ tức thì 1 job từ work/<job_id>/manifest.json vào films.db. — L282
- sync — Quét manifest → upsert films; ghi event khi trạng thái đổi. Trả {new, changed, total}. — L322
- needs_series_ids — (no doc) — L381
- sync_uploads — Link YouTube từ Z:\yt_uploader\upload_history.jsonl và queue_state.json. — L387
- source_keys — (no doc) — L473
- series_ids — (no doc) — L478
- update_block_status — Cập nhật trạng thái bản quyền (clean/blocked/claim/private/unknown) và lý do cho 1 phim. — L483
- query — (no doc) — L503
- get — (no doc) — L537
- get_lite — 1 row films, không kèm events — cho queue/sort. — L548
- get_many — Batch SELECT films theo job_id (không events). Giữ thứ tự ưu tiên theo input. — L555
- delete_film — Xoá 1 film khỏi database và tuỳ chọn xoá thư mục work trên ổ đĩa. — L578
- delete_films — Xoá nhiều film theo danh sách job_id. — L599
- purge_missing — Xoá toàn bộ hoặc các job chưa hoàn thành mà thư mục work đã bị xoá (work_exists = 0). — L622
- stats — (no doc) — L637
- to_csv — (no doc) — L657
- _dur — (no doc) — L669
- format_stats — (no doc) — L676
- format_rows — (no doc) — L690
- format_detail — (no doc) — L704
- upsert_library_block — Lưu hoặc cập nhật trạng thái bản quyền phim trong Thư viện gốc. — L726
- get_library_block — (no doc) — L792
- list_pending_rechecks — Lấy danh sách các bản ghi đang chờ recheck (status='testing'). — L798
- list_library_blocks — Trả về dict name -> record của tất cả các bộ đã check trong Thư viện. — L807
- delete_library_block — (no doc) — L814
- sync_library_blocks_from_yt_queue — Đồng bộ trạng thái bản quyền từ Z:\yt_uploader\queue_state.json cho các video D:\Lib. — L820

### core/job_meta.py
- parse_season_from_text — Bóc số phần/mùa từ title (Phần N / P N / 第N季). — L12
- norm_series_key — Chuẩn hoá tên bộ để sort. — L41
- extract_ui_meta — Trả title/series/season/group_* theo semantics hàng chờ (VI). — L55
- info_from_manifest_dict — (no doc) — L121
- info_from_film_row — Map films.db row → shape get_job_info. None nếu row thiếu title. — L134

### core/job_queue.py
- get_job_info — Metadata hàng chờ: ưu tiên films.db (series_ui/season_ui), fallback manifest. — L23
- get_jobs_info — Batch metadata cho nhiều job — 1 query DB + fallback file từng id thiếu. — L83
- job_sort_key — Khóa sắp xếp: (group_id|series_norm, season P1..Pn, title). — L108
- _reset_for_tests — Chỉ dùng trong pytest. — L126
- set_runner — (no doc) — L149
- is_wired_done — (no doc) — L154
- _persist_path — (no doc) — L167
- _save — (no doc) — L171
- _load — (no doc) — L188
- _hist_push — (no doc) — L216
- queue_busy — True nếu worker đang chạy hoặc còn job trong hàng — dùng GPU gate heal/watch. — L223
- current_detail — Stage/progress/ETA thô — đọc manifest của đúng 1 job (live). — L229
- build_queue_items — Metadata pending — 1 batch films.db (+ fallback), không N lần parse manifest. — L285
- queue_state — Trạng thái hàng chờ. enrich=True → queue_items/current_info qua batch DB. — L307
- http_queue_state — Payload GET /api/queue/jobs: state + live current_detail + labels ngắn. — L331
- queue_add — (no doc) — L350
- queue_sort — Sắp xếp lại các job đang chờ trong hàng: — L402
- queue_move — Di chuyển vị trí của 1 job trong hàng chờ: — L419
- queue_reorder — Gán lại toàn bộ thứ tự cho hàng chờ theo danh sách client gửi. — L449
- queue_add_group — Enqueue mọi member của group theo group_index tăng dần. — L461
- queue_front — (no doc) — L500
- queue_remove — Bỏ job khỏi hàng chờ (không stop current). — L508
- queue_update_opts — Đổi opts của job ĐANG CHỜ tại chỗ (giữ thứ tự, không đụng current) — thay cho remove+add. — L521
- queue_clear — (no doc) — L533
- queue_stop — Clear queue + báo worker dừng; gọi _stop_job(current) nếu server đã wire. — L541
- set_stop_hook — (no doc) — L563
- set_clear_stop_hook — (no doc) — L567
- _ensure_worker_unlocked — (no doc) — L572
- _ensure_worker — (no doc) — L583
- _worker_loop — (no doc) — L588

### core/manifest.py
- _now — (no doc) — L26
- _lock_for — (no doc) — L39
- _merge3 — Gộp 3 chiều dict JSON. Key mình không đổi so với lúc load → lấy bản đĩa (người khác — L52
- _xproc_lock — Khoá liên tiến trình (server + subprocess asr/tts cùng ghi). Không lấy được thì vẫn ghi — L77
- Manifest.__init__ — (no doc) — L97
- Manifest.load — (no doc) — L104
- Manifest._read_disk — (no doc) — L124
- Manifest.update — Đọc lại từ đĩa → fn(data) → ghi, trong khoá (thread + liên tiến trình). — L135
- Manifest.save — (no doc) — L148
- Manifest._write_locked — Ghi atomic; gọi khi đang giữ _lock_for(self.path). — L164
- Manifest.stage — (no doc) — L201
- Manifest.is_done — (no doc) — L204
- Manifest.mark_running — Giữ config cũ (voice/speed/engine/n_done...) — chỉ đổi status/started_at. — L208
- Manifest.mark_done — (no doc) — L220
- Manifest.mark_failed — (no doc) — L232

### server.py
- _maybe_auto_split_guarded — Wrap maybe_auto_split_job với lock chống gọi chồng cùng job_id. — L80
- _mux_output_ok — (no doc) — L103
- _part_pipeline_complete — Part/job đã mux + output, không stale → không chạy lại GPU pipeline. — L111
- _ensure_parent_mux_merged_done — Heal UI parent: Full đã merge mà mux còn running@80%. — L132
- _job_any_busy — Trả tên stage đang claim, hoặc None. — L162
- _claim_stage — Giữ chỗ trước khi submit thread — chống bấm 2-3 lần tạo nhiều task. — L171
- _release_stage — (no doc) — L180
- _busy_response — 409 nếu job đang có claim hoặc stage 'running' trong manifest, ngược lại None. — L187
- _submit_claimed — Claim (job, stage) rồi submit; nhả claim khi xong. Trả 409 nếu đã có claim. — L198
- _manifest_running — Stage đang 'running' trong manifest (nếu có). — L217
- _job_proc_alive — True nếu còn subprocess engine/ffmpeg đăng ký cho job. — L229
- _path_key — Khoá so đường dẫn: work là junction → D:, psutil.cwd() trả đường Z: chưa resolve. — L237
- _json_rows — (no doc) — L249
- _stage_complete_on_disk — Artifact ĐỦ (không phải bản dở sau Dừng/crash) — điều kiện để tự nâng stage lên done. — L257
- _stage_has_artifact — Artifact đĩa đủ để coi stage đã xong (dùng heal stale running). — L285
- _heal_stale_running — Sửa stage status=running mồ côi (kill/crash/skip không mark_done). — L309
- _next_incomplete_stage — Bước WIRED đầu tiên chưa done (để mark_running đúng — không ép lại ASR). — L380
- _run_engine — Chạy engine NẶNG (ASR/TTS) ở TIẾN TRÌNH RIÊNG. — L390
- _iter_job_engine_procs — Quét toàn hệ thống process Python đang chạy engine cho job_id (kể cả orphan). — L474
- _kill_job_engine_procs — Kill process engine trùng job (system-wide). Trả số process đã kill. — L520
- _kill_all_orphan_engine_procs — Kill toàn bộ orphan engine process trong WORK_ROOT (1 lượt quét duy nhất system-wide). — L535
- _noisy_log — Lọc log rác TTS (ref_text dài, tqdm...). Giữ gen_text + [ok]/[tts]/lỗi. — L577
- _kill_job_children — Kill MỌI tiến trình liên quan job (asr/clone_tts/demucs/ffmpeg/aria2c), — L589
- _stop_job — Dừng mọi việc đang chạy của 1 job + đưa stage 'running' về 'pending'. — L664
- _clear_stop — (no doc) — L750
- _stage_artifact_payload — Nếu đĩa đã có kết quả bước → payload để mark_done. None = chưa có artifact. — L764
- _heal_stages_from_disk — Misclick/Dừng giữa chừng: file đã ĐỦ mà status còn pending/failed → đánh done. — L824
- _force_mark_stage — Đánh dấu 1 bước done ngay (không chạy lại). — L846
- _url_host — (no doc) — L876
- _local_only_guard — Chỉ phục vụ máy này: Host lạ = DNS rebinding; Origin/Referer lạ trên /api = trang web — L885
- _quiet_conn_reset — Trên Windows, khi client (UI poll) đóng kết nối đột ngột giữa request, event — L902
- _reset_stale_running — Khi server khởi động, KHÔNG có thread nào đang chạy. Vậy mọi stage còn ghi — L919
- _start_queue_worker — Worker hàng đợi chỉ chạy SAU khi reset stage treo + kill engine orphan; chạy lúc import — L957
- _resume_hg_merge — Hàng đợi gộp Hongguo nạp lại từ work/logs/hg_merge_state.json → chạy tiếp nếu Hongguo đang mở — L965
- _startup_fix_tts — Khôi phục voice/progress TTS sau crash — không mất cấu hình. — L977
- _process_gpu — Phần NẶNG (GPU/LLM): ASR -> Dịch. Chạy ở hàng đợi _gpu (tuần tự). — L1209
- run_pipeline — TẢI (hàng đợi _dl, song song). Tải xong -> đẩy ASR+Dịch sang hàng đợi _gpu — L1236
- _auto_pipeline — 1-CLICK (chạy ở hàng _dl): tải (nếu cần) -> đẩy phần GPU sang hàng _gpu. — L1254
- _run_requested_review — Rà soát do Agent/user yêu cầu (manifest.agent.review_request): rà tên nhân vật theo bảng — L1341
- _save_series_glossary — (no doc) — L1402
- _auto_gpu — Phần GPU của 1-click (hàng _gpu, tuần tự): ASR -> Dịch -> TTS -> [Tách nền] — L1413
- _has_cjk — (no doc) — L1559
- _extract_vi_title — Bóc tách tên tiếng Việt từ response LLM có thể dài dòng / giải thích. — L1563
- _translate_title — Dịch tiêu đề gốc (Trung) sang tiếng Việt bằng gemma4 local, lưu title_vi. — L1593
- _maybe_translate_title — Kích hoạt dịch tiêu đề (lazy) nếu còn tiếng Trung. Bỏ qua khi ASR/TTS đang — L1640
- _asr_labels_from_source — Suy engine + model từ tên file sidecar (nguồn sự thật). — L1658
- _sync_asr_labels — Ép engine/model khớp asr_source (+ n_segments từ asr.json nếu có). — L1676
- _apply_hybrid_asr_overlay — Hybrid FA: UI đọc stages.asr — overlay % từ asr.*.progress.json nếu sidecar đang chạy. — L1714
- read_job — (no doc) — L1739
- _create — Tạo 1 job ở trạng thái CHỜ (chưa chạy). Người dùng bấm ▶ Bắt đầu mới chạy. — L1882
- _job_id_local — (no doc) — L1898
- _create_local_shell — Tạo job local (không URL). job_key ổn định theo path để resume cùng file. — L1902
- _list_local_videos — Liệt kê file video trong folder (sắp tên tự nhiên). — L1924
- _import_local_video_file — Copy/move 1 file video → job local. Trả dict ok/job_id hoặc error. — L1950
- create_job — Thêm link -> tạo job CHỜ. 1 link ra NHIỀU video (multi-P/playlist) -> gom — L1997
- _patch_job_group — Ghi/xoá group_* trong manifest.request. Trả False nếu job không tồn tại. — L2023
- _renumber_group — Sắp lại group_index 1..N theo index cũ (hoặc created). Trả job_ids còn trong nhóm. — L2053
- jobs_group — Gom job thành series / thêm vào nhóm / đổi tên / tách. — L2086
- api_queue_jobs_add — (no doc) — L2201
- api_queue_jobs_add_group — (no doc) — L2217
- api_queue_jobs_opts — {"opts_by_job": {job_id: opts}} — đổi opts job đang chờ tại chỗ (nguyên tử, giữ thứ tự). — L2232
- api_queue_jobs_remove — (no doc) — L2252
- _queue_current_detail — Alias → job_queue.current_detail (giữ tên cũ cho test/monkeypatch). — L2259
- api_queue_jobs_sort — (no doc) — L2264
- api_queue_jobs_move — (no doc) — L2272
- api_queue_jobs_reorder — (no doc) — L2287
- api_queue_jobs_state — (no doc) — L2299
- api_queue_jobs_stop — (no doc) — L2303
- api_queue_jobs_clear — (no doc) — L2307
- create_local_job_path — Tạo job từ file HOẶC folder video local. — L2311
- create_local_job_batch — Import nhiều path (file + folder). Mỗi folder → 1 group riêng. — L2381
- api_fs_list_dirs — Liệt kê folder con trực tiếp (1 cấp) để tick chọn import. — L2463
- api_fs_pick_dir — Mở hộp thoại Windows chọn folder (native). Chạy process riêng để không kẹt uvicorn. — L2516
- api_fs_pick_dirs — Hộp thoại chọn NHIỀU folder cùng lúc (Ctrl/Shift). Trả paths[]. — L2589
- create_local_job_upload — Tạo job từ upload video (không cần link). File lớn nên dùng /local-path. — L2654
- start_job — Chạy tự động các bước còn lại (download -> asr -> dịch) cho 1 job. — L2691
- _run_stage — Chạy ĐÚNG 1 bước (người dùng tự chọn). download -> hàng _dl; còn lại -> _gpu. — L2766
- _save_tts_voice — Lưu giọng vào manifest + sidecar — KHÔNG được wipe stages khác. — L2839
- _save_tts_speed — (no doc) — L2844
- _save_tts_engine — (no doc) — L2848
- _patch_tts_fields — Ghi field TTS an toàn: đọc đĩa trực tiếp, merge, atomic write. Không dùng — L2852
- _job_cfg_opts — Gộp opts + queue_opts (queue_opts thắng) — resolve voice/speed/engine. — L2895
- _resolve_voice — Giọng: arg → stages.tts → tts_config → queue_opts/opts → list[0]. — L2906
- _resolve_queue_voice — Queue chỉ dùng giọng được chọn rõ ràng hoặc đã lưu cho chính job. — L2931
- _resolve_speed — (no doc) — L2955
- _asr_script — (no doc) — L2996
- _patch_asr_fields — Ghi field ASR an toàn (không wipe stages khác). — L3000
- _save_asr_engine — Lưu engine. Nếu đã có sidecar tương ứng → promote luôn (tránh lệch nhãn/nội dung). — L3033
- _run_translate_engine — Chạy stage dịch ở TIẾN TRÌNH RIÊNG (subprocess) giống như ASR và TTS. — L3063
- _resolve_asr_engine — (no doc) — L3098
- _resolve_tts_engine — (no doc) — L3110
- _do_tts — Chạy TTS clone tiếng Việt (vieneu/omnivoice). Điều phối worker venv riêng — L3135
- _do_render — Ghép giọng (assemble nếu chưa) rồi render video localize (che+sub+trộn nền). — L3151
- run_stage — Chạy riêng 1 bước của job (chủ động chọn bước nào làm). Kiểm tra điều kiện — L3294
- stop_job — DỪNG mọi việc đang chạy của job (kill subprocess asr/tts/demucs/ffmpeg/aria2c — L3387
- mark_job_done — Đánh dấu bước (hoặc cả job) = done NGAY — không chạy lại / không chờ. — L3407
- translate_fill — VÁ câu trống ở bước Dịch: chạy lại dịch với LÔ NHỎ (25) — run_translate tự — L3464
- edit_script_line — Sửa tay zh và/hoặc vi: ghi script.json + regen SRT. Không đụng TTS clip — L3510
- clean_script_spam — Rút chuỗi 哈/呃 spam trong script.json (ASR lỗi) + prefill vi trivial nếu trống. — L3613
- set_tts_voice — Lưu giọng TTS đã chọn vào manifest (để nút Chạy / tự động dùng đúng giọng). — L3651
- run_all — 1-CLICK: chạy tự động toàn bộ pipeline từ bước còn thiếu tới hết. — L3665
- _queue_run_one — Run one queued job synchronously through mux and return status + detail. — L3737
- set_asr_engine — Lưu engine ASR (hybrid_fa / fun_asr_nano / …) cho job. — L4022
- _list_asr_sources — Liệt kê asr.json + asr.*.json có dữ liệu (bỏ progress/meta/chars/bak). — L4051
- _promote_asr_source — Copy sidecar → asr.json + sub.zh.srt; backup asr.json cũ. — L4104
- _invalidate_translate_for_asr — Backup script + đánh dấu translate lệch khi đổi asr_source. — L4224
- _translate_asr_sync_info — UI: script có khớp asr.json không? — L4268
- list_asr_sources — Danh sách file ASR có sẵn để chọn (Nano / FireRed / …). — L4317
- select_asr_source — Promote file ASR (vd asr.fun_nano.json) → asr.json + sub.zh.srt. — L4334
- _context_studio_input — Ưu tiên asr.json → sub.zh.srt. — L4349
- _do_context_studio — Chạy PRE-SCAN → ghi pack vào work_dir. — L4358
- get_context_studio — Xem pack Context Studio (summary + style_lock + characters). — L4421
- run_context_studio_api — Chạy Context Studio PRE-SCAN → glossary/style_lock/qa_flags trong work/<job>. — L4476
- get_translate_alts — Pack analyze checklist + danh sách câu đa nghĩa (vi_alts.json). — L4510
- run_translate_alts_api — Quét câu đa nghĩa theo chunk + pack analyze → vi_alts.json. — L4528
- apply_alt_pick — Chốt một phương án alts[pick] → vi (+ regen SRT). — L4553
- run_hardsub_asr_api — OCR hardsub → rà/sửa chữ ZH trên ASR (giữ timing). Không thay bước dịch. — L4611
- get_hardsub_asr — (no doc) — L4640
- _cookie_info — Đếm cookie + kiểm định dạng Netscape của 1 file cookie. — L4661
- cookies_status — (no doc) — L4675
- _header_to_netscape — Chuyển chuỗi header 'name=value; name2=value2' (copy từ DevTools) -> Netscape. — L4684
- import_cookies — Nhập cookies bằng FILE (.txt Netscape từ extension) HOẶC dán TEXT vào popup. — L4700
- list_jobs — (no doc) — L4745
- job_detail — (no doc) — L4758
- _audio_dur — Đo độ dài audio (giây) bằng ffprobe. Lỗi -> 0. — L4769
- _probe_video — Rút width/height/duration/vcodec bằng ffprobe. Lỗi -> {}. — L4782
- _clear_job_sources — Xoá source.* / mảnh .part cũ trước khi import. — L4806
- _link_or_copy — Hard link nếu được (cùng ổ — không tốn thêm dung lượng); khác ổ / FS không hỗ trợ mới copy. — L4818
- _direct_source_roots — (no doc) — L4829
- _is_direct_source — File trong thư viện (SOURCE_DIRECT_ROOTS) → job đọc thẳng video_path, không đặt file vào job. — L4834
- _place_source — Trả (đường dẫn video job dùng, cách đặt: direct/move/link/copy). — L4849
- _finalize_imported_source — Ghi meta + mark download done. `dest` có thể nằm ngoài job (source_mode=direct: file thư viện). — L4862
- _find_video — Tìm file video đã tải: ưu tiên video_path trong manifest, fallback glob. — L4906
- job_video — Stream video đã tải để preview. FileResponse tự xử lý Range -> tua được. — L4918
- _write_srt — Sinh .srt từ json nguồn, ghi ra sub.<lang>.srt. Trả (path, nội dung) hoặc — L4940
- _clone_voice_list — Giọng clone dùng chung cho cả 2 engine (registry voices/f5_voices.json). — L4996
- list_voices — Giọng clone (ref audio + lời) dùng chung — cả vieneu lẫn omnivoice đều — L5001
- list_frames — Danh sách PNG khung trong assets/overlays/frames. — L5008
- list_brand_logos — Logo kênh (assets/overlays/logos hoặc brand). — L5017
- _ref_asr_enabled — ASR mẫu: mặc định tắt nếu chưa có model (tránh treo tải Whisper 2GB lúc Thêm giọng). — L5033
- _probe_audio_dur — (no doc) — L5055
- _transcribe_ref — Lấy transcript của clip mẫu (F5 cần ref_text). Model medium int8 nhẹ VRAM. — L5067
- _prep_ref — Chuẩn hoá clip mẫu: cắt ≤max_dur, xuất wav 24k mono. Trả (wav, ref_text, dur). — L5081
- clone_voice — Clone 1 giọng từ file mẫu (3-8s). Đăng ký vào registry chung (VieNeu/OmniVoice). — L5143
- voice_sample — Đọc câu mẫu bằng engine+giọng (+ tốc độ) để nghe thử. Cache trên đĩa. — L5175
- tts_wav_ok — Danh sách index seg_*.wav còn trên đĩa (size OK) — UI khỏi báo thiếu oan khi chưa có tts.json. — L5215
- regen_tts — Lồng tiếng: mặc định RESUME (chỉ đọc câu thiếu). force=true -> đọc lại toàn bộ. — L5230
- regen_clip — Đọc lại DUY NHẤT 1 câu (index i) khi clip đó lỗi. Nhanh, không đụng câu khác. — L5323
- job_srt — Sinh .srt từ asr.json (zh) / script.json (vi), ghi ra file trong job rồi — L5339
- _reveal_path — Mở trình quản lý file, bôi sẵn đúng file (nếu target là file) hoặc mở thư mục. — L5354
- upload_source — Import source video qua upload (stream, không nhét cả file vào RAM). — L5373
- import_source_path — Import source từ đường dẫn local (cùng máy server) — phù hợp file multi-GB. — L5410
- upload_audio — Nhập 1 file audio lồng tiếng LÀM SẴN ở ngoài (từ SRT) để dùng cho mux. — L5449
- delete_audio — Bỏ audio ngoài đã nhập -> quay lại dùng TTS nội bộ. — L5482
- _translate_batch_size — Cỡ lô dịch — đọc TRANSLATE_BATCH (mặc định 20). Không hardcode 100. — L5498
- _translate_flow — Luồng dịch: (tùy chọn) DỊCH NHÁP rồi (tùy chọn) SOÁT lại lượt 2. — L5510
- retranslate_job — Dịch job: 1 lượt, HOẶC 2 lượt (nháp + soát), HOẶC chỉ soát bản có sẵn. — L5529
- mux_job — Render video localize -> output.mp4 (che watermark/hardsub + sub Việt + OCR — L5580
- assemble_job — Ghép clip TTS thành 1 track. — L5604
- get_split_plan — Xem trước kế hoạch chia part + cờ will_auto_split theo batch_config. — L5625
- api_split_job_parts — Chia video dài thành các sub-jobs (Part 1, Part 2...) chạy pipeline độc lập chống lệch time. — L5659
- api_merge_job_parts — Ghép các sub-jobs đã render xong thành output_full.mp4 (concat lossless). — L5668
- reveal_job — Mở thư mục job trong Explorer, chọn sẵn 1 file. Không truyền file -> chọn — L5677
- job_file — Phục vụ 1 file BÊN TRONG work/<job_id>/ (asr.json, script.json, mp3...). — L5704
- delete_job — Xoá 1 job = xoá cả thư mục work/<job_id>/ (video, audio, manifest...). — L5756
- _reexport_route_symbols — (no doc) — L5798
- _start_agent_watch — (no doc) — L5911
- _start_auto_publisher — (no doc) — L5924
- get_available_llm_models — Trả về danh sách toàn bộ các model LLM khả dụng (llama-server :8083, Ollama, 9router). — L5933

---

## 3. engines — per-function

### Engines atoms (AST)

- **Files:** 38
- **Functions/methods:** 538
- **Scope:** `engines/**/*.py` (module-level defs + class methods; nested defs skipped)

### engines/__init__.py
- *(none)*

### engines/asr/__init__.py
- *(none)*

### engines/asr/asr.py
- `_audio_marker` — (no docstring) — L46
- `_src_id` — (no docstring) — L50
- `extract_audio` — Tách audio về 16kHz mono PCM — chuẩn đầu vào Whisper. Ghi .partial rồi replace + marker nguồn. — L56
- `_wav_seconds` — (no docstring) — L78
- `_probe_seconds` — (no docstring) — L91
- `audio_wav_stale` — audio.wav có sẵn không dùng được: rỗng, marker khác nguồn / khác filter mốc, hoặc (chưa có — L100
- `ensure_audio_wav` — Trích audio.wav khi thiếu / hỏng / khác nguồn (hoặc force). True nếu vừa trích. — L130
- `resolve_asr_source` — Xác định nguồn audio sạch và chuẩn xác cho ASR. — L144
- `_cut_wav_from` — Cắt phần còn lại từ start_sec (resume ASR giữa chừng). — L197
- `pick_device` — Chọn cuda nếu có GPU, không thì cpu. Trả (device, compute_type). — L206
- `_salvage_asr` — Crash/treo: giữ asr.json đã có, status pending để bấm Tiếp tục. — L219
- `run_asr` — (no docstring) — L247
- `main` — (no docstring) — L421

### engines/asr/asr_align_nano_para.py
- `_norm_chars` — (no docstring) — L32
- `_ms_pair_to_s` — FunASR Paraformer timestamp luôn là milliseconds (vd. [8530, 8730] = 8.53s). — L36
- `extract_char_timeline` — Từ raw FunASR generate() → [{ch, start, end}, ...] (giây). — L42
- `_zip_text_ts` — (no docstring) — L68
- `chars_from_segments_spread` — Fallback khi không có char-ts: trải đều ký tự trong từng câu Para. — L103
- `_dtw_align` — DTW: trả map nano_idx -> para_idx (độ dài = len(nano_chars)). — L125
- `_window_map` — Map tỉ lệ + chỉnh local khi quá dài cho full DTW. — L189
- `align_nano_to_para` — Giữ text Nano; start/end lấy từ char-ts Para đã align. — L212
- `run_align` — (no docstring) — L318
- `main` — (no docstring) — L371

### engines/asr/asr_fix_align.py
- `_load` — (no docstring) — L41
- `_save_asr` — (no docstring) — L45
- `step1_nano_fallback` — Chỗ monotonic_fix (và đảo thời gian): lấy lại timing Nano theo chữ. — L55
- `_merge_indices_to_windows` — Gộp index gần nhau thành cửa sổ FA. — L105
- `step2_forced_align` — Forced-align từng cửa sổ chứa các câu nano_fallback. — L129
- `run_fix` — (no docstring) — L235
- `main` — (no docstring) — L312

### engines/asr/asr_hybrid_progress.py
- `_load_json` — (no docstring) — L21
- `map_sidecar_pct` — (no docstring) — L30
- `active_sidecar_progress` — Trả (tag, payload) sidecar đang chạy mới nhất; ưu tiên Para nếu cả hai. — L36
- `mirror_to_asr_stage` — Ghi tiến độ sidecar vào stages.asr (giữ hybrid_fa). Trả stage đã cập nhật. — L78
- `overlay_job_asr` — Overlay tiến độ sidecar lên dict stages.asr (cho API, không ghi đĩa). — L122

### engines/asr/asr_repair.py
- `_norm` — (no docstring) — L50
- `_load` — (no docstring) — L54
- `_overlap` — (no docstring) — L58
- `_text_sim` — Độ giống 0..1 (containment + overlap tuần tự) trên chuỗi đã _norm. — L62
- `_mid` — (no docstring) — L82
- `_already_has_similar` — True nếu base đã có câu gần nghĩa trong ±window_s (align lệch time). — L86
- `_para_cover` — (no docstring) — L109
- `_align_rank` — Ưu tiên giữ khi dedupe (cao hơn = tốt hơn). — L115
- `dedupe_shifted_repeats` — Xóa nhân bản lệch giờ: cùng/_gần text trong ±window_s → giữ 1 bản. — L129
- `_merge_windows` — wins: (start, end, reason) → merged {start,end,reasons}. — L184
- `detect_gaps` — Para có đoạn mà base phủ < max_cover_ratio → nghi thiếu câu. — L204
- `detect_cer_mismatches` — Chữ base khó khớp Para char-stream quanh mốc → nghi nghe sai. — L241
- `_asr_nano_clip` — (no docstring) — L280
- `apply_repairs` — Nano ASR từng cửa sổ: — L308
- `run_repair` — (no docstring) — L416
- `main` — (no docstring) — L523

### engines/asr/asr_spam.py
- `_strip_punct` — (no docstring) — L31
- `filler_stats` — (no docstring) — L35
- `is_phrase_loop_spam` — True nếu có cụm 2–12 chữ lặp ≥6 lần (vd «区域的»×200) — ASR kẹt loop. — L53
- `is_phrase_loop_remnant` — Sau clean_zh_spam giữ tối đa 2× unit — vẫn sót «…区域的区域». — L77
- `is_bg_filler_spam` — True nếu giống tiếng nền (cười/rên lặp), không phải thoại bình thường. — L104
- `is_filler_only` — (no docstring) — L119
- `clean_filler_text` — Rút chuỗi filler; giữ phần thoại thật nếu có. — L126
- `_load_heal_sources` — Sidecar ASR khác để vá filler (ưu tiên nano → para → sense → firered). — L140
- `_overlap_iou` — (no docstring) — L173
- `_heal_from_sources` — Tìm câu thật overlap đủ (IoU) — tránh lấy câu kế cận lệch thời gian. — L183
- `sanitize_asr_rows` — Rút spam + (tuỳ chọn) vá từ sidecar khác. — L266
- `sanitize_asr_file` — Đọc JSON ASR → sanitize → ghi đè (+ SRT nếu có cặp). — L390
- `prefer_non_spam` — Khi 2 bản lệch: ưu tiên bản không phải filler nền. — L423
- `main` — (no docstring) — L443

### engines/asr/asr_vad_utils.py
- `vad_kwargs_from_env` — Cho phép override qua env ASR_VAD_* (ms). — L33
- `parse_vad_ranges` — FunASR VAD generate → [(start_s, end_s), ...]. — L54
- `merge_close_ranges` — Gộp đoạn kề nhau (khoảng hở < gap_s), nhưng không gộp nếu tổng độ dài vượt max_dur_s. — L71
- `pad_ranges` — Mỗi VAD range → slice ASR có pad + overlap với hàng xóm. — L102
- `shift_char_timeline` — Cộng offset (slice_start) vào char-ts; optional cắt ngoài cửa sổ VAD gốc. — L141

### engines/asr/firered_asr.py
- `_roots` — (no docstring) — L46
- `_ensure_firered_importable` — (no docstring) — L54
- `_parse_firered_result` — FireRedAsr2System.process → [{start,end,text}]. — L69
- `run_asr_firered` — (no docstring) — L116
- `main` — (no docstring) — L330

### engines/asr/fun_asr_nano.py
- `_pick_device` — (no docstring) — L44
- `_wav_dur` — (no docstring) — L56
- `_ms_to_s` — FunASR timestamp luôn là milliseconds. — L71
- `_split_text_by_punct` — Tách câu theo dấu câu (mỏng: gọi subs.split_text_by_punct). — L79
- `_spread_sentences` — Không có timestamp ký tự -> chia thời gian theo độ dài chữ. — L85
- `_parse_funasr_result` — Chuẩn hoá output FunASR -> [{start, end, text}, ...]. — L106
- `_split_by_punct` — Gộp timestamp ký tự thành câu theo dấu câu Trung/Việt. — L178
- `_vad_ranges_chunked` — VAD theo cửa sổ ~chunk_s — tránh treo generate() trên file dài. — L216
- `_vad_slice_asr` — VAD cắt đoạn -> ASR từng đoạn có pad/overlap (Fun-ASR-Nano không có CTC ts). — L295
- `run_asr_nano` — sidecar: ghi asr.<tag>.json + sub.zh.<tag>.srt, không đụng asr.json / manifest ASR chính. — L398
- `main` — (no docstring) — L580

### engines/asr/hardsub_asr.py
- `_find_video` — (no docstring) — L31
- `_probe_size` — (no docstring) — L42
- `_norm_zh` — (no docstring) — L55
- `zh_sim` — Độ giống 0..1 (chuỗi đã chuẩn hóa). — L61
- `_band_y_frac` — (y0, y1) tỷ lệ chiều cao — ưu tiên hardsub_band.json. — L73
- `extract_hardsub_cues` — OCR crop đáy → list {start,end,zh,n,source}. — L100
- `_samples_to_cues` — Gộp frame liên tiếp cùng/gần text thành cue. — L166
- `merge_hardsub_into_asr` — Giữ timing ASR; chỉ thay text khi hardsub KHỚP chữ (tránh dính câu bên cạnh). — L202
- `_to_srt` — (no docstring) — L285
- `sync_script_zh` — Cập nhật script.json zh theo asr (khớp i hoặc time). — L309
- `run_hardsub_asr` — (no docstring) — L351
- `main` — (no docstring) — L432

### engines/asr/hybrid_asr.py
- `_prog` — (no docstring) — L45
- `run_hybrid_fa` — (no docstring) — L55
- `main` — (no docstring) — L180

### engines/asr/nano_fa_asr.py
- `_merge_all_to_windows` — Gom các câu thoại gần nhau thành cửa sổ nhỏ (<=24s) để Forced Aligner xử lý tối ưu. — L39
- `align_nano_with_fa` — Căn mốc trực tiếp từng câu của Nano bằng Qwen3ForcedAligner. — L75
- `run_nano_fa` — (no docstring) — L198
- `_torch_has_cuda` — (no docstring) — L314
- `main` — (no docstring) — L322

### engines/asr/paraformer_zh.py
- `run_asr_paraformer` — (no docstring) — L45
- `main` — (no docstring) — L292

### engines/asr/sensevoice_asr.py
- `_clean_sv_text` — (no docstring) — L51
- `_post_clean_segs` — (no docstring) — L65
- `run_asr_sensevoice` — sidecar: ghi asr.<tag>.json + sub.zh.<tag>.srt, không đụng asr.json / manifest ASR chính. — L77
- `main` — (no docstring) — L237

### engines/assemble.py
- `_read_mono` — Đọc 1 clip về mono float32 @ target_sr (bounded — chỉ 1 clip trong RAM). — L31
- `_compress_to_file` — Nén 'ratio'× bằng rubberband giữ formant -> file tạm. ratio<=1 trả nguyên in_path. — L65
- `_load_clips` — (no docstring) — L86
- `_slot_sec` — (no docstring) — L95
- `_natural_max_sec` — Trần độ dài đọc hợp lý (không phải câu TTS runaway). — L99
- `_runaway_cap_sec` — VieNeu đôi khi hú 15–23s cho câu 1–2 tiếng. Cắt trần, không đẩy cả film. — L105
- `is_runaway_tts` — True nếu wav quá dài bất thường so với slot/chữ (VieNeu hú). — L120
- `_resolve_max_speed` — UI/API thắng. Env ASSEMBLE_MAX_SPEED chỉ khi không truyền (None). — L125
- `_fit_mode` — fixed (max_speed>1 từ UI/API) | adaptive (mặc định) | off (ASSEMBLE_FIT_MODE=off). — L139
- `_is_bloated` — TTS kéo dài bất thường so với số chữ, hoặc ASR dồn mốc (khe ≤0.25s mà đọc >0.6s). — L147
- `_place` — (start, ratio) của một câu theo chế độ khớp. — L153
- `compute_fit_placements` — Đủ câu + khớp hình theo khoảng trống (KHÔNG cắt, nén theo _place). — L173
- `write_fit_timings` — Ghi tts_fit.json từ tts.json (không cần ghép lại audio). — L219
- `assemble` — NAIVE: báo cáo độ khớp (từ metadata, mọi độ dài). Dựng file chỉ khi ngắn. — L238
- `assemble_fit` — Đủ câu + ghép cạnh + bắt kịp khoảng trống (đúng yêu cầu user). — L284
- `main` — (no docstring) — L396

### engines/check_block.py
- `_utc_now` — (no docstring) — L21
- `extract_video_id` — Trích xuất Video ID (11 ký tự) từ link YouTube bất kỳ hoặc ID thô. — L25
- `check_youtube_block` — Kiểm tra video YouTube có bị Block hay dính bản quyền không (không cần cookie/đăng nhập). — L52
- `check_film_by_job` — Kiểm tra trạng thái bản quyền của một phim theo job_id và lưu kết quả vào film_db. — L319

### engines/clone_tts.py
- `resolve_engine_python` — Tìm python.exe của engine. Config sai path (thường sau install) -> thử chỗ mặc định. — L55
- `_load_registry` — (no docstring) — L91
- `list_clone_voices` — Tên các giọng clone đã có ref audio hợp lệ. — L97
- `_resolve_ref` — (no docstring) — L107
- `voice_ref_text` — (ref_path, ref_text) của 1 giọng, hoặc None. — L116
- `enroll_voice` — Đăng ký giọng clone vào voices/f5_voices.json (VieNeu + OmniVoice dùng chung). — L127
- `_is_trivial_vi` — True nếu không có chữ thật (vd ',', '...', '!!!') — không nên gọi TTS. — L149
- `vi_for_tts` — Chuẩn bị chữ cho VieNeu/Omni: gộp số có dấu nghìn để đọc đúng. — L155
- `_write_silence_wav` — Ghi wav im lặng đúng độ dài timeline (tối thiểu 0.15s để qua kiểm tra dur). — L180
- `_silence_entry` — Placeholder im lặng cho câu vô nghĩa / wav hỏng — đủ slot timeline, không báo thiếu. — L195
- `_dur` — Độ dài wav (giây). Ưu tiên wave; fallback ffprobe. — L203
- `_entry_from_wav` — Tạo entry tts.json từ file wav đã có. None nếu file hỏng/quá ngắn. — L221
- `_unlink_quiet` — (no docstring) — L232
- `_drop_runaway_from_done` — Resume/recheck: bỏ clip hú khỏi done + xóa wav → TTS sẽ đọc lại. — L239
- `_pack_clip` — Postprocess + entry. None nếu hỏng. Caller xử lý runaway. — L258
- `_recheck_pack_and_retry` — Đóng gói todo vừa TTS; runaway -> xóa -> retry tối đa N lần -> silence slot. — L267
- `_clip_key` — (no docstring) — L342
- `_load_keys` — (no docstring) — L347
- `_save_keys` — (no docstring) — L355
- `_stamp_keys` — (no docstring) — L365
- `_scan_done_from_disk` — Resume: nhận diện seg_XXXX.wav đã ghi (sau khi Dừng) dù chưa kịp ghi tts.json. — L371
- `_postprocess_clip` — (no docstring) — L392
- `_salvage_progress` — Khi dừng/crash: gom wav đã có -> tts.json, status pending (để bấm Tiếp tục). — L403
- `run_clone_tts` — (no docstring) — L462
- `_cleanup_audio` — Làm sạch clip gen ra: — L616
- `_trim_onset` — Cắt 'âm rác đầu' của OmniVoice: nếu đoạn tiếng ĐẦU TIÊN ngắn (<0.45s) và có — L646
- `_apply_speed` — Đổi tốc độ đọc bằng rubberband giữ formant (fallback atempo). speed>1 nhanh, <1 chậm. — L683
- `_run_worker` — Chạy worker venv cho `lines`=[(i,text)], ghi out_dir/seg_XXXX.wav. Raise nếu lỗi. — L711
- `synth_one` — Đọc 1 câu bằng engine+giọng -> ghi ra out_path (dùng cho nghe thử / đọc lại 1 clip). — L840
- `resynth_clip` — Đọc lại DUY NHẤT câu index i -> tts/seg_i.wav + vá tts.json. Trả entry. — L865
- `_norm_txt` — Chuẩn hoá để so khớp: thường hoá, bỏ dấu câu, gộp khoảng trắng. — L885
- `_similar` — (no docstring) — L893
- `_asr_check` — Nghe ngược list [(wav_path, expected_vi)] -> [(score, transcript)]. Whisper small. — L901
- `verify_and_fix` — TỰ KIỂM & SỬA: ASR nghe ngược từng clip, câu nào lệch nhiều so với bản dịch — L920
- `_roughness` — Độ 'nhám/méo' của clip: HF-ratio ở các khung CÓ CAO ĐỘ (voiced) — loại âm gió — L975
- `fix_glitches` — TỰ PHÁT HIỆN & SỬA câu bị vỡ/méo (âm): đo độ nhám voiced-frame, câu nào nhám — L1003
- `_prog` — (no docstring) — L1063
- `_finalize` — (no docstring) — L1079

### engines/download.py
- `_request_stop` — (no docstring) — L54
- `_is_stopped` — (no docstring) — L59
- `_clear_stop` — (no docstring) — L64
- `_kill_job_aria2c` — Kill tiến trình aria2c đang tải cho ĐÚNG job này (nhận diện qua job_id/đường — L69
- `_aria2_downloaded` — Byte ĐÃ TẢI THẬT theo file điều khiển .aria2. Khi tải đa kết nối, file .part — L91
- `_clean_incomplete_fragments` — Xoá RIÊNG các mảnh tải DỞ (file .part + control .aria2) để tải lại sạch bằng — L113
- `_delete_sources` — Xoá mọi source.* ; trả True nếu SẠCH (không còn file nào kẹt/khoá). — L127
- `_format_sel` — Selector yt-dlp. max_height giới hạn chiều cao; hevc=True ưu tiên H.265 cùng độ phân giải. — L141
- `_cfg_max_height` — DOWNLOAD_MAX_HEIGHT từ env/config (vd 720/480). 0/off = không giới hạn. — L172
- `_cfg_prefer_hevc` — DOWNLOAD_PREFER_HEVC=1 → ưu tiên H.265 cùng độ phân giải (file nhẹ, CDN đỡ đứt). — L190
- `_auto_height_for_duration` — Phim rất dài (Bilibili multi-season) → 720p AVC dễ ~3GB+, CDN hay đứt. — L202
- `_probe_duration` — Lấy duration nhanh (không tải) để chọn format. — L216
- `detect_platform` — (no docstring) — L232
- `normalize_url` — Chuyển link Bilibili kiểu mới về format yt-dlp hiểu (từ code Galaxy). — L243
- `job_id_from_url` — Job id mặc định = hash URL. Chạy lại cùng URL -> cùng thư mục -> resume. — L252
- `find_cookie_file` — Tìm file cookie theo nền tảng trong cookies_dir (vd bilibili_cookies.txt). — L257
- `get_aria2c_path` — Tìm aria2c -> trả ĐƯỜNG DẪN TUYỆT ĐỐI (yt-dlp tìm external_downloader trong — L271
- `apply_speed_opts` — Tải mảnh song song + aria2c nếu có (args tune từ code Galaxy). — L281
- `download_video` — Tải 1 video về work_dir. Trả về dict trạng thái stage (video_path + metadata). — L305
- `main` — (no docstring) — L659

### engines/llm.py
- `_settings` — (base, key, model) đọc LÚC GỌI (file config trước env) — sửa pineline.config.json — L58
- `_llama_base` — (no docstring) — L69
- `get_llama_models` — Lấy danh sách các model đang load trên llama-server (:8083). — L77
- `get_ollama_models` — Lấy danh sách model trên Ollama (:11434). — L95
- `list_available_models` — Trả về toàn bộ model khả dụng (llama-server 8083, ollama 11434, config). — L108
- `_is_loopback_base` — (no docstring) — L158
- `is_local` — (no docstring) — L163
- `is_chatgpt` — Model route qua Aurora / Chat2Api (pool account Free). Tiền tố chatgpt/ hoặc aurora/. — L170
- `_chatgpt_settings` — (bases, key, default_model) cho Aurora pool. — L176
- `_jwt_expired` — True nếu JWT có claim exp đã qua (token local hết hạn không được đè Aurora pool). — L204
- `_chatgpt_token_file` — Đọc access token tùy chọn từ data/chatgpt_token.txt (bỏ qua nếu JWT hết hạn). — L219
- `_chatgpt_chat` — Gọi Aurora/Chat2Api (OpenAI-compatible). Pool Free xoay phía server Aurora. — L238
- `aurora_upload_file` — Upload file lên Aurora `POST /v1/files` (cần ChatGPT access_token thật). — L315
- `_file_unread_response` — GPT trả JSON/text báo không đọc được file đã upload (thường do lệch account pool). — L391
- `chatgpt_chat_with_file` — Hỏi GPT kèm file đã upload (`type: input_file` + `file_id`) — 1 lần đọc file. — L411
- `ensure_ollama_model` — Model Ollama chưa pull -> TỰ pull (lần đầu, có thể vài GB). Auto cho bước dịch. — L513
- `free_ollama_vram` — Alias — nhả VRAM (Ollama + torch) trước/sau bước GPU. — L535
- `unload_local` — Nhả model Ollama khỏi VRAM (RTX 3060 12GB không chứa nổi LLM + TTS cùng — L541
- `_ollama_num_ctx` — Gemma3/4 mặc định context 131072. Cấp KV 128k trên RTX 3060 12GB -> tràn — L550
- `_ollama_chat` — Gọi Ollama qua endpoint GỐC /api/chat + TẮT thinking (think=False). — L560
- `chat` — Gửi messages, trả về text của assistant. Tự retry khi lỗi mạng/429/5xx. — L612
- `chat_with_meta` — Giống chat() OpenAI-path nhưng trả (content, meta) gồm usage/timings/TPS. — L765
- `parse_json` — Bóc JSON kể cả khi model bọc trong ```json ... ```, trailing commas hoặc kèm chữ thừa. — L822

### engines/media_ts.py
- `_boxes` — (no docstring) — L32
- `_child` — (no docstring) — L49
- `mp4_track_stts` — (timescale, [(count, delta)]) của track đầu tiên loại `kind` (soun/vide). — L53
- `audio_drift_points` — Trục 'dồn mẫu' → trục mốc: (vị trí theo mẫu [s], tiếng dư tích luỹ tới đó [s]). — L92
- `audio_ts_drift` — Tổng tiếng dư so với mốc (s). 0 nếu không đọc được. — L119
- `make_retime` — Hàm t(trục dồn mẫu) → t(trục hình). None nếu lệch không đáng kể. — L125
- `_probe_dur` — (no docstring) — L138
- `_retime_srt` — (no docstring) — L147
- `ensure_job_audio_ts` — Job đã ASR trên audio dồn mẫu → dời mốc về trục hình + ghép lại dub_fit. — L158
- `_tmp_of` — (no docstring) — L229
- `_backup_once` — Không bao giờ đè backup đã có — bản trong _pre_audio_ts luôn là bản gốc trước lần dời đầu. — L233
- `_atomic_write` — (no docstring) — L239
- `_commit_retime` — Pha thay file — chạy lại an toàn: mỗi bước kiểm tra trạng thái trước khi làm. — L245
- `main` — (no docstring) — L279

### engines/mux.py
- `_find_video` — (no docstring) — L31
- `_pick_dub` — Chọn track lồng tiếng: audio ngoài > dub_fit.wav > (tự ghép fit). — L40
- `_has_audio` — Video gốc có luồng audio không (để biết có ducking được không). — L59
- `run_mux` — (no docstring) — L72
- `main` — (no docstring) — L124

### engines/ocr.py
- `_meaningful` — Giữ chữ CÓ NGHĨA: ≥2 chữ Hán, hoặc số ≥3 chữ số (ID). Bỏ rác latin / 1 chữ đơn. — L39
- `_find_video` — (no docstring) — L54
- `_probe_size` — (no docstring) — L65
- `extract_keyframes` — Trích KEYFRAME + mốc giờ. Giải mã chỉ I-frame nên nhanh. stride: lấy cách quãng. — L77
- `_classify_zone` — Trả 'wm' (watermark), 'sub' (hardsub thoại), hoặc 'cand' (ứng viên). — L113
- `run_ocr` — (no docstring) — L128
- `_translate_entries` — Dịch danh sách chữ trên hình sang tiếng Việt (1 lời gọi LLM). — L243
- `main` — (no docstring) — L262

### engines/playlist.py
- `_build_url_from_entry` — Lấy URL đầy đủ từ một entry playlist. extract_flat có khi chỉ trả id. — L37
- `expand_meta` — Như expand nhưng trả THÊM metadata để gom nhóm: — L53
- `expand` — Đọc link, trả danh sách URL video. Video đơn -> [url]; playlist -> [nhiều]. — L106
- `batch_download` — Tải tất cả video của 1 link. Trả list kết quả {url, job_id, ok, error}. — L119
- `main` — (no docstring) — L176

### engines/pronoun_consistency.py
- `_cfg` — (no docstring) — L30
- `analyze_enabled` — (no docstring) — L38
- `analyze_model` — (no docstring) — L43
- `chunk_size` — (no docstring) — L54
- `analyze_mode` — file = upload SRT ZH 1 lần (Aurora /v1/files). fast = mẫu+lô. full = quét hết. — L61
- `max_chunks` — (no docstring) — L66
- `min_chunks_before_stop` — (no docstring) — L73
- `early_stop_enabled` — (no docstring) — L80
- `is_pronouns_locked` — (no docstring) — L85
- `mark_locked` — (no docstring) — L94
- `export_zh_lines` — Chuẩn hoá [{i, zh}] từ asr segments hoặc script rows. — L110
- `write_zh_export` — (no docstring) — L128
- `write_zh_srt` — Xuất sub.zh.srt để Aurora upload (API.md: POST /v1/files). — L138
- `_apply_analyze_delta_to_plan` — (no docstring) — L174
- `analyze_via_srt_file` — Upload sub.zh.srt → GPT đọc 1 lần → glossary pronouns (Aurora file QA). — L193
- `select_analyze_lines` — fast: phủ đầu/giữa/cuối + câu có hô ngữ — ít lô hơn full scan. — L281
- `_slim_memory` — Giảm token gửi Aurora mỗi lô. — L323
- `_merge_pronouns` — (no docstring) — L347
- `_merge_chars` — (no docstring) — L375
- `_analyze_chunk` — (no docstring) — L393
- `analyze_full_zh` — A) Quét toàn bộ ZH theo lô + memory → cập nhật plan + lock pronouns. — L430
- `lock_banner` — Block inject vào plan_block / batch khi đã lock. — L597
- `review_lock_rules` — Prompt ép 31B review: khi đã lock thì CẤM đổi self/call. — L623
- `fix_preserves_locked_register` — True nếu bản sửa không đổi thanh ngữ chính so với nháp (khi đang lock). — L639
- `filter_review_fixes_for_lock` — Khi pronouns_locked: loại fix làm đổi thanh ngữ so với vi_nhap. — L658
- `ledger_from_prev` — B) Ledger từ vài câu VI trước — nhắc model giữ thanh ngữ đang dùng. — L681
- `_forms_in` — (no docstring) — L706
- `find_pronoun_jumps` — C) QA: trong cửa sổ gần nhau, vừa có {anh,em} vừa có {ông} ngôi hô / tôi lệch kiểu. — L718
- `ensure_analyze_before_translate` — Gọi từ translate.run_translate sau khi có plan. — L761
- `run_post_translate_consistency` — C+D sau dịch/polish: post-pass + QA jumps + GPT vá đỏ. — L784

### engines/render.py
- `_ass_colour` — #RRGGBB hoặc &HAABBGGRR -> ASS. — L64
- `_sum_expr` — a+b+…; ffmpeg chỉ nhận ≤100 hạng tử cộng phẳng → dài thì gom ngoặc cân bằng. — L79
- `_pw_expr` — Theo t: vals[i] với i nhỏ nhất có t < ends[i] (ends tăng dần, len = len(vals) - 1), hết → vals[-1]. — L92
- `_censor_expr` — enable=... cho blur cảnh nhạy cảm. Config CENSOR_RANGES='12-18,90-102' (giây) — L109
- `_probe_dur` — Độ dài video (giây) để tính % render. — L136
- `_ffmpeg_progress` — Chạy ffmpeg + đọc -progress -> cập nhật % vào manifest (mux). Trả (mã, lỗi). — L152
- `_no_power_throttle` — Tắt EcoQoS của Windows cho ffmpeg con (tránh bị dồn sang E-core khi console thu nhỏ). — L286
- `_mp4_video_stts` — (timescale, [count, delta, ...]) từ box stts của track video mp4/mov. — L309
- `_probe_pts` — (no docstring) — L365
- `squeeze_fixes` — Đoạn mốc thời gian bị nén khi gộp tập khác fps: N khung dài ~0 rồi 1 khung dài hàng phút. — L379
- `squeeze_setpts` — setpts trải lại các đoạn bị nén (rỗng nếu không có). — L436
- `_cfg_num` — (no docstring) — L450
- `chunk_plan` — (giây mỗi khúc, số khúc chạy cùng lúc). RENDER_CHUNK_SEC=0 hoặc RENDER_CHUNK_PAR<2 → 1 lượt. — L458
- `chunk_cuts` — Điểm cắt mỗi ~sec giây, nằm GIỮA 2 khung liền nhau (không trùng mốc khung → không lặp/mất khung). — L468
- `_run_chunked` — Render video theo khúc (giữ mốc gốc), tối đa `par` khúc chạy cùng lúc, ghép copy, gắn audio 1 lần. — L489
- `_encoder_pref` — (no docstring) — L687
- `_nvenc_state` — (no docstring) — L700
- `_nvenc_save` — (no docstring) — L711
- `_want_nvenc` — (no docstring) — L718
- `_nvenc_mark_ok` — (no docstring) — L734
- `_nvenc_mark_fail` — (no docstring) — L738
- `_attach_filter_complex` — Ghi filtergraph ra file — tránh cắt cmdline Windows (~8191 ký tự). — L756
- `_ff_input` — Đường dẫn -i khi ffmpeg cwd=work_dir: file trong job → tên/relative; ngoài → absolute. — L764
- `_x264_cmd` — Đổi lệnh nvenc → libx264 (bỏ flag chỉ GPU). — L774
- `normalize_vbitrate` — Chuẩn hoá bitrate H264: trả (vbit, buf). Cho phép 2M | 4M | 8M. — L791
- `_find_video` — (no docstring) — L813
- `_size` — (no docstring) — L824
- `_fps` — (no docstring) — L833
- `_esc` — Escape text cho drawtext. — L847
- `_map_pt` — Toạ độ fraction (0-1) sau khi zoom+crop giữa. — L853
- `_map_box` — Map hộp nguồn → sau zoom/crop; None nếu gần như bị crop hết. — L859
- `_flip_box` — (no docstring) — L881
- `_default_wm_corners` — Fallback góc kênh khi OCR không bắt được logo hình (ô nhỏ, chỉ mép). — L890
- `_uploader_hint` — (no docstring) — L921
- `_is_wm_text` — (no docstring) — L929
- `_wm_quadrant` — (no docstring) — L944
- `_expand_logo_pad` — OCR chữ → snap nhẹ về mép góc; giữ kích thước gần bbox, cap nhỏ. — L957
- `_cap_wm_frac` — Giới hạn hộp che sau map — không cho phình quá mép góc. — L986
- `_wm_sample_times` — Mốc giây lấy mẫu watermark trên TOÀN bộ video (không chỉ 3 phút đầu). — L1005
- `_extract_wm_frames` — Seek từng mốc → 1 frame JPEG. Nhanh hơn decode cả file. — L1032
- `_merge_wm_timeline` — Gộp hit (t,q,x0,y0,x1,y1,txt) → [{t0,t1,x,y,w,h}, …] theo góc + thời gian. — L1055
- `_parse_wm_cache` — Đọc cache: list dict timed, hoặc list [x,y,w,h] cũ → coi full video. — L1129
- `detect_overlays` — Dò hardsub (đầu phim) + watermark THEO THỜI GIAN trên cả video. — L1150
- `detect_hardsub_band` — Tương thích cũ: chỉ trả band. — L1286
- `_hs_cluster_band` — (y0,y1) của 1 cụm vị trí — bỏ 5% ngoại lai mỗi phía khi đủ mẫu. — L1295
- `detect_hardsub_track` — Dò toạ độ hardsub THEO THỜI GIAN trên toàn video (file merge đổi vị trí giữa các tập). — L1303
- `_even` — (no docstring) — L1522
- `_rounded_bar_alpha` — Biểu thức geq alpha cho hình chữ nhật bo góc (0–255). — L1526
- `_boxblur_r` — Radius boxblur hợp lệ: ffmpeg yêu cầu 2*r < min(w,h) của plane. — L1544
- `_safe_crop` — crop ffmpeg an toàn khi iw/ih đổi giữa chừng (biểu thức min). — L1554
- `_hardsub_bar_filter` — Che hardsub: 1× boxblur + lớp đen geq bo góc (không desat). — L1563
- `_hardsub_cover_fullw` — Luôn phủ hết ngang khi che hardsub — OCR x0/x1 thường chỉ ~50% giữa → chữ Trung lòi 2 mép. — L1596
- `_hardsub_track_boxes` — Dải hardsub (tỉ lệ nguồn) → ô pixel trên canvas TRƯỚC zoom: (bx,by,bw,bh,ranges,tổng giây). — L1602
- `_stretch_cfg` — (sigma ngang, sigma dọc, phủ hết bề ngang) cho kiểu che stretch. — L1660
- `_stretch_chain` — Che hardsub kiểu kéo giãn: trung bình vài hàng ngay trên ô, kéo dọc phủ ô rồi làm mềm — L1671
- `_stretch_track_filter` — Kiểu stretch cho mọi dải: khoảng nào nhiều dải cùng hiện thì phủ 1 ô gộp (không chồng 2 lớp). — L1685
- `_hardsub_track_filter` — Che đúng ô hardsub theo thời gian (không lớp đen). — L1722
- `_srt_to_ass_margins` — SRT → ASS với MarginV riêng từng câu (mv_at(t_giữa_câu) → px). Trả số câu. — L1759
- `_hardsub_track_filter_dyn` — Nhiều dải → 1 chuỗi blur chính + 1 chuỗi phụ (chỉ bật lúc 2 dải chồng nhau). — L1803
- `resolve_canvas` — Chọn khung xuất: source = giữ gốc; 1080/1k = Full HD (giữ tỉ lệ, tối đa 1920×1080). — L1867
- `_parse_flip` — (no docstring) — L1880
- `build_video_filter` — Trả (filter_comma_chain_without_final_vout, meta). — L1891
- `_pick_dub` — (no docstring) — L2228
- `_normalize_audio_mode` — (no docstring) — L2239
- `_uses_sidechain` — duck / duck_bgm / sfx_lib dùng sidechaincompress — KHÔNG chạy cùng encode video — L2252
- `_stage_note` — Callback ghi dòng log tiến trình con vào cur_text của stage render (thưa ≥2 s). — L2258
- `_ensure_mixed_audio` — Pass 1: mixed_audio.wav (audio-only + sidechain). Trả (path, used_mode). — L2276
- `_mix_signature` — Filter + (đường dẫn, size, mtime) mọi input -i + độ dài — đổi thì phải trộn lại. — L2349
- `_write_mix_signature` — (no docstring) — L2366
- `_build_audio_filter` — Dựng filter audio + THÊM input vào cmd. Trả (filter, tên_chế_độ_thực). — L2375
- `run_render` — (no docstring) — L2518
- `main` — (no docstring) — L3003

### engines/render_fx.py
- `_esc_movie` — Escape path for ffmpeg movie= / lut3d= file=. — L21
- `resolve_lut_file` — (no docstring) — L27
- `resolve_grain_file` — (no docstring) — L41
- `list_bgm_files` — (no docstring) — L50
- `pick_bgm` — (no docstring) — L63
- `default_audio_mode` — voice_bgm nếu có thư viện BGM; không thì voice_only (không nhạc gốc). — L75
- `clamp_zoom` — (no docstring) — L80
- `normalize_grain` — (no docstring) — L98
- `_eq_fallback` — (no docstring) — L109
- `build_motion_zoompan` — Ken Burns nhẹ + Drift: scale cố định theo zoom + crop sin(t). — L116
- `build_static_zoom` — (no docstring) — L135
- `lut3d_filter_arg` — Đường dẫn LUT an toàn cho filtergraph Windows. — L142
- `_read_cube` — (no docstring) — L163
- `separable_lutrgb` — LUT 3D mà mỗi kênh ra chỉ phụ thuộc kênh vào cùng tên → lutrgb 1D tương đương. — L180
- `append_lut_filters` — Thêm LUT hoặc eq. Trả nhãn dùng thực tế. — L217
- `grain_noise_alls` — (no docstring) — L234
- `append_inline_noise_grain` — Film grain qua noise= (ổn định). PNG trong assets dùng khi blend input riêng. — L243
- `grain_blend_fragment` — PNG blend tắt mặc định (movie loop dễ treo). Giữ API cho phase sau. — L255
- `bgm_volume` — (no docstring) — L261
- `dub_volume` — Âm lượng giọng Việt khi mix (VieNeu đã chuẩn hoá ~0.9 → boost vừa phải 1.25 tránh vỡ tiếng). — L268
- `list_frame_files` — PNG/WebP khung trong assets/overlays/frames (+ overlays gốc). — L277
- `pick_frame` — choice: off | auto | tên file | đường dẫn. — L312
- `prepare_frame_file` — Copy khung vào job → basename cho movie= (cwd=work_dir). — L342
- `brand_text_value` — (no docstring) — L360
- `normalize_brand_mode` — off | drift | corners | drift_seed. — L367
- `brand_enabled` — (no docstring) — L390
- `brand_xy_expr` — Biểu thức ffmpeg x/y cho chữ/logo brand. — L397
- `list_brand_logo_files` — (no docstring) — L430
- `pick_brand_logo` — (no docstring) — L462
- `prepare_brand_logo` — (no docstring) — L487
- `brand_drawtext_filter` — Chữ kênh với x/y expression đã chọn. — L503
- `apply_brand_overlay` — Ghép brand (chữ ± logo) vào filter chain. Trả (body, meta). — L527

### engines/script_lint.py
- `_fix_kin` — (no docstring) — L33
- `_fix_punct` — (no docstring) — L39
- `_fix_num` — (no docstring) — L43
- `_glossary_terms` — (no docstring) — L47
- `_variant_re` — (no docstring) — L57
- `_chi_majority` — (no docstring) — L65
- `autofix_rows` — (no docstring) — L76
- `lint_rows` — Đếm lỗi còn lại — không sửa. Dùng cho QA gate / agent / UI. — L107
- `run_lint` — Lint script.json của 1 job; fix=True thì autofix + ghi lại (+ SRT/display). — L138
- `write_display` — (no docstring) — L155

### engines/separate.py
- `_find_video` — (no docstring) — L39
- `_probe_duration` — Lấy thời lượng file media (giây) qua ffprobe. — L50
- `_update_sep_progress` — Cập nhật tiến độ vào stage 'separate' VÀ đồng bộ sang stage 'asr' nếu ASR đang chờ tách giọng. — L63
- `_extract_audio` — Tách audio GỐC chất lượng cao (stereo 44.1k) — khác audio.wav 16k mono của ASR. — L82
- `_run_demucs_on_file` — Chạy Demucs trên 1 file audio (ngắn hoặc 1 chunk) và trả về (no_vocals_wav, vocals_wav). — L100
- `_concat_wav_chunks` — Ghép các chunk WAV thành 1 file WAV hoàn chỉnh (dùng -rf64 auto để hỗ trợ >4GB cho phim dài). — L170
- `run_separate` — (no docstring) — L194
- `main` — (no docstring) — L360

### engines/series_glossary.py
- `_core_of` — (no docstring) — L22
- `series_key` — (no docstring) — L32
- `_path` — (no docstring) — L43
- `load` — (no docstring) — L48
- `_valid_char` — (no docstring) — L73
- `_merge_list` — top đè base theo key; giữ thứ tự: mục của top trước, mục chỉ có ở base sau. — L77
- `_zh` — (no docstring) — L93
- `_pron` — (no docstring) — L97
- `apply` — (no docstring) — L101
- `save_from` — (no docstring) — L124

### engines/sfx_lib.py
- `effect_volume` — (no docstring) — L46
- `music_volume` — (no docstring) — L53
- `voice_boost` — Hệ số nhân thêm lên RENDER_DUB_VOL, chỉ cho sfx_lib. — L60
- `model_dir` — (no docstring) — L69
- `lib_dir` — (no docstring) — L73
- `model_files` — (no docstring) — L77
- `_fstat` — (no docstring) — L84
- `separate_stream` — Tách theo khúc, nối crossfade tuyến tính ở vùng chồng. — L94
- `_cdx_fn` — (no docstring) — L126
- `separate` — Âm gốc (video/audio bất kỳ) → sfx_effect.flac + sfx_music.flac. — L151
- `window_features` — (rms_db, flux) mỗi cửa sổ win_s của stem nhạc (mono; flux tính ở ~11 kHz). — L196
- `_median` — (no docstring) — L214
- `classify` — Cửa sổ → đoạn {start, end, level}. Mức calm/mid/intense chia theo tam phân vị của chính phim. — L222
- `library` — {mức: [(đường dẫn, giây)]} từ assets/bgm_yt/manifest.json (+ file lạ trong thư mục mức). — L271
- `_probe` — (no docstring) — L282
- `plan_bgm` — Xếp bài cho từng đoạn → [{file, at, off, dur, fin, fout}] (giây). Đoạn 'none' để trống. — L291
- `_decode` — (no docstring) — L321
- `render_bgm` — Ghi dải nhạc dài `total` giây theo plan (từng khối, không giữ cả dải trong RAM). — L331
- `prepare` — (no docstring) — L372
- `run_subprocess` — Gọi prepare ở tiến trình con (nhả VRAM/RAM khi xong); on_line(dòng log) để cập nhật tiến độ. — L409
- `main` — (no docstring) — L426

### engines/split_parts.py
- `_is_disk_full_text` — (no docstring) — L36
- `free_bytes` — Dung lượng trống trên volume chứa `path` (tạo parent nếu chưa có). — L41
- `estimate_split_need_bytes` — Ước lượng chỗ cần cho split copy-mode (= gần bằng size nguồn + margin). — L50
- `assert_enough_space_for_split` — (no docstring) — L56
- `_unlink_quiet` — (no docstring) — L66
- `probe_duration` — Lấy thời lượng video tính bằng giây. — L74
- `calculate_part_plan` — Tính toán danh sách (start_sec, end_sec) cho từng part. — L90
- `find_best_cut_point` — Tìm điểm khoảng lặng (silence) gần nhất với target_cut_sec trong phạm vi ±search_radius_sec. — L111
- `compute_smart_plan` — Tính plan hoàn chỉnh có điểm cắt thông minh (tránh đứt câu thoại). — L152
- `split_video_to_parts` — Cắt video thành các part theo smart plan (lossless copy). — L194
- `_hardlink_alias` — Tạo alias cùng inode với primary. Không bao giờ copy2 (tránh nhân đôi GB). — L331
- `cleanup_split_parts_dir` — Xoá thư mục `_split_parts` dở (orphan GB sau fail / ENOSPC). — L361
- `merge_parts_to_full` — Nối danh sách các part đã render hoàn chỉnh thành 1 file full (lossless copy 30s). — L373
- `split_job_to_subjobs` — Tự động chia một job video dài thành các sub-jobs (Part 1, Part 2...). — L412
- `merge_job_parts` — Kiểm tra các sub-job của job_id, nếu tất cả đã render xong thì ghép thành output_full.mp4. — L576
- `is_split_subjob` — Part đã tách (…_p01) — không auto-split lần nữa. — L675
- `maybe_auto_split_job` — Tự detect thời lượng video sau khi có source: — L688
- `try_auto_merge_parent` — Sau khi một part mux xong: nếu mọi part done → merge output_full trên job cha. — L792
- `main` — (no docstring) — L818

### engines/subs.py
- `_plain_len` — (no docstring) — L27
- `_mask_number_dots` — Che dấu nghìn trong số để không bị tách câu tại «3.000» / «31,000». — L49
- `_unmask_number_dots` — (no docstring) — L55
- `glue_vi_names` — Dán NBSP trong tên riêng — không xuống dòng giữa «Thiên Lang Tinh». — L101
- `unglue_vi_names` — (no docstring) — L113
- `_is_compound_break` — True nếu cắt tại pos đang tách đôi compound (…tấn| công…). — L117
- `_snap_cut_to_vi_word` — Ưu tiên cắt tại khoảng trắng VI; không cắt giữa từ / giữa số / compound. — L131
- `_snap_cut_outside_number` — Đẩy điểm cắt ra ngoài token số (tránh «31.» + «000 tỷ»). — L154
- `split_text_by_punct` — Tách câu theo dấu câu. weak=True: mỗi mệnh đề sau ，、, là 1 đoạn (thoại TTS). — L165
- `_join_clause` — CJK dính liền; VI/Latin cần khoảng trắng («Đù,» + «thế…» → «Đù, thế…»). — L212
- `_is_punct_only` — (no docstring) — L222
- `_split_for_display` — Tách text cho sub: dấu câu -> dấu phẩy; hard=True thì cắt cứng phần còn dài. — L226
- `_slice_contiguous` — Cắt 1 chuỗi thành N đoạn liên tiếp theo trọng số — không trộn với câu khác. — L263
- `merge_tiny_segments` — Gộp mảnh ASR vụn: chỉ dấu câu, cắt giữa từ, clip < 0.45s quá ngắn. — L314
- `_merge_parts` — Gộp parts dư thành đúng n cụm (ghép các cụm ngắn nhất liên tiếp). — L360
- `_expand_parts` — Chia parts ít hơn n thành đủ n cụm. — L379
- `_align_zh_vi` — Căn số cụm zh/vi; ưu tiên zh làm mốc thời gian. — L397
- `_spread_time_pairs` — Chia [start,end] theo độ dài vi (fallback zh). — L410
- `_split_hard` — Cắt cứng theo từ (Việt) hoặc ký tự (CJK) khi không còn dấu câu. — L433
- `split_long_segments` — Tách câu quá dài / quá lâu thành nhiều đoạn; chia thời gian theo độ dài chữ. — L527
- `split_bilingual_rows` — Sau dịch ZH→VI: tách sub dài (CUT). Ưu tiên cắt theo VI rồi cắt ZH liền mạch. — L571
- `carry_tail_fragments` — «…sáu mươi đứa. Đúng,» + «cùng lên…» → mảnh đầu câu sau sang cue kế tiếp. — L727
- `merge_broken_vi_number_rows` — Gộp mảnh lệch số: «…31,» + «000 tỷ» / «当前血量31,» + «000亿» → 1 câu. — L755
- `heal_script_broken_numbers` — Gộp số gãy trên script (giữ i của câu đầu) — trả (rows_mới, số_cặp_đã_gộp). — L799
- `sub_split_cfg` — (no docstring) — L805
- `_merge_short_orphans` — Gộp đuôi ngắn («này?», «Tinh,») — không nuốt lại «nhiều.» / «trường,». — L813
- `wrap_subtitle_text` — Gói phụ đề tối đa max_lines dòng, mỗi dòng ≤ max_chars. — L857
- `_wrap_cfg` — (no docstring) — L942
- `expand_placed_with_display` — Tách mỗi câu TTS (script 1:1) theo mảnh CUT trong script.display (src_i). — L949
- `_maybe_wrap` — (no docstring) — L1017
- `fmt_ts` — Giây (float) -> 'HH:MM:SS,mmm' theo chuẩn SRT. — L1029
- `to_srt` — Đổ list câu ra chuỗi SRT. Bỏ câu rỗng, đánh số lại liên tục. — L1040
- `to_srt_fit` — SRT burn theo script + dur TTS gốc (KHÔNG biết đàn hồi assemble). — L1056
- `to_srt_placed` — SRT burn khớp giọng sau assemble_fit: dùng start/end thật trên dub_fit.wav. — L1084

### engines/title_mt.py
- `_has_cjk` — (no docstring) — L30
- `_load_cache` — (no docstring) — L34
- `_save_cache` — (no docstring) — L51
- `_gtx` — (no docstring) — L64
- `translate_one` — Dịch 1 title; không CJK → trả nguyên. — L87
- `translate_titles` — Dịch list {series_id?, title} → gắn title_vi. Dùng cache. — L103

### engines/translate.py
- `_tmodel` — TRANSLATE_MODEL đọc lúc gọi (server import module 1 lần — MODEL ở trên bị đóng băng). — L59
- `_rmodel` — (no docstring) — L64
- `_is_llama_local_model` — (no docstring) — L68
- `_meaning_rules` — Quy tắc chống dịch đen / lệch ngữ cảnh (lồng tiếng phim). — L84
- `_style_rules` — Quy tắc Manhua / short-drama: cứng Hán Việt + mềm hiện đại + xưng hô. — L147
- `_character_rules` — Chống nhầm nhân vật / sai giới tính khi dịch thoại. — L179
- `_is_ancient_fantasy_genre` — True khi phương án/genre thuộc tu tiên·cổ trang·wuxia·xianxia (không mixed đô thị). — L201
- `_is_mixed_genre` — (no docstring) — L225
- `_mixed_address_rules` — Đô thị dị năng + võ/KH: xưng hô hiện đại + cổ phong Hán Việt. — L239
- `_ancient_address_rules` — Chỉ inject khi genre tu tiên/cổ — không áp cho đô thị hiện đại. — L260
- `_translate_rules` — Gộp nghĩa + văn phong + nhân vật (+ xưng hô theo genre). — L281
- `_ocr_name_hints` — Tên/chữ trên hình từ ocr.json (nếu có) — gợi ý cho PLAN. — L290
- `_resolve_translate_mode` — Trả 'oneshot' | 'batch'. — L317
- `_has_cjk` — Còn ký tự Hán trong bản dịch = model dịch sót/hỏng (đặc biệt model nhỏ local). — L345
- `_salvage_mixed_vi` — Cứu VI lẫn Hán (vd «Đạt được 100% 增幅.») — không thì trả '' để vá lại. — L373
- `build_plan` — LLM đọc toàn transcript -> phương án dịch: nhân vật, thuật ngữ, XƯNG HÔ, PHÂN CẢNH, tone. — L420
- `_plan_block` — Đổ plan ra text nhét vào mọi prompt dịch. CHỐNG LỖI: model đôi khi trả — L588
- `_plan_block_for_qa` — Plan block gọn cho pronoun-QA / GPT vá đỏ — chỉ genre+style+pronouns. — L700
- `_resolve_scene_context` — Xác định phân cảnh hiện tại của lô câu thoại (Scene-based context injection). — L774
- `_norm_zh_cue` — Chuẩn hóa cue ZH để khớp lock (bỏ dấu câu/space). — L867
- `ensure_hard_terms` — Gắn seed chengyu/taunt vào glossary.terms (không đè bản tay đã có). — L875
- `hard_term_lock_map` — zh_norm → vi bắt buộc (từ glossary type chengyu/idiom/combat_taunt/lock + seed). — L925
- `apply_hard_term_locks` — Post-pass: cue ZH khớp lock → ghi đè VI (chuẩn, không phụ thuộc LLM). — L964
- `normalize_vi_thousands` — Dấu nghìn chuẩn Việt: 31 000 / 31,000 → 31.000. — L1011
- `apply_style_polish` — Post-pass deterministic: sửa calque / văn mẫu thường gặp (mixed short-drama). — L1027
- `_is_modernish_genre` — Đô thị / mixed / hiện đại — cấm Ta–Ngươi cổ. — L1278
- `_char_aliases` — vi_name_lower → {zh, vi, aliases…} để khớp tên trong câu. — L1302
- `_pronoun_pairs` — (no docstring) — L1320
- `_detox_modern_pronouns` — Ép Ta/Ngươi → Tôi/Cậu cho thoại đô thị (giữ «ông ta/cô ta/chúng ta»). — L1336
- `apply_pronoun_postpass` — Post-pass deterministic xưng hô — không phụ thuộc LLM nhớ ma trận. — L1362
- `_salvage_items` — Vớt từng object {"i":.., "vi":..} kể cả khi JSON TỔNG THỂ hỏng (model — L1428
- `translate_oneshot` — Dịch TOÀN BỘ danh sách câu trong 1 lần gọi LLM (llama-server ctx lớn). — L1453
- `translate_batch` — LƯỢT 1 — DỊCH NGHĨA KỊCH BẢN CHUẨN XÁC (Semantic Accuracy) theo Phân Cảnh (Scene) + Series Glossary. Trả {i: vi}. — L1521
- `_translate_safe` — Dịch 1 lô CÓ CHỐNG LỖI: nếu parse hỏng hoặc LLM nuốt câu, CHIA ĐÔI lô rồi thử lại. — L1596
- `review_batch` — LƯỢT 2 — BẢN ĐỊA HÓA LỜI THOẠI LỒNG TIẾNG & KHỚP NHỊP PHỤ ĐỀ (Voice Dubbing Localization). — L1624
- `run_review` — LƯỢT 2: soát bản dịch nháp (script.json) bằng model chính xác (minimax) rồi — L1697
- `count_script_missing` — Đếm câu trống trong script.json (nguồn sự thật cho UI / auto-vá). — L1894
- `_trivial_vi` — Câu chỉ cười/thán từ — không cần LLM (model hay trả lại chữ Hán → _has_cjk xoá). — L1906
- `_compress_zh_for_llm` — Rút chuỗi cười/spam trước khi gửi LLM (tránh timeout / trả Hán). — L1947
- `clean_zh_spam` — Rút 哈/呃/嗯/啊 spam + cụm chữ lặp (区域的区域的…) từ ASR. — L1952
- `run_translate` — (no docstring) — L1989
- `main` — (no docstring) — L2502

### engines/translate_alts.py
- `_heuristic_ambiguous` — Trả lý do ngắn nếu câu nên đưa phương án; None = bỏ qua. — L35
- `_alts_batch` — Trả {i: {alts[], pick, reason}} — tối ưu theo ngữ cảnh + văn phong. — L65
- `run_ambiguous_alts` — Quét script → vi_alts.json (phương án tối ưu theo ngữ cảnh + văn phong). — L164
- `analyze_pack_report` — Checklist pack Context Studio có đủ để dịch chunk không. — L305
- `main` — (no docstring) — L353

### engines/vram.py
- `_ollama_loaded` — (no docstring) — L14
- `_stop_ollama` — (no docstring) — L27
- `_empty_torch` — Xả cache CUDA — KHÔNG synchronize (dễ treo vô hạn khi GPU kẹt). — L38
- `free_gpu_vram` — Stop Ollama + xả torch cache. An toàn gọi nhiều lần, kể cả không có GPU. — L56

---

## 4. http_routes / agents / pineline.server.routes

### Atoms: http_routes / agents / pineline.server.routes

Module-level functions and class methods only (nested defs skipped).

### http_routes/__init__.py
- (none)

### http_routes/routes_agent.py
- `def _agent_get_job` (L77)
- `def _agent_queue_add` (L84)
- `def _agent_edit_line` (L90)
- `def _agent_set_hold` (L101)
- `def _agent_get_hold` (L128)
- `def _agent_run_stage` (L136)
- `def _agent_stop_job` (L155)
- `def _agent_tts_set_voice` (L165)
- `def _agent_mux_run` (L179)
- `def _agent_asr_set_engine` (L201)
- `def _job_in_pipeline` (L211)
- `def _agent_script_review` (L218)
- `def _agent_resume` (L265)
- `def api_agent_review` (L297)
- `def api_agent_resume` (L302)
- `def _agent_script_review_legacy` (L306)
- `def _agent_heal_stale` (L320)
- `def _agent_translate_fill` (L329)
- `def _agent_translate_rerun` (L339)
- `def _agent_tts_run_simple` (L349)
- `def _agent_mux_retry` (L353)
- `def _agent_asr_force` (L357)
- `def _agent_assemble_fit` (L361)
- `def _agent_mux_force_av` (L369)
- `def _agent_reset_state` (L379)
- `def _agent_notify` (L403)
- `def api_agent_status` (L435)
- `def api_agent_chat` (L444)
- `def api_agent_pending` (L470)
- `def api_agent_confirm` (L475)
- `def api_agent_scan_failed` (L496)
- `def api_agent_heal_failed` (L506)
- `def api_agent_review_diff` (L531)
- `def api_agent_qa_gate` (L540)
- `def api_agent_reset_state` (L559)
- `def api_agent_watch_once` (L569)
- `def api_agent_av_sync` (L588)
- `def api_agent_av_sync_heal` (L597)
- `def api_agent_av_sync_scan` (L615)
- `def api_agent_av_sync_heal_batch` (L626)
- `class AgentHealBatchReq` (L484)
- `class AgentQaGateReq` (L490)
- `class AgentResetStateReq` (L552)
- `class AgentAvSyncHealReq` (L583)
- `class AgentAvSyncScanReq` (L607)

### http_routes/routes_films.py
- `def _get_base_url` (L25)
- `def films_ui` (L31)
- `def list_films` (L39)
- `def export_films_csv` (L68)
- `def get_film` (L93)
- `def sync_films` (L101)
- `def delete_films` (L110)
- `def purge_missing` (L126)
- `def check_block_films` (L133)
- `def check_block_all` (L146)
- `def get_library` (L160)
- `def library_accounts` (L169)
- `def library_action` (L178)
- `def library_set_block_status` (L198)
- `def library_clear_samples` (L207)
- `def library_cut_sample` (L216)
- `def library_enqueue_test` (L227)
- `def library_test_url` (L239)
- `def library_scan_queue` (L249)
- `def tc_status` (L262)
- `def tc_reset_quota` (L267)
- `def tc_recheck_health` (L272)
- `def tc_auth_url` (L278)
- `def tc_callback` (L289)
- `def tc_finish_auth` (L311)
- `def tc_disconnect` (L323)
- `def tc_test_one` (L329)
- `def tc_batch_start` (L341)
- `def tc_batch_progress` (L351)
- `def tc_recheck_one` (L356)
- `def tc_recheck_pending` (L363)

### http_routes/routes_hg.py
- `def _hg_base` (L51)
- `def _hg_err` (L57)
- `def hg_ping` (L69)
- `def hg_search` (L77)
- `def hg_resolve` (L90)
- `def hg_baike_search` (L107)
- `def hg_baike_info` (L122)
- `def hg_web_search` (L169)
- `def hg_series` (L192)
- `def hg_status` (L203)
- `def hg_cancel` (L214)
- `def hg_submit` (L225)
- `def hg_rank` (L236)
- `def hg_rank_episodes` (L255)
- `def hg_translate_titles` (L271)
- `def hg_library` (L283)
- `def hg_preview` (L294)
- `def hg_library_preview` (L310)
- `def hg_img` (L335)
- `def hg_poster` (L352)
- `def hg_merge` (L369)
- `def hg_merge_queue` (L381)
- `def hg_merge_queue_clear` (L387)
- `def hg_library_open` (L393)
- `def hg_library_delete` (L403)
- `def hg_library_update` (L416)
- `def hg_seasons_decline` (L429)
- `def meta_generate` (L443)
- `def meta_generate_title` (L462)
- `def meta_thumbnail` (L493)
- `def meta_thumbnail_get` (L523)
- `def meta_series_info` (L535)
- `def meta_ai_image` (L552)
- `def meta_baike` (L585)
- `class HgRankEpsIn` (L249)
- `class HgTranslateTitlesIn` (L266)

### http_routes/routes_ui.py
- `def find_index` (L29)
- `def index` (L43)
- `def ui3` (L56)
- `def ui4` (L62)
- `def _html_file` (L67)
- `def ui_hongguo` (L81)
- `def ui_hongguo2` (L86)
- `def ui_workflow` (L92)

### http_routes/routes_uploader_settings.py
- `def get_all_settings` (L47)
- `def update_settings` (L107)
- `def test_telegram_msg` (L154)
- `def test_llm_conn` (L190)
- `def _is_yt_uploader_running` (L234)
- `def _read_upload_history` (L252)
- `def _read_upload_queue` (L271)
- `def _write_upload_queue` (L282)
- `def get_uploader_status` (L293)
- `def enqueue_upload` (L329)
- `def remove_upload_item` (L376)
- `def clear_done_uploads` (L398)
- `def launch_yt_uploader_process` (L408)
- `def auto_publish_get_config` (L435)
- `def auto_publish_save_config` (L442)
- `def auto_publish_trigger` (L450)
- `def auto_publish_scan` (L464)
- `def auto_publish_status` (L476)
- `def canva_status` (L487)
- `def canva_auth_url` (L500)
- `def canva_callback` (L511)
- `def canva_save_config` (L539)
- `def canva_create` (L551)

### agents/__init__.py
- (none)

### agents/agent_autopilot.py
- `def _now` (L25)
- `def load_state` (L32)
- `def save_state` (L51)
- `def update_state` (L55)
- `def set_enabled` (L64)
- `def _get` (L82)
- `def _post` (L88)
- `def queue_opts` (L106)
- `def _opts_differ` (L114)
- `def sync_pending_to_batch` (L125)
- `def status_brief` (L175)
- `def tick_once` (L195)
- `def agent_chat` (L259)
- `def agent_confirm` (L281)
- `def hard_stop` (L285)
- `def format_status` (L320)

### agents/agent_av_sync.py
- `def _ffprobe_dur` (L22)
- `def _rms_at` (L40)
- `def _tts_fit_stats` (L70)
- `def _mux_meta` (L101)
- `def diagnose_av_sync` (L116)
- `def _hint` (L328)
- `def _invalidate_mixed` (L342)
- `def _quick_gap` (L356)
- `def scan_av_sync` (L385)
- `def heal_av_sync` (L456)
- `def heal_av_sync_batch` (L525)

### agents/agent_core.py
- `def _films_tool` (L852)
- `def _sidecar_cmd` (L866)
- `def _truthy` (L919)
- `def tool_tier` (L923)
- `def describe_action` (L954)
- `def _prune_pending` (L962)
- `def park_action` (L967)
- `def pending_actions` (L982)
- `def confirm_action` (L988)
- `def bind` (L1035)
- `def _require_rt` (L1040)
- `def summarize_job` (L1046)
- `def _load_script` (L1076)
- `def _line_brief` (L1086)
- `def _read_hold` (L1097)
- `def script_peek` (L1114)
- `def script_search` (L1136)
- `def script_get_lines` (L1163)
- `def classify_jobs` (L1179)
- `def default_yt_draft` (L1207)
- `def _dispatch` (L1247)
- `def _llm_cfg` (L1640)
- `def _chat_turn` (L1647)
- `def _chat_turn_model` (L1665)
- `def _chat_turn_text_protocol` (L1697)
- `def _parse_pycall_tool_calls` (L1772)
- `def _parse_text_tool_calls` (L1818)
- `def clip_tool_result` (L1859)
- `def run_agent` (L1874)
- `def status_snapshot` (L1950)
- `class Runtime` (L1008)
- `class AgentResult` (L1867)

### agents/agent_error_class.py
- `def classify_error` (L52)
- `def classify_stage_status` (L85)
- `def filter_actions_by_class` (L105)

### agents/agent_feeder.py
- `def _now_s` (L54)
- `def _today` (L58)
- `def load_state` (L64)
- `def save_state` (L83)
- `def normalize_spec` (L89)
- `def describe_spec` (L120)
- `def _get` (L145)
- `def _post` (L151)
- `def _hg` (L157)
- `def _job_manifests` (L162)
- `def _norm` (L177)
- `def imported_paths` (L181)
- `def lib_root` (L191)
- `def _match` (L206)
- `def library` (L213)
- `def candidates` (L246)
- `def _db_series_info` (L309)
- `def group_score` (L326)
- `def _season_no` (L363)
- `def _probe_dur` (L368)
- `def process_ratio` (L389)
- `def _translate` (L412)
- `def library_view` (L426)
- `def library_action` (L544)
- `def _probe_stream_meta` (L693)
- `def _concat_videos_smart` (L725)
- `def _sanitize_folder_name` (L863)
- `def combine_library_seasons` (L868)
- `def _fmt_srt_ts` (L1021)
- `def combine_rendered_jobs` (L1030)
- `def pick` (L1210)
- `def _have` (L1221)
- `def _existing_group` (L1227)
- `def add_jobs` (L1235)
- `def _merge_busy` (L1276)
- `def _hg_status` (L1284)
- `def _downloading_sids` (L1291)
- `def mergeable` (L1303)
- `def hongguo_pick` (L1320)
- `def prefetch` (L1352)
- `def pipeline_idle` (L1392)
- `def feed_tick` (L1399)
- `def preview` (L1434)
- `def _llm_cfg` (L1473)
- `def _extract_json` (L1480)
- `def parse_request_llm` (L1486)
- `def parse_request_rules` (L1510)
- `def set_request` (L1541)
- `def _server_tree_cpu` (L1560)
- `def _job_activity` (L1592)
- `def _running_stage` (L1607)
- `def _running_jobs` (L1618)
- `def _fmt_dur` (L1632)
- `def _requeue_front` (L1638)
- `def runwatch_tick` (L1654)
- `def running_text` (L1731)
- `def lib_verb` (L1779)
- `def _fold` (L1785)
- `def lib_key` (L1791)
- `def _lib_find` (L1796)
- `def _lib_line` (L1815)
- `def _lib_buttons` (L1823)
- `def _lib_detail` (L1837)
- `def lib_command` (L1853)
- `def lib_callback` (L1923)

### agents/agent_heal.py
- `def _mf` (L17)
- `def _stage` (L27)
- `def _count_missing_vi` (L31)
- `def _tts_missing` (L44)
- `def diagnose_job` (L62)
- `def heal_job` (L239)
- `def _job_needs_attention` (L344)
- `def scan_problem_jobs` (L358)
- `def heal_failed_batch` (L411)
- `def reset_job_state` (L469)

### agents/agent_hongguo.py
- `def detect_flow_mode` (L34)
- `def _find_hongguo_executable` (L44)
- `def ensure_hongguo_running` (L62)
- `def tool_hg_search` (L108)
- `def _norm_lb_cat` (L158)
- `def load_leaderboard` (L167)
- `def load_catalog` (L189)
- `def _enrich_page` (L224)
- `def _item_dict` (L248)
- `def tool_hg_rank` (L257)
- `def tool_hg_catalog` (L272)
- `def tool_hg_genres` (L290)
- `def _mark` (L299)
- `def render_view` (L303)
- `def render_genre_picker` (L365)
- `def view_callback` (L380)
- `def page_covers` (L400)
- `def cache_pick` (L421)
- `def resolve_series_ref` (L429)
- `def watch_url` (L453)
- `def preview_info` (L457)
- `def download_preview` (L494)
- `def render_watch_page` (L519)
- `def tool_hg_preview` (L555)
- `def tool_hg_download` (L586)
- `def tool_hg_status` (L608)
- `def tool_hg_library` (L638)
- `def tool_hg_merge` (L666)
- `def tool_hg_clean` (L692)
- `def _pick_lib_item` (L723)
- `def _get_existing_pineline_titles` (L746)
- `def tool_hg_series` (L769)
- `def tool_hg_auto_flow` (L889)
- `def handle_hongguo_tool` (L1473)
- `def running_auto_flows` (L1520)
- `def start_auto_flow_bg` (L1525)

### agents/agent_name_pass.py
- `def _fold` (L20)
- `def _names` (L25)
- `def find_issues` (L38)
- `def _fix_batch` (L53)
- `def run_name_pass` (L76)

### agents/agent_pronoun_pass.py
- `def _fold` (L22)
- `def find_pronoun_issues` (L27)
- `def _fix_batch` (L92)
- `def run_pronoun_pass` (L123)

### agents/agent_qa_gate.py
- `def _now` (L11)
- `def _load_rows` (L15)
- `def snapshot_pre_review` (L25)
- `def review_diff` (L34)
- `def _fail_reasons` (L106)
- `def evaluate_qa_gate` (L119)
- `def run_qa_gate` (L123)
- `def set_qa_gate` (L185)

### agents/agent_stage_io.py
- `def _mf` (L9)
- `def _stage` (L19)
- `def _file_info` (L23)
- `def _sample_list` (L33)
- `def peek_download` (L72)
- `def peek_asr` (L97)
- `def peek_translate` (L117)
- `def peek_tts` (L138)
- `def peek_ocr` (L166)
- `def peek_mux` (L181)
- `def peek_stage` (L215)
- `def peek_all` (L223)
- `def peek_style_pack` (L230)
- `def json_dump` (L285)

### agents/agent_tele_cmd.py
- `def _load_history_from_disk` (L83)
- `def _save_history_to_disk` (L95)
- `def get_user_history` (L111)
- `def add_user_history` (L122)
- `def clear_user_history` (L135)
- `def _ensure_agent_telegram` (L142)
- `def tg_send` (L148)
- `def tg_api` (L153)
- `def allowed_uids` (L168)
- `def tg_send_video` (L173)
- `def send_preview` (L197)
- `def send_covers` (L241)
- `def _edit_or_send` (L280)
- `def spawn_preview` (L292)
- `def _parse_catalog_args` (L301)
- `def hg_tele_command` (L328)
- `def _send_confirm_buttons` (L553)
- `def _agent_ask` (L567)
- `def _confirm_callback` (L579)
- `def _slash_hint` (L601)
- `def handle_command` (L635)
- `def _agent_reply` (L855)
- `def _fetch_poster_bytes` (L867)
- `def autopilot_loop` (L1745)
- `def filmdb_loop` (L1771)
- `def runwatch_loop` (L1836)
- `def feeder_loop` (L1848)
- `def _sync_and_report` (L1866)
- `def config_watch_loop` (L1878)
- `def _inline_kb` (L1895)
- `def _on_callback` (L1900)
- `def telegram_loop` (L1994)
- `def is_priority_cmd` (L2046)
- `def _tg_worker` (L2052)
- `def _handle_tg_text` (L2064)
- `def _single_instance_lock` (L2099)
- `def main` (L2115)
- `class CtrlHandler` (L905)
  - `def log_message` (L906)
  - `def _is_local` (L910)
  - `def _blocked` (L917)
  - `def _cors` (L938)
  - `def _json` (L946)
  - `def do_OPTIONS` (L955)
  - `def do_GET` (L962)
  - `def do_POST` (L1255)
- `class _ExclusiveHTTPServer` (L2089)
  - `def server_bind` (L2093)

### agents/agent_watch.py
- `def _log_dir` (L32)
- `def log_line` (L38)
- `def _state_path` (L49)
- `def _load_state` (L53)
- `def _save_state` (L63)
- `def _cooldown_sec` (L72)
- `def _skip_prefixes` (L79)
- `def _should_skip_job` (L84)
- `def _fingerprint` (L89)
- `def _load_dotenv` (L95)
- `def telegram_config` (L111)
- `def telegram_send` (L133)
- `def _gpu_busy` (L163)
- `def _filter_problems` (L186)
- `def _mark_healed` (L214)
- `def watch_once` (L226)
- `def _loop` (L325)
- `def start_watcher` (L342)
- `def stop_watcher` (L374)

### agents/auto_publisher.py
- `def get_auto_state` (L60)
- `def update_auto_state` (L83)
- `def _read_publish_queue` (L106)
- `def _write_publish_queue` (L116)
- `def _enqueue_job_record` (L124)
- `def _dequeue_job_record` (L176)
- `def _sync_queue_state_badge` (L191)
- `def touch_active_locks` (L203)
- `def is_pid_alive` (L214)
- `def get_job_lock_path` (L231)
- `def acquire_job_lock` (L239)
- `def release_job_lock` (L277)
- `def acquire_global_publish_lock` (L293)
- `def release_global_publish_lock` (L349)
- `def is_any_job_uploading` (L365)
- `def is_job_uploading` (L390)
- `def load_config` (L408)
- `def save_config` (L429)
- `def get_youtube_service` (L438)
- `def format_youtube_title` (L456)
- `def upload_to_youtube` (L510)
- `def _revert_job_to_done` (L629)
- `def enqueue_publish` (L655)
- `def _drain_publish_queue_async` (L680)
- `def _is_yt_upload_limit_error` (L694)
- `def _drain_publish_queue_loop` (L704)
- `def publish_job` (L749)
- `def _publish_job_internal` (L827)
- `def _collect_and_enqueue_done_jobs` (L1191)
- `def scan_and_publish_completed_jobs` (L1252)
- `def _scan_and_publish_impl` (L1311)
- `def _auto_publish_worker_loop` (L1353)
- `def start_worker` (L1364)
- `def stop_worker` (L1375)

### agents/canva_client.py
- `def load_config` (L31)
- `def save_config` (L47)
- `def load_token` (L66)
- `def save_token` (L81)
- `def is_connected` (L88)
- `def generate_auth_url` (L93)
- `def exchange_code` (L142)
- `def refresh_access_token` (L179)
- `def _get_auth_headers` (L203)
- `def upload_asset` (L212)
- `def import_design_from_image` (L269)
- `def create_youtube_thumbnail` (L322)

### agents/hongguo_bridge.py
- `def _save_merge_state` (L67)
- `def _load_merge_state` (L82)
- `def _set_phase` (L106)
- `def season_stem` (L121)
- `def franchise_core` (L136)
- `def _parse_cn_int` (L147)
- `def season_timeline_key` (L167)
- `def order_franchise_items` (L188)
- `def web_search_hongguoduanju` (L271)
- `def _ingest_web_into` (L334)
- `def web_expand_queries` (L363)
- `def web_expand_into` (L389)
- `def _load_title_cache` (L419)
- `def _save_title_cache` (L437)
- `def lookup_series` (L447)
- `def resolve_text` (L463)
- `def _cache_put` (L496)
- `def _fill_missing_from_cache` (L511)
- `def expand_queries` (L549)
- `def _base_port` (L579)
- `def _read_process_env_win` (L589)
- `def _hongguo_pids` (L645)
- `def discover_ui_token` (L663)
- `def _auth_headers` (L696)
- `def _is_ui_auth_error` (L707)
- `def _req` (L718)
- `def ping` (L773)
- `def search` (L809)
- `def status` (L936)
- `def cancel` (L940)
- `def submit` (L944)
- `def library_update` (L954)
- `def seasons_decline` (L961)
- `def rank` (L968)
- `def genres` (L1023)
- `def catalog` (L1040)
- `def rank_episodes` (L1104)
- `def preview_series` (L1113)
- `def library` (L1127)
- `def _output_dir` (L1155)
- `def inspect_series_folder` (L1164)
- `def safe_child` (L1205)
- `def resolve_preview_path` (L1220)
- `def resolve_poster_path` (L1233)
- `def fetch_poster` (L1248)
- `def fetch_img_proxy` (L1286)
- `def _trash_root` (L1339)
- `def purge_trash` (L1348)
- `def merged_covers_fragments` (L1374)
- `def _move_to_trash` (L1410)
- `def cleanup_fragments` (L1424)
- `def _list_episode_frags` (L1456)
- `def _probe_wh` (L1472)
- `def _probe_dur` (L1494)
- `def _frame_wh_at` (L1507)
- `def _pick_h264_encoder` (L1533)
- `def _scale_vf` (L1550)
- `def episode_resolutions` (L1558)
- `def merged_has_mixed_res` (L1580)
- `def normalize_merged_file` (L1612)
- `def merge_series_normalized` (L1686)
- `def mark_done` (L1774)
- `def merge_one` (L1784)
- `def merge_status` (L1791)
- `def open_library` (L1795)
- `def delete_library_series` (L1800)
- `def merge_resume` (L1878)
- `def merge_queue_state` (L1895)
- `def merge_queue_add` (L1917)
- `def merge_queue_clear` (L1960)
- `def _start_worker` (L1969)
- `def _finish` (L1980)
- `def _merge_worker` (L1995)
- `def _hist` (L2241)
- `def _baike_get` (L2265)
- `def _baike_clean_title` (L2271)
- `def _titles_same_franchise` (L2278)
- `def baike_search` (L2301)
- `def baike_info` (L2357)
- `def baike_deep` (L2548)
- `def baike_versions` (L2587)
- `def _norm_title_key` (L2640)
- `def _hongguo_match_version` (L2647)
- `def search_via_baike` (L2743)

### agents/meta_studio.py
- `def to_series_slug` (L30)
- `def clean_series_name` (L42)
- `def hooks_from_series_title` (L78)
- `def _hook_anchored_to_title` (L115)
- `def sanitize_hook_texts` (L125)
- `def pick_badge_text` (L150)
- `def vi_to_image_latin` (L164)
- `def build_master_image_prompt` (L181)
- `def finalize_thumb_meta_fields` (L243)
- `def get_series_key` (L294)
- `def get_series_meta` (L332)
- `def save_series_meta` (L373)
- `def get_series_thumbnail` (L390)
- `def save_series_thumbnail` (L429)
- `def _build_fallback_part_meta` (L447)
- `def get_film_story_info` (L515)
- `def generate_youtube_titles` (L626)
- `def generate_title_only` (L786)
- `def generate_part_metadata` (L792)
- `def _clean_json_response` (L921)
- `def _get_chatgpt_token` (L989)
- `def extract_job_summary` (L1000)
- `def _normalize_ref_jpeg` (L1096)
- `def _extract_best_video_frame` (L1115)
- `def get_job_reference_images` (L1157)
- `def _call_chatgpt` (L1232)
- `def _decode_aurora_image_response` (L1292)
- `def generate_ai_image` (L1309)
- `def generate_metadata` (L1436)
- `def create_thumbnail` (L1679)

### pineline/server/routes/__init__.py
- (none)

### pineline/server/routes/assets.py
- `def attach` (L24)

### pineline/server/routes/fs.py
- `def attach` (L15)

### pineline/server/routes/jobs.py
- `def attach` (L62)

### pineline/server/routes/queue.py
- `def attach` (L29)

## Counts

- Files: 29
- Module-level functions: 558
- Classes: 11
- Class methods: 9
- Total callables (funcs + methods): 567

### Per file

- `http_routes/__init__.py`: funcs=0, classes=0, methods=0
- `http_routes/routes_agent.py`: funcs=40, classes=5, methods=0
- `http_routes/routes_films.py`: funcs=31, classes=0, methods=0
- `http_routes/routes_hg.py`: funcs=34, classes=2, methods=0
- `http_routes/routes_ui.py`: funcs=8, classes=0, methods=0
- `http_routes/routes_uploader_settings.py`: funcs=23, classes=0, methods=0
- `agents/__init__.py`: funcs=0, classes=0, methods=0
- `agents/agent_autopilot.py`: funcs=16, classes=0, methods=0
- `agents/agent_av_sync.py`: funcs=11, classes=0, methods=0
- `agents/agent_core.py`: funcs=30, classes=2, methods=0
- `agents/agent_error_class.py`: funcs=3, classes=0, methods=0
- `agents/agent_feeder.py`: funcs=65, classes=0, methods=0
- `agents/agent_heal.py`: funcs=10, classes=0, methods=0
- `agents/agent_hongguo.py`: funcs=36, classes=0, methods=0
- `agents/agent_name_pass.py`: funcs=5, classes=0, methods=0
- `agents/agent_pronoun_pass.py`: funcs=4, classes=0, methods=0
- `agents/agent_qa_gate.py`: funcs=8, classes=0, methods=0
- `agents/agent_stage_io.py`: funcs=14, classes=0, methods=0
- `agents/agent_tele_cmd.py`: funcs=37, classes=2, methods=9
- `agents/agent_watch.py`: funcs=19, classes=0, methods=0
- `agents/auto_publisher.py`: funcs=34, classes=0, methods=0
- `agents/canva_client.py`: funcs=12, classes=0, methods=0
- `agents/hongguo_bridge.py`: funcs=84, classes=0, methods=0
- `agents/meta_studio.py`: funcs=30, classes=0, methods=0
- `pineline/server/routes/__init__.py`: funcs=0, classes=0, methods=0
- `pineline/server/routes/assets.py`: funcs=1, classes=0, methods=0
- `pineline/server/routes/fs.py`: funcs=1, classes=0, methods=0
- `pineline/server/routes/jobs.py`: funcs=1, classes=0, methods=0
- `pineline/server/routes/queue.py`: funcs=1, classes=0, methods=0

---

## 5. tools / desktop / UI JS

### Atoms: tools / desktop / restart + static UI JS

- **Date:** 2026-11-06
- **Scope:** module-level funcs via AST in `tools/**/*.py`, `app_desktop.py`, `restart_server.py`; JS names via regex on `static/ui/{index3,films_ui,hongguo,hongguo2,workflow}.html`
- **JS regex:** `function\s+(\w+)|(?:async\s+)?(\w+)\s*=\s*(?:async\s*)?\(`
- **JS note:** unique names, keyword false-positives skipped; cap **200** per file

## Counts

| Bucket | Files | Functions |
|---|---:|---:|
| Python (module-level) | 17 | 100 |
| HTML JS (unique names) | 5 | 634 |
| **Combined** | **22** | **734** |

- Cap hit (200): `static/ui/index3.html`

### Per-file counts

| File | Count |
|---|---:|
| `app_desktop.py` | 4 |
| `restart_server.py` | 8 |
| `tools/__init__.py` | 0 |
| `tools/context_studio/__init__.py` | 0 |
| `tools/context_studio/__main__.py` | 1 |
| `tools/context_studio/address_lexicon.py` | 4 |
| `tools/context_studio/analyzer.py` | 5 |
| `tools/context_studio/app_streamlit.py` | 0 |
| `tools/context_studio/character_mapper.py` | 10 |
| `tools/context_studio/exporter.py` | 1 |
| `tools/context_studio/schema.py` | 3 |
| `tools/context_studio/srt_io.py` | 4 |
| `tools/lib_check.py` | 9 |
| `tools/migrate_work.py` | 12 |
| `tools/pick_dirs_dialog.py` | 4 |
| `tools/preset_switcher.py` | 4 |
| `tools/test_channel.py` | 31 |
| `static/ui/index3.html` | 200 |
| `static/ui/films_ui.html` | 117 |
| `static/ui/hongguo.html` | 153 |
| `static/ui/hongguo2.html` | 156 |
| `static/ui/workflow.html` | 8 |

## Python — module-level functions (AST)

### `app_desktop.py` (4)

- L36: `def is_port_open`
- L44: `def start_backend`
- L78: `def wait_for_server`
- L87: `def main`

### `restart_server.py` (8)

- L61: `def _manifest_opts`
- L69: `def _tg`
- L78: `def _proc_env`
- L87: `def _precheck`
- L100: `def _requeue`
- L115: `def _start_server`
- L136: `def _restart_sidecar`
- L145: `def main`

### `tools/__init__.py` (0)

- _(none)_

### `tools/context_studio/__init__.py` (0)

- _(none)_

### `tools/context_studio/__main__.py` (1)

- L20: `def main`

### `tools/context_studio/address_lexicon.py` (4)

- L195: `def address_bank`
- L235: `def style_lock_policy`
- L265: `def merge_unique`
- L277: `def enrich_style_lock`

### `tools/context_studio/analyzer.py` (5)

- L12: `def _heuristic_analyze`
- L99: `def _sample_lines`
- L129: `def _llm_analyze`
- L245: `def analyze`
- L252: `def summarize`

### `tools/context_studio/app_streamlit.py` (0)

- _(none)_

### `tools/context_studio/character_mapper.py` (10)

- L27: `def _lock_mode`
- L43: `def _plausible_name`
- L48: `def _char_key`
- L52: `def _ensure_char`
- L86: `def infer_roles_from_segments`
- L150: `def build_relation_pronouns`
- L177: `def _matrix_from_pronouns`
- L192: `def sanitize_pronouns`
- L239: `def enrich_characters`
- L331: `def validate_pronouns`

### `tools/context_studio/exporter.py` (1)

- L9: `def write_pack`

### `tools/context_studio/schema.py` (3)

- L14: `def scan_number_flags`
- L51: `def empty_glossary_skeleton`
- L78: `def apply_style_lock_from_genre`

### `tools/context_studio/srt_io.py` (4)

- L14: `def _ts_to_sec`
- L19: `def parse_srt`
- L57: `def parse_asr_json`
- L78: `def load_segments`

### `tools/lib_check.py` (9)

- L30: `def resolve_title_vi`
- L74: `def find_source_video`
- L90: `def cut_sample`
- L168: `def add_to_yt_queue`
- L236: `def test_library_by_url`
- L265: `def scan_all_lib_from_yt_queue`
- L330: `def clear_samples`
- L357: `def list_yt_accounts`
- L379: `def batch_enqueue_untested_lib`

### `tools/migrate_work.py` (12)

- L42: `def log`
- L55: `def tg`
- L64: `def robocopy`
- L78: `def api`
- L86: `def api_retry`
- L99: `def running_stages`
- L115: `def procs`
- L124: `def kill_with_parent_cmd`
- L157: `def start_bat`
- L164: `def wait_http`
- L175: `def start_services_and_requeue`
- L200: `def main`

### `tools/pick_dirs_dialog.py` (4)

- L14: `def _nat_key`
- L19: `def _count_videos`
- L35: `def _list_children`
- L47: `def main`

### `tools/preset_switcher.py` (4)

- L30: `def get_active_preset`
- L55: `def list_available_presets`
- L75: `def is_model_ready`
- L125: `def switch_preset`

### `tools/test_channel.py` (31)

- L37: `def _safe_resolve_title_vi`
- L96: `def _utc_now`
- L100: `def _utc_now_plus_minutes`
- L104: `def _today_utc`
- L112: `def get_channel_limit_state`
- L125: `def mark_channel_limit_reached`
- L136: `def get_projects_health`
- L146: `def update_project_health`
- L160: `def verify_all_projects_health`
- L237: `def get_exhausted_projects`
- L246: `def mark_project_exhausted`
- L252: `def reset_exhausted_projects`
- L268: `def list_projects`
- L314: `def get_today_uploads_count`
- L389: `def get_status`
- L417: `def disconnect`
- L430: `def get_auth_url`
- L482: `def finish_oauth`
- L574: `def get_available_service`
- L606: `def get_read_service`
- L627: `def get_youtube_service`
- L635: `def upload_test_sample`
- L703: `def delete_test_video`
- L725: `def wait_and_check_test_video`
- L813: `def recheck_single`
- L892: `def check_and_process_pending_rechecks`
- L922: `def start_recheck_daemon`
- L944: `def run_full_test_for_season`
- L1045: `def _batch_worker`
- L1158: `def start_batch_test`
- L1187: `def get_batch_progress`

## HTML — JS function names (regex)

### `static/ui/index3.html` (200)

- `fmtSize`, `hhmm`, `parseUrls`, `updateUrlCount`
- `addJob`, `id`, `fpRenderSel`, `fpClearSel`
- `fpRemoveAt`, `fpSetPaths`, `pickMultiFolders`, `cur`
- `addSelectedFolders`, `target`, `nf`, `first`
- `addLocalPath`, `raw`, `addLocalFile`, `onload`
- `onerror`, `applyComposeUi`, `openQueue`, `setJobMode`
- `showCompose`, `closeCompose`, `select`, `toggleListSel`
- `jrow`, `start`, `moveBtns`, `renderList`
- `listStructSig`, `patchJrow`, `need`, `sortGroupSeries`
- `groupJobs`, `seasonOf`, `toggleGroup`, `groupSelected`
- `addSelectedToGroup`, `m`, `ungroupSelected`, `renameGroup`
- `dissolveGroup`, `mergeAllSeries`, `skip`, `defaultStep`
- `stages`, `selectStep`, `shellMidOk`, `autoBarHtml`
- `asrE`, `ttsE`, `logShellHtml`, `patchOneStep`
- `patchStepsShell`, `patchLogData`, `renderDetail`, `qh`
- `model`, `patchDetailLive`, `textContent`, `width`
- `fillAutoVoices`, `eng`, `list`, `autoEngineChanged`
- `e`, `panelSig`, `patchPanelLive`, `renderPanel`
- `stageCtrl`, `hasPartial`, `trD`, `ttsD`
- `asrD`, `dlD`, `mark`, `stepRow`
- `rawSt`, `isAsrSep`, `asrN`, `splitNote`
- `mini`, `buildLog`, `toggleLog`, `feedSentences`
- `toggle`, `loadArtifact`, `muxDone`, `durSec`
- `loadDynamicModels`, `isSel`, `artTranslate`, `zh`
- `runContextStudio`, `pollContextStudio`, `tick`, `showContextStudio`
- `chars`, `terms`, `tblTrans`, `ii`
- `initTransColResize`, `syncRail`, `tw`, `startDrag`
- `pct`, `up`, `focusMissLine`, `lineEditFocus`
- `lineEditInput`, `lineEditKey`, `lineEditSave`, `val`
- `orig`, `cleanZhSpam`, `viEditFocus`, `viEditInput`
- `viEditKey`, `viEditSave`, `artTts`, `clipRow`
- `ttsShowAll`, `fillTranslate`, `artOcr`, `artSeparate`
- `audioModeOptions`, `artMux`, `resLbl`, `fillMuxFrames`
- `files`, `fillMuxLogos`, `fillAutoFrames`, `fillAutoLogos`
- `muxModeChanged`, `display`, `autoPrefLoad`, `autoPrefSave`
- `autoPrefApply`, `autoPrefBind`, `queueBatchPush`, `v`
- `flushBatchPush`, `_btnFlash`, `loadBatchCfg`, `markPerJobDiff`
- `saveBatchCfg`, `autoAudioChanged`, `duck`, `loadVoices`
- `curEngine`, `curAsrEngine`, `st`, `saveAsrEngine`
- `asrEngineChanged`, `fillVoices`, `saveTtsEngine`, `engineChanged`
- `doTranslate`, `trMode`, `trModel`, `muxJob`
- `audio_mode`, `add_sub`, `fit`, `resolution`
- `flip`, `zVal`, `zoom`, `motion`
- `lut`, `grain`, `brand_mode`, `brand_text`
- `brand_logo`, `frame`, `vbitrate`, `regenClip`
- `assembleJob`, `spd`, `fn`, `cloneVoice`
- `name`, `msg`, `previewVoice`, `onended`
- `oncanplay`, `regenTts`, `fillTts`, `uploadAudio`
- `removeAudio`, `uploadSource`, `importSourcePath`, `path`
- `revealJob`, `splitJobParts`, `mergeJobParts`, `guardAct`

### `static/ui/films_ui.html` (117)

- `toast`, `tab`, `loadLib`, `stateLabel`
- `groupBlockBadge`, `formatRecheckTime`, `seasonBlockBadge`, `renderLib`
- `fBlock`, `openTestBlockModal`, `updateTestModalBadge`, `doModalRecheck`
- `closeTestBlockModal`, `doSkipCurrentLib`, `deleteLocalSeason`, `deleteEntireSeriesLocal`
- `deleteBlockedSeasonsOfCore`, `doDeleteCurrentLocalLib`, `doCutSample`, `doEnqueueSample`
- `doCheckTestUrl`, `setManualBlockStatus`, `checkTestChannelStatus`, `upBadge`
- `textContent`, `renderProjectsList`, `openTestChannelModal`, `closeTestChannelModal`
- `resetProjectQuota`, `avail`, `total`, `recheckTestChannelHealth`
- `startTestChannelOAuth`, `pollForTestChannelAuth`, `submitTestChannelCode`, `disconnectTestChannel`
- `testCheckedPrompt`, `startPinelineTestAllPrompt`, `doStartBatchTest`, `updateBatchProgressUI`
- `startBatchProgressPolling`, `poll`, `triggerRecheckPending`, `recheckOneSeason`
- `doPinelineDirectTestOne`, `clearSamplesCachePrompt`, `scanLibraryBlocks`, `act`
- `onSeriesPickChange`, `togglePickAllSeries`, `clearSeriesSelection`, `updateSeriesSelection`
- `addCheckedUnified`, `addCheckedSeries`, `addChecked`, `priorityCheckedSeries`
- `skipCheckedSeries`, `load`, `checkSingleBlock`, `batchCheckBlockPrompt`
- `checkAllUploadedBlock`, `promptDeleteSingle`, `batchDeletePrompt`, `closeDelModal`
- `execDeleteModal`, `promptPurge`, `purgeMissing`, `syncDb`
- `togglePickAll`, `clearPickAll`, `updateBatchBar`, `openMetaModal`
- `doRegenIndividualThumb`, `closeMetaModal`, `selectHookOpt`, `txt`
- `doFetchBaikeInfo`, `q`, `doGenerateMeta`, `doRenderThumbnail`
- `doCopyGptPrompt`, `copyText`, `copyThumbUrl`, `checkCanvaStatus`
- `openCanvaModal`, `closeCanvaModal`, `saveAndAuthCanva`, `doCreateCanvaDesign`
- `loadUploader`, `onUpAccountChange`, `onUpFilePicked`, `renderUploaderQueue`
- `renderUploaderHistory`, `submitEnqueueUpload`, `removeUploadItem`, `clearDoneUploads`
- `launchUploader`, `openPickFilmModal`, `renderPickFilmList`, `pickFilmForUpload`
- `openSettingsModal`, `closeSettingsModal`, `switchSettingsTab`, `loadSettings`
- `saveSettings`, `testLlmConn`, `testTelegramMsg`, `loadAutoPublishConfig`
- `saveAutoPublishConfig`, `triggerAutoPublishScan`, `quickUploadJob`, `buildIntegratedMasterPrompt`
- `badge`, `sub`, `doGenerateAuroraAiThumb`, `CURRENT_THUMB_URL`
- `pollAutoPubState`

### `static/ui/hongguo.html` (153)

- `exQ`, `jget`, `jpost`, `loadDlQueueFromStorage`
- `saveDlQueueToStorage`, `updateQueueBadges`, `onResCheckboxChange`, `bindResCheckboxes`
- `_qHandler`, `switchLeftTab`, `leftTab`, `hidden`
- `setRankBoard`, `rankBoard`, `reloadHotPane`, `setRankCat`
- `renderHotCards`, `loadRank`, `ensureExGenres`, `chips`
- `onclick`, `loadCatalog`, `fetchExplorer`, `items`
- `fillRankEpisodes`, `applyTitleVi`, `closeDetail`, `openBaikeDetailFromCard`
- `openBaikeDetail`, `tags`, `rel`, `setDetailRelChecked`
- `enqueueDetailMain`, `enqueueDetailRelated`, `dlDetailMain`, `dlDetailRelated`
- `ping`, `seasonStem`, `t`, `franchiseCore`
- `parseCnInt`, `s`, `seasonTimelineKey`, `cmpTimeline`
- `orderFranchiseItems`, `titleMark`, `formatTitleHtml`, `previewFromItem`
- `enqueueGroup`, `renderSeriesItem`, `mergeSeeds`, `expandQueries`
- `x`, `clientExpandSearch`, `ingest`, `addByPaste`
- `raw`, `item`, `stem`, `doSearch`
- `rejected`, `groups`, `toggleGroup`, `pickGroup`
- `selectAllVisible`, `selectedIds`, `updateDlBtn`, `dlGroup`
- `doDownload`, `doCancel`, `renderQueueList`, `removeFromDlQueue`
- `clearDlQueue`, `startDlQueue`, `_dlStatusSig`, `clearDlStatus`
- `applyDock`, `toggleDock`, `_dlLineTs`, `renderLog`
- `lsnHint`, `lsnTake`, `lsnItems`, `lsnList`
- `lsnN`, `lsnEps`, `lsnName`, `lsnMeta`
- `lsnBigAll`, `lsnBigAlbums`, `lsnGroups`, `lsnBusy`
- `lsnSugPill`, `lsnPlain`, `lsnAutoPill`, `lsnBadgeCount`
- `lsnUpdateBadge`, `lsnRender`, `lsnScores`, `lsnSubmit`
- `lsnDecline`, `lsnRefresh`, `lsnUpdateAll`, `lsnClick`
- `refreshStatus`, `textContent`, `dlLogLines`, `_loadLibSel`
- `_saveLibSel`, `_rememberLibSel`, `refreshLibrary`, `badge`
- `busy`, `mergeOneBtn`, `_pvEls`, `_pvMsg`
- `_pvStopCdn`, `_pvStopLib`, `_pvShape`, `_pvTabs`
- `previewLib`, `openPreview`, `openLibPreview`, `onloadedmetadata`
- `previewCatalog`, `openCatalogPreview`, `pvLoadCdn`, `onload`
- `closePreview`, `selectLib`, `selectLibPending`, `syncLibSelectAll`
- `libSelected`, `mergeNames`, `skip`, `mergeSelected`
- `deleteLibOne`, `deleteLibSelected`, `libPath`, `loadJobIndex`
- `vp`, `jobFor`, `jobLog`, `addJobs`
- `names`, `addJobsSelected`, `mergeAllLibrary`, `clearMergeQ`
- `refreshMerge`, `q`, `pct`, `mergeHist`
- `refreshAll`

### `static/ui/hongguo2.html` (156)

- `exQ`, `jget`, `jpost`, `loadDlQueueFromStorage`
- `saveDlQueueToStorage`, `updateQueueBadges`, `setCtaStatus`, `onResCheckboxChange`
- `bindResCheckboxes`, `_qHandler`, `switchLeftTab`, `setDiscoverMode`
- `discoverMode`, `setOpsQueue`, `opsQueue`, `hidden`
- `setRankBoard`, `reloadHotPane`, `setRankCat`, `renderHotCards`
- `loadRank`, `ensureExGenres`, `chips`, `onclick`
- `loadCatalog`, `fetchExplorer`, `items`, `fillRankEpisodes`
- `applyTitleVi`, `closeDetail`, `openBaikeDetailFromCard`, `openBaikeDetail`
- `tags`, `rel`, `setDetailRelChecked`, `enqueueDetailMain`
- `enqueueDetailRelated`, `dlDetailMain`, `dlDetailRelated`, `ping`
- `seasonStem`, `t`, `franchiseCore`, `parseCnInt`
- `s`, `seasonTimelineKey`, `cmpTimeline`, `orderFranchiseItems`
- `titleMark`, `formatTitleHtml`, `previewFromItem`, `enqueueGroup`
- `renderSeriesItem`, `mergeSeeds`, `expandQueries`, `x`
- `clientExpandSearch`, `ingest`, `addByPaste`, `raw`
- `item`, `stem`, `doSearch`, `rejected`
- `groups`, `toggleGroup`, `pickGroup`, `selectAllVisible`
- `selectedIds`, `updateDlBtn`, `dlGroup`, `doDownload`
- `doCancel`, `renderQueueList`, `removeFromDlQueue`, `clearDlQueue`
- `startDlQueue`, `_dlStatusSig`, `clearDlStatus`, `applyDock`
- `toggleDock`, `_dlLineTs`, `renderLog`, `lsnHint`
- `lsnTake`, `lsnItems`, `lsnList`, `lsnN`
- `lsnEps`, `lsnName`, `lsnMeta`, `lsnBigAll`
- `lsnBigAlbums`, `lsnGroups`, `lsnBusy`, `lsnSugPill`
- `lsnPlain`, `lsnAutoPill`, `lsnBadgeCount`, `lsnUpdateBadge`
- `lsnRender`, `lsnScores`, `lsnSubmit`, `lsnDecline`
- `lsnRefresh`, `lsnUpdateAll`, `lsnClick`, `refreshStatus`
- `textContent`, `dlLogLines`, `_loadLibSel`, `_saveLibSel`
- `_rememberLibSel`, `refreshLibrary`, `badge`, `busy`
- `mergeOneBtn`, `_pvEls`, `_pvMsg`, `_pvStopCdn`
- `_pvStopLib`, `_pvShape`, `_pvTabs`, `previewLib`
- `openPreview`, `openLibPreview`, `onloadedmetadata`, `previewCatalog`
- `openCatalogPreview`, `pvLoadCdn`, `onload`, `closePreview`
- `selectLib`, `selectLibPending`, `syncLibSelectAll`, `libSelected`
- `mergeNames`, `skip`, `mergeSelected`, `deleteLibOne`
- `deleteLibSelected`, `libPath`, `loadJobIndex`, `vp`
- `jobFor`, `jobLog`, `addJobs`, `names`
- `addJobsSelected`, `mergeAllLibrary`, `clearMergeQ`, `refreshMerge`
- `q`, `pct`, `mergeHist`, `refreshAll`

### `static/ui/workflow.html` (8)

- `resizeCanvas`, `drawCanvas`, `spacing`, `addLog`
- `selectStage`, `resetSimulation`, `startSimulation`, `runNextStep`

---

## 6. How to navigate — muốn hiểu X thì mở Y

| Muốn hiểu… | Mở |
|---|---|
| Toàn bộ hàm theo file (core/server) | [§2 core + server](#2-coreserverpy--per-function) |
| Toàn bộ hàm engines | [§3 engines](#3-engines--per-function) |
| HTTP routes + agents + pineline.server.routes | [§4 http / agents](#4-httproutes--agents--pinelineserverroutes) |
| tools / desktop / restart + UI JS | [§5 tools + UI](#5-tools--desktop--ui-js) |
| **Thứ tự gọi thật khi chạy 1 job** | [§1 Spine](#1-spine-gọi-từng-hàm) |
| Tạo job từ URL | `server.create_job` → `_create` → `engines.download.job_id_from_url` |
| Hàng chờ persist | `core/job_queue.py` (`queue_add`, `_worker_loop`, `_save`) |
| Orchestrator queue | `server._queue_run_one` |
| 1-click không qua queue | `server._auto_pipeline` → `_auto_gpu` |
| GPU stage chain | `server._auto_gpu` |
| Download | `engines/download.py` `download_video` |
| ASR engine map | `server.ASR_SCRIPTS` / `_asr_script` / `_run_engine` |
| Dịch | `engines/translate.py` `run_translate` (spawn qua `_run_translate_engine`) |
| TTS | `server._do_tts` → `engines/clone_tts.run_clone_tts` |
| Ghép giọng | `engines/assemble.py` `assemble` / `assemble_fit` |
| Render cuối | `server._do_render` → `engines/render.run_render` (không phải `mux.run_mux`) |
| Chia/ghép part dài | `engines/split_parts.py` (`maybe_auto_split_job`, `try_auto_merge_parent`) |
| HOLD / QA trước TTS | `server._auto_gpu` + `agents/agent_qa_gate.py` |
| Atom map (file → I/O → next) | [2026-11-06-v5-part-atoms.md](./2026-11-06-v5-part-atoms.md) |
| Layout thư mục / ports | `docs/LAYOUT.md`, `docs/ARCHITECTURE.md` |
| Contract manifest | `docs/MANIFEST_CONTRACT.md` |
