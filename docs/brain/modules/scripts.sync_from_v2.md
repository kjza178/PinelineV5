# `scripts.sync_from_v2`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `scripts/sync_from_v2.py` · **Lớp:** `ops` · **368 dòng** (309 code) · **12 hàm**, **0 class** · sha1 `2d6b838b24`

> sync_from_v2.py — Đồng bộ code từ cây nguồn (V2, bố cục phẳng) sang cây đích. Thay cho việc chép tay file root ("Sync V2/V4/V5") — cách đã làm V5 hỏng 11/2026. • Đích PHẲNG (V4): chép file runtime có trong allowlist, giữ

### Phụ thuộc

- **Gọi tới (import nội bộ):** —
- **Được dùng bởi:** —
- **Test:** ❌ chưa có test import trực tiếp

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `md5` | 65 | 2 | `p` |  |
| `read` | 69 | 6 | `p` |  |
| `write` | 77 | 5 | `p, text, crlf, bom` |  |
| `is_package_tree` | 84 | 2 | `root` |  |
| `package_index` | 88 | 12 | `root` | stem → [đường dẫn tương đối trong package] (một tên có thể ở nhiều chỗ). |
| `home_for` | 102 | 5 | `stem` |  |
| `_line_offsets` | 111 | 6 | `text` |  |
| `rewrite_imports` | 119 | 55 | `text, dotted` | import phẳng → package theo `dotted` (stem → 'core.manifest'). Trả (text, số chỗ đổi). |
| `rewrite_file_paths` | 180 | 23 | `text, depth` | Module ở root được chuyển xuống `depth` cấp: thư mục của file == gốc dự án → giữ ý nghĩa đó. |
| `add_bootstrap` | 208 | 27 | `text, depth` | Cho phép `python engines/asr/x.py` import `core.*` khi chạy trực tiếp. |
| `build_plan` | 239 | 24 | `src, dst, only` |  |
| `main` | 265 | 100 | `` |  |

**File/artifact nhắc tới:** `sync_report.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=1 · file_writes=2 · swallow_except=1

### Lịch sử (từ docs/)

- **Fix logs (3):**
  - [Port V2→V5: luồng dịch `translate_simple` (mặc định) + Demucs trước ASR](../../fixes/2026-11-12-port-simple-demucs.md)
  - [Port V2→V5: Second Brain (Telegram events + gỡ HOLD khi chạy tay) + đóng dấu luồng dịch theo job](../../fixes/2026-11-12-port-brain-hold-pipeline.md)
  - [V5 không khởi động được → chuyển về bố cục package bằng sync_from_v2](../../fixes/2026-11-11-v5-package-sync.md)
- **Reviews:** [2026-11-11-v4-v5-port-review](../../reviews/2026-11-11-v4-v5-port-review.md)
- Nhắc trong CHANGELOG: **4** lần · DECISIONS: **0** lần

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
