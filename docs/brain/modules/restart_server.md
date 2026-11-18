# `restart_server`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `restart_server.py` · **Lớp:** `control` · **263 dòng** (226 code) · **9 hàm**, **0 class** · sha1 `dbc3fcaacf`

> Restart server Pineline (giữ sidecar), khôi phục hàng đợi + Auto-pilot. Port mặc định V5: 8805 (env PORT / PINELINE_BASE). Legacy 8804/8801 nếu đặt env. --after-current: rút job chờ, đợi job đang chạy xong rồi mới restar

### Phụ thuộc

- **Gọi tới (import nội bộ):** [agents.agent_autopilot](./agents.agent_autopilot.md), [agents.agent_watch](./agents.agent_watch.md), [tools.migrate_work](./tools.migrate_work.md)
- **Được dùng bởi:** —
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [agents.agent_tele_cmd](./agents.agent_tele_cmd.md)
- **Test:** ❌ chưa có test import trực tiếp

```mermaid
flowchart LR
  restart_server[[restart_server]]
  restart_server --> agents_agent_autopilot[agents.agent_autopilot]
  restart_server --> agents_agent_watch[agents.agent_watch]
  restart_server --> tools_migrate_work[tools.migrate_work]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_manifest_opts` | 61 | 6 | `job_id` |  |
| `_tg` | 69 | 7 | `msg` |  |
| `_proc_env` | 78 | 7 | `pattern` |  |
| `_precheck` | 87 | 11 | `` | '' nếu code mới compile + import được; ngược lại là lỗi (không restart). |
| `_job_parked` | 100 | 7 | `job_id` |  |
| `_requeue` | 109 | 13 | `order, opts` |  |
| `_start_server` | 124 | 19 | `clean_env, env` |  |
| `_restart_sidecar` | 145 | 7 | `env` |  |
| `main` | 154 | 100 | `` |  |

### Config / env keys (2)

`AGENT_TELEGRAM`, `PORT`

**Cổng nhắc tới:** 8802

**File/artifact nhắc tới:** `manifest.json`, `restart_pending.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=6 · file_writes=1 · sleep=5 · subprocess=5

### Lịch sử (từ docs/)

- **Fix logs (8):**
  - [V5 không khởi động được → chuyển về bố cục package bằng sync_from_v2](../../fixes/2026-11-11-v5-package-sync.md)
  - [Hongguo "Merge all": không thấy đang chạy gì, 16 series rất lâu mới ra 1](../../fixes/2026-10-07-hg-merge-queue.md)
  - [Restart hẹn giờ chết giữa chừng, server :8801 nằm chết](../../fixes/2026-10-06-restart-killed-itself.md)
  - [Đợt 7: gỡ UI cũ, tách server.py](../../fixes/2026-10-06-batch7-ui-split.md)
  - [2026-10-06 — Đợt 6 review: bảo trì (git, pytest, M3, dọn script chết)](../../fixes/2026-10-06-batch6-maintenance.md)
  - [2026-10-06 — Đợt 5 review: agent an toàn hơn](../../fixes/2026-10-06-batch5-agent-safety.md)
  - [2026-10-06 — Đợt 4 review: tranh chấp ghi, một bản tiến trình, checkpoint an toàn](../../fixes/2026-10-06-batch4-write-races.md)
  - [Đợt 1 — chặn mất dữ liệu (review 6/10)](../../fixes/2026-10-06-batch1-data-loss.md)
- **Reviews:** [_atoms_tools_ui](../../reviews/_atoms_tools_ui.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-11-02-v4-structure-sync](../../reviews/2026-11-02-v4-structure-sync.md), [2026-11-02-v4-structure-and-v2-port](../../reviews/2026-11-02-v4-structure-and-v2-port.md), [2026-11-02-v4-duplication-audit](../../reviews/2026-11-02-v4-duplication-audit.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
- Nhắc trong CHANGELOG: **14** lần · DECISIONS: **1** lần

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
