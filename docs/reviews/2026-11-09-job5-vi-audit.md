# VI Transcript Audit — Job `9c3af49061a2` (series "5", Game Lit / Fantasy)

- **Date:** 2026-11-09
- **Source:** YouTube auto-captions `D:\PinelineV2_tmp\job5_yt\qqHgKvMZqaQ.vi.vtt` (script.json đã xóa sau merge)
- **Glossary:** `Z:\PinelineV2\data\series_glossary\5.json`
- **Cleaned cues:** 4132 (flash/completed-line units; raw timed blocks=8530, progressive=4398, flash=4132)
- **Stitched sentence-ish units:** 4025 (phục vụ đọc lỗi)
- **Sample size:** 190 unique cleaned cues (+ 102 stitched windows)
- **Verdict:** VI **kém** — đủ nặng để user complaint hợp lệ: tên lệch glossary, đại từ loạn, calque Hán-Việt dày, ASR-of-TTS ra câu vô nghĩa.

## Top findings

1. **Tên nhân vật lệch / thiếu so với glossary** — `Lão Đằng` (~14) lẫn **Lão Đường** (3, cửa sổ 3-cue) / **Lão Đẳng** (1); `Tuyết Cơ` lẫn **Huyết Cơ**; **Tĩnh Tĩnh = 0** (chỉ "Chị Tĩnh"); **Kawasaki = 0**.
2. **Pronoun / xưng hô chaos** — `tôi`/`cậu` chiếm đa số (đúng hướng hiện đại) nhưng vẫn còn `ta` (226), `nàng`, `huynh` (10), và **đại ca** (3; glossary khóa **lão đại** ≈74); bare `ta`+`tôi` vẫn xuất hiện.
3. **Calque Hán-Nôm thô rất dày** — `hắn` (**215** cue), `sinh mệnh` (30), `công kích vật lý`, `ám kim`, `thánh/tiên cấp` mở đầu và suốt phim — đây là tín hiệu mạnh nhất của bản VI “đúng chữ, sai tai người xem”.
4. **ASR-of-TTS artifacts rõ** — `gà Hán Đế`, `lạc đà chạy mau` (kề `Lão đường!`), `thợ giác rưởi` (4), `Tống Thạch`, `Hảo hảo hảo`.
5. **Redundant / stutter** — ~94 cue lặp từ (`X X`), 66 particle `à/ờ/ừ`, 40 `ha ha`; nhiều câu rỗng nghĩa.
6. **Stat/number garble** — HP/`sinh mệnh` lặp trong cùng đoạn (Khánh Vân tiên giả); số + đơn vị bị cắt giữa cue flash.
7. **Wrong/odd meaning** — `gặm được một con` (calque 啃), `chú/con ong nhỏ`, `bà hung ác` — nghe được từ nhưng sai/lệch ngữ cảnh game.
8. **Không có script.json gốc** — audit chỉ trên YT auto-captions của audio đã TTS; lỗi là hỗn hợp dịch VI gốc + TTS + ASR lại, không tách được từng tầng.

## Error taxonomy (counted events on cleaned cues unless noted)

| Category | Approx. event count | Notes |
|---|---:|---|
| Wrong/inconsistent character names vs glossary | ~9+ (window) | Lão Đường×3 + Đẳng×1 + Huyết Cơ×1 + Chị Tĩnh×1; Tĩnh Tĩnh=0; Kawasaki=0 |
| Pronoun / address chaos (ta/tôi/ngươi/anh/em/đại ca) | ~26 | ta=226, tôi=528, cậu=548, ngươi=5, đại ca=3, huynh=10, nàng=3 |
| Calque / Hán-Nôm thô (sinh mệnh, hắn, ám kim, …) | 252 | hắn=215; sinh mệnh=30; công kích vật lý mở đầu |
| Redundant / stutter / meaningless fillers | 200 | stutter≈94, à/ờ≈66, haha≈40 |
| Number/stat garble | 5 | HP lặp, gà Hán + số, vạn vạn |
| Obvious nonsense / ASR-of-TTS artifacts | 7+ | gà Hán, lạc đà, thợ giác rưởi×4, Tống Thạch |
| Obvious wrong/odd meaning (non-name) | 4+ | gặm được, ong nhỏ, bà hung ác; nhiều câu cần ZH để chốt |

### Character name presence (cleaned cues)

