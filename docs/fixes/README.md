# Fix logs





M?i l?n s?a bug ghi m?t file trong th? m?c n?y (rule: `.cursor/rules/fix-log-markdown.mdc`).





D?ng ?? **recheck** sau n?y: ??c `Root cause` + ch?y l?i m?c `Recheck`.





Bug s?a sau 2026-09-26 (ch?a c? file ri?ng) ???c ghi trong `docs/CHANGELOG.md` + `docs/worklog/`.





| Date | File | Triệu chứng |
| 2026-11-20 | [2026-11-20-cjk-backup-repair.md](./2026-11-20-cjk-backup-repair.md) | Park «còn 1 câu chữ Hán» — Aurora không vá CJK đã rv |
| 2026-11-20 | [2026-11-20-agent-resolve-short-job-id.md](./2026-11-20-agent-resolve-short-job-id.md) | Agent `/qa` báo thiếu script vì id `9aa089_p01` |
| 2026-11-20 | [2026-11-20-publish-ask-telegram.md](./2026-11-20-publish-ask-telegram.md) | Auto-publish hỏi Telegram trước khi upload |
| 2026-11-20 | [2026-11-20-thumb-prompt-simple.md](./2026-11-20-thumb-prompt-simple.md) | Prompt thumb AI quá dài / khóa 3D → lệch typo ảnh gốc |
| 2026-11-20 | [2026-11-20-ops-log-no-auto-show.md](./2026-11-20-ops-log-no-auto-show.md) | Nhật ký Films UI tự hiện lại sau khi bấm ✕ |
| 2026-11-20 | [2026-11-20-queue-stop-gpu-wait.md](./2026-11-20-queue-stop-gpu-wait.md) | Queue Stop treo ghế khi job xếp sau TTS trên `_gpu` |
| 2026-11-19 | [2026-11-19-meta-typo-free-form.md](./2026-11-19-meta-typo-free-form.md) | Meta form: typo gắn cứng tên phim / lửa vàng |
| 2026-11-19 | [2026-11-19-films-delete-orphan-work.md](./2026-11-19-films-delete-orphan-work.md) | Xoá job/part: DB mất nhưng work/ còn vài GB |
| 2026-11-19 | [2026-11-19-films-combine-progress-log.md](./2026-11-19-films-combine-progress-log.md) | Gộp job Films UI không có log/tiến độ giữa chừng |
| 2026-11-18 | [2026-11-18-thumb-poster-only-title-hooks.md](./2026-11-18-thumb-poster-only-title-hooks.md) | Thumb: poster-only + hook neo title (c7367 frame/hook lệch) |
| 2026-11-18 | [2026-11-18-thumb-ai-edits-no-pillow.md](./2026-11-18-thumb-ai-edits-no-pillow.md) | Thumb = ảnh gốc + /images/edits; bỏ Pillow; không generations khi có ref |
| 2026-11-18 | [2026-11-18-thumb-poster-faithful-fallback.md](./2026-11-18-thumb-poster-faithful-fallback.md) | (thu hồi) Pillow fallback — thay bằng thumb-ai-edits-no-pillow |
| 2026-11-18 | [2026-11-18-autopub-ref-typo.md](./2026-11-18-autopub-ref-typo.md) | Auto-publish thumb = ref ảnh gốc + typo title (không echo poster) |
| 2026-11-18 | [2026-11-18-meta-thumb-upload-ref.md](./2026-11-18-meta-thumb-upload-ref.md) | Meta thumb + Up ảnh gốc; /films HTML đè JSON trên :8801 |
| 2026-11-16 | [aurora-meta-timeout-roll-3377.md](./2026-11-16-aurora-meta-timeout-roll-3377.md) | Khắc phục lỗi abort kết nối Aurora (/images/edits wsasend abort) & Bỏ backup 192 (retry trên 3377 roll acc) |
| 2026-11-16 | [dynamic-concurrency-and-batch.md](./2026-11-16-dynamic-concurrency-and-batch.md) | Tự chọn cỡ lô dịch theo mức song song (DEEPSEEK_CONCURRENCY) & Khóa DeepSeek-Flash (bỏ NMT) |
| 2026-11-16 | [fix-pair-fill-json-escape.md](./2026-11-16-fix-pair-fill-json-escape.md) | Sửa lỗi JSON decode trong pair_fill (thẻ </escape> & schema "pairs") |
| 2026-11-15 | [simple-a7-a8-full-plan-overlap.md](./2026-11-15-simple-a7-a8-full-plan-overlap.md) | A7 Plan đọc cả phim bằng LLM context lớn & A8 Soát trượt có chồng lấn (Sliding Window Overlap) |
| 2026-11-15 | [aurora-retry-alibaba-ai-image.md](./2026-11-15-aurora-retry-alibaba-ai-image.md) | Retry Aurora account pool 400, fallback ngay khi :3377 đóng, thêm Alibaba DashScope & sửa sinh ảnh Aurora |
| 2026-11-14 | [simple-r1-bugs.md](./2026-11-14-simple-r1-bugs.md) | G1.1 simple R1.1–R1.5 (soát/plan/code/TZ/KIN) |
| 2026-11-14 | [seat-lock-translate-fill.md](./2026-11-14-seat-lock-translate-fill.md) | Ghost cam: Brain fill ngoài ghế queue |
| 2026-11-14 | [nmt-ct2-cuda13.md](./2026-11-14-nmt-ct2-cuda13.md) | NMT CT2 treo sau torch cu130 — ctranslate2-reborn CUDA 13 |


