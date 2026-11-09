# A/B review — NMT-primary (HachimiMT-60-QT) vs Pineline old gold

- **Date:** 2026-11-09
- **Job:** `0a5f60aead18` (xianxia, ZH→VI)
- **Input:** `D:\PinelineV2_tmp\mt_bench\ab_nmt_primary_vs_old.json` (40 items, "align by ZH fold", `pineline_old` from job `script.json`)
- **A = `nmt_primary`:** HachimiMT-60-QT raw output (no glossary, no LLM)
- **B = `pineline_old`:** old Pineline VI (LLM + glossary, convert/modern mix)
- **Context read:** `out\full_srt\COMPARE_full_base_vs_qt.md`, `2026-11-09-mt-bench-verdict.md`
- **Scope:** review only. No production code changed.

## Data caveat

- The JSON was **regenerated at 04:07** while this review was running.
- The earlier version aligned by cue index. Almost every `pineline_old` was a different cue, so it would have been 39/40 `ALIGN_FAIL`.
- This review scores the **current** ZH-fold-aligned file.
- Some old cues are still split differently from the NMT cue. Only one is a clear mismatch (see ALIGN_FAIL).

## Method

- Criteria, in order of weight: catastrophic or sense errors, name and title accuracy, natural xianxia VI voice.
- **Pronoun register (`ngươi/ta` vs `cậu/tôi/ông`) is not scored as a defect on its own.**
  - This job's old gold mixes modern and convert voice.
  - QT is hard-locked to convert voice.
- `tie` means both usable, or both wrong in the same way.
- Only one reviewer (an AI, single pass), with no native-speaker check.
- ZH here is ASR-noisy, so some "errors" originate in the source. Examples: 觉东荒, 周天骄, 城市三, 藏天渊.

## Tally (39 scored + 1 ALIGN_FAIL)

| Winner | Count | Share of scored (39) |
| --- | ---: | ---: |
| **pineline_old** | **14** | 35.9% |
| **nmt_primary** | **3** | 7.7% |
| **tie** | **22** | 56.4% |
| ALIGN_FAIL | 1 (not scored) | — |

- Old wins: i = 0, 73, 144, 292, 582, 885, 961, 1179, 1543, 1617, 2058, 2274, 2346, 2793.
- NMT wins: i = 366, 1326, 1914.
- ALIGN_FAIL: i = 1470.
  - ZH is `师尊放心，`.
  - Old is `đệ tử nhất định dốc sức tu luyện,`, which is the next cue.
- Ties: i = 218, 438, 510, 660, 730, 809, 1035, 1107, 1256, 1399, 1692, 1767, 1838, 1986, 2132, 2204, 2423, 2499, 2574, 2647, 2719, 2876.

**Reading:**
- Most cues are interchangeable (56% tie).
- When they differ, old wins about 4.7:1 (14 vs 3).
- The 14 old wins come from three failure types in NMT, listed in the next section.
- The 3 NMT wins are mostly **proper-name or literal fidelity**. Old gold drifted, or dropped a name.

### NMT failure classes (14 old wins)

- **Catastrophic literal or idiom errors:**
  - i=144: 不能飘 → "Không thể bay"
  - i=885: 走你 → "đi ngươi"
  - i=2346: broken syntax
  - i=582: stutter copied literally
- **ASR/typo tokens turned into fake names or nonsense:**
  - i=1543: `觉东荒` → "Giác Đông Hoang"
  - i=961: "Thành phố ba"
- **Name or term not aligned to job canon:** i=1617 (藏天渊, "Tàng Thiên" vs canon "Táng Thiên Uyên").
- **Weaker register or flavor:**
  - i=1179: 牛逼 → "lợi hại sao?"
  - i=2274: 苍穹 → "trời" instead of "thương khung"
  - i=2793: 捞 → "vớt"
  - i=0 and i=73: stiffer or more literal than old.

## 12 concrete cues

