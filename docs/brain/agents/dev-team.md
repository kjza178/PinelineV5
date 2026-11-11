# Đội subagent dev (Claude Code)

_Cập nhật: 2026-11-11. Bản gốc: `claude_setup/agents/*.md`, `claude_setup/commands/*.md` → cài vào `.claude/` bằng `claude_setup\INSTALL.bat` (sửa ở `claude_setup/` rồi chạy lại)._

| Agent | Vai | Quyền | Model | Output |
|---|---|---|---|---|
| **bug-hunter** | Săn bug có bằng chứng (race, mất dữ liệu, queue/stage, encoding, process/VRAM) | đọc + chạy lệnh chỉ-đọc; Write chỉ báo cáo | opus | `docs/reviews/<ngày>-bughunt-*.md` |
| **code-reviewer** | Review diff (codebak/git/brain-check) hoặc module; checklist 10 mục theo quy ước dự án | như trên | opus | `docs/reviews/<ngày>-review-*.md` |
| **fix-advisor** | Root cause + 1–3 phương án (diff đề xuất) + test + fix log nháp + checklist áp dụng | chỉ đọc | opus | trả về phiên chính |
| **improvement-advisor** | Cải tiến code/hiệu năng/độ tin cậy/workflow dev & vận hành, roadmap ưu tiên | đọc; Write báo cáo | opus | `docs/reviews/<ngày>-improve-*.md` |
| **agent-architect** | AI agent runtime + LLM I/O + eval + đội subagent & brain | đọc; Write báo cáo | opus | `docs/reviews/<ngày>-agents-*.md` |
| **brain-keeper** | Giữ second brain: build, MANUAL, processes/workflows/glossary | đọc + Write/Edit trong `docs/brain` | sonnet | file docs/brain |
| **port-sync-guardian** | Canh sync/port V2↔V4↔V5: tree_audit, file bị đè, import vỡ, cổng cứng, kế hoạch sync | đọc; Write báo cáo | opus | `docs/reviews/<ngày>-sync-*.md` |
| **brain-librarian** | Tra cứu nhanh có nguồn | chỉ đọc | haiku | trả lời ngắn + nguồn |

## Lệnh

| Lệnh | Chuỗi agent |
|---|---|
| `/bughunt [scope]` | brain_build → bug-hunter (song song theo nhóm) → fix-advisor cho P0/P1 → user duyệt |
| `/review [scope\|recent]` | code-reviewer (+ bug-hunter nếu đụng queue/manifest/thread) |
| `/fix <bug>` | librarian → fix-advisor → **duyệt** → backup → patch → test → code-reviewer → docs → brain-keeper |
| `/improve [area]` | improvement-advisor ∥ agent-architect → bảng ưu tiên gộp |
| `/agent-audit` | agent-architect ∥ bug-hunter (agent_*) |
| `/brain-sync [enrich N\|modules]` | brain-keeper |
| `/ask-brain <q>` | brain-librarian |
| `/sync-check [V2 → V5]` | tree_audit → port-sync-guardian |

## Nguyên tắc thiết kế đội

- **Tách người tìm lỗi và người sửa**: bug-hunter/reviewer không sửa → không "tự chấm bài mình".
- **Chỉ phiên chính được sửa code**, và chỉ sau khi user duyệt (trừ khi user nói "cứ sửa").
- **Agent đọc brain trước code** → tiết kiệm context (server.py ~6,6k dòng, translate.py ~4k).
- **Mọi báo cáo ghi file** trong `docs/reviews/` → không thất lạc, brain tự liên kết vào thẻ module ở lần build sau.
- **Model theo độ khó**: suy luận lỗi/kiến trúc = opus; ghi chép = sonnet; tra cứu = haiku.

## Mở rộng

Thêm agent: tạo `.claude/agents/<tên>.md` (frontmatter `name`, `description` nói rõ *khi nào dùng*, `tools`, `model`), thêm dòng vào bảng trên, cập nhật `CLAUDE.md` mục định tuyến.
