# PinelineV5 — hướng dẫn cho Claude Code

**Cây V5** `Z:\PinelineV5` · server **:8805** · **bố cục package** (`core/`, `engines/`, `engines/asr/`, `agents/`, `http_routes/`, `tools/`) — đọc `docs/LAYOUT.md` + `docs/MANIFEST_CONTRACT.md` trước khi sửa.

> **Trạng thái 2026-11-11 ~03:00:** đã chuyển về bố cục package bằng `scripts/sync_from_v2.py` (tree_audit ERROR 0, import smoke 85/85). Root chỉ còn `server.py`, `app_desktop.py`, `restart_server.py`; bản trùng cũ ở `_to_delete/`. Chờ chạy pytest + start :8805 trên Windows. **Sync từ V2 CHỈ bằng `sync_from_v2.py`** — không chép tay file root.

## Đọc trước (theo thứ tự, dừng khi đủ)

0. **`Z:\PinelineV2\docs\HANDOFF.md`** — tóm tắt phiên 12–14/11: luật làm việc với chủ dự án, trạng thái, việc còn dở.
1. `docs/brain/README.md` — bản đồ Second Brain (module, quy trình, workflow, thuật ngữ).
2. `docs/STATE.md` — đang chạy gì, job nào, **chờ restart** gì.
3. Thẻ module `docs/brain/modules/<module>.md` **trước khi** mở file code lớn (`server.py` ~6,6k dòng, `translate.py` ~4k, `render.py` ~3k, `hongguo_bridge.py` ~4k).
4. `docs/DECISIONS.md` — quyết định user đã khoá (đừng làm ngược).

## Đội subagent (`.claude/agents/`, bản gốc `claude_setup/` — cài bằng `claude_setup\INSTALL.bat`) — định tuyến

| Khi user… | Dùng |
|---|---|
| "check bug", "tìm lỗi", "sao job bị…" | `bug-hunter` → `fix-advisor` (lệnh `/bughunt`) |
| "review", "xem lại code", trước restart/áp dụng | `code-reviewer` (`/review`) |
| mô tả 1 bug cụ thể / "sửa giúp" | `/fix` — chẩn đoán → **user duyệt** → backup → sửa → test → review → docs → brain |
| "cải thiện", "refactor", "tối ưu", "workflow" | `improvement-advisor` (`/improve`) |
| AI agent, brain, prompt, LLM, tự động hoá, đội subagent | `agent-architect` (`/agent-audit`, `/improve agents`) |
| "X ở đâu / ai gọi / key nào / từng lỗi chưa" | `brain-librarian` (`/ask-brain`) |
| sau mỗi lần sửa code / "ghi lại" / "sync brain" | `brain-keeper` (`/brain-sync`) |
| trước/sau khi sync sang V4/V5, cây khác không chạy | `port-sync-guardian` (`/sync-check`) |

Chạy song song các subagent độc lập (vd nhiều bug-hunter cho nhiều nhóm module). Subagent phân tích **không sửa code**; chỉ phiên chính sửa, sau khi user duyệt (trừ khi user nói rõ "cứ sửa").

## Luật bắt buộc khi sửa (chi tiết: `docs/brain/workflows/dev-change.md`)

1. **Backup trước:** `python D:\PinelineV2_tmp\snapshot.py` + chép file gốc vào `Z:\PinelineV5_codebak\<YYYY-MM-DD>_<slug>\` (giữ đường dẫn tương đối).
2. Sửa nhỏ nhất; ghi manifest qua `Manifest.update`; I/O `encoding="utf-8"`.
3. `python -m py_compile <file>` + `python -m pytest -q tests\<liên quan>`.
4. Docs trước khi báo xong: `docs/CHANGELOG.md` (ghi **cần restart gì**), `docs/worklog/<ngày>.md`, bug → `docs/fixes/<ngày>-<slug>.md` (template `.cursor/rules/fix-log-markdown.mdc`, có Recheck Pass/Fail) + dòng `docs/fixes/README.md`, `docs/STATE.md` nếu trạng thái đổi, `docs/DECISIONS.md` nếu user chọn phương án.
5. **Sync brain:** `python scripts\brain_build.py` + cập nhật khối MANUAL thẻ module đã đổi hành vi.
6. Restart :8805/:8802 chỉ khi queue rảnh hoặc user đồng ý (yes/no). **Không bao giờ kill :8000 (Hongguo) hay :8083 (llama-server).**

## Không được

- In/ghi secret (`pineline.config.json`, cookies, token, OAuth) — chỉ tên key/file.
- Xoá `work/`, re-run ASR nặng, re-render job Done, upload YouTube khi chưa hỏi.
- Chạy REVIEW bằng CLI ngoài queue khi studio đang chạy (Studio SOP: 1 job/ghế).
- Báo "xong" khi CHANGELOG + worklog chưa cập nhật.

## Lệnh nhanh

```bat
python scripts\sync_from_v2.py --src Z:\PinelineV2 [--apply]   :: (ở V4/V5) sync an toàn, luôn dry-run trước
python scripts\brain_export.py && python scripts\build_workflow_html.py   :: làm mới docs\brain\workflow.html
python scripts\brain_build.py [--check | --module <tên> | --only a,b]
python scripts\tree_audit.py --peers Z:\PinelineV4 Z:\PinelineV5   :: ERROR phải = 0 trước restart/sync
python -m pytest -q tests
python restart_server.py --clean-env        :: xem docs/RUNBOOK.md trước (kiểm cổng của cây này)
```
