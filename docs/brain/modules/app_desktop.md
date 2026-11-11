# `app_desktop`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `app_desktop.py` · **Lớp:** `control` · **147 dòng** (121 code) · **4 hàm**, **0 class** · sha1 `68b8955ebb`

> app_desktop.py — Desktop App Studio cho Pineline V4. Sử dụng Microsoft Edge WebView2 (native engine siêu nhẹ, mượt mà, không phụ thuộc trình duyệt). Tự động khởi động backend, hiển thị cửa sổ native, dọn dẹp sạch tiến tr

### Phụ thuộc

- **Gọi tới (import nội bộ):** —
- **Được dùng bởi:** —
- **Test:** ❌ chưa có test import trực tiếp
- **Thư viện ngoài:** `webview`

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `is_port_open` | 36 | 6 | `host, port` |  |
| `start_backend` | 44 | 32 | `` |  |
| `wait_for_server` | 78 | 7 | `timeout` |  |
| `main` | 87 | 57 | `` |  |

### Config / env keys (2)

`PORT`, `TEMP`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=7 · sleep=2 · subprocess=1 · swallow_except=5 · threads=1

### Lịch sử (từ docs/)

- Fix logs: —
- **Reviews:** [_atoms_tools_ui](../../reviews/_atoms_tools_ui.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-11-02-v4-structure-sync](../../reviews/2026-11-02-v4-structure-sync.md), [2026-11-02-v4-structure-and-v2-port](../../reviews/2026-11-02-v4-structure-and-v2-port.md), [2026-11-02-v4-duplication-audit](../../reviews/2026-11-02-v4-duplication-audit.md)
- Nhắc trong CHANGELOG: **0** lần · DECISIONS: **2** lần

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
