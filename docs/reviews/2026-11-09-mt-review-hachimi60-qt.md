# Review: HachimiMT-60-QT (ngocdang83/HachimiMT-60-QT)

- **Date:** 2026-11-09
- **Job / gold:** `0a5f60aead18` → `samples/gold.json` (n=110, name_hit=40)
- **Hyp:** `out/hyp_hachimi60_qt.json`
- **Auto:** `out/auto_score.json` → key `hachimi60_qt`
- **Decode (from run_summary):** beam=1, `no_repeat_ngram_size=0`, repetition_penalty=1.0
- **Model card note:** convert voice `ta/ngươi/hắn/nàng` (archaic by design); do not enable `no_repeat_ngram_size` (name mangling risk). Trade-off: modern scenes also get convert voice.

## Auto metrics (context)

| Metric | hachimi60_qt | hachimi60 (base) |
|---|---:|---:|
| empty / cjk_leak | 0 / 0 | 0 / 0 |
| exact_match_ref | 1 | 0 |
| fold_match_ref | 5 | 2 |
| avg_ref_token_recall | 0.688 | 0.672 |
| pronoun_style_flips_adj | 10 | 6 |
| name_lock `逆天而行` (auto) | 7/7 “ok” | 7/7 |

**Auto name_lock is a false positive.** Checker accepts substring `Nghịch Thiên` inside wrong string `Nghịch thiên hành động`. Human check: **0/7** lines with `逆天而行` emit glossary form `Nghịch Thiên Nhi Hành`; 6/7 are literalized as verb phrase; 1/7 is truncated `Nghịch Thiên Hành`.

Pronoun corpus skim (whole n=110): MT has **0× tôi, 0× cậu**; gold has **10× tôi, 7× cậu**. MT uses **ta / ngươi / hắn** heavily — matches QT design, mismatches this job’s Pineline urban/mixed gold.

---

## Line review (≥25; severity 0–3)

Scale: **0** OK / style-only acceptable · **1** mild (register / awkward) · **2** clear error (sense, name drift, broken idiom) · **3** critical (MC name mangled, nonsense, meaning break).

