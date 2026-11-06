# voice_bgm: nhạc thư viện và audio dừng ở câu thoại cuối (M20)

- **Ngày:** 2026-10-07
- **Nguồn:** review media addendum M20 (`docs/reviews/2026-10-06-code-review.md`)
- **Mức:** P2. Batch đang dùng `duck` nên chưa job nào dính; sửa trước vì user muốn bỏ nhạc nền gốc (claim Content ID) và cân nhắc `voice_bgm`.

## Triệu chứng

`voice_bgm` trộn `[vo][bg]amix=duration=first` với giọng Việt đứng đầu và không `apad`. Dub thường ngắn hơn video (hết câu thoại cuối là hết file) → audio ra dừng ở câu thoại cuối, phần còn lại của video im lặng, nhạc thư viện cũng tắt theo.

## Sửa

`render.py` `_build_audio_filter`, nhánh `voice_bgm`: thêm `apad=pad_dur=7200` vào chuỗi `[vo]` (giống `voice_only`). Độ dài cuối do `-t` theo video chốt (pass1 `_ensure_mixed_audio` và các lệnh encode đều có `-t total`).

Test `tests/test_render_expr.py::test_voice_bgm_runs_past_last_dub_line`: dub 2 s, BGM 1 s loop, `-t 6` → ra đúng 6 s và đoạn 4–6 s có tiếng. Đỏ với bản cũ (ra 2 s), xanh với bản mới. Pytest 81/81.

Hiệu lực: render mới sau khi restart server (render chạy trong server). Không đổi CONFIG BATCH (vẫn `duck`).

Backup: `Z:\PinelineV2_codebak\2026-10-07_m20\` + zip `Z:\PinelineV2_backup_2026-10-07_0147.zip`.
