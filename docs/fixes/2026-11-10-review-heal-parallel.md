# REVIEW CLI song song + heal làm UI mất/soát % tụt

- **Date:** 2026-11-10
- **Job / khu vực:** `60892cc63cb7_p01` / `p02`, stage translate REVIEW gpt-6; `server._heal_stale_running`; UI `static/app.js` stepRow
- **Status:** fixed (ops + heal/UI); progress race còn cần theo dõi
- **Backup:** zip `Z:\PinelineV2_backup_2026-11-10_2057.zip`; codebak `Z:\PinelineV2_codebak\2026-11-10_heal-review-cli\`

## Triệu chứng

- UI hiện 2 job soát song song; rồi “mất” soát / về Sẵn sàng / Chờ.
- % soát nhảy lùi (vd 42% → 35%) dù CLI log vẫn tiến.

## Root cause

1. Agent chạy **2 CLI** `run_review_gpt6_60892.py` cùng lúc — trái mặc định 1 thread / 1 job.
2. CLI không vào `_PROCS` → `_heal_stale_running` hạ `translate` `running` → `pending` (`healed=stale_running_no_artifact`) → UI chỉ vẽ “soát %” khi `running`.
3. Ghi đè `manifest.json` raw (restore status) đọc được bản cũ → **giảm** `review_done` trên đĩa; cộng merge3 làm UI nháy số thấp.

## Evidence

- Proc: 2× `run_review_gpt6_60892.py` p01+p02; sau fix chỉ còn p01.
- Manifest: `healed=stale_running_no_artifact`, `status=pending` trong lúc CLI còn Established `:3377`.
- Poll: `cur_text` ghi 2240 nhưng `review_done=1840` (stomp/merge).

## Fix

- Ops: **kill p02 CLI**; p02 `pending` chờ xong p01 (1 job).
- `server._heal_stale_running`: bỏ qua translate đang `review` + `review_progress<100` + `updated_at` < 900s.
- `static/app.js` stepRow: vẫn hiện `soát %` khi mid-review dù status pending.
- Sync V2 → V4/V5. **Không** ghi đè full manifest khi CLI đang chạy.

## Recheck

1. Chỉ 1 process `run_review_gpt6_60892.py`.
2. Hard-refresh UI: p01 hiện soát tăng dần; p02 Chờ/paused.
3. Sau **Restart :8801** (nạp heal): status không bị heal về pending khi `updated_at` tươi.
4. **Pass nếu:** % không tụt vì heal; 1 job.
5. **Fail nếu:** lại 2 CLI, hoặc heal hạ pending khi review còn fresh.

## Liên quan

- REVIEW model `chatgpt/gpt-6`; queue_opts `review_backup=aurora_parallel`
- Follow-up: tránh raw rewrite manifest; cân nhắc monotonic `review_done = max(old,new)`
