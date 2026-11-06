# Runbook vận hành — PinelineV4

_Cập nhật: 2026-11-02_

Root code: `Z:\PinelineV4`. Cổng server **8804**, sidecar **8802**. (V2 production riêng ở `Z:\PinelineV2` :8801 — không lẫn launcher.)

## Khởi động / restart

| Việc | Lệnh | Ghi chú |
|---|---|---|
| Start desktop (WebView2) | `python app_desktop.py` / `run_v5.bat` | Nhúng UI `:8805` |
| Start desktop (Tauri) | `run_tauri.bat` | Cửa sổ Tauri → `http://127.0.0.1:8805` (tự start server nếu thiếu); cần Rust + `npm i` |
| Start web server | `run_v4.bat` → chọn **2** hoặc `python server.py --host 127.0.0.1 --port 8804` | `TEMP=D:\PinelineV4_tmp` |
| Restart server | `python restart_server.py` (cwd V4) | **Chỉ khi queue rảnh hoặc user đồng ý.** Dùng `run_v4.bat` / `server.py` — không fallback `run_v2`. |
| Restart hẹn giờ | `python restart_server.py --after-current --hold-file Z:\PinelineV4\.restart_hold --clean-env --sidecar` | Rút job chờ → đợi job chạy xong → hold → py_compile → start → sidecar → requeue. State: `work/logs/restart_pending.json` |
| Sidecar Telegram + Auto-pilot | `run_tele_cmd.bat` | 1 bản; khoá `.sidecar_8802.lock`. `PINELINE_BASE` theo `PORT`. |
| Hongguo Downloader | app riêng :8000 | UI token; API `/dl/*` |
| Job từ phim đã tải | `/hongguo` → Hàng đợi gộp → «＋ Job» | Series có `(merged)`, không đang gộp. Đã có job → `/ui3?job=<id>` |
| Merge queue HG | `/hongguo` hoặc `GET :8804/api/hg/merge-queue` | `work/logs/hg_merge_state.json`. `restart_server` từ chối khi đang gộp; `--ignore-hg` để ép |
| LLM local (tuỳ chọn) | `E:\models\presets\start-model.ps1 <id>` | Không kill llama-server khi chưa được phép |

Env process đang LISTEN:

```powershell
python -c "import psutil;[print(c.laddr.port,c.pid,{k:psutil.Process(c.pid).environ().get(k) for k in ('LLM_MODEL','AGENT_MODEL','AGENT_WATCH','AGENT_QA_GATE','TEMP','PORT')}) for c in psutil.net_connections('tcp') if c.laddr.port in (8804,8802) and c.status=='LISTEN']"
```

## UI / URL nhanh

| URL | Nội dung |
|---|---|
| `http://127.0.0.1:8804/` hoặc `/ui3` | Dashboard **index3.html** |
| `/hongguo` | Hongguo merge / tạo job |
| `/films/ui` | Quản lý films.db (cũng có trên sidecar :8802) |
| `/workflow` | Sơ đồ hệ thống (`workflow.html` ở root) |

Launcher cũ (`run_v2`, `Pineline.bat`, `app.py`…) nằm trong `scripts/archive/launchers_legacy/`. **Tauri đã restore** lên root (`run_tauri.bat`); bản archive chỉ đối chiếu.

## Khi nào cần restart gì

| Sửa file | Cần |
|---|---|
| `render.py`, `render_fx.py`, `sfx_lib.py`, `assemble.py`, `media_ts.py`, `subs.py`, `config.py`, key render trong `pineline.config.json` | Không — nạp lại mỗi lần render. **Lỗi cú pháp hỏng mux đang chạy** → `py_compile` ngay |
| `pineline.config.json` (key khác) | Nhiều key file-first qua `config.get`; chỗ đọc `os.getenv` trực tiếp vẫn cần restart |
| `hongguo_bridge.py` | `/api/hg/*` reload; tool agent trong server → restart :8804 |
| `agent_*.py` (trong server), `server.py`, `job_queue.py`, `translate.py`, `llm.py`, `asr*.py`, `clone_tts.py`, `split_parts.py`, `routes_*.py` | Restart **:8804** |
| `agent_tele_cmd.py`, `agent_autopilot.py`, `agent_feeder.py`, `film_db.py` | Restart **:8802** |
| `index3.html`, `hongguo.html`, `films_ui.html`, `static/app.js` | Ctrl+F5 |

