# `agent_quality`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `agent_quality.py` · **Lớp:** `agent` · **356 dòng** (331 code) · **6 hàm**, **0 class** · sha1 `fc43fe4a13`

> Deterministic VI quality scan + safe heals (Second Brain L2). Port từ D:\PinelineV2_tmp\_qa_watch_05670.py — không phụ thuộc Gemma.

### Phụ thuộc

- **Gọi tới (import nội bộ):** [agent_hang_fix](./agent_hang_fix.md), [fileio](./fileio.md)
- **Được dùng bởi:** [agent_brain](./agent_brain.md), [agent_hang_fix](./agent_hang_fix.md), [agent_qa_gate](./agent_qa_gate.md), [server](./server.md)
- **Test:** `tests/test_agent_quality.py`

```mermaid
flowchart LR
  agent_quality[[agent_quality]]
  agent_brain[agent_brain] --> agent_quality
  agent_hang_fix[agent_hang_fix] --> agent_quality
  agent_qa_gate[agent_qa_gate] --> agent_quality
  server[server] --> agent_quality
  agent_quality --> agent_hang_fix[agent_hang_fix]
  agent_quality --> fileio[fileio]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `scan_script` | 68 | 105 | `rows` | Trả flags {i,sev,kind,note,zh,vi,rv,mt}. |
| `apply_safe_heals` | 175 | 51 | `rows` | Heal deterministic an toàn tại chỗ. Trả số câu đổi. |
| `summarize_flags` | 228 | 13 | `flags` |  |
| `write_qa_brain` | 243 | 13 | `work_dir, flags, healed` | Ghi work/<job>/qa_brain.json cho gate + UI. |
| `load_qa_brain` | 258 | 9 | `work_dir` |  |
| `scan_and_heal_job` | 269 | 88 | `work_dir, write` | Scan script.json → heal → (high hang) LLM trace/fix → qa_brain.json. |

**File/artifact nhắc tới:** `qa_brain.json`, `script.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=5 · file_writes=3

### Lịch sử (từ docs/)

- **Fix logs (1):**
  - [Brain HOLD vì high hang — cần LLM trace/xử lý rồi mới mở](../../fixes/2026-11-10-brain-hang-llm-fix.md)
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