|------|------|-------------|


| 2026-11-13 | [lib-merge-local-fallback.md](./2026-11-13-lib-merge-local-fallback.md) | Lib đĩa không hiện / Hongguo «need ≥2» |
| 2026-11-13 | [meta-ai-image-8801.md](./2026-11-13-meta-ai-image-8801.md) | Meta thumb GPT 404 khi Films UI mở :8801 |
| 2026-11-11 | [optimize-b5-b6-b8-b10.md](./2026-11-11-optimize-b5-b6-b8-b10.md) | Dừng REVIEW chậm · audio mux lệch · restart treo · ghi plan |
| 2026-11-11 | [review-fail-park-port.md](./2026-11-11-review-fail-park-port.md) | REVIEW lỗi coi là đã soát · park treo hàng đợi |
| 2026-11-11 | [pass1-upload-size.md](./2026-11-11-pass1-upload-size.md) | Pass1 413 — chặn upload theo số cue |
| 2026-11-11 | [studio-1job-pipeline.md](./2026-11-11-studio-1job-pipeline.md) | SOP 1job ASR→NMT→Aurora∥→TTS→mux |
| 2026-11-10 | [queue-park-held.md](./2026-11-10-queue-park-held.md) | HOLD/soát dở → nhảy job kế (mất 1→output) |
| 2026-11-10 | [review-voice-loosen.md](./2026-11-10-review-voice-loosen.md) | Nới REVIEW Aurora — văn phong khi vá |
| 2026-11-10 | [review-gpt6-aurora.md](./2026-11-10-review-gpt6-aurora.md) | UI Aurora không rà — chuyển gpt-6 |
| 2026-11-10 | [brain-hang-llm-fix.md](./2026-11-10-brain-hang-llm-fix.md) | HOLD high hang — LLM trace/plan rồi mới mở |
| 2026-11-10 | [05670-script-wipe.md](./2026-11-10-05670-script-wipe.md) | 05670 máº¥t script.json sau restart/TTS |


| 2026-11-09 | [brain-llm-tool-loop.md](./2026-11-09-brain-llm-tool-loop.md) | Brain LLM tick tools=[] â khÃ´ng gá»i tool |


| 2026-11-09 | [bat-py-quote.md](./2026-11-09-bat-py-quote.md) | bat `python.exe" set "PY` not recognized |


| 2026-11-09 | [tc-quota-false-positive.md](./2026-11-09-tc-quota-false-positive.md) | Test Block bÃ¡o háº¿t quota dÃ¹ GCP cÃ²n |


