# Second Brain Agent — thiết kế

- **Date:** 2026-11-09
- **Policy:** full silent (không hỏi ✅; Telegram tối thiểu)
- **HOLD:** chỉ khi QA high severity chặn TTS/mux

## Mục tiêu

Daemon nền là “second brain” của Pineline: tự detect lỗi (ops + chất lượng VI + infra), tự quyết và autofix, giữ pipeline chạy mượt. Không thay chat agent Telegram (`agent_core`).

## Vòng lặp

```
tick (AGENT_BRAIN_SEC, mặc định 60s)
  → sensors (jobs / script QA / :8083,:3377,:8802)
  → incidents
  → policy (L0–L3 + HOLD)
  → actuators (heal / quality heal / hold / preset)
  → memory (agent_brain_state.json + work/<job>/qa_brain.json)
```

## Lớp sự cố

| Lớp | Hành động |
|---|---|
| L0 infra | ping fail → log; :8083 503 → đợi/switch preset (cooldown) |
| L1 ops | `agent_heal.heal_job` safe → aggressive nếu class cho phép |
| L2 quality | `agent_quality.apply_safe_heals`; còn high → HOLD |
| L3 nặng | restart llama / force re-review theo rule + cooldown; TG 1 dòng sau |
| HOLD | `hold_after_translate` + `qa_blocked` khi `high_open > 0` |

## Module

- `agent_quality.py` — scan/heal deterministic (port từ qa_watch ad-hoc)
- `agent_brain.py` — daemon + policy + actuators
- `agent_qa_gate.py` — `pass` xét thêm `qa_brain.json`
- `server.py` — `_start_agent_brain` lúc startup

## Config

- `AGENT_BRAIN=1` (mặc định bật)
- `AGENT_BRAIN_SEC=60`
- `AGENT_BRAIN_TELEGRAM=minimal` (chỉ HOLD/L3)
- `AGENT_BRAIN_CONFIRM=0` (opt-in hỏi ✅ — mặc định tắt)
- `AGENT_BRAIN_LLM_SAMPLE=0`
- `AGENT_BRAIN_MODE=hybrid` (rules + LLM tool-loop) — user chọn **C** 2026-11-09
- `AGENT_BRAIN_LLM_SEC=180`, `AGENT_BRAIN_LLM_STEPS=10+`
- LLM: `AGENT_MODEL` / `AGENT_BASE_URL` (:3377) — `llm_tick` ép `pineline_status` rồi deep `pineline_job`

## Không làm (MVP)

- Không nhân đôi heal trên sidecar :8802
- Không đụng job có `.stop`
- Không remake ASR/download trừ heal aggressive sẵn có
