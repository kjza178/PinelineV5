# Hongguo2: Mùa mới bị clip + Update all hiện 0/? + Ops chèn Discover

- **Date:** 2026-11-06
- **Job / khu vực:** `/hongguo2` UI — seasons board + Ops layout
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-06_hongguo2-layout2\` · zip `Z:\PinelineV2_backup_2026-11-06_1616.zip`
- **Follow-up backup:** `Z:\PinelineV2_codebak\2026-11-06_hongguo2-update-ux\` · zip `Z:\PinelineV2_backup_2026-11-06_1631.zip`

## Triệu chứng

1. Board Mùa mới gần như trống — pills bị CSS `max-height:72px/120px` cắt mất.
2. Bấm Update all → hint `0/?` vì `checked`/`to_check` thường undefined.
3. Cột Ops chiếm quá nhiều ngang; seasons nằm trong Ops cạnh library/queues.

## Root cause

- `.ops-sec.seasons{max-height:72px}` (+ `:has(...){120px}`) clip toàn bộ `#libSeasons`.
- Progress chỉ đọc `d.checked`/`d.to_check`, bỏ qua `seasons` buckets / `done`/`total` / `series` / album counts.
- IA 3 khối dọc trong Ops (seasons+lib+queues) tranh chiều cao với Discover hẹp.

## Evidence

- Grep trước fix: `max-height:72px` / `120px` trên `.ops-sec.seasons`.
- Hint loop: `d.checked+'/'+(d.to_check||'?')` → `undefined/?` → `0/?`.

## Fix

- `hongguo2.html` (V2 → sync V4 root + V5 `static/ui/`):
  - Grid `minmax(0,1.6fr) minmax(300px,0.85fr)`.
  - **Mùa mới** → banner full-width dưới topbar, collapsible; `#libSeasons` scroll `max-height:~220px`.
  - Ops tabs: **Thư viện | Hàng đợi** (default Thư viện); Hàng đợi giữ sub-tabs Tải|Gộp.
  - `lsnStatusVn` / progress card VN: «Đang quét thư viện… N series» / «Xong: A gợi ý · B sắp ra».
  - Update all + board trống → hiện `#seasonsProgress` card.
  - `lsnRender`: có nội dung → mở banner (`_lsnHide=false`) trừ khi user ✕ (`_lsnUserClosed`).

## Recheck

1. Hard refresh `/hongguo2` (Ctrl+F5).
2. Banner **Mùa mới** nằm dưới topbar; Ops chỉ 2 tab Thư viện|Hàng đợi; Discover rộng hơn.
3. Bấm **Cập nhật tất cả** khi board trống → thấy progress card (không chỉ hint nhỏ; không `0/?`).
4. Khi seasons có pills → banner mở, pills nhìn thấy (scroll trong ~220px).
5. **Pass nếu:** không còn clip 72px; progress VN; layout banner+tabs như trên.
6. **Fail nếu:** pills vẫn bị cắt; hint vẫn `0/?`; seasons vẫn nằm trong cột Ops.

## Liên quan

- Trước đó: `docs/fixes/2026-11-06-hg-new-seasons.md`, Ops hẹp changelog ~15:16

## Follow-up (~16:35) — Update vẫn “trống” vì `seasons: null`

### Triệu chứng

Sau layout2: banner Mùa mới có nhưng bấm Cập nhật tất cả vẫn “không thấy gì” / progress vô nghĩa. Live `/api/hg/status` khi library update: `seasons: null`, tiến độ ở root `checked`/`to_check`, `series[]` (status checked|queued|downloading|done), `found`, `phase`.

### Root cause

UI chỉ render board từ `st.seasons` buckets. Hongguo Downloader (live) không trả `seasons` object trong phase library-update — chỉ series checklist + counters root → board trống, progress card ẩn sớm.

### Fix

- Progress **live trên banner head** (`#seasonsLive`) + card body; banner `.busy` cao hơn.
- `lsnIsScanning` / `lsnStatusVn` đọc `checked`/`to_check`/`found`/`phase`/`eps_*`.
- Fallback `lsnScanFallbackHtml`: khi không có seasons board → liệt kê series theo status.
- Grid Ops cân hơn `1.15fr / 1fr`. Sync V2 root + V4 root + V5 `static/ui/hongguo2.html`.

### Recheck

1. Hard refresh `/hongguo2` (Ctrl+F5) trên :8801.
2. Bấm **Cập nhật tất cả** → head hiện `Đang quét… N/M · tìm thấy X · phase`; body hiện nhóm Đã kiểm / Chờ tải / Đang tải.
3. **Pass nếu:** không còn banner trống khi `seasons=null` và có `series`; không còn phụ thuộc `seasons.state`.
4. **Fail nếu:** head progress vẫn ẩn; board vẫn empty trong lúc `running` + `series.length>0`.

## Follow-up (~16:45) — «job khác» + user chỉ muốn thông tin mùa mới

### Triệu chứng

Hint `Hongguo đang chạy job khác — chờ xong rồi Update all`. User chỉ muốn lấy thông tin series/mùa mới, không tải lại toàn bộ.

### Root cause

1. Nút cũ gọi `POST /dl/library/update` — đúng nghĩa Hongguo **Update all = quét + tải tập thiếu** của series đã có; chung 1 máy tải → Hongguo từ chối khi `running` (`a download/update is already running`).
2. Pineline chặn cứng mọi `running` bằng câu «job khác» — kể cả khi job chính là library update.

### Fix

- Nút chính **🔎 Tìm mùa mới** → `lsnDiscoverNew`: đọc `/api/hg/library` + `/api/hg/search?expand=false` theo từng core — **chỉ thông tin**, board `held`/`related`, tải khi bấm **+ Thêm**.
- Nút phụ **↻ Cập nhật thư viện** = Update all cũ; nếu đang `mode=library` thì theo dõi, không POST chồng; nếu đang tải mode khác → gợi ý dùng «Tìm mùa mới».
- Sync V2/V4/V5 `hongguo2.html`.

### Recheck

1. Hard refresh `/hongguo2`.
2. Bấm **Tìm mùa mới** khi đang tải phim khác → vẫn chạy, hiện gợi ý, không tải.
3. Bấm **Cập nhật thư viện** khi đang tải → hint giải thích; khi idle → Hongguo quét+tải tập thiếu.
4. **Pass nếu:** không còn câu «job khác»; có 2 nút tách info vs download.
