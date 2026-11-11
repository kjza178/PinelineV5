---
name: pineline-agent
description: >-
  Manage Pineline (Z:\Pineline) video rebuild jobs via Agent V2 CLI/API —
  status, queue, YouTube draft. Use when user asks about Pineline jobs,
  hàng chờ, mux/ASR/TTS status, or YT pack from a job.
---

# Pineline Agent V2

Pineline = local FastAPI app at **http://127.0.0.1:8800** (not :8000 — :8000 is Hongguo).

Pipeline stages: `download → asr → translate → tts → mux` → `work/<job_id>/output.mp4`

## Prefer CLI (from Z:\Pineline)

```bat
python -m agent_v2 status
python -m agent_v2 job <job_id>
python -m agent_v2 queue status
python -m agent_v2 queue add <job_id> --voice v5
python -m agent_v2 queue stop
python -m agent_v2 yt <job_id>
python -m agent_v2 chat "mô tả mục tiêu"
```

## Rules

- Read status before mutating queue.
- Confirm before `queue add` / `queue stop` if user did not clearly ask to run/stop.
- Default TTS voice: `v5`. Default audio_mode for queue: `duck_bgm`.
- Do not delete `work/` or re-run heavy ASR without explicit ask.
- YT drafts are drafts — user edits before upload.

## Second Brain (hybrid = rules + LLM tool-loop)

Daemon `agent_brain` (+ `agent_quality` + `agent_brain_context`): rules deterministic + `llm_tick` gọi `agent_core` tools (`force_first_tool=pineline_status`).
- Config: `AGENT_BRAIN=1`, `AGENT_BRAIN_MODE=hybrid`, `AGENT_MODEL`/:3377, TG `minimal`
- Per-job: `work/<id>/qa_brain.json` · log `work/logs/agent_brain.log`
- Manual tick: `POST /api/agent/brain/tick` · standalone `D:\PinelineV2_tmp\_run_brain_standalone.py` tới khi restart :8801
- Không thay chat Telegram UX; Brain mutate silent (`require_confirm=False`).

## API cheat sheet

- `GET /api/jobs`
- `GET /api/jobs/{id}`
- `GET|POST /api/queue/jobs` (+ `/stop`, `/clear`)
- `POST /api/jobs/{id}/run-all`
- `POST /api/agent/brain/tick`
