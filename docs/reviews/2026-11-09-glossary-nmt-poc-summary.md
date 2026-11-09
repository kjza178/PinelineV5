# Tóm tắt Glossary POC × NMT — job `0a5f60aead18`

Dành cho product owner. Nguồn: `0a5f60aead18_report.md` + `0a5f60aead18_report.json`.  
Phạm vi: sandbox `mt_bench` (full thoại 2992 câu + hyp NMT base/QT đã có). **Không** đụng `translate.py` / production.

---

## 1) Full-dialogue + NMT có bắt gap mà sample `build_plan` bỏ sót không?

**Có — nhưng chủ yếu gap kiểu “khóa không giữ được”, không phải “thiếu cả dàn nhân vật”.**

| Góc nhìn | Kết quả POC |
|---|---|
| Phủ nhân vật đã có trong glossary | **0/26** character glossary không xuất hiện trong thoại → sample build_plan đã bắt đủ cast chính |
| Ứng viên ZH lặp ≥3 ngoài glossary | **29** — full thoại bắt được tần suất mà sample dễ bỏ |
| Chất lượng khóa vs NMT raw | **1** nhân vật bị dịch nghĩa hệ thống (xem mục 3) — đây là tín hiệu sample `build_plan` **không** tự hiện ra |

**Kết luận PO:** Full-dialogue + NMT **bổ sung** sample `build_plan` theo hướng *kiểm chứng khóa* + *gợi ý term/địa danh phụ*. Trên job này nó **không** chứng minh sample đã miss hàng loạt PN mới; phần lớn `suggest_add` là filler/hội thoại.

---

## 2) Top 10 `suggest_add` giống tên nhân vật / địa danh (đã lọc noise)

Danh sách gốc 29 mục đầy tiếng cười, “được rồi”, “không thể”… Dưới đây là **10 mục ít noise nhất**, ưu tiên danh hiệu / địa danh / thuật ngữ thế giới (không phải tên riêng kiểu “Trương Tam” thuần):

| # | ZH | ×freq | Vì sao giữ lại (không phải noise) | Gợi ý khóa VI từ NMT |
|---|---|---:|---|---|
| 1 | **太虚圣地封山** | 3 | Chứa địa danh **太虚圣地** (glossary có 天虚圣殿 / 瑶池圣地, **chưa** khóa Thái Hư) | Thái Hư Thánh Địa (+ “phong sơn” là động từ) |
| 2 | **少主** | 6 | Xưng hô nhân vật (thiếu chủ) lặp ổn định | thiếu chủ |
| 3 | **大弟子** | 4 | Chức vị “đại đệ tử / thủ tịch” gắn faction | đại đệ tử |
| 4 | **首徒** | 3 | Danh hiệu “thủ đồ” của điện chủ | thủ đồ |
| 5 | **师尊** | 4 | Xưng hô sư tôn (cần thống nhất form) | sư tôn |
| 6 | **修为** | 5 | Thuật ngữ tu tiên lõi, NMT đã ổn | tu vi |
| 7 | **每秒万年修为** | 4 | Cơ chế / “skill phrase” lặp — nên khóa cả cụm | mỗi giây vạn năm tu vi |
| 8 | **回禀殿主** | 3 | Công thức xưng hô / nghi thức | hồi bẩm điện chủ |
| 9 | **圣主所言** | 3 | Công thức dẫn lời thánh chủ | thánh chủ nói / theo lời thánh chủ |
| 10 | **这位道友** | 3 | Xưng hô đạo hữu (thống nhất tone) | vị đạo hữu này |

**Lưu ý:** Không có top-10 “tên người mới rõ ràng” ngoài glossary — cast PN đã khá đầy. Giá trị thực là **địa danh phụ + danh hiệu + cụm cơ chế**.

---

## 3) Nhân vật glossary mà MT **nhất quán** dịch nghĩa (phrase), không giữ PN khóa

Chỉ **một** entry đạt ngưỡng “dịch nghĩa hệ thống” trên cả Base và QT:

| ZH | VI glossary (khóa) | #câu | miss khóa Base/QT | MT dịch nghĩa? | Ví dụ MT |
|---|---|---:|---:|---|---|
| **逆天而行** | Nghịch Thiên Nhi Hành | 10 | **10 / 10** | **Y** (base 10, QT 9) | «nghịch thiên mà đi», «nghịch thiên hành động» |

Các PN còn lại (Từ Trường Sinh, Vương Đằng, Tần Phục Thiên, …): miss khóa ≈ 0 trên metric substring hiện tại.

**Ngoại lệ liên quan (không phải “dịch nghĩa”):**  
`天虚圣殿第九代殿主` → khóa ngắn «Điện chủ Thiên Hư» bị miss vì MT (và cả ref) **mở rộng** thành «Điện chủ đời thứ chín của Thiên Hư Thánh Điện» — lệch form khóa, không phải paraphrase nghĩa tên.

**Cảnh báo metric:** `天下无双` / `无双` có thể **pass giả** vì «Vô Song» là substring của «Thiên hạ vô song» — POC này chưa bắt hết soft-fail kiểu đó (đã ghi nhận ở review NMT riêng).

---

## 4) Khuyến nghị (1 đoạn) — đưa gợi ý NMT vào `build_plan` tương lai, **chưa** nối production

Giữ pipeline production nguyên trạng; thêm **bước offline sau khi có draft glossary + full SRT NMT** (đúng kiểu POC hiện tại): quét toàn thoại lấy span ZH tần suất ≥3, đối chiếu form khóa VI với hyp Base/QT, xuất báo cáo `lock_risk` (miss khóa / nghi dịch nghĩa) và `suggest_add` đã lọc filler; chỉ **đề xuất** (không auto-merge) các mục đạt ngưỡng “nameish” (xưng hô / địa danh / thuật ngữ lặp + form NMT ổn định) vào hàng đợi review của `build_plan` / editor. Mục tiêu gần: biến NMT thành **cảm biến kiểm chứng khóa** (ưu tiên case như `逆天而行`) và **gợi ý term phụ**, chứ chưa wire vào `translate.py` hay auto-lock runtime.

---

## Meta

- Job: `0a5f60aead18` · 2992 ZH · glossary chars≈26 · terms 28 · suggest_add 29  
- Method: freq ZH spans + so sánh locked VI vs full-SRT NMT (hachimi60 + hachimi60_qt); no `translate.py`  
- File nguồn: `0a5f60aead18_report.md`, `0a5f60aead18_report.json`
