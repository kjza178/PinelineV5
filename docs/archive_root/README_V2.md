# Pineline V2

Bản **tách** từ `Z:\Pineline` (Pineline 1).

| | Pineline 1 | Pineline V2 |
|---|---|---|
| Path | `Z:\Pineline` | `Z:\PinelineV2` |
| Work | `Z:\Pineline\work` | `Z:\PinelineV2\work` |
| Port | 8800 | **8801** |
| Agent | (sau khi restart code mới) | có sẵn (`agent_core`) |

Chạy:

```bat
Z:\PinelineV2\run_v2.bat
```

UI: http://127.0.0.1:8801/ui3 → nút **Agent**

## Agent A / B / C (mặc định trong `run_v2.bat`)

| Track | Env | Việc |
|---|---|---|
| **A Watcher** | `AGENT_WATCH=1`, `AGENT_WATCH_SEC=300`, `AGENT_TELEGRAM=1` | Định kỳ scan → heal **safe** khi GPU rảnh; log `work/../logs/agent_watch.log`; Telegram qua `~/.hermes/.env` |
| **B QA gate** | `AGENT_QA_GATE=1` | Sau translate: snapshot → `run_review` → diff; **pass** mới TTS; fail → `agent.qa_blocked` |
| **C Classifier** | (luôn) | `diagnose`/`heal` gắn class: `cuda_oom`, `missing_voice`, `disk_full`, … — `notify_only` không spam heal |

API nhanh:

- `GET /api/agent/scan-failed`
- `POST /api/agent/heal-failed`
- `GET /api/agent/jobs/{id}/review-diff`
- `POST /api/agent/jobs/{id}/qa-gate` body `{"enabled":true,"override_pass":true}`
- `POST /api/agent/watch-once`

Giọng TTS / venv / llama :8083 vẫn dùng chung máy — chỉ **job data** tách.
