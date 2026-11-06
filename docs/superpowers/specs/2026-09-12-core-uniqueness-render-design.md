# Core Uniqueness Render (v1) — Design

Date: 2026-09-12  
Status: approved for planning (pending user review of this file)  
Scope: horizontal YouTube (16:9 / keep source AR) — **not** Shorts 9:16

## Goal

Make localized Bilibili AI-animation outputs harder to fingerprint as near-duplicates while staying visually tasteful: static edge crop, subtle Ken Burns+Drift motion, light color grade, and film grain — in one ffmpeg pass inside Pineline’s existing render path.

## Non-goals (v1)

- Shorts / 9:16 canvas
- Intro / outro
- Separate illustrative icons / lower-thirds beyond existing burn-in subs + OCR overlays
- True 2.5D depth maps / parallax layers
- Two-pass re-encode after `output.mp4`

## Decisions locked

| Topic | Choice |
|-------|--------|
| Format | Horizontal; `resolve_canvas` stays `source` \| `1080` |
| Motion | Ken Burns + Drift as **one** `zoompan` expression |
| Approach | Extend `build_video_filter` / `run_render` (single encode) |
| UI | Preset + light controls (defaults on) |
| LUT | Prefer `.cube` via `lut3d`; else `eq` only (no required `colorbalance` in v1) |
| Grain | Prefer `assets/overlays/grain.png` loop; else `noise`; strengths weak/medium/strong |
| Flip | After motion, before hardsub (existing order) |
| Audio | Default `voice_bgm` (dub + library BGM) or `voice_only`; **never** treat filters as legal fair use |

## Copyright-safe audio (not “fair use”)

Zoom/LUT/grain/BGM swap do **not** make re-uploading others’ anime “fair use.”  
Pineline’s safer default is technical:

1. Strip original / Demucs BGM (`voice_only` / `voice_bgm`)
2. Optionally mix **your** tracks from `assets/bgm/` (royalty-free / owned / licensed)
3. Visual uniqueness for fingerprinting — still your responsibility for rights to the video

Sample `sample_ambient.mp3` is procedural for pipeline tests only.


## Architecture

```
source video
  → scale to canvas (optional 1080)
  → base static zoom headroom (1.10 / 1.12 / 1.15)
  → zoompan: Ken Burns (z' *= ~1.0001) + Drift (sin X/Y) → W×H
  → flip (optional)
  → hardsub blur / watermark delogo / OCR / burn-in SRT / censor
  → LUT (lut3d or eq fallback)
  → grain (PNG overlay blend or noise)
  → format=yuv420p
  → mux voice_bgm (giọng + BGM thư viện) hoặc voice_only — không nhạc gốc
```

Primary code touch points:

- `render.py` — `build_video_filter`, `run_render`, helpers for motion/LUT/grain
- `server.py` — `MuxReq`, `_do_render`, optional `RunAllReq` defaults
- `index.html` — mux panel selects
- `assets/luts/` (optional `.cube`), `assets/overlays/grain.png` (optional)
- `pineline.config.json` / env — paths and eq fallback knobs

## Filter details

### Base zoom

User-facing: **10% / 12% / 15%** → factors `1.10` / `1.12` / `1.15`.  
Default: `1.12`.

Provides edge crop uniqueness and headroom for drift so pan does not reveal black borders.

### Ken Burns + Drift (single `zoompan`)

When `motion=on` (default):

- One `zoompan` combining slow zoom and sinusoidal crop window drift.
- Output size `s=WxH` from resolved canvas (never hardcode 1080x1920 in v1).
- Prefer source FPS for in/out (do not force 25 if source differs).
- Example shape (parameters illustrative; implement with real `W`,`H`, fps):

```text
zoompan=z='min(zoom*1.0001,zmax)':x='iw/2-(iw/zoom/2)+sin(on*K1)*A':y='ih/2-(ih/zoom/2)+sin(on*K2)*B':d=1:s=WxH:fps=SRC_FPS
```

Exact expression tuned so motion is near-invisible but changes pixels over time. Amplitude small (~1–2% of frame or few px scaled to `iw/zoom`).

