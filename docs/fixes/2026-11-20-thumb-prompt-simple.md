# Prompt thumb AI quá dài / khóa 3D → lệch typo ảnh gốc

- **Date:** 2026-11-20
- **Job / khu vực:** `meta_studio.build_master_image_prompt` · auto-publish / Meta
- **Status:** fixed
- **Backup:** codebak `Z:\PinelineV2_codebak\2026-11-20_thumb-prompt-simple\`

## Triệu chứng

Thumb auto-publish lệch typo so với poster gốc, stamp 3D kim loại xấu / giống nhau giữa nhiều phim.

## Root cause

`build_master_image_prompt` khóa cứng: ASCII Latin bỏ dấu, menu ice/chrome/UE5, layout phải-trái, POSTER TEXT CLEANUP dài → model ưu tiên stamp chữ hơn bám poster.

## Fix

- Prompt ngắn: ref → 16:9 → ribbon → 2 dòng title (giữ dấu Việt) → typo theo nền ảnh.
- Badge cho phép `FULL` (+ NEW/HOT).
- Bỏ ép 3D-Latin / spell-out / Unreal / palette vật liệu.
- Test `test_meta_and_thumb` + `test_autopub_ref_typo` (10 pass).

## Recheck

1. `python -m pytest -q tests\test_meta_and_thumb.py tests\test_autopub_ref_typo.py`
2. Meta / auto-publish gen 1 series mới sau restart :8801 (in-process) hoặc CLI `meta_studio` (reload file).
3. **Pass nếu:** prompt không còn `INTEGRATED 3D LATIN` / `Unreal Engine`; chữ title có dấu; thumb bám cast poster hơn stamp cũ.
4. **Fail nếu:** vẫn gen chữ MAT CA không dấu kiểu stamp chrome mọi phim.

## Liên quan

- DECISIONS 11-20 (prompt thumb đơn giản); supersede phần «3D Latin» của 11-18 typo (vẫn poster-only + hook neo title ở auto-publish).
