# `scripts.tree_audit`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `scripts/tree_audit.py` · **Lớp:** `ops` · **226 dòng** (199 code) · **9 hàm**, **0 class** · sha1 `3730462856`

> tree_audit.py — Kiểm tra sức khoẻ cây code Pineline (V2/V4/V5) sau mỗi lần sync/port. Chỉ đọc (AST + hash), không import, không chạy code. Bắt các lỗi kiểu: • import không resolve được trong cây này  → server/sidecar khô

### Phụ thuộc

- **Gọi tới (import nội bộ):** —
- **Được dùng bởi:** —
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [scripts.sync_from_v2](./scripts.sync_from_v2.md)
- **Test:** ❌ chưa có test import trực tiếp

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `md5` | 51 | 5 | `p` |  |
| `py_files` | 58 | 15 | `root` |  |
| `module_exists` | 75 | 12 | `root, base_dir, dotted` | Có resolve được `dotted` từ sys.path = [thư mục script, ROOT] không. |
| `guarded` | 89 | 10 | `node, parents` | Import nằm trong try/except (ImportError/Exception) hay trong hàm → coi là tuỳ chọn. |
| `audit_imports` | 101 | 29 | `root` | (level, file, line, module, kind) — ERROR: import top-level không resolve; WARN: trong hàm/try. |
| `audit_ports` | 132 | 18 | `root` |  |
| `audit_duplicates` | 152 | 13 | `root` |  |
| `audit_peers` | 167 | 16 | `root, peers` |  |
| `main` | 185 | 38 | `` |  |

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=1 · file_writes=1 · swallow_except=1

### Lịch sử (từ docs/)

- **Fix logs (5):**
  - [Port V2→V5: preflight/chuẩn hoá video nguồn + extract_pcm bền + FireRed slice khoảng lặng + câu rác «None.» / ](../../fixes/2026-11-13-port-preflight-slice-junk.md)
  - [Port V2→V5: Brain — job đã xong không heal + park tự động ≠ HOLD cần người](../../fixes/2026-11-13-port-brain-finished-hold.md)
  - [Port V2→V5: luồng dịch `translate_simple` (mặc định) + Demucs trước ASR](../../fixes/2026-11-12-port-simple-demucs.md)
  - [V5 không khởi động được → chuyển về bố cục package bằng sync_from_v2](../../fixes/2026-11-11-v5-package-sync.md)
  - [REVIEW lỗi bị coi là đã soát · park treo hàng đợi · Brain V4 điều khiển nhầm V2](../../fixes/2026-11-11-review-fail-park-port.md)
- **Reviews:** [2026-11-11-v4-v5-port-review](../../reviews/2026-11-11-v4-v5-port-review.md)
- Nhắc trong CHANGELOG: **3** lần · DECISIONS: **0** lần

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