| 2026-11-09 | [review-keep-nmt.md](./2026-11-09-review-keep-nmt.md) | GPT polish thá»«a (LÃ£o tá»­â¦) â giá»¯ NMT |


| 2026-11-09 | [mt-draft-slim-gloss.md](./2026-11-09-mt-draft-slim-gloss.md) | NMT draft + glossary gáº§y + REVIEW GPT mini |


| 2026-11-09 | [hv-auditor.md](./2026-11-09-hv-auditor.md) | Gate/GPT khÃ³a sai Ã¢m HV â auditor Unihan+trap |


| 2026-11-08 | [nghich-thien-ni-hanh.md](./2026-11-08-nghich-thien-ni-hanh.md) | éå¤©èè¡ â Nghá» (sai); ÄÃºng Nghá»ch |


| 2026-11-08 | [split-parent-merge-heal.md](./2026-11-08-split-parent-merge-heal.md) | Part 1/2+2/2 xong â job gá»c váº«n pending |


| 2026-11-08 | [hongguo1-full-split.md](./2026-11-08-hongguo1-full-split.md) | Restore classic + /api/hg vs /api/hg2 |


| 2026-11-08 | [merge-frag-naming.md](./2026-11-08-merge-frag-naming.md) | Merge: need â¥2 eps + NVENC -22 ç¬¬013é |


| 2026-11-08 | [hongguo1-restore-isolate.md](./2026-11-08-hongguo1-restore-isolate.md) | Restore /hongguo + tÃ¡ch backend hg2 |


| 2026-11-08 | [hongguo1-boot-stuck.md](./2026-11-08-hongguo1-boot-stuck.md) | /hongguo káº¹t Äang táº£i báº£ng hot |


| 2026-11-08 | [hongguo2-dl-stop.md](./2026-11-08-hongguo2-dl-stop.md) | Downloads thiáº¿u Stop â Ã 502 under way |


| 2026-11-08 | [hongguo2-qualities-disk.md](./2026-11-08-hongguo2-qualities-disk.md) | qualities 502 + /api/disk 404 |


| 2026-11-08 | [hongguo2-play-button.md](./2026-11-08-hongguo2-play-button.md) | Detail thiáº¿u nÃºt Play (WinUI) |


| 2026-11-08 | [hongguo2-browse-scroll.md](./2026-11-08-hongguo2-browse-scroll.md) | Browse chá» 1 trang â thiáº¿u load-on-scroll |


| 2026-11-08 | [hongguo2-dropdown-winui.md](./2026-11-08-hongguo2-dropdown-winui.md) | Dropdown Browse chá»¯ má» + filter khÃ´ng Äá»i grid |


| 2026-11-08 | [python315-path-default.md](./2026-11-08-python315-path-default.md) | python â 3.15 thiáº¿u fastapi/requests sau update |


| 2026-11-08 | [hongguo2-intro-dropdown.md](./2026-11-08-hongguo2-intro-dropdown.md) | Detail intro chua VI + dropdown filter chu trang |


| 2026-11-08 | [hongguo2-browse-pagesize.md](./2026-11-08-hongguo2-browse-pagesize.md) | Browse hongguo2 chi hien ~20 phim |


| 2026-11-08 | [translate-partial-tts-jump.md](./2026-11-08-translate-partial-tts-jump.md) | Dich dung giua chung â nhay TTS voi so cau do |


| 2026-11-08 | [hongguo2-title-vi.md](./2026-11-08-hongguo2-title-vi.md) | Hongguo2 thieu dong dich TV duoi tieu de |


| 2026-11-08 | [hongguo2-library-winui.md](./2026-11-08-hongguo2-library-winui.md) | Library lech WinUI (thieu chip/Update info/hover) |


| 2026-11-08 | [hongguo2-settings-winui.md](./2026-11-08-hongguo2-settings-winui.md) | Settings lech WinUI + toast Can license |


