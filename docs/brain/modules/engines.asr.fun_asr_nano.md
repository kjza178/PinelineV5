# `engines.asr.fun_asr_nano`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `engines/asr/fun_asr_nano.py` · **Lớp:** `asr` · **597 dòng** (521 code) · **11 hàm**, **0 class** · sha1 `14d1281219`

> fun_asr_nano.py — STAGE ASR bằng Fun-ASR-Nano (chất lượng tiếng Trung cao nhất). Model : FunAudioLLM/Fun-ASR-Nano-2512 (+ fsmn-vad cắt đoạn dài) Đầu vào : work/<job>/source.mp4

### Phụ thuộc

- **Gọi tới (import nội bộ):** [core.manifest](./core.manifest.md), [engines.asr.asr](./engines.asr.asr.md), [engines.asr.asr_hybrid_progress](./engines.asr.asr_hybrid_progress.md), [engines.asr.asr_spam](./engines.asr.asr_spam.md), [engines.asr.asr_vad_utils](./engines.asr.asr_vad_utils.md), [engines.subs](./engines.subs.md), [engines.vram](./engines.vram.md)
- **Được dùng bởi:** [engines.asr.asr_fix_align](./engines.asr.asr_fix_align.md), [engines.asr.asr_repair](./engines.asr.asr_repair.md), [engines.asr.firered_asr](./engines.asr.firered_asr.md), [engines.asr.hybrid_asr](./engines.asr.hybrid_asr.md), [engines.asr.nano_fa_asr](./engines.asr.nano_fa_asr.md), [engines.asr.paraformer_zh](./engines.asr.paraformer_zh.md), [engines.asr.sensevoice_asr](./engines.asr.sensevoice_asr.md)
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [restart_server](./restart_server.md), [server](./server.md)
- **Test:** ❌ chưa có test import trực tiếp
- **Thư viện ngoài:** `funasr`, `soundfile`, `torch`, `transformers`

```mermaid
flowchart LR
  engines_asr_fun_asr_nano[[engines.asr.fun_asr_nano]]
  engines_asr_asr_fix_align[engines.asr.asr_fix_align] --> engines_asr_fun_asr_nano
  engines_asr_asr_repair[engines.asr.asr_repair] --> engines_asr_fun_asr_nano
  engines_asr_firered_asr[engines.asr.firered_asr] --> engines_asr_fun_asr_nano
  engines_asr_hybrid_asr[engines.asr.hybrid_asr] --> engines_asr_fun_asr_nano
  engines_asr_nano_fa_asr[engines.asr.nano_fa_asr] --> engines_asr_fun_asr_nano
  engines_asr_paraformer_zh[engines.asr.paraformer_zh] --> engines_asr_fun_asr_nano
  engines_asr_sensevoice_asr[engines.asr.sensevoice_asr] --> engines_asr_fun_asr_nano
  engines_asr_fun_asr_nano --> core_manifest[core.manifest]
  engines_asr_fun_asr_nano --> engines_asr_asr[engines.asr.asr]
  engines_asr_fun_asr_nano --> engines_asr_asr_hybrid_progress[engines.asr.asr_hybrid_progress]
  engines_asr_fun_asr_nano --> engines_asr_asr_spam[engines.asr.asr_spam]
  engines_asr_fun_asr_nano --> engines_asr_asr_vad_utils[engines.asr.asr_vad_utils]
  engines_asr_fun_asr_nano --> engines_subs[engines.subs]
  engines_asr_fun_asr_nano --> engines_vram[engines.vram]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_pick_device` | 44 | 10 | `device` |  |
| `_wav_dur` | 56 | 13 | `wav` |  |
| `_ms_to_s` | 71 | 6 | `v` | FunASR timestamp luôn là milliseconds. |
| `_split_text_by_punct` | 79 | 4 | `text` | Tách câu theo dấu câu (mỏng: gọi subs.split_text_by_punct). |
| `_spread_sentences` | 85 | 19 | `text, start, end` | Không có timestamp ký tự -> chia thời gian theo độ dài chữ. |
| `_parse_funasr_result` | 106 | 70 | `res, audio_dur` | Chuẩn hoá output FunASR -> [{start, end, text}, ...]. |
| `_split_by_punct` | 178 | 36 | `text, char_ts` | Gộp timestamp ký tự thành câu theo dấu câu Trung/Việt. |
| `_vad_ranges_chunked` | 216 | 77 | `vad_model, wav, audio_dur, vad_kw, chunk_s, overlap_s, on_progress` | VAD theo cửa sổ ~chunk_s — tránh treo generate() trên file dài. |
| `_vad_slice_asr` | 295 | 102 | `asr_model, vad_model, wav, language, on_progress, pad_s, overlap_s,…` | VAD cắt đoạn -> ASR từng đoạn có pad/overlap (Fun-ASR-Nano không có CTC ts). |
| `run_asr_nano` | 398 | 180 ⚠️ | `work_dir, device, force, language, hub, sidecar` | sidecar: ghi asr.<tag>.json + sub.zh.<tag>.srt, không đụng asr.json / manifest ASR chính. |
| `main` | 580 | 14 | `argv` |  |

**Hàm dài ≥120 dòng:** `run_asr_nano` (180, L398)

### Config / env keys (3)

`ASR_VAD_CHUNK_S`, `HF_HUB_DISABLE_SYMLINKS`, `HF_HUB_DISABLE_SYMLINKS_WARNING`

**File/artifact nhắc tới:** `.progress.json`, `asr.json`, `audio.wav`, `sub.zh.srt`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=12 · file_writes=7 · swallow_except=3

### Lịch sử (từ docs/)

- **Fix logs (1):**
  - [2026-10-06 — Đợt 4 review: tranh chấp ghi, một bản tiến trình, checkpoint an toàn](../../fixes/2026-10-06-batch4-write-races.md)
- **Reviews:** [_atoms_engines](../../reviews/_atoms_engines.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-11-02-v4-structure-and-v2-port](../../reviews/2026-11-02-v4-structure-and-v2-port.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
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
