# `http_routes.routes_agent`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `http_routes/routes_agent.py` · **Lớp:** `control` · **815 dòng** (673 code) · **47 hàm**, **7 class** · sha1 `ce5a9cf5aa`

> AI Agent nhúng (agent_core): hook cho Runtime + /api/agent/*. Tách từ server.py (đợt 7). Chỉ được nạp từ cuối server.py (sau khi mọi hàm/model lõi đã định nghĩa): truy cập server qua `S.<tên>` để patch `server.<tên>` tro

### Phụ thuộc

- **Gọi tới (import nội bộ):** [agents.agent_av_sync](./agents.agent_av_sync.md), [agents.agent_core](./agents.agent_core.md), [agents.agent_heal](./agents.agent_heal.md), [agents.agent_hold](./agents.agent_hold.md), [agents.agent_qa_ask](./agents.agent_qa_ask.md), [agents.agent_qa_gate](./agents.agent_qa_gate.md), [agents.agent_watch](./agents.agent_watch.md), [core.batch_config](./core.batch_config.md), [core.manifest](./core.manifest.md), [engines.assemble](./engines.assemble.md), [server](./server.md)
- **Được dùng bởi:** [server](./server.md)
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [restart_server](./restart_server.md)
- **Test:** `tests/test_server_split.py`
- **Thư viện ngoài:** `fastapi`, `pydantic`

```mermaid
flowchart LR
  http_routes_routes_agent[[http_routes.routes_agent]]
  server[server] --> http_routes_routes_agent
  http_routes_routes_agent --> agents_agent_av_sync[agents.agent_av_sync]
  http_routes_routes_agent --> agents_agent_core[agents.agent_core]
  http_routes_routes_agent --> agents_agent_heal[agents.agent_heal]
  http_routes_routes_agent --> agents_agent_hold[agents.agent_hold]
  http_routes_routes_agent --> agents_agent_qa_ask[agents.agent_qa_ask]
  http_routes_routes_agent --> agents_agent_qa_gate[agents.agent_qa_gate]
  http_routes_routes_agent --> agents_agent_watch[agents.agent_watch]
  http_routes_routes_agent --> core_batch_config[core.batch_config]
  http_routes_routes_agent --> core_manifest[core.manifest]
  http_routes_routes_agent --> engines_assemble[engines.assemble]
  http_routes_routes_agent --> server[server]
```

### API routes (18)

| Method | Path | Handler | Dòng |
|---|---|---|---:|
| POST | `/api/agent/av-sync/heal-batch` | `api_agent_av_sync_heal_batch` | 803 |
| POST | `/api/agent/av-sync/scan` | `api_agent_av_sync_scan` | 792 |
| POST | `/api/agent/chat` | `api_agent_chat` | 618 |
| POST | `/api/agent/confirm` | `api_agent_confirm` | 651 |
| POST | `/api/agent/heal-failed` | `api_agent_heal_failed` | 683 |
| GET | `/api/agent/jobs/{job_id}/av-sync` | `api_agent_av_sync` | 765 |
| POST | `/api/agent/jobs/{job_id}/av-sync-heal` | `api_agent_av_sync_heal` | 774 |
| POST | `/api/agent/jobs/{job_id}/qa-gate` | `api_agent_qa_gate` | 717 |
| POST | `/api/agent/jobs/{job_id}/reset-state` | `api_agent_reset_state` | 736 |
| GET | `/api/agent/jobs/{job_id}/review-diff` | `api_agent_review_diff` | 708 |
| GET | `/api/agent/pending` | `api_agent_pending` | 646 |
| POST | `/api/agent/qa-answer` | `api_agent_qa_answer` | 424 |
| POST | `/api/agent/qa-show` | `api_agent_qa_show` | 414 |
| POST | `/api/agent/resume/{job_id}` | `api_agent_resume` | 363 |
| POST | `/api/agent/review/{job_id}` | `api_agent_review` | 358 |
| GET | `/api/agent/scan-failed` | `api_agent_scan_failed` | 673 |
| GET | `/api/agent/status` | `api_agent_status` | 609 |
| POST | `/api/agent/watch-once` | `api_agent_watch_once` | 746 |

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| **class `AgentQaAnswerReq`** | 400 | 0 method | |  |
| **class `AgentQaShowReq`** | 409 | 0 method | |  |
| **class `AgentHealBatchReq`** | 661 | 0 method | |  |
| **class `AgentQaGateReq`** | 667 | 0 method | |  |
| **class `AgentResetStateReq`** | 729 | 0 method | |  |
| **class `AgentAvSyncHealReq`** | 760 | 0 method | |  |
| **class `AgentAvSyncScanReq`** | 784 | 0 method | |  |
| `_agent_get_job` | 80 | 5 | `job_id` |  |
| `_agent_queue_add` | 87 | 4 | `job_ids, opts` |  |
| `_agent_edit_line` | 93 | 9 | `job_id, i, vi, zh` |  |
| `_agent_set_hold` | 104 | 36 | `job_id, enabled` |  |
| `_agent_get_hold` | 142 | 6 | `job_id` |  |
| `_agent_run_stage` | 150 | 35 | `job_id, stage, opts` | Chạy 1 stage qua API nội bộ (vd tts sau duyệt). |
| `_agent_mark_qa_override` | 187 | 16 | `job_id` | agentI2: người chạy TTS qua Agent trên job QA-block → giữ ngữ nghĩa cũ agent.qa_override=True |
| `_agent_stop_job` | 205 | 8 | `job_id` |  |
| `_agent_tts_set_voice` | 215 | 12 | `job_id, opts` |  |
| `_agent_mux_run` | 229 | 20 | `job_id, opts` | Render lại theo đúng opts job đã chạy (queue_opts) ⊕ config batch, chỉ đè key agent truyền. |
| `_agent_asr_set_engine` | 251 | 8 | `job_id, engine` |  |
| `_job_in_pipeline` | 261 | 5 | `job_id` |  |
| `_agent_script_review` | 268 | 45 | `job_id, review_model` | Rà soát tên nhân vật + văn phong trước lồng tiếng. |
| `_agent_resume` | 315 | 40 | `job_id` | Duyệt xong → bỏ HOLD/QA block và xếp lại job lên ĐẦU hàng chờ: pipeline bỏ qua bước đã xong, |
| `api_agent_review` | 358 | 2 | `job_id, body` |  |
| `api_agent_resume` | 363 | 2 | `job_id` |  |
| `_agent_defer` | 368 | 11 | `job_id` |  |
| `_qa_release` | 381 | 17 | `job_id, deferred_ids` | Người trả lời xong câu hỏi QA → gỡ HOLD + xếp lại. Part đã gác cùng job cha → xếp lại job cha. |
| `api_agent_qa_show` | 414 | 7 | `req` | /qa <job> trên Telegram: hiện lại câu bị cờ + đề xuất + nút (tạo câu hỏi nếu chưa có). |
| `api_agent_qa_answer` | 424 | 16 | `req` | Trả lời câu hỏi HOLD QA (nút ✅/⏭/▶️ hoặc reply câu VI) → ghi script → hết cờ thì chạy tiếp. |
| `_agent_script_review_legacy` | 442 | 12 | `job_id, review_model` | Rà soát văn phong = translate API review_only (run_review). |
| `_agent_heal_stale` | 456 | 7 | `job_id` |  |
| `_agent_translate_fill` | 465 | 8 | `job_id` |  |
| `_agent_translate_rerun` | 475 | 8 | `job_id` |  |
| `_agent_tts_run_simple` | 485 | 2 | `job_id` |  |
| `_agent_mux_retry` | 489 | 2 | `job_id` |  |
| `_agent_asr_force` | 493 | 2 | `job_id` |  |
| `_agent_assemble_fit` | 497 | 6 | `job_id, max_speed` |  |
| `_agent_mux_force_av` | 505 | 8 | `job_id, audio_mode` |  |
| `_agent_reset_state` | 515 | 3 | `job_id, stages, keep_asr, restart` |  |
| `_as_auto` | 547 | 10 | `fn, who` | fix 2026-11-12 agentI2: hook heal/av-sync là logic TỰ ĐỘNG → chạy trong agent_hold.auto_context, |
| `_agent_user_ctx` | 563 | 12 | `request, route` | agentI2: route Agent nhận lệnh NGƯỜI (UI/WebView, hoặc header X-Pineline-Caller: user từ Telegram |
| `_agent_notify` | 577 | 4 | `text` |  |
| `api_agent_status` | 609 | 6 | `` | Snapshot jobs cho panel Agent (không cần LLM). |
| `api_agent_chat` | 618 | 25 | `req, request` | Chat với AI Agent — tools gọi hàm nội bộ (queue/manifest), không HTTP self. |
| `api_agent_pending` | 646 | 2 | `` |  |
| `api_agent_confirm` | 651 | 8 | `req, request` | Chạy (approve) hoặc huỷ thao tác agent đã đỗ lại chờ xác nhận. |
| `api_agent_scan_failed` | 673 | 7 | `` | Quét mọi job lỗi/kẹt (không sửa). |
| `api_agent_heal_failed` | 683 | 22 | `req` | Heal hàng loạt job lỗi. apply=false chỉ plan. |
| `api_agent_review_diff` | 708 | 6 | `job_id` |  |
| `api_agent_qa_gate` | 717 | 10 | `job_id, req` |  |
| `api_agent_reset_state` | 736 | 7 | `job_id, req` | Reset sạch trạng thái các stage bị kẹt/lỗi của job (xóa artifact dở, gỡ .stop, đưa manifest về pending). |
| `api_agent_watch_once` | 746 | 12 | `` | Chạy 1 vòng watcher ngay (scan→heal safe nếu GPU rảnh). |
| `api_agent_av_sync` | 765 | 6 | `job_id` |  |
| `api_agent_av_sync_heal` | 774 | 8 | `job_id, req` |  |
| `api_agent_av_sync_scan` | 792 | 8 | `req` |  |
| `api_agent_av_sync_heal_batch` | 803 | 13 | `req` |  |

### Config / env keys (1)

`AGENT_WATCH_MAX_JOBS`

**File/artifact nhắc tới:** `manifest.json`, `script.json`, `tts.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=33 · swallow_except=4

### Lịch sử (từ docs/)

- **Fix logs (6):**
  - [Port V2→V5: Brain — job đã xong không heal + park tự động ≠ HOLD cần người](../../fixes/2026-11-13-port-brain-finished-hold.md)
  - [Port V2→V5: Second Brain (Telegram events + gỡ HOLD khi chạy tay) + đóng dấu luồng dịch theo job](../../fixes/2026-11-12-port-brain-hold-pipeline.md)
  - [Queue nhảy job khi còn HOLD/soát dở — mất invariant studio 1 job→output](../../fixes/2026-11-10-queue-park-held.md)
  - [Brain LLM tick trả tools=[] (không gọi tool)](../../fixes/2026-11-09-brain-llm-tool-loop.md)
  - [Hongguo "Merge all": không thấy đang chạy gì, 16 series rất lâu mới ra 1](../../fixes/2026-10-07-hg-merge-queue.md)
  - [Đợt 7: gỡ UI cũ, tách server.py](../../fixes/2026-10-06-batch7-ui-split.md)
- **Reviews:** [_atoms_http_agents](../../reviews/_atoms_http_agents.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
- Nhắc trong CHANGELOG: **5** lần · DECISIONS: **0** lần

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
