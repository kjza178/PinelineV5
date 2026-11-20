# Auto-publish: hỏi Telegram trước khi upload (phần 1)

- **Date:** 2026-11-20
- **Job / khu vực:** `auto_publisher` · `agent_tele_cmd` `/publish`
- **Status:** fixed (cần restart :8801 + :8802)
- **Backup:** `Z:\PinelineV2_codebak\2026-11-20_publish-ask\`

## Triệu chứng

Mux/Full xong tự xếp upload — không có bước hỏi.

## Fix

- Config `ask_before_upload` (+ `/publish ask|auto|on|off|…`)
- `enqueue_publish`: ask-mode → `offer_publish_ask` + Telegram nút Upload/Skip/Private/Public; TTL 60' → skip
- Callback `pub:y|s|p|u:<job_id>` → `confirm_publish_ask`
- Scan không up thầm khi ask-mode
- Test `tests/test_publish_ask.py` (4) + dedup (4) = 8 pass

## Recheck

1. Restart :8802 rồi :8801 (nạp hook + mux trigger)
2. Telegram: `/publish ask` → status hiện mode ask
3. Mux xong 1 job (hoặc `enqueue_publish` từ API) → tin «Sẵn sàng đăng?»
4. Bấm ✅ → job vào queue; ⏭ → không up
5. **Pass nếu:** ask không xếp hàng trước khi bấm; `/publish auto` lại up ngay khi enabled
6. **Fail nếu:** ask-mode vẫn tự up; hoặc nút không phản hồi

## Liên quan

- Phần 2 sau: `/upload` list chọn job
- Không làm `/lib` / gộp parts UI (user chốt)
