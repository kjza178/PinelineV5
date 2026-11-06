# 2026-10-06 — Đợt 6 review: bảo trì (git, pytest, M3, dọn script chết)

Review gốc: `docs/reviews/2026-10-06-code-review.md` (đợt 6: `git init`, `pytest.ini` + test, dọn script/UI chết, M3 builder + test).

Backup trước khi sửa:

- Zip: `Z:\PinelineV2_backup_2026-10-06_1028.zip`.
- Bản gốc từng file: `Z:\PinelineV2_codebak\2026-10-06_batch6\` — `render.py`, `test_hardsub_asr.py`, `requirements.txt`.
- Script đã dọn: `Z:\PinelineV2_codebak\2026-10-06_batch6\attic\` (29 file). Các file này cũng có trong commit git đầu tiên `7657fea`.

Test: `python -m pytest -q` 75/75. Số này gồm 5 bộ `check_batch1–5` chạy dưới pytest, 16 test parser, 14 test M3 và 40 test cũ. Precheck của `restart_server.py` (compile 24 module + import thử) qua.

## Đã làm

### Git local

- `git init -b main` tại `Z:\PinelineV2`. Repo chỉ ở local: không có remote, không push.
- Đặt `core.autocrlf=false` cho repo, để git không đổi line ending của file đang chạy. `user.name` của repo là "PinelineV2 local"; email lấy theo cấu hình global.
- `.gitignore` loại khỏi git:
  - secret: `pineline.config.json`, `token*.json`, `client_secret*.json`, `cookies/`, `*.pem`, `*.key`, `.env`, `.claude/settings.local.json`;
  - dữ liệu: `work/` (junction sang D:, 187 GB), `data/`, `voices/`, `voice_samples/`;
  - file khoá/cờ: `.agent_lock`, `.restart_hold`, `.server_*.lock`, `.sidecar_*.lock`;
  - log, media, model, archive, `__pycache__`.
- `pineline.config.example.json`: bản sao `pineline.config.json` với các trường KEY/TOKEN/SECRET/PASS để rỗng. Máy mới thì chép thành `pineline.config.json` rồi điền key.
- Trước mỗi commit đều quét secret:
  - `D:\PinelineV2_tmp\git_b6.py` quét theo mẫu của `redact.py`;
  - `D:\PinelineV2_tmp\git_b6_real.py` đối chiếu với key LLM thật trong `pineline.config.json` và token Telegram thật.

  Kết quả: không file nào chứa key/token thật. Các chỗ khớp mẫu chỉ là:
  - tham chiếu biến `%HF_TOKEN%` trong `.bat` finetune;
  - chuỗi giả trong test `check_batch2.py`;
  - placeholder 8 ký tự cho LLM local trong `config.py`/`llm.py`/`run.bat`.
- Commit đầu `7657fea` "Baseline PinelineV2 sau review đợt 1-5 (06/10)", 363 file. Đợt 6 là commit thứ hai.

### pytest

- `pytest.ini`: `python_files = test_*.py`; `norecursedirs` bỏ `work`/`data`/`vendor`/`scripts`/`docs`…; `addopts = -p no:cacheprovider`; marker `batches`.
- `tests/test_review_batches.py`: chạy từng `scripts/check_batch*.py` như một test (marker `batches`), phủ S1/S2/S6/H1 và các mục khác của đợt 1–5. Bỏ qua bằng `pytest -m "not batches"`.
- `tests/test_agent_parser.py`: 16 ca cho parser tool call dạng chữ, chuyển từ `D:\PinelineV2_tmp\test_pycall.py`. Thêm các ca JSON tên ngắn, tool lạ, tham số dạng vị trí và biểu thức `__import__` (đều bị từ chối).
- `test_hardsub_asr.py::test_merge_rejects_neighbor_line`:
  - Test sai, code đúng. Câu hardsub kề bên đã bị loại đúng. Câu hardsub khớp chữ thì không chồng thời gian với đoạn ASR, và ASR chỉ khác dấu phẩy cuối, nên code cố ý giữ nguyên ASR (`_norm_zh` bằng nhau thì không thay).
  - Test viết lúc 22:02 ngày 20/09, trước bản code cuối cùng lúc 22:07.
  - Đã sửa test: giữ `那就放手一搏，`, không chứa chữ của câu bên cạnh, `replaced == 0`.
- `requirements.txt`: thêm `psutil`, `rapidocr-onnxruntime`, `pytest`.

### M3 — biểu thức che hardsub vượt giới hạn ffmpeg

- **Đo thật** (ffmpeg trong PATH, testsrc 640x360):
  - `if()` lồng 90 tầng OK, từ 100 tầng trở lên lỗi;
  - tổng `between()+…` phẳng tối đa 100 hạng tử ("Cannot allocate memory" khi ≥ 101);
  - gom ngoặc cân bằng: 1000 hạng tử vẫn OK.

  Bản ghép nhiều tập đổi vị trí sub (dò tối đa 300 mẫu) có thể vượt ngưỡng. Khi đó render fail, và vì đây không phải lỗi NVENC nên không có fallback. Dữ liệu thật hiện có (2ef87) mới chỉ cần độ sâu 1.
- **Sửa `render.py`**:
  - Thêm `_sum_expr(terms)` và `_pw_expr(ends, vals)`. Chuỗi ≤ 64 phần tử: giữ **đúng chuỗi cũ**. Dài hơn: tổng thành cây ngoặc cân bằng, `if()` thành cây nhị phân theo mốc thời gian (độ sâu khoảng log₂ n, cùng giá trị).
  - Dùng hai hàm này cho `_censor_expr`, `_stretch_track_filter` (crop/overlay y + enable), `_hardsub_track_filter` (enable từng ô), và `_hardsub_track_filter_dyn` (crop/overlay y + enable chuỗi phụ).
- **Kiểm tra**:
  - So với `render.py` gốc trên 2ef87 và 30 bộ ngẫu nhiên tới 60 đoạn: filter **giống hệt từng ký tự**, nên lần mux sắp tới của f9fe dùng y nguyên filter cũ.
  - 300 đoạn: bản cũ lỗi cả hai kiểu (stretch: "Cannot allocate memory"; blur dyn: "Nothing was written"), bản mới chạy được.
  - `tests/test_render_expr.py`:
    - giá trị tương đương tại mọi mốc;
    - độ sâu biểu thức;
    - ffmpeg thật nhận filter 300 đoạn ở testsrc 1920x1080.

### Dọn script chết

- Chuyển 29 file ở gốc sang `attic` (không xoá):
  - các script một lần `_bench_*`, `_diag_*`, `_probe_hg_*`, `_hg_dump`/`_hg_scan`, `_run_hybrid_*`, `_trial_oneshot_*`, `_test_ass_wrap1`, `_seed_agenttest`, `_crop_subs`, `_remux_both_wrap1`, `_preview_wrap1_fix`, `_merge_5060ti_config`, `_check_hg_preview_ui`;
  - `_patch_frame_wh.py` (còn ghi vào V1);
  - `_build_index3.py` và `_build_ui_variants.py` (chạy lại sẽ đè mất các sửa trực tiếp trong `index3.html`/`index*.html`);
  - `_hg_dl_ui.html` (bản dump UI Hongguo 240 KB, chỉ hai script probe dùng).
- Trước khi chuyển: không file nào được code/`.bat`/UI tham chiếu và không tiến trình nào đang chạy file đó.
- Giữ `_read_hg_ui_token.py` vì RUNBOOK đang dùng.
- **Không** đụng `index1.html`/`index2.html`/`index.html`, vì `server.py` vẫn có route phục vụ chúng. Việc gỡ route và UI cũ cần user quyết.

## Chưa làm (để sau, không làm khi đang có job chạy)

- Tách `server.py` (~6.000 dòng) thành router + services, tách `hongguo_bridge`, tách dispatch if-chain của agent thành registry.
- Bỏ hot-reload `render.py`/`config.py`…: cần state job/queue bền trước.
- Pin phiên bản trong `requirements.txt`, `film_db` đóng connection, gitleaks pre-commit.
- Gỡ UI cũ `index1/2.html`: cần user quyết.

## Hiệu lực

- `render.py`: **ngay** ở lần mux tới (server nạp lại mỗi lần mux). Với ≤ 64 đoạn filter giống hệt bản cũ.
- Các mục còn lại (git, pytest, test, dọn script) không ảnh hưởng tiến trình đang chạy.

## Recheck

```powershell
cd Z:\PinelineV2
$env:PYTHONIOENCODING='utf-8'
python -m pytest -q                    # 75 passed
python -m pytest -q -m "not batches"   # bỏ 5 bộ check đợt
git status --short                     # không có pineline.config.json / work / data
git add -A; python D:\PinelineV2_tmp\git_b6_real.py   # trước khi commit: "tổng file lộ: 0"
```
