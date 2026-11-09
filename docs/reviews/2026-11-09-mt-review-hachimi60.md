# Manual NMT review — robebo116/60-zh-vi (HachimiMT-60)

- **Date:** 2026-11-09
- **Job / sample:** `0a5f60aead18` gold n=110 (`samples/gold.json`)
- **Hypothesis:** `out/hyp_hachimi60.json`
- **Auto metrics:** `out/auto_score.json` → key `hachimi60`
- **Scope:** isolated sandbox only; no Pineline production code touched

## Summary verdict

**Usable as draft with glossary post-edit — do NOT replace the Pineline LLM pipeline alone.**

Fluency is generally readable for xianxia dialogue (no empty lines, **cjk_leak=0**). Sense on plain lines is often acceptable. But **proper-name locking fails systematically**: character names are paraphrased as idioms, ASR near-names are followed literally, and several sense errors would ship bad subtitles without a locked glossary / LLM polish pass.

| Auto (hachimi60) | Value |
|---|---|
| n / empty / cjk_leak | 110 / 0 / 0 |
| exact_match_ref / fold_match_ref | 0 / 2 |
| avg_ref_token_recall | 0.672 |
| pronoun_style_flips_adj | 6 |
| name_lock 逆天而行 (auto) | 7/7 “ok” |

**Caution:** auto `name_locks` for `逆天而行` only checks the **Nghịch** syllable (vs Nghị). Manual review finds **0/7** lines use the locked form **Nghịch Thiên Nhi Hành**; all 7 are literal phrase renderings.

## Special name checks

| ZH / expected | Result in hyp sample |
|---|---|
| **逆天而行 → Nghịch (not Nghị)** | **Syllable PASS** — MT always uses *Nghịch*, never *Nghị*. |
| **逆天而行 → Nghịch Thiên Nhi Hành** (glossary lock) | **FAIL** — consistently *Nghịch thiên mà đi / mà hành* (idiom, not PN). |
| **印天爵 → Ấn Thiên Tước** | **Not present** as `印天爵` in the 110-line gold sample. Near-hits: `印爵`→*ấn tước* (i=785); `印天诀`→*Ấn Thiên Quyết* (i=2027, ZH is 诀; ref maps to person *Ấn Thiên Tước*); `应天爵士`→*Ứng Thiên Tước Sĩ* (i=1132). |
| **沈道陵 → Thẩm Đạo Lăng** | **N/A in sample** — neither ZH nor VI in hyp/gold. Job glossary/script uses **Thẩm Đạo Ngôn** (not Lăng) elsewhere; not in this 110-line slice. |

## Manual review set

Reviewed **30 lines** (15 `name_hit=true`, 15 normal). Severity: **0=ok, 1=minor, 2=moderate, 3=severe / hallucination / wrong name**.

