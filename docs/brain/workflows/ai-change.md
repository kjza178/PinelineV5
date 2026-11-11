# Workflow: đổi model / prompt / hành vi AI agent

_Cập nhật: 2026-11-11._

Thay đổi LLM (model, prompt, nhiệt độ, chunk size, parallel) **khó thấy lỗi bằng mắt** và lỗi lan qua cả bộ phim. Quy trình:

1. **Ghi giả thuyết** trong worklog: đổi gì, kỳ vọng tốt hơn ở đâu (câu hang ít hơn? xưng hô? tốc độ?).
2. **Bench trên mẫu cố định** trước khi đổi mặc định: dùng job sandbox / SRT mẫu đã dùng ở `docs/reviews/2026-11-09-mt-*` (hachimi60, sandbox job). So: số câu sửa, câu sai tên/HV, hang high, thời gian, lỗi 413/timeout.
3. **Ghi kết quả** `docs/reviews/<ngày>-<chủ đề>.md` (bảng trước/sau + ví dụ câu).
4. **User chọn** → `docs/DECISIONS.md`.
5. **Đổi config** (key file-first trong `pineline.config.json` có hiệu lực ngay) → CHANGELOG + STATE mục cấu hình mặc định.
6. **Theo dõi 1–2 job đầu**: `work/<job>/qa_brain.json`, `work/logs/agent_brain.log`, tỉ lệ HOLD.
7. Agent runtime đổi hành vi (policy, tool, cooldown) → `/agent-audit runtime` trước khi bật mặc định; cập nhật `docs/brain/agents/runtime-agents.md`.

## Hàng rào an toàn cho agent tự động (checklist khi thêm hành động mới)

- [ ] Có env kill-switch (vd `AGENT_BRAIN=0`) và mặc định an toàn
- [ ] Cooldown theo job + fingerprint (kiểu `AGENT_WATCH_COOLDOWN`)
- [ ] Không đụng job có `.stop`, job Done đã upload, `work/` của job khác
- [ ] Không chạy khi `job_queue.queue_busy()` nếu cần GPU
- [ ] Ghi audit (trước/sau, lý do) vào log + manifest.agent
- [ ] Không trùng vai với agent khác (brain vs watch vs autopilot vs heal)
- [ ] Có test pytest cho parser/policy
