# Tổng kết cuối — NMT primary + GPT review keep-NMT

- **Date:** 2026-11-09 ~05:10
- **Sandbox:** `D:\PinelineV2_tmp\mt_sandbox_job` (120 cues, job gốc `0a5f60aead18`)
- **Code:** `translate._filter_cosmetic_nmt_fixes` · sync V2/V4/V5

## Verdict

**NMT là dịch chính ổn; GPT rà sau filter không còn viết lại thừa kiểu «Lão tử→Tôi».**

| Metric | Trước keep-NMT | Sau keep-NMT |
|--------|----------------|--------------|
| Giữ nguyên NMT | 16 (13%) | **82 (68%)** |
| Bị đổi vs NMT | 104 (87%) | **38 (32%)** |
| Review GPT apply | ~16–18/lô | **5 câu / 120** |
| Cosmetic GPT drop | 0 | **47** |
| i=48 Lão tử… | GPT viết lại | **giữ NMT** |

## Pipeline sandbox lần này

1. PLAN file → parse fail → sample; gemma cloud 429 → local 12b; series memory 69 NV
2. Pronoun file → parse fail → fast LOCK 40
3. NMT PRIMARY base 119 · còn 0 LLM vá
4. Style polish 31 + lint 2 (vẫn đụng xưng hô)
5. Review GPT: filter DROP polish; apply 5 cứng
6. `script.json` OK · exit 0

## Subagent

| Agent | Kết quả |
|-------|---------|
| Audit filter | Filter sau parse; keep A/C/D; V2=V4=V5 |
| Unit keep-NMT | PASS 5/0; probe i=48 không apply |
| Sandbox re-run | XONG; diff 82/38 |

## Còn lại (không chặn ship)

1. **Style polish / pronoun lint** vẫn đổi `ngươi→cậu` (~27/38 lệch) — ngoài filter review.
2. PLAN/pronoun `PLAN_MODE=file` vẫn parse JSON fail.
3. Restart **:8801** chưa nạp code mới (sandbox chạy CLI trực tiếp).

## Recheck

```bat
python translate.py D:\PinelineV2_tmp\mt_sandbox_job --force --batch 20
python D:\PinelineV2_tmp\mt_sandbox_job\_diff_nmt_gpt.py
```

Pass nếu: log `bỏ N fix cosmetic`; i=48 giữ «Lão tử…»; changed ≪ 87%.

## Artifacts

- `D:\PinelineV2_tmp\mt_sandbox_job\NMT_vs_GPT.md`
- `D:\PinelineV2_tmp\mt_sandbox_job\KEEPNMT_UNIT.md` / `KEEPNMT_RERUN.md`
- Fix: `docs/fixes/2026-11-09-review-keep-nmt.md`
