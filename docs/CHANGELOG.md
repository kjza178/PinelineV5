# Changelog

Mới nhất trên cùng. Mỗi mục: file/hàm — thay đổi — cần restart gì. Chi tiết bug: docs/fixes/. Nhật ký phiên: docs/worklog/.


## 2026-11-20

- **Sync V2 → V4/V5** (00:30 21/11) — agent/translate/server + `translate_simple` (CJK backup repair, PLAN backup) + toàn bộ `docs/fixes/2026-11-20-*.md` + DECISIONS/CHANGELOG/STATE. tree_audit ERROR=0. **Restart V4 :8804 / V5 :8805** nếu đang chạy bản cũ (yes/no).
- **Vá CJK/empty bằng Aurora sau DeepSeek** — còn cờ cứng sau `repair` chính → 1 lượt `repair` backup (không chỉ câu chưa rv). Ops `233da4eb69fb` i=882 `投影`→`hình chiếu` + resume. Test `test_cjk_backup_repair`. Bak `codebak\2026-11-20_cjk-backup-repair\`. Fix `docs/fixes/2026-11-20-cjk-backup-repair.md`. **Restart :8801** (yes/no).
- **Plan/soát luôn main + backup** — `PLAN_MODEL_BACKUP` (mặc định Aurora `chatgpt/gpt-6`); `build_plan` thử main→backup (A7/file/sample); soát: thiếu `review_backup` = aurora_parallel (chỉ `off` tắt). Test `test_plan_backup` 5. Bak `codebak\2026-11-20_plan-review-main-backup\`. **Restart :8801** (yes/no).
- **Ops: HOLD CJK `9aa0891fbfd1_p01` i=187** — sửa VI `C位`→`vị trí C`, gỡ HOLD; parent thức → translate done → TTS running. **Không restart.**
- **Agent resolve job id rút gọn `9aa089_p01`** — `resolve_job` nhận `prefix_pNN`; `_dispatch` chuẩn hoá mọi `job_id`; `script_peek`/`pineline_job` trả `hold_reason` + `cjk_in_vi_sample` (zh/vi). Test `test_agent_resolve_job` 4. Bak `codebak\2026-11-20_agent-resolve-job\`. Fix `docs/fixes/2026-11-20-agent-resolve-short-job-id.md`. **Restart :8801 + :8802** (yes/no).
- **Auto-publish hỏi Telegram trước upload (phần 1)** — `ask_before_upload`; `/publish status|on|off|ask|auto|privacy|thumb|queue`; nút ✅/⏭/🔒/🌐; TTL 60' skip. Test `test_publish_ask` 4. Bak `codebak\2026-11-20_publish-ask\`. Fix `docs/fixes/2026-11-20-publish-ask-telegram.md`. **Restart :8802 + :8801** (yes/no).
- **Prompt thumb đơn giản (ref + title + typo nền)** — bỏ khóa 3D-Latin/UE5/ice-chrome; giữ dấu Việt; badge thêm `FULL`; `hooks_from_series_title` tách `A - B - Ta…`. Test meta+autopub 11 pass. Bak `codebak\2026-11-20_thumb-prompt-simple\`. Fix `docs/fixes/2026-11-20-thumb-prompt-simple.md`. **Restart :8801** nếu auto-publish in-process (yes/no); Meta CLI/`importlib` reload `meta_studio` không bắt buộc.
- **Films UI Nhật ký: ✕ không bị poll mở lại** — `opsLogHide` + `sessionStorage`; push/ingest/`combineRender`/`normRender`/poll test chỉ `opsLogRender` (không `OPS_LOG_HIDDEN=false`). Mở lại khi bắt đầu gộp/chuẩn hóa hoặc nút «📋 Nhật ký». Bak `…_0415_ops-log.zip` + `codebak\2026-11-20_ops-log-no-auto-show\`. Fix `docs/fixes/2026-11-20-ops-log-no-auto-show.md`. **Hard refresh Films UI** — không restart.
- **Queue Stop treo ghế khi `_gpu` future còn pending** — `_queue_run_one` bỏ `done_event.wait()` vô hạn: poll 1s + `fut.cancel()` khi Stop và future chưa chạy (TTS/ASR khác giữ `JOB_WORKERS=1`) → nhả claim + `"stopped"`. Test `test_stop_cancels_pending_gpu_future`. Bak `Z:\PinelineV2_backup_2026-11-20_0235.zip` + `codebak\2026-11-20_queue-stop-gpu-wait\`. Fix `docs/fixes/2026-11-20-queue-stop-gpu-wait.md`. **Cần restart :8801** (đang TTS `72450cea31aa_p01` — hỏi yes/no).

## 2026-11-19

- **Films UI Test BQ: hiện kết quả khi dừng quota** — trước ẩn banner/status khi `running=false` nên chỉ còn 2 dòng cắt/upload trong nhật ký, không thấy «0 up / uploadLimitExceeded». Giữ banner + status card kết thúc (lỗi đỏ), toast + dòng log cuối. Bak cùng `…_films-ui-unified-log\`. **Hard refresh Films UI**.
- **Films UI: gom log về 1 bảng «📋 Nhật ký»** — bỏ 2 khung góc phải riêng (`normBox` / `combineBox` + `layoutSidePanels`). Nguồn: Gộp job (`/films/combine/status`), Chuẩn hóa (`/api/hg/library/normalize/status`), Test bản quyền (batch-progress). Lọc All/Gộp/Chuẩn hóa/Test BQ; status card + bảng Giờ|Nguồn|Nội dung. Banner test giữ nút dừng/recheck, chi tiết đổ vào nhật ký. Bak `Z:\PinelineV2_codebak\2026-11-19_films-ui-unified-log\`. **Hard refresh Films UI** — không restart.
- **Meta form: typography không gắn cứng tên phim / lửa vàng** — `finalize_thumb_meta_fields` giữ hook/concept LLM (`require_title_anchor=False`), giữ `master_image_prompt` LLM (chỉ patch badge/hook/sub); UI fallback bỏ scene «giơ tay bắn lửa». Auto-publish vẫn neo title riêng. Test meta+autopub 10 pass. Bak `…_meta-typo-free-form\`. **Hard refresh Films UI**; `/meta/*` reload `meta_studio` — không bắt buộc restart :8802.
- **Gộp job: F5 mất khung log dù vẫn chạy** — `importlib.reload(films_combine)` mỗi poll xoá RAM; status giờ đọc log/state đĩa; tele_cmd không reload module; UI hiện lại khi còn log. **Hard refresh UI**; **không restart :8802** khi đang gộp. Restart :8802 sau khi xong. Fix follow-up trong `docs/fixes/2026-11-19-films-combine-progress-log.md`.
- **Xoá job/part: DB mất nhưng work/ còn vài GB** — `film_db.delete_*` robust rmtree + báo `work_failed`; xoá parent kèm `_pNN`; API mặc định `delete_work=True`; UI luôn tick đĩa + kèm part; `GET /films/orphan-work` + `POST /films/purge-orphan-work` + banner. Probe: 19 orphan (~175 GB, 9 part). Test `tests/test_films_delete_orphan.py` (4). Bak `…_films-delete-orphan\`. Fix `docs/fixes/2026-11-19-films-delete-orphan-work.md`. **Cần restart :8802**. Orphan cũ chờ user yes/no purge đĩa.
- **Films UI gộp job: log + % tiến độ** (`films_combine.py` mới; `agent_feeder.combine_rendered_jobs` / `_concat_videos_smart` `on_progress`; `agent_tele_cmd` POST nền + `GET /films/combine/status`; `films_ui.html` khung 🔗). Trước: toast sync treo đến khi ffmpeg xong. Log: console :8802 + `work/logs/films_combine.log`. Test `tests/test_films_combine_progress.py` (3). Bak `Z:\PinelineV2_codebak\2026-11-19_films-combine-log\`. Fix `docs/fixes/2026-11-19-films-combine-progress-log.md`. **Cần restart :8802** (+ hard refresh Films UI).

## 2026-11-18

- **Aurora = DỰ PHÒNG thật cho soát simple** (user 22:41 — «Aurora chỉ chạy khi DeepSeek không hoạt động»): trước đây `review_backup=aurora_parallel` (Config Batch `REVIEW_BACKUP`) ép `_resolve_review_model` → `AURORA_REVIEW_MODEL` (chatgpt/gpt-6) soát TOÀN BỘ, DeepSeek không chạy (vd 7dd93f48f052: 2648 câu × lô 200 qua Aurora).
  - `translate_simple/cfg.review_model`: model chính = `SIMPLE_MODEL` / `REVIEW_MODEL` (DeepSeek), không đọc queue_opts. MỚI `cfg.backup_model(work_dir)` = `AURORA_REVIEW_MODEL` khi job bật `aurora_parallel`; `cfg.backup_batch()` (`SIMPLE_BACKUP_BATCH`=30).
  - `stage_review.run(backup_model=)`: lượt chính bằng DeepSeek; câu còn chưa rv (lô lỗi sau retry / rỗng / bỏ sót) → làm lại bằng Aurora lô ≤30, workers theo Aurora; log `[simple-review] N câu … lỗi/bỏ sót → dự phòng chatgpt/gpt-6`, stats `backup={model,n,ok}`. Không bật → thử lại cùng model như cũ.
  - `pipeline`: truyền backup cho review chính + soát bổ sung; in `[simple] soát chính … · dự phòng …`.
  - Nhãn UI/Config Batch: «Aurora GPT∥» → «Aurora dự phòng». Luồng legacy giữ nghĩa cũ.
  - Test `tests/test_review_backup.py` (3) + `test_review_parallel_workers` (legacy) vẫn qua. V2/V4/V5. **Cần restart :8801.**
- **Thumb AI: poster-only + hook neo title** (~22:40). Job `c7367a659c46`: frame video lệch cast + hook LLM «CẤM ĐỊA…» → thumb ≠ poster. `get_job_reference_images(include_video_frame=False)` mặc định; auto-publish chỉ poster, luôn rebuild prompt từ `hooks_from_series_title`, bỏ story/visual_dna LLM. Invalidate series master thumb lệch. Test 10 pass. Bak `…_thumb-poster-only-title-hooks\`. Fix `docs/fixes/2026-11-18-thumb-poster-only-title-hooks.md`. **Cần restart :8801.**

- **Agent chat: thử lại khi lỗi tạm, không fallback** (user 19:43): `agent_core._chat_turn` thử lại CÙNG model `AGENT_RETRIES` lần (mặc định 2, chờ `AGENT_RETRY_WAIT`=3 s × lượt) khi lỗi tạm (HTTP 429/5xx, Aurora «Error in message stream», timeout, mất kết nối); 4xx/lỗi khác → báo lỗi ngay. Test `tests/test_agent_retry.py`. V2/V4/V5. **Cần restart :8801/:8802.**
- **Bỏ fallback `openclaw` của Agent chat** (user 19:00): `AGENT_FALLBACK_MODEL=openclaw` → `set "AGENT_FALLBACK_MODEL="` trong run_v2.bat / run_tele_cmd.bat (V4: run_tele_cmd.bat; V5: apps/run_tele_cmd.bat); `scripts/check_batch2.py` kiểm ngược lại. Lý do: combo openclaw nằm trên 9router LAN 192.168.31.247 (đã bỏ 17/11) và `agent_core._chat_turn` gửi model fallback tới CÙNG base Aurora :3377 → luôn lỗi, chỉ thêm 1 lần thử vô ích. **Cần restart :8801/:8802 (mở lại cửa sổ .bat)** để hết env cũ.
- **Soát bổ sung chia lô theo số câu** (user 18:54): `translate_simple/pipeline._review_missing` dùng `cfg.missing_batch_for(n)` — còn ≤ `SIMPLE_MISSING_SMALL_MAX` (5) câu → lô `SIMPLE_MISSING_BATCH` (4) như cũ (câu rác/khó); nhiều hơn → lô thường `SIMPLE_BATCH` (30). c7367a659c46_p01: 81 câu OCR lượt B đổi chữ trước đi 21 lô × 4 (mỗi lô kèm cả plan) → nay 3 lô. Test `tests/test_missing_batch.py`. V2/V4/V5. **Cần restart :8801.**
- **Job mới bị khoá nhầm luồng dịch cũ (legacy)** (c7367a659c46_p01 chạy `run_translate` + upload SRT lên Aurora «pronoun-analyze»): server `mark_running(translate)` (started_at/status=running) TRƯỚC khi hỏi luồng → `translate_simple/cfg._infer_job_pipeline` coi là dấu vết legacy rồi đóng dấu luôn. Sửa: chỉ tính legacy khi `script.json` đã có câu VI hoặc stage translate done/error/failed (`_script_has_vi`). Test `tests/test_pipeline_infer.py` (3). V2/V4/V5. **Cần restart :8801** (V4/V5: server của bản đó).
- **Thumb: bỏ Pillow — chỉ ảnh gốc + /images/edits** (~04:15). User bác Pillow. `auto_publisher` xoá fallback `create_thumbnail`. Có ref → luôn edits, echo roll 6 lần; không generations; fail → YouTube mặc định. Test 8 pass. Bak `…_thumb-ai-edits-no-pillow\`. Fix `docs/fixes/2026-11-18-thumb-ai-edits-no-pillow.md`. **Cần restart :8801.**

- **Thumb: không generations khi có poster** (~04:10). (Thu hồi nhánh Pillow — xem mục trên.) Root: Free-pool edits echo → generations bịa nhân vật. `fallback_generations=False` khi có ref. Bak `…_thumb-poster-faithful\`.

- **Prompt thumb: appearance = ảnh gốc, text chỉ pose** (~03:52). `build_master_image_prompt`: `APPEARANCE SOURCE OF TRUTH`; đổi `CHARACTER & POSE` → `POSE / ACTION / ENERGY`; lọc `visual_dna` nếu toàn áo/mặt. Test cập nhật. Bak `…_prompt-ref-pose\`. Demo ảnh chờ `:3377`. **Không bắt buộc restart** cho Meta CLI; **restart :8801** nếu muốn auto-publish in-process.

- **Auto-publish thumb: ref ảnh gốc + typo title** (~03:50). User chốt: ảnh gốc = reference; nung chữ từ title (linh hoạt/đẹp/đa dạng). `auto_publisher`: `get_job_reference_images` + `allow_edits=True` khi có ref; sửa check prompt LATIN (trước so «VIETNAMESE» → mất typography_direction). `build_master_image_prompt`: POSTER TEXT CLEANUP + typo đa dạng theo nền. Test `test_autopub_ref_typo`. Bak `…_autopub-ref-typo\`. Fix `docs/fixes/2026-11-18-autopub-ref-typo.md`. **Cần restart :8801.** Series master thumb cũ xấu → gen lại.

- **Meta Studio: thumb + Up ảnh gốc** (~02:20). Root: `:8801 GET /films` bị `routes_ui` trả HTML → tab Đã làm/Meta gãy; Meta thiếu upload ảnh gốc. `routes_films.py` (mới); `routes_ui` bỏ HTML `/films`; `films_ui` fallback `:8802` + nút Up ảnh gốc + `poster_b64`. Test `test_meta_ref_upload`. Bak `…_meta-thumb-upload-ref\`. Fix `docs/fixes/2026-11-18-meta-thumb-upload-ref.md`. **Hard refresh Done list; restart :8801+:8802** cho native.

- **DeepSeek: TẮT thinking mặc định** (user chốt 00:46) — `llm._deepseek_chat` gửi `"thinking": {"type": "disabled"}`. Lý do: `deepseek-flash` (V4.1 Flash) bật thinking mặc định (effort high), token suy nghĩ tính vào max_tokens → plan cả phim trả content rỗng; mọi lần gọi chậm + tốn token đầu ra. Bật lại: `DEEPSEEK_THINKING=enabled` (hoặc low/high/max = reasoning_effort) — khi bật max_tokens tự +8192. Script kiểm `scripts/test_deepseek_plan.py <job> [--thinking enabled|--compare]` (bản sao asr.json, không đụng job, in finish_reason/tokens từng lần gọi). Test +1. **Cần restart :8801.**

- **DeepSeek trả rỗng bị coi là 5xx → gửi lại cả phim tới 16 lần** (b138b16bef8f_p01 «[simple-plan-a7] cloud lỗi tạm … DeepSeek (deepseek-flash) thất bại sau 4 lần: None»):
  - `llm._deepseek_chat`: 200 + `content` rỗng → log rõ `finish_reason`, prompt/completion tokens, max_tokens, độ dài reasoning, json_mode; thử lại đúng 1 lần không JSON mode; `finish_reason=length` → không thử lại. Ném `LLMEmptyResponse` (mới, con của LLMUnavailable) thay vì «thất bại …: None».
  - `cloud_retry.classify_cloud_retry`: `LLMEmptyResponse` → không thử lại (trước: khớp «thất bại» → transient, chờ ~109 s × 4 lượt).
  - `translate_simple.stage_draft.build_full_movie_plan` (A7): rỗng vì `length` → thử lại 1 lần với max_tokens ×2 (≤32768); lý do khác → lỗi lên ngay → `translate.build_plan` rơi xuống plan file/sample như cũ.
- **Brain quét QA job chưa dịch xong** (b138b16bef8f_p01 `phase=idle high=2514`, mọi câu VI trống = cờ empty_vi): `agent_brain` action qual bỏ qua phase `idle` không HOLD (`skipped=not_translated`) — hết spam log/phiếu LLM, `agent_qa_fix` không dịch lẻ câu trước bước dịch chính.
- Test `tests/test_deepseek_empty_and_brain_idle.py` (6). Backup `.backup_dsempty_20261118/`. **Cần restart :8801** (job đang dịch sẽ bị cắt — chờ queue rảnh).

- **Chuẩn hóa NHIỀU mùa + kiểm đã chuẩn + log về sidecar** — `lib_normalize.py` (viết lại), `hongguo_bridge.normalize_merged_file`, `agent_tele_cmd.py`, `films_ui.html`, `routes_hg.py`:
  - Films UI: nút **📐 Chuẩn hóa đã tick** (thanh Hàng chờ) — các mùa tick (`.pick`, state ready; chưa ghép thì bỏ + báo). Mỗi mùa KIỂM trước: metadata `comment=pineline_norm_v1` (đã chuẩn) hoặc `merge_check.json` ok (gộp mới đã kiểm tập + mối nối) → **bỏ qua**; gộp cũ / gộp báo lỗi / ffprobe không đọc → chuẩn hóa. Chạy lần lượt 1 ffmpeg/lúc; ⏹ huỷ hàng chờ. 📐 từng mùa = luôn chạy (lên đầu hàng).
  - Mùa không chuẩn hóa được → `failed` + lý do (thiếu file gộp / ffmpeg + 3–8 dòng lỗi cuối), toast + khung bên phải.
  - **Chạy + log trong sidecar :8802** (không qua :8801 nữa): console :8802 `[normalize] …` (mỗi 10 % / 2'), `work/logs/lib_normalize.log`, và log 60 dòng trong khung Films UI (nút Log). API (:8802): POST `/api/hg/library/normalize`, `/normalize/batch`, `/normalize/cancel`, GET `/normalize/status`.
  - `normalize_merged_file`: bỏ gói hỏng (`-err_detect ignore_err`, `+genpts+discardcorrupt`, `aresample async`) như hg_merge_check; NVENC lỗi → thử lại libx264; tiếng AAC 48k **stereo**; gắn `comment=pineline_norm_v1`; `auto_orient` (lib_normalize bật): nguồn dọc → 1080x1920 (hết viền đen 2 bên).
  - Chưa: chặn khi job Pineline đang đọc chính file đó; tranh GPU với job đang chạy (NVENC).
  - Test `tests/test_lib_normalize.py` 5/5. **Cần restart :8802** (+ :8801 nếu muốn route cũ dùng code mới).

## 2026-11-17

- **Chuẩn hóa 1080p (Films UI) chạy nền + tiến độ/log** — `lib_normalize.py` (mới), `hongguo_bridge.normalize_merged_file`, `routes_hg.py`, `agent_tele_cmd.py`, `films_ui.html`:
  - POST `/api/hg/library/normalize` giờ trả ngay, encode chạy nền (1 bộ / lần; bấm lại = xem tiến độ). GET `/api/hg/library/normalize/status[?name=]` (sidecar :8802 chuyển tiếp cả 2).
  - Tiến độ: phase (probe → encode → replace → done), %, thời lượng đã encode / tổng, tốc độ, còn ~bao lâu, số dòng lỗi giải mã ffmpeg + dòng lỗi cuối. Lỗi trả `error_tail` (15 dòng cuối ffmpeg) thay vì chỉ `rc`.
  - Log: console :8801 `[normalize] <bộ>: …` mỗi ~5 % / 60 s + `work/logs/lib_normalize.log`. UI: khung góc phải tự cập nhật 3 s/lần, mở lại trang vẫn hiện.
  - Route: dùng `safe_child` (chặn `..`), ưu tiên `*(merged).mp4`, bỏ file `.norm.*`.
  - Chưa đổi: vẫn ép 1920×1080 (video dọc bị viền), chưa thêm cờ bỏ gói hỏng/fallback libx264, chưa chặn khi job đang dùng file.
  - Test `tests/test_lib_normalize.py` (3). **Cần restart :8801 + :8802.**

- **Films UI nút 📐 1080p báo «❌ Lỗi chuẩn hóa: not found»** — `agent_tele_cmd.py` do_POST: trang `/films/ui` do sidecar :8802 phục vụ, nút gọi `/api/hg/library/normalize` (tương đối) nhưng route chỉ có ở :8801 (`routes_hg.py`) → 404. Thêm chuyển tiếp sang :8801 (timeout 3h vì encode đồng bộ). Chưa sửa: chạy nền + tiến độ, cờ bỏ gói hỏng/fallback libx264, khung dọc, safe_child, khoá, chặn khi job đang dùng (đã báo user). Backup `.backup_normproxy_20261117/`. **Cần restart :8802.**

- **Chuẩn hóa Video 1080p Full HD Thư Viện D:\Lib & Nút bấm chuẩn hóa trên Films UI**:
  - `hongguo_bridge.py`: Thêm `"-ar", "48000"` vào lệnh FFmpeg trong hàm `normalize_merged_file` để chuẩn hóa âm thanh lên tần số lấy mẫu chuẩn YouTube 48kHz (AAC 192k).
  - `routes_hg.py`: Thêm API endpoint `POST /api/hg/library/normalize` nhận `name` thư mục mùa phim, tự động gọi `normalize_merged_file` với card đồ họa NVIDIA NVENC.
  - `films_ui.html`:
    - Thêm nút `📐 1080p` tại từng mùa trong thẻ Thư Viện (cạnh nút `🛡️ Test` và `🗑️ Xoá`).
    - Thêm nút `📐 Chuẩn hóa 1080p` bên trong modal `🛡️ Kiểm tra Bản Quyền YouTube (Trước khi làm)`.
    - Thêm hàm JavaScript `normalizeSeasonVideo(name)` hiển thị xác nhận và gọi API với toast thông báo tiến độ.
  - Chuẩn hóa thành công bộ `异能战争,我七十亿双眼监控全球` về chuẩn Full HD 1080p (`1920x1080`, 30fps, AAC 48k, NVENC).
  - Không cần restart server ngay nếu chỉ dùng Films UI (nạp lại khi queue rảnh).

- **HOLD QA bổ sung (qaask2): xem ngữ cảnh, /qa <job>, agent sửa câu** — `agent_qa_ask.py`, `agent_tele_cmd.py`, `routes_agent.py`, `agent_core.py`:
  - Reply `?` hoặc `#380 ?` vào tin HOLD QA → ±3 câu ZH/VI quanh câu bị cờ (▶), không gọi LLM, không đổi script (`QA_ASK_CONTEXT`=3). Sidecar đọc job từ chữ «HOLD QA <job>» trong tin được reply (tin nào cũng có dòng này).
  - Lệnh Telegram `/qa <job>` (id hoặc ≥4 ký tự đầu duy nhất) → `POST /api/agent/qa-show`: hiện câu hỏi đang mở, chưa có thì tạo từ cờ high hiện tại (LLM đề xuất, có thể mất 1–2') — đủ 3 nút. Job không HOLD → ghi chú «chỉ ghi script, không xếp lại».
  - `_qa_release` chỉ xếp lại job khi job đang HOLD / đã gác.
  - Agent chat: tool mới `pineline_qa_flags` (câu bị cờ + đề xuất). `pineline_script_edit_line/edit_many` sửa xong → `agent_qa_ask.mark_edited` gắn `qa_ack` cờ high còn lại trên câu + đóng item câu hỏi; hết câu → hook `qa_release` (gỡ HOLD + xếp lại) → không bị HOLD lại.
  - Test: +6 trong `tests/test_brain_qa_ask.py` (14/14). Cần restart :8801 + :8802 (cùng lượt qaask).

- **HOLD QA hỏi người qua Telegram + không chặn hàng đợi** (user: «hỏi chi tiết và cách fix») — `agent_qa_ask.py` (mới), `agent_brain.py`, `routes_agent.py`, `agent_tele_cmd.py`:
  - Job vào HOLD QA (bộ cờ high mới) → LLM (`QA_ASK_MODEL` → QA_FIX_MODEL → …) đề xuất từng câu: fix/false_positive + VI mới + lý do + `conf`. Gửi 1 tin «⏸ HOLD QA <job>»: số câu, loại lỗi (CỨNG/mềm), ZH, VI hiện tại, VI đề xuất, lý do. Nút **✅ Áp đề xuất · ⏭ Cờ sai – bỏ qua · ▶️ Chạy tiếp nguyên trạng**; **reply** vào tin bằng câu VI mới (nhiều câu: `#số: câu`) → ghi script (`manual=1`) rồi chạy tiếp. Câu đã xử lý gắn `qa_ack` (scan không cờ lại), `vi_before_qa_ask`, `qa_ask` (audit). State `work/<job>/qa_ask.json`, tra tin→job `work/logs/qa_ask_index.json`.
  - API mới `POST /api/agent/qa-answer` {job_id, action | reply_to+chat_id+text}; hết câu chờ → `_agent_resume` (gỡ HOLD + xếp lại / park tự chạy), gỡ nút trên tin.
  - Quá `QA_HOLD_MAX_MIN` (**10'**, user chốt 17/11 21:50) không ai trả lời: cờ mềm → áp đề xuất (không có đề xuất = giữ nguyên); cờ cứng + `conf ≥ QA_ASK_SURE_CONF` (0.85) → áp + báo; cứng còn lại → **GÁC job** (hook `defer` = `queue_remove` job + job cha nếu là part → ghế park nhường job sau), manifest `agent.qa_deferred`, Telegram nhắc mỗi `QA_ASK_REMIND_MIN` (60'). Trả lời lúc nào cũng được → job xếp lại đầu hàng.
  - Bỏ tin «Brain NEED-LLM» khi đã có câu hỏi QA mở. Job hết HOLD → câu hỏi cũ đóng (`closed`).
  - Test `tests/test_brain_qa_ask.py` (8) + `test_brain_qa_hold_timeout.py` vẫn qua. Backup `.backup_qaask_20261117/`.
  - **Cần restart :8801** (brain + route) **và :8802** (nút/reply Telegram).

- **Cờ running giả khi HOLD** (ff8e66b475a7 «treo» 40', CPU/GPU đứng yên): hàng đợi `mark_running` bước kế (mux) trước khi chạy, pipeline dừng ở HOLD QA gate → mux «running» không có file nào; Brain tưởng post_tts nên chỉ «chờ mux», heal bị chặn vì queue.current.
  - `server._unmark_running_on_hold`: HOLD sau dịch / QA gate / hàng đợi trả «held» → tts/mux đang `running` về `pending` (Manifest.update).
  - Brain `_ghost_running`: job HOLD (qa_blocked / held_at qa_brain|qa_gate|after_translate) mà tts/mux `running` không dấu hiệu sống trong `GHOST_RUN_MIN` (10') (updated_at/started_at, partial/dub/mixed/_hstrack) → không phải post_tts; tts xong + mux không chạy → phase `held_post_tts` (quét QA, không sửa script) → CLEAR khi high=0 / HOLD quá giờ. `_reset_ghost_running` đưa stage giả về pending.
  - `_qa_hold_timeout` tính cả held_at=qa_gate.
  - `routes_agent._agent_resume`: job PARK (queue.current, không claim) → gỡ HOLD, hàng đợi tự chạy lại (trước trả «đang chạy rồi»).
  - Test: 5 test mới trong `tests/test_brain_qa_hold_timeout.py`.
- **Brain tự xử lý + tự thử lại** (yêu cầu: brain phải xử lý được, fail thì tự retry):
  - `agent_qa_fix.py` (mới): cờ QA **high khác hang** (name_echo, calque, vi_pattern, empty_vi, nonsense_shape…) → LLM (`QA_FIX_MODEL` → HANG_FIX_MODEL → PRONOUN_MODEL) xét từng câu trong cửa sổ ZH/VI: báo sai → `row.qa_ack=[kind]` (scan_script bỏ qua), lỗi thật → ghi VI mới (giữ `vi_before_qa_fix`). Tối đa `QA_FIX_MAX_TRIES`=2 lượt/câu; LLM lỗi không tính lượt. Audit `qa_fix_trace.json`. Gọi trong `agent_quality.scan_and_heal_job` (cả trước TTS lẫn brain tick). Tắt: `BRAIN_QA_FIX=0`.
  - `agent_retry.py` (mới): stage **failed** → đặt lại pending (GIỮ artifact: clip TTS, script…; chỉ xoá output.partial.mp4) + xếp lại hàng đợi (hook `resume`). Backoff `RETRY_BACKOFF_MIN`=5,15,45 phút, tối đa `RETRY_MAX`=3 lần/(job, stage), quá → Telegram «cần người xem». Lỗi notify_only (thiếu giọng, đầy đĩa, source hỏng, user dừng) → chỉ báo 1 lần. Bỏ qua job đang chạy / trong hàng đợi / `.stop` / đang HOLD. Chạy MỌI tick kể cả khi hàng đợi bận (trước: L1 heal bị bỏ 100% tick vì «tick busy»). Tắt: `AGENT_RETRY=0`.
  - Test `tests/test_brain_qa_fix_retry.py`. Backup `.backup_brainretry_20261117/`. Cần restart server.

- **Brain kẹt HOLD QA vô hạn** (ff8e66b475a7 kẹt ~10h trước khi chạy tay TTS) — `agent_brain.py`, `routes_agent.py`:
  - `_qa_pipeline_phase`: job đang HOLD QA mà manifest còn `tts=running` mồ côi → không còn coi là `post_tts` (trước: brain tưởng TTS đang chạy, heal bị chặn vì queue.current).
  - CLEAR HOLD (high=0) giờ gọi hook `resume` (= «Chạy tiếp»: xếp job lại đầu hàng) — trước chỉ gỡ cờ, không ai chạy tiếp.
  - HOLD QA quá `QA_HOLD_MAX_MIN` phút (mặc định 60; 0 = tắt) với cùng bộ cờ high: nếu mọi cờ là loại mềm (name_echo/hang/stutter/calque) → tự chạy tiếp + Telegram; loại cứng (empty_vi, CJK…) → chỉ Telegram nhắc người duyệt (1 lần/giờ).
  - Test `tests/test_brain_qa_hold_timeout.py`. Backup `.backup_qahold_20261117/`. Cần restart server.

- **QA Brain `name_echo` báo sai → job HOLD treo** (job ff8e66b475a7, i=380 «đường … cũng là … đường», i=2483 «Không ngờ … tinh không»): `agent_quality.scan_script` bỏ `(?i)` + lớp `[A-ZÀ-Ỹ]` (dải À–Ỹ gồm cả chữ thường đ/ư…); danh xưng phải viết hoa mọi từ và lặp đúng hoa/thường. Test `test_name_echo_no_false_positive_lowercase`. Cần restart server.

- **Bỏ hết IP LAN 192.168.31.244 / .247** (9router :20128, Aurora :5005) khỏi code + config:
  - `LLM_BASE_URL` mặc định → `http://127.0.0.1:8083/v1` (llama-server local) — config.py, llm.py, machine.py (V4/V5), pineline.config(.example).json.
  - `CLOUD_LLM_BASE_URL` mặc định rỗng; model `ollama/...-cloud` không có base → báo lỗi `LLMUnavailable` rõ ràng thay vì gọi IP LAN.
  - `AURORA_FALLBACK_URLS` mặc định `off` (V4/V5). `tests/test_chatgpt_route.py` đặt fallback giả 10.255.0.9.
  - Backup `.backup_noip_20261117/`. Cần restart server + sidecar.

- **Xoá hẳn Hongguo classic (Downloader 1.x HTTP :8000) — chỉ còn hongguo2 (RPC)**:
  - `hongguo_bridge.py`: bỏ toàn bộ nhánh HTTP (`_req`, `/dl/*`, token UI, `_use_rpc`, `merge_one/merge_status`, proxy ảnh :8000). `rank_episodes` dùng RPC `series.detail`; `seasons_decline` lưu cục bộ `hg_seasons_declined.json` (có `undo`); `library()` ẩn mùa đã từ chối khỏi `newSeasons`; `open_library` mở thư mục cục bộ.
  - `routes_hg.py` (bỏ `_bind_hg_ui_backend`, `api_disk` luôn RPC, `/library/seasons/decline` nhận `undo`), `server.py` (middleware chỉ alias `/api/hg2/*` → `/api/hg/*`; bỏ `HG_BACKEND`), `hongguo_rpc._ensure_licensed_quiet` (bỏ chặn classic), `routes_ui` (`/hongguo` luôn 307 → `/hongguo2`).
  - Chuyển vào `_to_delete/hg_classic_20261117/`: `hg_ui_ctx.py`, `_read_hg_ui_token.py`, `tests/test_hg_classic_removed.py`. Cờ `HG_CLASSIC` / `HG_BACKEND` không còn tác dụng (mục 2026-11-16 về rollback đã hết hiệu lực).
- **Gộp tập có kiểm tra + chuẩn hoá đầu vào** — `hg_merge_check.py` (mới), `_merge_worker` gọi `run_merge`:
  - Trước gộp: ffprobe + đọc packet + giải mã (toàn bộ tiếng, 3s đầu/cuối hình; `HG_MERGE_CHECK=deep` = giải mã cả hình) từng tập, song song `HG_MERGE_CHECK_WORKERS` (4).
  - Hỏng nặng (thiếu moov, < 20 KB, không có hình, tải cụt: đọc được < khai báo) → mặc định DỪNG series, không ra file thiếu (`HG_MERGE_ON_BAD=skip` = bỏ tập hỏng). Báo thiếu số tập.
  - Lệch nhẹ (thiếu tiếng, lệch dài tiếng/hình, pix_fmt ≠ yuv420p, lỗi packet/giải mã, khác res/fps/codec) → chuẩn hoá về số đông (scale/pad/fps, aac 48k-stereo, `aresample=async`, `anullsrc` nếu không có tiếng) rồi ghép.
  - Sau gộp: kiểm tổng thời lượng + giải mã ±2s quanh mỗi mối nối; copy hỏng → tự chuyển chuẩn hoá. Báo cáo `merge_check.json` trong thư mục series.
- **hongguo2.html**: Library thêm tab «Gộp tập» (hàng đợi + tiến độ + lịch sử, gộp tất cả, xoá hàng đợi), «Tra mùa mới» (quét, Tải/Không tải/Bỏ từ chối, Cập nhật tất cả qua Hongguo), nút «Gộp tập» / «Thêm job Pineline» (+ «chạy luôn») khi Select, nút hover trên thẻ; Link thêm «Tra Baike» / «Tìm web»; thẻ New seasons có nút «Không tải».
- Tests: `tests/test_hg_merge_check.py` (mới), `tests/test_hg_merge_queue.py` (`merge_status` raising=False).
- **Cần restart server :8801** (sidecar không cần). Chi tiết: `docs/fixes/2026-11-17-hg-classic-removed-merge-check.md`.

## 2026-11-16

- **Khắc phục lỗi Google OAuth "(invalid_grant) Invalid code verifier" & Báo đúng nguyên nhân token hết hạn**:
  - `test_channel.py`:
    - Sửa lỗi `(invalid_grant) Invalid code verifier`: Với Web Application OAuth (đã có `client_secret` bí mật), thư viện `google_auth_oauthlib` phiên bản mới tự động chèn PKCE (`autogenerate_code_verifier=True`). Khi người dùng mở đăng nhập lại hoặc lưu tạm trên đĩa qua file `.txt`, file này dễ bị ghi đè hoặc lệch giữa các lần click, dẫn đến việc Google từ chối code đổi token với lỗi Invalid code verifier.
    - Cấu hình tường minh `autogenerate_code_verifier=False` ở cả `Flow.from_client_config` trong `get_auth_url` và `finish_oauth`. Khi đó flow Web Application tuân thủ OAuth 2.0 Authorization Code chuẩn (dùng `client_id` + `client_secret`), không phụ thuộc file `code_verifier.txt`, triệt tiêu hoàn toàn lỗi lệch verifier.
    - Dọn sạch các file rác `code_verifier*.txt` trong `data/test_channel/`.
    - Cập nhật thông báo hướng dẫn: nhắc nhở người dùng bấm "Publish App" trên Google Cloud Console (mục OAuth Consent Screen -> In Production) để token không bị Google thu hồi sau mỗi 7 ngày ở chế độ Testing.
  - Không cần restart server hay sidecar.

- **Sửa lỗi UnboundLocalError 'preferred' trong test_channel.py (Kiểm tra Bản Quyền YouTube)**:
  - `test_channel.py`:
    - Trong hàm `get_available_service`: Khi người dùng chọn đích danh `project_id`, hai biến `preferred` và `exhausted_ok` trước đây chưa được khởi tạo, khiến câu lệnh định dạng chi tiết lỗi (`if preferred and exhausted_ok:`) ném ra `UnboundLocalError: cannot access local variable 'preferred' where it is not associated with a value`.
    - Khởi tạo sẵn `preferred = []` và `exhausted_ok = []` ở đầu hàm để trả về đúng chi tiết lỗi kết nối thực tế của Project.
  - Chi tiết: `docs/fixes/2026-11-16-fix-test-channel-unbound-preferred.md`.
  - Không cần restart server hay sidecar (sidecar :8802 tự động `importlib.reload(test_channel)` mỗi request).

- **Nâng cấp Prompt Typography đa dạng & Hòa hợp tương phản dựa trên nền ảnh tham chiếu**:
  - `meta_studio.py`:
    - `build_master_image_prompt`: Bổ sung tham số `typo_color` và `typo_integration`. Thiết kế lại mục `INTEGRATED 3D LATIN TYPOGRAPHY`:
      + Đa dạng hóa vật liệu & phong cách chữ (Fractured ice crystal, brushed titanium, ancient engraved jade, molten lava core, mirror chrome...) thay vì chữ vàng kim phẳng đơn điệu.
      + Neo chặt vào nền ảnh tham chiếu: Yêu cầu AI phân tích ánh sáng & bối cảnh nền ảnh gốc (Reference Image Background) để điều chỉnh màu chữ tương phản cực mạnh, đón hướng sáng môi trường (directional rim glow), tạo bóng đổ tách nền (ambient occlusion drop shadow) và luồn sương khói quanh chân chữ, bảo đảm đọc rõ nét trên mobile mà không che lấp nhân vật chính.
    - `finalize_thumb_meta_fields`: Truyền `typo_color` và `typo_integration` từ `typography_direction` vào `build_master_image_prompt`.
    - `generate_metadata`: Thêm `PHẦN 2B — QUY TẮC TYPOGRAPHY 3D ĐA DẠNG DỰA TRÊN NỀN ẢNH THAM CHIẾU` trong `system_prompt` hướng dẫn LLM nhận diện không gian âm (negative space), màu nền và nguồn sáng để thiết kế trường `typography_direction` đa dạng, giàu tương phản thị giác.
  - Tests: `tests/test_meta_and_thumb.py` (5/5 passed), `tests/test_chatgpt_route.py` (6/6 passed), `tree_audit.py` (ERROR=0).
  - Không cần restart server. — Bỏ Hongguo classic, mọi thứ chạy hongguo2 (RPC)

- **Nâng cấp Prompt Typography đa dạng & Hòa hợp tương phản dựa trên nền ảnh tham chiếu**:
  - `meta_studio.py`:
    - `build_master_image_prompt`: Bổ sung tham số `typo_color` và `typo_integration`. Thiết kế lại mục `INTEGRATED 3D LATIN TYPOGRAPHY`:
      + Đa dạng hóa vật liệu & phong cách chữ (Fractured ice crystal, brushed titanium, ancient engraved jade, molten lava core, mirror chrome...) thay vì chữ vàng kim phẳng đơn điệu.
      + Neo chặt vào nền ảnh tham chiếu: Yêu cầu AI phân tích ánh sáng & bối cảnh nền ảnh gốc (Reference Image Background) để điều chỉnh màu chữ tương phản cực mạnh, đón hướng sáng môi trường (directional rim glow), tạo bóng đổ tách nền (ambient occlusion drop shadow) và luồn sương khói quanh chân chữ, bảo đảm đọc rõ nét trên mobile mà không che lấp nhân vật chính.
    - `finalize_thumb_meta_fields`: Truyền `typo_color` và `typo_integration` từ `typography_direction` vào `build_master_image_prompt`.
    - `generate_metadata`: Thêm `PHẦN 2B — QUY TẮC TYPOGRAPHY 3D ĐA DẠNG DỰA TRÊN NỀN ẢNH THAM CHIẾU` trong `system_prompt` hướng dẫn LLM nhận diện không gian âm (negative space), màu nền và nguồn sáng để thiết kế trường `typography_direction` đa dạng, giàu tương phản thị giác.
  - Tests: `tests/test_meta_and_thumb.py` (5/5 passed), `tests/test_chatgpt_route.py` (6/6 passed), `tree_audit.py` (ERROR=0).
  - Không cần restart server. — Bỏ Hongguo classic, mọi thứ chạy hongguo2 (RPC)

- `routes_ui`: `/hongguo`, `/ui-hg` → 307 sang `/hongguo2` (giữ query). `hongguo.html` → `_to_delete/`.
- `hg_ui_ctx`: `classic_enabled()` (HG_CLASSIC, mặc định tắt); `force("http")` / `apply` classic → `rpc` ⇒ `/api/hg/*` cũng chạy RPC.
- `server.py`: `HG_BACKEND` mặc định `rpc` (trước `auto`); `hongguo_bridge._hg_backend_pref` mặc định `rpc` ⇒ agent/feeder/Telegram không còn rơi về :8000.
- Link trong `index*.html`, `films_ui.html`, `v5-map.html`, `static/app.js` → `/hongguo2`.
- CÒN gọi thẳng app Downloader 1.x :8000 (chưa có nhánh RPC): `rank_episodes`, `seasons_decline`, `merge_one`/`merge_status`, `open_library`, `fetch_poster` (có fallback file local), `_ingest_one`, `_hongguo_match_version`.
- Mất giao diện (chỉ trang cũ có): gộp tập/merge-queue, cập nhật mùa mới + từ chối mùa, baike, web-search, thêm job Pineline từ thư viện — dùng Films UI / agent thay.
- ~~Quay lại: `HG_CLASSIC=1` + `HG_BACKEND=auto`~~ (hết hiệu lực từ 2026-11-17 — classic đã xoá hẳn) trong pineline.config.json, chép `_to_delete/hongguo.html` về gốc, restart.
- Test mới `tests/test_hg_classic_removed.py`. **Restart server.** Backup `.backup_hg2_20261116\\`. Chưa chạy pytest / chưa chạy server thật.

## 2026-11-16

- **Nâng cấp Prompt Typography đa dạng & Hòa hợp tương phản dựa trên nền ảnh tham chiếu**:
  - `meta_studio.py`:
    - `build_master_image_prompt`: Bổ sung tham số `typo_color` và `typo_integration`. Thiết kế lại mục `INTEGRATED 3D LATIN TYPOGRAPHY`:
      + Đa dạng hóa vật liệu & phong cách chữ (Fractured ice crystal, brushed titanium, ancient engraved jade, molten lava core, mirror chrome...) thay vì chữ vàng kim phẳng đơn điệu.
      + Neo chặt vào nền ảnh tham chiếu: Yêu cầu AI phân tích ánh sáng & bối cảnh nền ảnh gốc (Reference Image Background) để điều chỉnh màu chữ tương phản cực mạnh, đón hướng sáng môi trường (directional rim glow), tạo bóng đổ tách nền (ambient occlusion drop shadow) và luồn sương khói quanh chân chữ, bảo đảm đọc rõ nét trên mobile mà không che lấp nhân vật chính.
    - `finalize_thumb_meta_fields`: Truyền `typo_color` và `typo_integration` từ `typography_direction` vào `build_master_image_prompt`.
    - `generate_metadata`: Thêm `PHẦN 2B — QUY TẮC TYPOGRAPHY 3D ĐA DẠNG DỰA TRÊN NỀN ẢNH THAM CHIẾU` trong `system_prompt` hướng dẫn LLM nhận diện không gian âm (negative space), màu nền và nguồn sáng để thiết kế trường `typography_direction` đa dạng, giàu tương phản thị giác.
  - Tests: `tests/test_meta_and_thumb.py` (5/5 passed), `tests/test_chatgpt_route.py` (6/6 passed), `tree_audit.py` (ERROR=0).
  - Không cần restart server.

- **Khắc phục lỗi abort kết nối Aurora (/images/edits wsasend abort), Tăng timeout & Bỏ toàn bộ backup 192 (retry 3377 để roll acc)**:
  - `meta_studio.py`:
    - Sửa nguyên nhân gốc `wsasend: An established connection was aborted`: dòng gọi `/images/edits` trước đây bị kẹp cứng `timeout=min(timeout, 90)`. Khi Aurora mất 2m10s để xử lý multipart upload, Python bị ngắt socket ở giây 90 khiến Aurora khi sinh xong 200 OK gọi write bị abort. Tăng timeout lên `edit_timeout = max(timeout, 240)` (caller 300s thì đợi đủ 300s).
    - Thêm cờ `allow_edits` / cấu hình `META_AI_IMAGE_EDITS`: cho phép bỏ qua upload ảnh tham chiếu để sinh ảnh nhanh bằng text prompt nếu cần.
    - **Bỏ hoàn toàn các IP backup 192.168.*** (`.247:5005`, `.244:5005`) trong `_chatgpt_candidate_bases()`.
    - Tăng số lần retry trực tiếp trên `http://127.0.0.1:3377/v1` lên 4 lần với sleep 1.0s để Aurora roll sang account khác trong pool khi gặp lỗi (400/500/bận).
    - Bỏ chặn `_DEAD_CHATGPT_BASES` với 3377 để luôn retry trực tiếp trên 3377.
  - `llm.py`:
    - Bỏ các IP LAN 192.168.* trong `_chatgpt_settings()`, chỉ giữ `http://127.0.0.1:3377/v1` để khi retry sẽ roll account khác trực tiếp trong pool của 3377.
  - `agent_tele_cmd.py` & `routes_hg.py`:
    - Hỗ trợ tham số `allow_edits` / `skip_edits` trong API sinh ảnh `/api/meta/ai-image`.
  - Tests: `tests/test_meta_and_thumb.py` (5/5 passed), `tests/test_chatgpt_route.py` (6/6 passed), `tree_audit.py` (ERROR=0).
  - Không cần restart server ngay nếu không dùng translate; sidecar reload `meta_studio` mỗi request. Chi tiết: `docs/fixes/2026-11-16-aurora-meta-timeout-roll-3377.md`.

- **Tự chọn cỡ lô dịch theo mức song song, Khóa DeepSeek-Flash 100% (bỏ NMT) & Sửa triệt để sampling A7 + pair_fill decode**:
  - `translate_simple/cfg.py`:
    - Thêm `deepseek_concurrency()` đọc `DEEPSEEK_CONCURRENCY` (mặc định 32, kẹp 1–64). Aurora và local giữ 8.
    - Nâng cấp `workers(model)`: tự động cấp 32 workers cho model DeepSeek (`deepseek/`, `deepseek-`).
    - Thêm `batch_for_rows(n_rows, workers, explicit)`: tự động tính `ceil(số câu ÷ số workers)`, kẹp trong khoảng `[40, 200]` câu. Phim 1.500 câu → lô 47 câu (1 đợt); phim 10.000 câu → lô 200 câu (~2 đợt). Tôn trọng `SIMPLE_BATCH` nếu user cấu hình cứng.
  - `translate_simple/stage_review.py`:
    - Tự động gọi `cfg.workers(model)` và `cfg.batch_for_rows(len(todo_idx), workers)` tại đầu hàm `run`.
    - Sửa hàm `_decode`: Lọc bỏ thẻ `</escape>` / `<escape>`, bổ sung hỗ trợ đầy đủ các schema `("lines", "pairs", "characters", "terms")` trong cứu hộ `raw_decode`. Khắc phục hoàn toàn lỗi `BadOutput` ở bước 3b `pair_fill`.
  - `translate_simple/stage_draft.py`:
    - Sửa thuật toán sampling A7: Khắc phục lỗi `cur >= 0` luôn đúng do `len(t) > step`, chuyển sang chia đều chỉ số theo tỷ lệ `target_count` và kẹp chốt chặn cứng không bao giờ vượt ngưỡng 26.000 ký tự.
    - Khi NMT tắt (`MT_ZH_VI="0"`), bỏ toàn bộ ThreadPool phụ, chỉ chạy `build_plan` A7, giải phóng 100% VRAM GPU khỏi CTranslate2.
  - `llm.py`:
    - Tự động alias mọi tên gọi model (`chat`, `v3`, `flash`, `auto`) về `deepseek-flash` để tối ưu chi phí rẻ nhất và tốc độ cao nhất, tuyệt đối né `pro`.
  - `uploader_settings_api.py` & `films_ui.html`:
    - Thêm `DEEPSEEK_API_KEY` và `DEEPSEEK_CONCURRENCY` vào API `get_settings()` / `update_settings()`.
    - Thêm ô nhập API key và số request song song DeepSeek vào tab AI trong modal ⚙️ Cài đặt.
  - Tests: `tests/test_translate_simple.py` (32 passed, 1 skipped), `tests/test_simple_r1_bugs.py` (7 passed), `tests/test_translate_simple_a7_a8.py` (6 passed), `tests/test_translate_simple_next.py` (29 passed).
  - **CẦN RESTART :8801**: Khi hàng chờ rảnh để nạp toàn bộ module `translate_simple` và `uploader_settings_api` mới vào tiến trình server. Chi tiết: `docs/fixes/2026-11-16-dynamic-concurrency-and-batch.md` và `docs/fixes/2026-11-16-fix-pair-fill-json-escape.md`.

## 2026-11-15

- **A7 Plan đọc cả phim bằng LLM context lớn & A8 Soát trượt có chồng lấn (Sliding Window Overlap)**:
  - `translate_simple/stage_draft.py`: Thêm `build_full_movie_plan` tận dụng context window lớn của LLM (DeepSeek-V3, Aurora `gpt-5-6-mini`, Qwen-Max) đưa toàn bộ thoại ASR tiếng Trung vào phân tích 1 lượt (lập bảng nhân vật toàn phim, phát hiện lỗi đồng âm ASR, quan hệ xưng hô 2 chiều, thuật ngữ và tóm tắt bối cảnh cốt truyện `summary`). Tự động phân đoạn mẫu dày đều nếu phim > 26.000 ký tự.
  - `translate.py`: Tích hợp A7 vào `build_plan` ưu tiên mode context lớn trước khi fallback file SRT/sample.
  - `translate_simple/cfg.py`: Thêm cấu hình `SIMPLE_FULL_PLAN` (mặc định 1), `SIMPLE_OVERLAP_CUES` (mặc định 3, phạm vi 0-10), `SIMPLE_PLAN_MODEL` / `plan_model()`.
  - `translate_simple/plan_view.py`: Đưa `TÓM TẮT PHIM` lên đầu `header_lines()` cho mỗi lô, kích hoạt tối đa Prompt Caching của LLM và duy trì bối cảnh xuyên suốt.
  - `translate_simple/stage_review.py`: `make_jobs` hỗ trợ chồng lấn `overlap` câu liền trước vào `before`, `build_prompt` gắn nhãn `NGỮ CẢNH TRƯỚC (CHỒNG LẤN)` và `NGỮ CẢNH SAU (NHÌN TRƯỚC)`. Parser kiểm soát nghiêm ngặt chỉ nhận câu trong lô `want`.
  - Tests: Mới `tests/test_translate_simple_a7_a8.py` (5/5 passed), `tests/test_translate_simple.py` (31/31 passed, 1 skipped).
  - Không cần restart server ngay nếu không có job dịch dở; job mới vào queue sẽ tự động áp dụng. Bak `Z:\PinelineV2_codebak\2026-11-15_a7-a8-full-plan-overlap\`. Chi tiết `docs/fixes/2026-11-15-simple-a7-a8-full-plan-overlap.md`.

- **Retry Aurora account pool 400 + fallback ngay khi :3377 đóng + thêm Alibaba DashScope + sửa sinh ảnh Aurora Films UI**:
  - `llm.py`: Thêm `_DEAD_BASES` (cooldown 60s) để khi `:3377` từ chối kết nối sẽ nhảy ngay sang LAN `.247/.244` (không mất 7s retry lặp lại mỗi câu). Thêm `_PAYLOAD_TOO_LARGE_RE` để lỗi 400 account pool (`no available account...`) được retry xoay account thay vì coi là no-retry. Thêm provider Alibaba DashScope (`alibaba/`, `dashscope/`, `qwen/`).
  - `cloud_retry.py`: Phân loại lỗi 400 do Aurora pool account thành `transient` để thử lại.
  - `config.py`: Đăng ký các key Alibaba `ALIBABA_BASE_URL`, `ALIBABA_API_KEY`, `ALIBABA_MODEL`, `DASHSCOPE_API_KEY`.
  - `meta_studio.py` & `films_ui.html`: Sửa chức năng sinh ảnh Aurora: phát hiện và từ chối ảnh tham chiếu bị echo ngược từ `/images/edits`, fallback chuẩn sang `/images/generations` khổ 16:9 (`1792x1024`), tự xoay pool account khi lỗi 400/500 và tự động tránh base dead.
  - `translate_simple/stage_review.py` & `pair_rules.py`: Chạy song song `review-retry` có progress bar và cache regex trong `_role_of`.
  - Test: 11/11 tests pass (`test_chatgpt_route.py`, `test_meta_and_thumb.py`). Smoke test sinh ảnh thực tế trên `:8802/api/meta/ai-image` ra ảnh raw 1672×941 và thumbnail 1280×720 thành công.
  - **Không cần restart :8802** (sidecar reload `meta_studio` mỗi request). **Restart :8801** khi server rảnh để áp dụng `llm.py` mới cho queue. Bak `Z:\PinelineV2_codebak\2026-11-15_aurora-retry-alibaba-ai-image\`. Chi tiết `docs/fixes/2026-11-15-aurora-retry-alibaba-ai-image.md`.

## 2026-11-14

- **G1.1 simple R1.1–R1.5** — Soát lại+cloud chết không còn done giả (`pop rv`); plan fail không ghi/reuse glossary rỗng + gate hold; lỗi CODE → HOLD + traceback (không park B2); `_now` → `core.timeutil.now_iso`; KIN+động từ tường thuật không cờ FP. Test `tests/test_simple_r1_bugs.py` (7). Bak `…_1906.zip` + `codebak\2026-11-14_simple-r1\`. Fix `docs/fixes/2026-11-14-simple-r1-bugs.md`. **Đã restart :8801** ~19:24 (cắt/resume `08ab_p02`).
- **Seat-lock: chặn translate_fill/heal GPU ngoài ghế** — Brain heal từng APPLY `translate_fill` trên job chờ → ghost `running` + UI nhiều cam. Mới `server._queue_seat_blocks` (409 `blocked_by_seat`); fill chỉ đánh `running` khi worker `_gpu` bắt đầu; `agent_heal.other_seat_busy` skip fill/TTS/ASR khi `queue.current` khác (`heal_stale` vẫn OK). Test `tests/test_seat_lock_heal.py`. Bak `Z:\PinelineV2_backup_2026-11-14_1620.zip` + `codebak\2026-11-14_seat-lock-fill\`. Fix `docs/fixes/2026-11-14-seat-lock-translate-fill.md`. **Đã restart :8801** ~16:27; smoke fill ngoài ghế → 409.
- **Dọn ghost translate + reset `08ab52d5b2f2_p02`** — UI hiện nhiều job cam vì manifest `translate=running` sót sau NMT treo (VI=0), trong khi queue chỉ 1 ghế `d043891ef637` (TTS part). Stop + stamp pending `08ab_p02`/`e00fcc_p01`; backup script 08ab; 08ab vẫn trong queue. **Không restart.**
- **NMT CUDA 13: `ctranslate2` → `ctranslate2-reborn` 4.9.0.post1** — sau khi torch lên cu130, CT2 official (CUDA 12) thiếu `cublas64_12` / trộn leftover `~orch` → `translate_batch` treo (GPU util ~0). Gỡ `ctranslate2`, cài `ctranslate2-reborn` (CUDA 13, import vẫn `ctranslate2`). Smoke: 4 câu OK ~11 s (load) + batch 32 ~0.1 s. **Đã restart :8801** ~11:32 (`--clean-env`, PID 18304); xếp `08ab52d5b2f2_p02` sau current `d043891ef637`. Fix `docs/fixes/2026-11-14-nmt-ct2-cuda13.md`.
- **OCR hardsub CÓ CHỌN LỌC (mặc định `SIMPLE_ZH_OCR_MODE=targeted`)** — sau sự cố `1efd1014ac77_p03` dịch «100% · treo?» hàng giờ (OCR cả phim 16.702 khung CPU). MỚI `translate_simple/zh_ocr_target.py`: lượt A (zh_source.prepare, trước plan: 他/她/它, tên hồ sơ phim, số) + lượt B (pipeline 4b, sau review: s_conf<0.7, s_to='?', bị cờ ±1 → thay chữ, bỏ rv → 5b soát lại); `align` Levenshtein, KHÔNG bớt chữ, câu <4 chữ chỉ 他/她/它, chặn chữ Hán→số/Latinh, conf ≥ `OCR_HS_ACCEPT_CONF` 0.8. MỚI `hs_ocr_fast.py` (mode full: 1 khung/s, pipe, -hwaccel cuda→CPU, chạy nền song song ASR qua `server._hs_ocr_prefetch`; `get_cues` chờ ≤ `SIMPLE_ZH_WAIT_SEC` 900 rồi dịch bằng ASR). onnxruntime-gpu: `_preload_cuda`, log thiết bị thật. `cfg.zh_ocr_mode/zh_ocr_pass_b`. Đo `e00fcc006b57_p01` lượt A: 452 câu, 110 s GPU, đổi 94 (17 hại → đã chặn). **Restart :8801.** Port V4/V5/V6 CHƯA. Chưa pytest. Bak `*.backup_edit_20261114_{hsfast,ocrtarget,preload,preload2,guard}`. Fix `docs/fixes/2026-11-14-hs-ocr-fast.md`.
- **Handoff** `docs/HANDOFF.md` (tóm tắt 12–14/11 cho phiên/tài khoản khác) + dòng «đọc trước» trong CLAUDE.md V2/V4/V5/V6.

## 2026-11-13 (bổ sung — sửa trực tiếp phiên chính)

- **Bỏ OCR khi chạy lại job đã soát đủ** — `translate_simple/pipeline.py` `_script_all_reviewed`; UI hiện «nguồn ZH: phát hiện hardsub / OCR…». **Restart :8801.** Bak `pipeline.py.backup_edit_20261113_zhskip`.
- **Chuẩn hoá độ to −14 LUFS khi render** — `render.py` `_loudnorm_gain_filter` (gain tuyến tính + alimiter −1.5 dBTP, cache `loudness.json`; đường thường + chia khúc + thử lại NVENC; chế độ trộn 2 lượt). `RENDER_LOUDNORM=0` tắt. Chủ dự án nghe A/B: giữ EQ giọng cũ. **Restart :8801.** Bak `render.py.backup_edit_20261113_loudnorm`.
- **Bật cờ simple** `SIMPLE_ZH_SOURCE/PAIR_RULES/PAIR_FILL/LEARN_INFERRED=1` (pineline.config.json, bak `.backup_edit_20261113_simpleflags`).
- **Gỡ giọng kém** Res, GiongBe, NgayCuoi, VieNeu_MaiAnh → `voices/_to_delete/` (bak `voices/f5_voices.backup_20261113_prune.json`).

## 2026-11-13

- **Parent đã ghép Full mà part vẫn ASR lại (60892cc63cb7)** (agent S). Gốc: 21:36 UTC Brain heal aggressive `asr_run_force` trên PARENT (parent «asr failed», không asr.json theo thiết kế) → `run_stage(parent, asr, force)` nằm hàng `_gpu` 2 h → 23:36 `split_job_to_subjobs` cắt lại + reset tts part → ép `--force` ASR p01 rồi p02 dù Full đã ghép 00:12. `skip_done=false` KHÔNG liên quan (không lưu). `server.py`: `_split_parent_finished`/`_split_parent_stop_if_finished` (dừng vòng part trước mỗi part + mỗi stage qua `_auto_gpu(abort_if=)`, gỡ parent khỏi hàng đợi), `_force_consumed` + `run_stage` mốc `requested_at` (force một lần), ASR-parent bỏ part đã mux, `work_root=WORK_ROOT`; `_queue_run_one` parent split đánh `mux` (không `asr`). `agent_heal.py`: parent split không `asr_bad`/`asr_run_force`. `job_queue.py`: không lưu force/skip_done vào opts. `split_parts.py`: `find_reusable_parts` (dùng lại part đúng kế hoạch, giữ stage part), `merge_parts_checked`/`check_merge_joints` (giải mã ±30 s mỗi mối nối, DTS = cảnh báo, lỗi → ghép regen → vẫn lỗi báo rõ), `merge_job_parts` ghép ra file tạm, giữ Full cũ khi lỗi, `already_merged` không ghép đè. Test mới `tests/test_parent_rerun_after_done.py` (19); bản sao 625 → 644 pass, cùng 23 fail + 6 error môi trường. **Restart :8801.** Port V4/V5/V6 CHƯA. Bak `.backup_edit_20261113_agentS\`. Fix `docs/fixes/2026-11-13-parent-rerun-after-done.md`.
- **extract_pcm: khúc chunk mở GIỮA vùng hỏng ra toàn 0 trên ffmpeg 8.1.2 → seek trên nguồn CHỈ-TIẾNG + loại khúc 0 từ đầu** (agent K3). Sau K2 user vẫn mất bíp 33/43/53 (`ffmpeg version 8.1.2-full_build-www.gyan.dev`). `media_ts.py`: khúc 30 s có lỗi + đuôi 0 ≥1 s (kể cả cả khúc 0) → chia nhỏ; khúc hỏng đầu tiên → copy AAC ra `.m4a` tạm và seek trên đó (không lùi keyframe hình; lệch 0 mẫu); khúc con lỗi → thử `-err_detect ignore_err` trên file gốc, giữ bản nhiều tiếng hơn. File lành không đổi. File hỏng thật (VM 4.4): 0 s im lặng, 48 s. Test +3/1 sửa; cloud 574 pass, cùng 31 fail môi trường. MỚI `Z:\PinelineV6\scripts\diag_extract_pcm.{py,bat}`. Đồng bộ `media_ts` + test sang V4, V5/V6 `engines/`. **ASR có hiệu lực ngay; server sau restart :8801/V4/V5/V6.** Bak `.backup_edit_20261113_agentK3\` (mỗi cây). Fix `docs/fixes/2026-11-12-video-preflight.md` mục D.
- **Meta: nút Sinh tiêu đề + bỏ khoá hook tên phim** (~14:35). `films_ui`: «🔤 Sinh tiêu đề» → `/meta/generate-title`; Áp chữ concept; Aurora tôn form. `meta_studio.finalize`: ưu tiên `typography.text_exact`. Test `test_meta_and_thumb` pass. Bak `…_meta-title-btn-hooks\`. **Hard refresh Films UI;** restart :8801 nếu muốn finalize mới trên server.

- **Brain: job đã xong bị heal «thất bại» + park tự động bị báo «HOLD / Cần bạn»** (agent N). Gốc: `agent_heal.diagnose_job` không biết job xong — `asr_bad` (translate done, asr.json đã dọn), `tts_not_started` (tts done nhưng tts.json đã dọn) → heal `tts_run` → «chưa dịch xong (thiếu script.json)» trên 2493d3c7cb29/ae9956bb8fb3/ec10e47767ed; `detect_stage_events` coi park `waiting_review` là HOLD. MỚI `agent_hold.job_finished` (MỘT định nghĩa: mux done+output.mp4/output_full.mp4, đã đăng, parent đã ghép Full, part của parent đó) dùng ở `agent_heal` (diagnose/heal/scan/batch/watch), `agent_brain` (sense_jobs, apply heal, deep tick, nhắc lỗi, clear_stale_holds), snapshot LLM; 3 detector sửa tận gốc (+`tts_missing_clips` chỉ khi dịch xong). `hold_class`: park/split_parts → tin «⏸ … tạm dừng soát dở N câu, tự thử lại lúc HH:MM (lần k/max)» 1 lần/lượt park; review_failed/qa_*/simple_gate/hold_after_translate → «⛔ … HOLD: … / Cần bạn: …» (kể cả khi park chuyển sang review_failed). «Chạy tiếp» / chạy tay / job xong gỡ cả `review_retries/review_retry_at/simple_park/split_wait_parts`. Test mới `tests/test_brain_finished_hold.py` (23), `test_agent_brain_notify` 1 kỳ vọng ⏸→⛔; bản sao 608 → 631 pass, cùng 14 fail + 6 error môi trường. **Restart :8801.** Port V4/V5/V6 CHƯA. Bak `.backup_edit_20261113_agentN\`. Fix `docs/fixes/2026-11-13-brain-finished-hold.md`.

- **Lib đĩa không hiện / Hongguo merge «need ≥2»** (~04:50). Folder chỉ có tập lẻ (vd `钞能玩家`) bị `feeder.library` bỏ; Hongguo không biết series → lỗi gộp. `merge_series_concat_copy` + fallback worker; feeder hiện `need_merge`. Đang gộp tay S1+S2 qua `tools/_merge_lib_chao.py`. Bak `…_hg-local-merge-fallback\`. Fix `docs/fixes/2026-11-13-lib-merge-local-fallback.md`. **Restart :8801** để queue UI dùng fallback; `/library` sidecar reload đủ hiện folder.

- **Meta UI thiếu nút Aurora** (~04:20). `films_ui.html`: thêm `btn-gen-ai-thumb` «✨ Sinh ảnh AI Aurora» (trước chỉ có JS, không có HTML → user không thấy nút). Hint tiêu đề: bấm Sinh Meta. Hard refresh. Bak `…_meta-aurora-btn\`. Follow-up `docs/fixes/2026-11-13-meta-ai-image-8801.md`. **Không restart.**

- **Meta Studio GPT thumb 404 trên :8801** (~02:45). `routes_hg` thiếu `POST /api/meta/ai-image` trong khi Films UI serve cả `:8801` và `:8802` → UI mở 8801 fail dù GPT `:3377` + sidecar OK. Thêm route parity sidecar; `films_ui` trên port 8801 fallback gọi `:8802` (CORS). Smoke `:8802` 200 / `thumb_gen_*.jpg`. Bak `Z:\PinelineV2_codebak\2026-11-13_meta-ai-image-8801\`. Fix `docs/fixes/2026-11-13-meta-ai-image-8801.md`. **Hard refresh Films UI đủ ngay; restart :8801** để route native trên server (hỏi yes/no).

- **Câu ASR rác «None.» làm dịch simple park mãi → part kẹt; parent auto-split quay lại part park** (agent M, sự cố `60892cc63cb7_p01` i=1039, 5150 câu). MỚI `text_junk.py` (`is_junk_text`: không CJK/chữ/số, hoặc None/null/nan ± dấu). `firered_asr._parse_firered_result`: bỏ câu rác + log số câu (nguồn: AED giải mã ồn thành «none», FireRedPunc viết hoa + «.»). `translate_simple`: câu zh rác → tự soát `vi=«…»` `rv=1` `junk=1` `skip_tts=1` (TTS `_is_trivial_vi` → slot im lặng đúng dài; không dùng vi rỗng vì `count_script_missing` chặn TTS), không gửi review/không cờ; sau repair còn câu chưa soát → 1 lượt review CHỈ câu đó lô `SIMPLE_MISSING_BATCH`=4; còn ≤ `SIMPLE_UNREVIEWED_TOLERANCE` (trống = max(3, 0.2 %); 0 tắt) và đều có nháp → nhận nháp `rv=1`+`unreviewed_accepted=1`, cổng done, lý do vào manifest `simple.accept_reason` + trace (+1 dòng brain nếu chạy trong tiến trình); vượt → park như cũ. `server.py`: vòng Part n/N — part park/HOLD → KHÔNG ghép hụt, parent `held_at=split_parts` (+`split_wait_parts`) → hàng đợi giữ ghế; `_queue_park_ready(parent)` = part tới hạn retry/hết HOLD/xong → chạy lại parent (trước: parent `failed`, rời hàng đợi, part park không ai quay lại → kẹt vĩnh viễn). Test mới `tests/test_simple_junk_park.py` (43); 2 ca cũ đặt tolerance=0. Toàn bộ tests bản sao 556 → 599 pass, cùng 14 fail môi trường. **Restart :8801** (translate_simple + server nạp trong tiến trình); FireRed hiệu lực ngay. Gỡ `60892cc63cb7_p01`: sau restart chạy lại/xếp lại parent `60892cc63cb7` (không sửa work). V6 `test_v2_translate_simple.bat` kỳ vọng 131. Port V4/V5/V6 CHƯA sửa. Bak `.backup_edit_20261113_agentM\`. Fix `docs/fixes/2026-11-13-simple-junk-park.md`.

- **extract_pcm: không tin bản full «đủ dài» khi decoder chết (ffmpeg 8.1.2 đệm im lặng)** (agent K2). Máy user `ffmpeg version 8.1.2-full_build-www.gyan.dev`: AAC hỏng → rc=0, đủ độ dài nhưng toàn mẫu 0 sau điểm hỏng (test `test_corrupt_aac_full_length_and_timing` fail trên Windows). `media_ts.py`: `_decode_errors` (từ khoá chịu cả 4.4/8.x), `_dead_zero_run`; có lỗi/rc≠0 + đoạn 0 tuyệt đối ≥2 s → head tới đó + chunk; không stderr → đuôi 0 ≥5 s tới hết; khúc 30 s có lỗi + đuôi 0 → chia khúc 5 s. File lành giữ nguyên 1 lệnh, giống từng byte. Đo file hỏng thật: 7741.451 s, im lặng 0 s, 58 s. Test +9 ca. **Có hiệu lực ngay cho ASR (tiến trình con); render/preflight trong server sau restart :8801.** Bak `.backup_edit_20261113_agentK2\`. Fix `docs/fixes/2026-11-12-video-preflight.md` mục C.
- **Preflight + chuẩn hoá video nguồn trước khi vào job + 2 fix review `extract_pcm_from_video`** (agent K, chủ dự án: «kiểm tra lại, chuẩn hoá video trước khi đưa vào job»). `media_ts.py`: nhận bản trích full chỉ khi thiếu ≤ `EXTRACT_FULL_TOL_SEC` (1 s; trước 0.85×video → mất tới 15 % cuối phim), DÀI hơn hình + luồng tiếng khai báo → AAC rác → chunk lại từ 0 (file thật `merged.mp4.bak_aac_corrupt`: full ra 7810.9 s vs 7741.4 s); mỗi khúc chunk/head ép ĐÚNG số mẫu cửa sổ (`_force_wav_frames`; trước: khúc thiếu ≤15 % làm mốc sau trôi, giả lập −2.7 s ở 53 s). MỚI `source_preflight.py`: ffprobe (hình/tiếng/codec/kênh/sr/độ dài/VFR) + giải mã thử toàn bộ audio (AUDIO_TS_FIX) + drift + vài khung hình → `stages.download.preflight`; lỗi audio → `work/<job>/source_norm.<mp4|mkv>` (`-c:v copy` + audio dựng lại bằng extract_pcm, AAC) + `download.video_path_norm`; không cứu được → fail sớm lý do rõ. Hàm resolve nguồn DUY NHẤT `resolve_source_video`/`stage_source_video` dùng ở `asr.resolve_asr_source`, `separate`/`ocr`/`hardsub_asr`/`render`/`mux._find_video`, `split_parts` (sub-job kế thừa), `server._find_video` (chỉ đọc), `agent_av_sync`. `download.py`: preflight ngay sau tải (fatal → download failed). `server._finalize_imported_source`: gắn `preflight_pending` (chạy lười ở stage đầu, không chặn request). Cờ `VIDEO_PREFLIGHT=1`, `VIDEO_NORMALIZE=1`, `VIDEO_NORMALIZE_DRIFT=0`, `EXTRACT_FULL_TOL_SEC=1.0`. Job cũ không chạy lại; MỚI `tools/preflight_scan.py` (chỉ đọc). Đo: phim 2 h 09' lành 9.2 s, hỏng 11.9 s, chuẩn hoá 127 s. Test mới `tests/test_extract_pcm_timing.py` (12), `tests/test_video_preflight.py` (13); toàn bộ 537 → 562 pass, cùng 31 fail môi trường. **media_ts/ASR (tiến trình con) có hiệu lực ngay; import/download/render/preview cần restart :8801.** Port V4/V5/V6 CHƯA sửa. Bak `.backup_edit_20261112_agentK\`. Fix `docs/fixes/2026-11-12-video-preflight.md`.

- **FireRed ASR: chia slice tại KHOẢNG LẶNG + đệm chồng lấn, cắt theo mẫu** (agent L). `firered_asr.py`: bỏ cắt cứng `ffmpeg -ss/-to` tại k×1200 s (câu vắt biên bị cắt đôi/lặp/mất chữ — vd `2d3316593ea9` @1200 «您已成为天。|命之子。»); điểm cắt = khoảng lặng gần mốc (RMS 20 ms numpy, cửa sổ ±`FIRERED_CUT_SEARCH_SEC`=60), không lặng → điểm năng lượng thấp nhất + đệm `FIRERED_SLICE_PAD_NOSIL_SEC`=10; đệm `FIRERED_SLICE_PAD_SEC`=2, giữ câu có tâm trong lõi slice; cắt bằng `separate.write_wav_slice` (đúng từng mẫu); `FIRERED_SLICE_SEC=0` = cả file 1 lượt; log `[firered] N slice, cắt tại khoảng lặng: …`. Test mới `tests/test_firered_slice_silence.py` (9). Mới `tools/asr_boundary_scan.py` (chỉ đọc): 10/10 job nghi lỗi, 53/71 biên, 106 câu → nên chạy lại ASR. **Có hiệu lực cho lần ASR FireRed kế tiếp** (tiến trình con) — không cần restart; asr.json cũ không tự sửa. Port V4/V5/V6 CHƯA sửa. Bak `.backup_edit_20261113_agentL\`. Fix `docs/fixes/2026-11-13-firered-slice-silence.md`.

## 2026-11-12

- **Remux `merged.mp4` job `2937ffd7989f`:** giữ video, thay audio ghép từ 109 tập `S03E*` (bak `merged.mp4.bak_aac_corrupt`); verify extract full rc=0. **Không cần restart.** Cần xếp lại ASR.
- **ASR/Demucs: extract PCM chịu AAC hỏng giữa file (rematrix 21ch → -22)** — job `2937ffd7989f`. `media_ts.extract_pcm_from_video`: full → salvage partial → chunk 30s/sub 5s + silence chỗ chết → fit đúng `vdur`; `asr.extract_audio` + `separate._extract_orig_wav` + `ensure_job_audio_ts` dùng chung. Test `tests/test_extract_pcm_robust.py`. Bak `Z:\PinelineV2_backup_2026-11-12_1915.zip`, `Z:\PinelineV2_codebak\2026-11-12_aac-extract-robust\`. Fix `docs/fixes/2026-11-12-aac-extract-rematrix.md`. **Không cần restart** (tiến trình con ASR). Cần xếp lại stage asr job đó.
- **Lệnh Telegram của người dùng = chạy tay → tự gỡ HOLD + 1 tin** (agent I2, quyết định chủ dự án). `agent_tele_cmd.py`: `_agent_ask` (có uid Telegram) + `_confirm_callback` (bấm ✅) gửi `X-Pineline-Caller: user`, `X-Pineline-Source: telegram`; `agent_autopilot.py`: `caller_headers`, `_post(headers=)`, `agent_chat/agent_confirm(caller=, source=)` (mặc định không gắn); `routes_agent.py`: `/api/agent/chat|confirm` nhận `Request`, request tay → `agent_hold.user_context` bọc `run_agent`/`confirm_action` ⇒ tool run_stage/tts/mux/dịch in-process đi `_manual_hold_override` gỡ HOLD sau claim; `_agent_run_stage("tts")` của người không gỡ HOLD trước claim, claim OK + QA-block → `qa_override` qua `Manifest.update`; hook heal/av-sync bọc `auto_context` (không tính tay); `agent_hold.py`: `user_context`, `manual_source` (brain/heal luôn thắng), `source` ghi `…+agent_chat:telegram`. Brain (in-process/header `brain`), Auto-pilot, heal KHÔNG gỡ. Test mới `tests/test_agent_hold_telegram.py` (14). **Restart :8801 + bot Telegram (:8802).** Port V4/V5/V6 CHƯA sửa. Bak `.backup_edit_20261112_agentI2\`. Fix `docs/fixes/2026-11-12-brain-notify-v2.md` mục D.
- **Second Brain: tin Telegram dựng theo MẪU + gỡ HOLD khi chạy tay + hoãn heal lúc khởi động** (agent H, chủ dự án: tin «nhiều, loạn, không hiểu»). MỚI `agent_brain_notify.py` (1 khối/job: emoji + tên phim VI rút gọn + P<n> + id rút gọn + ≤3 dòng chuyện gì / brain làm gì + kết quả / «Cần bạn»; plain text, bỏ markdown/`<badge>`/`|`); `agent_brain.py`: sự kiện có cấu trúc (`_emit`, `detect_stage_events` → dict, `hold_set`, nhắc lỗi ≤ mỗi 2 h ×3), văn DECISION LLM chỉ vào log, tool mutate LLM → tin «Brain: … → kết quả», heal rule path kèm kết quả, hoãn heal+LLM 180 s sau start, runtime `set_hold` qua `Manifest.update`; `agent_watch.py`: chờ `AGENT_HEAL_START_DELAY_SEC` (180) trước lượt heal đầu, bỏ job đang chạy, tin theo mẫu; `agent_heal.py`: `start_delay_sec`, `job_active` (queue.current / engine sống / claim) → `heal_job` không làm gì; MỚI `agent_hold.py` + `server.py` `_manual_hold_override` trong `/run/{stage}`, `/tts`, `/mux`, `/translate`, `/translate-fill` (chỉ request HTTP từ UI): job HOLD → gỡ cờ + `agent.hold_override` + 1 tin; `_auto_gpu`/`_agent_set_hold`(brain) không HOLD lại khi chưa có high mới; `_run_engine` lưu 40 dòng cuối vào `engine_fail_<script>.log` + `stages.<stage>.engine_tail`. `routes_agent.py`: hook `job_active`. Test mới `tests/test_agent_brain_notify.py` (28), `test_agent_brain_events.py` chỉnh 6 kỳ vọng. Config mới (mặc định trong code): `AGENT_BRAIN_REMIND_SEC`, `AGENT_BRAIN_REMIND_MAX`, `AGENT_BRAIN_TZ`, `AGENT_HEAL_START_DELAY_SEC`. **Restart :8801.** Port V4/V5/V6 CHƯA sửa. Bak `.backup_edit_20261112_agentH\`. Fix `docs/fixes/2026-11-12-brain-notify-v2.md`.
- **Second Brain: Telegram theo sự kiện + gỡ HOLD cũ tất định + DECISION lọc/khử trùng lặp** (agent G, chủ dự án phàn nàn spam). `agent_brain.py`: chế độ mặc định `AGENT_BRAIN_TELEGRAM=events` — chỉ báo stage →running/done/failed, job xong toàn bộ, brain HOLD/CLEAR/heal; trạng thái trước lưu `logs/agent_brain_state.json` (`job_stages`); gộp 1 tin/tick. Digest «Brain báo cáo» chỉ ở report/all, ≥600 s (`AGENT_BRAIN_TG_SEC` mặc định 600), chỉ khi nội dung đổi. DECISION chỉ khi có tool mutate hoặc job failed/high/held, khử trùng lặp 30' (`AGENT_BRAIN_DECISION_DEDUP_SEC`). Deep tick bỏ job running khoẻ/job đã xong, cooldown 30' cùng tình trạng (`AGENT_BRAIN_DEEP_SEC`); prompt kèm sẵn kết quả `pineline_job`/`diagnose`/plan heal (chỉ đọc) + tên tool chính xác. `clear_stale_holds`: job mux done + output (hoặc mọi stage done) còn `qa_blocked`/`hold_after_translate`/`held_at` → gỡ qua `Manifest.update` + 1 tin «CLEAR HOLD (job đã xong)» (vd `f0834acf0cc0`). `agent_heal.heal_job`: `note` khi plan safe rỗng (trước LLM hiểu `results: []` là «chưa thực thi»). Config: `config.json` + `pineline.config.json` `AGENT_BRAIN_TELEGRAM=events`, `AGENT_BRAIN_TG_SEC=600`. Test mới `tests/test_agent_brain_events.py` (11). **Restart :8801** (brain in-process). Port V4/V5/V6 CHƯA sửa. Bak `.backup_edit_20261112_agentG\`. Fix `docs/fixes/2026-11-12-brain-telegram-hold.md` (kèm chẩn đoán ASR `2937ffd7989f`).
- **Luồng dịch `translate_simple` thành MẶC ĐỊNH; rollback `TRANSLATE_PIPELINE=legacy`** (agent F2, quyết định chủ dự án; A/B golden: xưng hô simple 92 % (base 35 %), held-out 98,2 % (= nmt_hint 98,5 %), nhanh 2–3×). `translate_simple/cfg.py`: một nguồn sự thật — `pipeline_default()` (trống/`simple` → simple; `legacy|old|off|0|false|no` → luồng cũ, cùng quy ước V4/V5), `job_pipeline(wd, fresh=)` đóng dấu `manifest.translate_pipeline` (+`_why` default/inferred/fresh, `_at`) qua `Manifest.update`; job CHƯA đóng dấu mà có dấu vết luồng cũ (script.json / stage translate đã chạy, mode≠simple) → **giữ luồng cũ tới xong**; dấu vết simple (mode=simple / `simple_park`) → simple. `server.py`: `_translate_pipeline_simple(wd, fresh=)` uỷ cho cfg; `_auto_gpu`, `_process_gpu`, `_run_stage("translate")` (force = fresh), `_translate_flow` («Dịch LẠI» force = fresh, «Soát lại» = luồng của job), `retranslate_job` chốt luồng trước khi đánh running, **`translate-fill`** (job simple → `pipeline.run` không force; job cũ → `run_translate` lô 25 như trước; trả `pipeline`), **`_run_requested_review`** bước văn phong (job simple → simple `rereview=True`). Cờ con `SIMPLE_PAIR_RULES/PAIR_FILL/ZH_SOURCE/LEARN_INFERRED/LEXICON_EXCLUDE_GOLDEN` vẫn TẮT. Test: `test_translate_b2/_b2_review/_b3` đặt `TRANSLATE_PIPELINE=legacy` trong fixture; `test_translate_simple.py` 4 ca chỉnh kỳ vọng + 6 ca mới (`test_f2_*`). **Có hiệu lực khi restart :8801.** Bak `.backup_edit_20261112_agentF2\`. Fix `docs/fixes/2026-11-12-translate-simple-default.md`.
- **ASR mặc định chạy trên giọng tách Demucs + `separate.py` chia khúc tại khoảng lặng, cắt/ghép theo mẫu** (agent E, quyết định chủ dự án). `asr.py`: `ASR_USE_DEMUCS` mặc định **1** (`0` = rollback); Demucs lỗi/OOM/thiếu gói → log + FALLBACK ASR trên audio gốc (không fail job); ASR đã xong → không chạy Demucs; force ASR không ép tách lại; stage asr hiện pha «Tách giọng». `separate.py`: bỏ `ffmpeg -f segment` FLAC cắt cứng 60'; trích WAV PCM gốc 1 lần, chia khúc (>`DEMUCS_LONG_THRESHOLD_SEC`=2400, ~`DEMUCS_CHUNK_SEC`=1800) tại khoảng lặng (`split_parts.find_best_cut_point`), đệm ngữ cảnh `DEMUCS_CHUNK_PAD_SEC`=5 rồi cắt theo mẫu, ghép kiểm **đúng số mẫu gốc** (`n_frames` vào manifest), resume theo khúc, dùng lại kết quả hợp lệ (số mẫu/độ dài khớp video); KHÔNG còn ghi đè `audio.wav`. Test mới `tests/test_separate_demucs_chunks.py` (19). **Có hiệu lực ngay cho ASR mới** (tiến trình con) — không cần restart; nhánh render tự tách nền trong `_do_render` dùng bản cũ tới restart :8801 (tương thích). V6: `scripts/asr_demucs_compare.{py,bat}` (A/B khi V2 rảnh), `scratch/voice_exp/embed_campplus.py --vocals`. Port V4/V5/V6 CHƯA sửa. Bak `.backup_edit_20261112_agentE\`. Fix `docs/fixes/2026-11-12-asr-demucs-default.md`.
- **Review độc lập translate-simple «next» + autofix** (~khuya, agent D). `translate_simple/post.py`: gỡ lặp VI chỉ ở câu mà ZH có lặp ASR + dọn dấu phẩy treo (trước: «Đi mau, đi mau!» → «Đi mau,!» trên MỌI câu simple); `pipeline.py`: gỡ lặp ZH sau `zh_source.sync_rows` (sync từng trả lại chữ lặp), `store.stutter_i`; `zh_source.py`: `_guard_ocr` (1 dòng OCR không còn nhân sang 2 câu ASR bị tách), không pypinyin ⇒ không sửa tên (trước: 天下第二→天下第一); `pronoun_rules_zh_vi.json`: 兄弟/«huynh đệ» ruột → anh chị em (không phải bạn bè tao/mày), bạn bè + «tớ», cha + «ba», gọi sếp + «chủ tịch/anh/chị»; `tools/collect_manual_edits.py`: chặn `--out` là thư mục cha của `--work` và `golden_heldout`. Test mới `tests/test_translate_simple_next_review.py` (8 ca, gồm byte-identical bảng bộ 2 tập + park→chạy lại); `test_translate_simple_next.py` đổi 1 kỳ vọng (không pypinyin). Cờ vẫn MẶC ĐỊNH TẮT; `server.py`/`translate.py` KHÔNG đổi. V6 `test_v2_translate_simple.bat` thêm file test (kỳ vọng 82). Bak `.backup_edit_20261112_agentD\`. Review `docs/reviews/2026-11-12-translate-simple-next-review.md`. Restart :8801 chỉ cần khi chạy job simple thật (golden_ab chạy tiến trình con, không cần).
- **translate-simple «next» — cờ thử nghiệm MẶC ĐỊNH TẮT + sửa gỡ lặp ASR** (~khuya, agent B). `translate_simple/`: lexicon `src` (14 translate_rules / 38 golden_derived) + `SIMPLE_LEXICON_EXCLUDE_GOLDEN`; mới `pair_rules.py` + `data/lexicon/pronoun_rules_zh_vi.json` (`SIMPLE_PAIR_RULES`: điền cặp xưng hô trống theo quan hệ, không đè plan); mới `pair_fill.py` (`SIMPLE_PAIR_FILL`: 1 lần gọi model bổ sung cặp thiếu ≥3 câu, lỗi/429 → bỏ qua); `SIMPLE_LEARN_INFERRED` (cặp suy luận vào glossary/bảng bộ chỉ khi bật + cổng done); mới `zh_source.py` (`SIMPLE_ZH_SOURCE`: phát hiện hardsub → OCR thắng ASR giữ timing, sửa tên gần đúng có bảo vệ); sửa lỗi: simple nay gỡ lặp ASR như luồng cũ (`heal_obvious_internal_stutter`, zh + vi). Mới `tools/collect_manual_edits.py`, `tools/simple_stats.py` (chỉ đọc). `server.py`/`translate.py` KHÔNG đổi. Cờ tắt = trùng từng byte bản gốc (8 kịch bản). Cần restart :8801 để job simple dùng code mới. V6: `golden_ab.py` +4 biến thể, `golden_ab_simple.bat next`. Chi tiết `docs/fixes/2026-11-12-translate-simple-next.md`.
- **Review độc lập translate-simple** (~đêm) — sửa (vẫn MẶC ĐỊNH TẮT, `server.py` không đổi): bảng bộ học tập mới (`stage_draft` ghi plan trước `save_from`, cổng done → `save_from`); lexicon trường `re` (`我去` chỉ gợi ý khi là thán từ đứng riêng, `大爷的`), 52 mục; dòng cặp xưng hô `tự xưng «x» · gọi «y» (ghi chú)`; thiếu `conf` vẫn kiểm; `i` trùng-khác không rv; `script.json` hỏng → sao lưu trước khi dựng lại; `s_name_ok` reset; `trace.jsonl` xoay 8 MB; mới `translate_simple/suggest.py` → `plan_suggestions.json` (cặp thiếu, không chèn plan). Test mới `tests/test_translate_simple_scenarios.py` (19). V6: `scripts/golden_ab_simple.bat` (A/B base/regex_mask_off/simple), `test_v2_translate_simple.bat` thêm file test. Review `docs/reviews/2026-11-12-translate-simple-review.md`. Không cần restart (luồng tắt). Bak `.backup_edit_20261112_simple_review\`
- **Luồng dịch simple (`translate_simple/`) — MẶC ĐỊNH TẮT, bật bằng `TRANSLATE_PIPELINE=simple`** (~chiều). Package mới: plan ∥ NMT (2 thread) → REVIEW cloud 1 lần/lô 30 câu (±4 ngữ cảnh) trả ĐỦ câu `{i,vi,spk,to,conf}`: sửa nghĩa + áp xưng hô theo cặp plan + tên/thuật ngữ + thành ngữ (`data/lexicon/idioms_zh_vi.json`, 51 mục) + dịch câu trống → hậu kỳ CHỈ chuẩn số + khoá thuật ngữ (không regex đại từ) → bộ kiểm cờ (trống/chữ Hán/đại từ lệch cặp plan khi conf ≥ 0.7/tên) → vá câu bị cờ ≤2 lượt → cổng done/park/hold; `trace.jsonl` từng câu. Một chính sách retry (`cloud_retry`), KHÔNG fallback local/switch_preset. `server.py`: rẽ nhánh `_auto_gpu` / `_process_gpu` / `_run_stage` / `_translate_flow` khi `TRANSLATE_PIPELINE=simple` (park → `waiting_review` B2 + `simple_park`; hold → `held_at=simple_gate`), `_queue_park_ready` chờ tới hạn với `simple_park`; mặc định = luồng cũ y nguyên. Config `SIMPLE_*` (mặc định trong code, không sửa config.json). Test mới `tests/test_translate_simple.py` (26 ca). V6: biến thể `simple` trong `scripts/golden_ab.py`, `scripts/test_v2_translate_simple.bat`. Bak `.backup_edit_20261112_simple\`. Thiết kế `docs/design/2026-11-12-translate-simple.md`, fix `docs/fixes/2026-11-12-translate-simple.md`. **Restart :8801** (mặc định tắt → không đổi hành vi; bật sau khi A/B golden).

- **Dịch đợt 3 — translate-b3: 4 cờ thử nghiệm chất lượng dịch, MẶC ĐỊNH TẮT (= hành vi cũ y hệt)** (~trưa). `translate.py`: `PRONOUN_REGEX_MIXED=0` tắt phép đổi đại từ tất định trên phim mixed (`apply_style_polish` ngươi→cậu/ta→tôi/vá «cậu tôi», `apply_pronoun_postpass` detox khi plan mixed); `REVIEW_PRONOUN_MASK=0` (+ `REVIEW_PRONOUN_PLAN_GUIDE`, mặc định 1) → REVIEW có khối (G) xưng hô theo plan + giữ fix chỉ-đổi-đại-từ sang dạng trong plan (K20 vốn bỏ); `HALFCUE_MERGE=1` (`HALFCUE_GAP` 0.35 s, `HALFCUE_MAX_CHARS` 40, `HALFCUE_MAX_CUES` 3) gom cue cắt đôi trước NMT/LLM → chia VI lại theo dấu phẩy/tỉ lệ ZH, không cue trống, giữ timing, ghi `group_id`. `server.py`: `FILL_PENDING_PARK=1` (D1) — câu NMT sót vá cloud lỗi → park `waiting_review` tự thử lại (B2) thay vì dừng chờ người; tôn trọng `TRANSLATE_FILL_MODEL=local`. Test mới `tests/test_translate_b3.py` (23 ca, gồm đối chiếu mặc định với bản gốc trên 567 câu golden). V6: `scripts/golden_ab.py` + `golden_ab.bat` (A/B 7 biến thể trên golden — chỉ chạy khi V2 rảnh), `scripts/test_v2_translate_b3.bat`. Bak `.backup_edit_20261112_translate_b3\`. Fix `docs/fixes/2026-11-12-translate-b3.md`. **Restart :8801** (cờ mặc định tắt → không đổi hành vi; bật cờ trong `pineline.config.json`/env sau khi có kết quả A/B).

- **Review độc lập translate-b2 + sửa cửa chờ cloud** (~sáng). `cloud_retry.py`: ngân sách chờ CHUNG / đợt limit (≈577 s, trần 3600 s) — trước đó tổng chờ nhân theo số luồng (24 luồng ≈ 2,4 giờ); request bay từ trước đợt limit không mở cửa; Retry-After > ngân sách còn lại → bỏ cloud ngay; không thử lại khi lời gọi đã kéo dài ≥ ~1155 s; probe chết vì BaseException nhả quyền dò. Test mới `tests/test_translate_b2_review.py` (18 ca, gồm đối chiếu cấu hình cũ với bản trước b2 → giống hệt); `test_translate_b2.py` đổi 1 kỳ vọng. Không đổi `translate.py`/`server.py`/`llm.py`. Bak `.backup_edit_20261112_translate_b2_review\`. Review `docs/reviews/2026-11-12-translate-b2-review.md`. **Restart :8801** (cùng lần restart cho translate-b2; KHÔNG bấm translate-fill trước).

## 2026-11-11

- **Dịch/REVIEW đợt 2 — translate-b2 (retry cloud khi Aurora limit + bỏ gemma khỏi bước dịch)** (~11-12 sáng). `cloud_retry.py` (mới): 429/limit/quota + 5xx/timeout → thử lại CÙNG model cloud backoff 30→60→120→240 s (jitter, Retry-After), kiểm `.stop` ≤2 s, cửa chờ chung giữa các luồng (1 probe) — áp cho lô REVIEW, pass1 full file, dịch lấp câu trống; hết lượt mới fallback local C9 (`REVIEW_LOCAL_FALLBACK=1`) hoặc lô lỗi → park (`=0`). `translate.py`: NMT primary + REVIEW cloud → `run_translate` KHÔNG switch preset gemma, câu NMT sót vá bằng rmodel cloud (`fill_pending=1` nếu vẫn lỗi); `run_review` bước 0 vá bằng rmodel + hậu kỳ tất định chỉ trên câu vừa vá; `post_translate_gate_action`; log `[vram]`. `server.py`: cổng sau dịch → `run_review` bước 0 thay vì gọi lại `run_translate` (cấu hình cloud). `llm.py`: giữ response/`__cause__` lỗi Aurora. Config mới `REVIEW_CLOUD_RETRY`, `REVIEW_CLOUD_BACKOFF`, `REVIEW_LOCAL_FALLBACK`, `TRANSLATE_FILL_MODEL` (mặc định trong code). Test mới `tests/test_translate_b2.py` (cloud 47/47; code cũ 19 fail); 2 test b1 thêm `REVIEW_CLOUD_RETRY=0`. Bak `.backup_edit_20261111_translate_b2\`. Fix `docs/fixes/2026-11-11-translate-b2.md`. **Restart :8801** (server import lúc khởi động; translate-fill chỉ reload `translate.py` — KHÔNG bấm trước restart).

- **Review độc lập translate-b1 + sửa nhỏ** (~19:00). `translate.py`: `_parse_review_fixes` nhận JSON TRỌN giữa chữ thừa/sau `<think>` (`_scan_review_json` mới; JSON cụt vẫn = lô lỗi), thông điệp `ReviewBadOutput` kèm đầu/cuối phản hồi. `pronoun_register_policy.py`: thêm ngoại lệ «cậu này/đó/nọ/con/chàng/thiếu gia/thiếu niên/công tử/cháu»; «các cậu» giữa câu không viết hoa «Các». Test mới `tests/test_translate_b1_scenarios.py` (79 ca kịch bản tích hợp; cloud 79/79, toàn bộ tests 293 pass/14 fail môi trường như trước). Bak `.backup_edit_20261111_translate_b1_review\`. Review `docs/reviews/2026-11-11-translate-b1-review.md`. **Restart :8801** khi queue rảnh — KHÔNG bấm translate-fill trước restart.

- **Dịch/REVIEW đợt 1 — translate-b1 (C1/C2/C3/C9/T18 từ review dịch V6)** (~18:25). `translate.py`: REVIEW trả rỗng/JSON cụt/`{}` → `ReviewBadOutput` → lô LỖI (không rv, retry B1/park B2), `{"fixes":[]}` mới là "không cần sửa"; `_apply_result` không ghi đè câu `manual` (vẫn rv); fallback local REVIEW∥ chỉ 1 luồng switch preset/lượt + gọi local tuần tự; phân loại lỗi theo mã HTTP/kiểu exception; 413/context-length → chia lô, không đổi preset; `run_translate` giữ trường thêm của asr.json (`_seg_row`). `pronoun_register_policy.py`: «cậu» chỉ thay khi là ngôi 2 độc lập («Cậu ấy/cậu ruột/ông cậu/cậu Lâm» giữ), bỏ qua manual. `agent_name_pass.py`, `agent_pronoun_pass.py`, `pronoun_consistency.py`: không ghi đè manual. `preset_switcher.py`: `switch_allowed()` chặn đổi preset khi chạy pytest. Test mới `tests/test_translate_b1.py` (cloud 51/51; code cũ 37 fail). Không đổi prompt/văn phong/xưng hô mặc định. Bak `.backup_edit_20261111_translate_b1\`. Fix `docs/fixes/2026-11-11-translate-b1.md`. **Restart :8801** khi queue rảnh (server giữ hàm import lúc khởi động; `translate_fill` reload `translate.py` → trạng thái trộn cũ/mới tới khi restart).

- **Áp fix B1/B2/B3/B4/B7 + cổng (từ V4) + tối ưu B5/B6/B8/B10 + engine/router cho V5** (~03:05). Chép 7 file đã sửa (giống hệt gốc V2) + `agent_tool_loop.py`; `server.py` `_req_audio`, `_engine_script_path` + `PYTHONPATH`, router `http_routes.*`; `translate.py` dừng song song < 2 s + ghi atomic; `restart_server.py` `_job_parked`; `agent_autopilot.py`/`migrate_work.py` `PINELINE_BASE`. Test mới `tests/test_review_fail_not_rv.py`, `test_park_review_retry.py`, `test_optimize_b5_b6.py` (VM 16/16). Tooling: `scripts/sync_from_v2.py`, `brain_export.py`, `build_workflow_html.py`, `docs/brain/workflow.html`. Bak `.backup_edit_20261111_fix-batch\`, `…_optimize\`. Fix `docs/fixes/2026-11-11-review-fail-park-port.md`, `…-optimize-b5-b6-b8-b10.md`. **Restart :8801** khi queue rảnh (riêng `translate.py` được nạp lại ngay nếu gọi `translate_fill`).

- **Tooling sync V2/V4/V5** (~02:45). `scripts/tree_audit.py` (mới), `scripts/brain_build.py` (bố cục package, `generated/duplicates.md`, bỏ qua junction hỏng), agent `port-sync-guardian` + `/sync-check` trong `claude_setup/`. ⚠️ V4 đã có fix B1/B2/B3/B4/B7 + cổng; **V2 chưa** — đừng chép `server.py`/`translate.py`/`preset_switcher.py`/`agent_brain*.py` V2→V4 trước khi V2 có cùng fix. **Không cần restart.**

- **Review tổng + bug hunt** (~02:30). `docs/reviews/2026-11-11-codebase-overview-bugs-improve.md` (B1–B11, roadmap I1–I10). `scripts/brain_build.py`: `LAYER_RULES` thêm `test_channel`→publish trước `test_`. **Không cần restart.**

- **Second Brain dev + đội subagent** (~01:50). Mới: `scripts/brain_build.py` (AST → `docs/brain/modules/*.md` thẻ module AUTO+MANUAL, `docs/brain/generated/` index/config-keys/api-routes/dependency-graph/hotspots/long-functions/artifacts-ports, `_meta.json` sha1 để `--check`); `docs/brain/` README, processes (job-pipeline, queue-studio-sop, translate-review), workflows (dev-change, bug-and-review, ai-change), agents (runtime, dev-team), glossary; MANUAL viết sẵn cho `manifest`, `job_queue`, `config`. `CLAUDE.md` (định tuyến agent + luật sửa). `.cursor/rules/second-brain.mdc`. `claude_setup/` (7 subagent: bug-hunter, code-reviewer, fix-advisor, improvement-advisor, agent-architect, brain-keeper, brain-librarian + 7 lệnh /bughunt /review /fix /improve /agent-audit /brain-sync /ask-brain) → chạy `claude_setup\INSTALL.bat` để chép vào `.claude\`. Chỉ thêm file docs/tooling, không đụng runtime. Bak docs sửa: `.backup_edit_20261111_second-brain\`. **Không cần restart.**

- **Aurora∥ REVIEW max** (~00:50). `REVIEW_PARALLEL=24` (cap 32); file-first config keys. Bak `…_review-parallel-max\`. Job đang lô∥ giữ worker cũ tới hết lượt; job review mới lấy 24. Sync V2/V4/V5. **Không bắt buộc restart** (config file-first).

- **Pass1 = GPT đọc FULL file** (~00:36). Upload 1 SRT (≤5MB) hoặc chunk 1000 cue/file rồi merge; **tắt** chat sample (`ALLOW_CHAT_FALLBACK=0`). Bak `…_pass1-full-file\` (+ zip `…_0033.zip`). Fix `docs/fixes/2026-11-11-pass1-upload-size.md`. Sync V2/V4/V5. **Restart :8801** khi rảnh (Pass1 lần review mới).

- **Studio SOP 1 job/ghế + Aurora∥ REVIEW** (~00:10). User khóa: ASR→NMT→REVIEW (Aurora∥ / local fallback)→TTS→mux→Done→next. `_auto_gpu` chạy hết `run_review` trong ghế (không nhả sớm); `translate` fan-out `REVIEW_PARALLEL=6`; config keys. Bak `…_studio-1job-pipeline\`. Fix `docs/fixes/2026-11-11-studio-1job-pipeline.md`. Sync V2/V4/V5. **Restart :8801** để nạp (cắt `365baf` nếu đang dịch).

## 2026-11-10

- **Queue park HOLD/soát — không nhảy job** (~23:57). Studio invariant: 1 job→output. `_worker_loop` park khi `held`/`waiting_review`; `_auto_gpu` stamp `held_at=waiting_review`; QA gate stamp HOLD; `set_park_ready_hook`. Bak zip `…_2357.zip` + codebak `…_queue-park-held\`. Fix `docs/fixes/2026-11-10-queue-park-held.md`. Sync V2/V4/V5. **Restart :8801** (cắt current `365baf` nếu restart ngay — hỏi user).

- **REVIEW voice loosen (Aurora)** (~19:28). User chọn nới REVIEW: văn phong tự nhiên khi vá lỗi, không full rewrite. `review_batch` + `_style_voice_banner`; restart CLI gpt-6 60892. Bak `…_review-voice-loosen`. Fix `docs/fixes/2026-11-10-review-voice-loosen.md`. **Không cần restart server** (CLI).

- **REVIEW = chatgpt/gpt-6 (Aurora thật)** (~19:20). User chọn gpt-6; UI Aurora trước chỉ lưu queue_opts. Wire `_resolve_review_model`; config REVIEW_MODEL/AURORA_REVIEW_MODEL; stop Gemma; CLI force re-review 60892 p01+p02. Bak codebak `…_review-gpt6`. Fix `docs/fixes/2026-11-10-review-gpt6-aurora.md`. Sync V2/V4/V5. **Restart :8801** khi rảnh (CLI đang review).

- **Brain hang LLM trace+fix** (~19:00). User B: không chỉ merge — LLM hiểu root/plan rồi mới mở HOLD. `agent_hang_fix.py` (+ wire `scan_and_heal_job`, cuối `run_review`); `hang_ack` cho dialogue_trail; skip khi review đang ghi. Config `BRAIN_HANG_FIX=1`. Job `60892` p01 clear HOLD + TTS; p02 chờ review. Bak zip `…_1857.zip` + codebak `…_hang-llm-fix`. Fix `docs/fixes/2026-11-10-brain-hang-llm-fix.md`. Sync V2/V4/V5. **Restart :8801** khi rảnh để nạp in-process (CLI/review subprocess đã thấy module mới).

- **Brain TG report** (~13:27). AGENT_BRAIN_TELEGRAM=report + digest ~120s; standalone D:\\PinelineV2_tmp\\_run_brain_tg_report.py (không restart :8801 đang ASR). **Restart :8801** sau để nạp in-process.

- **FireRed BF16 forced_align** (~13:20). Cast logits→float32 trước torchaudio align (BF16 decode giữ). Vendor fireredasr_aed.py V2/V4/V5. Fix docs/fixes/2026-11-10-firered-bf16-align.md. **Không cần restart server** nếu ASR là subprocess mới.

- **FIRERED_ROOT + _check_stopped** (~13:13). Config FIRERED_ROOT sai path cũ Z:/Pineline/vendor/... → Z:/PinelineV2/vendor/FireRedASR2S. Thêm server._check_stopped (ASR split ≥3h NameError). Fix docs/fixes/2026-11-10-firered-root-path.md. **Restart :8801** nếu env còn FIRERED_ROOT cũ.



- **Mix #1+#3 title→ngươi + UI REVIEW backup** (~08:50). Bak zip `…_0847.zip` + codebak `…_mix13-review-backup`. `pronoun_register_policy.py`; `agent_pronoun_pass` #3; `review_batch` mask #1; config `PRONOUN_TITLE_POLICY=1` `REVIEW_PRONOUN_MASK=1`; UI/batch `review_backup=off|aurora_parallel`. Sync V2/V4/V5. Fix `docs/fixes/2026-11-10-mix13-title-nguoi.md`. **Restart:** :8801 để nạp translate/pronoun/UI.
- **NMT GPU** — MT_ZH_VI_DEVICE=cuda + MT_ZH_VI_BATCH=256 (bench 800 cue: CPU~200 → CUDA~1089 cue/s). Bak Z:\\PinelineV2_codebak\\2026-11-10_mt-cuda-batch\\ + zip Z:\\PinelineV2_backup_2026-11-10_0841.zip. Sync V2/V4/V5 config. **Restart:** :8801 nếu process đã load NMT trên CPU.\n- **firered_asr.py** — mặc định `use_half=True` (BF16 trên 3060) khi GPU; tắt bằng `FIRERED_USE_HALF=0`. Bak `Z:\PinelineV2_codebak\2026-11-10_firered-use-half\` + zip `Z:\PinelineV2_backup_2026-11-10_0827.zip`. **Restart:** server :8801.
- **run_v2.bat / run.bat / run_tele_cmd.bat** — LF→CRLF fix (CMD `if not exist`); bak `Z:\PinelineV2_codebak\2026-11-10_run-v2-crlf\`. **Restart:** `run_v2.bat`.
- **Restart :8801 nạp Brain C** (~00:36). `restart_server.py --clean-env` PID **4652**; tắt standalone. Sau restart TTS `05670` lọt ~104 câu (HOLD/override mất) → stop + HOLD lại + sửa cue i=34 trùng VI với i=35. Queue bị clear (requeued 0). **Không cần restart lại.**

## 2026-11-09

- **Brain C = LLM tool-loop** (~00:15 10/11). Backup zip `…_0007.zip` + codebak `…_brain-force-tool\`. User chọn C: Brain điều phối `agent_core` 24/7. `agent_brain_context` snapshot; `llm_tick` bind FS/HTTP Runtime + `force_first_tool=pineline_status` + deep `pineline_job`; `agent_core.run_agent` nhận `force_first_tool`/`force_first_args`; chat API field tương ứng. Smoke: 7 tools (status→job→hold→running_check), HOLD `05670`. Fix `docs/fixes/2026-11-09-brain-llm-tool-loop.md`. Sync V2/V4/V5. Standalone loop nạp code mới. **Restart :8801** khi 05670 idle để nạp in-process brain + force_first_tool vào server.

- **Second Brain Agent (full silent)** (~23:49). Backup `…_second-brain\`. Module `agent_quality.py` + `agent_brain.py`; QA gate xét `qa_brain.json` high; auto TTS HOLD trước khi lồng; startup `_start_agent_brain`; config `AGENT_BRAIN=1`. Design `docs/design/2026-11-09-second-brain-agent.md`. Tests `tests/test_agent_quality.py` 4 passed. Sync V2/V4/V5. Standalone loop tạm `D:\PinelineV2_tmp\_run_brain_standalone.py` (tránh restart giữa review 05670). **Restart :8801** khi queue/review rảnh để nạp thread trong server.

- **REVIEW → Gemma4 26b** (~22:18). User yes đổi luôn. Config `REVIEW_MODEL`/`REVIEW_PRESET=gemma4-26b-qat-uncen-mtp` (V2/V4/V5). Stop 12B mid-job → restart :8801 → force `review_only` `05670cbf7c1c`. Runtime :8083 = `gemma4-26b-qat-uncen-mtp-131k`. Lúc chuyển: `script.json` mất (đã restore từ `script.before_rereview_20261109_215318.json` + heal 没大没小). **Restart :8801** (đã).

- **QA watch 05670 + Gemma12 vs 26** (~22:12). Watcher deterministic `D:\PinelineV2_tmp\_qa_watch_05670.py` → `qa_watch_05670/REPORT.md`. Verdict review: 12B = cổng nhanh, không tin thành ngữ — `docs/reviews/2026-11-09-gemma12-vs-26-review.md`. **Không restart.**

- **没大没小 calque** (~22:05). Backup `…_2205.zip` + `…_meidameixiao-calque\`. NMT+review để `Cậu còn chưa lớn không nhỏ.` (`05670` i=8, `rv=1`). Polish + style term + Pass1 heuristic + prompt; heal live + watcher. Sync V2/V4/V5. Fix `docs/fixes/2026-11-09-meidameixiao-calque.md`. **Restart :8801** khi queue rảnh (job hiện heal ngoài process).

- **hg-rpc idle `_last_used`** (~21:53). `hongguo_rpc._idle_watch` thiếu `global _last_used` → crash thread idle. Sync V2/V4/V5. **Restart :8801** (đã).

- **Stop lúc soát → nhảy TTS** (~21:50). Tôn trọng `.stop` trong `run_review`; không mark_done/TTS khi stop; chặn TTS nếu còn câu chưa `rv`. Job `05670cbf7c1c` clear rv + `review_only` force. Fix `docs/fixes/2026-11-09-stop-during-review-tts.md`. **Restart :8801** (đã).

- **REVIEW Pass1 full VI + duty F** (~21:35). Backup `…_2130.zip` + `…_review-fullvi-pass`. Pass1 đọc pair SRT; duty F; heal đuôi «trước đó»; test 26 cue — i=0 sửa. Kết quả `docs/reviews/2026-11-09-review-pass1-halfcue/`. Sync V2/V4/V5. **Restart :8801** khi queue rảnh.

- **Sandbox retranslate job 9c3af (6×90s)** (~21:20). SenseVoice→NMT+Gemma; COMPARE 149/194 improved, 0 worse. `docs/reviews/2026-11-09-job5-retranslate-compare.md`. **Không restart.**

- **Audit VI job 9c3af (video 5)** (~20:52). YT VTT → 4132 cue; verdict poor (tên/xưng hô/calque/ASR-TTS). Report `docs/reviews/2026-11-09-job5-vi-audit.md`. Sandbox retranslate còn chạy. **Không restart.**

- **ASR-heal follow-up (onomat + pre-review)** (~20:40). Codebak `…_review-asr-merge\translate.py.before-onomat-followup`. `heal_obvious_internal_stutter` không cắt `叮当叮当`/`哈哈…`; `run_review` gọi `apply_asr_stutter_heal` trước LLM; prompt E có ví dụ; `review_batch` mặc định `_rmodel()`. Sandbox: heal i=17, giữ i=109; filter synthetic E PASS; Gemma vẫn hay bỏ sót E nên deterministic heal là lưới chính. Sync V2/V4/V5. **Restart :8801** khi queue rảnh.

- **REVIEW chữa ASR cut/repeat** (~20:25). Backup zip `Z:\PinelineV2_backup_2026-11-09_2016.zip` + codebak `Z:\PinelineV2_codebak\2026-11-09_review-asr-merge\`. `translate.py`: duty E rà stutter/tail→head; filter giữ sửa merge có bằng chứng; post-pass gỡ lặp nội bộ rõ ràng; làm mềm `吃醋` (`ghen` thường đúng nhưng `uống giấm` không tự động là hard error). Probe sandbox i=17 + sample i=582 + tail-head PASS; pytest 2 passed. Sync V2/V4/V5. **Restart :8801** khi queue rảnh.

- **REVIEW → Gemma4 12b local** (~20:07). Backup zip `…_2007.zip` + `…_review-gemma12b\`. `REVIEW_MODEL`/`REVIEW_PRESET=gemma4-12b-qat-mtp-fast` (cùng preset dịch cũ). Sync V2/V4/V5. **Không restart** (config hot). Job review tiếp theo auto-switch gemma.

- **REVIEW → local qwen36-turbo** (~14:20). Backup zip `…_1419.zip` + `…_review-qwen36\`. `REVIEW_MODEL=llama/qwen36-turbo` (pineline.config + config.json). Smoke review_batch OK ~15s. Sync V2/V4/V5. **Không restart** (config hot). Lần review đầu có thể mất ~70s nạp GGUF nếu đang gemma translate. *(superseded ~20:07 → Gemma4 12b)*

- **Poster hg 502 junk name** (~14:05). Backup zip `…_1402.zip` + `…_hg-poster-502\`. `hg_name` part/job/`downloads` → derive parent Lib; poster missing/junk **404** không 502; Films UI `resolveFilmPosterName`; heal 6 hàng DB. Fix `docs/fixes/2026-11-09-hg-poster-502-junk-name.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes — `1e2379edb4fe_p01` running) để nạp `routes_hg` 404; hard refresh Films UI.

- **Meta AI image → :3377** (~13:58). Backup zip `…_1358.zip` + `…_meta-chatgpt-3377\`. `meta_studio` đọc config `CHATGPT_*` (không chỉ env); ưu tiên local; Bearer `sk-local`; timeout ảnh theo config; `/api/meta/ai-image` 300s. Smoke ~23s / 1.5MB. Fix `docs/fixes/2026-11-09-meta-ai-image-3377.md`. Sync V2/V4/V5. **Không bắt buộc restart** (sidecar reload `meta_studio`); restart :8802 chỉ để nạp timeout 300 trong handler.

- **ChatGPT timeout 900s** (~13:55). Backup `…_chatgpt-timeout\`. Bỏ trần 120s; `CHATGPT_TIMEOUT=900` (+ PLAN_FILE 900, trần 1800). Sync. **Restart :8801** (chờ yes) — đang có job thì đợi idle.

- **Restart :8801 nạp ChatGPT :3377** (~08:07). `restart_server.py --clean-env` · PID **34240**. Job `9c3af49061a2_p01` mux bị đứt giữa chừng (TTS đã đủ 2122). **Không cần restart lại.**

- **ChatGPT → local :3377** (~07:40). Backup `…_chatgpt-local-3377\`. `CHATGPT_BASE_URL=http://127.0.0.1:3377/v1` + `CHATGPT_API_KEY=sk-local`; fallback Aurora 5005. Smoke `PONG-LOCAL` OK. Sync V2/V4/V5.

- **Launcher bat pin Python quote** (~07:30). `if exist … ( set PY= )` + CRLF + fallback where; V2/V4/V5. Fix `docs/fixes/2026-11-09-bat-py-quote.md`. **Không restart.**

- **Test Block chọn account** (~05:42). Backup `…_tc-pick-account\`. Modal dropdown Project; `test-one` + `upload_test_sample(project_id=)`; clear cờ local. Sync. **Hard refresh** Films UI (sidecar reload module).

- **Test Block quota false-positive** (~05:25). Backup `…_0521.zip` + `…_tc-quota-stale\`. `test_channel`: ngày Pacific; classify lỗi chặt; purge cờ legacy; UI lý do hết hạn. Live `available 3/3`. Fix `docs/fixes/2026-11-09-tc-quota-false-positive.md`. Sync V2/V4/V5. **Không restart** (sidecar reload module). Hard refresh Films UI.

- **Restart :8801** (~05:16). `restart_server.py --clean-env` · queue rỗng · nạp keep-NMT + NMT primary + PLAN file + hv_auditor. Sidecar :8802 giữ. **Không cần restart lại.**

- **Filter bỏ polish GPT** (~04:52). Backup zip `…_0452.zip` + `…_review-keep-nmt2\`. `_filter_cosmetic_nmt_fixes`: mặc định DROP; chỉ giữ CJK/tên-lock/TTS rút thật (từ mới ≤15%); cấm đổi xưng hô miệng. Probe i=48 → giữ NMT. Fix `docs/fixes/2026-11-09-review-keep-nmt.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **GPT rà tối thiểu** (~04:46). Backup `…_review-keep-nmt\`. User: NMT đã tốt mà GPT đổi thừa (vd Lão tử→Tôi). `review_batch` mặc định giữ NMT; chỉ vá A–D; temp 0.1. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **Văn phong linh hoạt + giữ NMT primary** (~04:15). Backup `…_flex-style-nmt-primary\`. Bỏ khóa register; mixed→MT base. Sync. **Restart :8801** (chờ yes).

- **P1 harden plan-file + A/B** (~04:10). Vá null-list; scene `[i=N]`; timeout PLAN. A/B report. Sync. **Restart :8801** (chờ yes).

- **Plan file + review style** (~04:05). Backup `…_plan-file-review-style\`. `PLAN_MODE=file`: upload full SRT → GPT glossary; review style_lock+mẫu. Follow-up fix `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **NMT dịch chính / LLM rà** (~03:35). Backup `…_mt-primary-llm-review\`. User đảo: `MT_ZH_VI_ROLE=primary` — HachimiMT ghi VI; gemma chỉ vá sót; GPT mini `run_review`. Follow-up `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **MT auto theo genre** (~02:45). Backup `…_mt-genre-auto\`. `MT_ZH_VI_MODEL=auto`: modern/mixed → base; xianxia → QT. Follow-up fix `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **NMT draft + slim glossary + REVIEW GPT mini** (~02:40). Backup `…_mt-draft-slim-gloss\`. Sau sandbox VERDICT: gắn lại `mt_zh_vi.py` làm **nháp** `mt_vi` → LLM; lock/name-pass/series chỉ `type=lock`; `REVIEW_MODEL=chatgpt/gpt-5-6-mini`. Config `MT_ZH_VI=1`. Fix `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`. Sync V2/V4/V5. **Restart :8801** (chờ yes).

- **NMT bench sandbox** (~01:30). Revert hook tạm; bench `D:\PinelineV2_tmp\mt_bench\` job `0a5f60aead18` (base+QT). Verdict → merge draft (mục trên).

- **HV Auditor (phương án A)** (~01:15). Backup `…_hv-auditor\`. Module `hv_auditor.py` + Unihan `data/unihan/kVietnamese.json`; trap-fix 逆; warn không đè tên riêng; series hygiene apply/save; gắn `ensure_hard_terms`. Fix `docs/fixes/2026-11-09-hv-auditor.md`. Sync V4/V5. **Restart :8801** (chờ yes).

## 2026-11-08

- **逆天而行 → Nghịch (không Nghị)** (~22:30). Backup `…_nghich-thien-heal\`. Heal series + 3 job glossary/script; seed lock trong `ensure_hard_terms`. Fix `docs/fixes/2026-11-08-nghich-thien-ni-hanh.md`. Sync V4/V5. **Restart :8801** để nạp seed (glossary đã heal trên đĩa).

- **Auto-split parent merge heal** (~19:18, restart ~19:21). Backup `…_split-parent-merge-heal\`. Parts xong mà parent treo (sau restart) → `_queue_split_parent_merge_if_ready` / notify sau part / GET job / entry auto-split. Job `2cd10c3fa86d` Full ~6925MB. Fix `docs/fixes/2026-11-08-split-parent-merge-heal.md`. Sync V4/V5. **Restart :8801** (đã).

- **Hongguo classic full split** (~10:10). Backup `…_hg1-full-split\`. Restore `hongguo.html` pre-WinUI; `/api/hg`=HTTP only; `/api/hg2`=RPC; hongguo2 → `/api/hg2/*`. Fix `docs/fixes/2026-11-08-hongguo1-full-split.md`. **Restart :8801** (đã). Hard refresh `/hongguo` + `/hongguo2`.

- **Merge frag naming + corrupt skip** (~09:20). Backup `…_merge-frag-re\`. `_FRAG_RE` nhận `S01E001`; `_MERGED_RE` nhận `merged.mp4`; dedupe/skip tập hỏng (NVENC -22). Fix `docs/fixes/2026-11-08-merge-frag-naming.md`. Sync. **Không bắt buộc restart** (bridge reload) — nên restart :8801 nếu worker merge đang chạy code cũ.

- **Hongguo1 restore + isolate hg2** (~08:55). Backup `…_hg1-isolate\`. Restore `hongguo.html` gốc; `hg_ui_ctx` + `X-HG-UI:2` (RPC) / hg1 `http_first`; `HG_BACKEND=auto`. Fix `docs/fixes/2026-11-08-hongguo1-restore-isolate.md`. **Restart :8801** (đã). Hard refresh `/hongguo` + `/hongguo2`.

- **Hongguo1 kẹt bảng hot** (~08:45). Backup `…_hongguo1-boot\`. *(superseded 08:55 — đã restore HTML gốc, không giữ patch parallel trong hongguo.html.)* Fix `docs/fixes/2026-11-08-hongguo1-boot-stuck.md`.

- **Hongguo2 Retry 502 license** (~08:25). `downloads.retry` prove license (force nếu helper chờ licence); UI Retry trên Failed. Follow-up `docs/fixes/2026-11-08-hongguo2-dl-stop.md`. **Hard refresh** (bridge hot-reload).

- **Hongguo2 Stop download** (~08:16). Backup `…_dl-stop\`. Helper chỉ có `cancelAll` → `cancel_download(sid)` = cancelAll + requeue others; UI **Stop** / **Stop all**; × trên active = stop. Fix `docs/fixes/2026-11-08-hongguo2-dl-stop.md`. Sync V4/V5. **Restart :8801** (đã). Hard refresh.

- **Hongguo2 qualities 502 + /api/disk 404** (~08:10). Backup `…_qualities-disk\`. `series.qualities` không gọi RPC flaky (helper crash) → ladder mặc định; thêm `GET /api/disk` (free_gb). Fix `docs/fixes/2026-11-08-hongguo2-qualities-disk.md`. Sync V4/V5. **Restart :8801**. Hard refresh.

- **Hongguo2 Play nhanh (480p + cache + %)** (~07:50). Backup `…_hongguo2-play-fast\`. Preview không dùng 1080p; async start/job hiện progress; cache hit tức thì. **Restart :8801** (đã). Hard refresh.

- **Hongguo2 Play RPC playback** (~07:30). Backup `…_hongguo2-play-rpc\`. Preview không cần :8000: `playback.prepare` + `/api/hg/playback/stream`; license ensure; UI `<video>` local. **Restart :8801** (đã). Hard refresh.

- **Hongguo2 Play + scroll fill** (~07:10). Backup `…_hongguo2-play-scroll\`. Nút Play cạnh Quality + preview modal (`/api/hg/preview`). Browse: scroll/IO/`maybeBrowseMore` fill viewport (hết kẹt 24). Fix `docs/fixes/2026-11-08-hongguo2-play-button.md`. Sync V4/V5. **Hard refresh**.

- **Hongguo2 Browse load-on-scroll** (~07:05). Backup `…_hongguo2-browse-scroll\`. Infinite scroll qua `sessionId`+`nextOffset`+sentinel IO; page 24; dedupe `series_id`. Fix `docs/fixes/2026-11-08-hongguo2-browse-scroll.md`. Sync V4/V5. **Hard refresh** (không restart).

- **Hongguo2 dropdown WinUI + filter RPC** (~06:22). Backup `…_hongguo2-dropdown-winui\` + zip `…_0622.zip`. Custom dd menu (pill/accent/menu tối); `feed.select` wrap `List[str]` (helper bỏ string đơn). Hot-reload rpc qua marker `list[str]`. Fix `docs/fixes/2026-11-08-hongguo2-dropdown-winui.md`. Sync V4/V5. **Hard refresh** (bridge reload mỗi request — không bắt buộc restart :8801).

- **Python default 3.12 (A+B)** (~06:12). Backup `…_run-v2-python312\` + zip `…_0610.zip`. Machine PATH bỏ `Python315`; đầu PATH = `C:\Python312`; `PY_PYTHON=3.12`. Launcher pin 312: `run_v2.bat`/`run_2.bat`/`run_tele_cmd.bat`/`run.bat` + V4/V5. Fix `docs/fixes/2026-11-08-python315-path-default.md`. **Mở terminal mới** (không bắt buộc restart :8801 — TTS đang chạy).

- **Hongguo2 intro VI + dropdown đọc được** (~06:05). Backup `…_hongguo2-intro-dropdown\`. Detail dịch intro qua translate-titles; CSS select option dark (hết chữ trắng trên trắng). Fix `docs/fixes/2026-11-08-hongguo2-intro-dropdown.md`. Sync V4/V5. **Hard refresh** (không restart).

- **Hongguo2 Browse chỉ 20 / No results · feed** (~06:00–06:10). Backup `…_hongguo2-browse-pagesize\`. `feed(limit)` gom trang; follow-up `_rpc_mod` hot-reload giữ `_proc` (hết TypeError limit → empty). Fix `docs/fixes/2026-11-08-hongguo2-browse-pagesize.md`. Sync V4/V5. **Hard refresh** (không bắt buộc restart).

- **Dịch dừng → nhảy TTS dở** (~05:40). Backup `…_translate-partial-tts-jump\`. Salvage dịch ghi đủ khung ASR; `translate_ready_for_tts` / coverage ≥90%; `_auto_gpu`+`_do_tts` không TTS khi script ngắn hơn ASR. Heal job `2cd10c3fa86d_p01` `n_total` 398→2616. Fix `docs/fixes/2026-11-08-translate-partial-tts-jump.md`. Sync V4/V5. **Restart :8801**.

- **Hongguo2 title VI** (~05:30). Backup `…_hongguo2-title-vi\` + zip `…_0528.zip`. `applyTitleVi` / `.tvi` + detail `#dTitleVi` gọi `POST /api/hg/translate-titles` sau Browse/Search/Rank/New/Library. Fix `docs/fixes/2026-11-08-hongguo2-title-vi.md`. Sync V2/V4/V5 + `static/ui`. **Hard refresh** (không restart — HTML static).

- **REVIEW local → qwen36-turbo** (~05:30). `REVIEW_PRESET=qwen36-turbo` (Huihui Qwen3.6 35B TurboQuant v0.4); dịch vẫn `gemma4-12b-qat-mtp-fast`. Job `2cd10c3fa86d_p01` (4–Phần 1/2) dừng vì **vieneu exit 15** @64/398 + claim `__all__` stale — resume TTS. **Không restart** (config/translate hot).

- **Ranking max 100 + route Film/Studio** (~05:15). Backup `…_rank-max100-routes\`. `rank.page`+`rank.more` gom ≤100; UI size=100; `/films|/film|/films/ui` → films_ui; `/studio` → index3; sidebar link. Follow-up `docs/fixes/2026-11-08-hongguo2-rank-new.md`. **Restart :8801** (đã). Hard refresh.

- **Hongguo2 Library = WinUI** (~05:00). Backup `…_library-winui\`. Update info / Select / Open folder; chips All downloads / New seasons / Lib path; card badge+hover Folder/Play + `N eps · size`; `POST /api/hg/library/update-info`. Fix `docs/fixes/2026-11-08-hongguo2-library-winui.md`. Sync + **restart :8801**. Hard refresh.

- **Hongguo settings merge+delete mảnh** (~04:55). `settings.update` `merge=true`, `deleteAfterMerge=true` (giống cũ: merge xong xóa episode lẻ). UI default Delete-after-merge = on. **Không restart.** Hard refresh Settings thấy toggle ON.

- **Hongguo2 Downloads sai tên** (~04:50). Backup `…_dl-title-folder\`. Snapshot `title=""` → hiện seriesId. Normalize lấy tên folder (+ series.detail); UI ưu tiên folder. Follow-up `docs/fixes/2026-11-08-hongguo2-downloads-winui.md`. **Restart :8801** (đã) + hard refresh.

- **Hongguo2 Settings Change folder** (~04:45). Backup `…_settings-pick-folder\`. Nút Change dùng `POST /api/fs/pick-dir` (dialog Windows) thay `prompt`. Follow-up trong `docs/fixes/2026-11-08-hongguo2-settings-winui.md`. **Hard refresh** (không cần restart).

- **Hongguo2 Settings = WinUI + license prove** (~04:40). Backup zip `…_0435.zip` + `…_settings-winui\`. UI Downloads/Output (save/quality/at-once/connections/file names/merge toggles); `POST /api/hg/settings` → `settings.update`; License block + auto-prove khi mở Settings / trước download. Fix `docs/fixes/2026-11-08-hongguo2-settings-winui.md`. Sync + **restart :8801**. Hard refresh `/hongguo2`.

- **Helper singleton + WinUI parity (giữ spawn riêng)** (~04:30). Backup zip `…_0428.zip` + `…_helper-singleton\`. Sau attach FAIL: không chung pipe WinUI. Siết 1 MainKt Pineline (`HG_HELPER_SINGLETON`, reap orphan mỗi ensure, không reload RPC, tele bỏ reload bridge). `/api/hg/settings` + hongguo2 boot quality/`D:\Lib`. Fix `docs/fixes/2026-11-08-helper-singleton-winui-parity.md`. Sync V2/V4/V5 + `static/ui`. **Restart :8801** (đã). Hard refresh `/hongguo2`.

- **Hongguo2 Downloads = WinUI** (~03:00). Backup `…_downloads-winui\`. List thumb/quality/Done line/Open folder/×; tabs All/Active/Done/Failed; Clear finished + speed. RPC clear/remove + open_folder. Fix `docs/fixes/2026-11-08-hongguo2-downloads-winui.md`. Sync + restart :8801. **Hard refresh** (cả `/static/ui/`).

- **Hongguo2 Ranking/New = WinUI** (~02:45). Backup `…_rank-new-winui\`. Ranking: `rank.page` charts/boards (8 tab EN + chip động). New: `feed` `online_time=days_N` + sort. Fix `docs/fixes/2026-11-08-hongguo2-rank-new.md`. Sync V2/V4/V5 + `static/ui`. **Restart :8801** + hard refresh.

- **Hongguo2 static/ui stale** (~02:35). User còn mở `/static/ui/hongguo2.html` (3 dropdown cũ). Chép đè root `hongguo2.html` → `static/ui/`. **Hard refresh** URL static hoặc dùng `/hongguo2`.

- **Hongguo2 Browse = WinUI 7 facets** (~02:35). Backup zip `…_0229.zip` + `…_browse-feed-facets\`. Đọc screenshot + `feed.page?panel` + `FilterText` DLL. UI 7 dropdown (All genres…Any time); `select` map RPC; `hongguo_feed_labels.json` ZH→EN. Routes `/api/hg/feed` nhận facet query. Fix `docs/fixes/2026-11-08-hongguo2-browse-facets.md`. Sync V2/V4/V5. **Restart :8801** + hard refresh `/hongguo2`.

- **Hongguo2 Browse filters → feed/catalog** (~02:10). Backup `…_hg2-browse-filters\`. Bỏ toast «map API khi có catalog». Filter Genre/Sort/Status: `board=browse` → RPC `feed.page`; `catalog_*` → Explorer (fallback rank + alias ZH/EN). Routes `/api/hg/genres|catalog|feed` (sau reload :8801). **Hard refresh `/hongguo2`**.

- **Hongguo2 Download all seasons (2.x dialog)** (~01:55). Backup `…_hg2-download-all-seasons\`. Dialog chi tiết: S1…Sn, quality, episode grid, **Download all N seasons** → `POST /api/hg/submit` multi-id. RPC `series.seasons`/`qualities`; `lookup_series` đính kèm; submit +`quality`. Routes `/series/{id}/seasons|qualities` (cần reload :8801 để đăng ký; payload seasons đã có qua detail). Sync V2/V4/V5. **Hard refresh `/hongguo2`**.

- **Hongguo2 img 422/403 + restart :8802** (~01:45). Backup `…_hg-img-u-param\`. `/api/hg/img` nhận `?u=` lẫn `?url=`; `fetch_img_proxy` dùng RPC `covers.get` (CDN fqnovel 403 khi fetch thẳng). UI hongguo2 → `?url=`. Restart sidecar PID mới; clear state upload part `p02`. **Hard refresh `/hongguo2`**. :8801 không restart (bridge reload mỗi request).

- **Hongguo2 design match WinUI + skip split-part upload** (~01:40). Backup `…_hongguo2-design-part-upload\`. `hongguo2.html` gần app 2.x (logo, filters, rank pills trắng, disk/Yearly Unlimited, theme). `auto_publisher.is_auto_split_part` chặn enqueue/publish `…_pNN` / `Phần N/N`; purge queue (`ad50b61b4050_p02`). Fix `docs/fixes/2026-11-08-skip-split-part-upload.md`. Sync V2/V4/V5. **Hard refresh `/hongguo2`**. **Restart :8802 khi idle** để nạp `auto_publisher` (sidecar); :8801 không bắt buộc (HTML static).

## 2026-11-07

- **Hongguo2 UI 2.x skin (option B)** (~22:45). Backup `…_hongguo2-ui-2x\`. Revive `/hongguo2` → `hongguo2.html` (sidebar Browse/Ranking/New/Link/Downloads/Library + Settings license). Wire `/api/hg/*` + `/api/hg/license/*`; hot-path `@@license@@status|store|prove|clear` trong `hongguo_bridge` search/resolve (process chưa reload route). Sync V2/V4/V5 + `static/ui/hongguo2.html`. DECISIONS revive B. **Restart :8801** (đã hẹn `--after-current`) để `/hongguo2` hết 302; tạm: `/static/ui/hongguo2.html`.

- **Hongguo 2.x UI plan (docs)** (~21:56). Spec `docs/superpowers/specs/2026-11-07-hongguo-2x-ui-plan.md` — screens↔`/api/hg/*`, license UX (no key echo), download gates, portability, P0/P1/P2; khuyến nghị extend `/hongguo` (không revive skin trừ khi user chọn). **Không restart.**

- **Hongguo 2.x license prove (download unlock)** (~21:45). Backup `…_hg-license-prove\`. Key DPAPI `%LOCALAPPDATA%\Pineline\hg_typed_key.dpapi` (không log). `hongguo_license_ensure.ensure_licensed` + HTTP proof bridge → `Hongguo.Licensing` Activate → `license.prove` cùng helper `hongguo_rpc`. Hook `submit` / `library_download_new_seasons`. Host `%TEMP%\HgLicActivate_patch\HgLicActivate.exe`. Review cập nhật. Sync V2/V4/V5. **Restart :8801** (hoặc reload `/api/hg/*`).

- **Hotfix mux `No module named 'core'`** (~21:18). Sync nhầm V5 `engines/render` → V2 flat `render.py`. Khôi phục V2/V4 từ bak `…_mux-heal-hstrack\V2_render.py`. Follow-up `docs/fixes/2026-11-07-mux-heal-hardsub-ocr.md`. **Không restart** (reload render mỗi mux). Remux `ad50b61b4050_p01`.

- **Hongguo 2.x JSON-RPC bridge** (~21:10). Backup zip `…_2107.zip` + `…_hongguo-rpc\`. Thêm `hongguo_rpc.py` (stdio helper.jar); `hongguo_bridge` `HG_BACKEND=rpc|http|auto` map search/rank/library/status/submit/… → RPC, giữ shape `/api/hg/*`. Spec `docs/superpowers/specs/2026-11-07-hongguo-rpc-bridge-design.md`. Sync V2/V4/V5. **Restart :8801** để nạp module (reload importlib khi gọi `/api/hg/*` cũng được nếu bridge reload).

- **Heal mux giả «Sẵn sàng» lúc OCR hardsub** (~18:20). Backup zip `…_1817.zip` + `…_mux-heal-hstrack\`. `_job_lineage_busy` (parent auto-split) + bỏ heal khi còn `_hstrack`; phase/`cur_text` hardsub trước encode. Fix `docs/fixes/2026-11-07-mux-heal-hardsub-ocr.md`. Sync V2/V4/V5. **Không restart :8801** (P3 đang `encode×3`) — nạp heal khi idle (cùng đợt hardsub_blur).

- **Concat chỉ encode phần lệch resolution** (~04:13). Backup zip `…_0413.zip` + `…_concat-partial-norm\`. `_concat_videos_smart` fallback: khớp W×H → `-c:v copy`; lệch → scale+pad. Mode `normalized_canvas_partial`. Fix `docs/fixes/2026-11-07-concat-partial-norm.md`. Sync V4/V5. **Không restart** (feeder reload theo request; job gộp đang chạy vẫn logic cũ).

- **Kênh Test exhausted che token Kênh 3** (~02:52). Backup zip `…_0251.zip` + `…_tc-exhausted-hint\`. `get_available_service` fallback project còn cờ exhausted khi auth phía còn quota fail; refresh sớm; xóa live `exhausted.json`. Fix `docs/fixes/2026-11-07-test-channel-exhausted-mask.md`. Sync V2→V4/V5. **Không restart** (:8802 reload module).

- **Kênh Test Đổi kênh poll giả** (~02:40). Backup `…_tc-doi-kenh-poll\`. Poll chờ `connected_at` mới; OAuth `replace_identity`; bỏ ghi đè CHANNEL từ pool count. Fix `docs/fixes/2026-11-07-test-channel-doi-kenh.md`. **Hard refresh Films** (tele reload `test_channel`).

- **Restart sidecar :8802** (~01:40). User yes. PID 35972→**28936**. Nạp preserve_order + oversized/skip Python. Smoke: `/config`, `/api/uploader/status`, `/api/settings` OK. **Không đụng :8801.**

- **Uploader Skip UX + oversized guard** (~01:15). Backup zip `…_0109.zip` + codebak `…_skip-upload-ux\`. Sticky `#up-skip-banner` + header Skip + Done/batch Skip; poll status 4s; `queue||items`; enqueue/auto-publish refuse >11.5h / ≥64GiB trừ confirm. Sync V4/V5 UI + `agents/auto_publisher`. Fix `docs/fixes/2026-11-07-uploader-skip-ux.md`. **Hard refresh Films**. **Không restart :8802** (auto-pub stage còn uploading / chưa idle) — restart khi idle để nạp Python API.

- **Combine part-order harden** (~01:25). Backup zip `…_0108.zip` + `…_combine-part-order\`. CN `第N季/集`, missing→0, secondary `created_at`/`job_id`, numbered ↑↓ + `preserve_order`/`explicit_order`. Sync V4/V5. Follow-up `docs/fixes/2026-11-07-combine-part-order.md`. **Hard refresh Films**. Sort-by-part: feeder reload (không cần :8801). **Hỏi restart :8802** nếu cần ↑↓ preserve_order trên process tele_cmd cũ.

- **Combine sort Phần 1→N** (~01:20). Backup `…_combine-part-order\`. Modal/API không nối theo thứ tự tick; cảnh báo >11.5h; Skip đang upload trên batch Done. Fix `docs/fixes/2026-11-07-combine-part-order.md`. **Hard refresh Films** (feeder reload mỗi POST).

- **SAFE autofix hardsub_blur UI/as_bool** (~00:55). Backup `…_hardsub-blur-safefix2\`. `films_ui` loadSettings coerce `"false"`; `index3` autoPrefApply + runOptsSummary; `run_all`/`mux_job` → `as_bool`; tests 22 OK. Sync V4/V5 + `static/ui`. Follow-up `docs/fixes/2026-11-07-hardsub-blur-toggle.md`. **Hard refresh UI**. **Không restart** (:8801 vẫn cần restart idle để nạp field).

- **hardsub_blur recheck P1** (~01:15). Backup `…_hardsub-blur-p1\`. Queue stamp `as_bool`; V5 `core/batch_config` + `engines/render` parity; log `hardsub=off`. Follow-up fix log. **Restart :8801 khi idle** (P0 live schema).

- **hardsub_blur coerce P0** (~01:10). Backup `…_hardsub-blur-coerce\`. `batch_config.as_bool`; `_queue_run_one`/`_auto_pipeline` + `render.py` queue_opts không còn `bool("false")`; Films load `/config` trước early-return. Tests ≥21. Sync V4/V5. Follow-up `docs/fixes/2026-11-07-hardsub-blur-toggle.md`. **Restart :8801 khi idle**.

- **SAFE autofix hardsub_blur stale V5 UI** (~00:50). Backup `…_hardsub-blur-autofix\`. Sync `static/ui/index3.html`+`films_ui.html` (live V5) ← root; null-guards settings/`queueBatchPush`; V2→V4→V5. Follow-up `docs/fixes/2026-11-07-hardsub-blur-toggle.md`. **Hard refresh V5 UI**. **Restart :8801 khi idle** (OpenAPI live chưa có MuxReq.hardsub_blur). :8802 không cần.

- **UI audit hardsub/combine SAFE** (~01:00). Backup `…_hardsub-blur-toggle\`. `index3.html`: `mux-hs-blur` sync từ `auto-hs-blur`. `films_ui.html`: bỏ `doCopyGptPrompt` trùng. Route `/films/mergeable` OK. Sync V4/V5. Follow-up `docs/fixes/2026-11-07-hardsub-blur-toggle.md`. **Hard refresh UI3/Films** (không restart).

- **hardsub_blur on/off** (~00:55). `MuxReq.hardsub_blur` + `mux_job` truyền `_do_render`; UI3 `auto-hs-blur`/`mux-hs-blur`; Films Settings tab Render → `/config`. Test `tests/test_hardsub_blur_toggle.py`. Swarm check/test/autofix. Fix `docs/fixes/2026-11-07-hardsub-blur-toggle.md`. **Restart :8801** khi idle để nạp MuxReq. Hard refresh UI3/Films.

- **Films UI gộp job đã làm** (~00:50). API `/films/combine` đã có nhưng thiếu nút. Batch **🔗 Gộp job đã làm** + modal; `films_merge_api` mergeable/merge-parts; lib tick `need_merge` + ghép hàng loạt. Fix `docs/fixes/2026-11-07-films-combine-ui.md`. **Sidecar :8802 restarted** (PID 35972). Hard refresh Films UI.

- **Port Settings+Uploader → :8802 + skip upload** (~00:40). Backup zip `…_0034.zip` + codebak `…_uploader-settings-8802\`. Module `uploader_settings_api.py`; wire `agent_tele_cmd` GET/POST; Films UI skip-current / skip-item / move / priority / auto-launch / clear-skipped; `yt_uploader` đọc `skip_current.flag`. Sync V4/V5 (+ V5 FastAPI bridge skip). Fix `docs/fixes/2026-11-07-uploader-settings-8802.md`. **Đã restart sidecar :8802** (PID 16628). Hard refresh Films UI.

- **Films UI jq onclick leftovers** (~00:10). Backup `Z:\PinelineV2_codebak\2026-11-07_films-ui-syntax\` + zip `…_0006.zip`. `films_ui.html`: thay `'${…}'`/`'${esc(…)}'` còn sót bằng `${jq(…)}` (OAuth id, job_id, titles, hooks; merge names → `JSON.parse(${jq(JSON.stringify(…))})`). jq 27→37; leftover unsafe string-ish=0. Sync V4/V5 + `static/ui`. Fix `docs/fixes/2026-11-07-films-ui-syntax.md`. **Hard refresh Films UI** (không restart).

## 2026-11-07

- **Tool loop pipeline** (~00:30). `agent_tool_loop.py` + `pineline_run_stage_wait` / `pineline_pipeline_loop`. CLI HTTP smoke. Tests 4 passed. Review `docs/reviews/2026-11-07-tool-loop.md`. **Restart :8801** khi idle.

- **Films UI jq HTML-escape + swarm** (~00:05). Backup `…_films-ui-jq-html\`. `jq` stringify + `&quot;` (onclick không còn cắt attribute); autopub load flat config; Settings/Uploader toast 404 rõ. Sync V4/V5. Fix `docs/fixes/2026-11-07-films-ui-syntax.md` · review `docs/reviews/2026-11-07-films-ui-swarm.md`. **Hard refresh `/films/ui`** (không restart). Còn mở: port `/api/settings` + `/api/uploader` vào :8802.

## 2026-11-06

- **Eng-swarm translate force** (~23:55). Báo cáo `docs/reviews/2026-11-06-v5-eng-swarm-translate-force.md`. Early-stop worker → translate `pending` (tránh ghost running). V5 đã `force=bool(force)` + 4 unit tests. **Cần restart :8801**.

- **Translate force-wipe mặc định** (~22:25). Backup `…_translate-force-default\` + restore `…_restore-script-88\`. `_translate_flow` hardcode `force=True` → mọi `/translate` xoá script; user thấy nhảy về «dịch lại từ đầu» lúc chuẩn bị TTS. Thêm `TranslateReq.force` (default false); UI «Dịch lại» gửi `force:true`. Khôi phục `88d80ba0be0f` từ `script.display.json` (4334/4342). Sync V4/V5. Fix `docs/fixes/2026-11-06-translate-force-wipe.md`. **Cần restart :8801**.

- **Translate stop dual-path + retranslate live** (~21:25). Backup `Z:\PinelineV2_codebak\2026-11-06_clear-stop-dual\`. Restart :8801 + force translate `88d80ba0be0f` (user «có»); live `script.json` + progress tăng, không ghost `.stop`. Harden `_clear_stop` (WORK_ROOT + `D:\PinelineV2_work`) + `_run_translate` clear trước flow. Sync V4/V5. Follow-up `docs/fixes/2026-11-06-translate-stop-ghost.md`. **Cần restart :8801 sau khi job 88d8 dịch xong** để nạp harden (đang chạy process cũ vẫn clear_stop một path — đủ vì junction).

- **Hongguo2 seasons banner + Ops tabs** (~16:30). Backup `Z:\PinelineV2_codebak\2026-11-06_hongguo2-layout2\`. Bỏ clip `max-height:72px`; Mùa mới full-width banner; Ops `Thư viện|Hàng đợi`; progress VN + card khi Update all. Sync V4/V5. Fix `docs/fixes/2026-11-06-hongguo2-seasons-layout.md`. **Hard refresh `/hongguo2`** (không restart).

- **Pronoun-QA slim plan (Aurora 413)** (~15:30). Backup `Z:\PinelineV2_codebak\2026-11-06_pronoun-qa-slim\`. `translate._plan_block_for_qa` (genre+style+pronouns only); `pronoun_consistency` + `agent_pronoun_pass` dùng slim; `llm._chatgpt_chat` no-retry 400/413/422. Đo `4041_p02`: full 72424 → slim 20119. Test `tests/test_pronoun_qa_slim_plan.py`. Sync V4/V5. Fix `docs/fixes/2026-11-06-pronoun-qa-413-slim.md`. **Cần restart :8801** (translate/llm/pronoun) khi queue idle — chưa restart (job `4041` đang ASR/translate).

- **Hongguo2 Ops hẹp** (~15:16). Backup `Z:\PinelineV2_codebak\2026-11-06_hongguo2-ops-narrow\`. CSS: Discover `1fr` | Ops `minmax(280px, min(34vw, 380px))`; seasons max ~120px; ops padding 6×10. Sync V4/V5. **Hard refresh `/hongguo2`** (không restart).

- **Hongguo2 review pass** (~08:30). Backup `Z:\PinelineV2_codebak\2026-11-06_hongguo2-review\`. CTA `doDownload` enqueue-only; submit chỉ `startDlQueue`/`dlGroup`/`dlDetail*`; `#results` scope; `catalog-hint`/`cta-status`; inflight guards; UX ops/labels; sync V4/V5. Fix `docs/fixes/2026-11-06-hongguo2-review.md`. **Hard refresh `/hongguo2`** (không restart).

- **Hongguo2 redesign** (~08:20). Backup `Z:\PinelineV2_codebak\2026-11-06_0818_hongguo2\`. Thêm `hongguo2.html` (IA 2 cột Discover 55% | Ops 45%: Tìm/Hot/Catalog + seasons/library/queues; không floating-q-bar). Route `GET /hongguo2` → `ui_hongguo2` trong `routes_ui.py` + re-export `server.py`. Link «Thử Hongguo2» trên `hongguo.html`. Sync V4/V5. **Restart :8801** để nạp route; hard refresh `/hongguo2`.

- **Hongguo New seasons board** (~08:00). Backup `Z:\PinelineV2_codebak\2026-11-06_hg-new-seasons\`. Bridge `submit(scores=)` + `library_update`/`seasons_decline`; routes `/api/hg/library/update` + `/seasons/decline`; `HgSubmitIn.scores`; UI tab 🆕 Mùa mới trên `hongguo.html`. Port V4/V5. Fix `docs/fixes/2026-11-06-hg-new-seasons.md`. **Hard refresh `/hongguo`**; **restart :8801** nếu cần nạp bridge/routes (HTML static không cần).

- **Merge no-dup output** (~03:00). Backup `Z:\PinelineV2_codebak\2026-11-06_merge-no-dup-output\`. `merge_job_parts`: ghi 1 lần `output.mp4`; `output_full` chỉ hardlink (`_hardlink_alias`, không `copy2`); cleanup `_split_parts`. Port V4/V5. Fix `docs/fixes/2026-11-06-merge-no-dup-output.md`. **Restart :8801** để nạp merge mới (job đã merge không cần remux).

## 2026-11-05

- **Split part sai giọng** (~21:40). Backup `…_split-voice-queue-opts\`. `_resolve_voice/speed/engine` đọc `queue_opts` trước fallback list[0]; `split_job_to_subjobs` seed `stages.tts`+`tts_config`. Port V4/V5. Fix `docs/fixes/2026-11-05-split-voice-queue-opts.md`. **Restart :8801/:8804/:8805**.

- **Stop heal mux merged** (~21:25). `_stop_job`: parent đã merge+Full → mux done 100% (không pending/80%); stop part heal parent. Heal tay `d01dbbc2d703` → overall 100. Follow-up fix `autosplit-conflict-guards`. **Restart** để nạp stop mới.

- **Auto-split conflict guards** (~21:20). Backup `Z:\PinelineV2_codebak\2026-11-05_autosplit-conflict-guards\`. `server.py`: merged+Full → skip; `_AUTO_SPLIT_ACTIVE` lock; skip part mux-done; promote cùng ASR nguồn → không invalidate TTS. Port V4/V5 (`_auto_gpu` + `maybe_auto_split_job`). Fix `docs/fixes/2026-11-05-autosplit-conflict-guards.md`. **Restart :8801/:8804/:8805** để nạp (không restart lúc encode nếu user chưa cho).

- **Split ENOSPC guard** (~01:20). Backup `Z:\PinelineV2_codebak\2026-11-05_split-enospc\`. `split_parts.py`: check free trước split; ENOSPC → `DiskFullError` **không** re-encode; fail mid-way xoá `_split_parts`; sub-job ưu tiên `move`. Test `tests/test_split_enospc_guard.py` (3 passed). Fix `docs/fixes/2026-11-05-split-enospc-guard.md`. **Restart :8801 sau** khi job `d01dbbc2d703` xong (không restart lúc đang chạy).

- **UI3 404/stages null-safe** (~01:09). Backup `Z:\PinelineV2_codebak\2026-11-05_ui3-404-stages\`. Sync từ V5: `renderDetail` guard `!j.job_id||!j.stages`; `refresh` check `detRes.ok`, clear selection + strip `?job=`. Fix `docs/fixes/2026-11-05-ui3-404-stages.md`. **Không restart** (hard refresh HTML).

- **Upload limit stop-queue** (~00:43). Backup `Z:\PinelineV2_codebak\2026-11-05_upload-limit-stop\`. `auto_publisher`: `_is_yt_upload_limit_error`; `stop_queue`/`upload_limit_exceeded` từ `_publish_job_internal`; `publish_job` finally không dequeue/drain khi limit; drain loop break. Test `tests/test_upload_limit_stop.py`. Fix `docs/fixes/2026-11-05-upload-limit-stop-queue.md`. Port V5 `agents/auto_publisher.py`. **Không restart**.

## 2026-11-04

- **Queue sort/move** (16:57). Backup `Z:\PinelineV2_codebak\2026-11-04_queue-sort-move\`. UI gọi `/api/queue/jobs/sort|move`; season ưu tiên «Phần N» trên title; `job_sort_key` dùng `group_id`/series normalize. Sync V2/V4/V5 (`job_queue.py` + `index3.html`). Fix `docs/fixes/2026-11-04-queue-sort-move.md`. **Restart :8801 done 17:11** (PID 35380; hard refresh UI vẫn nên).

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



