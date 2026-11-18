# `engines.pronoun_register_policy`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `engines/pronoun_register_policy.py` · **Lớp:** `translate` · **307 dòng** (255 code) · **10 hàm**, **1 class** · sha1 `17e8ad74c2`

> Policy xưng hô tổng quát cho mix #1+#3 — không gắn 1 job/phim. Mục tiêu: - Phát hiện cửa sổ CÓ DANH XƯNG BẬC (title hierarchy) + ngôi 2 thân mật «cậu»

### Phụ thuộc

- **Gọi tới (import nội bộ):** —
- **Được dùng bởi:** [agents.agent_pronoun_pass](./agents.agent_pronoun_pass.md)
- **Test:** `tests/test_translate_b1.py`, `tests/test_translate_b1_scenarios.py`

```mermaid
flowchart LR
  engines_pronoun_register_policy[[engines.pronoun_register_policy]]
  agents_agent_pronoun_pass[agents.agent_pronoun_pass] --> engines_pronoun_register_policy
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| **class `RegisterPlan`** | 89 | 1 method | | Kế hoạch ngôi cho 1 job (suy từ style_lock, không từ job id). |
| `_is_standalone_2nd_cau` | 60 | 12 | `text, m` | «cậu» tại m có phải đại từ ngôi 2 đứng độc lập không (xem danh sách ngoại lệ trên). |
| `standalone_2nd_cau_spans` | 74 | 4 | `text` | Vị trí các «cậu» là đại từ ngôi 2 độc lập (để thay máy an toàn). |
| `detect_mode` | 112 | 31 | `plan` |  |
| `build_register_plan` | 145 | 7 | `plan` |  |
| `window_has_title` | 154 | 3 | `texts` |  |
| `cue_has_intimate_2nd` | 159 | 3 | `vi` |  |
| `scan_title_intimate_issues` | 164 | 39 | `rows, window, existing_ids` | Thêm issue khi cue có «cậu» và cửa sổ ±window có title bậc. |
| `mechanical_cau_to_formal` | 205 | 30 | `vi, preferred` | Fallback máy: cậu → preferred; Các cậu → Các preferred / Các vị. |
| `normalize_ong_nguoi_in_title_window` | 237 | 37 | `rows, changed_ids, preferred, window` | Sau LLM: nếu cue vừa sửa còn ông+ngươi loạn quanh title → ép preferred. |
| `enforce_remaining_cau` | 276 | 32 | `rows, preferred, window` | Sau cùng: còn cậu trong title window → máy đổi (không chờ LLM). |

### Lịch sử (từ docs/)

- **Fix logs (1):**
  - [V5 không khởi động được → chuyển về bố cục package bằng sync_from_v2](../../fixes/2026-11-11-v5-package-sync.md)
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
