# `engines.media_ts`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-17 19:05. Đừng sửa tay khối này. -->
**File:** `engines/media_ts.py` · **Lớp:** `render` · **1019 dòng** (893 code) · **32 hàm**, **0 class** · sha1 `a5fe611c3f`

> Mốc thời gian tiếng của file nguồn — sửa tiếng "dồn mẫu" ở file ghép nhiều tập. File ghép copy nhiều tập AAC giữ lại 1024 mẫu mồi (priming) đầu mỗi tập: gói đó có mốc gần như trùng gói trước (stts ~0) nhưng vẫn chứa 23 m

### Phụ thuộc

- **Gọi tới (import nội bộ):** [core.config](./core.config.md), [engines.assemble](./engines.assemble.md)
- **Được dùng bởi:** [agents.agent_av_sync](./agents.agent_av_sync.md), [engines.asr.asr](./engines.asr.asr.md), [engines.mux](./engines.mux.md), [engines.render](./engines.render.md), [engines.separate](./engines.separate.md), [engines.sfx_lib](./engines.sfx_lib.md), [engines.source_preflight](./engines.source_preflight.md), [scripts.check_batch1](./scripts.check_batch1.md)
- **Được nhắc tên file `.py` (subprocess/script) bởi:** [restart_server](./restart_server.md)
- **Test:** `tests/test_extract_pcm_robust.py`, `tests/test_extract_pcm_timing.py`, `tests/test_video_preflight.py`

