# `engines.media_ts`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `engines/media_ts.py` · **Lớp:** `render` · **304 dòng** (265 code) · **14 hàm**, **0 class** · sha1 `f415ad9e96`

> Mốc thời gian tiếng của file nguồn — sửa tiếng "dồn mẫu" ở file ghép nhiều tập. File ghép copy nhiều tập AAC giữ lại 1024 mẫu mồi (priming) đầu mỗi tập: gói đó có mốc gần như trùng gói trước (stts ~0) nhưng vẫn chứa 23 m

### Phụ thuộc

- **Gọi tới (import nội bộ):** [engines.assemble](./engines.assemble.md)
- **Được dùng bởi:** [agents.agent_av_sync](./agents.agent_av_sync.md), [engines.asr.asr](./engines.asr.asr.md), [engines.mux](./engines.mux.md), [engines.render](./engines.render.md), [engines.separate](./engines.separate.md), [engines.sfx_lib](./engines.sfx_lib.md), [render](./render.md), [scripts.check_batch1](./scripts.check_batch1.md)
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [restart_server](./restart_server.md)
- **Test:** ❌ chưa có test import trực tiếp

```mermaid
flowchart LR
  engines_media_ts[[engines.media_ts]]
  agents_agent_av_sync[agents.agent_av_sync] --> engines_media_ts
  engines_asr_asr[engines.asr.asr] --> engines_media_ts
  engines_mux[engines.mux] --> engines_media_ts
  engines_render[engines.render] --> engines_media_ts
  engines_separate[engines.separate] --> engines_media_ts
  engines_sfx_lib[engines.sfx_lib] --> engines_media_ts
  render[render] --> engines_media_ts
  scripts_check_batch1[scripts.check_batch1] --> engines_media_ts
  engines_media_ts --> engines_assemble[engines.assemble]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_boxes` | 32 | 15 | `f, start, end` |  |
| `_child` | 49 | 2 | `f, s, e, name` |  |
| `mp4_track_stts` | 53 | 37 | `video, kind` | (timescale, [(count, delta)]) của track đầu tiên loại `kind` (soun/vide). |
| `audio_drift_points` | 92 | 25 | `video` | Trục 'dồn mẫu' → trục mốc: (vị trí theo mẫu [s], tiếng dư tích luỹ tới đó [s]). |
| `audio_ts_drift` | 119 | 4 | `video` | Tổng tiếng dư so với mốc (s). 0 nếu không đọc được. |
| `make_retime` | 125 | 11 | `video` | Hàm t(trục dồn mẫu) → t(trục hình). None nếu lệch không đáng kể. |
| `_probe_dur` | 138 | 7 | `p` |  |
| `_retime_srt` | 147 | 9 | `text, f` |  |
| `ensure_job_audio_ts` | 158 | 69 | `work_dir, video` | Job đã ASR trên audio dồn mẫu → dời mốc về trục hình + ghép lại dub_fit. |
| `_tmp_of` | 229 | 2 | `p` |  |
| `_backup_once` | 233 | 4 | `p, bak` | Không bao giờ đè backup đã có — bản trong _pre_audio_ts luôn là bản gốc trước lần dời đầu. |
| `_atomic_write` | 239 | 4 | `p, text` |  |
| `_commit_retime` | 245 | 32 | `work_dir, info` | Pha thay file — chạy lại an toàn: mỗi bước kiểm tra trạng thái trước khi làm. |
| `main` | 279 | 22 | `argv` |  |

**File/artifact nhắc tới:** `.audio_ts_fixed.json`, `.audio_ts_pending.json`, `asr.json`, `audio.ts.wav`, `audio.wav`, `manifest.json`, `mixed_audio.partial.wav`, `mixed_audio.wav`, `no_vocals.wav`, `orig_audio.wav`, `script.display.json`, `script.json`, `script.pre_review.json`, `sub.vi.burn.srt`, `sub.vi.srt`, `sub.zh.srt`, `tts.json`, `vocals.wav`

**Tín hiệu rủi ro (đếm tĩnh):** file_writes=3 · subprocess=2

### Lịch sử (từ docs/)

- **Fix logs (3):**
  - [Phim dài ~12h lệch khung sub — nguyên nhân + split_parts](../../fixes/2026-11-02-longfilm-sub-drift-split.md)
  - [2026-10-06 — Đợt 4 review: tranh chấp ghi, một bản tiến trình, checkpoint an toàn](../../fixes/2026-10-06-batch4-write-races.md)
  - [Đợt 1 — chặn mất dữ liệu (review 6/10)](../../fixes/2026-10-06-batch1-data-loss.md)
- **Reviews:** [_atoms_engines](../../reviews/_atoms_engines.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
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
