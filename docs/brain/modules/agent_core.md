# `agent_core`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `agent_core.py` · **Lớp:** `agent` · **2072 dòng** (1963 code) · **30 hàm**, **2 class** · sha1 `3ad725c477`

> agent_core.py — AI Agent nhúng trong Pineline V2. Không gọi HTTP self. Tools gọi runtime đã bind từ server.py (list jobs, queue, manifest, draft YT).

### Phụ thuộc

- **Gọi tới (import nội bộ):** [agent_qa_gate](./agent_qa_gate.md), [agent_tool_loop](./agent_tool_loop.md), [batch_config](./batch_config.md), [config](./config.md), [film_db](./film_db.md)
- **Được dùng bởi:** [agent_brain](./agent_brain.md), [routes_agent](./routes_agent.md)
- **Test:** ❌ chưa có test import trực tiếp
- **Thư viện ngoài:** `agent_av_sync`, `agent_heal`, `agent_hongguo`, `agent_stage_io`, `agent_watch`, `requests`

```mermaid
flowchart LR
  agent_core[[agent_core]]
  agent_brain[agent_brain] --> agent_core
  routes_agent[routes_agent] --> agent_core
  agent_core --> agent_qa_gate[agent_qa_gate]
  agent_core --> agent_tool_loop[agent_tool_loop]
  agent_core --> batch_config[batch_config]
  agent_core --> config[config]
  agent_core --> film_db[film_db]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| **class `Runtime`** | 1062 | 0 method | |  |
| **class `AgentResult`** | 1965 | 0 method | |  |
| `_films_tool` | 902 | 12 | `args` |  |
| `_sidecar_cmd` | 916 | 8 | `text` |  |
| `_truthy` | 973 | 2 | `v` |  |
| `tool_tier` | 977 | 29 | `name, args` | read / mutate / confirm. confirm = phá huỷ/tốn lâu, cần user bấm ✅ khi gọi từ Telegram. |
| `describe_action` | 1008 | 6 | `name, args` |  |
| `_prune_pending` | 1016 | 3 | `now` |  |
| `park_action` | 1021 | 13 | `name, args` | Giữ tool call lại chờ user xác nhận; trùng (name, args) chưa hết hạn thì dùng lại id cũ. |
| `pending_actions` | 1036 | 4 | `` |  |
| `confirm_action` | 1042 | 14 | `cid, approve` |  |
| `bind` | 1089 | 3 | `runtime` |  |
| `_require_rt` | 1094 | 4 | `` |  |
| `summarize_job` | 1100 | 28 | `j, work_root` |  |
| `_load_script` | 1130 | 8 | `work_root, job_id` |  |
| `_line_brief` | 1140 | 9 | `r` |  |
| `_read_hold` | 1151 | 15 | `work_root, job_id` |  |
| `script_peek` | 1168 | 20 | `work_root, job_id, sample` |  |
| `script_search` | 1190 | 25 | `work_root, job_id, query, missing_only, limit` |  |
| `script_get_lines` | 1217 | 14 | `work_root, job_id, i_from, i_to` |  |
| `classify_jobs` | 1233 | 26 | `jobs, work_root` |  |
| `default_yt_draft` | 1261 | 38 | `work_root, job_id, max_lines` |  |
| `_dispatch` | 1301 | 424 ⚠️ | `name, args, allow_mutate` |  |
| `_llm_cfg` | 1727 | 5 | `` | Cấu hình LLM cho Agent chat (có thể tách khỏi job translate) — config.agent_llm(). |
| `_chat_turn` | 1734 | 22 | `messages, use_tools, tool_choice` | Một turn OpenAI chat/completions. Trả message dict (content + tool_calls). |
| `_chat_turn_model` | 1758 | 35 | `messages, use_tools, model, tool_choice` |  |
| `_chat_turn_text_protocol` | 1795 | 67 | `messages, model` | Fallback khi model không tool-call: ép JSON {tool,args} hoặc {final}. |
| `_parse_pycall_tool_calls` | 1870 | 44 | `content` | Model hay in «Action: `hg_auto_flow(query_or_id="…", auto_run=True)`» thay vì gọi tool. |
| `_parse_text_tool_calls` | 1916 | 36 | `content` | Model qua proxy đôi khi in tool call dạng text (```json [{"name":..,"arguments":..}]```). |
| `clip_tool_result` | 1957 | 5 | `result, limit` |  |
| `run_agent` | 1972 | 96 | `message, history, allow_mutate, max_steps, require_confirm, force_f…` | Chạy agent. history = [{role, content}, ...] (user/assistant only). |
| `status_snapshot` | 2070 | 3 | `` |  |

**Hàm dài ≥120 dòng:** `_dispatch` (424, L1301)

### Config / env keys (4)

`AGENT_TOOL_RESULT_MAX`, `AGENT_WATCH_MAX_JOBS`, `AUTOPILOT_URL`, `LLM_ENABLE_THINKING`

**Cổng nhắc tới:** 8802

**File/artifact nhắc tới:** `manifest.json`, `output.mp4`, `script.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=5 · global_stmt=1 · swallow_except=1

### Lịch sử (từ docs/)

- **Fix logs (6):**
  - [Brain LLM tick trả tools=[] (không gọi tool)](../../fixes/2026-11-09-brain-llm-tool-loop.md)
  - [2026-10-06 — Đợt 5 review: agent an toàn hơn](../../fixes/2026-10-06-batch5-agent-safety.md)
  - [2026-10-06 — Đợt 4 review: tranh chấp ghi, một bản tiến trình, checkpoint an toàn](../../fixes/2026-10-06-batch4-write-races.md)
  - [2026-10-06 — Đợt 2 review: bảo mật + config một nguồn + LLM sập không để trống câu](../../fixes/2026-10-06-batch2-security.md)
  - [Agent chạy tool chỉ vì được nhắc trong câu trả lời](../../fixes/2026-10-06-agent-text-toolcall-overmatch.md)
  - [2026-09-26 — Port duck/duck_bgm two-pass sang PinelineV2](../../fixes/2026-09-26-duck-bgm-twopass-port.md)
- **Reviews:** [_atoms_http_agents](../../reviews/_atoms_http_agents.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-11-02-v4-structure-sync](../../reviews/2026-11-02-v4-structure-sync.md), [2026-11-02-v4-structure-and-v2-port](../../reviews/2026-11-02-v4-structure-and-v2-port.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
- Nhắc trong CHANGELOG: **13** lần · DECISIONS: **2** lần

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
