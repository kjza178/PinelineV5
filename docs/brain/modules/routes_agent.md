# `routes_agent`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `routes_agent.py` · **Lớp:** `control` · **645 dòng** (536 code) · **40 hàm**, **5 class** · sha1 `312524376f`

> AI Agent nhúng (agent_core): hook cho Runtime + /api/agent/*. Tách từ server.py (đợt 7). Chỉ được nạp từ cuối server.py (sau khi mọi hàm/model lõi đã định nghĩa): truy cập server qua `S.<tên>` để patch `server.<tên>` tro

### Phụ thuộc

- **Gọi tới (import nội bộ):** [agent_core](./agent_core.md), [agent_qa_gate](./agent_qa_gate.md), [batch_config](./batch_config.md), [server](./server.md)
- **Được dùng bởi:** [server](./server.md)
- **Test:** ❌ chưa có test import trực tiếp
- **Thư viện ngoài:** `agent_av_sync`, `agent_heal`, `agent_watch`, `assemble`, `fastapi`, `manifest`, `pydantic`

```mermaid
flowchart LR
  routes_agent[[routes_agent]]
  server[server] --> routes_agent
  routes_agent --> agent_core[agent_core]
  routes_agent --> agent_qa_gate[agent_qa_gate]
  routes_agent --> batch_config[batch_config]
  routes_agent --> server[server]
```

### API routes (16)

| Method | Path | Handler | Dòng |
|---|---|---|---:|
| POST | `/api/agent/av-sync/heal-batch` | `api_agent_av_sync_heal_batch` | 633 |
| POST | `/api/agent/av-sync/scan` | `api_agent_av_sync_scan` | 622 |
| POST | `/api/agent/chat` | `api_agent_chat` | 450 |
| POST | `/api/agent/confirm` | `api_agent_confirm` | 482 |
| POST | `/api/agent/heal-failed` | `api_agent_heal_failed` | 513 |
| GET | `/api/agent/jobs/{job_id}/av-sync` | `api_agent_av_sync` | 595 |
| POST | `/api/agent/jobs/{job_id}/av-sync-heal` | `api_agent_av_sync_heal` | 604 |
| POST | `/api/agent/jobs/{job_id}/qa-gate` | `api_agent_qa_gate` | 547 |
| POST | `/api/agent/jobs/{job_id}/reset-state` | `api_agent_reset_state` | 566 |
| GET | `/api/agent/jobs/{job_id}/review-diff` | `api_agent_review_diff` | 538 |
| GET | `/api/agent/pending` | `api_agent_pending` | 477 |
| POST | `/api/agent/resume/{job_id}` | `api_agent_resume` | 308 |
| POST | `/api/agent/review/{job_id}` | `api_agent_review` | 303 |
| GET | `/api/agent/scan-failed` | `api_agent_scan_failed` | 503 |
| GET | `/api/agent/status` | `api_agent_status` | 441 |
| POST | `/api/agent/watch-once` | `api_agent_watch_once` | 576 |

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| **class `AgentHealBatchReq`** | 491 | 0 method | |  |
| **class `AgentQaGateReq`** | 497 | 0 method | |  |
| **class `AgentResetStateReq`** | 559 | 0 method | |  |
| **class `AgentAvSyncHealReq`** | 590 | 0 method | |  |
| **class `AgentAvSyncScanReq`** | 614 | 0 method | |  |
| `_agent_get_job` | 77 | 5 | `job_id` |  |
| `_agent_queue_add` | 84 | 4 | `job_ids, opts` |  |
| `_agent_edit_line` | 90 | 9 | `job_id, i, vi, zh` |  |
| `_agent_set_hold` | 101 | 25 | `job_id, enabled` |  |
| `_agent_get_hold` | 128 | 6 | `job_id` |  |
| `_agent_run_stage` | 136 | 23 | `job_id, stage, opts` | Chạy 1 stage qua API nội bộ (vd tts sau duyệt). |
| `_agent_stop_job` | 161 | 8 | `job_id` |  |
| `_agent_tts_set_voice` | 171 | 12 | `job_id, opts` |  |
| `_agent_mux_run` | 185 | 20 | `job_id, opts` | Render lại theo đúng opts job đã chạy (queue_opts) ⊕ config batch, chỉ đè key agent truyền. |
| `_agent_asr_set_engine` | 207 | 8 | `job_id, engine` |  |
| `_job_in_pipeline` | 217 | 5 | `job_id` |  |
| `_agent_script_review` | 224 | 45 | `job_id, review_model` | Rà soát tên nhân vật + văn phong trước lồng tiếng. |
| `_agent_resume` | 271 | 29 | `job_id` | Duyệt xong → bỏ HOLD/QA block và xếp lại job lên ĐẦU hàng chờ: pipeline bỏ qua bước đã xong, |
| `api_agent_review` | 303 | 2 | `job_id, body` |  |
| `api_agent_resume` | 308 | 2 | `job_id` |  |
| `_agent_script_review_legacy` | 312 | 12 | `job_id, review_model` | Rà soát văn phong = translate API review_only (run_review). |
| `_agent_heal_stale` | 326 | 7 | `job_id` |  |
| `_agent_translate_fill` | 335 | 8 | `job_id` |  |
| `_agent_translate_rerun` | 345 | 8 | `job_id` |  |
| `_agent_tts_run_simple` | 355 | 2 | `job_id` |  |
| `_agent_mux_retry` | 359 | 2 | `job_id` |  |
| `_agent_asr_force` | 363 | 2 | `job_id` |  |
| `_agent_assemble_fit` | 367 | 6 | `job_id, max_speed` |  |
| `_agent_mux_force_av` | 375 | 8 | `job_id, audio_mode` |  |
| `_agent_reset_state` | 385 | 3 | `job_id, stages, keep_asr, restart` |  |
| `_agent_notify` | 409 | 4 | `text` |  |
| `api_agent_status` | 441 | 6 | `` | Snapshot jobs cho panel Agent (không cần LLM). |
| `api_agent_chat` | 450 | 24 | `req` | Chat với AI Agent — tools gọi hàm nội bộ (queue/manifest), không HTTP self. |
| `api_agent_pending` | 477 | 2 | `` |  |
| `api_agent_confirm` | 482 | 7 | `req` | Chạy (approve) hoặc huỷ thao tác agent đã đỗ lại chờ xác nhận. |
| `api_agent_scan_failed` | 503 | 7 | `` | Quét mọi job lỗi/kẹt (không sửa). |
| `api_agent_heal_failed` | 513 | 22 | `req` | Heal hàng loạt job lỗi. apply=false chỉ plan. |
| `api_agent_review_diff` | 538 | 6 | `job_id` |  |
| `api_agent_qa_gate` | 547 | 10 | `job_id, req` |  |
| `api_agent_reset_state` | 566 | 7 | `job_id, req` | Reset sạch trạng thái các stage bị kẹt/lỗi của job (xóa artifact dở, gỡ .stop, đưa manifest về pending). |
| `api_agent_watch_once` | 576 | 12 | `` | Chạy 1 vòng watcher ngay (scan→heal safe nếu GPU rảnh). |
| `api_agent_av_sync` | 595 | 6 | `job_id` |  |
| `api_agent_av_sync_heal` | 604 | 8 | `job_id, req` |  |
| `api_agent_av_sync_scan` | 622 | 8 | `req` |  |
| `api_agent_av_sync_heal_batch` | 633 | 13 | `req` |  |

### Config / env keys (1)

`AGENT_WATCH_MAX_JOBS`

**File/artifact nhắc tới:** `manifest.json`, `script.json`, `tts.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=24

### Lịch sử (từ docs/)

- **Fix logs (4):**
  - [Queue nhảy job khi còn HOLD/soát dở — mất invariant studio 1 job→output](../../fixes/2026-11-10-queue-park-held.md)
  - [Brain LLM tick trả tools=[] (không gọi tool)](../../fixes/2026-11-09-brain-llm-tool-loop.md)
  - [Hongguo "Merge all": không thấy đang chạy gì, 16 series rất lâu mới ra 1](../../fixes/2026-10-07-hg-merge-queue.md)
  - [Đợt 7: gỡ UI cũ, tách server.py](../../fixes/2026-10-06-batch7-ui-split.md)
- **Reviews:** [_atoms_http_agents](../../reviews/_atoms_http_agents.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
- Nhắc trong CHANGELOG: **1** lần · DECISIONS: **0** lần

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
