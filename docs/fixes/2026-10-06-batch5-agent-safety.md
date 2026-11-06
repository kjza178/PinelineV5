# 2026-10-06 — Đợt 5 review: agent an toàn hơn

Review gốc: `docs/reviews/2026-10-06-code-review.md` (A7, A8, A9, A13, tầng quyền + xác nhận tool phá huỷ, cắt kết quả tool, SYSTEM mâu thuẫn, X3 phần `agent_v2`).

Backup trước khi sửa:

- Zip: `Z:\PinelineV2_backup_2026-10-06_1009.zip`.
- Bản gốc từng file: `Z:\PinelineV2_codebak\2026-10-06_batch5\` — `agent_tele_cmd.py`, `agent_core.py`, `agent_hongguo.py`, `agent_feeder.py`, `agent_autopilot.py`, `server.py`, và cả thư mục `agent_v2\` (đã xoá khỏi project).
- Lúc 10:20 lỡ chép bản đã sửa của `agent_hongguo.py` và `agent_feeder.py` đè lên bản gốc trong thư mục backup. Đã lấy lại bản gốc từ zip 1009 và kiểm tra lại: bản gốc không có `detect_flow_mode` / `lib_verb`. Bốn file còn lại khớp từng byte với zip.

Test: `scripts/check_batch5.py` 128/128 (mock LLM/Telegram/Hongguo, không đụng server/sidecar/hàng đợi thật). Kết quả các đợt trước: đợt 1 ALL PASS, đợt 2 69/69, đợt 3 35/35, đợt 4 56/56. Pytest 39/40; test hỏng `test_hardsub_asr.py::test_merge_rejects_neighbor_line` đã hỏng từ trước, để đợt 6. Precheck của `restart_server.py` (compile 24 module + import thử) qua.

## Triệu chứng

| Mã | Triệu chứng |
|---|---|
| A8 | Telegram: chữ trơn không có `/` vẫn đổi trạng thái — `stop` (dừng hết + tắt Auto-pilot), `reset` (config batch về mặc định), `set`, `feed on/off`, `heal`, `tick`, `hg 2` / `hg auto …` / `hg clean …` (tải + gộp + **dọn tập**), `lib add …`. Câu chat có chữ "auto" và "pilot" (vd "đừng bật auto pilot") bị đoán là lệnh và **bật Auto-pilot**. |
| A13 | `hg_auto_flow` chọn nguồn theo chuỗi con: tên phim chứa "kho", "lib", "top", "hot", "rank" (vd «Kho Báu…», «Hot Mom…») → bốc bừa bộ đầu thư viện / đầu BXH rồi gộp + dọn tập. |
| A7 | Agent gọi `hg_auto_flow` chạy **đồng bộ** trong request `/api/agent/chat` (tải + gộp tới 90 phút) → request treo, sidecar timeout 180 s, user gửi lại thì chạy thêm một flow cùng bộ. |
| Quyền | Telegram gọi agent với `allow_mutate=True` cố định → model hiểu sai một câu là chạy ngay `queue_stop`, `stop_job`, `hg_clean`, `hg_merge`, chạy lại `force` (xoá clip/ASR), reset config, heal hàng loạt. |
| A9 | Sidecar xử lý tin Telegram tuần tự: đang chờ agent (tới 180 s) thì `/stop` cũng phải chờ. |
| Context | Kết quả tool (status indent, library, rank 100…) đưa nguyên vào context → model nhỏ tràn context. |
| SYSTEM | Nhắc tool `qa_override` không tồn tại; quy tắc 3 bảo "chỉ khi user xác nhận" cho một tool ma. |
| Khác | `/agent <câu>` lấy câu từ bản đã hạ chữ thường → hỏng tên/ID có chữ hoa. Hết số bước không nói đã chạy thao tác nào. |
| X3 | `agent_v2/` bản cũ lệch (cổng/volume cũ, không chặn `queue_stop`), không còn ai import. |

## Sửa

- **`agent_tele_cmd.py`**:
  - `_slash_hint(text)` chạy trước mọi nhánh, trong cả `handle_command` lẫn `telegram_loop`. Chữ trơn đổi trạng thái được xử lý như sau:
    - Câu ngắn (≤ 3 từ, không có `?`) hoặc có tiền tố `hg`/`lib` → trả lời "Lệnh thay đổi trạng thái cần dấu /: gõ /…" và **không chạy**.
    - Câu dài → chuyển cho agent chat. Tool phá huỷ vẫn phải bấm ✅.
    - Phần chỉ đọc vẫn gõ trơn được: `status`, `config`, `running`, `films`, `feed` / `feed status`, `hg rank`, `hg search`, `lib`, `lib 2`.
  - Bỏ nhánh đoán "auto"+"pilot". `autopilot on/off` gõ trơn → gợi ý `/on` / `/off`. `autopilot` gõ trơn → chỉ hiện trạng thái.
  - `_agent_ask(msg, uid)` / `_agent_reply` dùng chung cho chat tự nhiên, `/agent` và phần chat của `/hg`.
    - Có `uid` (Telegram) → `require_confirm=True`, và gửi mỗi thao tác chờ một tin kèm nút **✅ Chạy / ❌ Huỷ** (`agc:<id>:y|n`).
    - HTTP `/cmd` (chỉ nhận local, không có uid) giữ như cũ.
  - `_on_callback` `agc:` → `_confirm_callback` (chạy trong thread) gọi `/api/agent/confirm` rồi sửa tin thành "✅ Đã chạy …" / "🚫 Đã huỷ …" và bỏ nút.
  - A9: tin Telegram xếp vào worker FIFO `_TG_WORK`. `/stop`, `/stopqueue`, `/off`, `/status`, `/running`, `/jobs`, `/help` chạy ngay trên luồng poll (`is_priority_cmd`).
  - `/agent <câu>` giữ nguyên hoa/thường.
  - `/hg <số>`, `/hg auto …` và nút "làm A-Z" đi qua `start_auto_flow_bg`; trùng bộ đang chạy thì báo "đang chạy … phút". Nút "làm trọn bộ các phần" vẫn chạy tuần tự, có truyền `mode="name"`.
- **`agent_hongguo.py`**:
  - `detect_flow_mode(target)`: chỉ nhận **cả chuỗi** là từ khoá — thư viện (`lib`, `thư viện`, `chưa làm`, `kho`…) hoặc BXH (`top`, `bxh`, `rank`, `hot`, `trending`, `leaderboard`, `catalog`, có thể kèm số). Mọi chuỗi khác là tên/ID.
  - `tool_hg_auto_flow(..., mode=None)`: nhận `name | lib | rank`; bỏ trống thì gọi `detect_flow_mode`. Shortcut số thứ tự BXH chỉ áp cho `name`. Schema tool có `mode` (enum).
  - `start_auto_flow_bg(rt, args, notify)`: chạy flow trong thread nền và trả `started` ngay.
    - Khoá chống trùng theo target: `name:<tên chuẩn hoá>`, hoặc `lib` / `rank`. Trùng thì trả `already_running` kèm số phút đã chạy.
    - Lỗi được báo qua `notify`.
  - `handle_hongguo_tool` `hg_auto_flow` → `start_auto_flow_bg(..., notify=rt.notify)`. Thêm `running_auto_flows()`.
- **`agent_core.py`**:
  - `tool_tier(name, args)` → `read | mutate | confirm`. Các trường hợp `confirm`:
    - `queue_stop`, `stop_job`, `hg_merge`, `hg_clean`, `hg_auto_flow`;
    - `run_stage` / `tts_run` / `asr_run` / `ocr_run` khi có `force`;
    - `config_set reset`;
    - `script_edit_many` trên 20 dòng;
    - `heal_failed_batch` / `av_sync_heal_batch` khi `apply`;
    - `heal_job` khi `apply` với `aggressive`;
    - `library merge`;
    - `feed on/off/set`.
  - Kho chờ xác nhận: `park_action` (trùng tool+args thì dùng lại id), `pending_actions`, `confirm_action(id, approve)`. Hết hạn sau 15 phút; mỗi id chỉ chạy một lần.
  - `run_agent(..., require_confirm=False)`: khi bật, tool `confirm` **không chạy** mà trả `awaiting_user_confirm`; `AgentResult.confirms` liệt kê các thao tác đang chờ.
  - `clip_tool_result`: kết quả tool đưa vào context tối đa `AGENT_TOOL_RESULT_MAX` (mặc định 6000 ký tự), kèm ghi chú phần bị cắt. `steps` vẫn giữ bản xem trước 800 ký tự như cũ.
  - SYSTEM: thay tool ma `qa_override` bằng `qa_gate_set override_pass=true` (chỉ khi user nói rõ). Quy tắc 13 thêm `mode` và giải thích việc chạy nền. Thêm quy tắc 15: khi nhận `awaiting_user_confirm` thì báo đã gửi nút, không gọi lại tool, không nói là đã làm xong.
  - `Runtime.notify`.
  - Hết số bước → câu trả lời liệt kê các tool đã chạy làm thay đổi trạng thái (bỏ tool chỉ đọc và tool đang chờ ✅).
- **`server.py`**:
  - `AgentChatReq.require_confirm`; `/api/agent/chat` trả `confirms`.
  - `GET /api/agent/pending`, `POST /api/agent/confirm {id, approve}` (id lạ hoặc hết hạn → 404).
  - `_agent_notify` (Telegram qua `agent_watch.telegram_send(force=True)`, không gửi được thì in log) gắn vào `Runtime.notify`.
- **`agent_autopilot.py`**: `agent_chat(..., require_confirm)`, `agent_confirm(base, id, approve)`.
- **`agent_feeder.py`**: `lib_verb(word)` (động từ `/lib` đổi trạng thái), dùng cho `_slash_hint`.
- **Xoá `agent_v2/`** (bản sao trong thư mục backup batch5). Ngoài `docs/` không còn chỗ nào tham chiếu.

## Hành vi mới cần biết (Telegram)

| Gõ | Trước | Giờ |
|---|---|---|
| `stop` | Dừng hết + tắt Auto-pilot | "gõ /stop" |
| `reset`, `set …`, `tick`, `heal` | Chạy | "gõ /…" |
| `feed on`, `feed now` | Chạy | "gõ /feed …" (`feed` / `feed status` vẫn xem được) |
| `hg 2`, `hg auto …`, `hg clean …`, `lib add 2` | Chạy | "gõ /hg …", "gõ /lib …" |
| `autopilot on` / câu có "auto pilot" | Bật Auto-pilot | Gợi ý `/on` / chuyển cho agent |
| Chat "dừng job X đi" | Agent dừng ngay | Agent gửi nút ✅/❌, bấm ✅ mới dừng |
| Chat "làm bộ Kho Báu …" | Có thể bốc bộ đầu thư viện | Tìm đúng tên; flow chạy nền, tiến độ báo Telegram |
| `/stop` khi agent đang nghĩ | Chờ tới 180 s | Chạy ngay |

Panel Agent trên UI (`allow_mutate` bật tay) không đổi: tool phá huỷ vẫn chạy thẳng vì user đang ngồi ở máy và đã tick cho phép.

## Chưa làm trong đợt này

- Dispatch if-chain ~370 dòng trong `agent_core._dispatch` chưa tách bảng; nạp tool theo nhóm chưa làm. Cả hai để sau khi hết job chạy (đợt 6 không tách file lớn khi đang có job).
- UI panel chưa hiện nút xác nhận (vì không cần: UI không bật `require_confirm`).
- X4 còn lại (feeder `_requeue_front`, `feed_tick`, `hg_auto_flow` xếp hàng) như đợt 4.

## Hiệu lực

- **Sau restart server** (restart hẹn giờ): `agent_core.py`, `agent_hongguo.py` (bản trong server), `server.py`. Server **không** nạp lại các module agent, nên f9fe không bị ảnh hưởng.
- **Sau restart sidecar** (`--sidecar` của restart hẹn giờ): `agent_tele_cmd.py`, `agent_autopilot.py`, `agent_feeder.py`, `agent_hongguo.py`.
- Sidecar mới + server cũ: `require_confirm` bị server cũ bỏ qua (pydantic bỏ trường lạ) → hành vi như cũ cho tới khi server restart. Hai bên được restart cùng lúc nên không có khoảng hở này.

## Recheck

```powershell
cd Z:\PinelineV2
$env:PYTHONIOENCODING='utf-8'
python scripts\check_batch5.py        # 128 PASS
python scripts\check_batch4.py        # 56 PASS
python -m pytest -q -p no:cacheprovider
```

Sau restart, trên Telegram:

1. Gõ `stop` → phải nhận "gõ /stop".
2. Chat "dừng hàng chờ" → nhận nút ✅/❌; bấm ❌ → "Đã huỷ" và hàng chờ không đổi.
3. `GET http://127.0.0.1:8801/api/agent/pending` liệt kê các thao tác đang chờ.