## Video nguồn / work

- Work mặc định: junction/`PINELINE` work dưới cây V4 (thường `D:\PinelineV4_work` hoặc cấu hình hiện tại — xem `STATE.md`).
- Import trong `SOURCE_DIRECT_ROOTS` (mặc định `D:\Lib`) → `source_mode=direct`, không copy `source.mp4` vào job.
- **Đừng dọn/đổi tên bộ trong `D:\Lib` khi job chưa xong.**

## Phim dài (auto_split)

Mặc định `batch_config`: `auto_split=true`, `auto_split_min_h=3`, `auto_split_hours=2.5`, `auto_merge=true`.

- Queue / run-all job ≥3h → cắt `{id}_p01…pN`, xếp tuần tự, part cuối merge → job cha `output.mp4` (+ `output_full.mp4`).
- Xem trước: `GET /api/jobs/{id}/split-plan` (`will_auto_split`).
- Tắt: `/set auto_split=off`. Chi tiết: `docs/fixes/2026-11-02-longfilm-sub-drift-split.md`.

## Chế độ âm thanh (`audio_mode`)

CONFIG BATCH hiện: `sfx_lib`.

| Chế độ | Gồm | Nhạc gốc |
|---|---|---|
| `sfx_lib` | Giọng Việt + SFX CDX23 + `assets/bgm_yt/` theo mức | Không |
| `voice_only` | Chỉ giọng Việt | Không |
| `voice_bgm` | Giọng + 1 bài `assets/bgm/` | Không |
| `duck` / `duck_bgm` | Giọng + audio gốc (duck) ± BGM kho | Có |
| `demucs_keep` / `demucs_clean` | Nền Demucs ± giọng Trung nhỏ | Có |

## Sự cố thường gặp (V4)

| Triệu chứng | Xử lý |
|---|---|
| «Đã có server PinelineV4 khác giữ cổng 8804» | Đã có process — kiểm PID LISTEN 8804, không start bản 2 |
| Lệch tiếng/sub phim dài | `auto_split` + `AUDIO_TS_FIX`; job cũ `python media_ts.py --check <video>` |
| 409 job đang chạy | Đợi hoặc Dừng; stage kẹt → `heal_stale` |
| Sidecar / Telegram lệch films | So `:8804/films` vs `:8802/films` — cùng `film_db` |
| Mở nhầm cổng 8801 / path V2 | Dùng `run_v4.bat`; launcher V2 đã archive |

Bảng sự cố chi tiết lịch sử (agent confirm, HG merge, restart NoSuchProcess…): vẫn đúng về cơ chế — đổi cổng **8801→8804** và path **PinelineV2→PinelineV4** khi áp dụng. Xem thêm `docs/fixes/`.

## Backup (bắt buộc trước sửa)

1. `python D:\PinelineV2_tmp\snapshot.py` → zip `Z:\PinelineV2_backup_<ngày>_<giờ>.zip` (script tên lịch sử; che secret).
2. Chép file sắp sửa vào `Z:\PinelineV2_codebak\<YYYY-MM-DD>_<slug>\`.

Khôi phục 1 file: chép từ codebak đè vào `Z:\PinelineV4\`, rồi restart theo bảng trên.

## Test

```powershell
cd Z:\PinelineV4
$env:PYTHONIOENCODING='utf-8'
python -m pytest -q
```

## Archive trong repo

| Thư mục | Nội dung |
|---|---|
| `scripts/archive/launchers_legacy/` | `run_v2`, `run.bat`, `Pineline.bat`, `app.py`, … |
| `scripts/archive/tauri_desktop/` | Skeleton cũ (đối chiếu); live = root `src-tauri/` + `run_tauri.bat` |
| `scripts/archive/ui_legacy/` | `index.html` cũ |
| `scripts/archive/docs_stale/` | `workflow.html` bản docs cũ |
| `scripts/archive/scratch_oneshot/` | Script tạm |
