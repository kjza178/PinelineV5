# Tìm mùa mới vẫn kéo download / mất base sau xoá Lib

- **Date:** 2026-11-06
- **Job / khu vực:** Hongguo2 Mùa mới · `films.db` · `/api/hg/library/seasons/discover`
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-06_hg-watchlist\` · zip `Z:\PinelineV2_backup_2026-11-06_1650.zip`

## Triệu chứng

1. Bấm cập nhật → Hongguo báo đang tải / `cần +N` / hàng nghìn tập (Update all = quét+tải).
2. Xoá Lib giải phóng ổ → mất base để biết franchise nào cần theo dõi mùa mới.
3. Board meta (S1, eps, ★, mùa cũ) chỉ là gợi ý — user chỉ cần meta, không tải.

## Root cause

- `/dl/library/update` dùng chung máy tải với Download; series còn folder thiếu tập → auto download.
- «Tìm mùa mới» trước đó chỉ đọc Lib trên đĩa → xoá folder = hết base.
- Không có bảng lưu meta sau delete.

## Evidence

- Live status: `eps_need` ~7245 khi Update all; `seasons.older/related/soon` chỉ meta (`sid,title,eps,season,score,base`).
- Smoke: `discover_new_seasons(max_cores=4)` → `download:false`, `found_n=6`, watchlist seed 34 từ Lib.

## Fix

- Bảng `hg_watchlist` trong `films.db` (`film_db.upsert_hg_watchlist*` / `known_hg_sids` / `watchlist_cores`).
- `delete_library_series`: trước xoá đĩa → ghi meta (`source=delete`, `on_disk=0`).
- `discover_new_seasons` + `POST /api/hg/library/seasons/discover` — search theo cores watchlist+films, **không** gọi Update all.
- Hongguo2 **Tìm mùa mới** → API discover; **Cập nhật thư viện** = Update all (tải) tách riêng.
- Sync V2/V4/V5.

## Recheck

1. **Restart :8801** (nạp route discover) rồi hard refresh `/hongguo2`.
2. Bấm **Tìm mùa mới** khi đang tải phim khác → vẫn chạy, không tăng hàng tải Hongguo.
3. Xoá 1 series khỏi Lib → `SELECT * FROM hg_watchlist WHERE on_disk=0` còn sid/core.
4. Discover lại → vẫn quét được franchise đã xoá; board chỉ **+ Thêm** mới submit tải.
5. **Pass nếu:** discover `download:false`; watchlist giữ meta sau delete; Update all không phải nút mặc định tìm mùa.
6. **Fail nếu:** Tìm mùa mới 404 (chưa restart) hoặc vẫn gọi `/dl/library/update`.

## Liên quan

- Decision: watchlist meta trong DB thay vì giữ video trên đĩa.
- APIs: `/api/hg/library/seasons/discover`, `/api/hg/library/delete` (trả `watchlist_saved`).

## Follow-up — Films UI tab + filter mới/cũ (~17:12)

- **Backup:** `Z:\PinelineV2_codebak\2026-11-06_films-ui-seasons\` · zip `Z:\PinelineV2_backup_2026-11-06_1706.zip`
- **UI:** Films UI tab **🆕 Mùa mới** (`?tab=seasons`) — gom franchise, mặc định ẩn mùa ≤ max đã biết; Hongguo2 banner thu gọn + link `http://127.0.0.1:8802/films/ui?tab=seasons`.
- **API:** `discover_new_seasons` tách `held`/`older` + `groups`/`max_known`; `GET /api/hg/library/watchlist`; sidecar `:8802` phục vụ watchlist/discover/submit proxy (Films UI chạy trên autopilot).
- **Recheck:** mở `/films/ui?tab=seasons` → Tìm mùa mới → `download:false`, pill MỚI; Update Lib trên Hongguo2 vẫn tách. **Pass nếu** watchlist `n≥1` và discover không đẩy hàng tải.

## Follow-up — filter JS + :8802/hongguo (~17:40)

- **Backup:** `Z:\PinelineV2_codebak\2026-11-06_films-seasons-filter\`
- **Bug:** `!!$('sn-show-related')?.checked` → `(!!el)?.checked` luôn falsy → lưới trống dù API có `related`/`newer`.
- **Fix:** `snChecked()`; auto `snDiscover()` khi mở tab; link Hongguo → `:8801`; sidecar GET `/hongguo|/hongguo2|/v5-map` → 302 `BASE`.
- **Recheck:** hard refresh `http://127.0.0.1:8802/films/ui?tab=seasons` → có pill; `http://127.0.0.1:8802/hongguo` → redirect `:8801` (không JSON not found).
- **Review nit (HIGH):** chuẩn hoá `franchise_core` cho cores + `_same_franchise` — tránh đẩy hết vào related khi core còn 「第N季」. Smoke sau fix: `newer≥2`, `download:false`.
- **Follow-up nits ([Review](9ca08280-5145-40dd-a927-fbde1734a57c)):** `watchlist_cores` stem; sidecar `max_cores` try/int; Films UI link `/hongguo2` (302→BASE); error text nêu :8802.

## Follow-up — tên Việt tab Mùa mới (~18:01)

- **Backup:** `Z:\PinelineV2_codebak\2026-11-06_seasons-title-vi\`
- **Fix:** sau discover gọi `/api/hg/translate-titles` (sidecar `title_mt`); hiện `core_vi` / `title_vi` (xanh); nút **Dịch Việt**.
- **Recheck:** hard refresh `?tab=seasons` → Tìm mùa mới → header + pill có dòng Việt. **Pass nếu** `VI N` trên status và pill `.sn-tvi`.

## Follow-up — VI lệch Hongguo/Thư viện (~18:12)

- **Nguyên nhân:** tab Mùa mới dịch **stem ngắn** (`聚宝仙盆`→«Dồi dào») bằng gtx; Thư viện dùng title đủ mùa + cache feeder; Đã làm dùng `films.db` title_vi (meta).
- **Fix:** `snApplyTitleVi` ưu tiên `/library` rồi `/films`, chỉ gtx phần thiếu; `core_vi` theo rule `library_view` (không dịch stem riêng).
- **Recheck:** hard refresh → tên trùng Thư viện với franchise đã có trên Lib.

## Follow-up — FIX agent verify (~17:41)

- **Status:** already patched live; no further code edit; **không restart :8802** (HTML đọc disk mỗi request; redirect Python đã active).
- **Trees:** `films_ui.html` V5 `static/ui/` ≡ V2 root (SHA256 E05373D1…); `agent_tele_cmd.py` V2 ≡ V4 ≡ V5 `agents/` (SHA256 5BCB828D…).
- **Evidence:**
  - Served `/films/ui?tab=seasons`: has `snChecked`, no `!!$('…')?.checked`, auto `snDiscover`, links `:8801/hongguo2`, empty-state `totN/totO/totR`.
  - `GET :8802/hongguo|/hongguo2|/v5-map` → **302** `Location: http://127.0.0.1:8801…`
  - `POST :8802/api/hg/library/seasons/discover` `{max_cores:4}` → `ok=true download=false` watchlist=34 newer/held=2 related=3 groups=3.
- **Pass nếu:** seasons tab hiện related/newer; `/hongguo` trên :8802 không còn JSON not found.
- **Fail nếu:** hard-refresh vẫn trống dù discover API có `related_n>0` (cache HTML cũ / SAI file path).
