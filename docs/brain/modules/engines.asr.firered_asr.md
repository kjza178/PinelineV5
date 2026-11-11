# `engines.asr.firered_asr`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `engines/asr/firered_asr.py` · **Lớp:** `asr` · **346 dòng** (300 code) · **5 hàm**, **0 class** · sha1 `7bfcaac2b3`

> firered_asr.py — STAGE ASR bằng FireRedASR2-AED (system VAD+LID+ASR+Punc). Cần clone repo + tải model local (không pip một dòng): scripts\install_firered_asr.bat

### Phụ thuộc

- **Gọi tới (import nội bộ):** [core.config](./core.config.md), [core.manifest](./core.manifest.md), [engines.asr.asr](./engines.asr.asr.md), [engines.asr.asr_spam](./engines.asr.asr_spam.md), [engines.asr.fun_asr_nano](./engines.asr.fun_asr_nano.md), [engines.subs](./engines.subs.md), [engines.vram](./engines.vram.md)
- **Được dùng bởi:** —
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [restart_server](./restart_server.md), [server](./server.md)
- **Test:** ❌ chưa có test import trực tiếp
- **Thư viện ngoài:** `fireredasr2s`

```mermaid
flowchart LR
  engines_asr_firered_asr[[engines.asr.firered_asr]]
  engines_asr_firered_asr --> core_config[core.config]
  engines_asr_firered_asr --> core_manifest[core.manifest]
  engines_asr_firered_asr --> engines_asr_asr[engines.asr.asr]
  engines_asr_firered_asr --> engines_asr_asr_spam[engines.asr.asr_spam]
  engines_asr_firered_asr --> engines_asr_fun_asr_nano[engines.asr.fun_asr_nano]
  engines_asr_firered_asr --> engines_subs[engines.subs]
  engines_asr_firered_asr --> engines_vram[engines.vram]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_roots` | 46 | 6 | `` |  |
| `_ensure_firered_importable` | 54 | 13 | `root` |  |
| `_parse_firered_result` | 69 | 45 | `result` | FireRedAsr2System.process → [{start,end,text}]. |
| `run_asr_firered` | 116 | 217 ⚠️ | `work_dir, device, force` |  |
| `main` | 335 | 8 | `argv` |  |

**Hàm dài ≥120 dòng:** `run_asr_firered` (217, L116)

### Config / env keys (7)

`FIRERED_MODELS`, `FIRERED_ROOT`, `FIRERED_SLICE_SEC`, `FIRERED_USE_HALF`, `HF_HUB_DISABLE_SYMLINKS`, `HF_HUB_DISABLE_SYMLINKS_WARNING`, `PATH`

**File/artifact nhắc tới:** `asr.json`, `audio.wav`, `sub.zh.srt`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=3 · file_writes=2 · subprocess=1

### Lịch sử (từ docs/)

- **Fix logs (1):**
  - [2026-10-06 — Đợt 4 review: tranh chấp ghi, một bản tiến trình, checkpoint an toàn](../../fixes/2026-10-06-batch4-write-races.md)
- **Reviews:** [_atoms_engines](../../reviews/_atoms_engines.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
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
