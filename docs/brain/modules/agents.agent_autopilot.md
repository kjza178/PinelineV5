# `agents.agent_autopilot`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `agents/agent_autopilot.py` · **Lớp:** `sidecar` · **348 dòng** (287 code) · **17 hàm**, **0 class** · sha1 `941b874ce8`

> Auto-pilot — queue need_queue + heal safe qua HTTP Pineline (:8801). Chạy trong sidecar (agent_tele_cmd) — không cần restart server.

### Phụ thuộc

- **Gọi tới (import nội bộ):** [core.batch_config](./core.batch_config.md), [core.fileio](./core.fileio.md)
- **Được dùng bởi:** [agents.agent_feeder](./agents.agent_feeder.md), [agents.agent_tele_cmd](./agents.agent_tele_cmd.md), [restart_server](./restart_server.md), [scripts.check_batch3](./scripts.check_batch3.md), [scripts.check_batch4](./scripts.check_batch4.md), [tools.migrate_work](./tools.migrate_work.md)
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [restart_server](./restart_server.md)
- **Test:** `tests/test_agent_hold_telegram.py`
- **Thư viện ngoài:** `requests`

```mermaid
flowchart LR
  agents_agent_autopilot[[agents.agent_autopilot]]
  agents_agent_feeder[agents.agent_feeder] --> agents_agent_autopilot
  agents_agent_tele_cmd[agents.agent_tele_cmd] --> agents_agent_autopilot
  restart_server[restart_server] --> agents_agent_autopilot
  scripts_check_batch3[scripts.check_batch3] --> agents_agent_autopilot
  scripts_check_batch4[scripts.check_batch4] --> agents_agent_autopilot
  tools_migrate_work[tools.migrate_work] --> agents_agent_autopilot
  agents_agent_autopilot --> core_batch_config[core.batch_config]
  agents_agent_autopilot --> core_fileio[core.fileio]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_now` | 24 | 2 | `` |  |
| `load_state` | 31 | 17 | `` |  |
| `save_state` | 50 | 2 | `state` |  |
| `update_state` | 54 | 7 | `fn` | Đọc-sửa-ghi trong khoá: tick sidecar và bật/tắt (server/script) không đè nhau. |
| `set_enabled` | 63 | 16 | `on` |  |
| `_get` | 81 | 4 | `base, path, timeout` |  |
| `caller_headers` | 87 | 9 | `caller, source` | fix 2026-11-12 agentI2: header nguồn lệnh. caller="user" CHỈ khi người gõ/bấm (Telegram); |
| `_post` | 98 | 17 | `base, path, body, timeout, headers` |  |
| `queue_opts` | 117 | 6 | `base` |  |
| `_opts_differ` | 125 | 9 | `a, b` |  |
| `sync_pending_to_batch` | 136 | 48 | `base` | Job chưa bắt đầu trong hàng chờ → theo config batch mới nhất (giữ thứ tự). |
| `status_brief` | 186 | 18 | `base` |  |
| `tick_once` | 206 | 62 | `base, force` | 1 vòng: queue need_queue (nếu rỗng/thiếu) + watch-once heal safe. |
| `agent_chat` | 270 | 24 | `base, message, history, allow_mutate, require_confirm, caller, source` | caller="user" (+ source="telegram"): tin do NGƯỜI gõ → tool chạy stage/dịch/tts/mux tính là chạy tay. |
| `agent_confirm` | 296 | 4 | `base, cid, approve, caller, source` |  |
| `hard_stop` | 302 | 33 | `base` | Dừng queue + mọi stage running + tắt ý định re-queue. |
| `format_status` | 337 | 12 | `brief` |  |

### Config / env keys (1)

`PINELINE_BASE`

**Cổng nhắc tới:** 8801

**File/artifact nhắc tới:** `autopilot_state.json`, `manifest.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=6 · global_stmt=1 · sleep=1

### Lịch sử (từ docs/)

- **Fix logs (6):**
  - [Port V2→V5: Second Brain (Telegram events + gỡ HOLD khi chạy tay) + đóng dấu luồng dịch theo job](../../fixes/2026-11-12-port-brain-hold-pipeline.md)
  - [V5 không khởi động được → chuyển về bố cục package bằng sync_from_v2](../../fixes/2026-11-11-v5-package-sync.md)
  - [2026-10-06 — Đợt 5 review: agent an toàn hơn](../../fixes/2026-10-06-batch5-agent-safety.md)
  - [2026-10-06 — Đợt 4 review: tranh chấp ghi, một bản tiến trình, checkpoint an toàn](../../fixes/2026-10-06-batch4-write-races.md)
  - [2026-10-06 — Đợt 3 review: opts một nguồn, config file-first, ghi nguyên tử](../../fixes/2026-10-06-batch3-single-source.md)
  - [2026-10-06 — Đợt 2 review: bảo mật + config một nguồn + LLM sập không để trống câu](../../fixes/2026-10-06-batch2-security.md)
- **Reviews:** [_atoms_http_agents](../../reviews/_atoms_http_agents.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-11-02-v4-structure-and-v2-port](../../reviews/2026-11-02-v4-structure-and-v2-port.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
- Nhắc trong CHANGELOG: **7** lần · DECISIONS: **0** lần

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
