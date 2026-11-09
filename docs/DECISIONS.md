# Quyết định của user

Mới nhất trên cùng. Mỗi mục: quyết định — bối cảnh/lý do. Đổi quyết định → thêm mục mới, không xoá mục cũ.

## 2026-11

- **11-09 (NMT primary + văn phong linh hoạt)** User: không khóa văn phong (phim đô thị→tu tiên); NMT dịch chính là tốt nhất. → giữ `MT_ZH_VI_ROLE=primary`; bỏ ép register modern↔cổ; mixed/unknown → MT base; detox chỉ modern thuần.

- **11-09 (A/B NMT vs old)** Bench: old 14 / NMT 3 / tie 22. Tham khảo gates; user vẫn chọn NMT primary + GPT rà (không quay LLM-main).

- **11-09 (Plan file + review style + A/B)** User chọn cả: glossary upload full SRT (OCR soft); siết review style_lock+mẫu thoại; bench A/B. → `PLAN_MODE=file`.

- **11-09 (NMT chính / LLM rà)** User: NMT = dịch chính, LLM = rà soát (không LLM dịch chính + NMT hint). → `MT_ZH_VI_ROLE=primary` + `AUTO_REVIEW` GPT mini.

- **11-09 (MT auto genre)** User chọn option 3: modern→base `HachimiMT-60-zh-vi`, xianxia→QT; config `MT_ZH_VI_MODEL=auto`.

- **11-09 (NMT draft + REVIEW GPT mini — GO)** User: triển khai các phiên bản; soát/thiếu dùng model nhanh nhất → **chatgpt/gpt-5-6-mini**. Sau sandbox: `MT_ZH_VI=1` nháp + slim glossary (chỉ lock/characters) + `REVIEW_MODEL=chatgpt/gpt-5-6-mini`. Sync V2/V4/V5. Fix `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`.

- **11-09 (NMT — NO-GO gắn thẳng)** *(superseded GO draft cùng ngày)* User bắt test sandbox trước. Bench `0a5f60aead18` → CONDITIONAL draft QT only. Verdict `docs/reviews/2026-11-09-mt-bench-verdict.md`.

- **11-09 (NMT 60-zh-vi draft sớm)** *(superseded)* Gắn trước khi test → revert.

- **11-09 (HV Auditor A = 1+2+3)** User chọn đủ: Unihan auditor + consistency nội bộ + series hygiene — không chỉ whitelist seed. → `hv_auditor.py`; autofix **chỉ confusion trap** (逆 nghị→nghịch); Unihan lệch tên riêng = `hv_warn` không đè; series drop `hv_suspect`. Fix `docs/fixes/2026-11-09-hv-auditor.md`.

- **11-08 (Hongguo classic full split)** User: restore đúng trước WinUI; tách biệt hoàn toàn hongguo2. → `hongguo.html` bản 11-06 drop; `/api/hg`=HTTP only (không license); `/api/hg2`=RPC WinUI; hongguo2 chỉ gọi `/api/hg2/*`. Fix `docs/fixes/2026-11-08-hongguo1-full-split.md`.

- **11-08 (Hongguo1 restore + tách Hongguo2)** *(superseded full split)* User: restore nguyên bản `/hongguo`; hg2 làm riêng. → header/`http_first` — vẫn đụng RPC khi :8000 chết. Fix `docs/fixes/2026-11-08-hongguo1-restore-isolate.md`.

- **11-08 (Settings WinUI + License Pineline)** User gửi ảnh Settings WinUI (Downloads/Output, không ô license) + toast «Cần license». → Settings UI/API giống WinUI; License vẫn block riêng dưới Settings (Pineline DPAPI/prove — WinUI giữ license trong app). Auto-prove khi mở Settings / trước download nếu đã có key.

- **11-08 (Giữ spawn riêng — parity WinUI)** User: giữ hiện tại (không attach) nhưng spawn helper + hongguo2 **hành vi giống WinUI**. → Singleton 1 MainKt Pineline (cùng engine cwd/`settings`/`D:\Lib`/1080p/RPC API); không chia sẻ live queue với WinUI.exe. Fix `docs/fixes/2026-11-08-helper-singleton-winui-parity.md`.

