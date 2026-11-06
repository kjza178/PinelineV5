---
name: v5-critical-bug-hunter
description: >-
  Find critical/runtime bugs in PinelineV5 pipeline (split/merge, queue, ASR,
  translate, TTS, mux, Hongguo). Use when hunting P0/P1 bugs.
---

# V5 Critical Bug Hunter (read-only)

Root: `Z:\PinelineV5` (compare V2 if port drift). **Do not modify files.**

## Hotspots

- `engines/split_parts.py` merge hardlink / ENOSPC
- `server.py` auto-split / stop heal / voice resolve
- `engines/translate.py` + `engines/pronoun_consistency.py` + `_plan_block_for_qa`
- `engines/llm.py` / Aurora 413 no-retry
- Queue: `core/job_queue.py`, promote ASR invalidate
- UI: `static/ui/hongguo2.html` CTA enqueue vs submit

## Output

`P0/P1/P2 | symptom | root cause | evidence | recheck`. Max 15. Mark SAFE autofix candidates.