| Name (glossary) | Hits |
|---|---:|
| Lão Đằng | 13 |
| Trần Phong | 103 |
| Tử Ưu | 13 |
| Tử U | 14 |
| Tĩnh Tĩnh | 0 |
| Tuyết Cơ | 3 |
| Diệp Chiêu | 2 |
| Minh Vương | 2 |
| Hoàng Lão | 3 |
| Phong Oánh | 1 |
| Bạch Trạch | 19 |
| Ma Chủ | 12 |
| Thần Chủ | 2 |
| Kawasaki | 0 |
| Khánh Vân | 2 |
| Cao Cường | 1 |
| lão đại | 65 |
| đại ca | 3 |
| Chị Tĩnh (partial) | 1 |

### Top name mismatches

Counts dùng **cửa sổ 3 cue** (tránh mất tên bị cắt giữa flash). `Lão Đằng` đúng ≈14; dạng sai vẫn đủ để phá nhất quán.

| Pattern | Window hits |
|---|---:|
| Lão Đằng → Lão Đường | 3 |
| Lão Đằng → Lão Đẳng | 1 |
| Tuyết Cơ → Huyết Cơ | 1 |
| Tĩnh Tĩnh → Chị Tĩnh (truncated) | 1 |
| Tĩnh Tĩnh (canonical) | **0** (thiếu hoàn toàn) |
| Kawasaki (canonical) | **0** (thiếu hoàn toàn) |
| Lão Đằng → Lão Đăng / Tằng | 0 |
| Diệp Chiêu → Diệp Tiêu / Chiều | 0 |
| Trần Phong → Trần Phòng | 0 |
| Tử Ưu → Tử Yêu / Dược | 0 |

### Pronoun inventory (cleaned cues)

| Form | Count |
|---|---:|
| ta | 226 |
| tôi | 528 |
| ngươi | 5 |
| anh | 10 |
| em | 4 |
| cậu | 548 |
| các cậu | 102 |
| các ngươi | 0 |
| nàng | 3 |
| ngài | 17 |
| hắn | 215 |
| lão tử | 21 |
| công tử | 3 |
| lão phu | 2 |
| huynh | 10 |

- bare `ta` + `tôi` in same stitched window: **3**
- `chúng ta` + `tôi` (weaker): **11**

## Concrete bad examples

### 1. `00:00:14.669` — [nonsense]
- **VI:** quái vật bình thường cấp 95 của gà Hán
- **Why bad:** ASR-of-TTS: địa danh/chủng bị nghe thành 'gà Hán' — vô nghĩa.
- **Suggested fix:** Sửa theo tên ZH đúng (vd. Hán Đế / bản đồ Hán Đế), bỏ 'gà'.

### 2. `00:00:07.190` — [calque]
- **VI:** Hán đế thần ngưu cấp 95, sinh mệnh 250
- **Why bad:** Calque/ASR tên quái+map thô, khó hiểu.
- **Suggested fix:** Localize tên mob/map nhất quán (vd. Thần Ngưu Hán Đế Lv95).

### 3. `00:00:21.390` — [calque]
- **VI:** thường phải có cả đội mới gặm được một
- **Why bad:** Calque thô từ '啃' — nghe như gặm xương, lệch game lit.
- **Suggested fix:** mới hạ / mới xử lý được một con

### 4. `02:01:35.430` — [name]
- **VI:** "Lão đường!
- **Why bad:** Sai tên vs glossary: phải là Lão Đằng (老藤).
- **Suggested fix:** Lão Đằng

### 5. `02:04:41.350` — [name]
- **VI:** Lão Đường, cậu có gặp Tử Ưu không?
- **Why bad:** Sai tên vs glossary: phải là Lão Đằng (老藤).
- **Suggested fix:** Lão Đằng

### 6. `00:18:38.230` — [name]
- **VI:** công vài trăm mét của lão đẳng.
- **Why bad:** Sai tên: Đẳng ≠ Đằng.
- **Suggested fix:** Lão Đằng

### 7. `01:01:19.710` — [name]
- **VI:** công xã Đằng Dã sát huyết cơ kết nối bao
- **Why bad:** Glossary khóa Tuyết Cơ (雪姬); 'Huyết Cơ' là lệch âm/biến thể.
- **Suggested fix:** Tuyết Cơ

### 8. `01:34:39.550` — [pronoun/address]
- **VI:** mất rồi? Nhưng mà Trần Phong đại ca khoác áo truyền Tống Thạch chẳng phải
- **Why bad:** Glossary: đồng đội gọi Trần Phong là 'lão đại', không 'đại ca'.
- **Suggested fix:** lão đại

### 9. `02:26:56.910` — [pronoun/address]
- **VI:** Ai? Nếu có con ong nhỏ của đại ca thì
- **Why bad:** Glossary: đồng đội gọi Trần Phong là 'lão đại', không 'đại ca'.
- **Suggested fix:** lão đại