| 2026-11-08 | [helper-singleton-winui-parity.md](./2026-11-08-helper-singleton-winui-parity.md) | Leak MainKt + spawn/hongguo2 lech WinUI (giu spawn rieng) |


| 2026-11-08 | [hongguo2-downloads-winui.md](./2026-11-08-hongguo2-downloads-winui.md) | Downloads lech WinUI (thieu tab/Open folder/poster) |


| 2026-11-08 | [hongguo2-rank-new.md](./2026-11-08-hongguo2-rank-new.md) | Ranking/New lech WinUI (tab gia, New bo qua days) |


| 2026-11-08 | [hongguo2-browse-facets.md](./2026-11-08-hongguo2-browse-facets.md) | Browse filter lech WinUI (3 dropdown thay vi 7 facet) |


| 2026-11-08 | [skip-split-part-upload.md](./2026-11-08-skip-split-part-upload.md) | Part auto-split ?Ph?n N/N? b? ??a v?o upload YouTube |


| 2026-11-07 | [mux-heal-hardsub-ocr.md](./2026-11-07-mux-heal-hardsub-ocr.md) | Part mux hi?n S?n s?ng khi ?ang OCR hardsub (~25 ph?t) |


| 2026-11-07 | [concat-partial-norm.md](./2026-11-07-concat-partial-norm.md) | G?p encode c? lo?t d? ch? 1 ph?n l?ch resolution |


| 2026-11-07 | [test-channel-exhausted-mask.md](./2026-11-07-test-channel-exhausted-mask.md) | Reset Quota v?n b?o token K?nh 3 ch?t (c? 1+2 che) |


| 2026-11-07 | [test-channel-doi-kenh.md](./2026-11-07-test-channel-doi-kenh.md) | ??i k?nh Test b?o OK nhung project kh?ng d?i


| 2026-11-07 | [uploader-skip-ux.md](./2026-11-07-uploader-skip-ux.md) | Skip ?ang upload kh? t?m (ch? tab Uploader); thi?u c?nh b?o file >11.5h |


| 2026-11-07 | [combine-part-order.md](./2026-11-07-combine-part-order.md) | G?p job ?? l?m n?i theo tick (Ph?n 4?2?3) |


| 2026-11-07 | [hardsub-blur-toggle.md](./2026-11-07-hardsub-blur-toggle.md) | Thi?u b?t/t?t che hardsub (blur) tr?n UI/mux |


| 2026-11-07 | [films-combine-ui.md](./2026-11-07-films-combine-ui.md) | Films UI thi?u n?t g?p ?2 job ?? l?m |


| 2026-11-07 | [uploader-settings-8802.md](./2026-11-07-uploader-settings-8802.md) | Settings/Uploader 404 tr?n :8802; thi?u skip upload |


| 2026-11-07 | [films-ui-syntax.md](./2026-11-07-films-ui-syntax.md) | Films UI c?n onclick `'${?}'` / `'${esc(?)}'` (SyntaxError title/id) |


| 2026-11-07 | [films-ui-syntax.md](./2026-11-07-films-ui-syntax.md) | Films UI :8802 ? `jq` c?t onclick + autopub/settings |


| 2026-11-06 | [translate-force-wipe.md](./2026-11-06-translate-force-wipe.md) | D?ch xong / TTS ? l?i ?force: d?ch l?i t? ??u? (wipe script) |


| 2026-11-06 | [translate-stop-ghost.md](./2026-11-06-translate-stop-ghost.md) | Ph?n 6 translate force ? tr?ng VI / `.stop` ghost |


| 2026-11-06 | [hongguo2-seasons-layout.md](./2026-11-06-hongguo2-seasons-layout.md) | Hongguo2 M?a m?i clip + Update 0/? + Ops ch?n Discover |


| 2026-11-06 | [pronoun-qa-413-slim.md](./2026-11-06-pronoun-qa-413-slim.md) | Pronoun-QA GPT v? ?? Aurora 413 (full plan block) |


