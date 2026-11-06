# Agent chạy tool chỉ vì được nhắc trong câu trả lời

- **Date:** 2026-10-06
- **Job / khu vực:** `agent_core.py` — `_parse_pycall_tool_calls`, `run_agent`
- **Status:** fixed (chưa có hiệu lực trong server :8801 tới lần restart kế tiếp)

## Triệu chứng

Phát hiện khi review code (chưa xảy ra thật vì bản parser `tool(...)` thêm sáng 6/10 chưa được nạp vào server). Nếu đã nạp: câu tóm tắt kiểu «Đã gọi hg_auto_flow(query_or_id="X") xong» hoặc gợi ý «hãy dùng stop_job(job_id="…")» sẽ bị chạy thật (Telegram luôn `allow_mutate=True`), có thể lặp tới `max_steps`. Model nhại `hg_auto_flow(query_or_id=..., ...)` từ SYSTEM → `json.dumps(Ellipsis)` ném `TypeError` ngoài `try` → `/api/agent/chat` 500.

## Root cause

- Parser quét mọi `name(` khớp tên tool ở bất kỳ đâu trong tin nhắn.
- `run_agent` parse tool call dạng chữ ở mọi lượt, kể cả lượt tóm tắt sau khi tool đã chạy.
- `ast.literal_eval` chấp nhận `...`; `json.dumps` nằm ngoài khối `try`.
- Test cũ (`test_pycall.py`) chỉ thử tên tool không kèm ngoặc nên không bắt được.

## Fix

- `_parse_pycall_tool_calls`: chỉ nhận lời gọi khi (a) cả tin nhắn chỉ là lời gọi (bỏ qua `*`, backtick, `>`, `-`), hoặc (b) ngay trước lời gọi trên cùng dòng là nhãn `Action:` / `Hành động:`. `json.dumps` đưa vào `try`, bắt thêm `TypeError`.
- `run_agent`: chỉ parse tool call dạng chữ khi lượt này chưa chạy tool nào (`not steps`).

## Recheck

1. `python D:\PinelineV2_tmp\test_pycall.py` (11 ca: Action + backtick, lời gọi đứng riêng, nhắc trong câu, recap "Đã gọi …(…)", gợi ý "hãy dùng stop_job(…)", `...`, JSON fence).
2. **Pass nếu:** in `ALL PASS 0`.
3. Sau restart server: hỏi agent qua Telegram một câu khiến nó tóm tắt việc đã làm → `steps` không có tool chạy lặp.
4. **Fail nếu:** tool chạy 2 lần trong một lượt, hoặc `/api/agent/chat` trả 500 khi model nhại ví dụ SYSTEM.

## Liên quan

- Review: `docs/reviews/2026-10-06-code-review.md` (agent P0-1, P0-2).
- Vẫn còn: tool phá huỷ (stop/clean/queue_stop) nên đòi xác nhận thay vì chạy từ chữ — xem review.