```mermaid
flowchart LR
  engines_media_ts[[engines.media_ts]]
  agents_agent_av_sync[agents.agent_av_sync] --> engines_media_ts
  engines_asr_asr[engines.asr.asr] --> engines_media_ts
  engines_mux[engines.mux] --> engines_media_ts
  engines_render[engines.render] --> engines_media_ts
  engines_separate[engines.separate] --> engines_media_ts
  engines_sfx_lib[engines.sfx_lib] --> engines_media_ts
  engines_source_preflight[engines.source_preflight] --> engines_media_ts
  scripts_check_batch1[scripts.check_batch1] --> engines_media_ts
  engines_media_ts --> core_config[core.config]
  engines_media_ts --> engines_assemble[engines.assemble]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `_decode_errors` | 63 | 11 | `stderr` | Số dòng lỗi GIẢI MÃ (không tính cảnh báo mốc dts/pts của muxer). |
| `_dead_zero_run` | 76 | 39 | `wav, min_sec, tail_only` | Mốc (s) bắt đầu đoạn mẫu = 0 tuyệt đối dài ≥ min_sec, SAU khi đã có tiếng. |
| `_full_tol_sec` | 117 | 14 | `` | EXTRACT_FULL_TOL_SEC (env / pineline.config.json), mặc định 1.0 s. |
| `_ffprobe_duration` | 133 | 10 | `path` |  |
| `_ffprobe_audio_duration` | 145 | 11 | `path` | Độ dài khai báo của luồng tiếng đầu tiên (s); 0 nếu không đọc được. |
| `_ffmpeg_pcm_cmd` | 158 | 28 | `src, out, ac, ar, af, ss, t, rf64, pre_in` |  |
| `_write_silence_wav` | 188 | 11 | `out, dur, ac, ar, rf64` |  |
| `_write_silence_frames` | 201 | 16 | `out, n_frames, ac, ar, rf64` | Im lặng ĐÚNG n_frames mẫu (pcm_s16le). wave lỗi → lavfi (độ chính xác ms). |
| `_force_wav_frames` | 219 | 51 | `wav, n_frames, ac, ar, rf64` | Ép wav về ĐÚNG n_frames mẫu: thừa → cắt đuôi, thiếu → đệm im lặng ở đuôi. |
| `_fit_wav_to_duration` | 272 | 29 | `wav, target_sec, ac, ar, rf64` | Cắt/pad PCM về đúng target_sec (tránh async từng khúc làm wav dài hơn hình). |
| `_concat_wav_parts` | 303 | 23 | `parts, out, rf64` |  |
| `_extract_window` | 328 | 37 | `src, out, ss, t, ac, ar, af, rf64, dead_check, pre_in` | Trích [ss, ss+t). Trả duration thực; 0 nếu thất bại/rỗng. Số dòng lỗi giải mã → _LAST_WIN. |
| `_has_zero_run` | 370 | 27 | `wav, min_sec` | Có đoạn mẫu 0 tuyệt đối ≥ min_sec ở bất kỳ đâu (kể cả đầu khúc / cả khúc). |
| `_zero_tail_sec` | 399 | 22 | `wav` | Độ dài (s) đoạn mẫu 0 tuyệt đối ở ĐUÔI file (cả file 0 → cả độ dài). Đọc ngược theo khối. |
| `_nonzero_frac` | 423 | 17 | `wav` | Tỉ lệ khối 10 ms có mẫu khác 0 (đo "còn tiếng" để chọn bản trích tốt hơn). |
| `_audio_seek_source` | 442 | 39 | `src, tmp` | Copy luồng tiếng ra file chỉ-tiếng để seek theo GÓI TIẾNG (không theo keyframe hình). |
| `_extract_pcm_chunked` | 483 | 128 ⚠️ | `src, out, start, end, ac, ar, af, rf64, chunk_sec, head, seek_src, …` | Ghép head (optional) + các khúc [start, end); chỗ AAC chết → silence cùng độ dài. |
| `extract_pcm_from_video` | 613 | 133 ⚠️ | `src, out, ac, ar, af, rf64, chunk_sec` | Tách PCM từ video. Full-file trước; AAC rematrix/hỏng → salvage + chunk + silence. |
| `_boxes` | 748 | 15 | `f, start, end` |  |
| `_child` | 765 | 2 | `f, s, e, name` |  |
| `mp4_track_stts` | 769 | 37 | `video, kind` | (timescale, [(count, delta)]) của track đầu tiên loại `kind` (soun/vide). |
| `audio_drift_points` | 808 | 25 | `video` | Trục 'dồn mẫu' → trục mốc: (vị trí theo mẫu [s], tiếng dư tích luỹ tới đó [s]). |
| `audio_ts_drift` | 835 | 4 | `video` | Tổng tiếng dư so với mốc (s). 0 nếu không đọc được. |
| `make_retime` | 841 | 11 | `video` | Hàm t(trục dồn mẫu) → t(trục hình). None nếu lệch không đáng kể. |
| `_probe_dur` | 854 | 7 | `p` |  |
| `_retime_srt` | 863 | 9 | `text, f` |  |
| `ensure_job_audio_ts` | 874 | 68 | `work_dir, video` | Job đã ASR trên audio dồn mẫu → dời mốc về trục hình + ghép lại dub_fit. |
| `_tmp_of` | 944 | 2 | `p` |  |
| `_backup_once` | 948 | 4 | `p, bak` | Không bao giờ đè backup đã có — bản trong _pre_audio_ts luôn là bản gốc trước lần dời đầu. |
| `_atomic_write` | 954 | 4 | `p, text` |  |
| `_commit_retime` | 960 | 32 | `work_dir, info` | Pha thay file — chạy lại an toàn: mỗi bước kiểm tra trạng thái trước khi làm. |
| `main` | 994 | 22 | `argv` |  |

**Hàm dài ≥120 dòng:** `extract_pcm_from_video` (133, L613), `_extract_pcm_chunked` (128, L483)

**File/artifact nhắc tới:** `.alt.wav`, `.audio_ts_fixed.json`, `.audio_ts_pending.json`, `.concat.txt`, `asr.json`, `audio.ts.wav`, `audio.wav`, `audio_seek.m4a`, `head.wav`, `manifest.json`, `mixed_audio.partial.wav`, `mixed_audio.wav`, `no_vocals.wav`, `orig_audio.wav`, `script.display.json`, `script.json`, `script.pre_review.json`, `sub.vi.burn.srt`, `sub.vi.srt`, `sub.zh.srt`, `tts.json`, `vocals.wav`

**Tín hiệu rủi ro (đếm tĩnh):** broad_except=1 · file_writes=4 · subprocess=12

### Lịch sử (từ docs/)

- **Fix logs (4):**
  - [Port V2→V5: preflight/chuẩn hoá video nguồn + extract_pcm bền + FireRed slice khoảng lặng + câu rác «None.» / ](../../fixes/2026-11-13-port-preflight-slice-junk.md)
  - [Phim dài ~12h lệch khung sub — nguyên nhân + split_parts](../../fixes/2026-11-02-longfilm-sub-drift-split.md)
  - [2026-10-06 — Đợt 4 review: tranh chấp ghi, một bản tiến trình, checkpoint an toàn](../../fixes/2026-10-06-batch4-write-races.md)
  - [Đợt 1 — chặn mất dữ liệu (review 6/10)](../../fixes/2026-10-06-batch1-data-loss.md)
- **Reviews:** [_atoms_engines](../../reviews/_atoms_engines.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md), [2026-10-06-code-review](../../reviews/2026-10-06-code-review.md)
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
