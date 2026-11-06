# -*- coding: utf-8 -*-
"""One-shot builder: merge atom partials + spine into func-catalog."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "2026-11-06-v5-func-catalog.md"

COUNTS = {
    "core+server": 279,
    "engines": 538,
    "http+agents": 567,
    "tools+ui": 734,
}
TOTAL = sum(COUNTS.values())  # 2118

SPINE = r'''## 1. Spine gọi từng hàm

Happy path **queue** (UI/API xếp hàng → worker → mux → artifacts). Không đi nhánh HOLD/QA-block (ghi chú nhánh phụ). Nguồn: AST/read `server.py`, `core/job_queue.py`, `engines/{download,asr,translate,clone_tts,assemble,mux,render,split_parts,separate,ocr}.py`.

Ghi chú: `_auto_pipeline` là đường **1-click / run-all** (submit GPU sau download). **Queue happy path** gọi thẳng `_auto_gpu` từ `_queue_run_one` (không qua `_auto_pipeline`).

### 1.0 CALL ORDER (tóm tắt)

```
create_job → expand_meta → _create
  → api_queue_jobs_add → batch_config.resolve_job_opts → job_queue.queue_add
  → _ensure_worker_unlocked → _worker_loop → _runner=_queue_run_one
  → _heal_stale_running → is_wired_done? → resolve_job_opts → stamp queue_opts
  → _resolve_queue_voice → _claim_stage(__all__) → _find_video?
       → download_video (nếu thiếu) → source.* + manifest.download
  → maybe_auto_split? (nếu dài → queue_add parts + return "split")
  → _gpu.submit(_auto_gpu)
       → free_gpu_vram → _resolve_asr_engine → _run_engine(ASR script)
            → (subprocess) run_asr_* → asr.json + audio.wav + sub.zh.srt
       → _run_translate_engine → (subprocess) run_translate → script.json + glossary.json + sub.vi.srt
       → count_script_missing → (fill) _run_translate_engine(batch=25)
       → [HOLD?] return | [_run_requested_review?] | [run_qa_gate?]
       → _save_series_glossary → _resolve_voice/speed/tts_engine
       → _do_tts → run_clone_tts → tts/seg_*.wav + tts.json
       → [demucs?] run_separate → no_vocals.wav
       → [ocr?] run_ocr → ocr.json
       → _do_render → assemble(_fit) → run_render → output.mp4
  → try_auto_merge_parent? → auto_publisher.publish_job?
  → return "done"
```

### 1.1 Tạo job

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 1 | `server.py:1997` | `create_job(job: NewJob)` | `expand_meta(url, cookies…)` → loop `_create(url, target, cookies, group?)` | — (delegate) |
| 2 | `engines/playlist.py:53` | `expand_meta(url, …)` | yt-dlp playlist probe | — (meta in-memory) |
| 3 | `engines/download.py:252` | `job_id_from_url(url)` (via `_create`) | hashlib | — |
| 4 | `server.py:1882` | `_create(url, target, cookies_from_browser, group=None)` | `Manifest.save()` | `work/<job_id>/` mkdir; **`manifest.json`** (`request.url/target/cookies/group_*`) |

Local import (song song, không URL): `_create_local_shell` → `_place_source` → `_finalize_imported_source` → `source.*` + `meta.json` + `stages.download=done`.

### 1.2 Xếp hàng

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 5 | `server.py:2201` | `api_queue_jobs_add(req: JobQueueReq)` | `batch_config.resolve_job_opts(…)` → `job_queue.queue_add(ids, opts, skip_done)` | — |
| 6 | `core/batch_config.py:141` | `resolve_job_opts(opts, …)` | `load()` + merge layers | — (in-memory opts) |
| 7 | `core/job_queue.py:350` | `queue_add(job_ids, opts, skip_done=True, sort_first=True)` | `is_wired_done(wd)`; `job_sort_key`; `_save()`; `_ensure_worker_unlocked()` | **`work/.job_queue.json`** (`queue`, `opts`, `opts_by_job`, `current`) |
| 8 | `core/job_queue.py:154` | `is_wired_done(work_dir)` | read manifest + `output.mp4` size; stages in `WIRED` all `done` | — |
| 9 | `core/job_queue.py:171` | `_save()` | atomic json | **`work/.job_queue.json`** |
| 10 | `core/job_queue.py:572` | `_ensure_worker_unlocked()` | `Thread(target=_worker_loop)` | — |

Wire tại import: `server.py:5784` `job_queue.set_runner(_queue_run_one)`.

### 1.3 Worker → runner

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 11 | `core/job_queue.py:588` | `_worker_loop()` | pop `_q`; `_clear_stop_hook?`; `_save()`; `_runner(job_id, opts)` → `_hist_push` | **`.job_queue.json`** (current); history RAM |
| 12 | `core/job_queue.py:216` | `_hist_push(job_id, status, detail)` | ring buffer | — |

### 1.4 `_queue_run_one` (orchestrator)

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 13 | `server.py:3737` | `_queue_run_one(job_id, opts)` | (bảng dưới) | nhiều (qua helpers) |
| 14 | `server.py:309` | `_heal_stale_running(work_dir)` | kill orphan engines; reset `stages.*.status=running→pending` | **`manifest.json`** |
| 15 | `core/batch_config.py:141` | `resolve_job_opts(opts, fill_voice=False)` | — | — |
| 16 | `server.py:2839/2844/2848` | `_save_tts_voice/_speed/_engine(work_dir, …)` | Manifest stage tts / sidecar | **`manifest.json`**; often **`tts_config.json`** |
| 17 | `server.py:3098` | `_resolve_asr_engine(work_dir, asr_engine)` | `_save_asr_engine` | **`manifest.json` stages.asr** |
| 18 | `server.py:3033` | `_save_asr_engine(work_dir, engine)` | `_promote_asr_source?` / `_patch_asr_fields` | **`manifest.json`**; maybe promote **`asr.json`** |
| 19 | `core/manifest.py` | `Manifest.save()` / stamp `queue_opts` | — | **`manifest.json`** (`queue_opts` full snapshot) |
| 20 | `server.py:2931` | `_resolve_queue_voice(work_dir, voice)` | list clone voices | — |
| 21 | `server.py:162` | `_job_any_busy(job_id)` | `_STAGE_BUSY` set | — |
| 22 | `server.py:217` | `_manifest_running(work_dir)` | scan stages status | — |
| 23 | `server.py:171` | `_claim_stage(job_id, "__all__")` | `_STAGE_BUSY` | — (RAM) |
| 24 | `server.py:380` | `_next_incomplete_stage(work_dir)` | — | — |
| 25 | Manifest | `mark_running(early)` | — | **`manifest.json`** |
| 26 | `server.py:4906` | `_find_video(work_dir)` | manifest `video_path` / glob `source.*` | — |

### 1.5 Download (nếu chưa có video)

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 27 | `engines/download.py:305` | `download_video(url, work_dir, cookies_from_browser=…)` | `normalize_url`, `detect_platform`, `find_cookie_file`, `apply_speed_opts`, `_probe_duration`, `_auto_height_for_duration`, yt-dlp(+aria2c), Manifest mark | **`source.%(ext)s`**, **`source.info.json`**, thumbnail; **`manifest.json` stages.download=done** (`video_path`, title…) |
| 28 | helpers | `_format_sel`, `_cfg_max_height`, `_cfg_prefer_hevc`, `_clean_incomplete_fragments`, `_delete_sources` (fresh) | — | mảnh `.part` / clean |

### 1.6 Auto-split (optional, phim dài)

Happy path **không split** nếu `< auto_split_min_h`. Nếu split:

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 29 | `server.py:80` | `_maybe_auto_split_guarded(job_id, …)` | `maybe_auto_split_job` | lock RAM |
| 30 | `engines/split_parts.py:688` | `maybe_auto_split_job(…)` | `probe_duration` → `split_job_to_subjobs` | parent **`manifest.split_info`** |
| 31 | `engines/split_parts.py:412` | `split_job_to_subjobs(job_id, …)` | `compute_smart_plan` → `split_video_to_parts` → create sub jobs | **`work/<parent>_pNN/`** + part videos; parent/sub **`manifest.json`** |
| 32 | `core/job_queue.py:350` | `queue_add(sub_ids, opts, …)` | (as above) | **`.job_queue.json`** |
| — | `_queue_run_one` | return `"split"` | parent stages → pending “Chờ N part…” | **`manifest.json`** |

### 1.7 Submit GPU → `_auto_gpu`

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 33 | `_gpu.submit(_gpu_job)` | thread pool | `_auto_gpu(…)` then `_release_stage` | — |
| 34 | `server.py:1413` | `_auto_gpu(job_id, target, audio_mode, voice_vol, orig_vol, use_ocr, fit, resolution, translate_mode, render_kw, asr_engine)` | full stage chain below | stage artifacts |

Alt path (không phải queue): `server.py:1254` `_auto_pipeline` = download + optional split + `_gpu.submit(_auto_gpu)` (claim `__all__` tới khi GPU xong).

### 1.8 ASR

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 35 | `engines/vram.py:56` | `free_gpu_vram("trước ASR…")` | torch empty / GC | — |
| 36 | `server.py:3098` | `_resolve_asr_engine(wd, asr_engine)` | (again) | **`manifest.json`** |
| 37 | `server.py:2996` | `_asr_script(engine)` | map `ASR_SCRIPTS` | — |
| 38 | `server.py:390` | `_run_engine(script, wd)` | `_kill_job_engine_procs`; `subprocess.Popen([python, script, work_dir])` | engine writes; server streams logs |
| 39a | default map | e.g. `engines/asr/fun_asr_nano.py` / `nano_fa_asr.py` / `firered_asr.py` / `paraformer_zh.py` / `sensevoice_asr.py` / `hybrid_asr.py` | each `run_asr_*` / `main` | typically **`audio.wav`**, sidecar `asr.*.json`, promote **`asr.json`**, **`sub.zh.srt`**, **`manifest.stages.asr=done`** |
| 39b | `engines/asr/asr.py:247` | `run_asr(work_dir, …)` (Whisper path if used) | `resolve_asr_source` → `ensure_audio_wav` → `extract_audio` → Whisper → `to_srt` | **`audio.wav`**, **`asr.json`**, **`sub.zh.srt`**, manifest |

Common ASR helpers on happy path: `resolve_asr_source` → `ensure_audio_wav` → (`extract_audio` ffmpeg) → model generate → Manifest `mark_done`.

### 1.9 Translate (+ fill)

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 40 | `server.py:3063` | `_run_translate_engine(wd, target=…, mode=…)` | `_run_engine("engines/translate.py", …)` | via subprocess |
| 41 | `engines/translate.py:1989` | `run_translate(work_dir, batch, target, force, model, mode)` | LLM batches; glossary; optional preset_switcher | **`script.json`**, **`glossary.json`**, **`sub.vi.srt`**, **`manifest.stages.translate`** |
| 42 | `engines/translate.py:1894` | `count_script_missing(wd)` | read `script.json` | — |
| 43 | fill | `_run_translate_engine(wd, batch=25, mode="batch")` | same | update **`script.json`** |

### 1.10 Gates trước TTS (happy = pass-through)

| # | `file:line` | `func(args)` | calls | writes / branch |
|---|---|---|---|---|
| 44 | HOLD | if `agent.hold_after_translate` | Manifest update | **`manifest.json`** HOLD; **return** (không TTS) |
| 45 | `server.py:1341` | `_run_requested_review(wd, target)` | `run_name_pass`, `run_pronoun_pass`, `run_review` | may rewrite **`script.json`**; `script.pre_agent_review.json` |
| 46 | `agents/agent_qa_gate.py:123` | `run_qa_gate(wd, run_review_fn, target)` | `snapshot_pre_review` → review → `review_diff` → `evaluate_qa_gate` | **`script.pre_review.json`**; may rewrite **`script.json`**; if fail **return** |
| 47 | `server.py:1402` | `_save_series_glossary(wd)` | `series_glossary.save_from` | series glossary store |

### 1.11 TTS

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 48 | `server.py:2906` | `_resolve_voice(wd, None)` | manifest / queue_opts / voices | — |
| 49 | `server.py:2955` | `_resolve_speed(wd, None)` | — | — |
| 50 | `server.py:3110` | `_resolve_tts_engine(wd, None)` | tts_config / queue_opts | may **`tts_config.json`** |
| 51 | `engines/vram.py:56` | `free_gpu_vram("trước TTS")` | — | — |
| 52 | `server.py:3135` | `_do_tts(wd, voice, speed, engine, force=False)` | `_patch_tts_fields` → `run_clone_tts` | manifest tts cur_text |
| 53 | `engines/clone_tts.py:462` | `run_clone_tts(work_dir, engine, voice, speed, force)` | voice refs; worker venv; resume scan | **`tts/seg_XXXX.wav`**, **`tts.json`**, **`manifest.stages.tts`** |
| 54 | refill | if `n_missing` → `_do_tts` again | same | fill missing segs |

### 1.12 Separate / OCR (opts)

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 55 | `engines/separate.py:194` | `run_separate(wd)` if `audio_mode in demucs_*` | demucs | **`no_vocals.wav`** (+ vocals); **`manifest.stages.separate`** |
| 56 | `engines/ocr.py:128` | `run_ocr(wd)` if `use_ocr` | OCR engine | **`ocr.json`**; **`manifest.stages.ocr`** |

### 1.13 Assemble + Render (mux stage)

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 57 | `server.py:3151` | `_do_render(wd, force=False, audio_mode, voice_vol, orig_vol, fit, resolution, …)` | optional `run_separate`; `assemble`/`assemble_fit`; `engines.render.run_render` | see below |
| 58 | `engines/assemble.py:238` | `assemble(wd)` (short / fit=False) | `_load_clips`, `_read_mono` | **`dub_tts.wav`** (if ≤ NAIVE_MAX_SEC) |
| 59 | `engines/assemble.py:284` | `assemble_fit(wd)` (default / long) | `compute_fit_placements`, write wav | **`dub_fit.wav`**, **`tts_fit.json`** / fit stamp |
| 60 | `engines/render.py:2518` | `run_render(work_dir, …)` | `_find_video`; `ensure_job_audio_ts`; `write_fit_timings`; subs (`sub.vi.srt` / display); ffmpeg filtergraph (hardsub/blur/brand/lut/grain…) | **`output.mp4`**, updated **`sub.vi.srt`**, **`script.display.json`**, **`manifest.stages.mux=done`** (`output_path`) |

Note: `engines/mux.py:72` `run_mux` = simple ffmpeg A/V mux (copy video); **queue 1-click dùng `run_render` qua `_do_render`**, không gọi `run_mux` trực tiếp.

### 1.14 Artifacts sau done

| # | `file:line` | `func(args)` | calls | writes |
|---|---|---|---|---|
| 61 | `core/job_queue.py:154` | `is_wired_done(wd)` | check mux+wired stages + `output.mp4` | — |
| 62 | `engines/split_parts.py:792` | `try_auto_merge_parent(job_id, …)` (nếu part) | `merge_job_parts` → `merge_parts_to_full` | parent **`output.mp4` / `output_full.mp4`**, **`split_info.status=merged`** |
| 63 | `agents/auto_publisher.py` | `publish_job(job_id)` (daemon thread) | uploader / Canva paths | upload side-effects (outside work/) |
| 64 | `_queue_run_one` | return `("done", "hoàn tất")` | `_hist_push` via worker | **`.job_queue.json`** clear current |

### 1.15 Artifact checklist (job thường, không split)

| File | Stage ghi chính |
|---|---|
| `manifest.json` | mọi stage |
| `source.*` (+ `source.info.json`) | download |
| `audio.wav` | ASR |
| `asr.json` (+ sidecars) | ASR |
| `sub.zh.srt` | ASR |
| `script.json` / `glossary.json` / `sub.vi.srt` | translate |
| `tts/seg_*.wav` / `tts.json` | TTS |
| `no_vocals.wav` | separate (opt) |
| `ocr.json` | OCR (opt) |
| `dub_fit.wav` / `tts_fit.json` | assemble |
| `output.mp4` | render/mux |

'''

NAV = r'''## 6. How to navigate — muốn hiểu X thì mở Y

| Muốn hiểu… | Mở |
|---|---|
| Toàn bộ hàm theo file (core/server) | [§2 core + server](#2-coreserverpy--per-function) |
| Toàn bộ hàm engines | [§3 engines](#3-engines--per-function) |
| HTTP routes + agents + pineline.server.routes | [§4 http / agents](#4-httproutes--agents--pinelineserverroutes) |
| tools / desktop / restart + UI JS | [§5 tools + UI](#5-tools--desktop--ui-js) |
| **Thứ tự gọi thật khi chạy 1 job** | [§1 Spine](#1-spine-gọi-từng-hàm) |
| Tạo job từ URL | `server.create_job` → `_create` → `engines.download.job_id_from_url` |
| Hàng chờ persist | `core/job_queue.py` (`queue_add`, `_worker_loop`, `_save`) |
| Orchestrator queue | `server._queue_run_one` |
| 1-click không qua queue | `server._auto_pipeline` → `_auto_gpu` |
| GPU stage chain | `server._auto_gpu` |
| Download | `engines/download.py` `download_video` |
| ASR engine map | `server.ASR_SCRIPTS` / `_asr_script` / `_run_engine` |
| Dịch | `engines/translate.py` `run_translate` (spawn qua `_run_translate_engine`) |
| TTS | `server._do_tts` → `engines/clone_tts.run_clone_tts` |
| Ghép giọng | `engines/assemble.py` `assemble` / `assemble_fit` |
| Render cuối | `server._do_render` → `engines/render.run_render` (không phải `mux.run_mux`) |
| Chia/ghép part dài | `engines/split_parts.py` (`maybe_auto_split_job`, `try_auto_merge_parent`) |
| HOLD / QA trước TTS | `server._auto_gpu` + `agents/agent_qa_gate.py` |
| Atom map (file → I/O → next) | [2026-11-06-v5-part-atoms.md](./2026-11-06-v5-part-atoms.md) |
| Layout thư mục / ports | `docs/LAYOUT.md`, `docs/ARCHITECTURE.md` |
| Contract manifest | `docs/MANIFEST_CONTRACT.md` |

'''

HEADER = f'''# V5 function catalog — definitive per-function map

- **Date:** 2026-11-06
- **Root:** `Z:\\PinelineV5`
- **Nguồn:** merge AST partials `_atoms_*.md` + spine đọc live code
- **Scope:** module-level defs + class methods (nested skipped); UI = unique JS names (cap 200/`index3.html`)

## Stats

| Bucket | Functions |
|---|---:|
| core/ + `server.py` | {COUNTS["core+server"]} |
| `engines/**` | {COUNTS["engines"]} |
| http_routes + agents + pineline.server.routes | {COUNTS["http+agents"]} |
| tools + desktop/restart + static UI JS | {COUNTS["tools+ui"]} |
| **TOTAL** | **{TOTAL}** |

Sum check: {COUNTS["core+server"]}+{COUNTS["engines"]}+{COUNTS["http+agents"]}+{COUNTS["tools+ui"]} = **{TOTAL}**.

## Mục lục

1. [Spine gọi từng hàm](#1-spine-gọi-từng-hàm)
2. [core/ + server.py — per-function](#2-coreserverpy--per-function)
3. [engines — per-function](#3-engines--per-function)
4. [http_routes / agents / pineline.server.routes](#4-httproutes--agents--pinelineserverroutes)
5. [tools / desktop / UI JS](#5-tools--desktop--ui-js)
6. [How to navigate](#6-how-to-navigate--muốn-hiểu-x-thì-mở-y)

---

'''


def strip_leading_h1(text: str) -> str:
    lines = text.splitlines()
    # drop a top-level title if present; keep ## content
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    core = (ROOT / "_atoms_core_server.md").read_text(encoding="utf-8")
    eng = (ROOT / "_atoms_engines.md").read_text(encoding="utf-8")
    http = (ROOT / "_atoms_http_agents.md").read_text(encoding="utf-8")
    tools = (ROOT / "_atoms_tools_ui.md").read_text(encoding="utf-8")

    # Normalize section headers for TOC anchors
    sec2 = "## 2. core/+server.py — per-function\n\n" + strip_leading_h1(core)
    # core file starts with "## core/ + server.py" — demote to ###
    sec2 = sec2.replace("## core/ + server.py", "### core/ + server.py (atoms)", 1)

    sec3 = "## 3. engines — per-function\n\n" + strip_leading_h1(eng)
    sec3 = sec3.replace("# Engines atoms (AST)", "### Engines atoms (AST)", 1)

    sec4 = "## 4. http_routes / agents / pineline.server.routes\n\n" + strip_leading_h1(http)
    sec4 = sec4.replace(
        "# Atoms: http_routes / agents / pineline.server.routes",
        "### Atoms: http_routes / agents / pineline.server.routes",
        1,
    )

    sec5 = "## 5. tools / desktop / UI JS\n\n" + strip_leading_h1(tools)
    sec5 = sec5.replace(
        "# Atoms: tools / desktop / restart + static UI JS",
        "### Atoms: tools / desktop / restart + static UI JS",
        1,
    )

    body = "\n".join(
        [
            HEADER.rstrip(),
            "",
            SPINE.rstrip(),
            "",
            "---",
            "",
            sec2.rstrip(),
            "",
            "---",
            "",
            sec3.rstrip(),
            "",
            "---",
            "",
            sec4.rstrip(),
            "",
            "---",
            "",
            sec5.rstrip(),
            "",
            "---",
            "",
            NAV.rstrip(),
            "",
        ]
    )
    OUT.write_text(body, encoding="utf-8")
    nlines = body.count("\n") + 1
    print(f"Wrote {OUT} lines={nlines} total_funcs={TOTAL} bytes={OUT.stat().st_size}")


if __name__ == "__main__":
    main()
