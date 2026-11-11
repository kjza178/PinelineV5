# Brain HOLD vì high hang — cần LLM trace/xử lý rồi mới mở

- **Date:** 2026-11-10
- **Job / khu vực:** `60892cc63cb7_p01` / `_p02` · `agent_hang_fix` · `agent_quality.scan_and_heal_job` · `translate.run_review`
- **Status:** fixed
- **Backup:** zip `Z:\PinelineV2_backup_2026-11-10_1857.zip` · codebak `Z:\PinelineV2_codebak\2026-11-10_hang-llm-fix\`

## Triệu chứng

Job `造神` parts HOLD TTS: `qa_brain` `high_open` toàn `hang` (đuôi treo «là.» / «nhưng.»). Safe-heal không xử lý được; Brain chỉ chặn, không hiểu/context-fix.

## Root cause

1. `agent_quality` chỉ heal deterministic (calque/stutter…) — `hang` high không có pass LLM.
2. Nhiều hang là `dialogue_trail` (ASR cắt ý sang cue sau) → merge mù làm vỡ timing; cần trace root + chọn plan.
3. Race: chạy hang-fix khi Gemma review đang ghi `script.json` → mất `hang_ack`/`hang_fix`.

## Evidence

- p01 `qa_brain` high_i `[1442,1753,3084,3509,4876]` toàn hang (vd i=1442 `我是说。` / `Ý tôi là.`).
- p02 tương tự 6 high hang; review mid-flight `1240/5103` ghi đè script sau pass đầu.

## Fix

- Module `agent_hang_fix.py`: cửa sổ ±2 ZH/VI → LLM (`HANG_FIX_MODEL`/`PRONOUN_MODEL`) trả `root_cause` + `plan` (`complete`/`rewrite`/`keep_intentional`/`merge_next`) + `fixes`; ghi `qa_hang_trace.json`.
- `hang_ack=1` khi `keep_intentional` / `false_positive` → `scan_script` bỏ flag hang.
- Wire: `scan_and_heal_job` gọi khi còn high hang; **skip** nếu translate/review đang ghi; `run_review` cuối gọi `force=True`.
- Config `BRAIN_HANG_FIX=1`. Sync V2/V4/V5. Tests +1 `hang_ack`.

## Recheck

1. `python -c "from agent_hang_fix import fix_hang_job; print(fix_hang_job(r'D:\PinelineV2_work\60892cc63cb7_p01'))"`
2. Đọc `work/<job>/qa_hang_trace.json` — mỗi case có root/plan/rationale.
3. `qa_brain.high_open==0` → clear HOLD → TTS chạy.
4. **Pass nếu:** high hang hết hoặc chỉ còn sau LLM + rationale; TTS không bị HOLD mù.
5. **Fail nếu:** HOLD mãi với hang chưa trace; hoặc hang-fix chạy giữa review làm mất ack.

## Liên quan

- User chọn **B** (không chỉ merge).
- p01: TTS started sau clear. p02: chờ review xong → hang-fix cuối `run_review`.
