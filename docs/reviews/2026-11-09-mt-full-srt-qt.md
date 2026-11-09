# Review — FULL ZH→VI (HachimiMT-60-QT, no glossary)

- **Date:** 2026-11-09
- **Model / job:** `ngocdang83/HachimiMT-60-QT`
- **Inputs:** `FULL.zh.srt` (2992 cues) → `FULL_qt.vi.srt` (2992 cues)
- **Ref:** `FULL_pineline_ref.vi.srt` (4592 cues) — **không align theo index** (segmentation khác); chỉ tham khảo tone, **không trừ điểm** vì Pineline dùng tôi/cậu
- **Sandbox:** chỉ đọc/ghi dưới `D:\PinelineV2_tmp\mt_bench\` — không đụng production

## Spot-check

~40 cues: **1–14** (đầu) + **1491–1503** (giữa) + **2980–2992** (cuối), cộng scan toàn file (đại từ, CJK còn sót, slang ZH, pattern lỗi).

## Verdict

**PASS — usable convert-voice draft (cần post-edit nhẹ).**

| Trục | Đánh giá |
|------|----------|
| Convert-voice (ta/ngươi/hắn) | **Tốt.** Toàn file ~`ta` 315 / `ngươi` 290 / `hắn` 111; gần như không có `cậu`; 2 hit `tôi` đều là động từ *tôi luyện*, không phải đại từ. Không trộn ta+tôi trong cùng cue. 2 cue `tao` (#37, #1270) khớp ngữ MC hiện đại thô — chấp nhận được trong convert-voice thô. |
| Fluency | **Khá / lệch.** Nhiều câu xianxia đọc được; vẫn còn calque chữ-chữ và câu cụt theo cue ASR/split. |
| Nonsense | **Thỉnh thoảng.** Lỗi nghĩa rõ: 首席→*thủ tịch*, 乱断→*đứt đoạn*, 为师→*lão sư*, tên riêng/địa danh bị dịch literal. |
| Slang | **Không đều.** `特么/他妈/我操` thường → *mẹ nó / mẹ kiếp*; nhưng 我了个大操, 我靠了个DJ, 练血, đôi khi 牛逼→*ngưu bức* fail. |
| CJK leftover / empty | **0 / 0** |

**Không trừ** vì QT giữ ta/ngươi trong khi Pineline gold dùng tôi/cậu — đúng brief convert-voice.

## 10 examples

### 1. Convert-voice OK (đầu phim)
- **#1** ZH: 殿主没想到…把你伤成这样  
  QT: *Điện chủ không ngờ… làm **ngươi** bị thương thành như vậy*  
  → Giọng cổ điển ổn; khác Pineline (*ông*) nhưng đúng convert-voice.

### 2. Nonsense / calque
- **#4** ZH: 修为实力实不存一  
  QT: *Tu vi thực lực thực sự **không còn một***  
  → Nghĩa lệch; kỳ vọng kiểu *chẳng còn bao nhiêu / mười phần chẳng còn một*.

### 3. Proper-noun / structure fail
- **#7** ZH: 至于你石像殿交出所有法宝  
  QT: *Còn việc **tượng đá điện** của ngươi giao ra tất cả pháp bảo*  
  → 石像殿 nên là tên điện (*Thạch Tượng Điện*), không phải “tượng đá”.

### 4. Slang fail nặng
- **#9** ZH: 哎呦，我了个大操  
  QT: *Ôi chao, ta đúng là một **đại thao***  
  → Dịch từng chữ; slang vỡ nghĩa.

### 5. Slang / modern voice OK-ish
- **#10** ZH: 这特么什么情况？  
  QT: *Đây **mẹ nó** là tình huống gì vậy?*  
  → Thô nhưng hiểu được; giữ được cảm xúc MC.

### 6. Fluency / split cue
- **#14** ZH: 这杀气等等  
  QT: *Sát khí này **vân vân***  
  → 等等 = ngắt câu (“khoan…”), không phải “vân vân”.

### 7. Role pronoun fail (为师)
- **#1491** ZH: 为师也该去准备了  
  QT: ***Lão sư** cũng nên đi chuẩn bị rồi*  
  → 为师 = “ta (với tư cách thầy)”, không phải nói về “lão sư” ngôi ba. Lặp lại ở #1511, #1520…

### 8. Nonsense nghĩa
- **#1498** ZH: 东荒必将彻底乱断  
  QT: *Đông Hoang chắc chắn sẽ **đứt đoạn** hoàn toàn*  
  → Nên *loạn lạc / loạn tới mức đứt gãy trật tự*, không phải “đứt đoạn”.

### 9. Systemic glossary hole: 首席
- **#2981** (cùng pattern #2029, #2153…) ZH: 圣殿首席弟子是吧？  
  QT: ***Thủ tịch** đệ tử Thánh Điện phải không?*  
  → 首席 = trưởng/đứng đầu; *thủ tịch* sai nghĩa chính trị. **11 cue** cùng lỗi.

### 10. Slang soft-fail cuối file
- **#2992** ZH: 这小孩真他妈是练血啊  
  QT: *Đứa trẻ này đúng là **luyện huyết** mà*  
  → Mất thô tục + 练血 (khẩu ngữ “máu chiến / máu lạnh luyện”) bị dịch thuật ngữ tu luyện.

## Extra notes (không nằm trong 10 trên)

- **#150** 高冷 → *cao lãnh* (calque; nên *lạnh lùng*).
- **#1110** 我靠了个DJ → *Ta dựa vào DJ* (slang meme fail).
- **#1181** …不敢牛逼… → còn sót *ngưu bức* (pinyin-ish) giữa câu Việt.
- **#1500** 荒生 → *Hoang Sinh* (có thể đúng tên gọi; giữ nghi vấn vì không glossary).
- Fluency tốt hơn ở đoạn chiến/đối thoại dài (#2980, #2986, #2988): ta/ngươi nhất quán, câu đọc xuôi.

## Recheck gợi ý

1. Mở `FULL_qt.vi.srt` cues 1–14, 1491–1503, 2980–2992.  
2. Grep: `thủ tịch`, `đại thao`, `Lão sư`, `đứt đoạn`, `ngưu bức`.  
3. **Pass nếu:** giọng ta/ngươi/hắn ổn định; không CJK; lỗi slang/calque cục bộ.  
4. **Fail nếu:** trộn tôi/cậu hàng loạt, hoặc nonsense dày đặc làm mất mạch truyện.

## Liên quan

- Sample dump: `D:\PinelineV2_tmp\mt_bench\out\full_srt\_sample40.txt`
- Scripts tạm: `_spotcheck_qt.py`, `_dig_qt.py`
