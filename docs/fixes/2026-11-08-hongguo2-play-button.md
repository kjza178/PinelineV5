# Hongguo2 detail thiếu nút Play (WinUI)

- **Date:** 2026-11-08
- **Job / khu vực:** `/hongguo2` detail sheet · `/api/hg/preview`
- **Status:** fixed
- **Backup code:** `Z:\PinelineV2_codebak\2026-11-08_hongguo2-play-scroll\`

## Triệu chứng

Detail WinUI có nút **Play** cạnh quality; hongguo2 chỉ có pills chất lượng + Download — không có Play.

## Root cause

`hongguo2.html` chưa port nút Play / preview modal từ `hongguo.html` (CDN free via `/api/hg/preview`).

## Fix

- Nút `#dPlay` (pill ▶ Play) trong hàng Quality.
- Overlay `#prevMask` + iframe/video; Ep tabs; Retry.
- Follow-up scroll: `maybeBrowseMore` (scroll + IO + fill viewport) — hết kẹt 24 card.

## Follow-up — Play bấm không chạy (2026-11-08 ~07:30)

- **Root cause:** `/api/hg/preview` chỉ gọi Hongguo `:8000` `/dl/preview` — cổng tắt → 502. WinUI Play thật = RPC `playback.prepare` (cần license) → file `hongguo-player/*.mp4`.
- **Fix:** `hongguo_rpc.playback_prepare` + stream `/api/hg/playback/stream?session=`; bridge fallback RPC khi :8000 chết; UI dùng `<video>` cho URL local. Backup `…_hongguo2-play-rpc\`. **Restart :8801** (đã).
- **Evidence:** `GET /api/hg/preview?…` → `ok:true url=/api/hg/playback/stream?session=1`; stream `200 video/mp4`.

## Recheck

1. Hard refresh `/hongguo2`.
2. Mở phim → **Play** → chờ prepare (lần đầu có thể ~10–60s) → video phát.
3. Browse cuộn load thêm.
4. **Pass nếu:** Play phát được (RPC local hoặc :8000 CDN).
5. **Fail nếu:** modal báo lỗi license / timeout mãi.

## Follow-up — Preparing quá lâu / Preview failed (~07:50)

- **Root cause:** UI gửi quality 1080p vào prepare → tải nặng, chờ lâu rồi fail. Không cache.
- **Fix:** Preview cố định **480p**; cache đĩa; async `POST /api/hg/preview/start` + `GET /job` hiện `%` + giây. Backup `…_hongguo2-play-fast\`. **Restart :8801** (đã).
- **Evidence:** poll 0→100% ~15s; start lại `cached:true` ~9ms.

## Liên quan

- License prove: Settings hoặc `POST /api/hg/license/prove`.
- `docs/fixes/2026-11-08-hongguo2-browse-scroll.md`
