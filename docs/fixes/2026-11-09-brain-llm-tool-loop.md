# Brain LLM tick trả tools=[] (không gọi tool)

- **Date:** 2026-11-09
- **Job / khu vực:** `agent_brain.llm_tick` / `agent_core.run_agent` / Second Brain C
- **Status:** fixed
- **Backup:** zip `Z:\PinelineV2_backup_2026-11-10_0007.zip`; codebak `Z:\PinelineV2_codebak\2026-11-09_brain-force-tool\`

## Triệu chứng

`llm_tick` báo `ok` nhưng `tools=[]`; model viết phân tích snapshot và bảo «chưa đăng ký tool» / không xác minh được — không HOLD/heal thật.

## Root cause

1. Snapshot dài + `tool_choice=auto` → `chatgpt/gpt-5-6-mini` (:3377) hay trả text thuần dù native tools hoạt động với prompt ngắn / `tool_choice` ép tên hàm.
2. Path HTTP `:8801/api/agent/chat` dùng code server cũ (chưa `force_first_tool`) trong lúc không restart giữa review 05670.
3. Không có Runtime bind ngoài process server → standalone không chạy được `run_agent` in-process.

## Evidence

- Probe `:3377` + 5 tools + `tool_choice=required` → `pineline_status`.
- Snapshot đầy đủ + `auto` đôi khi có tool; cùng payload qua chat dài → `tools=[]`.
- Sau fix: `tools=['pineline_status','pineline_job','pineline_hold_after_translate',…]`; manifest `05670` `hold_after_translate=true`.

## Fix

- `agent_core.run_agent`: `force_first_tool` / `force_first_args`; synthesize call nếu proxy bỏ `tool_choice`.
- `agent_brain`: bind Runtime FS+HTTP; `llm_tick` ép `pineline_status` rồi deep `pineline_job` cho job ưu tiên; snapshot rút ~4500 ký tự.
- `routes_agent` / `AgentChatReq`: nhận `force_first_tool`.
- Hành vi mới: Brain C hybrid tự gọi tool và mutate silent (`require_confirm=False`).

## Recheck

1. `python -c "from pathlib import Path; from agent_brain import llm_tick; print(llm_tick(Path(r'Z:\PinelineV2\work')))"`
2. Xem `work/logs/agent_brain.log` — dòng `tools=[...]` có ≥1 tên tool.
3. **Pass nếu:** `via` chứa `inprocess` và có `pineline_status` (thường + `pineline_job` khi có focus).
4. **Fail nếu:** `tools=[]` hoặc chỉ reply text «chưa xác minh» mà không có step tool.

## Liên quan

- Config: `AGENT_BRAIN_MODE=hybrid`, `AGENT_MODEL=chatgpt/gpt-5-6-mini`, `AGENT_BASE_URL=http://127.0.0.1:3377/v1`
- Job smoke: `05670cbf7c1c` (HOLD khi QA high, không heal khi translate running)
- Restart :8801 khi idle để nạp in-process brain trong server
