# `tools.simple_stats`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `tools/simple_stats.py` · **Lớp:** `misc` · **116 dòng** (101 code) · **4 hàm**, **0 class** · sha1 `15c661e6df`

> Thống kê luồng dịch simple THEO JOB — CHỈ ĐỌC work dir (2026-11-12 next, Bước 8c). Mỗi job: số câu · tỉ lệ câu còn cờ (theo loại: pronoun/name/empty/cjk) · cổng (done/park/hold + lý do) · số lô review lỗi · cặp thiếu (pl

### Phụ thuộc

- **Gọi tới (import nội bộ):** —
- **Được dùng bởi:** —
- **Test:** ❌ chưa có test import trực tiếp

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_load` | 21 | 5 | `p, default` |  |
| `job_stats` | 28 | 39 | `jd` |  |
| `to_md` | 69 | 16 | `stats` |  |
| `main` | 87 | 26 | `argv` |  |

**File/artifact nhắc tới:** `manifest.json`, `plan_inferred.json`, `plan_suggestions.json`, `script.json`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=1 · file_writes=1

### Lịch sử (từ docs/)

- Fix logs: —
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