| 2026-11-06 | [hongguo2-review.md](./2026-11-06-hongguo2-review.md) | Hongguo2 CTA submit nh?m + selectedIds l?n detail / hint |


| 2026-11-06 | [hg-new-seasons.md](./2026-11-06-hg-new-seasons.md) | `/hongguo` thi?u board M?a m?i (G?i ? / S?p ra / Update all) |


| 2026-11-06 | [merge-no-dup-output.md](./2026-11-06-merge-no-dup-output.md) | Merge split t?o output + output_full nh?n ??i dung l??ng |


| 2026-11-05 | [split-voice-queue-opts.md](./2026-11-05-split-voice-queue-opts.md) | Part sau split TTS sai gi?ng (NgayCuoi ? v1 config) |


| 2026-11-05 | [autosplit-conflict-guards.md](./2026-11-05-autosplit-conflict-guards.md) | Auto-split pass 2 ? parent 80% + TTS l?i sau mux |


| 2026-11-05 | [split-enospc-guard.md](./2026-11-05-split-enospc-guard.md) | Split h?t ? ? re-encode ph?nh GB + orphan `_split_parts` |


| 2026-11-05 | [ui3-404-stages.md](./2026-11-05-ui3-404-stages.md) | UI3 TypeError khi job detail 404 / thi?u `stages` |


| 2026-11-05 | [upload-limit-stop-queue.md](./2026-11-05-upload-limit-stop-queue.md) | YT `uploadLimitExceeded` v?n drain queue ? fail h?ng lo?t |


| 2026-11-04 | [queue-sort-move.md](./2026-11-04-queue-sort-move.md) | Sort/move h?ng ch? kh?ng ??i th? t? th?t (UI fallback + group_index) |


| 2026-11-04 | [hardsub-partial-cover.md](./2026-11-04-hardsub-partial-cover.md) | Hardsub che h? 2 m?p (OCR h?p) |


| 2026-11-03 | [split-parent-false-failed.md](./2026-11-03-split-parent-false-failed.md) | Parent sau split b?o failed d? Full/part ?? xong |


| 2026-11-02 | [pronoun-consistency-abc.md](./2026-11-02-pronoun-consistency-abc.md) | Analyze+lock+ledger+QA x?ng h? (V2/V4/V5) |


| 2026-11-02 | [pronoun-aurora-port.md](./2026-11-02-pronoun-aurora-port.md) | Port post-pass x?ng h? + Aurora name/pronoun + cloud route t? V4 ? V2 |


| 2026-11-02 | [autosplit-asr-set-stage.md](./2026-11-02-autosplit-asr-set-stage.md) | Phim d?i auto-split: ASR parent crash `Manifest.set_stage` ? part kh?ng ASR/translate |


| 2026-10-09 | [films-ui-delete-missing.md](./2026-10-09-films-ui-delete-missing.md) | `films/ui`: nhi?u job ?? xo? th? m?c v?n t?n ??ng, thi?u b? l?c th? m?c v? thi?u ch?c n?ng xo? film |


| 2026-10-06 | [batch7-ui-split.md](./2026-10-06-batch7-ui-split.md) | ??t 7: g? UI c? `index1/2.html`; `server.py` 6221 d?ng ? t?ch `routes_ui/hg/agent.py` (OpenAPI gi?ng h?t) |


| 2026-10-08 | [queue-worker-disk-full.md](./2026-10-08-queue-worker-disk-full.md) | ? D: ??y ? `_save()` OSError gi?t thread h?ng ??i, job ch? ??ng im (ch?a s?a code, m?i x? l? tay) |


| 2026-10-07 | [hg-merge-queue.md](./2026-10-07-hg-merge-queue.md) | Hongguo Merge all: h?ng ??i ch? trong RAM b? agent restart xo?, b?m x?p h?ng b? treo v? chu?n ho? ??ng b?, UI kh?ng hi?n b??c/ti?n ?? |


