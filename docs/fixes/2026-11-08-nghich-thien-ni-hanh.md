# 逆天而行 dịch sai «Nghị Thiên Nhi Hành» (đúng: Nghịch…)

- **Date:** 2026-11-08
- **Job / khu vực:** series «Tu vi vạn năm mỗi giây»; jobs `acf32f20607c` / `1441e6ce478d` / `0a5f60aead18`; `translate.ensure_hard_terms`
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-08_nghich-thien-heal\`

## Triệu chứng

Bảng nhân vật / GPT name pass ghi `逆天而行 → Nghị Thiên Nhi Hành`. Đúng Hán Việt: **Nghịch Thiên Nhi Hành** (逆 = nghịch; Nghị = 议/議).

## Root cause

1. PLAN/LLM đọc sai âm 逆→«Nghị», ghi vào `glossary.characters`.
2. Các gate (name pass, QA, review, series_glossary) **khóa theo glossary** — nhất quán sai, không kiểm tra đúng âm Hán Việt.
3. Cùng file đã có `逆天体质 → Nghịch Thiên…` (đúng) nhưng không cross-check cùng chữ 逆.
4. `series_glossary` lan bản sai sang mùa/job sau.

## Evidence

- `data/series_glossary/Tu vi vạn năm mỗi giây.json`: characters `逆天而行 → Nghị…` vs terms `逆天体质 → Nghịch…`.
- Jobs trên: script có «Nghị Thiên Nhi Hành».

## Fix

- Heal glossary + script (Nghị→Nghịch) series + 3 job.
- `translate.py`: seed lock `逆天而行 → Nghịch Thiên Nhi Hành`; `ensure_hard_terms` đè bản «Nghị Thiên…» ở terms + characters.

## Recheck

1. Mở glossary series / job `acf32f20607c`: `逆天而行` → Nghịch Thiên Nhi Hành.
2. `grep -F "Nghị Thiên Nhi Hành" D:\PinelineV2_work\acf32f20607c` → không còn.
3. **Pass nếu:** không còn Nghị…; plan mới sau restart vẫn bị đè bởi seed lock.
4. **Fail nếu:** series_glossary hoặc script còn «Nghị Thiên Nhi Hành».

## Liên quan

- Gate không thay thế tra cứu Hán Việt; GPT name pass chỉ ép script khớp bảng.
- Sync V4/V5 `translate.py`. Restart :8801 để nạp seed (heal file glossary đã xong không cần restart).
