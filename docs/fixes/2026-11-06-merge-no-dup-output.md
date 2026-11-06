# Merge split tạo output + output_full nhân đôi dung lượng

- **Date:** 2026-11-06
- **Job / khu vực:** `merge_job_parts` — `split_parts.py` (V2/V4), `engines/split_parts.py` (V5); job mẫu `d01dbbc2d703`
- **Status:** fixed

## Triệu chứng

Sau khi mux hết các part và ghép Full, thư mục job cha có cả `output.mp4` và `output_full.mp4`. Explorer hiện ~2× dung lượng (vd ~23 GB × 2) → sợ hết ổ.

## Root cause

`merge_job_parts` ghi `output_full.mp4` rồi fallback `shutil.copy2` sang `output.mp4` khi hardlink fail → hai bản đầy đủ trên đĩa. Ngay cả khi hardlink thành công, Explorer vẫn cộng size từng tên file nên nhìn như gấp đôi.

## Evidence

- `d01dbbc2d703`: `output.mp4` / `output_full.mp4` cùng ~23.37 GB, `st_nlink=2`, `os.path.samefile` True → **wasted 0 GB** (đã hardlink).
- Code cũ V4/V5: `os.link` → `except OSError: shutil.copy2(...)`.

## Fix

- Ghi một lần vào `output.mp4`; `output_full.mp4` chỉ qua `_hardlink_alias` — **không bao giờ copy2**.
- Hardlink fail → chỉ giữ `output.mp4`, manifest `output_full_path` trỏ cùng file.
- Sau merge: `cleanup_split_parts_dir(_split_parts)`.
- Sync V2 / V4 / V5.
- Backup: `Z:\PinelineV2_codebak\2026-11-06_merge-no-dup-output\`

## Recheck

1. Chạy merge (job split đã mux đủ part) hoặc unit: gọi `merge_job_parts`.
2. `python -c "import os; from pathlib import Path; w=Path(r'Z:\\PinelineV2\\work\\<job>'); print(os.path.samefile(w/'output.mp4', w/'output_full.mp4'), (w/'output.mp4').stat().st_nlink)"`
3. **Pass nếu:** `samefile True` và `nlink >= 2`; hoặc chỉ còn `output.mp4` khi hardlink fail; không có bản copy thứ hai cùng size trên ổ khác inode.
4. **Fail nếu:** hai file khác inode / `samefile False` với size gần bằng nhau.

## Liên quan

- Job: `d01dbbc2d703`, `a1e135b20347` (đã hardlink)
- Part outputs `*_p0N/output.mp4` vẫn chiếm ~23 GB sau merge — xoá tay nếu user đồng ý (không auto-delete trong fix này)
