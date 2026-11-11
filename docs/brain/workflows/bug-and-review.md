# Workflow: săn bug · sửa bug · review

_Cập nhật: 2026-11-11._

## Săn bug định kỳ (khuyên: mỗi tuần, hoặc trước khi restart lớn)

```
/bughunt                 # top 5 hotspot
/bughunt queue           # một khu vực
/bughunt "job p02 TTS dừng 2.7% sau restart"   # theo triệu chứng
```

bug-hunter ghi `docs/reviews/<ngày>-bughunt-<scope>.md` (P0–P3, CONFIRMED/LIKELY/SUSPECT, file:dòng, kịch bản lỗi) → fix-advisor đưa phương án cho P0/P1 → bạn duyệt.

## Sửa một bug

```
/fix B2                  # mã bug trong báo cáo
/fix "Pass1 413 với file nhỏ"
```

Pha 1 chẩn đoán (không sửa) → bạn duyệt → Pha 2: backup → patch → test → code-reviewer → docs (fix log có Recheck) → brain-keeper sync → báo restart.

## Review

```
/review recent           # thay đổi từ lần build brain cuối + CHANGELOG hôm nay
/review translate        # review cả module
```

Kết luận ✅/⚠️/❌ + blocking. Blocking là bug → `/fix R1`.

## Đọc báo cáo thế nào

| Nhãn | Ý nghĩa | Làm gì |
|---|---|---|
| P0 | Mất dữ liệu / hỏng output / treo pipeline | Sửa trước restart kế tiếp |
| P1 | Sai kết quả có điều kiện, stop/retry sai | Sửa trong tuần |
| P2/P3 | Biên / vệ sinh | Gom đợt |
| CONFIRMED | Đã thấy trong log/test | Tin |
| LIKELY | Logic chắc, chưa tái hiện | Viết test tái hiện trước khi sửa |
| SUSPECT | Cần người xem | Đừng sửa mù |

## Nguồn ưu tiên khi săn bug

1. `docs/brain/generated/hotspots.md` (điểm rủi ro tĩnh)
2. `docs/fixes/README.md` — loại bug lặp (queue/park, script wipe, split/merge, hardsub, pronoun)
3. `docs/brain/generated/artifacts-ports.md` — artifact ≥2 module ghi (`manifest.json` ~26 module, `script.json` ~26) = nơi race
4. `work/logs/*.log` của job vừa lỗi
