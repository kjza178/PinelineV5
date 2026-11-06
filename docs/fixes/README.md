# Fix logs

Mỗi lần sửa bug ghi một file trong thư mục này (rule: `.cursor/rules/fix-log-markdown.mdc`).

Dùng để **recheck** sau này: đọc `Root cause` + chạy lại mục `Recheck`.

Bug sửa sau 2026-09-26 (chưa có file riêng) được ghi trong `docs/CHANGELOG.md` + `docs/worklog/`.

| Date | File | Triệu chứng |
|------|------|-------------|
| 2026-11-07 | [uploader-skip-ux.md](./2026-11-07-uploader-skip-ux.md) | Skip đang upload khó tìm (chỉ tab Uploader); thiếu cảnh báo file >11.5h |
| 2026-11-07 | [combine-part-order.md](./2026-11-07-combine-part-order.md) | Gộp job đã làm nối theo tick (Phần 4→2→3) |
| 2026-11-07 | [hardsub-blur-toggle.md](./2026-11-07-hardsub-blur-toggle.md) | Thiếu bật/tắt che hardsub (blur) trên UI/mux |
| 2026-11-07 | [films-combine-ui.md](./2026-11-07-films-combine-ui.md) | Films UI thiếu nút gộp ≥2 job đã làm |
| 2026-11-07 | [uploader-settings-8802.md](./2026-11-07-uploader-settings-8802.md) | Settings/Uploader 404 trên :8802; thiếu skip upload |
| 2026-11-07 | [films-ui-syntax.md](./2026-11-07-films-ui-syntax.md) | Films UI còn onclick `'${…}'` / `'${esc(…)}'` (SyntaxError title/id) |
| 2026-11-07 | [films-ui-syntax.md](./2026-11-07-films-ui-syntax.md) | Films UI :8802 — `jq` cắt onclick + autopub/settings |
| 2026-11-06 | [translate-force-wipe.md](./2026-11-06-translate-force-wipe.md) | Dịch xong / TTS → lại «force: dịch lại từ đầu» (wipe script) |
| 2026-11-06 | [translate-stop-ghost.md](./2026-11-06-translate-stop-ghost.md) | Phần 6 translate force → trống VI / `.stop` ghost |
| 2026-11-06 | [hongguo2-seasons-layout.md](./2026-11-06-hongguo2-seasons-layout.md) | Hongguo2 Mùa mới clip + Update 0/? + Ops chèn Discover |
| 2026-11-06 | [pronoun-qa-413-slim.md](./2026-11-06-pronoun-qa-413-slim.md) | Pronoun-QA GPT vá đỏ Aurora 413 (full plan block) |
| 2026-11-06 | [hongguo2-review.md](./2026-11-06-hongguo2-review.md) | Hongguo2 CTA submit nhầm + selectedIds lẫn detail / hint |
| 2026-11-06 | [hg-new-seasons.md](./2026-11-06-hg-new-seasons.md) | `/hongguo` thiếu board Mùa mới (Gợi ý / Sắp ra / Update all) |
| 2026-11-06 | [merge-no-dup-output.md](./2026-11-06-merge-no-dup-output.md) | Merge split tạo output + output_full nhân đôi dung lượng |
| 2026-11-05 | [split-voice-queue-opts.md](./2026-11-05-split-voice-queue-opts.md) | Part sau split TTS sai giọng (NgayCuoi ≠ v1 config) |
| 2026-11-05 | [autosplit-conflict-guards.md](./2026-11-05-autosplit-conflict-guards.md) | Auto-split pass 2 → parent 80% + TTS lại sau mux |
| 2026-11-05 | [split-enospc-guard.md](./2026-11-05-split-enospc-guard.md) | Split hết ổ → re-encode phình GB + orphan `_split_parts` |
| 2026-11-05 | [ui3-404-stages.md](./2026-11-05-ui3-404-stages.md) | UI3 TypeError khi job detail 404 / thiếu `stages` |
| 2026-11-05 | [upload-limit-stop-queue.md](./2026-11-05-upload-limit-stop-queue.md) | YT `uploadLimitExceeded` vẫn drain queue → fail hàng loạt |
| 2026-11-04 | [queue-sort-move.md](./2026-11-04-queue-sort-move.md) | Sort/move hàng chờ không đổi thứ tự thật (UI fallback + group_index) |
| 2026-11-04 | [hardsub-partial-cover.md](./2026-11-04-hardsub-partial-cover.md) | Hardsub che hở 2 mép (OCR hẹp) |
| 2026-11-03 | [split-parent-false-failed.md](./2026-11-03-split-parent-false-failed.md) | Parent sau split báo failed dù Full/part đã xong |
| 2026-11-02 | [pronoun-consistency-abc.md](./2026-11-02-pronoun-consistency-abc.md) | Analyze+lock+ledger+QA xưng hô (V2/V4/V5) |
| 2026-11-02 | [pronoun-aurora-port.md](./2026-11-02-pronoun-aurora-port.md) | Port post-pass xưng hô + Aurora name/pronoun + cloud route từ V4 → V2 |
| 2026-11-02 | [autosplit-asr-set-stage.md](./2026-11-02-autosplit-asr-set-stage.md) | Phim dài auto-split: ASR parent crash `Manifest.set_stage` → part không ASR/translate |
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
