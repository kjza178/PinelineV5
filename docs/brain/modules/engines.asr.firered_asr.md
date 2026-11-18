# `engines.asr.firered_asr`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `engines/asr/firered_asr.py` · **Lớp:** `asr` · **570 dòng** (489 code) · **14 hàm**, **0 class** · sha1 `2501d529a1`

> firered_asr.py — STAGE ASR bằng FireRedASR2-AED (system VAD+LID+ASR+Punc). Cần clone repo + tải model local (không pip một dòng): scripts\install_firered_asr.bat

### Phụ thuộc

- **Gọi tới (import nội bộ):** [core.config](./core.config.md), [core.manifest](./core.manifest.md), [engines.asr.asr](./engines.asr.asr.md), [engines.asr.asr_spam](./engines.asr.asr_spam.md), [engines.asr.fun_asr_nano](./engines.asr.fun_asr_nano.md), [engines.separate](./engines.separate.md), [engines.subs](./engines.subs.md), [engines.text_junk](./engines.text_junk.md), [engines.vram](./engines.vram.md)
- **Được dùng bởi:** —
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [agents.agent_brain_notify](./agents.agent_brain_notify.md), [engines.translate_simple.zh_source](./engines.translate_simple.zh_source.md), [restart_server](./restart_server.md), [server](./server.md), [tools.asr_boundary_scan](./tools.asr_boundary_scan.md)
- **Test:** `tests/test_firered_slice_silence.py`, `tests/test_simple_junk_park.py`
- **Thư viện ngoài:** `fireredasr2s`, `numpy`

```mermaid
flowchart LR
  engines_asr_firered_asr[[engines.asr.firered_asr]]
  engines_asr_firered_asr --> core_config[core.config]
  engines_asr_firered_asr --> core_manifest[core.manifest]
  engines_asr_firered_asr --> engines_asr_asr[engines.asr.asr]
  engines_asr_firered_asr --> engines_asr_asr_spam[engines.asr.asr_spam]
  engines_asr_firered_asr --> engines_asr_fun_asr_nano[engines.asr.fun_asr_nano]
  engines_asr_firered_asr --> engines_separate[engines.separate]
  engines_asr_firered_asr --> engines_subs[engines.subs]
  engines_asr_firered_asr --> engines_text_junk[engines.text_junk]
  engines_asr_firered_asr --> engines_vram[engines.vram]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_roots` | 52 | 6 | `` |  |
| `_ensure_firered_importable` | 60 | 13 | `root` |  |
| `_parse_firered_result` | 75 | 17 | `result` | FireRedAsr2System.process → [{start,end,text}] — đã bỏ câu rác (text_junk.is_junk_text). |
| `_parse_firered_result_raw` | 94 | 45 | `result` | FireRedAsr2System.process → [{start,end,text}] (chưa lọc rác). |
| `_num_env` | 150 | 13 | `name, default` |  |
| `slice_cfg` | 165 | 10 | `` | FIRERED_SLICE_SEC=0 -> không chia (một lượt cả file). |
| `_is_pcm16_mono16k` | 177 | 7 | `info` |  |
| `_read_i16` | 186 | 7 | `info, f, start, count` |  |
| `find_cut_frame` | 195 | 53 | `info, f, target_sec, lo_sec, hi_sec, min_sil_sec, sil_db` | Điểm cắt (frame) trong [lo_sec, hi_sec] gần target_sec. |
| `plan_slices` | 250 | 44 | `wav_path, conf` | [{start,end,core0,core1,sil_left,sil_right}] theo FRAME. Lõi phủ kín [0,n) không chồng. |
| `describe_plan` | 296 | 10 | `plan, rate` |  |
| `transcribe_sliced` | 308 | 53 | `process_fn, wav, tmp_dir, conf, on_slice` | Chạy process_fn(path, uttid) -> dict FireRed trên từng slice; trả rows tuyệt đối. |
| `run_asr_firered` | 363 | 194 ⚠️ | `work_dir, device, force` |  |
| `main` | 559 | 8 | `argv` |  |

**Hàm dài ≥120 dòng:** `run_asr_firered` (194, L363)

### Config / env keys (6)

`FIRERED_MODELS`, `FIRERED_ROOT`, `FIRERED_USE_HALF`, `HF_HUB_DISABLE_SYMLINKS`, `HF_HUB_DISABLE_SYMLINKS_WARNING`, `PATH`

**File/artifact nhắc tới:** `asr.json`, `asr16k.wav`, `audio.wav`, `sub.zh.srt`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=5 · file_writes=2 · subprocess=1

### Lịch sử (từ docs/)

- **Fix logs (2):**
  - [Port V2→V5: preflight/chuẩn hoá video nguồn + extract_pcm bền + FireRed slice khoảng lặng + câu rác «None.» / ](../../fixes/2026-11-13-port-preflight-slice-junk.md)
  - [2026-10-06 — Đợt 4 review: tranh chấp ghi, một bản tiến trình, checkpoint an toàn](../../fixes/2026-10-06-batch4-write-races.md)
- **Reviews:** [_atoms_engines](../../reviews/_atoms_engines.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
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