| # | i | ZH (short) | NMT-primary (QT) | pineline_old | Winner / why |
| --- | ---: | --- | --- | --- | --- |
| 1 | 144 | 不能飘不能飘。 | Không thể bay không thể bay. | không được kiêu, không được ngạo. | **old** — 飘 is slang for "get cocky". NMT's literal "bay" is a catastrophic sense error. |
| 2 | 885 | 坐标太虚圣地，走你。 | Tọa độ Thái Hư Thánh Địa, đi ngươi. | Định vị đến Thái Hư Thánh Địa, đi thôi. | **old** — 走你 is "go!". NMT misreads it as a pronoun. The name is OK in both. |
| 3 | 1543 | 觉东荒竟然也遭到了天机反噬， | Giác Đông Hoang vậy mà cũng bị thiên cơ phản phệ, | Đến cả Đông Hoang mà cũng bị thiên cơ phản phệ, | **old** — NMT invents a person "Giác Đông Hoang" from an ASR-damaged token. |
| 4 | 582 | 去啦，殿主属下属下就知道你洪福齐天， | Đi thôi, thuộc hạ của điện chủ thuộc hạ biết ngươi hồng phúc tề thiên, | Đi đây, Điện chủ, thuộc hạ biết ngay ngài phúc đức ngút trời, | **old** — NMT copies the stutter and garbles the vocative. Old reads fluently. |
| 5 | 1617 | 十有八九是因为藏天渊出了大变故。 | …Tàng Thiên Uyên xảy ra biến cố lớn. | …Táng Thiên Uyên xảy ra biến cố lớn. | **old** — old matches the job canon (Táng Thiên). NMT has no glossary lock. |
| 6 | 2346 | 危险尔等可随意施为。 | Nguy hiểm các ngươi có thể tùy ý thi triển. | Có nguy hiểm thì tùy ý ra tay. | **old** — NMT is word-by-word and unclear. Old gives the conditional meaning. |
| 7 | 366 | 名叫秦福天， | Tên là Tần Phúc Thiên, | tên là Tần Phục Thiên, | **NMT** — 福 = Phúc. Old has a reading error (Phục). This is a real name-accuracy win for NMT. |
| 8 | 1914 | 这屈原城谁知道我铜头哥的大名？ | Khuất Nguyên thành này ai biết đại danh Đồng Đầu ca của ta? | Ai mà không biết đại danh Đồng Đầu ca? | **NMT** — keeps the city name 屈原城. Old drops it, losing information. |
| 9 | 1326 | 怎么连你也变得这么扭扭捏捏的了？ | Sao ngay cả ngươi cũng trở nên ngượng ngùng như vậy? | sao ngay cả ông cũng trở nên lúng túng như thế? | **NMT** (slight) — 扭捏 is bashful or coy. "ngượng ngùng" is closer than "lúng túng". |
| 10 | 438 | 以太虚圣地为首的正道联盟…踏平了天虚圣殿 | …Thái Hư Thánh Địa đứng đầu…Thiên Hư Thánh Điện của chúng ta rồi. | thì liên minh…Thái Hư Thánh Địa dẫn đầu…Thiên Hư Thánh Điện tôi rồi. | **tie** — both keep the two similar sect names correctly. NMT keeps 咱们; old uses "tôi" (voice differs only). |
| 11 | 2204 | …噬天魔龙的龙珠…殿主的首徒 | …long châu của Phệ Thiên Ma Long…thủ đồ của điện chủ sao? | …Long Châu Phệ Thiên Ma Long…đệ tử trưởng của Điện chủ sao? | **tie** — both correct. Old has better title casing. NMT is slightly less natural at "ngươi cảm thấy". |
| 12 | 1179 | 你这名字起的挺牛逼的嘛？ | Cái tên này của ngươi đặt cũng rất lợi hại sao? | Cái tên này của cậu đặt cũng oai đấy nhỉ? | **old** — 嘛 (a tag of mild surprise) becomes a stiff "sao?" in NMT. Old has spoken flavor. |

## Observations vs the earlier bench docs

- The older base-vs-QT docs compared two MT models. They show QT beating base on slang and idiom.
- This A/B is **QT vs the production LLM output**.
- On the same xianxia job, the LLM + glossary path wins decisively where it matters: sense on slang, ASR-noise handling, and name canon.
- This matches the earlier verdict: QT is the better draft voice, but the verdict also said "neither is safe without a name and glossary layer".

