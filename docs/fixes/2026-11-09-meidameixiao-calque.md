# 没大没小 → «chưa lớn không nhỏ» (calque vô nghĩa đã rv)

- **Date:** 2026-11-09
- **Job / khu vực:** `05670cbf7c1c` cue i=8; `translate.apply_style_polish` / Pass1 heuristic / style terms
- **Status:** fixed

## Triệu chứng

ZH `你还没大没小了。` → VI `Cậu còn chưa lớn không nhỏ.` — vô nghĩa. User thấy sau (hoặc trong) rà soát.

## Root cause

1. NMT (`mt=1`) calque từng chữ 没/大/没/小.
2. Pass1 + Gemma review đánh `rv=1` mà không sửa (Pass1 chỉ flag nửa câu/đuôi treo; không bắt calque thành ngữ).
3. Chưa có seed glossary / polish deterministic cho 没大没小.

Nghĩa đúng: vô lễ / không biết trên dưới / không biết lớn biết nhỏ.

## Evidence

- `script.json` i=8: `zh=你还没大没小了。` `vi=Cậu còn chưa lớn không nhỏ.` `rv=1` `mt=1`
- `review_pass1.json`: `8 not in nonsense_i` (676 flags khác)

## Fix

- Cue live → `Cậu còn không biết trên dưới à.` (+ watcher heal vì review ghi đè memory mỗi batch).
- `_DEFAULT_STYLE_TERMS` + `_style_rules` + review prompt: CẤM «chưa lớn không nhỏ».
- `apply_style_polish`: heal regex khi ZH có 没大没小.
- `_heuristic_nonsense_flags`: flag calque này cho duty F.
- Backup: `Z:\PinelineV2_backup_2026-11-09_2205.zip` + `Z:\PinelineV2_codebak\2026-11-09_meidameixiao-calque\`.
- Sync V2/V4/V5 `translate.py`.

## Recheck

1. `python -c "from translate import apply_style_polish; r=[{'i':8,'zh':'你还没大没小了。','vi':'Cậu còn chưa lớn không nhỏ.'}]; apply_style_polish(r,{}); print(r[0]['vi'])"` → có «không biết trên dưới».
2. Job `05670`: cue i=8 trên disk = bản đúng sau khi review xong (watcher `D:\PinelineV2_tmp\_heal_meidameixiao_05670.py`).
3. **Pass nếu:** không còn «lớn không nhỏ» cạnh 没大没小; UI/TTS dùng câu mới.
4. **Fail nếu:** sau review xong cue i=8 vẫn «chưa lớn không nhỏ».

## Liên quan

- Restart :8801 khi queue rảnh để worker nạp polish (job này heal bằng process ngoài).
- Cùng họ calque thành ngữ: 吃醋 / 打天下 / 脑子进水.