| 2026-10-07 | [source-duplicate-copy.md](./2026-10-07-source-duplicate-copy.md) | Video ngu?n ch?p 2 b?n (th? vi?n + job): `/source-path` lu?n copy, import r?i v? copy kh?ng log ? 0281/dccc th?a ~36,7 GiB |


| 2026-10-07 | [sfxlib-sidechain-short.md](./2026-10-07-sfxlib-sidechain-short.md) | `sfx_lib` pass 1 c? l?c h?t ?u?i (~30% l?n, `sidechaincompress` k?t th?c s?m khi dub ng?n h?n phim) |


| 2026-10-07 | [m20-voice-bgm-apad.md](./2026-10-07-m20-voice-bgm-apad.md) | `voice_bgm` thi?u `apad` ? nh?c th? vi?n + audio d?ng ? c?u tho?i cu?i, cu?i video im l?ng |


| 2026-10-06 | [restart-killed-itself.md](./2026-10-06-restart-killed-itself.md) | Restart kill server c? xong th? v?ng `NoSuchProcess` tr?n `cmd.exe` b?c server ?? t? tho?t (l?p l?i 07/10; gi? thuy?t PID t?i d?ng ban ??u kh?ng ph?i nguy?n nh?n ch?nh) ? server :8801 n?m ch?t, 3a2e ch?a x?p l?i |


| 2026-10-06 | [batch6-maintenance.md](./2026-10-06-batch6-maintenance.md) | ??t 6 review: kh?ng c? git/pytest.ini, test hardsub k? v?ng sai, filter che hardsub v??t gi?i h?n ffmpeg khi nhi?u ?o?n (M3), script ch?t ? g?c (c? c?i ghi v?o V1) |


| 2026-10-06 | [batch5-agent-safety.md](./2026-10-06-batch5-agent-safety.md) | ??t 5 review: ch? tr?n Telegram ??i tr?ng th?i / t? b?t Auto-pilot, agent ch?y th?ng tool ph? hu?, `hg_auto_flow` b?c nh?m b? theo chu?i con v? treo request 90 ph?t, `/stop` ph?i ch? agent, k?t qu? tool tr?n context |


| 2026-10-06 | [batch4-write-races.md](./2026-10-06-batch4-write-races.md) | ??t 4 review: manifest ghi ?? c? HOLD, b?m tay ch?y song song v?i h?ng ??i, 2 b?n server/sidecar, Auto-pilot l?p job l?i, audio/TTS/b?n tr?n c? b? d?ng l?i, checkpoint ghi d? |


| 2026-10-06 | [batch3-single-source.md](./2026-10-06-batch3-single-source.md) | ??t 3 review: c?ng job render kh?c nhau theo ???ng g?i, s?a config kh?ng ?n t?i restart, batch_config/autopilot state ghi d? ? Auto-pilot d?ng m?c ??nh sai |


| 2026-10-06 | [batch2-security.md](./2026-10-06-batch2-security.md) | ??t 2 review: web l? g?i API/sidecar, SSRF Hongguo, path traversal t?n b?, XSS onclick, key trong code/backup, LLM s?p ?? tr?ng c?u, model ??ng b?ng t?i restart |


| 2026-10-06 | [batch1-data-loss.md](./2026-10-06-batch1-data-loss.md) | ??t 1 review: heal ??nh done sai, Stop kh?ng kill ffmpeg, m?t opts/watermark, d?n t?p Hongguo xo? nh?m, agent ch?n nh?m phim, d?i m?c ti?ng 2 l?n, c?t c?u runaway sai |


| 2026-10-06 | [agent-text-toolcall-overmatch.md](./2026-10-06-agent-text-toolcall-overmatch.md) | Agent ch?y tool ch? v? ???c nh?c trong c?u tr? l?i (parser `tool(...)`) |


| 2026-09-26 | [ui4-ops.md](./2026-09-26-ui4-ops.md) | UI4 Ops |


| 2026-09-26 | [p0-job-management.md](./2026-09-26-p0-job-management.md) | Opts theo job, ch?y series, dashboard queue, GPU gate |


