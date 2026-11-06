# 2026-10-06 — Đợt 3 review: opts một nguồn, config file-first, ghi nguyên tử

Review gốc: `docs/reviews/2026-10-06-code-review.md` (X1, X2, X3, S13). Một phần đợt 3 đã làm cùng đợt 2: M7/M8/M9, config agent (`config.agent_llm`), feeder dùng chung LLM, bỏ key/`LLM_*` khỏi `.bat`. Giữ `openclaw` làm fallback (quyết định 10-05).

Backup trước khi sửa:

- Zip: `Z:\PinelineV2_backup_2026-10-06_0937.zip`.
- Bản gốc từng file: `Z:\PinelineV2_codebak\2026-10-06_batch3\` — `server.py`, `batch_config.py`, `agent_autopilot.py`, `render.py`, `config.py`, `app.py`, `llm.py`, `job_queue.py`.

Test: `scripts/check_batch3.py` 35/35 (file tạm, không đụng hàng đợi/config thật). pytest 23/23. Đợt 1 ALL PASS, đợt 2 69/69.

## Triệu chứng

| Mã | Triệu chứng |
|---|---|
| X1 | Cùng một job, render ra khác nhau tuỳ đường gọi. Các nguồn mặc định khác nhau: `MuxReq`/`RunAllReq` (voice_bgm, 0.6, 8M), `_queue_run_one` (duck_bgm 0.22), `_agent_mux_run` (ép motion/lut/fit bật, 4M, tắt logo/khung, brand drift), `run_stage mux` (`_do_render` mặc định: voice_bgm, không brand). |
| X2 | Server chép file config vào env bằng `setdefault` lúc start; `config.get` đọc env trước với key thường → sửa `pineline.config.json` không có tác dụng tới khi restart. `render.py` đọc `RENDER_ENCODER` env trước. Ba bản copy vòng chép env (`server.py`, `llm.py`, `app.py`) với luật khác nhau (`app.py` để env thắng cả key LLM). |
| S13 | `batch_config.json`, `autopilot_state.json` ghi thẳng (đọc đúng lúc ghi → JSON dở); `load()` nuốt lỗi → trả DEFAULTS → Auto-pilot xếp job giọng v5/âm duck_bgm. Server và sidecar cùng đọc-sửa-ghi → mất cập nhật (vd tick Auto-pilot ghi đè lần bật/tắt). |

## Sửa

- **`fileio.py`** (mới):
  - `atomic_write_text`: temp riêng theo pid+thread, `fsync`, `os.replace`, thử lại khi Windows báo khoá.
  - `file_lock`: file `.lock` tạo O_EXCL; khoá bỏ quên quá 60 s thì gỡ.
- **`batch_config.py`**:
  - `_write` ghi nguyên tử; `update`/`reset` đọc-sửa-ghi trong `file_lock`.
  - `load()` thử 3 lần, hỏng thì trả **bản đọc tốt gần nhất** và log.
  - `resolve_job_opts(*layers, fill_voice=True)`: config batch rồi lần lượt đè bởi từng lớp, bỏ None và `pin_opts`.
  - `render_kwargs(o)`: bộ tham số `_do_render`/`MuxReq` (brand bật khi `brand` hoặc `brand_mode` ≠ off).
- **`agent_autopilot.py`**:
  - `load_state` thử 3 lần, rồi dùng bản tốt gần nhất;
  - `save_state` ghi nguyên tử;
  - `update_state(fn)` trong khoá, dùng cho `set_enabled`, ghim opts và ghi `last_tick`.
- **`server.py`**:
  - `POST /api/queue/jobs` và `/group`: `model_dump(exclude_unset=True)` + `resolve_job_opts(..., fill_voice=False)` → trường client không gửi lấy theo config batch thay vì mặc định cứng của model. UI vốn gửi đủ nên không đổi.
  - `_queue_run_one`: `resolve_job_opts(opts, fill_voice=False)` điền key thiếu.
  - `_agent_mux_run`: `resolve_job_opts(queue_opts của job, opts agent)` → render lại **đúng opts job đã chạy**, chỉ đè key agent truyền. `brand=False` → tắt watermark; `brand`/`brand_text` khi job đang off → drift (như cũ). Bỏ ép motion/lut, tắt logo/khung, 4M.
  - `run_stage(..., "mux")`: `_do_render(**render_kwargs(resolve_job_opts(queue_opts)))` thay vì mặc định voice_bgm/không brand.
  - `_agent_resume`: `resolve_job_opts(queue_opts)`.
  - Vòng chép env → `config.inject_env()`.
- **Giọng không lấy từ config batch** (`fill_voice=False`) ở hàng đợi/API: không truyền giọng → dùng giọng đã lưu của job, không có thì "chưa chọn giọng" (test `test_missing_job_voice_fails_without_global_fallback`). Lần chạy đầu của bản sửa đã điền giọng v2 cho mọi job — test bắt được, đã sửa trước khi xong đợt.
- **`config.py`**:
  - `inject_env()`: một chỗ duy nhất chép file → env. Key LLM: file đè env. Key khác: chỉ đặt khi env chưa có và ghi tên vào `PINELINE_CFG_KEYS`.
  - `get()`: key trong `PINELINE_CFG_KEYS` cũng đọc file trước → sửa file có hiệu lực ngay. Env do user đặt thật (không phải chép từ file) vẫn thắng.
- **`llm.py`, `app.py`**: dùng `config.inject_env()`; `app.py` nay để file thắng env với key LLM, giống server.
- **`render.py`** `_encoder_pref`: `config.get("RENDER_ENCODER")` (file trước). Có hiệu lực ngay lần mux tới — giá trị hiện tại không đổi vì env không đặt riêng.
- X3: `agent_v2` (ghép LLM lệch) để đợt 5 xoá; feeder/agent_core đã dùng `config.agent_llm` từ đợt 2.

## Hiệu lực

- **Ngay** (nạp lại mỗi lần mux trong server đang chạy): `render.py`, `config.py`. Đã kiểm: server cũ chưa có `PINELINE_CFG_KEYS`, file không có key `AGENT_*` → `get()` trả như cũ.
- **Sau restart server**: `server.py`, `batch_config.py`, `llm.py`, `fileio.py`.
- **Sau restart sidecar**: `agent_autopilot.py`, `batch_config.py`.

## Recheck

```powershell
cd Z:\PinelineV2
python scripts\check_batch3.py        # 35 PASS
python -m pytest -q -p no:cacheprovider tests
```
