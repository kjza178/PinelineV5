# Review: FULL ZH→VI RAW MT (robebo116 / 60-zh-vi) — no Pineline glossary

- **Date:** 2026-11-09
- **Job / files:** job `0a5f60aead18`; `FULL.zh.srt` (2992 cues) → `FULL_base.vi.srt`; contrast only `FULL_pineline_ref.vi.srt` (4592 cues, different cue split — aligned by timestamp overlap)
- **Model:** robebо116 / 60-zh-vi (base MT, no glossary locks)
- **Spot-check:** ~42 cues across indices ~1–50, ~1400–1450, ~2900–2992 (+ full-file heuristic scans)
- **Status:** review only (sandbox; no production code touched)

## Verdict

**Usable raw baseline for xianxia ZH→VI, not publish-ready alone.**

| Axis | Score (1–5) | Note |
|------|-------------|------|
| Fluency | **3.5** | Most mid/long cues read as natural VN; genre register (ngươi/ta/hắn, Điện chủ, phong sơn) is consistent and often smoother than locked-glossary proper-noun stiffness. |
| Sense / accuracy | **3.0** | Core plot lines usually OK; slang, truncated cues, and a few fixed phrases are wrong or half-wrong. |
| Pronoun consistency | **3.5** | Strong in-file consistency on **ngươi / ta / hắn**; Pineline ref prefers **ông / cậu / mình** (more modern dialogue). Neither is “broken”; MT is more classical. |
| Obvious nonsense | **2.5** (worse = more nonsense) | Several fragment cues and slang calques fail hard (see examples). |
| CJK leak | **5** | **0 / 2992** cues with Han characters in MT. |

**Bottom line:** Without requiring glossary locks, this MT is **good enough to draft / post-edit**, especially for fluent narrative and formulaic cultivation lines. It is **not** safe to ship unedited: short ASR-style fragments, internet slang, and a handful of fixed idioms produce clear meaning breaks. Glossary locks would mainly help **name casing/spacing** and **term unity** (e.g. 陨落 ↔ vẫn lạc vs ngã xuống); they would **hurt** fluency if they force every title as a frozen proper noun in dialogue.

### When MT is MORE natural than locked proper nouns

- Everyday complaint / banter (“Chuyện quái gì thế này?”, ghế đầu lâu, “không phải lúc chê bai cái ghế”) reads like spoken VN; locking every 殿主/圣地 as rigid title tokens would feel stiff.
- Soft rendering of ranks in flow (“Bản thiếu chủ liền ban…”, “Thái Hư Thánh Địa phong sơn bế thị”) is idiomatic for the genre.
- Not inventing glossary romanizations mid-sentence keeps rhythm better than “LOCK(ĐiệnChủThiênHư)”-style post-edit artifacts.

### When unlocked MT breaks meaning

- Slang: 嘎 → “hack”; 我了个大操 → wrong paraphrase; 别来无恙 → “đã lâu không gặp” (wrong idiom).
- Truncated ZH cues: 这打电、→ “Cái gọi điện này”; 通的闭关 → “Thông bế quan”; drop of 化神 in “圣主化神巅峰修为”.
- Calque / wrong sense: 够分了 → “Đủ điểm rồi”; 做到筑基中期 → “Làm đến…” (should be declined *down to*); 秒天、秒地 → “Miểu Thiên, giây lát”.
- Awkward reduplication from 回禀 / 打包: “Bẩm bẩm”, “Gói gói”.
- 陨落 inconsistently “vẫn lạc” / “ngã xuống” / “tử trận” (genre-OK but not locked).

## Spot-check notes by band

### Start (~1–50) — isekai / system rant

