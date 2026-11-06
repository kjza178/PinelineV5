# Changelog

Mới nhất trên cùng. Mỗi mục: file/hàm — thay đổi — cần restart gì. Chi tiết bug: docs/fixes/. Nhật ký phiên: docs/worklog/.

## 2026-11-06

- **SAFE autofix eng-swarm** (~15:45). Backup `Z:\PinelineV2_codebak\2026-11-06_v5-swarm-autofix\`. Port ENOSPC/`DiskFullError`/`assert_enough_space` + no re-encode-on-disk-full + cleanup mid-split từ V2 → `engines/split_parts.py`; `_AUTO_SPLIT_ACTIVE` + `_maybe_auto_split_guarded` trong `server.py`; default `PORT=8805`; uploader `WORK_DIR`/`TEMP` → `D:\PinelineV5_work`/`D:\PinelineV5_tmp`. Tests `tests/test_split_enospc_guard.py`. Fix `docs/fixes/2026-11-06-v5-enospc-port.md`. **Không restart** (user); nạp khi restart :8805 sau.

- **Eng-swarm docs index** (~15:40). `docs/reviews/README.md` (link eng-swarm + part-atoms); `docs/ARCHITECTURE.md` section *Engineering swarm* → `.cursor/skills/v5-eng-swarm`. **Không restart**.

- **V5 part atoms review** (~15:36). `docs/reviews/2026-11-06-v5-part-atoms.md` — finest-grain map entry/core/HTTP/pipeline/agents/UI/data (atom→file→fn→side effect). **Không restart**.

- **Pronoun-QA slim plan (Aurora 413)** (~15:30). Backup `Z:\PinelineV2_codebak\2026-11-06_pronoun-qa-slim\`. `engines/translate._plan_block_for_qa`; `engines/pronoun_consistency` + `agents/agent_pronoun_pass` slim; `engines/llm._chatgpt_chat` no-retry 400/413/422. Sync V2/V4. Fix `docs/fixes/2026-11-06-pronoun-qa-413-slim.md`. **Cần restart :8805** khi nạp module (chưa restart nếu không running).

- **Hongguo2 Ops hẹp** (~15:16). Sync `static/ui/hongguo2.html` từ V2: Discover rộng, Ops capped ~380px. **Hard refresh `/hongguo2`** (không restart).

- **Hongguo2 review pass** (~08:30). Sync `static/ui/hongguo2.html` từ V2 (CTA enqueue-only, `#results` scope, catalog-hint/cta-status, busy guards, UX). Fix `docs/fixes/2026-11-06-hongguo2-review.md`. **Hard refresh `/hongguo2`** (không restart).

