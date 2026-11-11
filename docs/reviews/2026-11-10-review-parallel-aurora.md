# Bench: REVIEW GPT song song qua Aurora (script dài)

- **Date:** 2026-11-10
- **Job:** `05670cbf7c1c` (`script.json` 3900 cue)
- **Harness:** `D:\PinelineV2_tmp\review_parallel_bench.py`
- **Upstream:** Aurora `192.168.31.247:5005` + `192.168.31.244:5005` (`gpt-5-6-mini`)
- **Note:** `:3377` timeout lúc bench — không dùng

## Setup

- Workload: **8 part × 100 cue**, `offset=3100` (cùng slice cho parallel & sequential)
- Prompt: review tối thiểu JSON `{fixes:{i:vi}}` + `style_lock.json`
- Parallel workers=8; sequential workers=1
- Agents: probe / parallel / sequential (Cursor subagents)

## Kết quả

| Mode | wall_s | sum_part_s | speedup vs sum | ok/fail | parse_ok | fixes |
|---|---:|---:|---:|---|---:|---:|
| probe (12 tiny) | 15.18 | — | — | 12/0 | — | — |
| **parallel 8×100** | **122.55** | 804.33 | **6.56×** | 8/0 | 8 | 186 |
| **sequential 8×100** | **837.59** | 837.59 | 1.0× | 8/0 | 8 | 178 |

**Speedup thực parallel vs sequential:** `837.59 / 122.55 ≈ 6.8×`  
(ước lượng ideal max-part ≈ 130s → ~6.4× — khớp thực nghiệm).

- HTTP: toàn **200**, **0× 429/5xx** trên workload này.
- `X-Aurora-Account-Id` trống trên `/chat/completions` (Aurora chỉ set header này lúc **upload file**) → không suy ra “1 account” từ header.

## Raw outs

- `D:\PinelineV2_tmp\review_parallel_probe.json`
- `D:\PinelineV2_tmp\review_parallel_parallel.json`
- `D:\PinelineV2_tmp\review_parallel_sequential.json`

## Verdict

**Có — fan-out REVIEW qua Aurora thực tế được** cho ~800 cue (~2 phút wall vs ~14 phút tuần tự).

Để đưa vào production `translate.run_review`:

1. `REVIEW_PARALLEL` + `REVIEW_BATCH` + overlap biên (±cue)
2. Prefer text chat (không phụ thuộc `file_id` sticky)
3. Semaphore + retry 429; dual base `.247`/`.244` (hoặc pool local khi `:3377` sống)
4. Merge fixes theo `i`; giữ Pass1 / style_lock chung mọi part

## Không làm trong bench

- Chưa sửa `translate.py` / config production
- Chưa đánh giá chất lượng fixes (chỉ đếm + parse JSON)

## Follow-up — FULL file (chi tiết thật)

- Harness: `D:\PinelineV2_tmp\review_parallel_full.py`
- Job `05670cbf7c1c` **3900 cue** → 26×150, workers=10, wall **369s**, parts **26/26 OK**, **710** câu đổi thật
- Output (không ghi đè `script.json` production):
  - `D:\PinelineV2_tmp\review_full_05670\01_before.vi.srt`
  - `D:\PinelineV2_tmp\review_full_05670\02_after.vi.srt`
  - `D:\PinelineV2_tmp\review_full_05670\CHANGES.md` — đủ 710 cue: ZH / VI trước / VI sau
  - `changes.json`, `script.after_parallel.json`

## Follow-up — nhúng pronoun lock + re-test

User bắt lệch xưng hô (`tôi`/`ta` vs `cậu` với Môn chủ). Harness mới: `review_parallel_locked.py` nhúng `glossary.json` pronouns + `lock_banner` / `review_lock_rules` + rule cấm tôi↔ta + filter client.

| Run | wall | changes | note |
|---|---:|---:|---|
| unlocked full (trước) | 369s | 710 | cue **5** bị `tôi→ta` |
| locked head 0–449 | 115s | 62 | cue **5 giữ tôi**; 6–8 không đổi |
| locked mid 1800–2249 | 116s | 56 | giữ ngôi; 7 diff add/drop nghĩa |

Compare scope 0–449: pronoun flips **18 → 11**; cue 5 unlocked đổi / locked không. Out: `review_locked_head/`, `review_locked_mid/`, `COMPARE_pronoun.md`.

**Verdict:** lock hữu ích để **không phá ngôi** khi parallel. Lệch «lão già Môn chủ» + «cậu» vẫn là lỗi **VI gốc** — cần pass sửa xưng hô có chủ đích, không chỉ lock.

## Follow-up — ABC test (200 cue đầu)

Harness: `D:\PinelineV2_tmp\pronoun_abc_test.py` → `pronoun_abc/mode{1,2,3}_*`

| Method | Cue 5 `tôi` | Cue 7–8 `cậu` vs Môn chủ | Ghi chú |
|---|---|---|---|
| #1 mask/unmask REVIEW | giữ + được polish nghĩa | **không sửa** | 0 pronoun flip; chỉ đóng băng |
| #2 speaker + mech | giữ | **`cậu→ông`** | Speaker GPT = Unknown; rule mech cứu |
| #3 pronoun-QA siết | giữ | **`cậu→ngươi`** | 10 issues / 9 fixed |

**Khuyến nghị (test tmp):** `#1` + `#3` — chưa wire production (user chỉ test).

## Follow-up — mix #1+#3 trên sub thật (tmp)

- Harness: `D:\PinelineV2_tmp\pronoun_mix_13_test.py`
- Out: `D:\PinelineV2_tmp\pronoun_mix_13\` (`02_final.vi.srt`, `CHANGES.md`, `AUDIT.md`)
- 400 cue `05670`: step1 108s/67 · step3 30s/12 · tổng 79 đổi
- Cue5 giữ **tôi** (unlocked từng `tôi→ta`); 7 **cậu→ông**; 8 **cậu→ngươi**
- Audit: **partial** — còn ông/ngươi liền nhau + «các cậu» sót
