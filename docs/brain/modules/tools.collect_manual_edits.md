# `tools.collect_manual_edits`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `tools/collect_manual_edits.py` · **Lớp:** `misc` · **192 dòng** (164 code) · **8 hàm**, **0 class** · sha1 `6fee4cf71b`

> Gom câu NGƯỜI SỬA TAY (manual) trong work dir thành ỨNG VIÊN golden (định dạng golden V6) — CHỈ ĐỌC work dir. 2026-11-12 next (Bước 8b). Không đụng pipeline, không ghi gì vào work dir. Ghi vào thư mục --out: <out>/<job>/

### Phụ thuộc

- **Gọi tới (import nội bộ):** —
- **Được dùng bởi:** —
- **Test:** ❌ chưa có test import trực tiếp

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_load` | 30 | 5 | `p, default` |  |
| `_trace_prev` | 37 | 25 | `job_dir` | {i: vi máy cuối cùng} từ trace.1.jsonl rồi trace.jsonl (bỏ bước «manual»). |
| `_norm` | 64 | 2 | `s` |  |
| `_pair_of` | 68 | 5 | `plan, spk, to` |  |
| `_split` | 75 | 3 | `v` |  |
| `collect_job` | 80 | 59 | `job_dir` |  |
| `_jobs` | 141 | 4 | `work, only` |  |
| `main` | 147 | 42 | `argv` |  |

**File/artifact nhắc tới:** `characters.json`, `glossary.json`, `lines.gold.jsonl`, `manifest.json`, `meta.json`, `pairs.json`, `script.json`, `summary.json`, `trace.1.jsonl`, `trace.jsonl`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=2 · file_writes=2

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
