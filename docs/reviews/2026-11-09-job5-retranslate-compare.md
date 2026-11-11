# Job5 retranslate sandbox — COMPARE vs YouTube VI

- Source job: `9c3af49061a2` (series 5)
- Sandbox: `D:\PinelineV2_tmp\job5_retranslate_sandbox`
- Old VI: YouTube auto-captions `qqHgKvMZqaQ.vi.vtt` (via `cues_clean.jsonl`)
- New VI: SenseVoiceSmall **CPU** ZH → HachimiMT-60-zh-vi (**primary**) + review (`AUTO_REVIEW`)
- ASR note: `nano_fa` skipped — GPU ~11.7/12GB held by llama-server :8083; used SenseVoice CPU + `SKIP_VRAM_FREE=1`

## Stats (heuristic)

- Total aligned rows: **194** (all 6 windows end-to-end)
- Clearly improved: **149** (~77%)
- Roughly same: **4**
- Worse: **0** (auto-score; see caveats)
- Unclear / mixed: **41**

Most “improved” = YT auto-caption glue/overlap vs clean NMT sentence. Still a strong signal that Pineline ZH→VI beats YT-of-dubbed-audio.

### Per window

| win | offset_s | n | improved | same | worse | unclear |
|---|---:|---:|---:|---:|---:|---:|
| 00 | 60 | 27 | 20 | 1 | 0 | 6 |
| 01 | 600 | 38 | 32 | 1 | 0 | 5 |
| 02 | 1500 | 28 | 19 | 0 | 0 | 9 |
| 03 | 3600 | 35 | 30 | 0 | 0 | 5 |
| 04 | 7200 | 30 | 20 | 0 | 0 | 10 |
| 05 | 10000 | 36 | 28 | 2 | 0 | 6 |

## Top 10 before/after (curated)

### 1. 雪姬 → Tuyết Cơ (YT: “huyết cơ / Đằng Dã”)

- **ZH:** 杀雪姬连接杀带奖励30万，
- **VI old:** thanh vọng hủy diệt năm vạn chú địa của công xã Đằng Dã sát huyết cơ kết nối bao
- **VI new:** Sát Tuyết Cơ kết nối sẽ được thưởng 30 vạn,

### 2. 噬神 → Phệ Thần (YT: “thực thần ăn”)

- **ZH:** 噬神每技能都无比强大，
- **VI old:** nổ trang bị ám kim rồi. Lần này toàn bộ trang bị đều cho thực thần ăn. Mau đút
- **VI new:** Phệ Thần mỗi kỹ năng đều vô cùng cường đại,

### 3. 噬神 gear line

- **ZH:** 这次的装备全部为噬神，
- **VI old:** lười xem nữa, kinh nghiệm chưa bao giờ là thứ tôi mong muốn. / Quái vật từ cấp 90…
- **VI new:** Lần này trang bị toàn bộ là Phệ Thần,

### 4. 子优 name lock (YT lowercase “tử ưu” mid-glue)

- **ZH:** 还得给子优一班，
- **VI old:** vạn 20 người điểm, còn phải đưa tử ưu một nửa vào tay mới hơn 4000. 87 tháng
- **VI new:** Còn phải cho lớp Tử Ưu Nhất,
- *Caveat:* “一班” NMT → “lớp … Nhất” is still awkward (share/portion sense).

### 5. 陈峰 → Trần Phong

- **ZH:** 可我不能保证陈峰会像放过地狱之门一样放过我，
- **VI old:** thì sao? Tôi tin rằng hắn sẽ không so đỏ. đi xin lỗi hắn đi…
- **VI new:** Nhưng tôi không thể cam đoan Trần Phong sẽ buông tha cho tôi giống như bỏ qua Địa Ngục Chi Môn

### 6. 尘封 → Trần Phong (glossary)

- **ZH:** 那个尘封可以在这片空间随意穿梭。
- **VI old:** …Tôi ra tay thế nào? Trần Phong có thể tự…
- **VI new:** Trần Phong có thể tùy ý xuyên qua không gian này.

### 7. 圣级 consistency

- **ZH:** 面对圣级。
- **VI old:** máu của đêm khuya, 1 phút 26 triệu, chỉ dựa vào độc dược hơn 10 tiếng, đối mặt
- **VI new:** Đối mặt với Thánh cấp.

### 8. De-glue party loot names

- **ZH:** 林子一人一件，
- **VI old:** …hộ sư tử ưu hạo nhiên khinh vũ lâm tử ngân tử mỗi người một món…
- **VI new:** Lâm Tử mỗi người một cái,

### 9. YT “9 vạn năm” hallucination → numeric XP line

- **ZH:** 一头95000经验，
- **VI old:** …Một con 9 vạn năm kinh nghiệm, ngày 87…
- **VI new:** Một con 9500 kinh nghiệm,
- *Caveat:* NMT dropped a zero (95000→9500); still better than YT “9 vạn năm”.

### 10. Reward package de-glue

- **ZH:** 第二个金色礼包了，
- **VI old:** công xã Đằng Dã sát huyết cơ kết nối bao các thưởng 30 vạn à hiện tại vừa vặn 101…
- **VI new:** Gói quà màu vàng thứ hai,

## Highlight clusters

- **Names:** 雪姬→Tuyết Cơ; 噬神→Phệ Thần (not “thực thần”); 子优→Tử Ưu; 陈峰/尘封→Trần Phong; 圣级→Thánh cấp
- **YT garbage removed:** “gà Hán / Đằng Dã / huyết cơ / 9 vạn năm / overlapping glue”
- **Pronoun/style:** review kept most NMT; hard-locks + style polish applied in pipeline

## Caveats (residual errors)

- SenseVoice CPU ≠ nano_fa quality: e.g. `约8级` → ASR `月8级` → VI “Ngày 8 cấp…”
- NMT number shrink: `95000`→`9500`, `4000多`→`400`
- Auto “worse=0” under-counts numeric/ASR meaning slips when YT text is also wrong
- Compare aligns by absolute time overlap; YT cue fragmentation can attach multiple old cues to one new row

## Files

- `compare.jsonl` — `{win,i,start,end,zh,vi_new,vi_old,notes}`
- `compare_stats.json`, `pipeline_status.json`, `README.md`
