# Agent không mở script HOLD vì id rút gọn `9aa089_p01`

- **Date:** 2026-11-20
- **Job / khu vực:** agent `/qa`, `pineline_script_*`, `pineline_job` — job `9aa0891fbfd1_p01`
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-20_agent-resolve-job\`

## Triệu chứng

User / agent hỏi câu lỗi HOLD bằng id ngắn `9aa089_p01` → báo «chưa có script.json» dù folder thật `work/9aa0891fbfd1_p01/script.json` đã có. Agent không lấy được zh/vi câu CJK để sửa.

## Root cause

`agent_qa_ask.resolve_job` chỉ `startswith(ref)` với `ref=9aa089_p01`. Tên folder `9aa0891fbfd1_p01` **không** bắt đầu bằng chuỗi đó (hash nằm giữa prefix và `_p01`). `_load_script` trong `agent_core` cũng không resolve — nhìn thẳng `work/<raw>/script.json`.

## Evidence

- Trước: `resolve_job(work, "9aa089_p01")` → `None`; path `work/9aa089_p01` không tồn tại.
- Sau: resolve → `9aa0891fbfd1_p01`; `script_peek` trả `i=187` zh=`我可是C位啊。` vi=`Tôi là C位 đấy.` + `hold_reason` CJK.

## Fix

- `resolve_job`: nhận dạng `prefix_pNN` → regex `^{pref}[0-9a-f]*_p0*{N}$`.
- `resolve_job_candidates` + lỗi có gợi ý ứng viên.
- `agent_core.resolve_job_id` + `_normalize_tool_job_args` trong `_dispatch` (mọi tool có `job_id`/`job_ids`).
- `script_peek` / `pineline_job`: `hold_reason` + `cjk_in_vi_sample`.
- SYSTEM prompt 8b: agent dùng peek/job, không đoán nội dung Hán.
- Test: `tests/test_agent_resolve_job.py`.

## Recheck

1. `python -c "from pathlib import Path; import agent_qa_ask as q; print(q.resolve_job(Path('work'),'9aa089_p01'))"` → `9aa0891fbfd1_p01`
2. `python -c "from pathlib import Path; import agent_core as ac; print(ac.script_peek(Path('work'),'9aa089_p01')['cjk_in_vi_sample'])"`
3. `python -m pytest -q tests/test_agent_resolve_job.py`
4. **Pass nếu:** resolve đúng part; peek có zh/vi câu CJK; agent Telegram `/qa 9aa089_p01` không báo thiếu script vì sai id.
5. **Fail nếu:** vẫn `None` / FileNotFoundError path `9aa089_p01`.

## Liên quan

- HOLD `review_failed` / simple CJK sau 3 retries — nội dung câu do agent sửa sau khi resolve OK.
- Restart :8801 + :8802 để load `agent_core` / `agent_qa_ask` (yes/no khi queue rảnh).
