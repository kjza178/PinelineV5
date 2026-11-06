# Core Uniqueness + Copyright-Safe Audio — Implementation Plan

> **For agentic workers:** Implement task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Ship visual uniqueness (zoom, Ken Burns+Drift, LUT, grain) plus copyright-safe audio (`voice_only` / `voice_bgm` with library tracks), backed by `assets/` samples.

**Architecture:** Single-pass ffmpeg in `render.py`. Optional assets under `assets/{luts,overlays,bgm}/`. New audio mode `voice_bgm` = dubbed voice + looped library BGM (never original/Demucs BGM). UI labels speak of “an toàn bản quyền / bỏ nhạc gốc”, not legal “fair use”.

**Tech Stack:** Python, ffmpeg 7.x, existing Pineline `render.py` / `server.py` / `index.html`.

## Global Constraints

- Horizontal only (no 9:16 in this plan)
- Do not claim fair use in UI/docs; claim strip original BGM + licensed/sample library
- Defaults: zoom 1.12, motion on, lut on, grain weak, audio `voice_bgm` if any `assets/bgm/*` else `voice_only`
- Missing assets → silent fallbacks (eq / noise / no BGM)

---

### Task 1: Assets tree + sample generator

**Files:**
- Create `assets/README.md`
- Create `assets/luts/`, `assets/overlays/`, `assets/bgm/`
- Create `scripts/gen_sample_assets.py` (ffmpeg + stdlib/PIL) writing:
  - `assets/overlays/grain.png`
  - `assets/luts/soft_contrast.cube`
  - `assets/bgm/sample_ambient.mp3` (procedural, labeled SAMPLE)

- [ ] Write generator script
- [ ] Run script; verify files exist
- [ ] README documents drop-in + license responsibility

### Task 2: Uniqueness video filters

**Files:** `render.py`

- [ ] Add helpers: resolve LUT path, grain path, motion zoompan, eq fallback, grain filter
- [ ] Extend `build_video_filter` / `run_render` with `zoom`, `motion`, `lut`, `grain`
- [ ] Unit-style asserts on filter strings

### Task 3: `voice_bgm` audio mode

**Files:** `render.py`, `server.py`, `index.html`

- [ ] `_build_audio_filter`: `voice_bgm` → dub + looped pick from `assets/bgm/` (or `RENDER_BGM_FILE`), volume duck under voice
- [ ] MuxReq + UI: audio modes include `voice_bgm`; uniqueness controls
- [ ] Prefer `voice_bgm` when library non-empty else `voice_only`

### Task 4: Spec touch-up

**Files:** `docs/superpowers/specs/2026-09-12-core-uniqueness-render-design.md`

- [ ] Add copyright-safe audio / library BGM; remove “Audio unchanged”
- [ ] Explicit: transforms ≠ fair use

### Done when

- Sample assets generated
- Filter builder smoke passes
- Mux UI exposes uniqueness + `voice_bgm`