- Strong fluency on multi-clause lines (#1, #16, #37, #49).
- Failures cluster on **vulgar slang** and **cue fragments** (#9, #13, #22).
- 华外 → “Hoa Ngoại” (likely mis-hear / fragment of 话里话外); #21 treats it as a name — unlocked MT invents a proper noun.
- Pronoun: MC as **ta**, enemies addressing as **ngươi**; Pineline often **mình/ông** — MT more “novel narration”, ref more “dubbing dialogue”.

### Middle (~1400–1450) — Thái Hư phong sơn

- Formula lines excellent (#1400, #1403, #1415, #1427, #1445).
- 陨落 → “vẫn lạc” matches fan-xianxia VN; Pineline sometimes “ngã xuống” (clearer to general audience).
- Weak spots: incomplete cues (#1406, #1412), slight sense drift (#1430 断了 as “cắt đứt” vs pillar “gãy”), “Bẩm bẩm sư tôn” (#1440).
- #1421 drops **Hóa Thần** from “圣主化神巅峰修为” → only “Tu vi đỉnh phong của Thánh Chủ”.

### End (~2900–2992) — thiếu chủ / luyện hư quả

- Offer/banter mostly fine (#2900, #2912, #2920).
- Clear sense errors: #2916 别来无恙; #2928 够分了; #2921 齐了 as “Đủ rồi” while #2920 correctly “đông đủ”.
- #2915 “Dao Trì Thánh Nữ từ biệt” — unlocked transliteration is natural; glossary might prefer a fixed “Dao Trì / Ngọc Trì” form, but meaning holds.
- #2933 “Gói gói mang về” — fluency ding only.

## Full-file scans (supporting)

- CJK leak: **0**
- Empty MT cues: **0**
- “vẫn lạc”: 6; other 陨落 → ngã xuống / tử trận (inconsistent but mostly sensible)
- Pronoun mass: ngươi ~221, ta ~294, hắn ~104 (stable register)
- Rare glitches: Bẩm bẩm×1, Gói gói×1, Hoa Ngoại×1

## 10 example triples

Ref text = Pineline LLM+glossary, **timestamp-aligned** (ref has finer splits; `/` joins overlapping ref cues). Judgments are on **RAW MT**, not “must match glossary”.

### 1) Fluency win — opening (MT ≈ ref sense; MT slightly tighter)

- **#1** `00:00:00,000 → 00:00:04,320`
- **ZH:** 殿主没想到三百年前那一战竟真把你伤成这样，
- **MT:** Điện chủ không ngờ trận chiến ba trăm năm trước lại thật sự làm ngươi bị thương như vậy
- **Pineline ref:** Điện chủ không ngờ trận chiến ba trăm / năm trước lại thực sự khiến ông bị / thương nặng đến thế,
- **Note:** MT natural; unlock → **ngươi** vs ref **ông**. Neither nonsense.

### 2) Slang fail

- **#9** `00:00:26,850 → 00:00:28,610`
- **ZH:** 哎呦，我了个大操，
- **MT:** Ôi chao, ta làm cái quái gì vậy
- **Pineline ref:** *(short overlapping fragment; ref split differs)*
- **Note:** MT invents “làm cái quái gì” — **wrong sense** of the swear. Fluency OK, meaning broken.

### 3) Fragment → near-nonsense (unlocked)

- **#13** `00:00:36,050 → 00:00:37,330`
- **ZH:** 这打电、
- **MT:** Cái gọi điện này
- **Pineline ref:** Cái điện thoại này,
- **Note:** Both guess “phone”; MT “gọi điện” is weaker. Typical ASR-fragment risk, not glossary-related.

### 4) Hard nonsense — slang 嘎

- **#22** `00:00:49,587 → 00:00:50,530`
- **ZH:** 话里话外这是要嘎。
- **MT:** Trong lời nói ra là muốn hack.
- **Pineline ref:** Xong đời rồi, / Nói bóng nói gió là muốn giết mình
- **Note:** **Obvious nonsense** (hack). Glossary would not save this; need slang-aware MT or post-edit.

### 5) Sense drift — 做到 = declined *to*

- **#28** `00:00:57,175 → 00:00:58,695`
- **ZH:** 做到筑基中期，
- **MT:** Làm đến Trúc Cơ trung kỳ,
- **Pineline ref:** chỉ còn lại Trúc Cơ trung kỳ,
- **Note:** MT reads as achievement; context is **crippled down to** Foundation mid. Meaning break.

### 6) Genre fluency without locks

- **#1403** `00:55:29,040 → 00:55:31,200`
- **ZH:** 太虚圣地封山闭市了，
- **MT:** Thái Hư Thánh Địa phong sơn bế thị rồi,
- **Pineline ref:** Thái Hư Thánh Địa đã phong sơn bế / thị,
- **Note:** MT natural; treating 太虚圣地 as flowing title (not a frozen glossary token) is **more natural** here.

### 7) Dropped term (accuracy)

- **#1421** `00:55:55,984 → 00:55:57,824`
- **ZH:** 圣主化神巅峰修为，
- **MT:** Tu vi đỉnh phong của Thánh Chủ,
- **Pineline ref:** Thánh chủ có tu vi Hóa Thần đỉnh / phong,
- **Note:** MT drops **Hóa Thần** realm — sense incomplete. Glossary lock on realm names would help.

### 8) 陨落 — unlocked genre calque vs clearer ref

- **#1424** `00:56:00,064 → 00:56:01,184`
- **ZH:** 怎会轻易陨落？
- **MT:** Sao có thể dễ dàng vẫn lạc?
- **Pineline ref:** sao có thể dễ dàng ngã xuống?
- **Note:** MT “vẫn lạc” is **more natural for fans** / genre; ref “ngã xuống” is clearer general VN. Unlock wins for target audience; not a meaning break.

### 9) Fixed idiom fail

- **#2916** `02:04:00,090 → 02:04:01,610`
- **ZH:** 圣女，别来无恙？
- **MT:** Thánh nữ, đã lâu không gặp?
- **Pineline ref:** Thánh nữ, vẫn bình an chứ?
- **Note:** MT substitutes a different greeting. Fluency OK, **wrong idiom**.

### 10) Wrong sense — 够分了

- **#2928** `02:04:31,950 → 02:04:32,590`
- **ZH:** 够分了。
- **MT:** Đủ điểm rồi.
- **Pineline ref:** đủ để chia rồi.
- **Note:** Context = enough fruits **to share/divide**, not “points”. Clear meaning break; glossary irrelevant.

## Summary judgment

RAW MT (**robebo116/60-zh-vi**) on this FULL ZH→VI job:

1. **No CJK leak**, full cue coverage, mostly fluent xianxia VN.
2. Pronouns/titles stay **internally consistent** (ngươi/ta/hắn) without glossary — often **more natural** than over-locked proper nouns.
3. Failures are concentrated in **slang, truncated cues, fixed idioms, and occasional dropped realm terms** — enough that unedited output will show occasional nonsense on screen.
4. Recommend: use as **draft** + light human/LLM post-edit focused on slang & fragments; apply glossary **selectively** (realms, unique names) rather than locking every title word.

## Recheck (how this review was produced)

1. Parsed `FULL.zh.srt` / `FULL_base.vi.srt` / `FULL_pineline_ref.vi.srt`.
2. Spot-checked ~42 indices in bands 1–50 / 1400–1450 / 2900–2992; aligned ref by timestamp overlap.
3. Scanned all 2992 MT cues for CJK, empty lines, and pattern counts.
4. **Pass if:** review file exists with verdict + 10 triples and cites concrete failures.
5. **Fail if:** only index-aligned ref (wrong due to 4592 vs 2992) or claims glossary-required for all quality.