- **Hongguo2 redesign** (~08:20). Backup `Z:\PinelineV2_codebak\2026-11-06_0818_hongguo2\`. Thêm `static/ui/hongguo2.html` (IA 2 cột Discover|Ops). Route `GET /hongguo2` → `ui_hongguo2` trong `http_routes/routes_ui.py` + re-export `server.py`. Link «Thử Hongguo2» trên `static/ui/hongguo.html`. Sync V2/V4. **Restart :8805** để nạp route; hard refresh `/hongguo2`.

- **Hongguo New seasons board** (~08:00). Backup `Z:\PinelineV2_codebak\2026-11-06_hg-new-seasons\`. `agents/hongguo_bridge`: `submit(scores=)` + `library_update`/`seasons_decline`; `http_routes/routes_hg` `/api/hg/library/update` + `/seasons/decline`; `HgSubmitIn.scores`; UI `static/ui/hongguo.html` tab 🆕 Mùa mới. Sync V2/V4. Fix `docs/fixes/2026-11-06-hg-new-seasons.md`. **Hard refresh `/hongguo`**; **restart :8805** nếu cần nạp bridge/routes.

- **Merge no-dup output** (~03:00). Backup `Z:\PinelineV2_codebak\2026-11-06_merge-no-dup-output\`. `engines/split_parts.merge_job_parts`: ghi 1 lần `output.mp4`; `output_full` chỉ hardlink (`_hardlink_alias`, không `copy2`); cleanup `_split_parts`. Sync V2/V4. Fix `docs/fixes/2026-11-06-merge-no-dup-output.md`. **Restart :8805** để nạp merge mới (job đã merge không cần remux).

## 2026-11-05

- **Split voice queue_opts** (~21:40). `_resolve_voice`/speed/tts_engine đọc `queue_opts` trước list[0]; `split_job_to_subjobs` seed `stages.tts` + `tts_config`. Backup `Z:\PinelineV2_codebak\2026-11-05_split-voice-queue-opts\`. Fix `docs/fixes/2026-11-05-split-voice-queue-opts.md`. **Restart :8805** để nạp (chưa restart).

- **Auto-split conflict guards** (~21:20). Backup `Z:\PinelineV2_codebak\2026-11-05_autosplit-conflict-guards\`. `server.py` + `engines/split_parts.maybe_auto_split_job`: skip merged / mux-done; promote cùng nguồn không invalidate TTS. Sync V2/V4. Fix `docs/fixes/2026-11-05-autosplit-conflict-guards.md`. **Restart :8805** để nạp.

- **Restore Tauri desktop V5** (~04:25–04:30). Backup `Z:\PinelineV2_codebak\2026-11-05_restore-tauri\`. Copy từ archive → root (`src-tauri/`, `package.json`, `run_tauri.bat`…). Branding V5 / `devUrl` `:8805`; thêm `build.rs`, `capabilities/default.json`, `desktop/tauri_www/`; `run_tauri.bat` tự start `server.py` nếu chưa có cổng. `npm i` + `cargo check` OK. Archive giữ làm đối chiếu. **Không restart** servers; mở app: `run_tauri.bat`.

- **UI3 stale `?job=` clear** (~01:15). `refresh`: clear selection khi job không còn trong list (không chỉ khi detail 404). Sync V2/V4/V5. **Không restart** (hard refresh).
- **UI3 404/stages sync → V2/V4** (~01:09). Logic đã có trên `static/ui/index3.html`; sync `renderDetail`/`refresh` guards sang V2+V4 root `index3.html`. Backup `Z:\PinelineV2_codebak\2026-11-05_ui3-404-stages\`. Fix `docs/fixes/2026-11-05-ui3-404-stages.md`. **Không restart** (hard refresh).

- **Upload limit stop-queue** (~00:43). Backup `Z:\PinelineV2_codebak\2026-11-05_upload-limit-stop\`. Port từ V2: `_is_yt_upload_limit_error`; `publish_job` finally không dequeue/drain khi `stop_queue`; drain loop break; `_publish_job_internal` trả `upload_limit_exceeded`+`stop_queue`. Test `tests/test_upload_limit_stop.py`. Fix `docs/fixes/2026-11-05-upload-limit-stop-queue.md`. **Không restart** (user).

- **V5 `core/` package** (~00:05). Backup codebak `Z:\PinelineV2_codebak\2026-11-05_v5-core\` + zip `Z:\PinelineV2_backup_2026-11-05_0005.zip` (snapshot script). Move kernel → `core/`: `config`, `batch_config`, `job_queue`, `job_meta`, `film_db`, `manifest`, `fileio` (ROOT/`WORK_ROOT` = `parents[1]`; inter-import relative). Rewrite call sites → `import core.X as X` / `from core.X import …` (không shim root). `restart_server.CHECK_MODULES` → `core/*.py` (+ job_meta/film_db). Tests/LAYOUT/ARCHITECTURE/unity skill. Root còn 3 entry: `server.py`, `app_desktop.py`, `restart_server.py`. **Chờ restart :8805** (parent).

## 2026-11-04

- **V5 structure unity** (~23:55). Backup codebak `Z:\PinelineV2_codebak\2026-11-04_v5-unity\`. Docs-first: LAYOUT/ARCHITECTURE/README/`pineline`/`http_routes`/DECISIONS/STATE + design `2026-11-04-v5-structure-unity.md` — app core = 10 root `.py`; attach registries LIVE; bodies ở `http_routes/`. Xoá TARGET shells rỗng: `pineline/{agents,pipeline,sidecar,desktop,ops,server/services}`. Harden `tests/test_layout_paths.py`. **Không restart :8805** (docs + empty dirs only).

- **V5 restart :8805 Phase F** (~23:50). `PORT=8805 restart_server.py --ignore-hg --clean-env`; PID 27296→38920. Smoke `/` `/films/ui` `/api/queue/jobs` `/api/voices` 200; queue idle. **Không cần restart thêm.**

- **V5 layout Phase F** (~23:46). Backup zip `Z:\PinelineV2_backup_2026-11-04_2346.zip` + codebak `Z:\PinelineV2_codebak\2026-11-04_v5-layout-F\`. F1: `scripts/install/` (+ reqs sibling), `scripts/check_cookies.py`, `work/logs/migrate_work.log`, xoá root `__pycache__`, archive `finetune_xuyenthanh` / legacy `config.json` / `.claude`+`.superpowers` → `scripts/archive/…`; `config/` cho preset JSON (giữ `pineline.config.json` root; `.nvenc_state.json` root). F2: package `tools/` — `lib_check`, `test_channel`, `preset_switcher`, `pick_dirs_dialog`, `migrate_work`, `context_studio/`; rewrite imports (no shim); `server` spawn `tools/pick_dirs_dialog.py`; `restart_server` CHECK_MODULES + `tools.migrate_work`. **Đã restart :8805** 23:50 (PID 38920).

- **V5 layout Phase E** (~22:30). Backup codebak `Z:\PinelineV2_codebak\2026-11-04_v5-layout-E\` (+ zip `Z:\PinelineV2_backup_2026-11-04_2224.zip`). Rewrite flat import → `engines.*` / `engines.asr.*` / `agents.*` / `http_routes.*` (codemod ~362); CLI: `ASR_SCRIPTS` + `_run_engine("engines/translate.py")`, `sfx_lib` self-spawn `Path(__file__)`, `apps/run_tele_cmd.bat` → `python -m agents.agent_tele_cmd`, `restart_server` CHECK_MODULES/SMOKE package paths. Xoá **58** root shim; root còn **17** `.py`. Tests: layout assert shims gone; patch targets `agents.*`/`engines.*`; `ASR_USE_DEMUCS=1` trong demucs test. Smoke OpenAPI 177. **Không restart :8805** (parent). SKIP: `test_restart_guard` + check_batch4 sidecar lock (pre-existing).

- **V5 batch-check + README layout** (~21:15). Backup codebak `Z:\PinelineV2_codebak\2026-11-04_v5-layout-sync\`. `scripts/check_batch{1,2}` ROOT=`Path(__file__).resolve().parents[1]` (không còn `Z:\PinelineV2`); batch2 UI → `static/ui/index3.html`, AST/source `agents/`+`engines/`; batch1 AST `agents/`, tmp `D:\PinelineV5_tmp`; batch3/4 đã `parents[1]` (batch4 comment V5). README mô tả `apps/agents/http_routes/engines/static/ui`. **Không restart :8805.**

- **V5 layout Phase D** (~21:10). Backup codebak `Z:\PinelineV2_codebak\2026-11-04_v5-layout-D\` (+ zip `Z:\PinelineV2_backup_2026-11-04_2105.zip`). Move 22 pipeline engines → `engines/` flat + root shims (`importlib` + `sys.modules` alias; shim `importlib.import_module("engines")` trước load để `reload` OK). Path `parents[1]` cho `render`/`render_fx`/`sfx_lib`/`clone_tts`/`series_glossary`/`llm`/`title_mt`. `scripts/check_batch3` đọc `engines/render.py`+`engines/llm.py`. Test: `import download,translate,render,…` OK; `import server` OpenAPI 177; pytest core layout+queue+render/sfx/pronoun 55 OK; full suite 117 pass / 4 fail pre-existing (restart_guard, batch2/4 V2). **Không restart :8805.** SKIP: không.

- **V5 layout Phase C** (~21:05). Backup codebak `Z:\PinelineV2_codebak\2026-11-04_v5-layout-C\`. Move 14 ASR modules → `engines/asr/` (+ root shims); `firered_asr._roots` vendor path `parents[2]`. Giữ `download`/`translate`/`render` ở root (Phase D). Verify `import asr, fun_asr_nano, hybrid_asr`; pytest layout+queue 9 OK. **Không restart :8805.**

- **V5 Phase B verify + thumb root** (~21:02). Backup zip `…_2101.zip` + codebak `…_v5-layout-B-fix\`. Fix `routes_hg.meta_thumbnail_get` → project `data/thumbnails` (`parent.parent`). Tests `tests/test_layout_paths.py` (find_index cwd=`C:\Windows`, films_ui, openapi `/`+`/films/ui`). Pytest 9 OK. Fix `docs/fixes/2026-11-04-http-routes-thumb-root.md`. **Không restart :8805.**

- **V5 layout Phase B** (~20:51). Backup codebak `Z:\PinelineV2_codebak\2026-11-04_v5-layout-B\`. Move `agent_*.py` + `hongguo_bridge`/`auto_publisher`/`meta_studio`/`canva_client` → `agents/`; `routes_*.py` → `http_routes/`; root shims (`sys.modules` alias) giữ `import agent_core` / `import routes_ui`. `server.py` re-export cycle-safe; `router = APIRouter()` trước `import server`. ROOT/`_HERE` → project root (`parent.parent`). Pytest 5 OK. **Không restart :8805.**

- **V5 layout Phase A** (~20:50). Backup zip `Z:\PinelineV2_backup_2026-11-04_2048.zip` + codebak `Z:\PinelineV2_codebak\2026-11-04_v5-layout-A\`. HTML → `static/ui/`; launchers → `apps/` + root stubs; archive `run_v4`/V4.spec → `scripts/archive/v4/`; root markdown junk → `docs/archive_root/`; `static/app.js` → `scripts/archive/ui_legacy/`; `restart_server`/`migrate_work` default `run_v5.bat`. **Restart :8805** (parent).

- **V5 cleanup plan + auditor skills** (~19:50). Skills `.cursor/skills/v5-{structure-auditor,deadcode-hunter,ops-docs-auditor}`; design `docs/design/2026-11-04-v5-structure-cleanup.md`; plan `docs/superpowers/plans/2026-11-04-v5-codebase-cleanup.md`. **Không restart** (docs/skills only).

- **V5 assets/fs attach** (~19:45). Backup `Z:\PinelineV2_codebak\2026-11-04_v5-assets-fs-attach\`. Strip 10 `@app` (cookies/voices/frames/brand/clone/voice-sample/models/llm/fs); `assets`/`fs` registry + `include_router`. Oneshots → `scripts/archive/oneshot/`; xoá `tauri_desktop/node_modules`. Follow-up `docs/fixes/2026-11-04-v5-queue-ssot.md`. **Restart :8805.**

- **V5 queue/jobs SSOT + gọn codebase** (~19:00). Backup `Z:\PinelineV2_codebak\2026-11-04_v5-queue-ssot\`. `pineline.server.routes.queue` → registry `attach` (xoá body trùng); wire `queue`+`jobs` `include_router`; strip `@app` queue/jobs; `job_queue.current_detail` / `build_queue_items` / `http_queue_state` (queue_state không còn N× `get_job_info` rời). Docs: `MANIFEST_CONTRACT.md`, ARCHITECTURE, routes README, DECISIONS. Fix `docs/fixes/2026-11-04-v5-queue-ssot.md`. **Restart :8805.**

- **Queue meta từ films.db** (17:30, V5 only). Backup `Z:\PinelineV2_codebak\2026-11-04_v5-film-db-queue\`. Cột `series_ui`/`season_ui`/`group_index`; `job_meta.py`; `get_jobs_info` DB-first; `/api/queue/jobs` bỏ N× manifest pending. Fix `docs/fixes/2026-11-04-film-db-queue-meta.md`. **Restart :8805.**

- **Queue sort/move** (16:57). Backup `Z:\PinelineV2_codebak\2026-11-04_queue-sort-move\`. UI gọi `/api/queue/jobs/sort|move`; season ưu tiên «Phần N» trên title; `job_sort_key` dùng `group_id`/series normalize. Sync V2/V4/V5 (`job_queue.py` + `index3.html`). Fix `docs/fixes/2026-11-04-queue-sort-move.md`. **Restart :8801** (+ hard refresh UI).

- **Title YT cấm tên nhân vật** (05:36). Backup `Z:\PinelineV2_codebak\2026-11-04_title-no-charname\`. Prompt: chỉ premise/hệ thống/«Ta» — không Hứa Hoa/Lão Lục…. Sync V2/V4/V5. **Restart** nếu meta in-process.

- **Title YT công thức Premise + Ta** (04:20). Backup `Z:\PinelineV2_codebak\2026-11-04_title-prompt-ta\`. `generate_youtube_titles`: `Phần N | PREMISE: HOOK, Ta PAYOFF` (user mẫu xuyên không / thức tỉnh / Ta…). Sync V2/V4/V5. Dump `docs/prompts/title_youtube_prompt_filled.txt`. **Restart** nếu meta in-process.

- **Thumb Latin + title YT prompt** (04:05). Backup `Z:\PinelineV2_codebak\2026-11-04_thumb-latin-title\`. `vi_to_image_latin` — chữ nung ảnh ASCII không dấu; `generate_youtube_titles` CTR bám Baike, cấm template/sáo. Sync V2/V4/V5. Fix follow-up `docs/fixes/2026-11-04-thumb-hardcoded-prompt.md`. **Restart :8801/:8804/:8805** nếu auto-publish/meta in-process; regener title+thumb job cũ nếu cần.

- **Thumb: badge NEW/HOT, giữ AI typography** (03:55). Backup `Z:\PinelineV2_codebak\2026-11-04_thumb-prompt-fix\`. Bỏ scene-only/Pillow; AI vẫn nung chữ 3D; cấm badge «TRỌN BỘ THUYẾT MINH»; hook neo tên. Sync V2/V4/V5. Fix `docs/fixes/2026-11-04-thumb-hardcoded-prompt.md`. **Restart server** nếu auto-publish in-process; regener thumb cũ nếu cần.

- **Hardsub hở theo thời gian** (00:29). Backup `Z:\PinelineV2_codebak\2026-11-04_hardsub-gap-fill\`. Job `50ba645d468b` track chỉ che ~42% (OCR miss). Wire `HARDSUB_FIXED_BOTTOM`; full-cover ratio 0.40; gap-fill. Sync V2/V4/V5. Fix `docs/fixes/2026-11-04-hardsub-temporal-gaps.md`. **Restart :8801/:8804/:8805 + remux** (đang TTS Mùa 5 trên :8801 — hỏi trước khi restart).

- **Hardsub che hở 2 mép** (00:10). Backup `Z:\PinelineV2_codebak\2026-11-04_hardsub-fullw\`. OCR x0/x1 ~52% → ép full ngang + pad dọc; sync V2/V4/V5. Fix `docs/fixes/2026-11-04-hardsub-partial-cover.md`. **Remux job** (không cần restart nếu CLI; server mux cần restart :8801/:8804/:8805).

## 2026-11-03

- **Split parent false-failed** (16:00). Backup `Z:\PinelineV2_codebak\2026-11-03_split-parent-done\`. V2 `merge_job_parts` đánh done đủ stage; queue heal parent đã có Full; V4 clear running khi `return "split"`. Heal `09537b974243`/`b04b8b957d9f`. Fix `docs/fixes/2026-11-03-split-parent-false-failed.md`. **Restart :8801/:8804/:8805.**

- **Aurora file sticky account** (01:43). Upload có `file_id` nhưng chat lấy account pool khác → GPT «không đọc được file» → analyze fallback 8 lô. Vá Aurora `X-Aurora-Account-Id` + sticky `GetByID`; Pineline gửi lại header + cùng host upload. Binary mới `Z:\aurora\aurora` (bak `aurora.bak_before_sticky`). **Cần restart Aurora :5005 trên .244/.247 + Pineline :8801/:8804/:8805.**

- **Aurora file = pool session sống** (01:15). Backup `Z:\PinelineV2_codebak\2026-11-03_aurora-pool-file\`. JWT `data/chatgpt_token.txt` hết hạn bị bỏ qua; upload + chat `input_file` ưu tiên noauth pool (`192.168.31.247:5005`). Smoke OK ~27s. Sync V2/V4/V5. Fix `docs/fixes/2026-11-03-aurora-pool-file-upload.md`. **Restart :8801/:8804/:8805** để process nạp `llm.py`.

## 2026-11-02

- **Pronoun-analyze = upload SRT** (01:10). Mode `file`: Aurora POST /v1/files + chat input_file (API.md). Token local hết hạn → fallback fast (sau đó 2026-11-03 dùng pool). Restart :8804.

- **Pronoun-analyze nhanh** (01:06). PRONOUN_ANALYZE_MODE=fast + chunk 220 + early-stop. **Restart :8804** (job đang 8/28 cần dừng/re-run analyze hoặc chờ xong rồi job sau).

- **Review 31B không phá xưng hô đã lock** (23:55). Backup `Z:\PinelineV2_codebak\2026-11-02_review-pronoun-lock\`. **Restart :8804.**
  - `review_batch`: `review_lock_rules` + `filter_review_fixes_for_lock` (prompt + lọc fix đổi anh/em→ông).
- **Pronoun consistency A–C** (22:21, 3 bản). Backup `Z:\PinelineV2_codebak\2026-11-02_pronoun-consistency-abc\`. **Restart :8804.**
  - `pronoun_consistency.py`: analyze full ZH + lock + ledger + QA jumps + GPT vá.
  - Hook translate plan/batch/post; config `PRONOUN_ANALYZE=1`.
  - Fix log `docs/fixes/2026-11-02-pronoun-consistency-abc.md`.


- **REVIEW_MODEL = gemma4:31b-cloud** (18:36, user yes). Backup `Z:\PinelineV2_codebak\2026-11-02_review-31b\`. **Restart :8804** (nạp `llm.py` cloud route).
  - `CLOUD_LLM_BASE_URL` / `CLOUD_LLM_API_KEY` (từ V2, không ghi key vào docs).
  - `llm.chat` route `ollama/*`/`*-cloud` → 9router thay vì nuốt `:8083`.
- **Aurora GPT cho name/pronoun pass** (18:18, user thử pool Free). Backup `Z:\PinelineV2_codebak\2026-11-02_aurora-name-pronoun\`. **Restart :8804** để server nạp `llm.py`/config (file config GPT keys có hiệu lực ngay cho CLI).
  - `llm.is_chatgpt` + `_chatgpt_chat` (Aurora `:5005`); `config.pass_llm_model`.
  - `NAME_MODEL`/`PRONOUN_MODEL`=`chatgpt/gpt-5-6-mini`; TRANSLATE/REVIEW vẫn local.
  - Test `tests/test_chatgpt_route.py` + smoke PONG qua Aurora OK.
- **Improve xưng hô translate** (13:24, user Cosk làm V4+V5). Backup `Z:\PinelineV2_codebak\2026-11-02_v4-pronoun-pass\`. **Cần restart :8804** (V5 :8805).
  - `translate.apply_pronoun_postpass` + inject pronouns theo scene; siết prompt batch.
  - `agent_pronoun_pass.py`; hook `_run_requested_review` (tên → xưng hô → style).
  - Test `tests/test_pronoun_postpass.py` 3 passed.
- **V5 workspace** (04:17–04:23, quyết định user). Snapshot `Z:\PinelineV2_backup_2026-11-02_0418.zip`. **V4 runtime không đổi** (chỉ docs DECISIONS). Refactor ở `Z:\PinelineV5` — xem CHANGELOG/DECISIONS bên V5.
- **Đồng bộ cấu trúc V4** (04:10). Review `docs/reviews/2026-11-02-v4-structure-sync.md`. Backup `Z:\PinelineV2_codebak\2026-11-02_v4-sync\`. **Cần restart :8804** (+ Ctrl+F5 UI).
  - Vá nhãn/cổng còn V2·8801 trên `index3`, agent_*, `server`/`routes_*`, `fileio`, `migrate_work` docstring, `workflow.html`.
  - `build_desktop.bat` đóng gói `index3.html`; tests Host → `:8804` (4 passed).
  - Còn cố ý: heal/feeder/restart legacy path·port 8801; `scripts/check_batch*`; STATE job history V2.
- **Cleanup thừa + RUNBOOK/ARCHITECTURE V4** (04:05). Backup `Z:\PinelineV2_codebak\2026-11-02_v4-cleanup\`. **Cần restart :8804.**
  - Archive Tauri stack → `scripts/archive/tauri_desktop/`; `index.html` → `ui_legacy/`; `scratch/` → `scratch_oneshot/`.
  - Launcher + `PineLine/` đã trong `launchers_legacy/` (root sạch: chỉ `run_v4` + `run_tele_cmd` + `build_desktop` + install ASR/ORT).
  - `routes_ui`: chỉ `index3.html`. Viết lại `docs/RUNBOOK.md` + `docs/ARCHITECTURE.md` cổng 8804.
- **Audit trùng/thừa + vá** (03:55, user kiểm tra codebase). Review `docs/reviews/2026-11-02-v4-duplication-audit.md`. Backup `Z:\PinelineV2_codebak\2026-11-02_v4-dedupe\`. **Cần restart :8804.**
  - Archive launcher V1/V2: `scripts/archive/launchers_legacy/` (`run_v2`, `run.bat`, `Pineline.bat`, `app.py`, …).
  - `routes_ui`: `/` và `/ui3` ưu tiên **`index3.html`** (hết orphan sau port V2).
  - Canva redirect mặc định `:8804`; `lib_check` sample → `data/samples` V4.
  - Archive `docs/workflow.html` stale; `restart_server`/`migrate_work` bỏ fallback `run_v2`; lock message `PinelineV4`.
- **Auto-split phim dài** (03:21–03:25, user: detect → cắt → đánh số → làm lần lượt → file cuối). Backup `Z:\PinelineV2_codebak\2026-11-02_v4-auto-split\`. **Cần restart :8804.**
  - `batch_config`: `auto_split=true`, `auto_split_min_h=3`, `auto_split_hours=2.5`, `auto_merge=true`.
  - Queue/run-all: probe ≥3h → `{id}_p01…pN` (title «Phần k/N»), xếp **đúng thứ tự**, worker 1 job/lần = part 1 xong mới part 2…
  - Part cuối mux xong → merge → job cha có **`output.mp4`** (+ `output_full.mp4`), stages wired = done.
  - `GET .../split-plan` → `will_auto_split`.
- **Queue sort + meta title + split_parts** (03:15, user: lệch sub phim 12h + làm 1+2+3). Backup `Z:\PinelineV2_codebak\2026-11-02_v4-split-queue\`. Fix log `docs/fixes/2026-11-02-longfilm-sub-drift-split.md`. **Cần restart :8804.**
  - `server.py`: `POST /api/queue/jobs/{sort,move,reorder}`; `GET/POST .../split-plan|split-parts|merge-parts`.
  - `split_parts.py` (port V2): chia ~2.5h/part (smart silence cut), merge `output_full.mp4`.
  - `routes_hg.py`: `POST /meta/generate-title` (giữ ai-image/baike).
  - Pytest `tests/test_queue_jobs_api.py` 2 passed.
- **Follow-up stale port V4** (sau review structure): port `preset_switcher.py`; default `PORT=8804` / `PINELINE_BASE` cho `agent_autopilot`, `agent_hongguo`, `agent_feeder`, `agent_heal` (+`D:\PinelineV4_work`), `meta_studio` poster, `migrate_work`, `restart_server` (start `server.py`/`run_v4.bat`). Codebak `…\2026-11-02_v4-port-v2\followup\`. **Cần restart :8804 + :8802.**
- **Review V4 + port cập nhật từ V2** (02:05–02:20, user yêu cầu). Chi tiết: `docs/reviews/2026-11-02-v4-structure-and-v2-port.md`. Backup codebak `Z:\PinelineV2_codebak\2026-11-02_v4-port-v2\` + zip snapshot `Z:\PinelineV2_backup_2026-11-02_0209.zip`. **Cần restart server :8804 + sidecar :8802** để nạp module mới.
  - Port wholesale từ V2: pipeline (`separate` chunk Demucs dài, `asr.resolve_asr_source`, `nano_fa_asr`, `render` hardsub ngưỡng, `clone_tts` rubberband, `job_queue.get_job_info`, `translate`/`llm`/`series_glossary`, `batch_config`, `film_db` sync_one/upload-lock, `auto_publisher` queue/lock, `meta_studio`, `agent_feeder`, `agent_tele_cmd`, `index3`/`static/app.js`, …).
  - `server.py` (merge): ASR `nano_fa` mặc định; `/api/queue/jobs` thêm `queue_items`; **giữ** `routes_films` + `routes_uploader_settings`.
  - Vá V4: `routes_films.library_action` → feeder (fix log `docs/fixes/2026-11-02-library-action-missing-api.md`); `config` file-first `RENDER_DUB_VOL`/`RENDER_BGM_VOL` (giữ `save_config`); sidecar `BASE` theo `PORT`; poster `films_ui` relative.
  - Kiểm: py_compile OK; pytest job_queue+render_expr+sfx_lib **37 passed**.

- **Cải tiến `/films/ui` & thêm chức năng xoá film** (03:30, user yêu cầu):
  - **`film_db.py`**: thêm `query(work_exists=...)`, `delete_film(job_id, delete_work=...)`, `delete_films(job_ids, delete_work=...)`, `purge_missing(only_pending_failed=...)`, cập nhật `stats()` trả `work_exists` và `work_missing`.
  - **`agent_tele_cmd.py`**: thêm endpoints `POST /films/delete`, `POST /films/purge-missing`, `POST /films/sync`, lệnh Telegram `/delfilm <job_id> [work]`, nhận tham số `work_exists` trong `GET /films`. **Đã restart sidecar :8802.**
  - **`films_ui.html`**: giao diện quản lý phim trực quan với cột thao tác nút `🗑️ Xoá` (kèm modal tuỳ chọn xoá file `work/` hoặc chỉ xoá DB), thanh chọn nhiều job để xoá hàng loạt, bộ lọc thư mục (tất cả / chỉ còn thư mục / đã xoá), toggle "Ẩn đã xoá thư mục", banner cảnh báo job mất thư mục kèm nút `🧹 Xoá sạch toàn bộ` / `Chỉ xoá pending/failed`.
  - Backup: `Z:\PinelineV2_backup_2026-10-09_0124.zip`, codebak `Z:\PinelineV2_codebak\2026-10-09_films-ui-delete\`. Fix log: `docs/fixes/2026-10-09-films-ui-delete-missing.md`.

## 2026-10-08

- **PineLine V3 portable** (00:00-01:50, user yêu cầu): bản mang đi ở `Z:\PinelineV3` (~10,8 GB), chạy bằng `PineLine.exe` (launcher tkinter, PyInstaller). V2 không đổi. Chi tiết: `Z:\PinelineV3\README_V3.md`.
  - `app\` = clone V2 `ea7b881` (bỏ remote, nhánh `v3`) + asset (cdx23, bgm_yt, voices, `data/films.db`); không chép secret/token/cookie.
  - `runtime\python` 8,3 GB: Python 3.12 + torch 2.8.0 cu128 (RTX 20xx-50xx, driver ≥ 570) + 192 gói, `pip check` sạch; chạy với `PYTHONNOUSERSITE=1`. `runtime\ffmpeg` 8.1, `runtime\llama` (llama-server CUDA 12), `apps\hongguo` (bản quyền riêng, máy mới có thể phải kích hoạt lại). 9router không đi kèm.
  - Model (~8-9 GB) tải lần đầu từ launcher (`launcher\setup_models.py`: Fun-ASR-Nano, fsmn-vad, paraformer-zh, ct-punc, Qwen3-ForcedAligner, VieNeu v3 Turbo, MOSS tokenizer).
  - LLM mặc định Ollama Cloud (`https://ollama.com/v1`, `gemma4:31b`, dự phòng `gpt-oss:120b`), key nhập trong launcher, ghi vào `pineline.config.json` (gitignore).
  - GPU tự dò (`nvidia-smi`): CUDA nếu driver ≥ 570, batch VieNeu theo VRAM; không NVIDIA → CPU + x264.
  - Sửa code cho portable (chỉ ở V3): `agent_hongguo` (`HONGGUO_DIR`), `server`/`pick_dirs_dialog`/`agent_feeder` (`PINELINE_LIB` thay `D:\Lib` cứng), `migrate_work` (`PINELINE_BASE`/`PORT`/`AUTOPILOT_PORT`), `restart_server` (`PINELINE_TMP`, cổng theo env), `run_v2.bat`/`run_tele_cmd.bat` (runtime portable + `v3_env.bat`).
  - Kiểm: import + CUDA, VieNeu tổng hợp trên GPU, Fun-ASR-Nano, server V3 cổng 9801 (UI/API 200), tải paraformer qua launcher, exe nhận dịch vụ V2 là "ngoài launcher".
- **Sự cố ổ D: đầy 0 GB** (01:20-01:35): gộp 问鼎仙途 6,9 GB + render → mux 0be257b1594b lỗi `Error muxing a packet`, 9a78abb17ad5 lỗi đầu ASR, worker hàng đợi chết (`_save` OSError). User cho xoá `mixed_audio.wav` + `dub_fit.wav` của 13 job đã render xong (26 file, 52,1 GB). Kích lại hàng đợi (xoá + thêm lại job chờ). Chưa sửa code. Fix log `fixes/2026-10-08-queue-worker-disk-full.md`.

## 2026-10-07

- **Sơ đồ workflow toàn hệ thống** (12:50): `docs/workflow.html` — trang tĩnh mở bằng trình duyệt, 7 tầng (giao diện, AI agent, nguồn phim, job/hàng đợi, pipeline, đầu ra, hạ tầng), 33 khối + 54 đường nối, bấm khối xem chi tiết/file/kết nối; kèm bảng 3 cách điều khiển và chốt an toàn.
- **Hongguo: tạo job UI3 từ thư viện** (06:03–06:10, user yêu cầu): `/hongguo` tab Hàng đợi gộp → thư viện: nút **«＋ Job»** mỗi series (tạo job UI3 từ file `(merged)` qua `POST /api/jobs/local-path`, title = tên folder, đọc thẳng `D:\Lib`), **«＋ Job đã chọn»** + ô «chạy luôn» (xếp `POST /api/queue/jobs` theo CONFIG BATCH, mặc định tắt). Series đã có job (khớp `download.video_path` hoặc `title_zh` bỏ « (merged)») hiện **«↗ UI3»** mở thẳng job; khoá nút khi chưa gộp hoặc đang trong hàng đợi gộp; hỏi lại nếu tạo trùng. Log chung thêm dòng `[job]`. UI3 nhận `?job=<id>` để mở thẳng job. Chỉ sửa `hongguo.html` + 1 dòng `index3.html`, không restart. Backup `codebak\2026-10-07_hg_add_job\`.
- **Hongguo: thanh công cụ gọn + log dạng dock** (04:53–04:58, user yêu cầu): Thanh công cụ gọn: tab + công cụ của tab trên **1 hàng** (bỏ tiêu đề từng pane; Bảng hot 46px, Tìm 75px, Catalog 85px ở 1920px — trước ~6 hàng). Sửa lỗi ô tìm catalog hiện cả khi đang ở Leaderboard (`.exctl{display:flex}` đè `hidden`). Khung tải/log thành **dock thu gọn** ở đáy (mặc định 40px: trạng thái + dòng log mới nhất; «▴ Log» mở, nhớ trong localStorage). Thẻ phim 176px (10 cột ở 1920px). Không restart. Backup `codebak\2026-10-07_hg_compact_top\`.
- **Hongguo: thư viện vào tab Hàng đợi gộp** (04:46–04:50, user yêu cầu): Khung **Thư viện Hongguo** chuyển vào tab «🎞 Hàng đợi gộp» (hàng đợi trái, thư viện phải 440px; màn < 980px xếp chồng), bỏ cột phải → Tìm / Bảng hot dùng hết chiều ngang. Series trong hàng đợi có nhãn «● đang gộp» / «chờ #n»; xếp hàng xong tự bỏ tick; nút «Chưa gộp» không tick series đã trong hàng đợi. Không restart. Backup `codebak\2026-10-07_hg_lib_in_tab\`.
- **Hongguo: tab Hàng đợi gộp + 1 log chung** (04:35–04:40, user yêu cầu): `/hongguo`: hàng đợi gộp chuyển thành **tab riêng** «🎞 Hàng đợi gộp» (cạnh Tìm / Bảng hot, có số series còn lại) — nút Gộp đã chọn / Tất cả chưa gộp / Xoá hàng chờ, khối Đang làm (bước · % · thời gian · thanh tiến độ), danh sách chờ đánh số, kết quả gần đây; bấm gộp tự mở tab này. Bỏ khối Merge queue ở cột thư viện. **Một log chung** «Trạng thái tải · log»: dòng `[tải]` + `[gộp]` xếp theo giờ (chuẩn hoá % chỉ giữ dòng mới nhất), Clear ẩn dòng cũ. Không restart. Backup `codebak\2026-10-07_hg_merge_tab\`.
- **Hongguo Merge all bền + hiện tiến độ** (04:28–04:32): hàng đợi gộp lưu `work/logs/hg_merge_state.json`, server khởi động/UI hỏi trạng thái thì chạy tiếp; `merge_queue_add` chỉ xếp hàng (chuẩn hoá/dọn chuyển vào worker); UI hiện series · bước · % · thời gian, tiến độ lô, 6 kết quả gần nhất; `restart_server.py` từ chối restart khi đang gộp (`--ignore-hg` để ép). Test 5 mới, pytest 103/103, check_batch1–5 pass. Backup `codebak\2026-10-07_hg_merge_q\` + zip 04:28. Restart server PID 32156. Fix log `fixes/2026-10-07-hg-merge-queue.md`.
- **Job đọc video thẳng từ `D:\Lib`** (04:00–04:25, user chọn): import file trong `SOURCE_DIRECT_ROOTS` (mặc định `D:\Lib`) → manifest `video_path` = đường dẫn thư viện, không đặt file vào job; ngoài thư viện vẫn hard link/copy. Ghi `source_mode`/`video_size`/`video_mtime`; heal báo `source_changed`; `agent_av_sync`, `media_ts --check` đọc `video_path`. Test 5, liên quan 17/17, check_batch1–5 pass. Backup `codebak\2026-10-07_source_direct\`. Restart server PID 22868.
- **Source video không chép 2 bản** (03:40–03:46): `server._link_or_copy` — hard link trước, chỉ copy khi khác ổ (có log); dùng cho import thư viện và `/api/jobs/{id}/source-path` (trước luôn copy). Test `tests/test_source_link.py`, pytest 96/96. Backup `codebak\2026-10-07_source_link\` + zip 03:42. Restart server (queue rảnh) PID 28108. Fix log `fixes/2026-10-07-source-duplicate-copy.md`.
- **Restart server + sidecar** (03:22, queue rảnh): sidecar nạp `batch_config` có `sfx_lib` (trước đó Telegram `/set audio_mode=sfx_lib` bị từ chối). Server PID 56888, sidecar PID 27392.
- **Docs** (03:02): RUNBOOK thêm bảng 7 chế độ âm thanh; kho `bgm_yt` đã dò không có bài nào có lời.
- **CONFIG BATCH → `sfx_lib`** (02:52, user duyệt mẫu). Chỉnh theo user (nhạc nhỏ hơn, tiếng động to vừa phải, giọng to hơn): `RENDER_SFX_VOL` 0,62, `RENDER_LIB_BGM_VOL` 0,25, key mới `RENDER_SFX_VOICE_BOOST` 1,25 (× `RENDER_DUB_VOL`), limiter −1 dBFS. Sửa hụt đuôi pass 1 (`fixes/2026-10-07-sfxlib-sidechain-short.md`). Backup `codebak\2026-10-07_sfxlib_tune\` + zip 02:45. Pytest 93/93. Mẫu `E2_sfx_lib_chinh.mp4` (−15,8 LUFS, peak −0,9 dBFS).
- **Chế độ audio `sfx_lib`** (02:10–02:36): giọng Việt + tiếng động gốc (CDX23) + nhạc kho YouTube theo mức. Backup `codebak\2026-10-07_sfxlib\` + zip. Render tự chuẩn bị (tiến trình con, ~14 phút/phim 2,6 h lần đầu, cache sau). Server cần restart cho `batch_config`/`agent_core` (danh sách chế độ); render/sfx_lib nạp lại mỗi lần render.
  - Mới: `sfx_lib.py`, `models/cdx23/` (3 checkpoint, MIT, `.gitignore` thêm `*.th`), `tests/test_sfx_lib.py` (11 test). Pytest 92/92.
  - `render.py`: mode `sfx_lib` (alias `sfx_library`/`sfx_yt`/`yt_lib`; `sfx_bgm` vẫn là `duck_bgm`), two-pass sidechain, gọi `sfx_lib.run_subprocess` trước pass 1, ghi tiến độ vào `cur_text`.
  - `batch_config.py`, `agent_core.py`, `index.html`, `index3.html`, `static/app.js`: thêm lựa chọn `sfx_lib`. `restart_server.py`: precheck thêm `sfx_lib.py`.
  - CONFIG BATCH **không đổi** (vẫn `duck`).

- **Kho nhạc YouTube Audio Library** (02:40). `assets/bgm_yt/{calm,mid,intense}/` 45 bài (Attribution not required, Ambient/Cinematic) + `assets/bgm_yt/manifest.json` (license từng bài). Chưa có code dùng; `assets/bgm/` giữ nguyên. Không cần restart.

- **M20 — `voice_bgm` thêm `apad` cho dub** (01:50). `render.py` `_build_audio_filter`. Cần restart server cho render mới; CONFIG BATCH không đổi. Test mới trong `tests/test_render_expr.py`, pytest 81/81. Fix log `fixes/2026-10-07-m20-voice-bgm-apad.md`. Backup `codebak\2026-10-07_m20\` + zip 0147.

- **Restart văng lần 2 → sửa root cause thật** (01:27–01:40). Fix log `fixes/2026-10-06-restart-killed-itself.md` (mục cập nhật 07/10). Backup `Z:\PinelineV2_codebak\2026-10-07_restartfix2\` + `2026-10-07_restartfix3\` + zip 0135.
  - `migrate_work.kill_with_parent_cmd`: mọi lời gọi psutil trên tiến trình đã chết được bỏ qua (`procs()` trả cả `cmd.exe` bọc server, cmd tự thoát khi python bị kill → `NoSuchProcess`).
  - `tests/test_restart_guard.py`: thêm `test_kill_dead_process_is_noop`, `test_kill_wrapper_after_child`. Pytest 80/80.
  - Đã restart bằng `restart_server.py --clean-env --sidecar` (queue rảnh): server PID 59488, sidecar PID 57748 — **đợt 7 đã có hiệu lực**. Auto-pilot vẫn tắt.

## 2026-10-06

- **Đợt 7 — gỡ UI cũ, tách server.py** (14:50–15:20). **Cần restart server** mới có hiệu lực (chỉ khi hàng đợi rảnh / user đồng ý). Backup zip 1455 + `Z:\PinelineV2_codebak\2026-10-06_batch7\`. Fix log `fixes/2026-10-06-batch7-ui-split.md`.
  - Xoá `index1.html`, `index2.html`, route `/ui1` `/ui2` `/index1.html` `/index2.html`; bỏ link trong `index.html`, `index3.html`; `hongguo.html` nút UI1 → `/ui3` (HTML có hiệu lực ngay).
  - `server.py` 6221 → 5372 dòng: `routes_ui.py`, `routes_hg.py`, `routes_agent.py` (`APIRouter`, gọi server qua `S.<tên>`, `server` re-export tên cũ, alias `sys.modules["server"]` khi chạy `python server.py`). OpenAPI 108 route giống hệt.
  - `restart_server.py`: precheck compile thêm `routes_*.py`. `tests/test_server_split.py`. Pytest 78/78.

- **Restart hẹn giờ chết giữa chừng** (13:58, phát hiện 14:31, sửa 14:35–14:50). Fix log `fixes/2026-10-06-restart-killed-itself.md`. Backup `Z:\PinelineV2_codebak\2026-10-06_restartfix\` + zip 1435.
  - `migrate_work.kill_with_parent_cmd`: không kill chính mình / tổ tiên (psutil duyệt con đệ quy chỉ so thời điểm tạo với gốc → PID tái dùng làm tiến trình gọi thành "cháu").
  - `restart_server.py`: log từng bước sau khi job xong; `try/except` ở `main` ghi traceback + báo Telegram.
  - `tests/test_restart_guard.py`. Pytest 76/76.
  - Đã start tay server (PID 25032) + sidecar (PID 13400) bằng code mới, xếp lại 3a2e. Đợt 1–6 giờ đã có hiệu lực.
  - `D:\PinelineV2_tmp\snapshot.py`: bỏ qua file đang bị khoá.

- **Đợt 6 review — bảo trì** (10:26–10:40). Pytest 75/75. Backup zip 1028 + `Z:\PinelineV2_codebak\2026-10-06_batch6\`. Fix log `fixes/2026-10-06-batch6-maintenance.md`.
  - Git local: `git init` (không remote), `.gitignore` (secret, `work/`, `data/`, voices, lock, log, media), `core.autocrlf=false`, `pineline.config.example.json` (key để rỗng). Commit gốc `7657fea`, quét secret trước khi commit.
  - `pytest.ini`; `tests/test_review_batches.py` (chạy `check_batch1–5`), `tests/test_agent_parser.py`, `tests/test_render_expr.py`. Sửa kỳ vọng sai trong `test_hardsub_asr.py`.
  - `render.py` (M3): `_sum_expr` / `_pw_expr` dựng cây khi trên 64 đoạn, vì ffmpeg lỗi khi `if()` lồng ≥100 tầng hoặc tổng `between` >100 hạng tử. ≤64 đoạn: filter giống hệt bản cũ. Hiệu lực ngay ở lần mux tới.
  - Chuyển 29 script một lần / UI dump ở gốc sang `codebak\2026-10-06_batch6\attic\`. Giữ `_read_hg_ui_token.py`.
  - `requirements.txt`: thêm `psutil`, `rapidocr-onnxruntime`, `pytest`.
- **Đợt 5 review — agent an toàn hơn** (10:09–10:25). Test `scripts/check_batch5.py` (128). Backup zip 1009 + `Z:\PinelineV2_codebak\2026-10-06_batch5\`. Fix log `fixes/2026-10-06-batch5-agent-safety.md`.
  - `agent_tele_cmd.py`:
    - `_slash_hint`: chữ trơn đổi trạng thái (`stop`, `reset`, `set`, `feed on`, `hg auto`/`hg 2`/`hg clean`, `lib add`…) chỉ trả gợi ý "gõ /…"; câu dài thì chuyển cho agent.
    - Bỏ nhánh đoán "auto"+"pilot".
    - Nút ✅/❌ cho thao tác agent đang chờ (`agc:`).
    - Worker FIFO cho tin Telegram, `/stop` `/off` `/status` chạy ngay.
    - `/hg` auto chạy nền, chống trùng.
    - `/agent` giữ nguyên hoa/thường.

    **Restart sidecar.**
  - `agent_core.py`: `tool_tier` (read/mutate/confirm), `park_action`/`confirm_action` (hết hạn 15 phút), `run_agent(require_confirm=...)`, `clip_tool_result` (6000 ký tự), SYSTEM bỏ tool ma `qa_override` và thêm quy tắc 15, hết bước thì liệt kê thao tác đã chạy, `Runtime.notify`. **Restart server.**
  - `agent_hongguo.py`: `detect_flow_mode` (chỉ nhận cả chuỗi), `tool_hg_auto_flow(mode=name|lib|rank)`, `start_auto_flow_bg` (chạy nền + chống trùng), agent gọi `hg_auto_flow` → chạy nền. **Restart server + sidecar.**
  - `server.py`: `AgentChatReq.require_confirm`, `/api/agent/chat` trả `confirms`, `GET /api/agent/pending`, `POST /api/agent/confirm`, `_agent_notify`. **Restart server.**
  - `agent_autopilot.py` (`agent_chat(require_confirm)`, `agent_confirm`), `agent_feeder.py` (`lib_verb`). **Restart sidecar.**
  - Xoá `agent_v2/` (bản cũ lệch, không ai import; bản sao trong backup batch5).
- **Đợt 4 review — tranh chấp ghi, một bản tiến trình, checkpoint an toàn** (09:44–10:10). Test `scripts/check_batch4.py` (56). Backup zip 0944 + `Z:\PinelineV2_codebak\2026-10-06_batch4\`. Fix log `fixes/2026-10-06-batch4-write-races.md`.
  - `manifest.py`: `save()` gộp 3 chiều với bản đĩa trong khoá liên tiến trình; `update(fn)`. **Restart server** (subprocess dùng ngay ở lần spawn kế).
  - `server.py`: `_patch_*_fields` qua `Manifest.update`; claim cho `tts`/`mux`/`translate`/`translate/fill`/`assemble` (409 khi đang chạy); khớp/kill engine theo đường dẫn job; `mark-done` 409 khi job trong hàng đợi; worker hàng đợi khởi động sau startup reset; khoá một bản `.server_{port}.lock`; `POST /api/queue/jobs/opts`. **Restart server.**
  - `job_queue.py` `queue_update_opts`. **Restart server.**
  - `agent_autopilot.py`: đồng bộ opts qua `/opts` thay remove+add, không xếp lại job failed; `agent_core.py` `need_queue` bỏ failed/HOLD/QA. **Restart server + sidecar.**
  - `agent_tele_cmd.py`: khoá một bản `.sidecar_{port}.lock`, bind độc quyền trước khi chạy loop. **Restart sidecar.**
  - `fileio.py`: `atomic_write_json`, `read_json_checkpoint`; `file_lock` bắt `PermissionError` (Windows). **Restart server + sidecar.**
  - `asr.py` + 4 engine ASR: `ensure_audio_wav` / marker `audio.wav.json`, `asr.json` nguyên tử. Hiệu lực lần ASR kế tiếp.
  - `translate.py`: `script.json` nguyên tử. `clone_tts.py`: key clip (lời/giọng/engine/tốc độ), `tts/_keys.json`. **Restart server.**
  - `assemble.py` (`dub_fit.partial.wav`), `render.py` (`mixed_audio.json`): hiệu lực ngay lần mux tới.
  - `restart_server.py`: precheck thêm module mới.
- **Đợt 3 review — một nguồn opts/config, ghi nguyên tử** (09:37–10:00). Test `scripts/check_batch3.py` (35). Backup zip 0937 + `Z:\PinelineV2_codebak\2026-10-06_batch3\`. Fix log `fixes/2026-10-06-batch3-single-source.md`.
  - `fileio.py` (mới): `atomic_write_text`, `file_lock`.
  - `batch_config.py`: ghi nguyên tử + khoá, `load()` giữ bản tốt gần nhất, `resolve_job_opts`, `render_kwargs`. **Restart server + sidecar.**
  - `agent_autopilot.py`: state ghi nguyên tử, `update_state` trong khoá. **Restart sidecar.**
  - `server.py`: API xếp hàng lấy trường thiếu theo config batch; `_queue_run_one`, `_agent_mux_run`, `run_stage mux`, `_agent_resume` dùng `resolve_job_opts` (giọng không lấy từ config batch); `config.inject_env()`. **Restart server.**
  - `config.py`: `inject_env()`, `get()` đọc file trước cho key chép từ file. `llm.py`, `app.py` dùng `inject_env()`. `render.py` `RENDER_ENCODER` qua `config.get`. `config.py`/`render.py` có hiệu lực ngay (nạp lại mỗi lần mux).
- **`restart_server.py`** (09:30) — thêm `--hold-file`/`--hold-max-h`, `--clean-env` (start bằng `start_8801.py` với env chụp từ server cũ), `--sidecar`. Thêm py_compile + import thử trước khi kill; lỗi thì không restart và xếp lại job. Ghi `work/logs/restart_pending.json`. Backup `Z:\PinelineV2_codebak\2026-10-06_restart\`. Đã chạy hẹn giờ lúc 09:34 (rút 3a2e). Không cần restart.
- **Đợt 2 review — bảo mật + config một nguồn + LLM sập** (09:10–09:35). Test `scripts/check_batch2.py` (69 kiểm tra). Backup trước: zip 0908 + `Z:\PinelineV2_codebak\2026-10-06_batch2\`. Fix log `fixes/2026-10-06-batch2-security.md`.
  - `server.py`: middleware `_local_only_guard` chặn Host/Origin/Referer lạ (S4); `_hg_base` bỏ `base` từ client (H4); dịch tiêu đề đọc `TRANSLATE_MODEL` qua config. **Cần restart server.**
  - `hongguo_bridge.py`: `safe_child` cho preview/poster/merge (H5). **Cần restart server.**
  - `index.html`, `index3.html`, `static/app.js`: `escapeHtml` thoát `'`, tên nhóm/`group_id` trong onclick qua escape (H6). Có hiệu lực ngay (Ctrl+F5).
  - `agent_tele_cmd.py`: `_blocked()` + CORS chỉ origin local (A2). **Cần restart sidecar.**
  - `config.py`: `AGENT_*` file-first, `llm_settings()`, `agent_llm()`; `agent_core.py`/`agent_feeder.py` dùng `agent_llm()`. **Cần restart server + sidecar.**
  - `llm.py`: đọc base/key/model lúc gọi (M8), `LOCAL_LLM_BASE_URL` mặc định Ollama 11434 (M9), `LLMUnavailable` khi LLM sập, 400/413/422 không retry (M7); bỏ key trong docstring. **Cần restart server.**
  - `translate.py`, `translate_alts.py`: `_tmodel()/_rmodel()` đọc lúc gọi; `LLMUnavailable` dừng stage (salvage → pending) thay vì để trống câu (M7). **Cần restart server.**
  - Secret (H7): bỏ key khỏi `run_v2.bat` (cùng `LLM_*` chết), `run_tele_cmd.bat`, `config.json`, `.claude\settings.local.json`; `D:\PinelineV2_tmp\redact.py` + `snapshot.py` che secret trong zip. Có hiệu lực ngay.
  - `tests/test_queue_jobs_api.py`: TestClient dùng Host `127.0.0.1:8801`.
- **Đợt 1 review — chặn mất dữ liệu** (08:34–09:10). Test `scripts/check_batch1.py` (mới, 44 kiểm tra trên thư mục tạm). Backup trước: `Z:\PinelineV2_backup_2026-10-06_0834.zip` + `Z:\PinelineV2_codebak\2026-10-06_batch1\`. Fix log `fixes/2026-10-06-batch1-data-loss.md`.
  - `assemble.py` `assemble_fit`: cắt câu runaway theo `dur/ratio` (M5). **Không cần restart** — có hiệu lực ở lần render kế tiếp.
  - `media_ts.py` `ensure_job_audio_ts`: 2 pha + `.audio_ts_pending.json`, `_commit_retime`, `_backup_once` (M2). **Không cần restart** (render reload).
  - `server.py`:
    - `_stage_complete_on_disk`, `_path_key`.
    - `read_job` không heal.
    - Heal dùng kiểm tra đủ (S1).
    - So cwd ffmpeg bằng realpath (S3).
    - Stamp đủ `queue_opts` (S7).

    **Cần restart server.**
  - `job_queue.py`: giữ opts job đang chạy tới khi xong (S6). **Cần restart server.**
  - `restart_server.py`: job thiếu snapshot opts → opts toàn cục + `queue_opts` manifest. Không cần restart.
  - `hongguo_bridge.py`: `merged_covers_fragments`, `cleanup_fragments` (chỉ tập đúng mẫu, ≥98% thời lượng, vào `D:\Lib_trash`, giữ 7 ngày), `purge_trash`, gộp lại khi có tập mới, poll gộp bám tên series, chuẩn hoá lỗi không dọn (H1/H2/H3/H11). **Cần restart server.**
  - `agent_hongguo.py`: số trần không có danh sách → hỏi lại; `_pick_lib_item` (trùng tên → series_id → chuỗi con duy nhất); hết giờ tải / thiếu tập → dừng (A3/A4). **Cần restart server + sidecar.**
  - `agent_feeder.py`: `_downloading_sids` đọc khoá `sid` của `/dl/status`. **Cần restart server + sidecar.**
- **`agent_core.py`** (06:00) — Siết parser tool call dạng chữ: chỉ nhận lời gọi đứng riêng hoặc sau nhãn `Action:`; bắt `TypeError` (giá trị `...`); `run_agent` chỉ parse dạng chữ khi lượt chưa chạy tool nào. Fix log `fixes/2026-10-06-agent-text-toolcall-overmatch.md`. **Cần restart server** (cùng đợt với các sửa agent khác).
- **docs/reviews/2026-10-06-code-review.md** — Review toàn bộ code V2 + agent (4 mảng).
- **docs/** — Dựng hệ thống markdown (`README`, `STATE`, `ARCHITECTURE`, `RUNBOOK`, `DECISIONS`, `CHANGELOG`, `worklog/`, `reviews/`). `PROJECT_STATE.md` thành trang trỏ; bản cũ khôi phục từ backup 5/10 tại `docs/archive_PROJECT_STATE_2026-10-05.md`. Rule mới `.cursor/rules/docs-on-change.mdc`.
- **`agent_core.py`** — `_parse_pycall_tool_calls()`: bắt tool call dạng `tool(key=value)` (tên thuộc `_TOOL_NAMES` hoặc tiền tố `pineline_`, chỉ keyword args, `ast.literal_eval`); `_parse_text_tool_calls` fallback sang nó. SYSTEM: folder trong `D:\Lib` chưa có job → `library add`/`hg_auto_flow`, `queue_add` chỉ cho job có sẵn; quy tắc 14 "hành động = gọi tool". **Cần restart server.**
- **`agent_hongguo.py`** — `tool_hg_library(query="")` lọc theo query, trả đủ (trước cắt `[:30]` → 77 bộ chỉ thấy 30). `tool_hg_merge` gọi `POST /api/hg/merge` của server (fallback `merge_queue_add` nếu server không lên). **Server cần restart; sidecar đã restart.**
- **`hongguo_bridge.py`** — State hàng đợi gộp (`_merge_lock/_q/_cur/_hist/_stop/_thread/_done`) giữ qua `importlib.reload` bằng `globals()`. **Cần restart server.**
- **`render.py`** — Che hardsub `HARDSUB_STYLE=stretch` mặc định: lấy hàng ảnh ngay trên vùng chữ kéo giãn xuống (1 lớp), gộp nhiều vị trí đồng thời thành 1 dải, `HARDSUB_STRETCH_SIGMA`/`_V` mặc định 0/0 (không `gblur`), đệm 15/13 px, phủ hết ngang. Không cần restart.

## 2026-10-05

- **`render.py`** — Render chia khúc `RENDER_CHUNK_SEC` (300) × `RENDER_CHUNK_PAR` (3, tối đa 6): `-copyts -ss … -to …`, điểm cắt giữa 2 khung, tránh vùng mốc nén, `-enc_time_base demux`, concat demuxer + inpoint/outpoint `-c copy`, khúc lỗi → render lại 1 lượt. Bỏ `RENDER_CHUNKS` cũ.
- **`media_ts.py`** (mới) — `AUDIO_TS_FIX` (aresample async) dùng trong `asr.py`, `separate.py`, `mux.py`, `render.py`; `ensure_job_audio_ts()` chỉnh mốc job cũ (backup `_pre_audio_ts/`, đánh dấu `.audio_ts_fixed.json`); CLI `--check`. `agent_av_sync.py` thêm check `audio_ts_drift`.
- **`assemble.py`** — Khớp thời gian thích ứng: nền 1,12×, tăng tới 1,30× khi trễ, vào sớm ≤0,15 s, câu phình tới 1,6×; đánh dấu `.fit_mode`, job ghép bằng code cũ tự ghép lại khi render. `ASSEMBLE_FIT_MODE=off` để tắt. `render.py` reload kéo theo `assemble`/`media_ts`.
- **`server.py`, `job_queue.py`** — Không tự load queue / khởi worker khi chạy dưới pytest (23/23 test qua, 4 s).
- **`config.py`** — Key LLM ưu tiên `pineline.config.json` hơn env; model dịch/review/agent = gemma4 qua 9router. `start_8801.py` start server sạch env.

## 2026-10-04

- **`render.py`** — `HARDSUB_MODE=track` mặc định: dò dải hardsub theo đoạn (~300 khung OCR, `hardsub_track.json`), blur đúng vùng trước zoom, bỏ lớp đen (`HARDSUB_MODE=bar` để dùng lại). Sub Việt bám dải hardsub. Audio AAC encode song song với hình (ghép cuối ~1 phút thay ~50 phút). `_boxblur_r` tính theo chiều cao chẵn + kênh màu nửa kích thước (fix watermark mỏng 16–17 px làm job 12032 fail). `duck`: tiếng gốc chạy hết độ dài video.
- **Cắt video** — 0281 `output.mp4` 14,5 h → `output_part1/2.mp4` (copy, cắt tại keyframe trong khoảng nghỉ thoại).

## 2026-10-03

- **`render.py`** — Chia 2 đoạn render song song + ghép copy + gắn audio 1 lần (fallback 1 mạch); sửa tập 25 fps hỏng mốc (trải lại khung); LUT `lut3d` → `lutrgb` (giống từng bit, nhanh hơn ~43%). Sửa cách tính % pass 2.
- **ffmpeg** — Nâng lên 8.1.2 full_build (NVENC OK). Thử libplacebo LUT: không dùng.
- **`agent_hongguo.py`, `agent_tele_cmd.py`** — Hongguo preview (`/dl/preview`, episodes), `/hg rank` (leaderboard 3 tab), `/hg catalog`, nút 👁 xem thử.

## 2026-09-30

- **`yt_uploader`** — Xử lý HTTP 308 resumable (không dừng sau khúc đầu); khúc 256 MB + log tốc độ; xoá dòng bằng Delete/chuột phải kể cả khi đang upload; bỏ file trung gian khi thêm folder job; lấy tên Việt từ `films.db`.
- **`translate.py` / `context_studio`** — Phân tích mạch truyện/xưng hô: bỏ cặp mặc định, "ngươi" → "mày", tăng cửa sổ mẫu (`n_win=12`, `win=70`). cc52: ghép `sub.vi.srt` user sửa vào `script.json`, sửa 17 lỗi 他/她, TTS lại.
- **`E:\models\presets`** — Preset gemma4-26b-qat-mtp chuyển `--fit` 131k.

## 2026-09-29

- **`agent_feeder.py`** (mới), **`agent_autopilot.py`**, **`agent_tele_cmd.py`** — Theo dõi job treo (tiến độ + file + CPU, 30/45 phút → stop + xếp lại đầu, tối đa 2 lần/stage); feeder tự thêm phim khi rảnh (`/feed`, mặc định OFF); `/lib` thư viện có nút Thêm/Ưu tiên/Bỏ/Ghép.
- **`film_db.py`** (mới), `films_ui.html` — SQLite `data/films.db`, sync 2 phút, `/films/ui` (fix trùng `window.status`).
- **`agent_name_pass.py`**, `agent_core.py` — Yêu cầu rà tên/văn phong trước TTS: job đang dịch thì hẹn, xong dịch tự rà → QA gate → TTS.
- **`yt_uploader`** — Đa tài khoản + proxy, khoá IP từng request (upload, chunk, refresh token, thumbnail), chặn proxy rò.

## 2026-09-28

- **`yt_uploader`** — Mô tả mẫu biến, thumbnail tự ghép tên/chọn nhiều, chuyển ra `Z:\yt_uploader`, sửa hàng loạt, đặt tên tài khoản + hiện kênh/email.
- **Hệ thống** — Dọn `C:\temp\sslkey.log` 9 GB, tắt `SSLKEYLOGFILE`.

## 2026-09-27

- **`server.py`, `job_queue.py`** — Ép snapshot opts cho mọi job khi đến lượt, lưu `queue_opts` vào manifest. STOP tắt Auto-pilot.
- **`batch_config.py`** (mới) — `work/logs/batch_config.json` dùng chung; Telegram `/config` `/set` `/reset`; agent tool đọc/sửa config batch; UI3/UI4 nút "Lưu làm config batch".
- **`agent_core.py`** — Tool `queue_add` nhận `group_id` + đủ opts; fallback parse tool call JSON dạng chữ.
- **`index3.html`** — Âm nền + các ô batch nhớ qua localStorage; tiêu đề nhóm không vẽ lại mỗi 2 s; hộp xác nhận tóm tắt config. `index4.html`: ▶ Group.
- **`migrate_work.py`** — Chuyển `work` sang `D:` + junction, retry khi server chậm.
- **`run_v2.bat`, `agent_core.py`** — Tách `AGENT_*` (9router) và `LLM_*` (local).
- **`yt_uploader/`** (mới) — App tkinter upload YouTube OAuth, chọn trình duyệt/copy URL.

## 2026-09-26

- **`render.py`, `agent_av_sync.py`, `agent_core.py`, `server.py`** — Port duck/duck_bgm two-pass sang V2; AV scan/heal_batch (`docs/fixes/2026-09-26-duck-bgm-twopass-port.md`).
- **P0 quản lý job** — opts theo job, chạy cả series, dashboard queue (stage/%/ETA), GPU gate heal/watch (`docs/fixes/2026-09-26-p0-job-management.md`).
- **`index4.html`** (mới) — UI4 Ops (`docs/fixes/2026-09-26-ui4-ops.md`), form + Job, nút stage, panel Agent kéo resize.
- **`index3.html`, `server.py`, `pick_dirs_dialog.py`** — Sửa `compose-on`; `POST /api/jobs/local-batch` nhiều folder; hộp thoại chọn nhiều folder.
- **`agent_autopilot.py`, `agent_tele_cmd.py`** (mới) — Sidecar :8802, Auto-pilot, Telegram `/on /off /status /heal /tick /stop /agent`.

## 2026-09-24 → 25

Xem `docs/fixes/` (stop mux, hardsub hwaccel/drawbox, run-all stale mux, queue voice stop race, duck bgm truncate) và `docs/superpowers/` (job queue tuần tự).
