# `agents.agent_pronoun_pass`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `agents/agent_pronoun_pass.py` · **Lớp:** `agent` · **256 dòng** (231 code) · **4 hàm**, **0 class** · sha1 `c4c613aac0`

> Rà XƯNG HÔ trong bản dịch theo glossary.pronouns + genre. 1. Quét deterministic (cùng apply_pronoun_postpass) rồi 2. Các câu còn nghi (Ta/Ngươi lệch genre, hoặc cặp who+to có mặt mà self/call lệch)

### Phụ thuộc

- **Gọi tới (import nội bộ):** [config](./config.md), [core.config](./core.config.md), [core.manifest](./core.manifest.md), [engines.llm](./engines.llm.md), [engines.subs](./engines.subs.md), [engines.translate](./engines.translate.md), [pronoun_register_policy](./pronoun_register_policy.md)
- **Được dùng bởi:** —
- **Test:** ❌ chưa có test import trực tiếp

```mermaid
flowchart LR
  agents_agent_pronoun_pass[[agents.agent_pronoun_pass]]
  agents_agent_pronoun_pass --> config[config]
  agents_agent_pronoun_pass --> core_config[core.config]
  agents_agent_pronoun_pass --> core_manifest[core.manifest]
  agents_agent_pronoun_pass --> engines_llm[engines.llm]
  agents_agent_pronoun_pass --> engines_subs[engines.subs]
  agents_agent_pronoun_pass --> engines_translate[engines.translate]
  agents_agent_pronoun_pass --> pronoun_register_policy[pronoun_register_policy]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_fold` | 22 | 3 | `s` |  |
| `find_pronoun_issues` | 27 | 63 | `rows, plan` |  |
| `_fix_batch` | 92 | 36 | `chunk, plan_block, model, system` |  |
| `run_pronoun_pass` | 130 | 127 ⚠️ | `work_dir, model` |  |

**Hàm dài ≥120 dòng:** `run_pronoun_pass` (127, L130)

### Config / env keys (1)

`PRONOUN_TITLE_POLICY`

**File/artifact nhắc tới:** `glossary.json`, `script.json`, `sub.vi.srt`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=8 · file_writes=3 · swallow_except=3

### Lịch sử (từ docs/)

- **Fix logs (2):**
  - [Pronoun-QA GPT vá đỏ → Aurora 413 (payload quá lớn)](../../fixes/2026-11-06-pronoun-qa-413-slim.md)
  - [Lệch xưng hô sau dịch (Ta–Ngươi / sai self–call)](../../fixes/2026-11-02-pronoun-xung-ho.md)
- **Reviews:** [_atoms_http_agents](../../reviews/_atoms_http_agents.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md)
- Nhắc trong CHANGELOG: **3** lần · DECISIONS: **1** lần

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
