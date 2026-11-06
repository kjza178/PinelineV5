# Đợt 7: gỡ UI cũ, tách server.py

- **Ngày:** 2026-10-06, 14:50–15:20
- **User chọn:** «ui_old, split_server — nhớ làm đủ save/backup trước khi thực hiện»
- **Backup:** zip `Z:\PinelineV2_backup_2026-10-06_1455.zip`; bản gốc từng file trong `Z:\PinelineV2_codebak\2026-10-06_batch7\` (`server.py`, `index.html`, `index1.html`, `index2.html`, `index3.html`, `hongguo.html`, `restart_server.py`).
- **Hiệu lực:** chỉ sau khi restart server :8801. Server đang chạy (PID 25032) vẫn dùng code trước đợt 7, job 3a2e không bị ảnh hưởng.

## 1. Gỡ UI cũ (review X9)

- Xoá `index1.html`, `index2.html` (bản A/B test 22/09, không ai link tới ngoài chính nó).
- `server.py`: bỏ route `/ui1`, `/index1.html`, `/ui2`, `/index2.html`.
- Bỏ link UI1/UI2 trong `index.html` và `index3.html`. Nút UI1 trong `hongguo.html` giờ trỏ `/ui3`. Các file HTML được đọc lại mỗi request nên link mới có hiệu lực ngay.

## 2. Tách server.py

`server.py` 6221 → 5372 dòng. Ba nhóm route ít phụ thuộc được chuyển ra:

| File | Nội dung | Tên |
|---|---|---|
| `routes_ui.py` | `find_index`, `/`, `/ui3`, `/ui4`, `/hongguo` | 6 |
| `routes_hg.py` | `/api/hg/*` (cầu nối Hongguo Downloader) | 26 |
| `routes_agent.py` | hook agent (`_agent_*`, `_HEAL_HOOKS`, `_AV_SYNC_HOOKS`), `agent_core.bind(Runtime(...))`, `/api/agent/*` | 45 |

Cách làm (`D:\PinelineV2_tmp\split_server.py`, sinh tự động bằng AST, không chép tay):

- Code chuyển đi gọi server qua `S.<tên>` (`import server as S`), không dùng `from server import …`. Lý do: `mock.patch.object(server, "WORK_ROOT"/"mux_job", …)` trong `check_batch3` vẫn có tác dụng.
- Import module chuẩn (`json`, `JSONResponse`, `Manifest`…) được chép sang file mới.
- `@app.` đổi thành `@router.`. `server.py` gọi `app.include_router(...)` ở đúng chỗ khối agent cũ, sau khi mọi hàm/model lõi đã định nghĩa, và re-export toàn bộ tên đã chuyển (`server._agent_mux_run`, `server.hg_merge`… vẫn dùng được).
- `sys.modules.setdefault("server", sys.modules[__name__])` ở đầu `server.py`. Khi chạy `python server.py`, module là `__main__`; thiếu alias này thì `import server` trong routes sẽ nạp server lần 2 (app thứ 2, hàng đợi thứ 2).
- Phần jobs/queue/pipeline giữ nguyên trong `server.py`: check đợt 1–4 đọc trực tiếp mã nguồn các hàm đó (`_stage_complete_on_disk`, guard, `run_stage`, `_queue_run_one`).
- `restart_server.py`: precheck compile thêm `routes_*.py`.

## Kiểm chứng

- `D:\PinelineV2_tmp\compare_openapi.py`: so bản trước/sau khi tách (đều đã gỡ ui1/ui2). 108 route, OpenAPI `paths` + `components` giống hệt, startup handler và middleware cùng thứ tự, gọi thử `/`, `/ui3`, `/ui4`, `/hongguo`, `/api/agent/pending`, `/api/hg/merge-queue`, `/api/queue/jobs`, `POST /api/agent/confirm`, `/ui1` cho cùng mã trạng thái. Chạy với `PYTHONHASHSEED` = 0 và 123: FastAPI sinh operationId trùng cho route GET+HEAD (`/api/jobs/{job_id}/video`, `/api/hg/library/preview`) theo thứ tự set, nên không cố định seed thì 2 path này có thể lệch giữa 2 lần chạy, kể cả với file không đổi.
- `D:\PinelineV2_tmp\check_main_alias.py`: chạy `server.py` như `__main__` (thay `uvicorn.run`) → `sys.modules["server"]`, `routes_agent.S`, `routes_hg.S` đều là module `__main__`.
- pyflakes: không có tên chưa định nghĩa (chỉ còn 2 cảnh báo cũ trong `server.py`).
- `tests/test_server_split.py` (route còn đủ, re-export, cùng module). Pytest 78/78. Precheck restart OK.

## Recheck

```powershell
cd Z:\PinelineV2; python -m pytest -q
$env:PYTHONHASHSEED='0'; python D:\PinelineV2_tmp\compare_openapi.py   # cần D:\PinelineV2_tmp\oldsrv\server.py (bản trước khi tách)
python D:\PinelineV2_tmp\check_main_alias.py
```

## Chưa làm

- Tách tiếp phần jobs/pipeline của `server.py` (cần viết lại check đợt 1–4 đang đọc mã nguồn).
- `hongguo_bridge.py`, bỏ hot-reload.