| # | i | type | sev | zh (short) | note |
|---|---:|---|---:|---|---|
| 1 | 39 | name+dlg | 2 | 系统老爷爷逆天血脉喂！ | Garbled system yell; “lão gia…huyết mạch này” loses urgency / vocative of gold. |
| 2 | 126 | name+dlg | 2 | 将天虚圣殿发展为…至尊新手大礼包 | Syntax mash: faction development fused into “gói quà tân thủ”; loses two-clause system UI beat. |
| 3 | 255 | name | 1 | …天虚圣地…什么鸟样 | `Thánh Địa` vs series lock `Thánh Điện`; sense OK. |
| 4 | 340 | dlg | 0 | …本座…跟他现在差不多 | `bản tọa`/`hắn` fine for convert; meaning OK. |
| 5 | 537 | name | 3 | 天虚圣殿所有徒有一个算一个 | Nonsense: “Tất cả chỉ số một trong số…” — idiom `有一个算一个` failed. |
| 6 | 691 | name+dlg | 1 | …一锅端了 | Idiom “một mẻ hốt gọn” good; `Hắn` + archaic OK for QT; gold more colloquial. |
| 7 | 785 | name | 2 | …天虚殿主印爵… | `ấn tước` not locked `Ấn Thiên Tước`; title lowercased / split wrong. |
| 8 | 853 | name+dlg | 1 | 你跑到我天虚圣殿来撒野 | Intentional QT: `Ngươi…ta` vs gold `cậu…tôi`. Sense OK. |
| 9 | 1089 | dlg | 2 | 狗样…邪魅狂凝 | Over-literal “hình chó má”; `cuồng ngưng` opaque vs `cuồng ngạo`. |
| 10 | 1129 | dlg | 1 | 我去不好啊 | `Ta đi không tốt` vs gold `Tôi đi không ổn sao?` — register flip + flatter question. |
| 11 | 1132 | name | 3 | …天虚殿主应天爵士嘛？ | Hallucinated `Ứng Thiên tước sĩ`; gold is just Điện chủ address. |
| 12 | 1213 | name+dlg | 1 | 从现在起你就是我…左护法 | `ngươi`/`ta` vs `cậu`; name `Tả hộ pháp` + Thánh Điện OK. |
| 13 | 1227 | dlg | 3 | 简直帅的批爆 | Slang collapse: “đẹp trai mà **phê bình**” — meaning destroyed. |
| 14 | 1271 | dlg | 3 | 还是先天的 | `先天` → “Vẫn là ngày xưa” (wrong sense; should be Tiên Thiên). |
| 15 | 1336 | name | 2 | 若是得到了逆天打击 | `đả kích nghịch thiên` ≠ gold `trợ lực nghịch thiên` (buff vs hit). |
| 16 | 1516 | dlg | 2 | …天选， | Vocative `Thiên tuyển` vs character `Thiên Huyền`. |
| 17 | 1599 | name | 3 | 天虚圣殿的应天诀呢？ | MT invents skill `Ứng Thiên Quyết`; gold = ask about Điện chủ. |
| 18 | 1708 | dlg | 2 | …羽化仙去了 | “đi Vũ Hóa Tiên” calque; gold `phi thăng` clearer. |
| 19 | 1806 | name | 3 | 逆天而行， | **MC name → “Nghịch thiên hành động”** (verb phrase). |
| 20 | 1854 | name | 2 | 天下无双那小子镇着 | Character `Vô Song` → “Tiểu tử vô song thiên hạ”. |
| 21 | 1880 | name+dlg | 3 | 哦，他叫逆天而行 | Name mangled + `hắn gọi là` (he *is called* → he *calls*). |
| 22 | 1940 | dlg | 2 | …我知道我画 | ASR junk kept: “ta biết ta **vẽ**”; gold heals to “tôi nói”. |
| 23 | 2022 | dlg | 2 | 谨遵电教教诲 | ASR `电教` → “lời dạy của điện”; should be Điện chủ. |
| 24 | 2027 | name+dlg | 2 | 你便是我印天诀的首徒 | `Ấn Thiên Quyết` ≠ glossary `Ấn Thiên Tước`; + `Ngươi`/`ta`. |
| 25 | 2098 | dlg | 2 | 混沌道体…先天机面魔体 | Body/title soup; drops `Nguyên Thủy`, invents `Tiên Thiên Cơ Diện`. |
| 26 | 2227 | name | 2 | 这个天下无双的确是可造之材 | Again no locked `Vô Song`; literal “Thiên hạ vô song”. |
| 27 | 2473 | dlg | 2 | 目标将天墟殿的旗帜… | `Thiên Khư Điện` (wrong graph/sound) ≠ Thiên Hư Thánh Điện. |
| 28 | 2955 | name | 2 | 哼，逆天而行这名字… | Truncated `Nghịch Thiên Hành` (missing `Nhi`). |

**Reviewed n = 28** · **Σ severity = 55** · **mean severity ≈ 1.96**

Breakdown: sev0=1 · sev1=6 · sev2=14 · sev3=7  
Among **name_hit** subset in table (18 lines): mean ≈ **2.06**.

---

## Error catalog

### A. Pronoun / voice consistency
- QT **always** prefers convert set (`ta`, `ngươi`, `hắn`); never emits Pineline urban/mixed `tôi`/`cậu` on this sample.
- Gold for job `0a5f60aead18` is **mixed**: xianxia titles (`bản tọa`, `vi sư`) + modern/urban 2nd–1st (`cậu`/`tôi`) in peer/system/narration beats.
- Auto `pronoun_style_flips_adj=10` (higher than base) — QT is internally archaic-leaning but still flips when neutral lines sit between arch-marked ones.
- **Verdict (a):** Unusable as drop-in for Pineline jobs that want `tôi`/`cậu`. Only fits **QT-only / convert-voice genres**, and even then modern meta jokes (novel-author aside, system UI) sound anachronistically classical.

### B. Name accuracy vs glossary
Glossary targets (from `score_auto.NAME_LOCKS` / gold heal):
- `逆天而行` → **Nghịch Thiên Nhi Hành**
- `印天爵` / `印天诀`(ASR) → **Ấn Thiên Tước**
- Faction: **Thiên Hư Thánh Điện**; peer: **Thái Hư Thánh Địa**

