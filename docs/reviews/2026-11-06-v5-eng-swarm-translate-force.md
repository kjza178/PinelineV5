# Eng-swarm — translate force-wipe / stop (V2·V4·V5)

- **Date:** 2026-11-06 (~23:55)
- **Scope:** `_translate_flow` force-default, `_clear_stop` dual-path, UI `doTranslate`, tests
- **Agents:** PR review · bug hunt · syntax/sync · test+autofix
- **Backup autofix:** `Z:\PinelineV2_codebak\2026-11-07_v5-swarm-autofix\` · test bak `…_v5-swarm-test\`

## Verdict

**Request changes → patched on disk.** Live `:8801` vẫn cần **restart** mới nạp fix.

| Check | Result |
|-------|--------|
| Syntax `server.py` V2/V4/V5 | **PASS** |
| `pytest tests/test_translate_force_default.py` (V5) | **4 passed** |
| TTS / run-all wipe script? | **No** (chỉ `/translate` + `runStep(translate,force)` + UI «Dịch lại») |
| Dual-tree `_translate_flow` honors `force` | **V2/V4/V5 OK** (`force=bool(force)`) |

## Swarm findings (triaged)

### Fixed this swarm (SAFE)

| Sev | Item | Action |
|-----|------|--------|
| P0 | V5 `_translate_flow` hardcode `force=True` | → `force=bool(force)` (+ unit tests) |
| P2 | V4/V5 API response thiếu `"force"` | echo `force` như V2 |
| P1 | Stop trước worker → translate kẹt `running` | mark `pending` khi early-return (V2/V4/V5) |
| Docs | README/CHANGELOG lag | update kèm report này + fix logs |

### Still open (không autofix tối nay)

| Sev | Item | Note |
|-----|------|------|
| P0 | Force wipe **trước** check `.stop` → Stop giữa force mất script | Cần bak-before-wipe trong `translate.py` |
| P1 | Agent `translate_rerun` không gửi `force` → có thể no-op sau fix | Quyết intentional vs force |
| P1 | Cascade TTS/MUX demote khi resume translate | Chỉ cascade khi force/script đổi |
| P1 | Skip-if-done không so `len(script)` vs `len(asr)` | ASR mọc thêm câu |
| P2 | V5 subprocess translate vs V2 in-process | Drift kiến trúc |

## Sync matrix

| Feature | V2 | V4 | V5 |
|---------|----|----|-----|
| `TranslateReq.force` default false | ✓ | ✓ | ✓ |
| `_translate_flow` → `bool(force)` | ✓ | ✓ | ✓ |
| `_clear_stop` dual-path | ✓ | ✓ | ✓ |
| UI `force:true` chỉ «Dịch lại» | ✓ | ✓ | ✓ `static/ui` |
| Unit test force-default | — | — | ✓ 4 tests |
| Response `"force"` | ✓ | ✓ | ✓ |

## Recheck sau restart :8801

1. Job có `script.json` đủ VI → `POST /translate` **không** `force` → `[skip]` / không xoá script.
2. UI «↻ Dịch lại toàn bộ» + confirm → wipe + dịch lại (có chủ đích).
3. Chỉ «▶ Tạo giọng» → không thấy `force: dịch lại từ đầu`.

## Liên quan

- `docs/fixes/2026-11-06-translate-force-wipe.md`
- `docs/fixes/2026-11-06-translate-stop-ghost.md`
- Agents: [PR review](3ab64305-2baf-41e2-b864-79605e0428ee) · [Bug hunt](b0b09a7e-f0f6-44e8-8773-fcdae89d795e) · [Syntax](ea3fecf0-ca0f-4637-bca5-0dc033590568) · [Tests](3d5aa590-541c-4f5b-a76b-f4a5aae135b3)