- **11-08 (Helper chung WinUI — attach FAIL)** User chọn thử «một helper duy nhất / attach WinUI». Probe: RPC chỉ **stdin/stdout** (`Server.readLine`); WinUI giữ pipe; **không** named pipe/TCP; `-XX:+DisableAttachMechanism`. Không attach được. Persist chung `Roaming\HongguoDownloader\helper-queue.json` (jobs=[] lúc test) ≠ live sync. Phát hiện ~104 `MainKt` leak parent `agent_tele_cmd.py` + 1 helper WinUI. Hướng còn: sync file / enqueue-only / deep-link / Pineline-only khi WinUI tắt. **Superseded hành động:** quyết định «giữ spawn + parity» cùng ngày.

- **11-07 (Revive Hongguo2 UI = option B)** User: làm lại UI giống app Hongguo Downloader 2.x (Browse / Ranking / New / Library…) cho `/hongguo2`. Supersede drop 11-06: route phục vụ `hongguo2.html` (WinUI skin); classic `/hongguo` giữ nguyên. License Settings + `/api/hg/license/*`; hot-path magic `@@license@@*` qua search/resolve tới khi :8801 reload. Backup `Z:\PinelineV2_codebak\2026-11-07_hongguo2-ui-2x\`.

- **11-07 (Hongguo 2.x license prove)** User paste Hongguo key → activate+prove hợp lệ vào helper Pineline; key DPAPI local (không docs); hook download RPC. Không crack / không cướp stdin WinUI.

- **11-06 (Drop Hongguo2)** *(superseded 11-07 revive B)* User: bỏ hongguo 2, quá tệ — update V4–V5. Route `/hongguo2` → 302 `/hongguo`; không còn nav/link thử nghiệm; deep-link Films UI → Hongguo gốc + `bootFromQuery`. File `hongguo2.html` giữ archive trên đĩa. Fix `docs/fixes/2026-11-06-drop-hongguo2.md`.

- **11-06 (Films UI Mùa mới)** User: ok làm đi — bảng mùa mới chính ở Films UI (`/films/ui?tab=seasons`), filter chỉ mùa mới hơn max đã biết; Hongguo2 còn badge/compact + Update Lib. Fix follow-up `docs/fixes/2026-11-06-hg-watchlist-discover.md`. *(superseded: Hongguo2 đã drop.)*
- **11-06 (hg_watchlist)** User: ok — tạo bảng meta trong `films.db` (`hg_watchlist`); xoá Lib giữ sid/core/title; «Tìm mùa mới» quét theo DB+watchlist, **không** gọi Hongguo Update all (tránh tải hàng nghìn tập). Nút «Cập nhật thư viện» giữ hành vi tải tập thiếu. Fix `docs/fixes/2026-11-06-hg-watchlist-discover.md`.

- **11-05 (autosplit conflict guards)** User asked V2+V4+V5 — guards chống auto-split / ASR promote chồng luồng (merged skip, same-source promote, part pipeline complete). Fix log `docs/fixes/2026-11-05-autosplit-conflict-guards.md`. Không restart lần này.

- **11-05 (restore Tauri V5)** User: có — khôi phục Tauri từ archive lên root V5 (song song WebView2 `app_desktop.py`). Branding/port **8805**; `cargo check` pass. Backup `Z:\PinelineV2_codebak\2026-11-05_restore-tauri\`.

- **11-04 (V5 unity — docs + xoá TARGET shells)** Consensus 3 auditor: docs-first unity; root ~10 `.py` = intentional **app core** (không tạo `core/` tuần này); giữ `pineline.server.routes` attach LIVE; giữ `http_routes` bodies; xoá shells rỗng `pineline/{agents,pipeline,sidecar,desktop,ops,server/services}`; **không** move `job_queue` vào `core/`; **không** merge `http_routes` vào `pineline`. Design: `docs/design/2026-11-04-v5-structure-unity.md`. Backup `Z:\PinelineV2_codebak\2026-11-04_v5-unity\`. Không restart :8805 (docs + delete empty dirs).

- **11-05 (V5 `core/` package)** User: yes. Chuyển kernel root → `core/`: `config`, `batch_config`, `job_queue`, `job_meta`, `film_db`, `manifest`, `fileio`. Entry giữ root: `server.py`, `app_desktop.py`, `restart_server.py`. Không shim — rewrite `import X` → `import core.X as X` / `from core.X import …`. Backup `Z:\PinelineV2_codebak\2026-11-05_v5-core\`.

- **11-04 (V5 Phase E — xoá shim)** User: yes. Rewrite import → `agents.*` / `engines.*` / `http_routes.*`; sửa CLI subprocess path; xoá shim root để Explorer sạch. Giữ entry thật: `server.py`, `config.py`, `job_queue.py`, … Backup `Z:\PinelineV2_codebak\2026-11-04_v5-layout-E\`.

- **11-04 (V5 full layout A–D)** User: làm hết toàn bộ gọn tree; luôn sub-agent kiểm tra chéo / test / fix; codebase đồng bộ đầu–cuối. Chấp nhận move có **shim root** (`from pkg.X import *`): A junk/HTML/apps/docs → B `agents/`+`routes/` → C `engines/asr/` → D engines nóng. Restart :8805 sau mỗi phase rủi ro. Backup theo đợt `Z:\PinelineV2_codebak\2026-11-04_v5-layout-*`.

- **11-04 (V5 cleanup plan + 3 auditors)** User: tạo sub-agent kiểm tra chéo + review cấu trúc + kế hoạch gọn. Skills: `v5-structure-auditor`, `v5-deadcode-hunter`, `v5-ops-docs-auditor`. Synthesis `docs/design/2026-11-04-v5-structure-cleanup.md`. Plan `docs/superpowers/plans/2026-11-04-v5-codebase-cleanup.md`. Nguyên tắc: không big-bang pipeline; không xoá TARGET maps; dual tree/films giữ; ưu tiên docs+footgun+dead UI+test trước move `routes_*`. (Superseded một phần bởi full layout A–D cùng ngày.)

- **11-04 (V5 assets/fs attach + OpID)** Tiếp declutter: `assets`+`fs` cùng pattern attach; hết `@app` API còn lại trên `server.py`. GET+HEAD → `operation_id` riêng (`job_video`, `hg_library_preview`). Archive oneshot scripts + xoá tauri `node_modules` attic. Backup `Z:\PinelineV2_codebak\2026-11-04_v5-assets-fs-attach\`.

- **11-04 (V5 queue/jobs SSOT)** User: nâng cấp V5 gọn, hết chắp vá dual route/manifest. Chọn: **một thân handler trong `server.py`** + **một bản đồ path** `pineline.server.routes.{queue,jobs}.attach` + `include_router` (giống quyết định jobs 11-02). Xoá bản copy dead trong package `queue.py`. Metadata list → `films.db`; live progress → 1 manifest (`current`). Hợp đồng: `docs/MANIFEST_CONTRACT.md`. Không port pattern này sang V2/V4 trong đợt này. Backup `Z:\PinelineV2_codebak\2026-11-04_v5-queue-ssot\`.

- **11-02 (review lock)** 31B chỉ mượt văn; CẤM đổi self/call khi pronouns_locked (prompt + filter).

- **11-02 (pronoun A–C)** User: làm hết V2+V4+V5 — analyze full ZH (lô+memory) → lock → ledger → QA/GPT vá. Không đợi diarization. Backup Z:\PinelineV2_codebak\2026-11-02_pronoun-consistency-abc\.

- **11-02 (pipeline LLM 3 tầng)** Sync V4: local dịch → GPT name/pronoun → REVIEW `gemma4:31b-cloud` + `CLOUD_LLM_*`. Backup `Z:\PinelineV2_codebak\2026-11-02_review-31b\`.
- **11-02 (Aurora GPT pass ngắn)** Sync V4: `chatgpt/` route + `NAME_MODEL`/`PRONOUN_MODEL`; translate bulk vẫn local. Backup `Z:\PinelineV2_codebak\2026-11-02_aurora-name-pronoun\`.
- **11-02 (xưng hô translate)** Đồng bộ với V4: `apply_pronoun_postpass` + `agent_pronoun_pass` + inject cảnh; Agent review = tên → xưng hô → văn phong. Backup `Z:\PinelineV2_codebak\2026-11-02_v4-pronoun-pass\`.
- **11-02 (jobs registry)** Tiếp khung V5: `/api/jobs/*` đăng ký qua `pineline.server.routes.jobs.attach` (bảng path→handler). Thân hàm **giữ trong `server.py`** (xen helper ~1.7k dòng) — tránh big-bang AST move (extractor unparse đã thử và rollback). Bỏ `@app` trên jobs; `include_router` sau queue. Tiếp: assets registry hoặc chuyển dần body jobs.
- **11-02 (khung thư mục)** User: cần cấu trúc khung rõ ràng hơn trên V5.
  - Thêm package **`pineline/`** làm bản đồ + chỗ chuyển dần: `server/routes`, `server/services`, `pipeline`, `agents`, `sidecar`, `desktop`, `ops` (mỗi nhánh có README).
  - Code runtime cũ **giữ ở root** đến khi từng cụm LIVE; không big-bang move.
  - Đợt 1 LIVE: `pineline.server.routes.queue` (`/api/queue/*`); `server.py` `include_router` + re-export tên cũ cho test/`check_batch*`.
  - Route trong package `pineline.*` dùng **lazy `S` proxy** (không `import server` top-level) để tránh circular import khi server nạp router.
  - Launcher **`run_v5.bat`**, default port **8805** (desktop/restart/tele/migrate/canva/agents).
  - Tiếp theo (cùng khung): `jobs` → `assets` → chuyển `routes_ui/hg/agent` vào `pineline.server.routes`.
- **11-02** Refactor cấu trúc codebase (dễ đọc / ổn định) — **không sửa inplace trên V4**.
  - Tạo tree riêng **`Z:\PinelineV5`** (copy từ V4). V4 = bản ổn định / restore; production ops vẫn theo V4 (:8804) cho đến khi user chuyển.
  - V5 dùng cổng **:8805**, temp `D:\PinelineV5_tmp`, work mặc định `D:\PinelineV5_work` (tránh đụng process/data V4).
  - Phương án kỹ thuật: **A** — tách dần `server.py` theo cụm `routes_*` (queue → jobs → assets), giữ `import server as S` như đợt 7; không big-bang package.
  - Mọi thay đổi refactor **bắt buộc** ghi thêm mục vào `DECISIONS.md` (V5) + CHANGELOG/worklog; trước mỗi đợt sửa: zip snapshot + codebak.
  - Nếu V5 fail: xóa/đổi tên `Z:\PinelineV5`, giữ nguyên V4; khôi phục từ zip trong `Z:\PinelineV2_codebak\2026-11-02_v4-to-v5\` / snapshot log.

## 2026-10

- **10-08** V3: nhiều key LLM xoay vòng (429/401/403) — **chỉ V3**, V2 giữ 1 key. UI3 + Hongguo hiển thị **trong launcher** bằng WebView2 (tkinter không render được web hiện đại; viết lại UI3 bằng tkinter quá lớn) — bỏ UI4 khỏi V3.
- **10-08** Tạo **V3 portable** ở `Z:\PinelineV3` (V2 giữ nguyên, vẫn là bản chạy chính). Launcher tkinter + exe; gói code + Python, model tải lần đầu; mang cả Hongguo + llama-server; GPU tự dò (cu128 để chạy được RTX 50xx); LLM mặc định **Ollama Cloud** bằng key người dùng nhập, 9router chỉ dùng qua preset Custom. Kích thước thực ~10,8 GB (torch cu128 riêng 6,9 GB) thay vì ~6 GB user ước.
- **10-07** Hàng đợi gộp Hongguo **lưu ra file** và restart server phải tôn trọng nó như queue render (chặn restart khi đang gộp). Xếp hàng chỉ ghi tên; việc nặng (ffprobe, chuẩn hoá 1080p, dọn tập lẻ) làm trong worker để UI không bị treo.
- **10-07** Video nguồn lấy **trực tiếp từ `D:\Lib`** (user chọn thay cho hard link): job không giữ bản sao/link, chỉ ghi đường dẫn thư viện trong manifest. Không viết lại pipeline (user: không cần test lại toàn bộ) — chỉ đổi chỗ chọn đường dẫn lúc import. File ngoài thư viện vẫn hard link/copy. Job cũ (0281, dccc bản sao; 5 job hard link) **giữ nguyên** — chỉ áp dụng từ job tiếp theo.
- **10-07** User duyệt mẫu `sfx_lib` → CONFIG BATCH dùng `sfx_lib`. Yêu cầu chỉnh: nhạc kho nhỏ hơn, tiếng động gốc to hơn nhưng vừa phải, giọng Việt to hơn (đặt 0,25 / 0,62 / ×1,25, có limiter). Bản tách CDX23 giữ bản nhanh (user chưa chọn khác).
- **10-07** Bỏ hẳn nhạc nền gốc vì claim Content ID (vd "Latin Zumba Dance Workout – Liberektro"). User không muốn dò từng bài sau khi bị claim (phức tạp với video dài) → chọn công thức **giọng Việt + tiếng động gốc + nhạc mới sạch bản quyền**: tách tiếng động bằng CDX23 (MIT), nhạc lấy từ **YouTube Audio Library** (Attribution not required, Ambient/Cinematic), chọn theo mức êm/vừa/dồn dập đo từ nhạc gốc. Mặc định CDX23 1 checkpoint (đo: sót nhạc không hơn bản 3 checkpoint, nhanh ~3×). Chế độ `sfx_lib` có trong UI/CONFIG BATCH nhưng **chưa đổi CONFIG BATCH** (vẫn `duck`) tới khi user duyệt mẫu. Không dùng MusicGen (license cấm thương mại), không dùng Pixabay (nhiều bài dính Content ID).
- **10-06** (đợt 7) Gỡ UI cũ `index1/2.html` + route `/ui1`, `/ui2` (user chọn). Tách `server.py` theo nhóm route bằng `APIRouter`; code chuyển đi gọi server qua `S.<tên>` (không `from server import …`) để patch trong test vẫn ăn và không nạp server 2 lần. Phần jobs/queue/pipeline giữ trong `server.py` vì check đợt 1–4 đọc mã nguồn của nó. Code mới chỉ có hiệu lực khi restart, restart chỉ khi hàng đợi rảnh hoặc user đồng ý.
- **10-06** (đợt 6) Có git local (không remote, không push). Secret và dữ liệu job không vào git. Script một lần ở gốc chuyển ra `codebak\…\attic` (không xoá). UI cũ `index1/2.html` giữ nguyên tới khi user quyết. Không tách file lớn khi đang có job chạy.
- **10-06** (đợt 5, theo review user chọn làm) Telegram:
  - Lệnh đổi trạng thái **phải có `/`**. Chữ trơn chỉ nhận gợi ý; câu dài thì chuyển cho agent.
  - Agent muốn dừng hàng chờ/job, gộp/dọn tập, chạy A-Z, chạy lại `force`, reset config, heal hàng loạt → **gửi nút ✅/❌**, bấm ✅ mới chạy (hết hạn 15 phút).
  - Panel Agent trên UI giữ như cũ (đã tick cho phép thì chạy thẳng).
  - `hg_auto_flow` từ agent chạy nền, mỗi bộ một flow.
  - Xoá `agent_v2/`.
- **10-06** Làm tiếp **đợt 2–6** review. Restart server: **hẹn sau khi f9fe xong** — rút 3a2e khỏi hàng đợi tạm, restart, xếp lại 3a2e.
- **10-06** (đợt 4, theo review user chọn làm) Auto-pilot **không tự xếp lại job failed** và job HOLD / QA chặn — job lỗi phải xem rồi xếp tay, HOLD chờ duyệt. Bấm Tạo giọng / Render / Dịch lại / Ghép khi job đang chạy (hàng đợi hoặc stage running) → từ chối 409 thay vì chạy song song. Server và sidecar chỉ chạy 1 bản (khoá file).
- **10-06** (đợt 3) Opts job một nguồn: config batch → `queue_opts` của job → tham số truyền thêm. Agent `mux_run` render lại theo đúng opts job đã chạy (không còn ép motion/LUT/4M/tắt logo). Giọng **không** lấy từ config batch khi xếp hàng qua API/queue (giữ luật cũ: job thiếu giọng → báo lỗi).
- **10-06** (đợt 2) API key **chỉ đặt trong `pineline.config.json`**; `.bat`/`config.json`/code không chứa key. Backup zip tự che secret. Server/sidecar chỉ nhận Host/Origin local. LLM sập → dừng stage dịch (pending, bấm Tiếp tục), không để trống câu.
- **10-06** Luôn **backup trước khi sửa** (zip toàn project + bản gốc từng file vào `Z:\PinelineV2_codebak\<ngày>_<đợt>\`) và ghi md đủ để biết đã sửa gì. Làm đợt 1 review trước; restart server **để sau**.
- **10-06** Tập lẻ sau gộp: **chuyển vào thùng rác, giữ 7 ngày** rồi mới xoá hẳn (không xoá ngay). Thùng rác đặt `D:\Lib_trash\<bộ>\<thời điểm>\` (ngoài `D:\Lib` để không bị quét như tập/bộ mới).
- **10-06** Docs: mọi thay đổi phải có markdown trong `docs/` (rule `docs-on-change.mdc`). Huỷ các câu hỏi đang treo (restart server, tắt llama-server).
- **10-06** Che hardsub stretch: **đệm 15/13 px** giữ nguyên — mọi mức mỏng hơn (12/11, 10/9, 6/4, 3/2) lọt nét ở ký tự cao (job 2ef87, t=2688,5 s).
- **10-06** Che hardsub stretch: **không làm mềm (sigma 0/0)** — user so 0/0, 0,6/1, 0,8/1 và chọn 0/0.
- **10-06** Che hardsub: chuyển từ blur sang **vệt kéo giãn giữ màu cảnh** (`HARDSUB_STYLE=stretch`), 1 lớp, gộp nhiều vị trí cùng lúc thành 1 dải. Giữ font sub. **Không render lại 2ef87.**
- **10-06** Mùa 1 chạy trước mùa 2 (kế thừa glossary/xưng hô đã duyệt).
- **10-05** Job 2ef87: để nguyên 21/93 lô review lỗi. Giữ `openclaw` làm fallback agent dù combo đang hỏng.
- **10-05** Model LLM lấy theo file config (file-first) cho dịch/review/agent: `ollama/gemma4:31b-cloud` qua 9router.
- **10-05** Render chia khúc: khúc 300 s, 3 song song (thay chia đôi), sau test 5 phút × 3 đạt.
- **10-04** Bỏ lớp đen hardsub; chỉ che đúng toạ độ chữ dò được theo đoạn (`HARDSUB_MODE=track`), bám zoom.
- **10-04** Video >12 h: cắt copy thành part cho YouTube (0281 → part1/part2).
- **10-04** LUT: giữ `lutrgb` trên CPU, không chuyển libplacebo (chậm hơn + lệch màu). Dùng ffmpeg 8.1.2 full_build.
- **10-03** Tăng tốc render: làm chia đoạn song song (đo 4,1×); LUT dùng lutrgb.
- **10-03** Hongguo preview/rank/catalog đưa vào Telegram + agent.

## 2026-09

- **09-30** Bản dịch: user tự sửa `sub.vi.srt` của cc52 → ghép ngược vào `script.json` rồi TTS lại; đổi "anh tôi/cô tôi" (他/她) thành "anh ta/cô ta".
- **09-30** Preset gemma4-26b-qat-mtp dùng `--fit` 131k (thay `-ngl 99 --n-cpu-moe 16`).
- **09-29** Agent: rà tên + văn phong trước TTS (sau khi dịch 100%); feeder tự thêm job khi hàng chờ trống, mặc định OFF tới khi có yêu cầu.
- **09-29** Database phim SQLite `data/films.db` + `/films/ui`; thư viện `/lib` qua Telegram.
- **09-29** YT uploader: mỗi tài khoản khoá 1 IP proxy, kiểm IP trước mọi request; proxy chết thì không upload (không rơi về mạng thẳng). Token Google không gửi bên thứ ba.
- **09-28** YT uploader tách ra `Z:\yt_uploader`, đa tài khoản đặt tên, sửa hàng loạt, thumbnail nhiều file.
- **09-28** Agent dùng 9router `gemma4:31b-cloud` mặc định.
- **09-27** Chuyển `work` sang `D:\PinelineV2_work` (junction từ Z) để không tranh ổ với Windows.
- **09-27** Config batch dùng chung (`batch_config.json`) cho UI3/UI4/Agent/Telegram/Auto-pilot; đổi config thì job chưa chạy theo luôn, job đang chạy giữ config cũ.
- **09-27** Mỗi job bị ép snapshot opts khi đến lượt (không kế thừa leftover). STOP = dừng hết + tắt Auto-pilot.
- **09-27** Tách 2 LLM: Agent → 9router, job → local (phương án 1, env tách). Sau đó (10-05) job cũng chuyển 9router.
- **09-27** YT uploader là app desktop (không web UI).
- **09-26** Auto-pilot: nút + lệnh, điều khiển qua Telegram; không restart server khi đang chạy.
- **09-26** Chỉ làm trên V2 (`Z:\PinelineV2`), không đụng V1 (`Z:\Pineline`, :8800).
- **09-26** UI4 Ops: layout danh sách dự án trên-trái, preview trên-phải, pipeline dưới-trái, kịch bản dưới-phải; form + Job trên UI4; chọn nhiều folder bằng hộp thoại Windows.

## 2026-11-08 — Python default sau update 3.15

- **Quyết định:** A+B — bỏ Python315 khỏi Machine PATH; C:\Python312 đầu PATH; PY_PYTHON=3.12. Giữ 3.15 cài tại C:\Python315\ (gọi full path nếu cần). Launcher Pineline pin 312 thêm lớp dự phòng.
- **Không chọn:** Cài deps lên 3.15; chỉ pin từng project.
