# `engines.translate_simple.pair_fill`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `engines/translate_simple/pair_fill.py` · **Lớp:** `misc` · **134 dòng** (116 code) · **6 hàm**, **0 class** · sha1 `fc31e2e3b6`

> Bước 6 (2026-11-12 next) — bổ sung cặp xưng hô THIẾU bằng 1 lần gọi model (cờ SIMPLE_PAIR_FILL=1). Sau review lượt 1: cặp spk→to mà cả hai là nhân vật plan, CHƯA có cặp (kể cả sau bảng quy tắc bước 2), xuất hiện ≥ SIMPLE

### Phụ thuộc

- **Gọi tới (import nội bộ):** [engines.cloud_retry](./engines.cloud_retry.md), [engines.llm](./engines.llm.md), [engines.translate_simple.cfg](./engines.translate_simple.cfg.md), [engines.translate_simple.plan_view](./engines.translate_simple.plan_view.md), [engines.translate_simple.stage_review](./engines.translate_simple.stage_review.md), [engines.translate_simple.suggest](./engines.translate_simple.suggest.md)
- **Được dùng bởi:** [engines.translate_simple.pipeline](./engines.translate_simple.pipeline.md)
- **Test:** `tests/test_translate_simple_next.py`
- **Thư viện ngoài:** `engines`

```mermaid
flowchart LR
  engines_translate_simple_pair_fill[[engines.translate_simple.pair_fill]]
  engines_translate_simple_pipeline[engines.translate_simple.pipeline] --> engines_translate_simple_pair_fill
  engines_translate_simple_pair_fill --> engines_cloud_retry[engines.cloud_retry]
  engines_translate_simple_pair_fill --> engines_llm[engines.llm]
  engines_translate_simple_pair_fill --> engines_translate_simple_cfg[engines.translate_simple.cfg]
  engines_translate_simple_pair_fill --> engines_translate_simple_plan_view[engines.translate_simple.plan_view]
  engines_translate_simple_pair_fill --> engines_translate_simple_stage_review[engines.translate_simple.stage_review]
  engines_translate_simple_pair_fill --> engines_translate_simple_suggest[engines.translate_simple.suggest]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `candidates` | 31 | 2 | `rows, pv, conf_min, min_n` |  |
| `_char` | 35 | 6 | `pv, name` |  |
| `_lines_between` | 43 | 9 | `rows, pv, a, b` |  |
| `build_prompt` | 54 | 21 | `rows, pv, cands` |  |
| `parse` | 77 | 21 | `text, want, pv, conf_min` |  |
| `run` | 100 | 35 | `rows, pv, model, conf_review, min_n, conf_min, stop_check` | Trả {"asked": [...], "added": [...], "rows": [i…], "error"?}. Không ném (trừ «stopped by user»). |

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=1

### Lịch sử (từ docs/)

- Fix logs: —
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