Failures:
1. **MC name literalization (sev3 cluster):** 1806/1952/1964/2153/2949 → `Nghịch thiên hành động`; 1880 same + wrong verb; 2955 truncated. Auto 7/7 “ok” is invalid (substring FP).
2. **Title/person collapse:** `印爵`→`ấn tước`; `印天诀`→`Ấn Thiên Quyết`; `应天爵士`/`应天诀` invent `Ứng Thiên tước sĩ` / `Ứng Thiên Quyết`.
3. **Alias characters:** `天下无双` not locked to `Vô Song`.
4. **Faction graph noise:** `天虚圣地`→`Thánh Địa`; `天墟殿`→`Thiên Khư Điện`.
5. Place variants: `藏/葬天渊` → `Tàng`/`Táng` mixed (gold prefers `Táng`/`Tàng` consistently per line).

**Verdict (b):** Name accuracy **fails production bar** without a hard glossary post-lock. Auto metric currently **hides** the worst MC failure.

### C. Idiom / colloquial quality
- **Good / usable:** `一锅端`→“một mẻ hốt gọn”; `油尽灯枯`; `封山避世`→“phong sơn lánh đời”; many cultivation boilerplate lines are fluent.
- **Broken slang / idiom:** `帅的批爆`→“phê bình”; `有一个算一个`→numeric nonsense; `先天的`→“ngày xưa”; `逆天亲历`→“thân phận nghịch thiên” (affinity→status).
- **ASR pass-through:** `我画`, `电教` kept instead of healed like gold.
- **Calques:** `羽化仙去`, `封山毕业仪式`→“nghi thức tốt nghiệp phong sơn”.

**Verdict (c):** Mid fluency on stock xianxia prose; **weak on net-speak / system / ASR-noisy lines** — same lines Pineline gold usually heals.

---

## Examples (representative)

**Critical name mangling**
- zh `逆天而行。` → mt `Nghịch thiên hành động.` · ref `Nghịch Thiên Nhi Hành.`

**Register mismatch vs urban/mixed gold**
- zh `你跑到我天虚圣殿来撒野，` → mt `Ngươi…ta…` · ref `cậu…tôi…`

**Idiom collapse**
- zh `简直帅的批爆，` → mt `Đúng là đẹp trai mà phê bình,`

**Meaning break**
- zh `还是先天的。` → mt `Vẫn là ngày xưa.` · ref `lại còn là Tiên Thiên nữa.`

---

## Pineline-use verdict

### **Reject for current pipeline** (primary)

Not safe as default NMT for Pineline urban/mixed (or glossary-locked) jobs:

1. Convert pronouns conflict with `tôi`/`cậu` product voice.
2. Protagonist name systematically demoted to a verb phrase — glossary auto-check currently lies.
3. Title/ASR lines invent skills/people (`Ứng Thiên Quyết`, `Ấn Thiên Quyết`).

### Secondary niche (not “approve”)

| Use case | OK? |
|---|---|
| Pure convert / cổ trang QT genre, human post-edit + **hard glossary lock** | Draft-only |
| Urban / mixed / system-comedy / modern aside jobs | No |
| Replace current Pineline NMT without postprocess | No |

### Recommendation

1. **Do not ship QT as Pineline default** for current voice + glossary pipeline.
2. If experimenting on QT-only titles: keep beam=1, keep `no_repeat_ngram_size=0` (card warning), **mandatory** post glossary replace for `逆天而行` and peer locks — do not trust auto name_lock until matcher requires word-boundary / full form (reject bare `Nghịch Thiên` substring).
3. Prefer base `hachimi60` (or current prod) for mixed-register jobs; reserve QT only when product explicitly wants `ta/ngươi/hắn` throughout.
4. Re-score after fixing name_lock heuristic; treat human mean severity ~2.0 on this set as the release bar signal (need ≪1.0 with names clean).

---

## Summary numbers

- Lines reviewed: **28** (name_hit + dialogue)
- Mean severity: **~1.96** (name_hit subset ~2.06)
- Critical (sev3) rate: **7/28 ≈ 25%**
- `逆天而行` human lock rate: **0/7** (auto falsely 7/7)
- `tôi`/`cậu` emissions: **0 / 0** (gold 10 / 7)
- **Verdict: reject for current Pineline pipeline**; QT-genre = draft-only + glossary heal only.