### 10. `03:08:52.990` — [pronoun/address]
- **VI:** Đại ca, huynh buông tôi ra.
- **Why bad:** Glossary: đồng đội gọi Trần Phong là 'lão đại', không 'đại ca'.
- **Suggested fix:** lão đại

### 11. `00:42:43.750` — [pronoun]
- **VI:** là nàng làm hỏng. Bây giờ không phải lúc
- **Why bad:** Đại từ cổ 'nàng' lệch tone hiện đại; glossary ưu tiên cô/em.
- **Suggested fix:** cô / em (theo quan hệ)

### 12. `02:52:03.790` — [pronoun]
- **VI:** nàng nhớ cậu lắm. Được không? Vậy cậu đi
- **Why bad:** Đại từ cổ 'nàng' lệch tone hiện đại; glossary ưu tiên cô/em.
- **Suggested fix:** cô / em (theo quan hệ)

### 13. `02:59:20.190` — [pronoun]
- **VI:** nhưng ma chủ đã biết nàng vẫn còn sống,
- **Why bad:** Đại từ cổ 'nàng' lệch tone hiện đại; glossary ưu tiên cô/em.
- **Suggested fix:** cô / em (theo quan hệ)

### 14. `00:48:34.829` — [calque]
- **VI:** thánh cấp boss cấp bậc 95 sinh mệnh 10
- **Why bad:** Calque HP 'sinh mệnh' + số — cứng, Hán-Việt thô.
- **Suggested fix:** HP/máu: …

### 15. `01:29:51.430` — [calque]
- **VI:** vậy sinh mệnh 186 vạn song phòng 8 vạn
- **Why bad:** Calque HP 'sinh mệnh' + số — cứng, Hán-Việt thô.
- **Suggested fix:** HP/máu: …

### 16. `00:00:10.070` — [calque]
- **VI:** vạn, công kích vật lý ba vạn, kỹ năng
- **Why bad:** Calque stat cứng.
- **Suggested fix:** sát thương vật lý …

### 17. `00:55:48.789` — [calque]
- **VI:** khí, công kích vật lý cộng thêm hai vạn
- **Why bad:** Calque stat cứng.
- **Suggested fix:** sát thương vật lý …

### 18. `02:01:38.189` — [nonsense]
- **VI:** A, lạc đà chạy mau.
- **Why bad:** ASR artifact: 'Lão Đằng' / lệnh khác bị nghe thành 'lạc đà'.
- **Suggested fix:** Lão Đằng / ngữ cảnh đúng

### 19. `00:13:28.189` — [nonsense]
- **VI:** Cho dù thiên phú của hắn có rác rưởi đến
- **Why bad:** ASR nonsense / vỡ từ.
- **Suggested fix:** … (cần đối chiếu audio/ZH)

### 20. `00:16:20.670` — [nonsense]
- **VI:** cứ làm như vậy, đều là thợ giác rưởi sẽ phát động công thành chiến với Đằng Dã
- **Why bad:** ASR nonsense / vỡ từ.
- **Suggested fix:** … (cần đối chiếu audio/ZH)

### 21. `00:40:47.870` — [nonsense]
- **VI:** Đúng là rác rưởi. Tôi không chịu nổi nữa
- **Why bad:** ASR nonsense / vỡ từ.
- **Suggested fix:** … (cần đối chiếu audio/ZH)

### 22. `00:14:05.350` — [meaning]
- **VI:** nhưng chú ong nhỏ vừa xuất hiện xảy ra
- **Why bad:** Có thể lệch nghĩa / meme ASR; cần check ZH.
- **Suggested fix:** đối chiếu ZH

### 23. `00:00:19.870` — [calque]
- **VI:** cả boss ám kim cấp 50. Người chơi bình
- **Why bad:** Thuật ngữ grade 'ám kim' calque; người xem VI có thể không hiểu.
- **Suggested fix:** Dark Gold / Ám Kim (chú thích) / cấp đồ

### 24. `00:01:45.630` — [calque]
- **VI:** nổ trang bị ám kim rồi. Lần này toàn bộ
- **Why bad:** Thuật ngữ grade 'ám kim' calque; người xem VI có thể không hiểu.
- **Suggested fix:** Dark Gold / Ám Kim (chú thích) / cấp đồ

### 25. `01:05:07.430` — [calque]
- **VI:** giới ám kim, U Minh chiến sư cấp bậc 60.
- **Why bad:** Thuật ngữ grade 'ám kim' calque; người xem VI có thể không hiểu.
- **Suggested fix:** Dark Gold / Ám Kim (chú thích) / cấp đồ

### 26. `02:04:44.669` — [meaning]
- **VI:** Thấy rồi, yên tâm đi, bà hung ác kia
- **Why bad:** Dịch lệch/thô — có thể chỉ boss nữ nhưng wording kém.
- **Suggested fix:** đối chiếu ZH

