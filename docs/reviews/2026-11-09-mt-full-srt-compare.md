# FULL SRT compare: base vs QT (no glossary)

- **Date:** 2026-11-09
- **Scope:** Sandbox MT bench only — raw web-novel VI readability (ignore Pineline glossary)
- **Inputs:**
  - ZH: D:\PinelineV2_tmp\mt_bench\FULL.zh.srt
  - BASE: D:\PinelineV2_tmp\mt_bench\FULL_base.vi.srt
  - QT: D:\PinelineV2_tmp\mt_bench\FULL_qt.vi.srt
- **Cue count:** 2992 / 2992 / 2992 (aligned by index)
- **Identity:** same text **921** (30.8%) · differ **2071** (69.2%)

## Verdict

**QT wins the sample tally** (colloquial xianxia / web-novel feel, slang & idiom capture).  
**BASE is safer on hard failures** (QT occasionally garbles long/complex cues).

**Listen / read first:** FULL_qt.vi.srt  
**Keep BASE open as fallback** when a QT line sounds broken or doubled.

## Winner tally (27 judged diffs, base≠QT)

| Winner | Count | Share |
|--------|------:|------:|
| **QT** | **15** | 55.6% |
| **BASE** | **12** | 44.4% |
| Tie (excluded from sample focus) | — | — |

Recommendation weight: **QT first**, not a landslide — roughly 56/44 with BASE retaining value on fidelity/clarity crashes.

## Sample cues (base ≠ QT)

Judging rule: which line reads better as raw web-novel Vietnamese (spoken xianxia tone, natural word order, correct term sense). Glossary compliance ignored.

### QT better

| Cue | ZH (short) | Why QT |
|-----|------------|--------|
| 202 | 饶属下一命 | QT *Tha cho hạ một mạng* đúng nghĩa tha; BASE *Cho dù là một mạng* lệch nghĩa |
| 247 | 如果宿主选 | QT *ký chủ* chuẩn hệ thống; BASE *chủ ký sinh* calque xấu |
| 376 | 按在地上摩擦 | QT *đè…chà đạp* sống động hơn *ấn…cọ xát* |
| 407 | 一剑把我秒了 | QT bắt *秒* (*ngay lập tức*); BASE chỉ *giết chết* |
| 450 | 静置…远古神眸 | QT *thần mâu* + khí tức; BASE *Tĩnh tâm* lệch 静置 |
| 550 | 破镜的机会 | QT *phá cảnh* đúng tu tiên; BASE *phá gương* quá literal |
| 692 | 一锅端了 | QT *một mẻ hốt gọn*; BASE *Cướp sạch* sai hướng hành động |
| 729 | 噼里啪啦的突破 | QT *ầm ầm đột phá* bắt onomatopoeia; BASE *nhanh chóng* nhạt |
| 1000 | 量产了仨 | QT *ba người*; BASE *ba khối* lệch |
| 1096 | 就这么愉快的决定了 | QT *Cứ thế mà quyết định vui vẻ* tự nhiên hơn |
| 1190 | 老登…拍着胸脯 | QT mượt hơn ở câu dài khẩu ngữ |
| 2204 | 有些草率 | QT *qua loa* sát 草率 hơn *vội vàng* |
| 2205 | 噬天魔龙的龙珠 | QT đúng *long châu*; BASE nuốt mất 珠 → *Long Phệ…* |
| 2225 | 到底有多牛逼 | QT thêm *rốt cuộc* = 到底 |
| 2818 | 愿意余生赎罪 | QT *Nguyện cả đời để chuộc tội* văn hơn |

### BASE better

| Cue | ZH (short) | Why BASE |
|-----|------------|----------|
| 1 | 伤成这样 | BASE *bị thương như vậy*; QT *thương thành như vậy* calque + thừa dấu |
| 300 | 已经被本座砍了 | BASE *chém chết*; QT *chém đầu* cụ thể hóa quá |
| 857 | 剑道杀招 | BASE *Kiếm đạo sát chiêu* đúng thứ tự hợp danh |
| 907 | 随手撕开 | BASE *tiện tay* tự nhiên hơn *tùy tay* |
| 1466 | …应天绝若真 | BASE rõ tên + quan hệ; QT xáo trộn cú pháp |
| 1514 | 重复演化 | BASE *diễn hóa*; QT *diễn biến* yếu hơn |
| 1724 | 非我等所能揣度 | BASE rõ; QT tautology *suy đoán…suy đoán* hỏng |
| 1897 | 小小年纪就这么重的杀意 | BASE trật tự câu rõ hơn |
| 2004 | 跟为师回天 | BASE *vi sư* đúng xưng hô; QT *lão sư* lệch |
| 2258 | 秒天秒地秒空气 | BASE còn đọc được; QT lặp *giây* + đứt đoạn nặng |
| 2729 | 一群蝼蚁 | BASE *sâu kiến* chuẩn tu tiên; QT *kiến hôi* sai |
| 2865 | 十枚练虚果 | BASE *quả Luyện Hư*; QT *Luyện Hư Quả* thừa *Quả* |

## Pattern notes

1. **QT strengths:** khẩu ngữ, thành ngữ hành động (秒 / 一锅端 / 噼里啪啦 / 草率), một số thuật ngữ hệ thống (*ký chủ*), bắt đủ danh từ ghép (*long châu*).
2. **QT risks:** cue dài/phức tạp đôi khi **garble** (vd 1466, 1724, 2258) — nghe sẽ “đứt” rõ.
3. **BASE strengths:** ổn định hơn, ít lỗi cú pháp thảm họa, danh hiệu/casing ổn định hơn ở vài chỗ.
4. **BASE risks:** quá literal hoặc mất sắc thái meme/web-novel; vài chỗ sai nghĩa nhẹ (饶, 破镜, 龙珠).

## Recommendation

| Priority | File | Use |
|----------|------|-----|
| **1 — listen/read first** | D:\PinelineV2_tmp\mt_bench\FULL_qt.vi.srt | Cảm giác tiểu thuyết mạng VI tốt hơn trên đa số diff |
| **2 — cross-check** | D:\PinelineV2_tmp\mt_bench\FULL_base.vi.srt | Khi QT nghe lệch / lặp / vỡ câu |
| Reference | D:\PinelineV2_tmp\mt_bench\FULL.zh.srt | Đối chiếu nghĩa |

**Bottom line:** Prefer **QT** as primary listen pass for raw novel VI; expect ~7/10 cues equal-or-better, and spot-fix the remaining with BASE when QT collapses.

## Method

- Parsed all three SRTs; aligned by cue index.
- Diff rate 69.2% (2071/2992).
- Stratified sample across runtime + high-edit-distance outliers; judged 27 clear semantic/style diffs (punctuation-only diffs de-emphasized).
- Auxiliary dump: D:\PinelineV2_tmp\mt_bench\out\full_srt\_diff_sample.json
