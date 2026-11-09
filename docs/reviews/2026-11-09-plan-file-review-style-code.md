# Code review — PLAN_MODE=file + review style lock (`translate.py`)

- **Date:** 2026-11-09
- **Scope:** `Z:\PinelineV2\translate.py` — `_plan_seed_blocks`, `_build_plan_from_file`, `build_plan` (L451–715); `_style_voice_banner`, `_style_exemplars`, `review_batch` (L1795–1935); callers `run_translate` (L2426) / `run_review` (L2044, L2064).
- **Phương pháp:** đọc code + `ast.parse` + `import translate, pronoun_consistency` + chạy mock thử fallback / input xấu. Không đổi code.
- **Kết quả kiểm tra nhanh:** syntax OK · import OK (không vòng) · `work_dir` được truyền đúng · fallback sample hoạt động khi upload lỗi / không có `work_dir`.

## Kết luận

**P0: không có.** **P1: 3 mục** (dưới). P2: 7 mục.

## P1

### P1-1. Plan file-mode thành công nhưng `build_plan` vẫn crash khi LLM trả `null` cho một list → mất hết plan
- `_normalize_plan_data` (L503–522) chỉ `setdefault` → key tồn tại với giá trị `null` không được thay. `_build_plan_from_file` chỉ yêu cầu `characters or terms` truthy.
- Tái hiện (mock): GPT trả `{"characters":[...],"terms":null}` → log "file-mode OK" rồi `build_plan` raise `TypeError: NoneType has no len()` ở dòng print `len(data['terms'])` (L712).
- Hậu quả: `run_translate` (L2436–2442) bắt exception → **dịch KHÔNG có bảng nhân vật** dù Aurora đã trả plan tốt (tốn 1 lượt GPT, mất glossary).
- Fix đề xuất: trong `_normalize_plan_data`, với mỗi key list: `if not isinstance(data.get(k), list): data[k] = []`; `relationship_matrix` phải là dict; ép `characters` phần tử non-dict bị bỏ.

### P1-2. `scenes[].range` lệch hệ chỉ số với `i` (cue SRT ≠ segment `i`)
- Prompt (L559) bảo GPT "range theo **số thứ tự cue trong SRT**". `write_zh_srt` đánh số cue `n = 1..N` **bỏ câu rỗng**, 1-based (`pronoun_consistency.py` L149–169). Nhưng `_resolve_scene_context` (L913–927) so `range` với `r["i"]` (thường 0-based, không bỏ rỗng).
- Hậu quả: phân cảnh inject sai lô (lệch 1 cue ở đầu, lệch dần khi có segment trống) → ngữ cảnh cảnh/xưng hô sai ở review + translate.
- Fix: map cue→`i` sau khi nhận plan (lưu mapping khi `write_zh_srt`), hoặc ghi `i` thật vào SRT (vd prefix `[i]` trong text) và prompt "range theo số `i`", hoặc chuyển range sau parse.

### P1-3. Timeout fallback không có trần tổng → file-mode có thể treo rất lâu trước khi rơi về sample
- `chatgpt_chat_with_file(timeout=420)` lặp 4 model × N base × 2 auth, mỗi lần tới 420s; upload thêm 180s × base × auth (`llm.py` L315–510). Aurora treo → hàng chục phút đến hơn 1h cho một lần lập plan, trong khi `PLAN_MODE=file` là **mặc định** (`_plan_mode` L422, cả `config.json`).
- Ngoài ra `model` truyền từ `run_translate(model=...)` (UI `req.model`, `server.py` L5856) **ghi đè `PLAN_MODEL`** (L565–569): chọn model local (llama/…) thì file-mode gửi tên đó cho Aurora (rồi mới rơi về `auto`) — thứ tự ưu tiên ngược với ý định `PLAN_MODEL`.
- Fix: deadline tổng (vd 600s) cho file-mode bằng wrapper/thread hoặc giảm `timeout`; `use_model = PLAN_MODEL or (model nếu là chatgpt/*)`; log rõ lý do fallback.

## P2

