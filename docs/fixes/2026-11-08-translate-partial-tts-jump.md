# Dịch dừng giữa chừng → nhảy TTS với số câu dở (vd 64/398 vs ASR 2698)

- **Date:** 2026-11-08
- **Job / khu vực:** `2cd10c3fa86d_p01` · `_auto_gpu` / `run_translate` salvage / `_do_tts`
- **Status:** fixed (cần restart :8801)

## Triệu chứng

ASR xong (vd **2698** câu). Dịch bị dừng giữa chừng. Pipeline vẫn nhảy **Lồng tiếng** và chỉ TTS phần đã dịch (UI `64/398`) → lệch / sai so với full script.

## Root cause

1. Khi Dừng/crash, salvage `translate` chỉ ghi các câu **đã có VI** vào `script.json` (vd 398 dòng, tất cả đủ VI).
2. `count_script_missing` = **0** (mọi dòng trong file đều có VI) → `run_translate` **skip** «đã dịch xong».
3. `_auto_gpu` in «TTS sẽ bỏ qua câu thiếu» rồi gọi TTS trên script ngắn.

Không phải lỗi nano_fa / VieNeu.

## Evidence

- Job `2cd10c3fa86d_p01`: ASR 2698 · script sau này 2616 VI · TTS `n_total=398`, `started_at` sớm hơn lúc dịch đủ.
- Salvage cũ: `ordered = [done[i] for i in done]` — thiếu khung ASR trống.

## Fix

- Backup: `Z:\PinelineV2_codebak\2026-11-08_translate-partial-tts-jump\`
- `translate.py`: `translate_coverage_gap` / `translate_ready_for_tts`; salvage ghi **đủ khung ASR** (`vi=""`); skip-if-done đòi coverage ≥90% ASR.
- `server.py` `_auto_gpu`: không TTS nếu chưa ready; `_do_tts` chặn cùng điều kiện.
- Heal job: `tts.n_total` ← số câu có VI hiện tại.

## Recheck

1. Job thử: Dừng dịch khi ~10–20% → `script.json` phải còn đủ ~N dòng ASR, nhiều `vi` trống; `n_missing>0`.
2. Chạy tiếp auto / queue: **không** nhảy TTS; translate `pending` với lý do coverage/missing.
3. Dịch đủ → TTS `n_total` ≈ số câu có VI (không kẹt 398).
4. **Pass nếu:** dừng giữa chừng không còn TTS dở; đủ dịch mới TTS.
5. **Fail nếu:** lại thấy TTS `n/M` với M ≪ ASR trong khi dịch chưa xong.

## Liên quan

- Job: `2cd10c3fa86d_p01`
- Restart: **:8801** để nạp `server.py` / `translate.py`
