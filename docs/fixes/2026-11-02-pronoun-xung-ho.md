# Lệch xưng hô sau dịch (Ta–Ngươi / sai self–call)

- **Date:** 2026-11-02
- **Job / khu vực:** `translate.py`, `agent_pronoun_pass.py`, `server._run_requested_review` (V4 :8804 + V5 :8805)
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-02_v4-pronoun-pass\`

## Triệu chứng

Phụ đề Việt sau translate hay lệch xưng hô: đô thị/mixed còn Ta–Ngươi, hoặc self/call không khớp bảng nhân vật / phân cảnh.

## Root cause

1. Prompt batch nhắc xưng hô nhưng không ép theo `who`/`to` + scene pronouns đủ mạnh.
2. Không có post-pass deterministic sau polish để tẩy đại từ cổ khi tone đô thị/mixed.
3. Agent review chỉ chạy name-pass + style, không có pass riêng cho xưng hô.

## Evidence

- Review thủ công nhiều job: cặp Ta/Ngươi xuất hiện ở phim hiện đại.
- `pytest tests/test_pronoun_postpass.py` — 3 case (tẩy Ta–Ngươi; ép tôi/anh; giữ khi thiếu tên).

## Fix

- `translate.apply_pronoun_postpass` + gọi sau polish; inject pronouns trong `_resolve_scene_context`; siết prompt batch.
- `agent_pronoun_pass.run_pronoun_pass` (LLM).
- `_run_requested_review`: tên → xưng hô → văn phong.
- Đồng bộ V5 (`translate.py`, `agent_pronoun_pass.py`, `server.py`).

## Recheck

1. Restart :8804 (V4) và/hoặc :8805 (V5).
2. `python -m pytest -q tests/test_pronoun_postpass.py` → 3 passed.
3. Dịch lại 1 batch job đô thị có `series_glossary` / scene matrix.
4. **Pass nếu:** không còn Ta–Ngươi ở tone đô thị/mixed; self/call khớp khi có tên who/to.
5. **Fail nếu:** vẫn Ta–Ngươi đô thị, hoặc post-pass đổi đại từ khi thiếu tên (không nên).

## Liên quan

- DECISIONS 2026-11-02 (xưng hô translate)
- V5 sync cùng ngày