**NMT strengths seen:**
- Faithful and stable on plain narrative lines (the 22 ties).
- Fast and cheap.
- Sometimes better than old on literal name reading (i=366, 1914).

**NMT risks seen:**
- It cannot tell ASR typos from names.
- It translates slang literally (飘, 走你).
- It has no glossary lock (藏/葬 Thiên).
- Disfluent stutter cues.

**Old-gold risks seen:**
- Reading-error names (Phục).
- Dropped location names (i=1914).
- Sometimes a wrong subject, e.g. `Bọn họ` for 他 (i=730, scored tie).
- Old gold is not perfect and should not be treated as ground truth for names.

## Production verdict: is "NMT primary + later GPT review" reasonable?

**CONDITIONAL GO** for NMT-as-first-pass draft **in a sandbox or optional, off-by-default lane**.
**NO-GO** for NMT-as-the-**final** or silent-default main translation, or for dropping the LLM as the source-of-truth pass.

Why:
- 14 old wins vs 3 NMT wins is a clear quality gap, and the NMT failures are the catastrophic kind (nonsense or invented names), not just stylistic.
- A later GPT review can fix many of them. But it only sees the NMT text plus ZH, so it must be prompted to distrust the draft. Otherwise anchoring will carry errors through.
- The review step must re-check ZH, not only polish the VI.
- The cost argument (NMT is cheap and fast) only holds if review does **not** need to re-translate most lines. Here 36% of lines had a worse NMT version, so the review stage would still touch a large share.
- Evidence is **one xianxia job, 40 cues, one AI reviewer**. That is too small to flip a default.

### Gates (all must pass before NMT becomes primary)

1. **Name and glossary lock after NMT.**
   - Locked ZH spans must appear as the pinned VI form.
   - Aliases (e.g. 藏/葬 → Táng Thiên Uyên, 圣地 vs 圣殿) must be remapped before review.
2. **ASR-noise guard.**
   - Pre-flag low-confidence or odd tokens (觉东荒, 城市三, 周天骄).
   - Do not let NMT turn them into names. Route them to the LLM with the context window.
3. **Slang/idiom canary list.**
   - Examples: 飘, 走你, 牛逼, 捞, 躺赢, 一锅端, 摊上.
   - NMT must pass a fixed canary set per genre, or the job falls back to LLM-main.
4. **Review prompt contract.**
   - The GPT review gets ZH + glossary + NMT draft, with an explicit "draft is untrusted".
   - It must return a changed/unchanged flag per cue, so the review rate is measurable.
5. **Quantitative bar on a bigger holdout.**
   - At least 2 jobs (xianxia plus modern urban) and 150+ cues each.
   - Required: after review, win/tie-rate vs old ≥ 90%.
   - Required: zero catastrophic sense errors on a fixed canary set.
   - Required: name accuracy ≥ 99% after the lock.
6. **Register profile.**
   - Per-job convert vs modern. QT is locked to convert, so modern jobs need a different model or a pronoun post-pass.
7. **Kill switch.**
   - Per-job flag, off by default.
   - Fallback to LLM-main on gate failure.
   - Never write `sub.vi.srt` from raw NMT.
8. **Cue-level audit trail.**
   - Store NMT draft, reviewed text and gate hits per cue. This is needed to debug regressions.

## Recheck

1. Open `D:\PinelineV2_tmp\mt_bench\ab_nmt_primary_vs_old.json` and compare the 12 cues above by `i`.
2. Verify ZH alignment: `zh` field must match the old cue's meaning (i=1470 is the known mismatch).
3. **Pass (report holds) if:** the tally of about 14 old / 3 NMT / 22 tie / 1 ALIGN_FAIL is reproducible by another reviewer within ±3 on old wins.
4. **Fail if:** a reviewer finds NMT winning more than about 10 of the cues listed as old wins.

## Evidence pointers

- `D:\PinelineV2_tmp\mt_bench\ab_nmt_primary_vs_old.json`
- `D:\PinelineV2_tmp\mt_bench\out\full_srt\COMPARE_full_base_vs_qt.md`
- `Z:\PinelineV2\docs\reviews\2026-11-09-mt-bench-verdict.md`
