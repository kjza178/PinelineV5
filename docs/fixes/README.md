# Fix logs

Mỗi lần sửa bug ghi một file trong thư mục này (rule: `.cursor/rules/fix-log-markdown.mdc`).

Dùng để **recheck** sau này: đọc `Root cause` + chạy lại mục `Recheck`.

Bug sửa sau 2026-09-26 (chưa có file riêng) được ghi trong `docs/CHANGELOG.md` + `docs/worklog/`.

| Date | File | Triệu chứng |
|------|------|-------------|
| 2026-11-06 | [v5-enospc-port.md](./2026-11-06-v5-enospc-port.md) | V5 split thiếu ENOSPC guard / re-encode khi hết ổ; PORT/uploader default lệch |
| 2026-11-06 | [pronoun-qa-413-slim.md](./2026-11-06-pronoun-qa-413-slim.md) | Pronoun-QA GPT vá đỏ Aurora 413 (full plan block) |
| 2026-11-06 | [hongguo2-review.md](./2026-11-06-hongguo2-review.md) | Hongguo2 CTA submit nhầm + selectedIds lẫn detail / hint |
| 2026-11-06 | [hg-new-seasons.md](./2026-11-06-hg-new-seasons.md) | `/hongguo` thiếu board Mùa mới (Gợi ý / Sắp ra / Update all) |
| 2026-11-06 | [merge-no-dup-output.md](./2026-11-06-merge-no-dup-output.md) | Merge split tạo output + output_full nhân đôi dung lượng |
| 2026-11-05 | [split-voice-queue-opts.md](./2026-11-05-split-voice-queue-opts.md) | Part sau split dùng sai giọng (NgayCuoi thay vì queue_opts) |
| 2026-11-05 | [autosplit-conflict-guards.md](./2026-11-05-autosplit-conflict-guards.md) | Auto-split pass 2 → parent 80% + TTS lại sau mux |
| 2026-11-05 | [ui3-404-stages.md](./2026-11-05-ui3-404-stages.md) | UI3 404/stages — sync guards V5 → V2/V4 |
| 2026-11-05 | [upload-limit-stop-queue.md](./2026-11-05-upload-limit-stop-queue.md) | YT `uploadLimitExceeded` vẫn drain queue → fail hàng loạt |
| 2026-11-04 | [http-routes-thumb-root.md](./2026-11-04-http-routes-thumb-root.md) | `/meta/thumbnail` resolve nhầm `http_routes/data/` sau Phase B |
| 2026-11-04 | [v5-queue-ssot.md](./2026-11-04-v5-queue-ssot.md) | V5 dual-route queue/jobs + queue_state double enrich |
| 2026-11-04 | [film-db-queue-meta.md](./2026-11-04-film-db-queue-meta.md) | Queue poll đọc N× manifest — chuyển metadata sang films.db (V5) |
| 2026-11-04 | [queue-sort-move.md](./2026-11-04-queue-sort-move.md) | Sort/move hàng chờ không đổi thứ tự thật (UI fallback + group_index) |
| 2026-11-02 | [pronoun-consistency-abc.md](./2026-11-02-pronoun-consistency-abc.md) | Analyze+lock+ledger+QA xưng hô (V2/V4/V5) |
| 2026-11-02 | [pronoun-xung-ho.md](./2026-11-02-pronoun-xung-ho.md) | Dịch lệch xưng hô — post-pass + agent pass (sync V4) |
| 2026-11-02 | [longfilm-sub-drift-split.md](./2026-11-02-longfilm-sub-drift-split.md) | Phim ~12h lệch khung sub tích lũy (AAC priming + pipeline dài); port `split_parts` |
| 2026-11-02 | [library-action-missing-api.md](./2026-11-02-library-action-missing-api.md) | `/library/action` gọi `film_db.mark_library_*` / `enqueue_library_item` không tồn tại → 500 |
| 2026-10-09 | [films-ui-delete-missing.md](./2026-10-09-films-ui-delete-missing.md) | `films/ui`: nhiều job đã xoá thư mục vẫn tồn đọng, thiếu bộ lọc thư mục và thiếu chức năng xoá film |
| 2026-10-06 | [batch7-ui-split.md](./2026-10-06-batch7-ui-split.md) | Đợt 7: gỡ UI cũ `index1/2.html`; `server.py` 6221 dòng → tách `routes_ui/hg/agent.py` (OpenAPI giống hệt) |
| 2026-10-08 | [queue-worker-disk-full.md](./2026-10-08-queue-worker-disk-full.md) | Ổ D: đầy → `_save()` OSError giết thread hàng đợi, job chờ đứng im (chưa sửa code, mới xử lý tay) |
| 2026-10-07 | [hg-merge-queue.md](./2026-10-07-hg-merge-queue.md) | Hongguo Merge all: hàng đợi chỉ trong RAM bị agent restart xoá, bấm xếp hàng bị treo vì chuẩn hoá đồng bộ, UI không hiện bước/tiến độ |
| 2026-10-07 | [source-duplicate-copy.md](./2026-10-07-source-duplicate-copy.md) | Video nguồn chép 2 bản (thư viện + job): `/source-path` luôn copy, import rơi về copy không log → 0281/dccc thừa ~36,7 GiB |
| 2026-10-07 | [sfxlib-sidechain-short.md](./2026-10-07-sfxlib-sidechain-short.md) | `sfx_lib` pass 1 có lúc hụt đuôi (~30% lần, `sidechaincompress` kết thúc sớm khi dub ngắn hơn phim) |
| 2026-10-07 | [m20-voice-bgm-apad.md](./2026-10-07-m20-voice-bgm-apad.md) | `voice_bgm` thiếu `apad` → nhạc thư viện + audio dừng ở câu thoại cuối, cuối video im lặng |
| 2026-10-06 | [restart-killed-itself.md](./2026-10-06-restart-killed-itself.md) | Restart kill server cũ xong thì văng `NoSuchProcess` trên `cmd.exe` bọc server đã tự thoát (lặp lại 07/10; giả thuyết PID tái dùng ban đầu không phải nguyên nhân chính) → server :8801 nằm chết, 3a2e chưa xếp lại |
| 2026-10-06 | [batch6-maintenance.md](./2026-10-06-batch6-maintenance.md) | Đợt 6 review: không có git/pytest.ini, test hardsub kỳ vọng sai, filter che hardsub vượt giới hạn ffmpeg khi nhiều đoạn (M3), script chết ở gốc (có cái ghi vào V1) |
| 2026-10-06 | [batch5-agent-safety.md](./2026-10-06-batch5-agent-safety.md) | Đợt 5 review: chữ trơn Telegram đổi trạng thái / tự bật Auto-pilot, agent chạy thẳng tool phá huỷ, `hg_auto_flow` bốc nhầm bộ theo chuỗi con và treo request 90 phút, `/stop` phải chờ agent, kết quả tool tràn context |
| 2026-10-06 | [batch4-write-races.md](./2026-10-06-batch4-write-races.md) | Đợt 4 review: manifest ghi đè cờ HOLD, bấm tay chạy song song với hàng đợi, 2 bản server/sidecar, Auto-pilot lặp job lỗi, audio/TTS/bản trộn cũ bị dùng lại, checkpoint ghi dở |
| 2026-10-06 | [batch3-single-source.md](./2026-10-06-batch3-single-source.md) | Đợt 3 review: cùng job render khác nhau theo đường gọi, sửa config không ăn tới restart, batch_config/autopilot state ghi dở → Auto-pilot dùng mặc định sai |
| 2026-10-06 | [batch2-security.md](./2026-10-06-batch2-security.md) | Đợt 2 review: web lạ gọi API/sidecar, SSRF Hongguo, path traversal tên bộ, XSS onclick, key trong code/backup, LLM sập để trống câu, model đóng băng tới restart |
| 2026-10-06 | [batch1-data-loss.md](./2026-10-06-batch1-data-loss.md) | Đợt 1 review: heal đánh done sai, Stop không kill ffmpeg, mất opts/watermark, dọn tập Hongguo xoá nhầm, agent chọn nhầm phim, dời mốc tiếng 2 lần, cắt câu runaway sai |
| 2026-10-06 | [agent-text-toolcall-overmatch.md](./2026-10-06-agent-text-toolcall-overmatch.md) | Agent chạy tool chỉ vì được nhắc trong câu trả lời (parser `tool(...)`) |
| 2026-09-26 | [ui4-ops.md](./2026-09-26-ui4-ops.md) | UI4 Ops |
| 2026-09-26 | [p0-job-management.md](./2026-09-26-p0-job-management.md) | Opts theo job, chạy series, dashboard queue, GPU gate |
| 2026-09-26 | [duck-bgm-twopass-port.md](./2026-09-26-duck-bgm-twopass-port.md) | Port duck/duck_bgm two-pass sang V2 |
| 2026-09-25 | [duck-bgm-audio-truncated.md](./2026-09-25-duck-bgm-audio-truncated.md) | duck_bgm cắt cụt audio |
| 2026-09-24 | [queue-voice-stop-race.md](./2026-09-24-queue-voice-stop-race.md) | Queue: race voice/stop |
| 2026-09-24 | [stop-mux-ffmpeg.md](./2026-09-24-stop-mux-ffmpeg.md) | Dừng không kill được ffmpeg mux |
| 2026-09-24 | [hardsub-hwaccel-drawbox.md](./2026-09-24-hardsub-hwaccel-drawbox.md) | **Tối ưu:** bỏ hwaccel+drawbox (hết xanh, nhanh) |
| 2026-09-24 | [hardsub-green-bar.md](./2026-09-24-hardsub-green-bar.md) | Bar xanh / lệch (desat - superseded) |
| 2026-09-24 | [run-all-stale-mux.md](./2026-09-24-run-all-stale-mux.md) | 1-click lỗi liên tục / 409 mux running |
