# Quyáº¿t Äá»nh cá»§a user

- **11-11 (V6 = một codebase thay V2/V4/V5)** User chốt: V6 dựng trên **V5 package** (đã có hotfix B1–B10) + phần riêng V4; mục tiêu **thay cả V2/V4/V5** (1 codebase, nhiều instance theo config: cổng/work/desktop); hot-reload render → **render chạy subprocess mỗi job**. Lộ trình F0 (tạo cây :8806 + job thật) → F1 B9 (Manifest.update qua hàm trạng thái) → F2 A (opts một nguồn) → F3 D (runtime + Stage/Gate, server chỉ app) → F4 C (sidecar client thuần) → F5 E (render subprocess) → F6 B11 + chuyển production. Mỗi pha: tree_audit 0, pytest, /review, 1 job thật so output với V2.

- **11-11 (Studio SOP = 1 job / ghế tới Done)** User khóa vận hành: **1 job một lần** → ASR OK → NMT dịch → REVIEW (Aurora∥, fail → local) → TTS → mux → **Done** → next job. Không CLI soát ngoài queue; không nhảy job giữa chừng. → `_auto_gpu` chạy hết REVIEW trong ghế; `run_review` fan-out `REVIEW_PARALLEL`; queue park chỉ HOLD/soát fail. Fix `docs/fixes/2026-11-11-studio-1job-pipeline.md`.

- **11-10 (Studio queue = 1 job → output, park khi HOLD/soát)** User: workflow studio trước luôn 1 job ra output rồi mới job kế; sau Brain nhảy linh tinh. → Queue **park** ghế khi held/waiting_review (không pop job kế); stamp `held_at=waiting_review`; clear khi soát xong / resume. Fix `docs/fixes/2026-11-10-queue-park-held.md`.

- **11-10 (REVIEW nới văn phong, vẫn vá lỗi)** User chọn 1: Aurora REVIEW thêm lớp thoại tự nhiên khi sửa; không full dịch lại. → review_batch voice loosen. Fix `docs/fixes/2026-11-10-review-voice-loosen.md`.

- **11-10 (REVIEW = chatgpt/gpt-6 Aurora)** User: gpt-6; UI đã chọn Aurora nhưng trước đó chỉ backup nhãn. → REVIEW_MODEL=chatgpt/gpt-6 + resolve aurora_parallel; re-review 60892. Fix `docs/fixes/2026-11-10-review-gpt6-aurora.md`.

- **11-10 (Brain hang = LLM trace+fix rồi mới mở HOLD)** User chọn B: không chỉ merge hang; Brain/LLM phải hiểu vấn đề, trace error, chọn phương án (complete/rewrite/keep_intentional/merge_next) rồi mới clear HOLD. → `agent_hang_fix` + `hang_ack`; chạy sau review (tránh race). Fix `docs/fixes/2026-11-10-brain-hang-llm-fix.md`.

