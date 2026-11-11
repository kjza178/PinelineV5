# `core.config`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `core/config.py` · **Lớp:** `core` · **201 dòng** (158 code) · **9 hàm**, **0 class** · sha1 `8825d06233`

> config.py — Cấu hình/đường dẫn PORTABLE cho Pineline. Thứ tự ưu tiên khi lấy 1 giá trị: biến môi trường  >  pineline.config.json  >  mặc định. install.py sẽ ghi pineline.config.json với đường dẫn thật của máy (venv, HF c

### Phụ thuộc

- **Gọi tới (import nội bộ):** —
- **Được dùng bởi:** [agents.agent_core](./agents.agent_core.md), [agents.agent_hongguo](./agents.agent_hongguo.md), [agents.agent_name_pass](./agents.agent_name_pass.md), [agents.agent_pronoun_pass](./agents.agent_pronoun_pass.md), [agents.agent_watch](./agents.agent_watch.md), [agents.hongguo_bridge](./agents.hongguo_bridge.md), [engines.asr.firered_asr](./engines.asr.firered_asr.md), [engines.clone_tts](./engines.clone_tts.md), [engines.download](./engines.download.md), [engines.llm](./engines.llm.md), [engines.render](./engines.render.md), [engines.render_fx](./engines.render_fx.md), [engines.sfx_lib](./engines.sfx_lib.md), [engines.subs](./engines.subs.md), [hongguo_bridge](./hongguo_bridge.md), [http_routes.routes_uploader_settings](./http_routes.routes_uploader_settings.md), [render](./render.md), [scripts.check_batch2](./scripts.check_batch2.md), [scripts.check_batch3](./scripts.check_batch3.md)
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [config](./config.md), [restart_server](./restart_server.md), [scripts._tmp_extract_sigs_batch2](./scripts._tmp_extract_sigs_batch2.md), [scripts.brain_build](./scripts.brain_build.md)
- **Test:** `tests/test_chatgpt_route.py`, `tests/test_layout_paths.py`

```mermaid
flowchart LR
  core_config[[core.config]]
  agents_agent_core[agents.agent_core] --> core_config
  agents_agent_hongguo[agents.agent_hongguo] --> core_config
  agents_agent_name_pass[agents.agent_name_pass] --> core_config
  agents_agent_pronoun_pass[agents.agent_pronoun_pass] --> core_config
  agents_agent_watch[agents.agent_watch] --> core_config
  agents_hongguo_bridge[agents.hongguo_bridge] --> core_config
  engines_asr_firered_asr[engines.asr.firered_asr] --> core_config
  engines_clone_tts[engines.clone_tts] --> core_config
  engines_download[engines.download] --> core_config
  engines_llm[engines.llm] --> core_config
  engines_render[engines.render] --> core_config
  engines_render_fx[engines.render_fx] --> core_config
  engines_sfx_lib[engines.sfx_lib] --> core_config
  engines_subs[engines.subs] --> core_config
  hongguo_bridge[hongguo_bridge] --> core_config
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_load_cfg` | 20 | 19 | `force` | Nạp lại pineline.config.json khi file đổi (tránh setdefault env khóa giá trị cũ). |
| `save_config` | 44 | 13 | `updates` | Cập nhật pineline.config.json an toàn + đồng bộ runtime. |
| `_from_file_keys` | 85 | 2 | `` |  |
| `inject_env` | 89 | 24 | `` | Chép pineline.config.json (rồi config.json) vào os.environ để tiến trình con kế thừa. |
| `get` | 115 | 23 | `key, default` | env var  >  config.json  >  default. |
| `llm_settings` | 140 | 13 | `` | LLM cho job (dịch/review) — đọc lúc gọi để sửa pineline.config.json có hiệu lực không cần restart. |
| `pass_llm_model` | 155 | 15 | `kind` | Model cho pass ngắn (name/pronoun). Ưu tiên NAME_MODEL/PRONOUN_MODEL → CHATGPT_* → REVIEW → LLM. |
| `agent_llm` | 172 | 11 | `` | LLM cho agent chat / feeder: AGENT_* rồi LLM_* (cả hai file trước env). |
| `venv_python` | 185 | 4 | `venv_dir` | Đường dẫn python trong venv, đúng theo OS. |

### Config / env keys (2)

`HF_HUB_DISABLE_SYMLINKS`, `HF_HUB_DISABLE_SYMLINKS_WARNING`

**Cổng nhắc tới:** 8083

**File/artifact nhắc tới:** `config.json`, `pineline.config.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=2 · file_writes=1 · global_stmt=1

### Lịch sử (từ docs/)

- **Fix logs (3):**
  - [2026-10-06 — Đợt 6 review: bảo trì (git, pytest, M3, dọn script chết)](../../fixes/2026-10-06-batch6-maintenance.md)
  - [2026-10-06 — Đợt 3 review: opts một nguồn, config file-first, ghi nguyên tử](../../fixes/2026-10-06-batch3-single-source.md)
  - [2026-10-06 — Đợt 2 review: bảo mật + config một nguồn + LLM sập không để trống câu](../../fixes/2026-10-06-batch2-security.md)
- **Reviews:** [_atoms_core_server](../../reviews/_atoms_core_server.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
- Nhắc trong CHANGELOG: **4** lần · DECISIONS: **1** lần

<!-- AUTO:END -->

<!-- MANUAL:START -->
> ⚠️ Chép từ thẻ V2 ngày 2026-11-11 — **chưa xác minh với bản `core/` của V5** (có thể cũ hơn root/V2). brain-keeper cần soát lại.

## Vai trò (viết tay)

Nguồn cấu hình portable: đường dẫn máy, venv, model, key LLM. Đọc `pineline.config.json` (secret — **không commit, không in**) + env + default. Tự nạp lại file khi mtime đổi (`_load_cfg`).

## Luồng chính

- `get(key, default)` — hàm mọi module dùng (thường alias `cfg`, `_cfg_get`, `_get`…). Danh sách key + nơi đọc: `generated/config-keys.md`.
- `inject_env()` — đẩy giá trị file vào env cho subprocess.
- `llm_settings()`, `pass_llm_model(kind)`, `agent_llm()` — gói cấu hình LLM theo vai.
- `venv_python(venv_dir)` — đường python của venv engine.

## Bất biến & hợp đồng — thứ tự ưu tiên

| Nhóm key | Thắng |
|---|---|
| `LLM_FILE_FIRST_KEYS` (LLM_*, TRANSLATE/REVIEW/NAME/PRONOUN_MODEL, CHATGPT_*, AURORA_*, REVIEW_PARALLEL*, REVIEW_BACKUP, REVIEW_PASS1_*…), `AGENT_FILE_FIRST_KEYS`, `RENDER_ENCODER/DUB_VOL/BGM_VOL`, tiền tố `SUB_`, `HARDSUB_` | **file** > env > default — sửa file có hiệu lực ngay |
| Còn lại | env (`run_v2.bat`, shell) > file > default |
| Opts job | snapshot `queue_opts` lúc xếp hàng (không thuộc config.py) |

Lý do file-first: env kế thừa từ shell khởi động server từng giữ model đã bỏ suốt phiên (comment trong `config.py`).

## Bẫy đã biết

- Module đọc key **lúc import** (hằng số module-level) sẽ không thấy thay đổi file tới khi restart — kiểm trước khi hứa "có hiệu lực ngay".
- Key mới phải thêm vào `pineline.config.example.json`; key LLM/REVIEW mới cân nhắc thêm vào `LLM_FILE_FIRST_KEYS`.
- Docs không được ghi giá trị secret — chỉ tên key.

## Ghi chú vận hành

Sửa `config.py` → restart :8801 + :8802. Sửa `pineline.config.json` → key file-first ăn ngay, key env-first cần restart với `--clean-env`.
<!-- MANUAL:END -->