### 27. `02:11:59.109` — [pronoun]
- **VI:** ta. Trần Phong lão đại. Tôi tin rằng
- **Why bad:** Cùng đoạn có 'ta' (không phải chúng ta) và 'tôi' — pronoun chaos.
- **Suggested fix:** Thống nhất theo glossary (thường 'tôi' với đồng đội; 'ta' chỉ vs U Minh/cổ).

### 28. `02:16:58.790` — [pronoun]
- **VI:** tôi sắp bị người ta hầm rồi. Cậu cậu cái
- **Why bad:** Cùng đoạn có 'ta' (không phải chúng ta) và 'tôi' — pronoun chaos.
- **Suggested fix:** Thống nhất theo glossary (thường 'tôi' với đồng đội; 'ta' chỉ vs U Minh/cổ).

### 29. `02:52:08.590` — [pronoun]
- **VI:** cấp quá chậm rồi, hãy rời đi là được. Ừ, ta vậy tôi đi khiêu chiến chiến thần bí
- **Why bad:** Cùng đoạn có 'ta' (không phải chúng ta) và 'tôi' — pronoun chaos.
- **Suggested fix:** Thống nhất theo glossary (thường 'tôi' với đồng đội; 'ta' chỉ vs U Minh/cổ).

### 30. `00:20:44.590` — [redundant]
- **VI:** Các vị xã trưởng cứ chờ xem. Hắc hắc,
- **Why bad:** Lặp từ / TTS stutter / phụ đề thừa.
- **Suggested fix:** Bỏ từ trùng.

### 31. `01:01:58.510` — [redundant]
- **VI:** Anh anh ơi, đây là cuộn trục gì vậy? Hóa
- **Why bad:** Lặp từ / TTS stutter / phụ đề thừa.
- **Suggested fix:** Bỏ từ trùng.

### 32. `01:08:08.109` — [redundant]
- **VI:** Được được được.
- **Why bad:** Lặp từ / TTS stutter / phụ đề thừa.
- **Suggested fix:** Bỏ từ trùng.

### 33. `01:08:14.589` — [redundant]
- **VI:** thể hạ gục. Làm muội muội Phong Oánh
- **Why bad:** Lặp từ / TTS stutter / phụ đề thừa.
- **Suggested fix:** Bỏ từ trùng.

### 34. `01:39:59.669` — [redundant]
- **VI:** Đằng gia gia sẽ cảm ơn các con thật tốt.
- **Why bad:** Lặp từ / TTS stutter / phụ đề thừa.
- **Suggested fix:** Bỏ từ trùng.

### 35. `01:44:20.830` — [redundant]
- **VI:** rồi. Được được được, tôi sẽ cùng cậu đọc
- **Why bad:** Lặp từ / TTS stutter / phụ đề thừa.
- **Suggested fix:** Bỏ từ trùng.

### 36. `00:02:14.030` — [calque]
- **VI:** thù đại hận gì với hắn. Nếu cậu lo lắng
- **Why bad:** Narration/đối thoại dùng 'hắn' dày đặc — calque Hán Việt, lệch giọng hiện đại.
- **Suggested fix:** anh ta / hắn (chỉ khi cần cổ) / tên nhân vật

### 37. `00:02:16.229` — [calque]
- **VI:** thì sao? Tôi tin rằng hắn sẽ không so
- **Why bad:** Narration/đối thoại dùng 'hắn' dày đặc — calque Hán Việt, lệch giọng hiện đại.
- **Suggested fix:** anh ta / hắn (chỉ khi cần cổ) / tên nhân vật

### 38. `00:02:19.270` — [calque]
- **VI:** đỏ. đi xin lỗi hắn đi. Hừng, nghe cậu
- **Why bad:** Narration/đối thoại dùng 'hắn' dày đặc — calque Hán Việt, lệch giọng hiện đại.
- **Suggested fix:** anh ta / hắn (chỉ khi cần cổ) / tên nhân vật

## Method

1. Parse YouTube word-level VTT; strip `<c>` / embedded timestamps.
2. Keep **flash** cues (duration ≤ 20ms) as completed-line units; drop consecutive duplicate text → `cues_clean.jsonl`.
3. Stitch adjacent flashes into sentence-ish windows → `cues_stitched.jsonl` (audit readability only).
4. Systematic sample: start / 25% / 50% / 75% / end + random pockets (≥120 unique cleaned cues).
5. Regex taxonomy vs series glossary character list + pronoun table.

## Outputs

- `cues_clean.jsonl`
- `cues_stitched.jsonl`
- `sample_cues.jsonl`
- `summary.json`
- `AUDIT.md` (this file)