- **11-10 (mix #1+#3 prod + Aurora UI backup)** User: wire mix trước; Parallel Aurora chỉ UI backup (chưa fan-out). → PRONOUN_TITLE_POLICY/REVIEW_PRONOUN_MASK=1; review_backup default off.
Má»i nháº¥t trÃªn cÃ¹ng. Má»i má»¥c: quyáº¿t Äá»nh â bá»i cáº£nh/lÃ½ do. Äá»i quyáº¿t Äá»nh â thÃªm má»¥c má»i, khÃ´ng xoÃ¡ má»¥c cÅ©.

## 2026-11

- **11-09 (Brain C = LLM tool-loop 24/7)** User chá»n C: Brain Äiá»u phá»i `agent_core` tool-loop; LLM Äá»c hiá»u há» thá»ng vÃ  quyáº¿t Äá»nh (khÃ´ng chá» rule job). â `AGENT_BRAIN_MODE=hybrid` + `llm_tick` (force tool + deep job); snapshot `agent_brain_context`; mutate silent `require_confirm=False`. Fix `docs/fixes/2026-11-09-brain-llm-tool-loop.md`.

- **11-09 (REVIEW Pass1 full VI + duty F)** User: soÃ¡t pháº£i Äá»c máº¡ch VI, cÃ¢u pháº£i cÃ³ nghÄ©a (vd ÄuÃ´i treo Â«trÆ°á»c ÄÃ³Â»). â Pass1 upload/full pair SRT + duty F + heal ÄuÃ´i treo; giá»¯ NMT khi ÄÃ£ Äá»§ nghÄ©a. Fix `docs/fixes/2026-11-09-review-pass1-halfcue.md`.

- **11-09 (åé má»m + soÃ¡t ASR merge)** User: `åé` â Â«ghenÂ» ÄÃºng nghÄ©a nhÆ°ng Â«uá»ng giáº¥mÂ»/biáº¿n thá» tá»± nhiÃªn váº«n OK, khÃ´ng hard-forbid; thÃªm nhiá»m vá»¥ soÃ¡t nháº­n ASR cáº¯t/láº·p â gá»p & tá»i Æ°u trÆ°á»c production. â soft wording trong review; duty E + filter evidence; deterministic `apply_asr_stutter_heal` (trÆ°á»c LLM + post-pass), khÃ´ng cáº¯t tÆ°á»£ng thanh. Fix `docs/fixes/2026-11-09-review-asr-merge.md`.

- **11-09 (Second Brain = full silent)** User chá»n option 3: gáº§n nhÆ° khÃ´ng há»i; chá» HOLD khi QA high cháº·n TTS/mux; Telegram tá»i thiá»u. â `agent_brain` + `agent_quality`; `AGENT_BRAIN=1`. Design `docs/design/2026-11-09-second-brain-agent.md`. KhÃ´ng thay `agent_core` chat.

- **11-09 (REVIEW = Gemma4 26b local)** User: Â«Äá»i luÃ´n vÃ  cháº¡y xem saoÂ» sau khi nghi 12B yáº¿u. â `REVIEW_MODEL=llama/gemma4-26b-qat-uncen-mtp`, `REVIEW_PRESET=gemma4-26b-qat-uncen-mtp` (runtime alias `:8083` = `gemma4-26b-qat-uncen-mtp-131k`). Force rereview `05670cbf7c1c`. NMT QT váº«n dá»ch chÃ­nh. (supersede Gemma4 12b review cÃ¹ng ngÃ y)

- **11-09 (REVIEW = Gemma4 12b local)** *(superseded â Gemma4 26b)* User: Äá»i soÃ¡t â `gemma4-12b-qat-mtp-fast` (cÃ¹ng preset dá»ch cÅ©). â `REVIEW_MODEL=llama/gemma4-12b-qat-mtp-fast`, `REVIEW_PRESET=gemma4-12b-qat-mtp-fast`. NMT QT váº«n dá»ch chÃ­nh; NAME/PLAN/PRONOUN váº«n ChatGPT mini. (supersede qwen36 review cÃ¹ng ngÃ y)

- **11-09 (REVIEW = local qwen36-turbo)** *(superseded â Gemma4 12b)* User: soÃ¡t GPT `:3377` cháº­m â chá»n phÆ°Æ¡ng Ã¡n 1. â `REVIEW_MODEL=llama/qwen36-turbo`.

- **11-09 (NMT primary + vÄn phong linh hoáº¡t)** User: khÃ´ng khÃ³a vÄn phong (phim ÄÃ´ thá»âtu tiÃªn); NMT dá»ch chÃ­nh lÃ  tá»t nháº¥t. â giá»¯ `MT_ZH_VI_ROLE=primary`; bá» Ã©p register modernâcá»; mixed/unknown â MT base; detox chá» modern thuáº§n.

- **11-09 (A/B NMT vs old)** Bench: old 14 / NMT 3 / tie 22. Tham kháº£o gates; user váº«n chá»n NMT primary + GPT rÃ  (khÃ´ng quay LLM-main).

- **11-09 (Plan file + review style + A/B)** User chá»n cáº£: glossary upload full SRT (OCR soft); siáº¿t review style_lock+máº«u thoáº¡i; bench A/B. â `PLAN_MODE=file`.

- **11-09 (NMT chÃ­nh / LLM rÃ )** User: NMT = dá»ch chÃ­nh, LLM = rÃ  soÃ¡t (khÃ´ng LLM dá»ch chÃ­nh + NMT hint). â `MT_ZH_VI_ROLE=primary` + `AUTO_REVIEW` GPT mini.

- **11-09 (MT auto genre)** User chá»n option 3: modernâbase `HachimiMT-60-zh-vi`, xianxiaâQT; config `MT_ZH_VI_MODEL=auto`.

- **11-09 (NMT draft + REVIEW GPT mini â GO)** User: triá»n khai cÃ¡c phiÃªn báº£n; soÃ¡t/thiáº¿u dÃ¹ng model nhanh nháº¥t â **chatgpt/gpt-5-6-mini**. Sau sandbox: `MT_ZH_VI=1` nhÃ¡p + slim glossary (chá» lock/characters) + `REVIEW_MODEL=chatgpt/gpt-5-6-mini`. Sync V2/V4/V5. Fix `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`.

- **11-09 (NMT â NO-GO gáº¯n tháº³ng)** *(superseded GO draft cÃ¹ng ngÃ y)* User báº¯t test sandbox trÆ°á»c. Bench `0a5f60aead18` â CONDITIONAL draft QT only. Verdict `docs/reviews/2026-11-09-mt-bench-verdict.md`.

- **11-09 (NMT 60-zh-vi draft sá»m)** *(superseded)* Gáº¯n trÆ°á»c khi test â revert.

- **11-09 (HV Auditor A = 1+2+3)** User chá»n Äá»§: Unihan auditor + consistency ná»i bá» + series hygiene â khÃ´ng chá» whitelist seed. â `hv_auditor.py`; autofix **chá» confusion trap** (é nghá»ânghá»ch); Unihan lá»ch tÃªn riÃªng = `hv_warn` khÃ´ng ÄÃ¨; series drop `hv_suspect`. Fix `docs/fixes/2026-11-09-hv-auditor.md`.

- **11-08 (Hongguo classic full split)** User: restore ÄÃºng trÆ°á»c WinUI; tÃ¡ch biá»t hoÃ n toÃ n hongguo2. â `hongguo.html` báº£n 11-06 drop; `/api/hg`=HTTP only (khÃ´ng license); `/api/hg2`=RPC WinUI; hongguo2 chá» gá»i `/api/hg2/*`. Fix `docs/fixes/2026-11-08-hongguo1-full-split.md`.

- **11-08 (Hongguo1 restore + tÃ¡ch Hongguo2)** *(superseded full split)* User: restore nguyÃªn báº£n `/hongguo`; hg2 lÃ m riÃªng. â header/`http_first` â váº«n Äá»¥ng RPC khi :8000 cháº¿t. Fix `docs/fixes/2026-11-08-hongguo1-restore-isolate.md`.

- **11-08 (Settings WinUI + License Pineline)** User gá»­i áº£nh Settings WinUI (Downloads/Output, khÃ´ng Ã´ license) + toast Â«Cáº§n licenseÂ». â Settings UI/API giá»ng WinUI; License váº«n block riÃªng dÆ°á»i Settings (Pineline DPAPI/prove â WinUI giá»¯ license trong app). Auto-prove khi má» Settings / trÆ°á»c download náº¿u ÄÃ£ cÃ³ key.

- **11-08 (Giá»¯ spawn riÃªng â parity WinUI)** User: giá»¯ hiá»n táº¡i (khÃ´ng attach) nhÆ°ng spawn helper + hongguo2 **hÃ nh vi giá»ng WinUI**. â Singleton 1 MainKt Pineline (cÃ¹ng engine cwd/`settings`/`D:\Lib`/1080p/RPC API); khÃ´ng chia sáº» live queue vá»i WinUI.exe. Fix `docs/fixes/2026-11-08-helper-singleton-winui-parity.md`.

- **11-08 (Helper chung WinUI â attach FAIL)** User chá»n thá»­ Â«má»t helper duy nháº¥t / attach WinUIÂ». Probe: RPC chá» **stdin/stdout** (`Server.readLine`); WinUI giá»¯ pipe; **khÃ´ng** named pipe/TCP; `-XX:+DisableAttachMechanism`. KhÃ´ng attach ÄÆ°á»£c. Persist chung `Roaming\HongguoDownloader\helper-queue.json` (jobs=[] lÃºc test) â  live sync. PhÃ¡t hiá»n ~104 `MainKt` leak parent `agent_tele_cmd.py` + 1 helper WinUI. HÆ°á»ng cÃ²n: sync file / enqueue-only / deep-link / Pineline-only khi WinUI táº¯t. **Superseded hÃ nh Äá»ng:** quyáº¿t Äá»nh Â«giá»¯ spawn + parityÂ» cÃ¹ng ngÃ y.

- **11-07 (Revive Hongguo2 UI = option B)** User: lÃ m láº¡i UI giá»ng app Hongguo Downloader 2.x (Browse / Ranking / New / Libraryâ¦) cho `/hongguo2`. Supersede drop 11-06: route phá»¥c vá»¥ `hongguo2.html` (WinUI skin); classic `/hongguo` giá»¯ nguyÃªn. License Settings + `/api/hg/license/*`; hot-path magic `@@license@@*` qua search/resolve tá»i khi :8801 reload. Backup `Z:\PinelineV2_codebak\2026-11-07_hongguo2-ui-2x\`.

- **11-07 (Hongguo 2.x license prove)** User paste Hongguo key â activate+prove há»£p lá» vÃ o helper Pineline; key DPAPI local (khÃ´ng docs); hook download RPC. KhÃ´ng crack / khÃ´ng cÆ°á»p stdin WinUI.

- **11-06 (Drop Hongguo2)** *(superseded 11-07 revive B)* User: bá» hongguo 2, quÃ¡ tá» â update V4âV5. Route `/hongguo2` â 302 `/hongguo`; khÃ´ng cÃ²n nav/link thá»­ nghiá»m; deep-link Films UI â Hongguo gá»c + `bootFromQuery`. File `hongguo2.html` giá»¯ archive trÃªn ÄÄ©a. Fix `docs/fixes/2026-11-06-drop-hongguo2.md`.

- **11-06 (Films UI MÃ¹a má»i)** User: ok lÃ m Äi â báº£ng mÃ¹a má»i chÃ­nh á» Films UI (`/films/ui?tab=seasons`), filter chá» mÃ¹a má»i hÆ¡n max ÄÃ£ biáº¿t; Hongguo2 cÃ²n badge/compact + Update Lib. Fix follow-up `docs/fixes/2026-11-06-hg-watchlist-discover.md`. *(superseded: Hongguo2 ÄÃ£ drop.)*
- **11-06 (hg_watchlist)** User: ok â táº¡o báº£ng meta trong `films.db` (`hg_watchlist`); xoÃ¡ Lib giá»¯ sid/core/title; Â«TÃ¬m mÃ¹a má»iÂ» quÃ©t theo DB+watchlist, **khÃ´ng** gá»i Hongguo Update all (trÃ¡nh táº£i hÃ ng nghÃ¬n táº­p). NÃºt Â«Cáº­p nháº­t thÆ° viá»nÂ» giá»¯ hÃ nh vi táº£i táº­p thiáº¿u. Fix `docs/fixes/2026-11-06-hg-watchlist-discover.md`.

- **11-05 (autosplit conflict guards)** User asked V2+V4+V5 â guards chá»ng auto-split / ASR promote chá»ng luá»ng (merged skip, same-source promote, part pipeline complete). Fix log `docs/fixes/2026-11-05-autosplit-conflict-guards.md`. KhÃ´ng restart láº§n nÃ y.

- **11-05 (restore Tauri V5)** User: cÃ³ â khÃ´i phá»¥c Tauri tá»« archive lÃªn root V5 (song song WebView2 `app_desktop.py`). Branding/port **8805**; `cargo check` pass. Backup `Z:\PinelineV2_codebak\2026-11-05_restore-tauri\`.

- **11-04 (V5 unity â docs + xoÃ¡ TARGET shells)** Consensus 3 auditor: docs-first unity; root ~10 `.py` = intentional **app core** (khÃ´ng táº¡o `core/` tuáº§n nÃ y); giá»¯ `pineline.server.routes` attach LIVE; giá»¯ `http_routes` bodies; xoÃ¡ shells rá»ng `pineline/{agents,pipeline,sidecar,desktop,ops,server/services}`; **khÃ´ng** move `job_queue` vÃ o `core/`; **khÃ´ng** merge `http_routes` vÃ o `pineline`. Design: `docs/design/2026-11-04-v5-structure-unity.md`. Backup `Z:\PinelineV2_codebak\2026-11-04_v5-unity\`. KhÃ´ng restart :8805 (docs + delete empty dirs).

- **11-05 (V5 `core/` package)** User: yes. Chuyá»n kernel root â `core/`: `config`, `batch_config`, `job_queue`, `job_meta`, `film_db`, `manifest`, `fileio`. Entry giá»¯ root: `server.py`, `app_desktop.py`, `restart_server.py`. KhÃ´ng shim â rewrite `import X` â `import core.X as X` / `from core.X import â¦`. Backup `Z:\PinelineV2_codebak\2026-11-05_v5-core\`.

- **11-04 (V5 Phase E â xoÃ¡ shim)** User: yes. Rewrite import â `agents.*` / `engines.*` / `http_routes.*`; sá»­a CLI subprocess path; xoÃ¡ shim root Äá» Explorer sáº¡ch. Giá»¯ entry tháº­t: `server.py`, `config.py`, `job_queue.py`, â¦ Backup `Z:\PinelineV2_codebak\2026-11-04_v5-layout-E\`.

- **11-04 (V5 full layout AâD)** User: lÃ m háº¿t toÃ n bá» gá»n tree; luÃ´n sub-agent kiá»m tra chÃ©o / test / fix; codebase Äá»ng bá» Äáº§uâcuá»i. Cháº¥p nháº­n move cÃ³ **shim root** (`from pkg.X import *`): A junk/HTML/apps/docs â B `agents/`+`routes/` â C `engines/asr/` â D engines nÃ³ng. Restart :8805 sau má»i phase rá»§i ro. Backup theo Äá»£t `Z:\PinelineV2_codebak\2026-11-04_v5-layout-*`.

- **11-04 (V5 cleanup plan + 3 auditors)** User: táº¡o sub-agent kiá»m tra chÃ©o + review cáº¥u trÃºc + káº¿ hoáº¡ch gá»n. Skills: `v5-structure-auditor`, `v5-deadcode-hunter`, `v5-ops-docs-auditor`. Synthesis `docs/design/2026-11-04-v5-structure-cleanup.md`. Plan `docs/superpowers/plans/2026-11-04-v5-codebase-cleanup.md`. NguyÃªn táº¯c: khÃ´ng big-bang pipeline; khÃ´ng xoÃ¡ TARGET maps; dual tree/films giá»¯; Æ°u tiÃªn docs+footgun+dead UI+test trÆ°á»c move `routes_*`. (Superseded má»t pháº§n bá»i full layout AâD cÃ¹ng ngÃ y.)

- **11-04 (V5 assets/fs attach + OpID)** Tiáº¿p declutter: `assets`+`fs` cÃ¹ng pattern attach; háº¿t `@app` API cÃ²n láº¡i trÃªn `server.py`. GET+HEAD â `operation_id` riÃªng (`job_video`, `hg_library_preview`). Archive oneshot scripts + xoÃ¡ tauri `node_modules` attic. Backup `Z:\PinelineV2_codebak\2026-11-04_v5-assets-fs-attach\`.

- **11-04 (V5 queue/jobs SSOT)** User: nÃ¢ng cáº¥p V5 gá»n, háº¿t cháº¯p vÃ¡ dual route/manifest. Chá»n: **má»t thÃ¢n handler trong `server.py`** + **má»t báº£n Äá» path** `pineline.server.routes.{queue,jobs}.attach` + `include_router` (giá»ng quyáº¿t Äá»nh jobs 11-02). XoÃ¡ báº£n copy dead trong package `queue.py`. Metadata list â `films.db`; live progress â 1 manifest (`current`). Há»£p Äá»ng: `docs/MANIFEST_CONTRACT.md`. KhÃ´ng port pattern nÃ y sang V2/V4 trong Äá»£t nÃ y. Backup `Z:\PinelineV2_codebak\2026-11-04_v5-queue-ssot\`.

- **11-02 (review lock)** 31B chá» mÆ°á»£t vÄn; Cáº¤M Äá»i self/call khi pronouns_locked (prompt + filter).

- **11-02 (pronoun AâC)** User: lÃ m háº¿t V2+V4+V5 â analyze full ZH (lÃ´+memory) â lock â ledger â QA/GPT vÃ¡. KhÃ´ng Äá»£i diarization. Backup Z:\PinelineV2_codebak\2026-11-02_pronoun-consistency-abc\.

- **11-02 (pipeline LLM 3 táº§ng)** Sync V4: local dá»ch â GPT name/pronoun â REVIEW `gemma4:31b-cloud` + `CLOUD_LLM_*`. Backup `Z:\PinelineV2_codebak\2026-11-02_review-31b\`.
- **11-02 (Aurora GPT pass ngáº¯n)** Sync V4: `chatgpt/` route + `NAME_MODEL`/`PRONOUN_MODEL`; translate bulk váº«n local. Backup `Z:\PinelineV2_codebak\2026-11-02_aurora-name-pronoun\`.
- **11-02 (xÆ°ng hÃ´ translate)** Äá»ng bá» vá»i V4: `apply_pronoun_postpass` + `agent_pronoun_pass` + inject cáº£nh; Agent review = tÃªn â xÆ°ng hÃ´ â vÄn phong. Backup `Z:\PinelineV2_codebak\2026-11-02_v4-pronoun-pass\`.
- **11-02 (jobs registry)** Tiáº¿p khung V5: `/api/jobs/*` ÄÄng kÃ½ qua `pineline.server.routes.jobs.attach` (báº£ng pathâhandler). ThÃ¢n hÃ m **giá»¯ trong `server.py`** (xen helper ~1.7k dÃ²ng) â trÃ¡nh big-bang AST move (extractor unparse ÄÃ£ thá»­ vÃ  rollback). Bá» `@app` trÃªn jobs; `include_router` sau queue. Tiáº¿p: assets registry hoáº·c chuyá»n dáº§n body jobs.
- **11-02 (khung thÆ° má»¥c)** User: cáº§n cáº¥u trÃºc khung rÃµ rÃ ng hÆ¡n trÃªn V5.
  - ThÃªm package **`pineline/`** lÃ m báº£n Äá» + chá» chuyá»n dáº§n: `server/routes`, `server/services`, `pipeline`, `agents`, `sidecar`, `desktop`, `ops` (má»i nhÃ¡nh cÃ³ README).
  - Code runtime cÅ© **giá»¯ á» root** Äáº¿n khi tá»«ng cá»¥m LIVE; khÃ´ng big-bang move.
  - Äá»£t 1 LIVE: `pineline.server.routes.queue` (`/api/queue/*`); `server.py` `include_router` + re-export tÃªn cÅ© cho test/`check_batch*`.
  - Route trong package `pineline.*` dÃ¹ng **lazy `S` proxy** (khÃ´ng `import server` top-level) Äá» trÃ¡nh circular import khi server náº¡p router.
  - Launcher **`run_v5.bat`**, default port **8805** (desktop/restart/tele/migrate/canva/agents).
  - Tiáº¿p theo (cÃ¹ng khung): `jobs` â `assets` â chuyá»n `routes_ui/hg/agent` vÃ o `pineline.server.routes`.
- **11-02** Refactor cáº¥u trÃºc codebase (dá» Äá»c / á»n Äá»nh) â **khÃ´ng sá»­a inplace trÃªn V4**.
  - Táº¡o tree riÃªng **`Z:\PinelineV5`** (copy tá»« V4). V4 = báº£n á»n Äá»nh / restore; production ops váº«n theo V4 (:8804) cho Äáº¿n khi user chuyá»n.
  - V5 dÃ¹ng cá»ng **:8805**, temp `D:\PinelineV5_tmp`, work máº·c Äá»nh `D:\PinelineV5_work` (trÃ¡nh Äá»¥ng process/data V4).
  - PhÆ°Æ¡ng Ã¡n ká»¹ thuáº­t: **A** â tÃ¡ch dáº§n `server.py` theo cá»¥m `routes_*` (queue â jobs â assets), giá»¯ `import server as S` nhÆ° Äá»£t 7; khÃ´ng big-bang package.
  - Má»i thay Äá»i refactor **báº¯t buá»c** ghi thÃªm má»¥c vÃ o `DECISIONS.md` (V5) + CHANGELOG/worklog; trÆ°á»c má»i Äá»£t sá»­a: zip snapshot + codebak.
  - Náº¿u V5 fail: xÃ³a/Äá»i tÃªn `Z:\PinelineV5`, giá»¯ nguyÃªn V4; khÃ´i phá»¥c tá»« zip trong `Z:\PinelineV2_codebak\2026-11-02_v4-to-v5\` / snapshot log.

## 2026-10

- **10-08** V3: nhiá»u key LLM xoay vÃ²ng (429/401/403) â **chá» V3**, V2 giá»¯ 1 key. UI3 + Hongguo hiá»n thá» **trong launcher** báº±ng WebView2 (tkinter khÃ´ng render ÄÆ°á»£c web hiá»n Äáº¡i; viáº¿t láº¡i UI3 báº±ng tkinter quÃ¡ lá»n) â bá» UI4 khá»i V3.
- **10-08** Táº¡o **V3 portable** á» `Z:\PinelineV3` (V2 giá»¯ nguyÃªn, váº«n lÃ  báº£n cháº¡y chÃ­nh). Launcher tkinter + exe; gÃ³i code + Python, model táº£i láº§n Äáº§u; mang cáº£ Hongguo + llama-server; GPU tá»± dÃ² (cu128 Äá» cháº¡y ÄÆ°á»£c RTX 50xx); LLM máº·c Äá»nh **Ollama Cloud** báº±ng key ngÆ°á»i dÃ¹ng nháº­p, 9router chá» dÃ¹ng qua preset Custom. KÃ­ch thÆ°á»c thá»±c ~10,8 GB (torch cu128 riÃªng 6,9 GB) thay vÃ¬ ~6 GB user Æ°á»c.
- **10-07** HÃ ng Äá»£i gá»p Hongguo **lÆ°u ra file** vÃ  restart server pháº£i tÃ´n trá»ng nÃ³ nhÆ° queue render (cháº·n restart khi Äang gá»p). Xáº¿p hÃ ng chá» ghi tÃªn; viá»c náº·ng (ffprobe, chuáº©n hoÃ¡ 1080p, dá»n táº­p láº») lÃ m trong worker Äá» UI khÃ´ng bá» treo.
- **10-07** Video nguá»n láº¥y **trá»±c tiáº¿p tá»« `D:\Lib`** (user chá»n thay cho hard link): job khÃ´ng giá»¯ báº£n sao/link, chá» ghi ÄÆ°á»ng dáº«n thÆ° viá»n trong manifest. KhÃ´ng viáº¿t láº¡i pipeline (user: khÃ´ng cáº§n test láº¡i toÃ n bá») â chá» Äá»i chá» chá»n ÄÆ°á»ng dáº«n lÃºc import. File ngoÃ i thÆ° viá»n váº«n hard link/copy. Job cÅ© (0281, dccc báº£n sao; 5 job hard link) **giá»¯ nguyÃªn** â chá» Ã¡p dá»¥ng tá»« job tiáº¿p theo.
- **10-07** User duyá»t máº«u `sfx_lib` â CONFIG BATCH dÃ¹ng `sfx_lib`. YÃªu cáº§u chá»nh: nháº¡c kho nhá» hÆ¡n, tiáº¿ng Äá»ng gá»c to hÆ¡n nhÆ°ng vá»«a pháº£i, giá»ng Viá»t to hÆ¡n (Äáº·t 0,25 / 0,62 / Ã1,25, cÃ³ limiter). Báº£n tÃ¡ch CDX23 giá»¯ báº£n nhanh (user chÆ°a chá»n khÃ¡c).
- **10-07** Bá» háº³n nháº¡c ná»n gá»c vÃ¬ claim Content ID (vd "Latin Zumba Dance Workout â Liberektro"). User khÃ´ng muá»n dÃ² tá»«ng bÃ i sau khi bá» claim (phá»©c táº¡p vá»i video dÃ i) â chá»n cÃ´ng thá»©c **giá»ng Viá»t + tiáº¿ng Äá»ng gá»c + nháº¡c má»i sáº¡ch báº£n quyá»n**: tÃ¡ch tiáº¿ng Äá»ng báº±ng CDX23 (MIT), nháº¡c láº¥y tá»« **YouTube Audio Library** (Attribution not required, Ambient/Cinematic), chá»n theo má»©c Ãªm/vá»«a/dá»n dáº­p Äo tá»« nháº¡c gá»c. Máº·c Äá»nh CDX23 1 checkpoint (Äo: sÃ³t nháº¡c khÃ´ng hÆ¡n báº£n 3 checkpoint, nhanh ~3Ã). Cháº¿ Äá» `sfx_lib` cÃ³ trong UI/CONFIG BATCH nhÆ°ng **chÆ°a Äá»i CONFIG BATCH** (váº«n `duck`) tá»i khi user duyá»t máº«u. KhÃ´ng dÃ¹ng MusicGen (license cáº¥m thÆ°Æ¡ng máº¡i), khÃ´ng dÃ¹ng Pixabay (nhiá»u bÃ i dÃ­nh Content ID).
- **10-06** (Äá»£t 7) Gá»¡ UI cÅ© `index1/2.html` + route `/ui1`, `/ui2` (user chá»n). TÃ¡ch `server.py` theo nhÃ³m route báº±ng `APIRouter`; code chuyá»n Äi gá»i server qua `S.<tÃªn>` (khÃ´ng `from server import â¦`) Äá» patch trong test váº«n Än vÃ  khÃ´ng náº¡p server 2 láº§n. Pháº§n jobs/queue/pipeline giá»¯ trong `server.py` vÃ¬ check Äá»£t 1â4 Äá»c mÃ£ nguá»n cá»§a nÃ³. Code má»i chá» cÃ³ hiá»u lá»±c khi restart, restart chá» khi hÃ ng Äá»£i ráº£nh hoáº·c user Äá»ng Ã½.
- **10-06** (Äá»£t 6) CÃ³ git local (khÃ´ng remote, khÃ´ng push). Secret vÃ  dá»¯ liá»u job khÃ´ng vÃ o git. Script má»t láº§n á» gá»c chuyá»n ra `codebak\â¦\attic` (khÃ´ng xoÃ¡). UI cÅ© `index1/2.html` giá»¯ nguyÃªn tá»i khi user quyáº¿t. KhÃ´ng tÃ¡ch file lá»n khi Äang cÃ³ job cháº¡y.
- **10-06** (Äá»£t 5, theo review user chá»n lÃ m) Telegram:
  - Lá»nh Äá»i tráº¡ng thÃ¡i **pháº£i cÃ³ `/`**. Chá»¯ trÆ¡n chá» nháº­n gá»£i Ã½; cÃ¢u dÃ i thÃ¬ chuyá»n cho agent.
  - Agent muá»n dá»«ng hÃ ng chá»/job, gá»p/dá»n táº­p, cháº¡y A-Z, cháº¡y láº¡i `force`, reset config, heal hÃ ng loáº¡t â **gá»­i nÃºt â/â**, báº¥m â má»i cháº¡y (háº¿t háº¡n 15 phÃºt).
  - Panel Agent trÃªn UI giá»¯ nhÆ° cÅ© (ÄÃ£ tick cho phÃ©p thÃ¬ cháº¡y tháº³ng).
  - `hg_auto_flow` tá»« agent cháº¡y ná»n, má»i bá» má»t flow.
  - XoÃ¡ `agent_v2/`.
- **10-06** LÃ m tiáº¿p **Äá»£t 2â6** review. Restart server: **háº¹n sau khi f9fe xong** â rÃºt 3a2e khá»i hÃ ng Äá»£i táº¡m, restart, xáº¿p láº¡i 3a2e.
- **10-06** (Äá»£t 4, theo review user chá»n lÃ m) Auto-pilot **khÃ´ng tá»± xáº¿p láº¡i job failed** vÃ  job HOLD / QA cháº·n â job lá»i pháº£i xem rá»i xáº¿p tay, HOLD chá» duyá»t. Báº¥m Táº¡o giá»ng / Render / Dá»ch láº¡i / GhÃ©p khi job Äang cháº¡y (hÃ ng Äá»£i hoáº·c stage running) â tá»« chá»i 409 thay vÃ¬ cháº¡y song song. Server vÃ  sidecar chá» cháº¡y 1 báº£n (khoÃ¡ file).
- **10-06** (Äá»£t 3) Opts job má»t nguá»n: config batch â `queue_opts` cá»§a job â tham sá» truyá»n thÃªm. Agent `mux_run` render láº¡i theo ÄÃºng opts job ÄÃ£ cháº¡y (khÃ´ng cÃ²n Ã©p motion/LUT/4M/táº¯t logo). Giá»ng **khÃ´ng** láº¥y tá»« config batch khi xáº¿p hÃ ng qua API/queue (giá»¯ luáº­t cÅ©: job thiáº¿u giá»ng â bÃ¡o lá»i).
- **10-06** (Äá»£t 2) API key **chá» Äáº·t trong `pineline.config.json`**; `.bat`/`config.json`/code khÃ´ng chá»©a key. Backup zip tá»± che secret. Server/sidecar chá» nháº­n Host/Origin local. LLM sáº­p â dá»«ng stage dá»ch (pending, báº¥m Tiáº¿p tá»¥c), khÃ´ng Äá» trá»ng cÃ¢u.
- **10-06** LuÃ´n **backup trÆ°á»c khi sá»­a** (zip toÃ n project + báº£n gá»c tá»«ng file vÃ o `Z:\PinelineV2_codebak\<ngÃ y>_<Äá»£t>\`) vÃ  ghi md Äá»§ Äá» biáº¿t ÄÃ£ sá»­a gÃ¬. LÃ m Äá»£t 1 review trÆ°á»c; restart server **Äá» sau**.
- **10-06** Táº­p láº» sau gá»p: **chuyá»n vÃ o thÃ¹ng rÃ¡c, giá»¯ 7 ngÃ y** rá»i má»i xoÃ¡ háº³n (khÃ´ng xoÃ¡ ngay). ThÃ¹ng rÃ¡c Äáº·t `D:\Lib_trash\<bá»>\<thá»i Äiá»m>\` (ngoÃ i `D:\Lib` Äá» khÃ´ng bá» quÃ©t nhÆ° táº­p/bá» má»i).
- **10-06** Docs: má»i thay Äá»i pháº£i cÃ³ markdown trong `docs/` (rule `docs-on-change.mdc`). Huá»· cÃ¡c cÃ¢u há»i Äang treo (restart server, táº¯t llama-server).
- **10-06** Che hardsub stretch: **Äá»m 15/13 px** giá»¯ nguyÃªn â má»i má»©c má»ng hÆ¡n (12/11, 10/9, 6/4, 3/2) lá»t nÃ©t á» kÃ½ tá»± cao (job 2ef87, t=2688,5 s).
- **10-06** Che hardsub stretch: **khÃ´ng lÃ m má»m (sigma 0/0)** â user so 0/0, 0,6/1, 0,8/1 vÃ  chá»n 0/0.
- **10-06** Che hardsub: chuyá»n tá»« blur sang **vá»t kÃ©o giÃ£n giá»¯ mÃ u cáº£nh** (`HARDSUB_STYLE=stretch`), 1 lá»p, gá»p nhiá»u vá» trÃ­ cÃ¹ng lÃºc thÃ nh 1 dáº£i. Giá»¯ font sub. **KhÃ´ng render láº¡i 2ef87.**
- **10-06** MÃ¹a 1 cháº¡y trÆ°á»c mÃ¹a 2 (káº¿ thá»«a glossary/xÆ°ng hÃ´ ÄÃ£ duyá»t).
- **10-05** Job 2ef87: Äá» nguyÃªn 21/93 lÃ´ review lá»i. Giá»¯ `openclaw` lÃ m fallback agent dÃ¹ combo Äang há»ng.
- **10-05** Model LLM láº¥y theo file config (file-first) cho dá»ch/review/agent: `ollama/gemma4:31b-cloud` qua 9router.
- **10-05** Render chia khÃºc: khÃºc 300 s, 3 song song (thay chia ÄÃ´i), sau test 5 phÃºt Ã 3 Äáº¡t.
- **10-04** Bá» lá»p Äen hardsub; chá» che ÄÃºng toáº¡ Äá» chá»¯ dÃ² ÄÆ°á»£c theo Äoáº¡n (`HARDSUB_MODE=track`), bÃ¡m zoom.
- **10-04** Video >12 h: cáº¯t copy thÃ nh part cho YouTube (0281 â part1/part2).
- **10-04** LUT: giá»¯ `lutrgb` trÃªn CPU, khÃ´ng chuyá»n libplacebo (cháº­m hÆ¡n + lá»ch mÃ u). DÃ¹ng ffmpeg 8.1.2 full_build.
- **10-03** TÄng tá»c render: lÃ m chia Äoáº¡n song song (Äo 4,1Ã); LUT dÃ¹ng lutrgb.
- **10-03** Hongguo preview/rank/catalog ÄÆ°a vÃ o Telegram + agent.

## 2026-09

- **09-30** Báº£n dá»ch: user tá»± sá»­a `sub.vi.srt` cá»§a cc52 â ghÃ©p ngÆ°á»£c vÃ o `script.json` rá»i TTS láº¡i; Äá»i "anh tÃ´i/cÃ´ tÃ´i" (ä»/å¥¹) thÃ nh "anh ta/cÃ´ ta".
- **09-30** Preset gemma4-26b-qat-mtp dÃ¹ng `--fit` 131k (thay `-ngl 99 --n-cpu-moe 16`).
- **09-29** Agent: rÃ  tÃªn + vÄn phong trÆ°á»c TTS (sau khi dá»ch 100%); feeder tá»± thÃªm job khi hÃ ng chá» trá»ng, máº·c Äá»nh OFF tá»i khi cÃ³ yÃªu cáº§u.
- **09-29** Database phim SQLite `data/films.db` + `/films/ui`; thÆ° viá»n `/lib` qua Telegram.
- **09-29** YT uploader: má»i tÃ i khoáº£n khoÃ¡ 1 IP proxy, kiá»m IP trÆ°á»c má»i request; proxy cháº¿t thÃ¬ khÃ´ng upload (khÃ´ng rÆ¡i vá» máº¡ng tháº³ng). Token Google khÃ´ng gá»­i bÃªn thá»© ba.
- **09-28** YT uploader tÃ¡ch ra `Z:\yt_uploader`, Äa tÃ i khoáº£n Äáº·t tÃªn, sá»­a hÃ ng loáº¡t, thumbnail nhiá»u file.
- **09-28** Agent dÃ¹ng 9router `gemma4:31b-cloud` máº·c Äá»nh.
- **09-27** Chuyá»n `work` sang `D:\PinelineV2_work` (junction tá»« Z) Äá» khÃ´ng tranh á» vá»i Windows.
- **09-27** Config batch dÃ¹ng chung (`batch_config.json`) cho UI3/UI4/Agent/Telegram/Auto-pilot; Äá»i config thÃ¬ job chÆ°a cháº¡y theo luÃ´n, job Äang cháº¡y giá»¯ config cÅ©.
- **09-27** Má»i job bá» Ã©p snapshot opts khi Äáº¿n lÆ°á»£t (khÃ´ng káº¿ thá»«a leftover). STOP = dá»«ng háº¿t + táº¯t Auto-pilot.
- **09-27** TÃ¡ch 2 LLM: Agent â 9router, job â local (phÆ°Æ¡ng Ã¡n 1, env tÃ¡ch). Sau ÄÃ³ (10-05) job cÅ©ng chuyá»n 9router.
- **09-27** YT uploader lÃ  app desktop (khÃ´ng web UI).
- **09-26** Auto-pilot: nÃºt + lá»nh, Äiá»u khiá»n qua Telegram; khÃ´ng restart server khi Äang cháº¡y.
- **09-26** Chá» lÃ m trÃªn V2 (`Z:\PinelineV2`), khÃ´ng Äá»¥ng V1 (`Z:\Pineline`, :8800).
- **09-26** UI4 Ops: layout danh sÃ¡ch dá»± Ã¡n trÃªn-trÃ¡i, preview trÃªn-pháº£i, pipeline dÆ°á»i-trÃ¡i, ká»ch báº£n dÆ°á»i-pháº£i; form + Job trÃªn UI4; chá»n nhiá»u folder báº±ng há»p thoáº¡i Windows.

## 2026-11-08 â Python default sau update 3.15

- **Quyáº¿t Äá»nh:** A+B â bá» Python315 khá»i Machine PATH; C:\Python312 Äáº§u PATH; PY_PYTHON=3.12. Giá»¯ 3.15 cÃ i táº¡i C:\Python315\ (gá»i full path náº¿u cáº§n). Launcher Pineline pin 312 thÃªm lá»p dá»± phÃ²ng.
- **KhÃ´ng chá»n:** CÃ i deps lÃªn 3.15; chá» pin tá»«ng project.


- **2026-11-10 (FireRed half):** User b?t m?c d?nh `FIRERED_USE_HALF=1` (BF16 trên 3060) sau bench CER identical / ~1.4× nhanh. T?t b?ng 0 n?u c?n FP32.
