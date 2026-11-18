# `tools.asr_boundary_scan`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `tools/asr_boundary_scan.py` · **Lớp:** `asr` · **147 dòng** (133 code) · **4 hàm**, **0 class** · sha1 `a4f8a5b30f`

> tools/asr_boundary_scan.py — CHỈ ĐỌC: tìm câu ASR nghi bị cắt ở biên slice cứng k×1200 s. Lỗi cũ (trước fix 2026-11-13-firered-slice-silence): firered_asr.py cắt audio tại đúng k×FIRERED_SLICE_SEC -> câu vắt biên bị cắt 

### Phụ thuộc

- **Gọi tới (import nội bộ):** —
- **Được dùng bởi:** —
- **Test:** ❌ chưa có test import trực tiếp

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_core` | 25 | 2 | `t` |  |
| `scan_rows` | 29 | 46 | `rows, slice_sec, tol, near` | Trả danh sách biên nghi lỗi: {boundary, kind, prev, next}. |
| `scan_job` | 77 | 27 | `job, slice_sec, all_engines` |  |
| `main` | 106 | 38 | `argv` |  |

**File/artifact nhắc tới:** `asr.json`, `manifest.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=2 · file_writes=1 · swallow_except=1

### Lịch sử (từ docs/)

- **Fix logs (1):**
  - [Port V2→V5: preflight/chuẩn hoá video nguồn + extract_pcm bền + FireRed slice khoảng lặng + câu rác «None.» / ](../../fixes/2026-11-13-port-preflight-slice-junk.md)
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
