# HV Auditor: glossary khóa sai âm Hán Việt (逆→Nghị)

- **Date:** 2026-11-09
- **Job / khu vực:** `hv_auditor.py` + `translate.ensure_hard_terms` + `series_glossary` apply/save; Unihan `data/unihan/kVietnamese.json`
- **Status:** fixed
- **Backup:** `Z:\PinelineV2_codebak\2026-11-09_hv-auditor\`

## Triệu chứng

PLAN/GPT ghi `逆天而行 → Nghị Thiên Nhi Hành`; các gate chỉ khóa theo glossary → lan series. Seed/list vá tay không đủ.

## Root cause

Gate name/QA/review = consistency theo bảng, không chứng minh âm HV. Unihan `kVietnamese` lại thiếu/sai nhiều âm tên riêng (沈≠đắm, 帝≠đấy) → không được đè mù toàn bộ.

## Evidence

- Cùng glossary: `逆天体质→Nghịch` vs `逆天而行→Nghị`.
- Unihan: `逆=['nghịch']`, `行` cần EXTRA `hành|hàng`; autofix mù từng đè `Thẩm→Đắm`.

## Fix

1. **Unihan table** `data/unihan/kVietnamese.json` + EXTRA đa âm + giản→phồn.
2. **Trap-only autofix** (`_CONFUSION_TRAPS`): chỉ sửa nhầm chữ rõ (逆 nghị→nghịch). Lệch Unihan khác → `hv_warn` (không đè).
3. **Consistency**: cùng chữ Hán, chỉ ép khi có variant *không* nằm trong tập âm hợp lệ.
4. **Series hygiene**: apply/save chạy audit; drop `hv_suspect`; giữ `hv_warn`; auto-fix trap trước khi ghi kho.
5. Gắn vào cuối `ensure_hard_terms`.

## Recheck

1. `python -c "from hv_auditor import audit_entry; print(audit_entry('逆天而行','Nghị Thiên Nhi Hành'))"` → `fixed_vi=Nghịch Thiên Nhi Hành`.
2. `audit_entry('沈道陵','Thẩm Đạo Lăng')` → `fixed_vi=None`, `warn=True` (không Đắm).
3. Dịch job mới / `ensure_hard_terms(glossary)`: meta `_meta.hv_auditor`.
4. **Pass nếu:** Nghị→Nghịch; Thẩm/Tư Đồ/Thánh Chủ không bị đè bậy.
5. **Fail nếu:** tên riêng bị Unihan rewrite; hoặc Nghị còn sót sau ensure_hard_terms.

## Liên quan

- Quyết định user 11-09: phương án A (1+2+3).
- Sync V4/V5: `hv_auditor.py`, `translate.py`, `series_glossary.py`, `data/unihan/`.
- **Restart :8801** để process nạp module mới.
