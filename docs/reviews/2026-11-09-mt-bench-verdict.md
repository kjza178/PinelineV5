# MT bench verdict — HachimiMT-60 vs HachimiMT-60-QT

- **Date:** 2026-11-09
- **Job sample:** `0a5f60aead18` (n=110 lines; 40 name-hit)
- **Models:** `robebo116/60-zh-vi` (base / HachimiMT-60) vs `ngocdang83/HachimiMT-60-QT`
- **Gold:** Pineline `sub.vi.srt` + script glossary for that job
- **Scope:** bench-only under `D:\PinelineV2_tmp\mt_bench\` — **no production Pineline code changed**
- **Reviews:** `review_hachimi60.md` / `review_hachimi60_qt.md` **absent** at run time → this file includes a ≥15-line human A/B spot-check

---

## Executive GO / NO-GO

| Decision | Status |
| --- | --- |
| Wire either model into `translate.py` as default / replacement for LLM | **NO-GO** |
| Optional **draft-before-LLM** behind an explicit off-by-default flag (bench / sidecar experiment) | **CONDITIONAL GO — QT only**, xianxia/convert jobs, with gates below |
| Fine-tune now on `tran-vi-teacher` | **NO-GO** (already in pretrained; no training this cycle) |
| Treat MT output as publishable VI | **NO-GO** |

**Short verdict:** Prefer **HachimiMT-60-QT** as the safer *optional* draft for convert-register xianxia drafts; keep **both** out of `translate.py` until post-MT name/glossary gates exist and a second job family (modern register) is scored.

---

## Auto score (from `auto_score.json`)

| Metric | base (`hachimi60`) | QT (`hachimi60_qt`) |
| --- | --- | --- |
| n / empty / CJK leak | 110 / 0 / 0 | 110 / 0 / 0 |
| exact_match_ref | 0 | 1 |
| fold_match_ref | 2 | 5 |
| avg_ref_token_recall | 0.672 | **0.688** |
| pronoun_style_flips_adj | **6** | 10 |
| name lock `逆天而行` | 7/7 (1.0) | 7/7 (1.0) |

Notes:

- QT edges lexical overlap with Pineline gold on this xianxia sample.
- Higher QT `pronoun_style_flips_adj` vs gold adjacency is expected: QT hard-locks convert voice (`ta/ngươi/hắn`), while gold sometimes uses modern (`cậu/tôi`). This is **style mismatch to gold**, not proof QT is internally inconsistent (HF card claims 0 flips on their 7-chapter test).
- Runtime (same machine, `run_summary.json`): base ~5.4s (beam 4) vs QT ~13.9s (beam 1 CT2 path as run) — draft cost is acceptable only if optional.

Diff rate base≠QT: **100 / 110** lines (10 identical).

---

## Side-by-side spot-check (≥15 differing lines)

Winner = better vs gold sense + glossary (not “more convert”). Tie = both usable / both wrong in same way.

| # | ZH (clip) | Gold issue | Base | QT | Better |
| --- | --- | --- | --- | --- | --- |
| 39 | 系统老爷爷逆天血脉喂！ | vocative “đâu rồi!” | misses vocative; OK name | same sense; word order worse | **tie** (both miss vocative) |
| 126 | …最牛逼的势力至尊新手大礼包 | gift-pack sense | “cường ngưu… Đại Lễ Bao” awkward merge | keeps “gói quà tân thủ” closer | **QT** |
| 255 | 天虚**圣地**…鸟样 | gold remaps → Thánh **Điện** | Thánh Địa (literal) | Thánh Địa (literal) | **tie** — both need glossary remap |
| 332 | 印帝…玉玺…化神 | caps / titles | “ấn đế” uncased | “Ấn Đế” cased better | **QT** (minor) |
| 345 | **店主**您… | gold = **Điện chủ** | “chủ tiệm” | “chủ tiệm ngài” | **tie / both fail glossary** |
| 384 | 但凡碰上咱们天虚圣殿… | phrasing | “phàm là đụng phải” stiffer | “hễ gặp được” ≈ gold | **QT** |
| 388 | 出门**历练** | genre term | “rèn luyện” | “lịch luyện” = gold | **QT** |
| 438 | 太虚圣地…天虚圣殿 | two names | OK names; “thánh điện” casing | cleaner casing + “rồi” | **QT** (slight) |
| 456 | 宗门**内务** | nội vụ tông môn | “việc trong tông môn” | “việc nội môn” (drift) | **base** (slight) / neither perfect |
| 468 | 十大**真禅**弟子 | gold = chân **truyền** | “Chân Thiền” literal | “Chân Thiền” literal | **tie / both fail** |
| 493 | 还剩下的三个人在不在殿外 | focus on remaining three | clearer question shape | wordier, hedges “sao?” | **base** |
| 537 | 所有徒有一个算一个 | “một người một suất” | mangled | also mangled idiom | **tie / both weak** |
| 546 | 未必能**摊上**一回的机缘 | “gặp được một lần” | ≈ gold | “**bỏ lỡ** một lần” **sense flip** | **base** |
| 691 | …**一锅端**了 | wipe out / scoop | “Cướp sạch” wrong | “một mẻ hốt gọn” closer idiom | **QT** (gold itself odd here) |
| 853 | 你跑到我天虚圣殿来撒野 | gold modern cậu/tôi | convert ngươi/ta + “làm càn” | convert + “gây sự” | **base** vs *this* gold style; **QT** if convert draft desired |
| 938 | 哎哎哎，小心小心 | Ấy ấy ấy | “Ai ai ai” | “Ai ai ai ai” over-repeat | **tie / both weak** |
| 1002 | 吐血三升 | thổ huyết ba thăng | keeps “thổ huyết” | “hộc máu” looser | **base** |
| 1021 | 根本没把天虚圣殿当回事 | “căn bản chẳng coi” | “hoàn toàn không” | “căn bản không” ≈ gold | **QT** |

### Spot-check tally (18 lines)

- **QT better:** 7 (126, 332, 384, 388, 438, 691, 1021)
- **Base better:** 4 (493, 546, 853-vs-gold-style, 1002)
- **Tie / both fail:** 7 — including **shared glossary killers**: `店主→Điện chủ`, `真禅→chân truyền`, `圣地↔圣殿` remaps, idioms 537/938

**Takeaway:** QT is the better *xianxia draft voice* and slightly closer lexically; **neither** is safe without a Pineline glossary/name lock layer. Sense errors still appear (QT #546; base #691).

---

## HF cards — what each model is

### `robebo116/60-zh-vi` ≈ HachimiMT-60 base

- ~57M Marian asymmetric (8 enc / 2 dec), ZH→VI web-novel.
- Trained on `ngocdang83/tran-vi-teacher` + hirashiba filtered + more Gemini gold.
- **Natural / context-dependent register** (can mix modern + convert).
- Documented limits: rare-name hallucination, long-context name drift, Simplified-only, not for unreviewed publish.

### `ngocdang83/HachimiMT-60-QT`

- Same size class; **convert voice edition** (`ta/ngươi/hắn/nàng` locked).
- Continual patches (v1.1/v1.2) for idioms, title+不要/且 misreads; rare names still fragile.
- **By design** modern stories also come out archaic — bad if Pineline job wants modern intimate register.
- Decode warning: do **not** use `no_repeat_ngram_size` (mangles names). Bench decode already differs (base used ngram=2; QT ngram=0).

### Dataset `ngocdang83/tran-vi-teacher`

- ~351k **strict-clean** ZH→VI paragraph parallels distilled from **Gemini 2.5/3.0/3.1** (mostly Flash-Lite ~86%, Flash ~16%, Pro ~3%).
- Gates: finish stop, closed tags, line-count match, **no Han leak**, length/ratio sanity.
- Intended as **teacher/distill pool** for MT — not literary final gold; Pro subset is the better seed if ever reviewing.

**Fine-tune later vs pretrained now?**

- **Now:** use **pretrained only**. Both candidates already absorbed this teacher set; another FT pass without Pineline-specific name/glossary supervision adds cost and regression risk.
- **Later (optional):** FT or continue-train **only if** (a) post-MT gates still leave systematic glossary misses on Pineline jobs, (b) a locked Pineline term bank + human/LLM-judged holdout exists, (c) modern vs convert is an explicit data split. Prefer adapter/small continue over full retrain. **No training in this cycle.**

---

## Production wiring decision

### Safer as OPTIONAL draft BEFORE LLM

**HachimiMT-60-QT**, and only when:

1. Job genre = xianxia / convert-register expected.
2. Feature flag **off by default**; never on the critical path of `translate.py`.
3. Output is a **hint/draft** for the LLM (or a UI preview), not the final `sub.vi`.
4. Post-MT gates run (below) before any LLM sees the draft as “trusted”.

Base model: keep as A/B alternate for **modern-register** jobs; do not default either.

### Must NEVER be wired into `translate.py` yet

1. Default translator / LLM replacement.
2. Silent fallback when LLM fails (would ship convert-locked or glossary-wrong lines).
3. Any path that writes `sub.vi.srt` / script VI without LLM + glossary pass.
4. Batch retranslate of historical jobs without per-line name lock.
5. QT with base decode knobs (`no_repeat_ngram_size>0`) — name corruption risk per HF card.
6. Unsegmented long paragraphs (>~200–250 ZH chars) without chunking (name drift).

---

## Proposed auto-fix / gates (proposals only — do not implement in `Z:\PinelineV2`)

1. **Post-MT name lock**  
   - From `script.json` / glossary: every locked ZH span must appear as the pinned VI form (fold-insensitive).  
   - Fail line → drop MT draft for that line (LLM-only) or force replace.

2. **Alias remap gate**  
   - Job-specific: `天虚圣地`→`Thiên Hư Thánh Điện` when gold/script says so; `店主`→`Điện chủ`; `真禅`/`真传`→`chân truyền`.  
   - MT raw must not win over script aliases.

3. **Register filter**  
   - Detect convert vs modern pronoun clusters; if job profile = modern and MT is ≥X% convert (or vice versa), reject draft.  
   - Adjacent-line flip rate vs *job profile* (not vs gold during live run).

4. **CJK / empty / length gates**  
   - Reject if any Han in VI, empty, or VI/ZH char ratio outside [0.8, 5.0] (align with teacher strict-clean ideas).

5. **Idiom / sense canaries**  
   - Small per-job or global probe list (`一锅端`, `摊上`, `吐血三升`, `历练`…) — if MT misses canary sense class, demote model for that job.

6. **LLM trust boundary**  
   - Draft may be passed as `mt_draft` field; prompt must say draft is untrusted; glossary + ZH source remain authoritative.

7. **Bench gate before any flag flip**  
   - Require second job (modern urban) + this xianxia job: QT win-rate vs base, name-lock ≥99% after gate, zero CJK, catastrophic sense ≤ threshold on canaries.

---

## Recommendation matrix

| Use case | Choice |
| --- | --- |
| Pineline production translate path | **Neither** |
| Optional draft, xianxia/convert | **QT** + gates |
| Optional draft, modern natural VI | **Base** (re-bench first) |
| Training this week | **None** — use pretrained |
| Future FT data | Pineline glossary-locked pairs ≫ raw `tran-vi-teacher` replay |

---

## Evidence pointers

- Hyps: `D:\PinelineV2_tmp\mt_bench\out\hyp_hachimi60.json`, `hyp_hachimi60_qt.json`
- Scores: `D:\PinelineV2_tmp\mt_bench\out\auto_score.json`
- Meta: `D:\PinelineV2_tmp\mt_bench\samples\meta.json` (job `0a5f60aead18`)
- HF: [robebo116/60-zh-vi](https://huggingface.co/robebo116/60-zh-vi), [HachimiMT-60-QT](https://huggingface.co/ngocdang83/HachimiMT-60-QT), [tran-vi-teacher](https://huggingface.co/datasets/ngocdang83/tran-vi-teacher)

---

## Final line

**NO-GO for production `translate.py` wiring. CONDITIONAL GO for off-by-default QT draft-before-LLM on convert/xianxia only, after name/glossary/register gates — not implemented here.**