| i | name_hit | sev | error types | note |
|---|---|---|---|---|
| 39 | Y | 1 | sense, register | Misses 喂→“đâu rồi”; *lão gia* vs *lão già* |
| 126 | Y | 2 | literal idiom, truncation | *cường ngưu* for 牛逼; gift-pack clause mangled |
| 255 | Y | 1 | register / glossary | *Thánh Địa* vs locked *Thánh Điện* (ZH also 圣地) |
| 332 | N | 1 | wrong HV casing | *ấn đế / ngọc tỷ* not title-cased |
| 340 | N | 0 | — | Near-paraphrase of ref |
| 345 | N | 2 | sense, register | *chủ tiệm* for 店主 (should be Điện chủ in context) |
| 468 | N | 2 | wrong HV name / ASR follow | *Thập Đại Chân Thiền* vs *chân truyền* (ZH 真禅) |
| 537 | Y | 2 | sense / literal | *một người tính một* opaque vs “một người một suất” |
| 583 | N | 0 | — | Match |
| 691 | Y | 2 | sense | 一锅端 → *Cướp sạch* (should be wipe-out / gom hết) |
| 785 | Y | 2 | wrong HV name | *ấn tước* lowercase fragment for 印爵≈Ấn Thiên Tước |
| 1021 | Y | 0 | — | Good sense + name |
| 1089 | N | 1 | literal | *bộ dáng chó má* for 狗样 (over-literal) |
| 1132 | Y | 3 | wrong HV name, hallucination | *Ứng Thiên Tước Sĩ* invented from ASR 应天爵士 |
| 1227 | N | 0 | — | *ngầu lòi* OK slang for 帅的批爆 |
| 1336 | Y | 2 | sense | 逆天打击 → *đả kích* vs ref *trợ lực* |
| 1516 | N | 2 | wrong HV name | *Thiên Tuyển* vs *Thiên Huyền* |
| 1599 | Y | 3 | wrong HV name, sense | *Ứng Thiên Quyết* vs ref “Điện chủ…” |
| 1708 | N | 3 | sense / hallucination | 羽化仙去 → *Vũ Hóa Tiên* (should be phi thăng / hóa tiên) |
| 1806 | Y | 3 | wrong HV name, literal idiom | PN → *Nghịch thiên mà đi* |
| 1824 | Y | 2 | sense / literal | 亲历 → *trải nghiệm* vs *tương thích* |
| 1880 | Y | 3 | wrong HV name, pronoun | PN phrase; *hắn* vs *cậu ta* |
| 1940 | N | 2 | sense (ASR follow) | 我画 → *ta vẽ* (garbage ASR kept) |
| 1952 | Y | 3 | wrong HV name | PN → *Nghịch thiên mà hành* |
| 1964 | Y | 3 | wrong HV name | *nghịch thiên mà đi* after Đệ tử |
| 2022 | N | 3 | wrong HV name / ASR | 电教 → *Điện Giáo* vs *Điện chủ* |
| 2027 | Y | 2 | wrong HV name | *Ấn Thiên Quyết* vs *Ấn Thiên Tước* (ZH 诀) |
| 2227 | Y | 2 | wrong HV name, truncation | *Thiên hạ vô song* phrase; drops “nhân tài bồi dưỡng” sense |
| 2473 | N | 2 | wrong HV name | *Thiên Khư Điện* vs *Thiên Hư* |
| 2927 | N | 2 | sense | 够分了 → *Đủ điểm* vs *đủ chia* |

### Severity stats (n=30)

| sev | count | share |
|---|---|---|
| 0 | 4 | 13% |
| 1 | 4 | 13% |
| 2 | 13 | 43% |
| 3 | 9 | 30% |

- **Mean severity: 1.90**
- **Share sev≥2: 73%** (22/30)
- **Share sev=3: 30%** (9/30) — concentrated on name PNs + ASR-induced title errors

## Top failure modes (ranked)

1. **Wrong HV / unlocked proper names** — Character names rendered as free phrases (`逆天而行`, `天下无双`) or wrong HV (`Ứng Thiên…`, `Ấn Thiên Quyết`, `Thiên Khư`).
2. **Literal idiom / calque** — 牛逼→cường ngưu; PN decomposed; 狗样 over-literal.
3. **Sense error** — 一锅端, 羽化仙去, 够分了, 逆天打击, 亲历.
4. **ASR garbage followed** — 电教, 我画, 应天爵士 / 应天诀 treated as real terms.
5. **Pronoun / register vs Pineline style** — frequent *ngươi/ta/hắn* where ref uses *cậu/tôi*; *chủ tiệm* vs *Điện chủ*; auto notes 6 pronoun_style_flips_adj.
6. **Truncation / clause merge** — long system/gift lines lose segment boundaries (i=126).
7. **CJK leak** — none observed (auto + manual).
8. **Nghị vs Nghịch** — **not** a failure for this model on this sample (good); production SRT/display still has Nghị drift elsewhere in the job.

## Example triples (zh / vi_ref / vi_mt)

### 1 — OK dialogue (sev 0)
- **zh:** 那岂不是说本座当年也就跟他现在差不多？呃，
- **vi_ref:** Vậy chẳng phải nghĩa là bản tọa năm đó cũng chỉ ngang ngửa hắn bây giờ sao? Ờ,
- **vi_mt:** Vậy chẳng phải nói bản tọa năm đó cũng chỉ ngang ngửa với hắn bây giờ sao? Ờ,

### 2 — OK name-bearing (sev 0)
- **zh:** 说明对方根本没把天虚圣殿当回事。
- **vi_ref:** cho thấy đối phương căn bản chẳng coi Thiên Hư Thánh Điện ra gì.
- **vi_mt:** Điều này chứng tỏ đối phương hoàn toàn không coi Thiên Hư Thánh Điện ra gì.

### 3 — PN → idiom (sev 3) ★ special
- **zh:** 逆天而行，
- **vi_ref:** Nghịch Thiên Nhi Hành,
- **vi_mt:** Nghịch thiên mà đi,

