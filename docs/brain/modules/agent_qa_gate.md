# `agent_qa_gate`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `agent_qa_gate.py` · **Lớp:** `agent` · **226 dòng** (196 code) · **8 hàm**, **0 class** · sha1 `1b0edf4728`

> Gate QA: translate → review → diff → mới cho TTS.

### Phụ thuộc

- **Gọi tới (import nội bộ):** [agent_quality](./agent_quality.md)
- **Được dùng bởi:** [agent_core](./agent_core.md), [routes_agent](./routes_agent.md), [server](./server.md)
- **Test:** ❌ chưa có test import trực tiếp
- **Thư viện ngoài:** `manifest`

```mermaid
flowchart LR
  agent_qa_gate[[agent_qa_gate]]
  agent_core[agent_core] --> agent_qa_gate
  routes_agent[routes_agent] --> agent_qa_gate
  server[server] --> agent_qa_gate
  agent_qa_gate --> agent_quality[agent_quality]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_now` | 11 | 2 | `` |  |
| `_load_rows` | 15 | 8 | `path` |  |
| `snapshot_pre_review` | 25 | 7 | `work_dir` |  |
| `review_diff` | 34 | 86 | `work_dir, job_id` | So script.json vs script.pre_review.json + thống kê rv / missing. |
| `_fail_reasons` | 122 | 20 | `n, missing_ratio, review_ran, pack, brain_high` |  |
| `evaluate_qa_gate` | 144 | 2 | `work_dir` |  |
| `run_qa_gate` | 148 | 60 | `work_dir, run_review_fn, target, review_model` | Snapshot → run_review (sync) → diff → quyết định pass/block. |
| `set_qa_gate` | 210 | 17 | `work_dir, enabled, override_pass` |  |

**File/artifact nhắc tới:** `glossary.json`, `qa_flags.json`, `script.json`, `script.pre_review.json`, `style_lock.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=5

### Lịch sử (từ docs/)

- Fix logs: —
- **Reviews:** [_atoms_http_agents](../../reviews/_atoms_http_agents.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md)
- Nhắc trong CHANGELOG: **0** lần · DECISIONS: **0** lần

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
