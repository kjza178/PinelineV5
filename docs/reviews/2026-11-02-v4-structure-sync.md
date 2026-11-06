# Kiểm tra đồng bộ cấu trúc PinelineV4

_Date: 2026-11-02 04:10_

## Kết luận

**Runtime lõi đã đồng bộ V4** (cổng 8804, launcher, UI index3, Canva, batch `auto_split`, archive thừa).  
**Chưa 100%** trên lớp nhãn/comment/test lịch sử và một số đường dẫn dual-work cố ý.

## Đã khớp

| Hạng mục | Trạng thái |
|---|---|
| Launcher root | Chỉ `run_v4` / `run_tele_cmd` / `build_desktop` / install ASR·ORT |
| Default `PORT` | 8804 trong `run_v4`, `run_tele_cmd`, `app_desktop`, `restart_server`, `migrate_work`, sidecar `BASE` |
| UI | `routes_ui` → `index3.html` only |
| Canva callback | `:8804` |
| `lib_check` samples | `PinelineV4\data\samples` |
| Docs ops | `RUNBOOK` + `ARCHITECTURE` V4 |
| Attic | launchers / Tauri / index.html / scratch / docs_stale |

## Vừa vá (pass đồng bộ nhãn)

- `index3.html` brand/port V4·8804
- Docstring/Telegram string: `agent_tele_cmd`, `agent_feeder`, `agent_hongguo`, `agent_core`, `agent_watch`, `fileio`, `server`, `routes_*`
- `build_desktop.bat` đóng gói `index3.html` (trước đó còn `index.html` đã archive → build gãy)
- `migrate_work` docstring + tests Host → `:8804`
- `workflow.html` work path

Backup: `Z:\PinelineV2_codebak\2026-11-02_v4-sync\`

## Còn lệch có chủ đích / thấp ưu tiên

1. **`agent_heal`**: vẫn dò `D:\PinelineV2_work` cạnh V4 — heal job cũ.
2. **`restart_server`**: nhánh legacy `start_8801.py` nếu `PORT=8801` (bridge máy cũ).
3. **`agent_feeder`**: cmdline fallback nhận cả 8804/8801 khi detect process.
4. **`scripts/check_batch*.py`**: hardcode `Z:\PinelineV2` + Host 8801 — script lịch sử đợt review V2, không phải runtime.
5. **`docs/STATE.md` bảng job**: số liệu/path work vẫn mô tả thời V2 (lịch sử vận hành).
6. **Dual API** `/films`+`/meta` trên :8804 và :8802 — cố ý.
7. **Nhiều engine ASR** — chọn config, không phải lệch version.

## Cấu trúc module

Ổn: `routes_*` / pipeline stage / agent server+sidecar / desktop WebView2.  
Nợ: `server.py` monolithic; không chặn đồng bộ V4.

## Recheck

1. `python -c "import routes_ui; assert routes_ui.find_index().name=='index3.html'"`
2. Grep active (không `scripts/archive`, không `docs`): không còn `Pineline V2` / `port 8801` trên UI.
3. `pytest tests/test_queue_jobs_api.py tests/test_server_split.py`
4. Restart :8804 để nạp nhãn UI + routes (process cũ).