| 2026-09-26 | [duck-bgm-twopass-port.md](./2026-09-26-duck-bgm-twopass-port.md) | Port duck/duck_bgm two-pass sang V2 |


| 2026-09-25 | [duck-bgm-audio-truncated.md](./2026-09-25-duck-bgm-audio-truncated.md) | duck_bgm c?t c?t audio |


| 2026-09-24 | [queue-voice-stop-race.md](./2026-09-24-queue-voice-stop-race.md) | Queue: race voice/stop |


| 2026-09-24 | [stop-mux-ffmpeg.md](./2026-09-24-stop-mux-ffmpeg.md) | D?ng kh?ng kill ???c ffmpeg mux |


| 2026-09-24 | [hardsub-hwaccel-drawbox.md](./2026-09-24-hardsub-hwaccel-drawbox.md) | **T?i ?u:** b? hwaccel+drawbox (h?t xanh, nhanh) |


| 2026-09-24 | [hardsub-green-bar.md](./2026-09-24-hardsub-green-bar.md) | Bar xanh / l?ch (desat - superseded) |


| 2026-09-24 | [run-all-stale-mux.md](./2026-09-24-run-all-stale-mux.md) | 1-click l?i li?n t?c / 409 mux running |





- [2026-11-10-run-v2-bat-lf](2026-11-10-run-v2-bat-lf.md)  run_v2.bat LF?CRLF / false missing Python






- [2026-11-10-firered-use-half](2026-11-10-firered-use-half.md)  FireRed default BF16 use_half


- `2026-11-10-mix13-title-nguoi.md` — Mix #1+#3 title→ngươi + UI REVIEW backup

- 2026-11-10-firered-root-path.md — FIRERED_ROOT path + _check_stopped
- 2026-11-10-firered-bf16-align.md — BF16 torchaudio forced_align
- 2026-11-12-translate-simple.md — luồng dịch simple (TRANSLATE_PIPELINE=simple, mặc định tắt)
- 2026-11-12-translate-simple-next.md — simple «next»: lexicon src, quy tắc xưng hô, bổ sung cặp, học lại, nguồn ZH, gỡ lặp ASR (cờ mặc định tắt)
- 2026-11-12-aac-extract-rematrix.md — ASR/Demucs chết rematrix 21ch (AAC hỏng merged) → extract_pcm salvage+chunk+silence
- 2026-11-12-asr-demucs-default.md — ASR mặc định trên vocals Demucs (ASR_USE_DEMUCS=1, fallback audio gốc) + separate chia khúc tại khoảng lặng, cắt/ghép đúng từng mẫu
- 2026-11-12-brain-telegram-hold.md — Second Brain: Telegram theo sự kiện (events, gộp 1 tin/tick), digest ≥10', DECISION lọc + khử trùng lặp, gỡ HOLD cũ job đã xong, heal plan rỗng có note; chẩn đoán ASR 2937ffd7989f
- 2026-11-13-firered-slice-silence.md — FireRed ASR chia slice tại khoảng lặng (±60 s) + đệm 2 s lọc theo tâm câu, cắt đúng mẫu; FIRERED_SLICE_SEC=0 = cả file; tools/asr_boundary_scan.py
- 2026-11-13-brain-finished-hold.md — Brain: một `job_finished` (output/đã đăng/ghép Full/part) → heal/watch/brain/LLM bỏ qua; park tự động (⏸ tự thử lại) ≠ HOLD cần người (⛔); bảng vòng đời HOLD
- (2026-11-18) chuẩn hóa thư viện: xem CHANGELOG 18/11 — `lib_normalize` hàng đợi + kiểm đã chuẩn, Films UI «📐 Chuẩn hóa đã tick»
- 2026-11-17-qa-hold-ask-telegram.md — HOLD QA hỏi người qua Telegram (ZH/VI/đề xuất/lý do + nút ✅⏭▶️ + reply câu VI); quá 60' mềm tự áp, cứng chắc áp, cứng còn lại gác job để hàng đợi chạy tiếp
