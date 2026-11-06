# Review PinelineV4 + port cập nhật từ V2

_Date: 2026-11-02_

## 1) Thừa / thiếu / rủi ro (V4)

### Thừa / lệch nhãn
- `run_v2.bat` trong cây V4 vẫn `PORT=8801` + `D:\PinelineV2_tmp` — dễ mở nhầm instance V2-path trên code V4.
- `docs/STATE.md` vẫn tiêu đề «PinelineV2», PID/cổng 8801 cũ.
- `scratch/*`, `lib_check.py` còn path cứng `Z:\PinelineV2`.
- `src-tauri/` + `node_modules/` (Tauri CLI) song song với `app_desktop.py` (WebView2) — hai hướng desktop.
- `workflow.html` (root) vs `docs/workflow.html` — trùng vai trò.

### Thiếu (đã thấy trước khi port)
- `routes_films.py` gọi `film_db.mark_library_skipped/priority` và `enqueue_library_item` — **không tồn tại** → `/library/action` skip/priority/enqueue crash.
- `index4.html` không có file; `routes_ui` `/ui4`/`/index4.html` đã fallback về `index.html` (ổn).
- Pipeline lõi **lạc hậu V2** (Demucs chunk dài, ASR `nano_fa`/`resolve_asr_source`, hardsub ngưỡng, queue series/season, publisher queue/lock, …).

### Giữ (unique V4 — không ghi đè từ V2)
- `app_desktop.py`, `run_v4.bat`, `routes_films.py`, `routes_uploader_settings.py`
- `config.save_config` (uploader settings)
- `films_ui.html` / `index.html` bản V4 (lớn hơn; chỉ sửa poster URL)
- `routes_hg.py` bản V4 (lớn hơn)

### Rủi ro còn lại
- `restart_server.py` / `migrate_work.py` / `agent_heal.py` còn path `8801` / `D:\PinelineV2_work` — sidecar V4 (`run_tele_cmd.bat`) đã `PORT`-aware nhưng restart script chưa chuẩn hóa hết.
- `server.py` vẫn message «PinelineV2» khi trùng cổng.

## 2) Port từ V2 (đã làm)

**Copy wholesale:** `separate`, `asr`, `hybrid_asr`, `nano_fa_asr` (mới), `assemble`, `clone_tts`, `job_queue`, `render`, `render_fx`, `translate`, `llm`, `series_glossary`, `fun_asr_nano`, `asr_vad_utils`, `asr_spam`, `paraformer_zh`, `sensevoice_asr`, `batch_config`, `film_db`, `auto_publisher`, `meta_studio`, `agent_feeder`, `agent_tele_cmd`, `static/app.js`, `index3.html` + vài tests.

**Merge chọn lọc `server.py`:** thêm `nano_fa`, `queue_items`/`get_job_info`, label ASR — **giữ** `routes_films` / `routes_uploader_settings`.

**Vá V4:** `routes_films.library_action` → `agent_feeder.library_action`; `config` thêm `RENDER_*_VOL` file-first (giữ `save_config`); `agent_core` choices `nano_fa`; `films_ui` poster relative; sidecar `BASE` theo `PORT`/`PINELINE_BASE`.

## 3) Kiểm
- `py_compile` 17 module lõi OK
- `pytest tests/test_job_queue.py tests/test_render_expr.py tests/test_sfx_lib.py` → **37 passed**

## 4) Backup
- Codebak: `Z:\PinelineV2_codebak\2026-11-02_v4-port-v2\` (+ `followup\`)
- Zip (script snapshot trỏ V2): `Z:\PinelineV2_backup_2026-11-02_0209.zip`

## 5) Follow-up sau subagent review
- Port thêm `preset_switcher.py` (translate V2 gọi khi đổi preset LLM).
- Chuẩn hoá default **8804** / `PINELINE_BASE`: `agent_autopilot`, `agent_hongguo`, `agent_feeder` (detect server), `agent_heal` (+`PinelineV4_work`), `meta_studio` poster, `migrate_work`, `restart_server` (start `server.py` / `run_v4.bat`).
- Còn treo (không đụng lần này): gỡ/đổi tên `run_v2.bat`/`run.bat`/`Pineline.bat`, dual Tauri vs WebView2, Canva callback `:8802` vs routes trên `:8804`, sync `index.html`/`index3.html`.