When `motion=off`: keep current static `scale=W*z:H*z,crop=W:H` behavior only.

**Headroom rule:** if motion on and chosen zoom leaves insufficient margin for drift amplitude, either clamp amplitude or bump effective pre-scale slightly — prefer clamping amplitude first so UI zoom stays honest.

### LUT

1. If configured `.cube` exists and is readable → `lut3d=file=...` (path escaped for ffmpeg).
2. Else fallback:

```text
eq=contrast=1.05:brightness=0.02:saturation=1.08
```

If `lut3d` fails at runtime (bad file), fall back to `eq` and continue; do not fail the job. Log one line.

`lut=off` → skip both.

### Film grain

Preference:

1. If `assets/overlays/grain.png` (or config path) exists → loop as extra input, scale to canvas, blend over video.
2. Else → ffmpeg `noise` generator.

Strength:

| Level | Intent | Generator (`noise`) | PNG blend |
|-------|--------|---------------------|-----------|
| `off` | none | — | — |
| `weak` (default) | subtle | ~`allf=0.5` | overlay, low opacity |
| `medium` | visible but tasteful | ~`allf=1.0` | overlay, medium opacity |
| `strong` | aggressive uniqueness | ~`allf=1.5` | screen (or stronger opacity) |

Exact ffmpeg blend/opacity constants chosen at implement time to match the table intent; unit tests assert filter fragments per level.

### Flip

Unchanged semantics (`h` / `v` / `hv`). Applied **after** motion, **before** hardsub/OCR/subs so burned text is not mirrored.

### Subtitles / OCR / hardsub

Existing pipeline stays. Coordinates mapped with static base zoom (`_map_pt`); small drift may slightly misalign hardsub band — accepted in v1 (no per-frame remap).

LUT + grain apply **after** burn-in so subtitle pixels are also graded/grained.

## API / UI / config

### `MuxReq` / `run_render` knobs

| Field | Values | Default |
|-------|--------|---------|
| `zoom` | `1.10` \| `1.12` \| `1.15` (float ok) | `1.12` |
| `motion` | bool | `true` |
| `lut` | bool | `true` |
| `grain` | `off` \| `weak` \| `medium` \| `strong` | `weak` |
| `flip` | existing | `""` |
| `resolution` | existing | `source` |

CLI: expose the same flags on `render.py` for smoke tests.

Auto / 1-click pipeline: use the same defaults (no extra required UI on auto panel in v1; mux panel is enough).

### UI (mux panel)

- Zoom: select 10% / 12% / 15%
- Motion: checkbox Ken Burns+Drift (checked)
- LUT: checkbox (checked)
- Grain: select off / weak / medium / strong
- Existing: flip, resolution, audio mode, subs, fit

### Config / assets

- `assets/luts/` — optional; e.g. `default.cube` or path via `RENDER_LUT_FILE`
- `assets/overlays/grain.png` — optional; or `RENDER_GRAIN_FILE`
- Eq fallback constants overridable via env if useful (`RENDER_EQ_CONTRAST`, etc.) — optional nicety

Ship repo with README note under assets: drop-in files; without them fallbacks apply.

## Error handling

- Missing optional assets → silent fallback + one log line
- Bad LUT file → eq fallback
- `voice_only` without dub → existing error (unchanged)
- Motion/zoom invalid values → clamp to allowed set

## Testing

1. **Unit:** build filter string for combinations (motion on/off, lut file present/absent, grain levels) and assert expected substrings / input count for PNG grain.
2. **Smoke:** short job → `output.mp4` correct WxH, audio present in voice_only, manifest stores zoom/motion/lut/grain used.

## Out of scope follow-ups

- Shorts 9:16 canvas + center crop
- Intro/outro concat
- Icon packs / kinetic captions beyond current SRT
- 2.5D depth parallax
- Stronger per-frame hardsub remapping under drift

## Success criteria

- Default mux produces visibly mild uniqueness (crop + tiny motion + grade + grain) without looking “filtered to death”
- Each knob independently disableable
- One encode pass; no mandatory new binary deps beyond current ffmpeg
- Horizontal AR preserved
