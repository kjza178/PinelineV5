# Audit trùng lặp / thừa PinelineV4

_Date: 2026-11-02 · nguồn: scan agent + follow-up vá_

## Đã xử lý (follow-up)

| Việc | Chi tiết |
|---|---|
| Archive launcher nguy hiểm | `run_v2.bat`, `run.bat`, `Pineline.bat`, `app.py`, `dung-may-5060ti.bat`, `PineLine/` → `scripts/archive/launchers_legacy/` |
| UI orphan `index3` | `routes_ui.find_index` ưu tiên `index3.html`; `/ui3` serve index3 |
| Canva callback | Default `:8804` (`canva_client` + `films_ui` text) |
| `lib_check.SAMPLE_DIR` | `Z:\PinelineV4\data\samples` (không còn V2) |
| `docs/workflow.html` stale | → `scripts/archive/docs_stale/` (root `workflow.html` là bản served) |
| Fallback `run_v2` | `restart_server` / `migrate_work` chỉ `run_v4.bat` |
| Lock message | `server.py` in «PinelineV4» |

Backup code: `Z:\PinelineV2_codebak\2026-11-02_v4-dedupe\`

## Quét thêm (không exact-dup file)

- Không còn cặp `.py/.html/.js` trùng hash ngoài archive.
- Root còn ~72 `.py` — không phát hiện module clone tên gần giống thừa.
- `scratch/*` + `scripts/check_batch*.py` / `check_sidecar_lock.py` còn hardcode `Z:\PinelineV2` (script lịch sử / one-shot).

## Follow-up 04:05

- Archive Tauri + `index.html` + `scratch/` (xem `scripts/archive/*/README.md`).
- RUNBOOK + ARCHITECTURE viết lại cho V4 :8804.
- Còn chủ đích: dual `/films`+`/meta` :8804/:8802; nhiều engine ASR; `server.py` monolithic.

## Giữ

`run_v4.bat`, `run_tele_cmd.bat`, `app_desktop.py`, `server` + `routes_*`, pipeline, `films_ui`/`hongguo`, `docs/`, `tests/`, `scripts/archive/` (attic).

## Restart

Cần **restart :8804** để `routes_ui` + Canva default có hiệu lực.
