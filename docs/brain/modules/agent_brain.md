# `agent_brain`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `agent_brain.py` · **Lớp:** `agent` · **1221 dòng** (1090 code) · **34 hàm**, **0 class** · sha1 `ba61b4ab2c`

> Second Brain — daemon nền full-silent. Sensors → incidents → policy → actuators. Bật: AGENT_BRAIN=1 (hoặc pineline.config.json).

### Phụ thuộc

- **Gọi tới (import nội bộ):** [agent_brain_context](./agent_brain_context.md), [agent_core](./agent_core.md), [agent_hang_fix](./agent_hang_fix.md), [agent_quality](./agent_quality.md), [config](./config.md), [job_queue](./job_queue.md)
- **Được dùng bởi:** [server](./server.md)
- **Test:** ❌ chưa có test import trực tiếp
- **Thư viện ngoài:** `agent_heal`, `agent_watch`, `manifest`, `preset_switcher`

```mermaid
flowchart LR
  agent_brain[[agent_brain]]
  server[server] --> agent_brain
  agent_brain --> agent_brain_context[agent_brain_context]
  agent_brain --> agent_core[agent_core]
  agent_brain --> agent_hang_fix[agent_hang_fix]
  agent_brain --> agent_quality[agent_quality]
  agent_brain --> config[config]
  agent_brain --> job_queue[job_queue]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_cfg` | 28 | 9 | `key, default` |  |
| `_truthy` | 39 | 2 | `v` |  |
| `brain_enabled` | 43 | 6 | `` |  |
| `_interval_sec` | 51 | 5 | `` |  |
| `_tg_mode` | 58 | 2 | `` |  |
| `_log_dir` | 62 | 4 | `root` |  |
| `log_line` | 68 | 9 | `root, msg` |  |
| `_state_path` | 79 | 2 | `root` |  |
| `_load_state` | 83 | 8 | `root` |  |
| `_save_state` | 93 | 7 | `root, state` |  |
| `_cooldown_ok` | 102 | 4 | `state, fp, sec` |  |
| `_mark_fp` | 108 | 3 | `state, fp, note` |  |
| `_telegram` | 113 | 16 | `msg, level` |  |
| `_ping` | 131 | 12 | `url, timeout` |  |
| `sense_infra` | 145 | 21 | `` |  |
| `sense_jobs` | 168 | 49 | `work_root, max_jobs` | Quét job có script / failed / stale cho quality + ops hints. |
| `_qa_pipeline_phase` | 219 | 63 | `work_dir` | Perceive: job đang ở đâu — mid_review / pre_tts / post_tts / idle. |
| `_gpu_or_queue_busy` | 284 | 12 | `work_root` |  |
| `decide` | 298 | 39 | `incidents, state` | Policy full-silent → list actions. |
| `apply_actions` | 339 | 191 ⚠️ | `work_root, actions, state, hooks` |  |
| `_llm_enabled` | 532 | 7 | `` |  |
| `_llm_interval_sec` | 541 | 5 | `` |  |
| `_http_json` | 548 | 11 | `method, url, body, timeout` |  |
| `_ensure_brain_runtime` | 561 | 177 ⚠️ | `work_root` | Bind agent_core Runtime nếu chưa có — FS + HTTP proxy (không cần restart :8801). |
| `_run_agent_llm` | 740 | 71 | `message, work_root, max_steps, force_first_tool, force_first_args` | Gọi agent_core tool-loop in-process (bind FS/HTTP nếu cần) hoặc fallback HTTP chat. |
| `llm_tick` | 813 | 185 ⚠️ | `work_root` | LLM Second Brain: đọc snapshot toàn hệ → tool-loop quyết định. |
| `_tg_report_sec` | 1001 | 5 | `` |  |
| `_progress_digest` | 1008 | 72 | `work_root` | Tóm tắt ngắn running/queue cho Telegram. |
| `_maybe_tg_progress` | 1082 | 11 | `work_root, state` |  |
| `tick` | 1095 | 73 | `work_root, hooks, list_jobs` |  |
| `_loop` | 1170 | 14 | `work_root, hooks, list_jobs, interval` |  |
| `start_brain` | 1186 | 22 | `work_root, hooks, list_jobs` |  |
| `stop_brain` | 1210 | 2 | `` |  |
| `brain_once` | 1214 | 8 | `work_root, hooks, list_jobs` | API/ops: chạy 1 tick thủ công. |

**Hàm dài ≥120 dòng:** `apply_actions` (191, L339), `llm_tick` (185, L813), `_ensure_brain_runtime` (177, L561)

### Config / env keys (10)

`AGENT_BRAIN`, `AGENT_BRAIN_LLM`, `AGENT_BRAIN_LLM_SEC`, `AGENT_BRAIN_LLM_STEPS`, `AGENT_BRAIN_MODE`, `AGENT_BRAIN_SEC`, `AGENT_BRAIN_TELEGRAM`, `AGENT_BRAIN_TG_SEC`, `REVIEW_PRESET`, `TRANSLATE_PRESET`

**Cổng nhắc tới:** 3377, 8083, 8801, 8802

**File/artifact nhắc tới:** `agent_brain.log`, `agent_brain_last_snapshot.json`, `agent_brain_state.json`, `brain_pending_decisions.json`, `manifest.json`, `script.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=36 · file_writes=5 · global_stmt=1 · swallow_except=8 · threads=1

### Lịch sử (từ docs/)

- **Fix logs (1):**
  - [Brain LLM tick trả tools=[] (không gọi tool)](../../fixes/2026-11-09-brain-llm-tool-loop.md)
- Nhắc trong CHANGELOG: **1** lần · DECISIONS: **1** lần

<!-- AUTO:END -->

<!-- MANUAL:START -->
## Vai trò (viết tay)

_Chưa viết. 2–4 câu: module này chịu trách nhiệm gì trong pipeline, ai gọi nó, nó KHÔNG làm gì._

## Luồng chính

_Các hàm vào (entry) → bước chính → output/side effect. Ghi tên hàm thật._

## Bất biến & hợp đồng

_Điều luôn phải đúng (vd: chỉ ghi manifest qua `Manifest.update`; 1 job / ghế). Vi phạm = bug._

## Bẫy đã biết

_Lỗi từng gặp + link `docs/fixes/...`. Những chỗ dễ sửa sai._

## Ghi chú vận hành

_Config key quan trọng, cần restart gì khi sửa (:8801 / :8802 / hot-reload), cách test._
<!-- MANUAL:END -->
