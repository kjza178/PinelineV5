# `tools.pick_dirs_dialog`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `tools/pick_dirs_dialog.py` · **Lớp:** `ops` · **204 dòng** (169 code) · **4 hàm**, **0 class** · sha1 `9a9157ba1d`

> Hộp thoại chọn NHIỀU folder cùng lúc (Listbox multi-select). Chạy: python tools/pick_dirs_dialog.py [initial_dir] Stdout: mỗi path 1 dòng (UTF-8). Rỗng = hủy.

### Phụ thuộc

- **Gọi tới (import nội bộ):** —
- **Được dùng bởi:** —
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [server](./server.md)
- **Test:** ❌ chưa có test import trực tiếp

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_nat_key` | 14 | 3 | `name` |  |
| `_count_videos` | 19 | 14 | `folder, limit` |  |
| `_list_children` | 35 | 10 | `root` |  |
| `main` | 47 | 154 ⚠️ | `` |  |

**Hàm dài ≥120 dòng:** `main` (154, L47)

### Lịch sử (từ docs/)

- Fix logs: —
- **Reviews:** [_atoms_tools_ui](../../reviews/_atoms_tools_ui.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md)
- Nhắc trong CHANGELOG: **2** lần · DECISIONS: **0** lần

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