### 4 — PN in sentence (sev 3) ★ special
- **zh:** 哦，他叫逆天而行。
- **vi_ref:** Ồ, cậu ta tên là Nghịch Thiên Nhi Hành.
- **vi_mt:** Ồ, hắn gọi là nghịch thiên mà hành.

### 5 — Ấn Thiên near-miss (sev 2) ★ special
- **zh:** 你便是我印天诀的首徒，
- **vi_ref:** cậu chính là thủ đồ của Ấn Thiên Tước tôi,
- **vi_mt:** Ngươi chính là thủ đồ của Ấn Thiên Quyết ta

### 6 — Hallucinated title from ASR (sev 3)
- **zh:** 还站着天虚殿主应天爵士嘛？
- **vi_ref:** Còn đứng đó làm gì, Điện chủ Thiên Hư?
- **vi_mt:** Còn đứng đó là Thiên Hư Điện Chủ Ứng Thiên Tước Sĩ sao?

### 7 — Sense / wrong verb (sev 2)
- **zh:** 把他连同天虚圣殿那些高阶战力一锅端了。
- **vi_ref:** đoàn kết cả hắn cùng đám chiến lực cao cấp Thiên Hư Thánh Điện.
- **vi_mt:** Cướp sạch hắn cùng các chiến lực cao giai của Thiên Hư Thánh Điện.

### 8 — Literal slang (sev 2)
- **zh:** 将天虚圣殿发展为诸天万界最牛逼的势力至尊新手大礼包，
- **vi_ref:** Phát triển Thiên Hư Thánh Điện thành thế lực bá đạo nhất chư thiên vạn giới. Nhận gói quà tân thủ chí tôn!
- **vi_mt:** Đem Thiên Hư Thánh Điện phát triển thành thế lực cường ngưu nhất Chư Thiên Vạn Giới Đại Lễ Bao

### 9 — Hallucinated immortal title (sev 3)
- **zh:** 本座刚从玄机山已确认太虚圣主徐长生已然羽化仙去了。
- **vi_ref:** Bản tọa vừa xác nhận tại Huyền Cơ Sơn, Thái Hư Thánh chủ Từ Trường Sinh đã phi thăng.
- **vi_mt:** Bổn tọa vừa từ Huyền Cơ Sơn xác nhận Thái Hư Thánh Chủ Từ Trường Sinh đã hóa thành Vũ Hóa Tiên.

### 10 — ASR followed literally (sev 3)
- **zh:** 谨遵电教教诲，
- **vi_ref:** Tuân lệnh Điện chủ,
- **vi_mt:** Cẩn tuân theo giáo huấn của Điện Giáo,

### 11 — Sense flip (sev 2)
- **zh:** 够分了。
- **vi_ref:** đủ chia rồi.
- **vi_mt:** Đủ điểm rồi.

### 12 — Context sense (sev 2)
- **zh:** 跟店主您这种纯凭自身修为横扫东荒的绝世高手相比，
- **vi_ref:** So với Điện chủ, tuyệt thế cao thủ chỉ凭 tu vi bản thân quét sạch Đông Hoang,
- **vi_mt:** So với cao thủ tuyệt thế như chủ tiệm, người chỉ dựa vào tu vi bản thân quét ngang Đông Hoang

## Recommendation

1. **Do not** drop-in replace Pineline LLM / glossary-aware translate with raw Hachimi-60.
2. **Do** consider Hachimi-60 as a **cheap first draft** *if* followed by:
   - hard glossary lock (至少: Nghịch Thiên Nhi Hành, Ấn Thiên Tước, Thiên Hư Thánh Điện, Vô Song / Thiên Hạ Vô Song),
   - ASR-noise filter before MT (电教/我画/应天爵*),
   - light LLM or rule post-edit for pronouns + sense.
3. Treat auto `name_locks` “7/7 ok” as **misleading** until the metric requires full locked PN string, not just Nghịch⊃Nghị.
4. Re-bench when sample includes explicit `印天爵` and `沈道陵` lines (absent here); current special checks for those two are **inconclusive on this slice**.
5. Compared to production SRT drift to **Nghị**, this model’s **Nghịch** syllable is a plus — but phrase rendering still blocks ship-ready name consistency.

**Bottom line:** draft-quality NMT for dialogue; **never** as sole final for named xianxia jobs without locks + post-edit.
