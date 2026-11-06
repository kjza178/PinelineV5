# 2026-10-06 — Đợt 2 review: bảo mật + config một nguồn + LLM sập không để trống câu

Review gốc: `docs/reviews/2026-10-06-code-review.md` (S4, H4, H5, H6, A2, H7, M7, M8, M9, X2/X3 một phần).

Backup trước khi sửa:

- Zip: `Z:\PinelineV2_backup_2026-10-06_0908.zip` (trước sửa). Sau sửa: `Z:\PinelineV2_backup_2026-10-06_0930.zip` (đã che secret).
- Bản gốc từng file: `Z:\PinelineV2_codebak\2026-10-06_batch2\`:
  - code: `server.py`, `agent_tele_cmd.py`, `hongguo_bridge.py`, `agent_hongguo.py`, `llm.py`, `translate.py`, `translate_alts.py`, `config.py`, `agent_core.py`, `agent_feeder.py`, `batch_config.py`, `agent_autopilot.py`;
  - UI: `index.html`, `index3.html`, `static\app.js`;
  - cấu hình: `run_v2.bat`, `run_tele_cmd.bat`, `config.json`, `settings.local.json`;
  - khác: `snapshot.py`, `test_queue_jobs_api.py`.

  (`config.py`/`agent_core.py`/`agent_feeder.py` lấy từ zip 0908 vì quên chép trước khi sửa — nội dung trùng bản trước sửa.)

Test: `scripts/check_batch2.py` (69 kiểm tra, không đụng server/sidecar đang chạy) — 69/69 PASS. `pytest tests` 23/23. `scripts/check_batch1.py` ALL PASS.

## Triệu chứng / rủi ro

| Mã | Rủi ro |
|---|---|
| S4 | Trang web bất kỳ mở trên máy (hoặc DNS rebinding) gọi được `/api/*` của :8801: xoá job, chạy queue, đọc file. |
| H4 | `/api/hg/*` nhận `base` từ client → server gọi tới URL tuỳ ý (SSRF) kèm UI token Hongguo. |
| H5 | Tên bộ trong preview/poster/merge ghép thẳng vào `D:\Lib` → `..\`, `C:x` thoát khỏi thư viện. |
| H6 | `escapeHtml` không thoát `'`; tên nhóm/`group_id` chèn vào `onclick='...'` → chạy JS tuỳ ý trong UI. |
| A2 | Sidecar :8802 trả `Access-Control-Allow-Origin: *` → web lạ điều khiển Auto-pilot/Telegram. |
| H7 | API key 9router nằm trong `llm.py` (docstring), `run_v2.bat`, `run_tele_cmd.bat`, `config.json`, `.claude\settings.local.json`; `snapshot.py` đưa tất cả vào zip backup. |
| M7 | LLM sập → `_translate_safe` coi như lỗi parse, chia lô tới từng câu, gọi lại hàng chục lần rồi **để trống câu** và vẫn xong stage. |
| M8 | `llm.chat_with_meta` dùng `BASE_URL/API_KEY/MODEL` đóng băng lúc import; `translate.MODEL/REVIEW_MODEL` cũng vậy → sửa `pineline.config.json` không có hiệu lực tới khi restart. |
| M9 | `LOCAL_LLM_BASE_URL` mặc định `:8083` (llama-server) nhưng `_ollama_chat` gọi `/api/chat` của Ollama. |
| X2/X3 | Agent (server, sidecar, feeder) mỗi nơi đọc `AGENT_*`/`LLM_*` một kiểu, `.bat` chép key riêng. |

## Root cause → sửa

- **S4** `server.py` — middleware `_local_only_guard` (ngay sau `app = FastAPI`):
  - `Host` không phải `127.0.0.1`/`localhost`/`::1` → 403 (mọi đường dẫn);
  - trên `/api/*`: có `Origin` mà không local (kể cả `null`) → 403; không có `Origin` nhưng `Referer` không local → 403.
  - Script/curl/sidecar không gửi `Origin` nên vẫn qua. Cả 3 dịch vụ chỉ nghe `127.0.0.1` nên không chặn truy cập LAN nào đang dùng.
- **H4** `server.py` `_hg_base()` luôn trả `hg.DEFAULT_BASE`, bỏ qua `base` client gửi.
- **H5** `hongguo_bridge.safe_child(root, name)` → `None` nếu tên rỗng, `.`/`..`, chứa `/ \ :` hoặc `..`, hoặc cha ≠ root. Dùng trong `resolve_preview_path`, `resolve_poster_path`, `merge_queue_add` (bỏ qua tên xấu), `_merge_worker` (ghi lỗi vào lịch sử, đi tiếp).
- **H6** `index.html`, `index3.html`, `static/app.js`: `escapeHtml` thoát thêm `'`→`&#39;`; `renameGroup(${JSON.stringify(gt)})`, `runGroupQueue/toggleGroup/dissolveGroup('${j.group_id}')` đều qua `escapeHtml`. Giữ nguyên encoding/BOM. Có hiệu lực ngay (Ctrl+F5).
- **A2** `agent_tele_cmd.CtrlHandler`: `_blocked()` (Host/Origin/Referer như S4, trả 403 JSON) gọi đầu `do_OPTIONS/do_GET/do_POST`; `_cors()` chỉ echo Origin local + `Vary: Origin`, bỏ `*`.
- **X2/X3** `config.py`:
  - `AGENT_FILE_FIRST_KEYS` (`AGENT_BASE_URL/API_KEY/MODEL/FALLBACK_MODEL`) — file trước env như key LLM;
  - `llm_settings()` (job) và `agent_llm()` (agent: `AGENT_*` → `LLM_*` → mặc định). `agent_core._llm_cfg`/`_chat_turn` và `agent_feeder._llm_cfg` dùng `config.agent_llm()`.
- **M8** `llm.py` `_settings()` đọc `config.llm_settings()` lúc gọi; `chat()` và `chat_with_meta()` dùng nó. `translate.py` `_tmodel()`/`_rmodel()` thay mọi `model or MODEL` / `REVIEW_MODEL`; plan dùng `_cfg_get("LLM_MODEL")`. `translate_alts.py` dùng `_tmodel()`. `server.py` dịch tiêu đề dùng `config.get("TRANSLATE_MODEL")`.
- **M9** `LOCAL_BASE_URL` mặc định `http://127.0.0.1:11434/v1` (Ollama).
- **M7**:
  - `llm.LLMUnavailable(RuntimeError)`: ném khi hết retry vì mạng/429/5xx, thiếu key, Ollama mất kết nối (trước trả `""`).
  - HTTP 400/413/422 → `RuntimeError` thường ngay, không retry (lô quá dài → splitter chia nhỏ như cũ).
  - `translate._translate_safe`, vòng review, nhánh oneshot→batch và `translate_alts` ném tiếp `LLMUnavailable`. Khối ngoài `run_translate` đã có salvage: lưu phần đã dịch, stage về `pending` + `last_error` → bấm Tiếp tục khi LLM lên lại.
- **H7** (secret):
  - Xoá key khỏi docstring `llm.py`, `config.json` (`pineline.config.json` vẫn giữ — nguồn duy nhất), `run_v2.bat` (cùng `LLM_*`/`TRANSLATE_MODEL` đã chết vì file-first), `run_tele_cmd.bat` (`AGENT_BASE_URL/API_KEY`, nay lấy qua `config.agent_llm`). Giữ `AGENT_MODEL` + `AGENT_FALLBACK_MODEL=openclaw`.
  - `.claude\settings.local.json`: 7 chuỗi key trong danh sách lệnh cho phép → `***REDACTED***`.
  - `D:\PinelineV2_tmp\redact.py` (mới) + `snapshot.py`: file text vào zip đều qua `redact()` (key `sk-…`, `GOCSPX-…`, `ya29.…`, refresh token `1//…`, token Telegram, giá trị của biến tên `*API_KEY*/*TOKEN*/*SECRET*/*PASSWORD*`), bỏ thêm `.env`.
  - Zip 0930: 15 file được che, quét lại 0 secret.
- `tests/test_queue_jobs_api.py`: `TestClient(base_url="http://127.0.0.1:8801")` — Host mặc định `testserver` giờ bị guard chặn.

## Cần restart

| Thay đổi | Hiệu lực |
|---|---|
| UI escape (H6) | Ngay (Ctrl+F5) |
| `.bat`, `config.json`, `settings.local.json`, `snapshot.py` | Ngay |
| `server.py` (S4, H4), `config.py`, `llm.py`, `translate*.py`, `agent_core.py`, `hongguo_bridge.py` (H5 trong server) | Restart server |
| `agent_tele_cmd.py` (A2), `agent_feeder.py`, `config.py` | Restart sidecar |

Job f9fe đã qua bước dịch (đang TTS) nên không bị ảnh hưởng; 3a2e dịch sau lần restart hẹn giờ.

## Còn lại / lưu ý

- Key 9router và OAuth secret từng nằm trong các zip cũ (`Z:\PinelineV2_backup_2026-10-05_0133.zip`, `…_0834.zip`, `…_0908.zip`) và lịch sử chat. Zip cũ **không** sửa. Khuyến nghị đổi key 9router.
- Khôi phục từ zip mới: `pineline.config.json` trong zip đã bị che key → điền lại key thật.
- `openclaw` vẫn là fallback agent (quyết định 10-05).

## Recheck

```powershell
cd Z:\PinelineV2
python scripts\check_batch2.py        # 69 PASS
python -m pytest -q -p no:cacheprovider tests
# sau restart server: Host lạ phải 403
python -c "import urllib.request as u;r=u.Request('http://127.0.0.1:8801/api/queue/jobs',headers={'Origin':'http://evil.com'});print(u.urlopen(r).status)"   # HTTPError 403
```
