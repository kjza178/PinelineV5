---
name: v5-part-atomizer
description: >-
  Map PinelineV5 into the smallest operational parts (entry, core, routes,
  engines stages, agents, UI, data). Use when explaining how V5 works piece by piece.
---

# V5 Part Atomizer

Root: `Z:\PinelineV5`. Produce finest-grain map; write `docs/reviews/YYYY-MM-DD-v5-part-atoms.md` if swarm asked.

## Atomize each layer

| Layer | Split into |
|---|---|
| Entry | `run_v5.bat` → `server.py` lifespan → port 8805 |
| `core/` | config, batch_config, job_queue, job_meta, film_db, manifest, fileio — one paragraph each |
| HTTP | each `http_routes/routes_*.py` + attach registry role |
| Pipeline | download → asr → translate → tts → mux; split_parts; pronoun analyze/qa |
| Agents | tele_cmd, feeder, hongguo, publisher — trigger → API |
| UI | index3, films_ui, hongguo/hongguo2, workflow |
| Data | `work/<job_id>/`, films.db, queue json, locks |

## Output

Mermaid or nested bullets: **atom → file → main function → side effect**. No fluff.
