# `agents.agent_qa_gate`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `agents/agent_qa_gate.py` · **Lớp:** `agent` · **201 dòng** (174 code) · **8 hàm**, **0 class** · sha1 `69824b3fc6`

> Gate QA: translate → review → diff → mới cho TTS.

### Phụ thuộc

- **Gọi tới (import nội bộ):** [core.manifest](./core.manifest.md)
- **Được dùng bởi:** [agents.agent_core](./agents.agent_core.md), [http_routes.routes_agent](./http_routes.routes_agent.md)
- **Test:** ❌ chưa có test import trực tiếp

```mermaid
flowchart LR
  agents_agent_qa_gate[[agents.agent_qa_gate]]
  agents_agent_core[agents.agent_core] --> agents_agent_qa_gate
  http_routes_routes_agent[http_routes.routes_agent] --> agents_agent_qa_gate
  agents_agent_qa_gate --> core_manifest[core.manifest]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_now` | 11 | 2 | `` |  |
| `_load_rows` | 15 | 8 | `path` |  |
| `snapshot_pre_review` | 25 | 7 | `work_dir` |  |
| `review_diff` | 34 | 70 | `work_dir, job_id` | So script.json vs script.pre_review.json + thống kê rv / missing. |
| `_fail_reasons` | 106 | 11 | `n, missing_ratio, review_ran, pack` |  |
| `evaluate_qa_gate` | 119 | 2 | `work_dir` |  |
| `run_qa_gate` | 123 | 60 | `work_dir, run_review_fn, target, review_model` | Snapshot → run_review (sync) → diff → quyết định pass/block. |
| `set_qa_gate` | 185 | 17 | `work_dir, enabled, override_pass` |  |

**File/artifact nhắc tới:** `glossary.json`, `qa_flags.json`, `script.json`, `script.pre_review.json`, `style_lock.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=4

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