1. **`_style_exemplars` / `_style_voice_banner` không có guard kiểu dữ liệu** — `characters[].vi` là int (LLM) → `AttributeError .strip` (đã tái hiện). `review_batch` gọi chúng **ngoài try** → exception → `run_review` (L2070–2073) nuốt lỗi, `fixes={}` và vẫn set `rv=1` ⇒ **lô bị đánh dấu "đã soát" mà không soát**. Bọc cả hai bằng `try/except → ""` (như `lock_banner`) và dùng `str(c.get("vi") or "")`.
2. **Banner luôn xuất header "BẮT BUỘC KHỚP"** kể cả `plan={}` / mode `unknown` (chỉ trả `""` khi không phải dict). Nên `return ""` khi không có mode/genre/tone/reg; không in `mode=unknown`.
3. **Trùng lặp ràng buộc trong prompt review**: `STYLE LOCK`/CẤM/ƯU TIÊN đã nằm trong `plan_block` (`_plan_block`), `lock_banner` xuất hiện 2 lần (trong plan_block + `lock_ctx`), thêm `voice` banner → ~3 bản cùng nội dung, tốn token và dễ mâu thuẫn (forbid cắt khác nhau: 10 / 12 / 24). Chọn một nguồn.
4. **`_style_exemplars` tĩnh**: luôn lấy ≤5 câu **đầu tiên có tên NV** (hoặc 12 câu đầu) từ toàn `rows` → mọi lô nhận cùng mẫu (không gần ngữ cảnh lô); có thể là bản NMT nháp chưa soát và có thể chính là câu trong lô. Nên ưu tiên `rv==1`, loại `i` trong chunk, chọn gần `pos`. Match tên bằng `in` (phân biệt hoa/thường, tên ngắn như "Lâm" dễ trùng) — dùng word-boundary / bỏ tên < 2 từ.
5. **`_plan_seed_blocks`**: nhãn "Terms lock (chỉ type=lock)" nhưng `terms_list` **không lọc** theo type (L479–483) → mọi term series bị gắn nhãn lock. Lọc `type=="lock"` hoặc đổi nhãn. Nhánh `soft_ocr=False` là dead code (mọi caller truyền True).
6. **`_build_plan_from_file`**: `data.get("error")` — nếu `parse_json` trả list → `AttributeError` (đã tái hiện; vẫn được `build_plan` bắt và fallback nên chỉ là message xấu). Thêm `isinstance(data, dict)`. `int(x["i"])` trong `write_zh_srt` nổ nếu segment thiếu `i` (`s.get("i")` → None) — cũng chỉ rơi về fallback.
7. **Riêng tư / config**: file-mode upload toàn bộ transcript ZH lên Aurora theo mặc định (kể cả khi chỉ chạy local). Cân nhắc cờ opt-in rõ ràng hoặc ghi vào RUNBOOK. `write_zh_srt` ghi đè `sub.zh.srt` dùng chung với pronoun-analyze (cùng nội dung nên OK, nhưng race nếu chạy song song). Timestamp `ms` làm tròn có thể ra `1000` (pre-existing).

## Đã kiểm tra — OK

| Hạng mục | Kết quả |
|---|---|
| Syntax / import | `ast.parse` OK; `import translate, pronoun_consistency` OK |
| Vòng import | `translate`↔`pronoun_consistency` chỉ import **lazy trong hàm** (L536, 808, 1869, 1931 ↔ `pronoun_consistency` L791/802); `context_studio.schema` không import translate → không vòng |
| `work_dir` pass | `run_translate` L2426–2432 truyền `work_dir=work_dir`; không có `work_dir` ⇒ bỏ qua file-mode, dùng sample (đã thử) |
| Fallback | upload/chat lỗi → `build_plan` bắt `Exception` → `_build_plan_sample` → default dict; `_normalize_plan_data` + `apply_style_lock_from_genre` bọc try (trừ P1-1 ở bước print) |
| Caller `review_batch` | `exemplars_pool=rows` ở cả 2 call (L2046, L2066); tham số mới có default → tương thích ngược |
| Prompt review | system đánh số 1–5 liền mạch (rule3 = mục 3), có "CẤM đổi register", output `{"fixes":[…]}`; `filter_review_fixes_for_lock` vẫn áp sau parse |
| Schema `style_lock` | `_plan_json_schema` sinh `mode/default_register`; `apply_style_lock_from_genre` hạ xianxia→mixed khi genre đô thị (khớp với banner) |

## Recheck

1. P1-1: mock `chatgpt_chat_with_file` trả `{"characters":[{"zh":"a","vi":"b"}],"terms":null}` → `build_plan(segs, work_dir=tmp)` **không** raise, `plan["terms"]==[]`.
2. P1-2: segment `i` bắt đầu 0, có 1 câu `text` rỗng giữa chừng; so cue SRT với `i` — cue N phải map về đúng `i`; `_resolve_scene_context` chọn đúng scene.
3. P1-3: mock `requests.post` treo → `build_plan` trả về plan sample trong ≤ deadline đã chọn; log nêu lý do.
4. P2-1: `_style_exemplars({"characters":[{"vi":123}]}, rows)` trả `""` không raise; `review_batch` không đánh `rv=1` khi lỗi nội bộ prompt.
5. Chạy lại: `python -c "import ast;ast.parse(open('translate.py',encoding='utf-8').read())"` + `python -c "import translate"`.

## Liên quan

- Fix log nguồn: `docs/fixes/2026-11-09-mt-draft-slim-gloss.md`, CHANGELOG mục "Plan file + review style".
- Config: `PLAN_MODE`, `PLAN_MODEL` (`config.json`, `pineline.config.json`).
