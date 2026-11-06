# Engines atoms (AST)

- **Files:** 38
- **Functions/methods:** 538
- **Scope:** `engines/**/*.py` (module-level defs + class methods; nested defs skipped)

### engines/__init__.py
- *(none)*

### engines/asr/__init__.py
- *(none)*

### engines/asr/asr.py
- `_audio_marker` — (no docstring) — L46
- `_src_id` — (no docstring) — L50
- `extract_audio` — Tách audio về 16kHz mono PCM — chuẩn đầu vào Whisper. Ghi .partial rồi replace + marker nguồn. — L56
- `_wav_seconds` — (no docstring) — L78
- `_probe_seconds` — (no docstring) — L91
- `audio_wav_stale` — audio.wav có sẵn không dùng được: rỗng, marker khác nguồn / khác filter mốc, hoặc (chưa có — L100
- `ensure_audio_wav` — Trích audio.wav khi thiếu / hỏng / khác nguồn (hoặc force). True nếu vừa trích. — L130
- `resolve_asr_source` — Xác định nguồn audio sạch và chuẩn xác cho ASR. — L144
- `_cut_wav_from` — Cắt phần còn lại từ start_sec (resume ASR giữa chừng). — L197
- `pick_device` — Chọn cuda nếu có GPU, không thì cpu. Trả (device, compute_type). — L206
- `_salvage_asr` — Crash/treo: giữ asr.json đã có, status pending để bấm Tiếp tục. — L219
- `run_asr` — (no docstring) — L247
- `main` — (no docstring) — L421

### engines/asr/asr_align_nano_para.py
- `_norm_chars` — (no docstring) — L32
- `_ms_pair_to_s` — FunASR Paraformer timestamp luôn là milliseconds (vd. [8530, 8730] = 8.53s). — L36
- `extract_char_timeline` — Từ raw FunASR generate() → [{ch, start, end}, ...] (giây). — L42
- `_zip_text_ts` — (no docstring) — L68
- `chars_from_segments_spread` — Fallback khi không có char-ts: trải đều ký tự trong từng câu Para. — L103
- `_dtw_align` — DTW: trả map nano_idx -> para_idx (độ dài = len(nano_chars)). — L125
- `_window_map` — Map tỉ lệ + chỉnh local khi quá dài cho full DTW. — L189
- `align_nano_to_para` — Giữ text Nano; start/end lấy từ char-ts Para đã align. — L212
- `run_align` — (no docstring) — L318
- `main` — (no docstring) — L371

### engines/asr/asr_fix_align.py
- `_load` — (no docstring) — L41
- `_save_asr` — (no docstring) — L45
- `step1_nano_fallback` — Chỗ monotonic_fix (và đảo thời gian): lấy lại timing Nano theo chữ. — L55
- `_merge_indices_to_windows` — Gộp index gần nhau thành cửa sổ FA. — L105
- `step2_forced_align` — Forced-align từng cửa sổ chứa các câu nano_fallback. — L129
- `run_fix` — (no docstring) — L235
- `main` — (no docstring) — L312

### engines/asr/asr_hybrid_progress.py
- `_load_json` — (no docstring) — L21
- `map_sidecar_pct` — (no docstring) — L30
- `active_sidecar_progress` — Trả (tag, payload) sidecar đang chạy mới nhất; ưu tiên Para nếu cả hai. — L36
- `mirror_to_asr_stage` — Ghi tiến độ sidecar vào stages.asr (giữ hybrid_fa). Trả stage đã cập nhật. — L78
- `overlay_job_asr` — Overlay tiến độ sidecar lên dict stages.asr (cho API, không ghi đĩa). — L122

### engines/asr/asr_repair.py
- `_norm` — (no docstring) — L50
- `_load` — (no docstring) — L54
- `_overlap` — (no docstring) — L58
- `_text_sim` — Độ giống 0..1 (containment + overlap tuần tự) trên chuỗi đã _norm. — L62
- `_mid` — (no docstring) — L82
- `_already_has_similar` — True nếu base đã có câu gần nghĩa trong ±window_s (align lệch time). — L86
- `_para_cover` — (no docstring) — L109
- `_align_rank` — Ưu tiên giữ khi dedupe (cao hơn = tốt hơn). — L115
- `dedupe_shifted_repeats` — Xóa nhân bản lệch giờ: cùng/_gần text trong ±window_s → giữ 1 bản. — L129
- `_merge_windows` — wins: (start, end, reason) → merged {start,end,reasons}. — L184
- `detect_gaps` — Para có đoạn mà base phủ < max_cover_ratio → nghi thiếu câu. — L204
- `detect_cer_mismatches` — Chữ base khó khớp Para char-stream quanh mốc → nghi nghe sai. — L241
- `_asr_nano_clip` — (no docstring) — L280
- `apply_repairs` — Nano ASR từng cửa sổ: — L308
- `run_repair` — (no docstring) — L416
- `main` — (no docstring) — L523

### engines/asr/asr_spam.py
- `_strip_punct` — (no docstring) — L31
- `filler_stats` — (no docstring) — L35
- `is_phrase_loop_spam` — True nếu có cụm 2–12 chữ lặp ≥6 lần (vd «区域的»×200) — ASR kẹt loop. — L53
- `is_phrase_loop_remnant` — Sau clean_zh_spam giữ tối đa 2× unit — vẫn sót «…区域的区域». — L77
- `is_bg_filler_spam` — True nếu giống tiếng nền (cười/rên lặp), không phải thoại bình thường. — L104
- `is_filler_only` — (no docstring) — L119
- `clean_filler_text` — Rút chuỗi filler; giữ phần thoại thật nếu có. — L126
- `_load_heal_sources` — Sidecar ASR khác để vá filler (ưu tiên nano → para → sense → firered). — L140
- `_overlap_iou` — (no docstring) — L173
- `_heal_from_sources` — Tìm câu thật overlap đủ (IoU) — tránh lấy câu kế cận lệch thời gian. — L183
- `sanitize_asr_rows` — Rút spam + (tuỳ chọn) vá từ sidecar khác. — L266
- `sanitize_asr_file` — Đọc JSON ASR → sanitize → ghi đè (+ SRT nếu có cặp). — L390
- `prefer_non_spam` — Khi 2 bản lệch: ưu tiên bản không phải filler nền. — L423
- `main` — (no docstring) — L443

### engines/asr/asr_vad_utils.py
- `vad_kwargs_from_env` — Cho phép override qua env ASR_VAD_* (ms). — L33
- `parse_vad_ranges` — FunASR VAD generate → [(start_s, end_s), ...]. — L54
- `merge_close_ranges` — Gộp đoạn kề nhau (khoảng hở < gap_s), nhưng không gộp nếu tổng độ dài vượt max_dur_s. — L71
- `pad_ranges` — Mỗi VAD range → slice ASR có pad + overlap với hàng xóm. — L102
- `shift_char_timeline` — Cộng offset (slice_start) vào char-ts; optional cắt ngoài cửa sổ VAD gốc. — L141

### engines/asr/firered_asr.py
- `_roots` — (no docstring) — L46
- `_ensure_firered_importable` — (no docstring) — L54
- `_parse_firered_result` — FireRedAsr2System.process → [{start,end,text}]. — L69
- `run_asr_firered` — (no docstring) — L116
- `main` — (no docstring) — L330

### engines/asr/fun_asr_nano.py
- `_pick_device` — (no docstring) — L44
- `_wav_dur` — (no docstring) — L56
- `_ms_to_s` — FunASR timestamp luôn là milliseconds. — L71
- `_split_text_by_punct` — Tách câu theo dấu câu (mỏng: gọi subs.split_text_by_punct). — L79
- `_spread_sentences` — Không có timestamp ký tự -> chia thời gian theo độ dài chữ. — L85
- `_parse_funasr_result` — Chuẩn hoá output FunASR -> [{start, end, text}, ...]. — L106
- `_split_by_punct` — Gộp timestamp ký tự thành câu theo dấu câu Trung/Việt. — L178
- `_vad_ranges_chunked` — VAD theo cửa sổ ~chunk_s — tránh treo generate() trên file dài. — L216
- `_vad_slice_asr` — VAD cắt đoạn -> ASR từng đoạn có pad/overlap (Fun-ASR-Nano không có CTC ts). — L295
- `run_asr_nano` — sidecar: ghi asr.<tag>.json + sub.zh.<tag>.srt, không đụng asr.json / manifest ASR chính. — L398
- `main` — (no docstring) — L580

### engines/asr/hardsub_asr.py
- `_find_video` — (no docstring) — L31
- `_probe_size` — (no docstring) — L42
- `_norm_zh` — (no docstring) — L55
- `zh_sim` — Độ giống 0..1 (chuỗi đã chuẩn hóa). — L61
- `_band_y_frac` — (y0, y1) tỷ lệ chiều cao — ưu tiên hardsub_band.json. — L73
- `extract_hardsub_cues` — OCR crop đáy → list {start,end,zh,n,source}. — L100
- `_samples_to_cues` — Gộp frame liên tiếp cùng/gần text thành cue. — L166
- `merge_hardsub_into_asr` — Giữ timing ASR; chỉ thay text khi hardsub KHỚP chữ (tránh dính câu bên cạnh). — L202
- `_to_srt` — (no docstring) — L285
- `sync_script_zh` — Cập nhật script.json zh theo asr (khớp i hoặc time). — L309
- `run_hardsub_asr` — (no docstring) — L351
- `main` — (no docstring) — L432

### engines/asr/hybrid_asr.py
- `_prog` — (no docstring) — L45
- `run_hybrid_fa` — (no docstring) — L55
- `main` — (no docstring) — L180

### engines/asr/nano_fa_asr.py
- `_merge_all_to_windows` — Gom các câu thoại gần nhau thành cửa sổ nhỏ (<=24s) để Forced Aligner xử lý tối ưu. — L39
- `align_nano_with_fa` — Căn mốc trực tiếp từng câu của Nano bằng Qwen3ForcedAligner. — L75
- `run_nano_fa` — (no docstring) — L198
- `_torch_has_cuda` — (no docstring) — L314
- `main` — (no docstring) — L322

### engines/asr/paraformer_zh.py
- `run_asr_paraformer` — (no docstring) — L45
- `main` — (no docstring) — L292

### engines/asr/sensevoice_asr.py
- `_clean_sv_text` — (no docstring) — L51
- `_post_clean_segs` — (no docstring) — L65
- `run_asr_sensevoice` — sidecar: ghi asr.<tag>.json + sub.zh.<tag>.srt, không đụng asr.json / manifest ASR chính. — L77
- `main` — (no docstring) — L237

### engines/assemble.py
- `_read_mono` — Đọc 1 clip về mono float32 @ target_sr (bounded — chỉ 1 clip trong RAM). — L31
- `_compress_to_file` — Nén 'ratio'× bằng rubberband giữ formant -> file tạm. ratio<=1 trả nguyên in_path. — L65
- `_load_clips` — (no docstring) — L86
- `_slot_sec` — (no docstring) — L95
- `_natural_max_sec` — Trần độ dài đọc hợp lý (không phải câu TTS runaway). — L99
- `_runaway_cap_sec` — VieNeu đôi khi hú 15–23s cho câu 1–2 tiếng. Cắt trần, không đẩy cả film. — L105
- `is_runaway_tts` — True nếu wav quá dài bất thường so với slot/chữ (VieNeu hú). — L120
- `_resolve_max_speed` — UI/API thắng. Env ASSEMBLE_MAX_SPEED chỉ khi không truyền (None). — L125
- `_fit_mode` — fixed (max_speed>1 từ UI/API) | adaptive (mặc định) | off (ASSEMBLE_FIT_MODE=off). — L139
- `_is_bloated` — TTS kéo dài bất thường so với số chữ, hoặc ASR dồn mốc (khe ≤0.25s mà đọc >0.6s). — L147
- `_place` — (start, ratio) của một câu theo chế độ khớp. — L153
- `compute_fit_placements` — Đủ câu + khớp hình theo khoảng trống (KHÔNG cắt, nén theo _place). — L173
- `write_fit_timings` — Ghi tts_fit.json từ tts.json (không cần ghép lại audio). — L219
- `assemble` — NAIVE: báo cáo độ khớp (từ metadata, mọi độ dài). Dựng file chỉ khi ngắn. — L238
- `assemble_fit` — Đủ câu + ghép cạnh + bắt kịp khoảng trống (đúng yêu cầu user). — L284
- `main` — (no docstring) — L396

### engines/check_block.py
- `_utc_now` — (no docstring) — L21
- `extract_video_id` — Trích xuất Video ID (11 ký tự) từ link YouTube bất kỳ hoặc ID thô. — L25
- `check_youtube_block` — Kiểm tra video YouTube có bị Block hay dính bản quyền không (không cần cookie/đăng nhập). — L52
- `check_film_by_job` — Kiểm tra trạng thái bản quyền của một phim theo job_id và lưu kết quả vào film_db. — L319

### engines/clone_tts.py
- `resolve_engine_python` — Tìm python.exe của engine. Config sai path (thường sau install) -> thử chỗ mặc định. — L55
- `_load_registry` — (no docstring) — L91
- `list_clone_voices` — Tên các giọng clone đã có ref audio hợp lệ. — L97
- `_resolve_ref` — (no docstring) — L107
- `voice_ref_text` — (ref_path, ref_text) của 1 giọng, hoặc None. — L116
- `enroll_voice` — Đăng ký giọng clone vào voices/f5_voices.json (VieNeu + OmniVoice dùng chung). — L127
- `_is_trivial_vi` — True nếu không có chữ thật (vd ',', '...', '!!!') — không nên gọi TTS. — L149
- `vi_for_tts` — Chuẩn bị chữ cho VieNeu/Omni: gộp số có dấu nghìn để đọc đúng. — L155
- `_write_silence_wav` — Ghi wav im lặng đúng độ dài timeline (tối thiểu 0.15s để qua kiểm tra dur). — L180
- `_silence_entry` — Placeholder im lặng cho câu vô nghĩa / wav hỏng — đủ slot timeline, không báo thiếu. — L195
- `_dur` — Độ dài wav (giây). Ưu tiên wave; fallback ffprobe. — L203
- `_entry_from_wav` — Tạo entry tts.json từ file wav đã có. None nếu file hỏng/quá ngắn. — L221
- `_unlink_quiet` — (no docstring) — L232
- `_drop_runaway_from_done` — Resume/recheck: bỏ clip hú khỏi done + xóa wav → TTS sẽ đọc lại. — L239
- `_pack_clip` — Postprocess + entry. None nếu hỏng. Caller xử lý runaway. — L258
- `_recheck_pack_and_retry` — Đóng gói todo vừa TTS; runaway -> xóa -> retry tối đa N lần -> silence slot. — L267
- `_clip_key` — (no docstring) — L342
- `_load_keys` — (no docstring) — L347
- `_save_keys` — (no docstring) — L355
- `_stamp_keys` — (no docstring) — L365
- `_scan_done_from_disk` — Resume: nhận diện seg_XXXX.wav đã ghi (sau khi Dừng) dù chưa kịp ghi tts.json. — L371
- `_postprocess_clip` — (no docstring) — L392
- `_salvage_progress` — Khi dừng/crash: gom wav đã có -> tts.json, status pending (để bấm Tiếp tục). — L403
- `run_clone_tts` — (no docstring) — L462
- `_cleanup_audio` — Làm sạch clip gen ra: — L616
- `_trim_onset` — Cắt 'âm rác đầu' của OmniVoice: nếu đoạn tiếng ĐẦU TIÊN ngắn (<0.45s) và có — L646
- `_apply_speed` — Đổi tốc độ đọc bằng rubberband giữ formant (fallback atempo). speed>1 nhanh, <1 chậm. — L683
- `_run_worker` — Chạy worker venv cho `lines`=[(i,text)], ghi out_dir/seg_XXXX.wav. Raise nếu lỗi. — L711
- `synth_one` — Đọc 1 câu bằng engine+giọng -> ghi ra out_path (dùng cho nghe thử / đọc lại 1 clip). — L840
- `resynth_clip` — Đọc lại DUY NHẤT câu index i -> tts/seg_i.wav + vá tts.json. Trả entry. — L865
- `_norm_txt` — Chuẩn hoá để so khớp: thường hoá, bỏ dấu câu, gộp khoảng trắng. — L885
- `_similar` — (no docstring) — L893
- `_asr_check` — Nghe ngược list [(wav_path, expected_vi)] -> [(score, transcript)]. Whisper small. — L901
- `verify_and_fix` — TỰ KIỂM & SỬA: ASR nghe ngược từng clip, câu nào lệch nhiều so với bản dịch — L920
- `_roughness` — Độ 'nhám/méo' của clip: HF-ratio ở các khung CÓ CAO ĐỘ (voiced) — loại âm gió — L975
- `fix_glitches` — TỰ PHÁT HIỆN & SỬA câu bị vỡ/méo (âm): đo độ nhám voiced-frame, câu nào nhám — L1003
- `_prog` — (no docstring) — L1063
- `_finalize` — (no docstring) — L1079

### engines/download.py
- `_request_stop` — (no docstring) — L54
- `_is_stopped` — (no docstring) — L59
- `_clear_stop` — (no docstring) — L64
- `_kill_job_aria2c` — Kill tiến trình aria2c đang tải cho ĐÚNG job này (nhận diện qua job_id/đường — L69
- `_aria2_downloaded` — Byte ĐÃ TẢI THẬT theo file điều khiển .aria2. Khi tải đa kết nối, file .part — L91
- `_clean_incomplete_fragments` — Xoá RIÊNG các mảnh tải DỞ (file .part + control .aria2) để tải lại sạch bằng — L113
- `_delete_sources` — Xoá mọi source.* ; trả True nếu SẠCH (không còn file nào kẹt/khoá). — L127
- `_format_sel` — Selector yt-dlp. max_height giới hạn chiều cao; hevc=True ưu tiên H.265 cùng độ phân giải. — L141
- `_cfg_max_height` — DOWNLOAD_MAX_HEIGHT từ env/config (vd 720/480). 0/off = không giới hạn. — L172
- `_cfg_prefer_hevc` — DOWNLOAD_PREFER_HEVC=1 → ưu tiên H.265 cùng độ phân giải (file nhẹ, CDN đỡ đứt). — L190
- `_auto_height_for_duration` — Phim rất dài (Bilibili multi-season) → 720p AVC dễ ~3GB+, CDN hay đứt. — L202
- `_probe_duration` — Lấy duration nhanh (không tải) để chọn format. — L216
- `detect_platform` — (no docstring) — L232
- `normalize_url` — Chuyển link Bilibili kiểu mới về format yt-dlp hiểu (từ code Galaxy). — L243
- `job_id_from_url` — Job id mặc định = hash URL. Chạy lại cùng URL -> cùng thư mục -> resume. — L252
- `find_cookie_file` — Tìm file cookie theo nền tảng trong cookies_dir (vd bilibili_cookies.txt). — L257
- `get_aria2c_path` — Tìm aria2c -> trả ĐƯỜNG DẪN TUYỆT ĐỐI (yt-dlp tìm external_downloader trong — L271
- `apply_speed_opts` — Tải mảnh song song + aria2c nếu có (args tune từ code Galaxy). — L281
- `download_video` — Tải 1 video về work_dir. Trả về dict trạng thái stage (video_path + metadata). — L305
- `main` — (no docstring) — L659

### engines/llm.py
- `_settings` — (base, key, model) đọc LÚC GỌI (file config trước env) — sửa pineline.config.json — L58
- `_llama_base` — (no docstring) — L69
- `get_llama_models` — Lấy danh sách các model đang load trên llama-server (:8083). — L77
- `get_ollama_models` — Lấy danh sách model trên Ollama (:11434). — L95
- `list_available_models` — Trả về toàn bộ model khả dụng (llama-server 8083, ollama 11434, config). — L108
- `_is_loopback_base` — (no docstring) — L158
- `is_local` — (no docstring) — L163
- `is_chatgpt` — Model route qua Aurora / Chat2Api (pool account Free). Tiền tố chatgpt/ hoặc aurora/. — L170
- `_chatgpt_settings` — (bases, key, default_model) cho Aurora pool. — L176
- `_jwt_expired` — True nếu JWT có claim exp đã qua (token local hết hạn không được đè Aurora pool). — L204
- `_chatgpt_token_file` — Đọc access token tùy chọn từ data/chatgpt_token.txt (bỏ qua nếu JWT hết hạn). — L219
- `_chatgpt_chat` — Gọi Aurora/Chat2Api (OpenAI-compatible). Pool Free xoay phía server Aurora. — L238
- `aurora_upload_file` — Upload file lên Aurora `POST /v1/files` (cần ChatGPT access_token thật). — L315
- `_file_unread_response` — GPT trả JSON/text báo không đọc được file đã upload (thường do lệch account pool). — L391
- `chatgpt_chat_with_file` — Hỏi GPT kèm file đã upload (`type: input_file` + `file_id`) — 1 lần đọc file. — L411
- `ensure_ollama_model` — Model Ollama chưa pull -> TỰ pull (lần đầu, có thể vài GB). Auto cho bước dịch. — L513
- `free_ollama_vram` — Alias — nhả VRAM (Ollama + torch) trước/sau bước GPU. — L535
- `unload_local` — Nhả model Ollama khỏi VRAM (RTX 3060 12GB không chứa nổi LLM + TTS cùng — L541
- `_ollama_num_ctx` — Gemma3/4 mặc định context 131072. Cấp KV 128k trên RTX 3060 12GB -> tràn — L550
- `_ollama_chat` — Gọi Ollama qua endpoint GỐC /api/chat + TẮT thinking (think=False). — L560
- `chat` — Gửi messages, trả về text của assistant. Tự retry khi lỗi mạng/429/5xx. — L612
- `chat_with_meta` — Giống chat() OpenAI-path nhưng trả (content, meta) gồm usage/timings/TPS. — L765
- `parse_json` — Bóc JSON kể cả khi model bọc trong ```json ... ```, trailing commas hoặc kèm chữ thừa. — L822

### engines/media_ts.py
- `_boxes` — (no docstring) — L32
- `_child` — (no docstring) — L49
- `mp4_track_stts` — (timescale, [(count, delta)]) của track đầu tiên loại `kind` (soun/vide). — L53
- `audio_drift_points` — Trục 'dồn mẫu' → trục mốc: (vị trí theo mẫu [s], tiếng dư tích luỹ tới đó [s]). — L92
- `audio_ts_drift` — Tổng tiếng dư so với mốc (s). 0 nếu không đọc được. — L119
- `make_retime` — Hàm t(trục dồn mẫu) → t(trục hình). None nếu lệch không đáng kể. — L125
- `_probe_dur` — (no docstring) — L138
- `_retime_srt` — (no docstring) — L147
- `ensure_job_audio_ts` — Job đã ASR trên audio dồn mẫu → dời mốc về trục hình + ghép lại dub_fit. — L158
- `_tmp_of` — (no docstring) — L229
- `_backup_once` — Không bao giờ đè backup đã có — bản trong _pre_audio_ts luôn là bản gốc trước lần dời đầu. — L233
- `_atomic_write` — (no docstring) — L239
- `_commit_retime` — Pha thay file — chạy lại an toàn: mỗi bước kiểm tra trạng thái trước khi làm. — L245
- `main` — (no docstring) — L279

### engines/mux.py
- `_find_video` — (no docstring) — L31
- `_pick_dub` — Chọn track lồng tiếng: audio ngoài > dub_fit.wav > (tự ghép fit). — L40
- `_has_audio` — Video gốc có luồng audio không (để biết có ducking được không). — L59
- `run_mux` — (no docstring) — L72
- `main` — (no docstring) — L124

### engines/ocr.py
- `_meaningful` — Giữ chữ CÓ NGHĨA: ≥2 chữ Hán, hoặc số ≥3 chữ số (ID). Bỏ rác latin / 1 chữ đơn. — L39
- `_find_video` — (no docstring) — L54
- `_probe_size` — (no docstring) — L65
- `extract_keyframes` — Trích KEYFRAME + mốc giờ. Giải mã chỉ I-frame nên nhanh. stride: lấy cách quãng. — L77
- `_classify_zone` — Trả 'wm' (watermark), 'sub' (hardsub thoại), hoặc 'cand' (ứng viên). — L113
- `run_ocr` — (no docstring) — L128
- `_translate_entries` — Dịch danh sách chữ trên hình sang tiếng Việt (1 lời gọi LLM). — L243
- `main` — (no docstring) — L262

### engines/playlist.py
- `_build_url_from_entry` — Lấy URL đầy đủ từ một entry playlist. extract_flat có khi chỉ trả id. — L37
- `expand_meta` — Như expand nhưng trả THÊM metadata để gom nhóm: — L53
- `expand` — Đọc link, trả danh sách URL video. Video đơn -> [url]; playlist -> [nhiều]. — L106
- `batch_download` — Tải tất cả video của 1 link. Trả list kết quả {url, job_id, ok, error}. — L119
- `main` — (no docstring) — L176

### engines/pronoun_consistency.py
- `_cfg` — (no docstring) — L30
- `analyze_enabled` — (no docstring) — L38
- `analyze_model` — (no docstring) — L43
- `chunk_size` — (no docstring) — L54
- `analyze_mode` — file = upload SRT ZH 1 lần (Aurora /v1/files). fast = mẫu+lô. full = quét hết. — L61
- `max_chunks` — (no docstring) — L66
- `min_chunks_before_stop` — (no docstring) — L73
- `early_stop_enabled` — (no docstring) — L80
- `is_pronouns_locked` — (no docstring) — L85
- `mark_locked` — (no docstring) — L94
- `export_zh_lines` — Chuẩn hoá [{i, zh}] từ asr segments hoặc script rows. — L110
- `write_zh_export` — (no docstring) — L128
- `write_zh_srt` — Xuất sub.zh.srt để Aurora upload (API.md: POST /v1/files). — L138
- `_apply_analyze_delta_to_plan` — (no docstring) — L174
- `analyze_via_srt_file` — Upload sub.zh.srt → GPT đọc 1 lần → glossary pronouns (Aurora file QA). — L193
- `select_analyze_lines` — fast: phủ đầu/giữa/cuối + câu có hô ngữ — ít lô hơn full scan. — L281
- `_slim_memory` — Giảm token gửi Aurora mỗi lô. — L323
- `_merge_pronouns` — (no docstring) — L347
- `_merge_chars` — (no docstring) — L375
- `_analyze_chunk` — (no docstring) — L393
- `analyze_full_zh` — A) Quét toàn bộ ZH theo lô + memory → cập nhật plan + lock pronouns. — L430
- `lock_banner` — Block inject vào plan_block / batch khi đã lock. — L597
- `review_lock_rules` — Prompt ép 31B review: khi đã lock thì CẤM đổi self/call. — L623
- `fix_preserves_locked_register` — True nếu bản sửa không đổi thanh ngữ chính so với nháp (khi đang lock). — L639
- `filter_review_fixes_for_lock` — Khi pronouns_locked: loại fix làm đổi thanh ngữ so với vi_nhap. — L658
- `ledger_from_prev` — B) Ledger từ vài câu VI trước — nhắc model giữ thanh ngữ đang dùng. — L681
- `_forms_in` — (no docstring) — L706
- `find_pronoun_jumps` — C) QA: trong cửa sổ gần nhau, vừa có {anh,em} vừa có {ông} ngôi hô / tôi lệch kiểu. — L718
- `ensure_analyze_before_translate` — Gọi từ translate.run_translate sau khi có plan. — L761
- `run_post_translate_consistency` — C+D sau dịch/polish: post-pass + QA jumps + GPT vá đỏ. — L784

### engines/render.py
- `_ass_colour` — #RRGGBB hoặc &HAABBGGRR -> ASS. — L64
- `_sum_expr` — a+b+…; ffmpeg chỉ nhận ≤100 hạng tử cộng phẳng → dài thì gom ngoặc cân bằng. — L79
- `_pw_expr` — Theo t: vals[i] với i nhỏ nhất có t < ends[i] (ends tăng dần, len = len(vals) - 1), hết → vals[-1]. — L92
- `_censor_expr` — enable=... cho blur cảnh nhạy cảm. Config CENSOR_RANGES='12-18,90-102' (giây) — L109
- `_probe_dur` — Độ dài video (giây) để tính % render. — L136
- `_ffmpeg_progress` — Chạy ffmpeg + đọc -progress -> cập nhật % vào manifest (mux). Trả (mã, lỗi). — L152
- `_no_power_throttle` — Tắt EcoQoS của Windows cho ffmpeg con (tránh bị dồn sang E-core khi console thu nhỏ). — L286
- `_mp4_video_stts` — (timescale, [count, delta, ...]) từ box stts của track video mp4/mov. — L309
- `_probe_pts` — (no docstring) — L365
- `squeeze_fixes` — Đoạn mốc thời gian bị nén khi gộp tập khác fps: N khung dài ~0 rồi 1 khung dài hàng phút. — L379
- `squeeze_setpts` — setpts trải lại các đoạn bị nén (rỗng nếu không có). — L436
- `_cfg_num` — (no docstring) — L450
- `chunk_plan` — (giây mỗi khúc, số khúc chạy cùng lúc). RENDER_CHUNK_SEC=0 hoặc RENDER_CHUNK_PAR<2 → 1 lượt. — L458
- `chunk_cuts` — Điểm cắt mỗi ~sec giây, nằm GIỮA 2 khung liền nhau (không trùng mốc khung → không lặp/mất khung). — L468
- `_run_chunked` — Render video theo khúc (giữ mốc gốc), tối đa `par` khúc chạy cùng lúc, ghép copy, gắn audio 1 lần. — L489
- `_encoder_pref` — (no docstring) — L687
- `_nvenc_state` — (no docstring) — L700
- `_nvenc_save` — (no docstring) — L711
- `_want_nvenc` — (no docstring) — L718
- `_nvenc_mark_ok` — (no docstring) — L734
- `_nvenc_mark_fail` — (no docstring) — L738
- `_attach_filter_complex` — Ghi filtergraph ra file — tránh cắt cmdline Windows (~8191 ký tự). — L756
- `_ff_input` — Đường dẫn -i khi ffmpeg cwd=work_dir: file trong job → tên/relative; ngoài → absolute. — L764
- `_x264_cmd` — Đổi lệnh nvenc → libx264 (bỏ flag chỉ GPU). — L774
- `normalize_vbitrate` — Chuẩn hoá bitrate H264: trả (vbit, buf). Cho phép 2M | 4M | 8M. — L791
- `_find_video` — (no docstring) — L813
- `_size` — (no docstring) — L824
- `_fps` — (no docstring) — L833
- `_esc` — Escape text cho drawtext. — L847
- `_map_pt` — Toạ độ fraction (0-1) sau khi zoom+crop giữa. — L853
- `_map_box` — Map hộp nguồn → sau zoom/crop; None nếu gần như bị crop hết. — L859
- `_flip_box` — (no docstring) — L881
- `_default_wm_corners` — Fallback góc kênh khi OCR không bắt được logo hình (ô nhỏ, chỉ mép). — L890
- `_uploader_hint` — (no docstring) — L921
- `_is_wm_text` — (no docstring) — L929
- `_wm_quadrant` — (no docstring) — L944
- `_expand_logo_pad` — OCR chữ → snap nhẹ về mép góc; giữ kích thước gần bbox, cap nhỏ. — L957
- `_cap_wm_frac` — Giới hạn hộp che sau map — không cho phình quá mép góc. — L986
- `_wm_sample_times` — Mốc giây lấy mẫu watermark trên TOÀN bộ video (không chỉ 3 phút đầu). — L1005
- `_extract_wm_frames` — Seek từng mốc → 1 frame JPEG. Nhanh hơn decode cả file. — L1032
- `_merge_wm_timeline` — Gộp hit (t,q,x0,y0,x1,y1,txt) → [{t0,t1,x,y,w,h}, …] theo góc + thời gian. — L1055
- `_parse_wm_cache` — Đọc cache: list dict timed, hoặc list [x,y,w,h] cũ → coi full video. — L1129
- `detect_overlays` — Dò hardsub (đầu phim) + watermark THEO THỜI GIAN trên cả video. — L1150
- `detect_hardsub_band` — Tương thích cũ: chỉ trả band. — L1286
- `_hs_cluster_band` — (y0,y1) của 1 cụm vị trí — bỏ 5% ngoại lai mỗi phía khi đủ mẫu. — L1295
- `detect_hardsub_track` — Dò toạ độ hardsub THEO THỜI GIAN trên toàn video (file merge đổi vị trí giữa các tập). — L1303
- `_even` — (no docstring) — L1522
- `_rounded_bar_alpha` — Biểu thức geq alpha cho hình chữ nhật bo góc (0–255). — L1526
- `_boxblur_r` — Radius boxblur hợp lệ: ffmpeg yêu cầu 2*r < min(w,h) của plane. — L1544
- `_safe_crop` — crop ffmpeg an toàn khi iw/ih đổi giữa chừng (biểu thức min). — L1554
- `_hardsub_bar_filter` — Che hardsub: 1× boxblur + lớp đen geq bo góc (không desat). — L1563
- `_hardsub_cover_fullw` — Luôn phủ hết ngang khi che hardsub — OCR x0/x1 thường chỉ ~50% giữa → chữ Trung lòi 2 mép. — L1596
- `_hardsub_track_boxes` — Dải hardsub (tỉ lệ nguồn) → ô pixel trên canvas TRƯỚC zoom: (bx,by,bw,bh,ranges,tổng giây). — L1602
- `_stretch_cfg` — (sigma ngang, sigma dọc, phủ hết bề ngang) cho kiểu che stretch. — L1660
- `_stretch_chain` — Che hardsub kiểu kéo giãn: trung bình vài hàng ngay trên ô, kéo dọc phủ ô rồi làm mềm — L1671
- `_stretch_track_filter` — Kiểu stretch cho mọi dải: khoảng nào nhiều dải cùng hiện thì phủ 1 ô gộp (không chồng 2 lớp). — L1685
- `_hardsub_track_filter` — Che đúng ô hardsub theo thời gian (không lớp đen). — L1722
- `_srt_to_ass_margins` — SRT → ASS với MarginV riêng từng câu (mv_at(t_giữa_câu) → px). Trả số câu. — L1759
- `_hardsub_track_filter_dyn` — Nhiều dải → 1 chuỗi blur chính + 1 chuỗi phụ (chỉ bật lúc 2 dải chồng nhau). — L1803
- `resolve_canvas` — Chọn khung xuất: source = giữ gốc; 1080/1k = Full HD (giữ tỉ lệ, tối đa 1920×1080). — L1867
- `_parse_flip` — (no docstring) — L1880
- `build_video_filter` — Trả (filter_comma_chain_without_final_vout, meta). — L1891
- `_pick_dub` — (no docstring) — L2228
- `_normalize_audio_mode` — (no docstring) — L2239
- `_uses_sidechain` — duck / duck_bgm / sfx_lib dùng sidechaincompress — KHÔNG chạy cùng encode video — L2252
- `_stage_note` — Callback ghi dòng log tiến trình con vào cur_text của stage render (thưa ≥2 s). — L2258
- `_ensure_mixed_audio` — Pass 1: mixed_audio.wav (audio-only + sidechain). Trả (path, used_mode). — L2276
- `_mix_signature` — Filter + (đường dẫn, size, mtime) mọi input -i + độ dài — đổi thì phải trộn lại. — L2349
- `_write_mix_signature` — (no docstring) — L2366
- `_build_audio_filter` — Dựng filter audio + THÊM input vào cmd. Trả (filter, tên_chế_độ_thực). — L2375
- `run_render` — (no docstring) — L2518
- `main` — (no docstring) — L3003

### engines/render_fx.py
- `_esc_movie` — Escape path for ffmpeg movie= / lut3d= file=. — L21
- `resolve_lut_file` — (no docstring) — L27
- `resolve_grain_file` — (no docstring) — L41
- `list_bgm_files` — (no docstring) — L50
- `pick_bgm` — (no docstring) — L63
- `default_audio_mode` — voice_bgm nếu có thư viện BGM; không thì voice_only (không nhạc gốc). — L75
- `clamp_zoom` — (no docstring) — L80
- `normalize_grain` — (no docstring) — L98
- `_eq_fallback` — (no docstring) — L109
- `build_motion_zoompan` — Ken Burns nhẹ + Drift: scale cố định theo zoom + crop sin(t). — L116
- `build_static_zoom` — (no docstring) — L135
- `lut3d_filter_arg` — Đường dẫn LUT an toàn cho filtergraph Windows. — L142
- `_read_cube` — (no docstring) — L163
- `separable_lutrgb` — LUT 3D mà mỗi kênh ra chỉ phụ thuộc kênh vào cùng tên → lutrgb 1D tương đương. — L180
- `append_lut_filters` — Thêm LUT hoặc eq. Trả nhãn dùng thực tế. — L217
- `grain_noise_alls` — (no docstring) — L234
- `append_inline_noise_grain` — Film grain qua noise= (ổn định). PNG trong assets dùng khi blend input riêng. — L243
- `grain_blend_fragment` — PNG blend tắt mặc định (movie loop dễ treo). Giữ API cho phase sau. — L255
- `bgm_volume` — (no docstring) — L261
- `dub_volume` — Âm lượng giọng Việt khi mix (VieNeu đã chuẩn hoá ~0.9 → boost vừa phải 1.25 tránh vỡ tiếng). — L268
- `list_frame_files` — PNG/WebP khung trong assets/overlays/frames (+ overlays gốc). — L277
- `pick_frame` — choice: off | auto | tên file | đường dẫn. — L312
- `prepare_frame_file` — Copy khung vào job → basename cho movie= (cwd=work_dir). — L342
- `brand_text_value` — (no docstring) — L360
- `normalize_brand_mode` — off | drift | corners | drift_seed. — L367
- `brand_enabled` — (no docstring) — L390
- `brand_xy_expr` — Biểu thức ffmpeg x/y cho chữ/logo brand. — L397
- `list_brand_logo_files` — (no docstring) — L430
- `pick_brand_logo` — (no docstring) — L462
- `prepare_brand_logo` — (no docstring) — L487
- `brand_drawtext_filter` — Chữ kênh với x/y expression đã chọn. — L503
- `apply_brand_overlay` — Ghép brand (chữ ± logo) vào filter chain. Trả (body, meta). — L527

### engines/script_lint.py
- `_fix_kin` — (no docstring) — L33
- `_fix_punct` — (no docstring) — L39
- `_fix_num` — (no docstring) — L43
- `_glossary_terms` — (no docstring) — L47
- `_variant_re` — (no docstring) — L57
- `_chi_majority` — (no docstring) — L65
- `autofix_rows` — (no docstring) — L76
- `lint_rows` — Đếm lỗi còn lại — không sửa. Dùng cho QA gate / agent / UI. — L107
- `run_lint` — Lint script.json của 1 job; fix=True thì autofix + ghi lại (+ SRT/display). — L138
- `write_display` — (no docstring) — L155

### engines/separate.py
- `_find_video` — (no docstring) — L39
- `_probe_duration` — Lấy thời lượng file media (giây) qua ffprobe. — L50
- `_update_sep_progress` — Cập nhật tiến độ vào stage 'separate' VÀ đồng bộ sang stage 'asr' nếu ASR đang chờ tách giọng. — L63
- `_extract_audio` — Tách audio GỐC chất lượng cao (stereo 44.1k) — khác audio.wav 16k mono của ASR. — L82
- `_run_demucs_on_file` — Chạy Demucs trên 1 file audio (ngắn hoặc 1 chunk) và trả về (no_vocals_wav, vocals_wav). — L100
- `_concat_wav_chunks` — Ghép các chunk WAV thành 1 file WAV hoàn chỉnh (dùng -rf64 auto để hỗ trợ >4GB cho phim dài). — L170
- `run_separate` — (no docstring) — L194
- `main` — (no docstring) — L360

### engines/series_glossary.py
- `_core_of` — (no docstring) — L22
- `series_key` — (no docstring) — L32
- `_path` — (no docstring) — L43
- `load` — (no docstring) — L48
- `_valid_char` — (no docstring) — L73
- `_merge_list` — top đè base theo key; giữ thứ tự: mục của top trước, mục chỉ có ở base sau. — L77
- `_zh` — (no docstring) — L93
- `_pron` — (no docstring) — L97
- `apply` — (no docstring) — L101
- `save_from` — (no docstring) — L124

### engines/sfx_lib.py
- `effect_volume` — (no docstring) — L46
- `music_volume` — (no docstring) — L53
- `voice_boost` — Hệ số nhân thêm lên RENDER_DUB_VOL, chỉ cho sfx_lib. — L60
- `model_dir` — (no docstring) — L69
- `lib_dir` — (no docstring) — L73
- `model_files` — (no docstring) — L77
- `_fstat` — (no docstring) — L84
- `separate_stream` — Tách theo khúc, nối crossfade tuyến tính ở vùng chồng. — L94
- `_cdx_fn` — (no docstring) — L126
- `separate` — Âm gốc (video/audio bất kỳ) → sfx_effect.flac + sfx_music.flac. — L151
- `window_features` — (rms_db, flux) mỗi cửa sổ win_s của stem nhạc (mono; flux tính ở ~11 kHz). — L196
- `_median` — (no docstring) — L214
- `classify` — Cửa sổ → đoạn {start, end, level}. Mức calm/mid/intense chia theo tam phân vị của chính phim. — L222
- `library` — {mức: [(đường dẫn, giây)]} từ assets/bgm_yt/manifest.json (+ file lạ trong thư mục mức). — L271
- `_probe` — (no docstring) — L282
- `plan_bgm` — Xếp bài cho từng đoạn → [{file, at, off, dur, fin, fout}] (giây). Đoạn 'none' để trống. — L291
- `_decode` — (no docstring) — L321
- `render_bgm` — Ghi dải nhạc dài `total` giây theo plan (từng khối, không giữ cả dải trong RAM). — L331
- `prepare` — (no docstring) — L372
- `run_subprocess` — Gọi prepare ở tiến trình con (nhả VRAM/RAM khi xong); on_line(dòng log) để cập nhật tiến độ. — L409
- `main` — (no docstring) — L426

### engines/split_parts.py
- `_is_disk_full_text` — (no docstring) — L36
- `free_bytes` — Dung lượng trống trên volume chứa `path` (tạo parent nếu chưa có). — L41
- `estimate_split_need_bytes` — Ước lượng chỗ cần cho split copy-mode (= gần bằng size nguồn + margin). — L50
- `assert_enough_space_for_split` — (no docstring) — L56
- `_unlink_quiet` — (no docstring) — L66
- `probe_duration` — Lấy thời lượng video tính bằng giây. — L74
- `calculate_part_plan` — Tính toán danh sách (start_sec, end_sec) cho từng part. — L90
- `find_best_cut_point` — Tìm điểm khoảng lặng (silence) gần nhất với target_cut_sec trong phạm vi ±search_radius_sec. — L111
- `compute_smart_plan` — Tính plan hoàn chỉnh có điểm cắt thông minh (tránh đứt câu thoại). — L152
- `split_video_to_parts` — Cắt video thành các part theo smart plan (lossless copy). — L194
- `_hardlink_alias` — Tạo alias cùng inode với primary. Không bao giờ copy2 (tránh nhân đôi GB). — L331
- `cleanup_split_parts_dir` — Xoá thư mục `_split_parts` dở (orphan GB sau fail / ENOSPC). — L361
- `merge_parts_to_full` — Nối danh sách các part đã render hoàn chỉnh thành 1 file full (lossless copy 30s). — L373
- `split_job_to_subjobs` — Tự động chia một job video dài thành các sub-jobs (Part 1, Part 2...). — L412
- `merge_job_parts` — Kiểm tra các sub-job của job_id, nếu tất cả đã render xong thì ghép thành output_full.mp4. — L576
- `is_split_subjob` — Part đã tách (…_p01) — không auto-split lần nữa. — L675
- `maybe_auto_split_job` — Tự detect thời lượng video sau khi có source: — L688
- `try_auto_merge_parent` — Sau khi một part mux xong: nếu mọi part done → merge output_full trên job cha. — L792
- `main` — (no docstring) — L818

### engines/subs.py
- `_plain_len` — (no docstring) — L27
- `_mask_number_dots` — Che dấu nghìn trong số để không bị tách câu tại «3.000» / «31,000». — L49
- `_unmask_number_dots` — (no docstring) — L55
- `glue_vi_names` — Dán NBSP trong tên riêng — không xuống dòng giữa «Thiên Lang Tinh». — L101
- `unglue_vi_names` — (no docstring) — L113
- `_is_compound_break` — True nếu cắt tại pos đang tách đôi compound (…tấn| công…). — L117
- `_snap_cut_to_vi_word` — Ưu tiên cắt tại khoảng trắng VI; không cắt giữa từ / giữa số / compound. — L131
- `_snap_cut_outside_number` — Đẩy điểm cắt ra ngoài token số (tránh «31.» + «000 tỷ»). — L154
- `split_text_by_punct` — Tách câu theo dấu câu. weak=True: mỗi mệnh đề sau ，、, là 1 đoạn (thoại TTS). — L165
- `_join_clause` — CJK dính liền; VI/Latin cần khoảng trắng («Đù,» + «thế…» → «Đù, thế…»). — L212
- `_is_punct_only` — (no docstring) — L222
- `_split_for_display` — Tách text cho sub: dấu câu -> dấu phẩy; hard=True thì cắt cứng phần còn dài. — L226
- `_slice_contiguous` — Cắt 1 chuỗi thành N đoạn liên tiếp theo trọng số — không trộn với câu khác. — L263
- `merge_tiny_segments` — Gộp mảnh ASR vụn: chỉ dấu câu, cắt giữa từ, clip < 0.45s quá ngắn. — L314
- `_merge_parts` — Gộp parts dư thành đúng n cụm (ghép các cụm ngắn nhất liên tiếp). — L360
- `_expand_parts` — Chia parts ít hơn n thành đủ n cụm. — L379
- `_align_zh_vi` — Căn số cụm zh/vi; ưu tiên zh làm mốc thời gian. — L397
- `_spread_time_pairs` — Chia [start,end] theo độ dài vi (fallback zh). — L410
- `_split_hard` — Cắt cứng theo từ (Việt) hoặc ký tự (CJK) khi không còn dấu câu. — L433
- `split_long_segments` — Tách câu quá dài / quá lâu thành nhiều đoạn; chia thời gian theo độ dài chữ. — L527
- `split_bilingual_rows` — Sau dịch ZH→VI: tách sub dài (CUT). Ưu tiên cắt theo VI rồi cắt ZH liền mạch. — L571
- `carry_tail_fragments` — «…sáu mươi đứa. Đúng,» + «cùng lên…» → mảnh đầu câu sau sang cue kế tiếp. — L727
- `merge_broken_vi_number_rows` — Gộp mảnh lệch số: «…31,» + «000 tỷ» / «当前血量31,» + «000亿» → 1 câu. — L755
- `heal_script_broken_numbers` — Gộp số gãy trên script (giữ i của câu đầu) — trả (rows_mới, số_cặp_đã_gộp). — L799
- `sub_split_cfg` — (no docstring) — L805
- `_merge_short_orphans` — Gộp đuôi ngắn («này?», «Tinh,») — không nuốt lại «nhiều.» / «trường,». — L813
- `wrap_subtitle_text` — Gói phụ đề tối đa max_lines dòng, mỗi dòng ≤ max_chars. — L857
- `_wrap_cfg` — (no docstring) — L942
- `expand_placed_with_display` — Tách mỗi câu TTS (script 1:1) theo mảnh CUT trong script.display (src_i). — L949
- `_maybe_wrap` — (no docstring) — L1017
- `fmt_ts` — Giây (float) -> 'HH:MM:SS,mmm' theo chuẩn SRT. — L1029
- `to_srt` — Đổ list câu ra chuỗi SRT. Bỏ câu rỗng, đánh số lại liên tục. — L1040
- `to_srt_fit` — SRT burn theo script + dur TTS gốc (KHÔNG biết đàn hồi assemble). — L1056
- `to_srt_placed` — SRT burn khớp giọng sau assemble_fit: dùng start/end thật trên dub_fit.wav. — L1084

### engines/title_mt.py
- `_has_cjk` — (no docstring) — L30
- `_load_cache` — (no docstring) — L34
- `_save_cache` — (no docstring) — L51
- `_gtx` — (no docstring) — L64
- `translate_one` — Dịch 1 title; không CJK → trả nguyên. — L87
- `translate_titles` — Dịch list {series_id?, title} → gắn title_vi. Dùng cache. — L103

### engines/translate.py
- `_tmodel` — TRANSLATE_MODEL đọc lúc gọi (server import module 1 lần — MODEL ở trên bị đóng băng). — L59
- `_rmodel` — (no docstring) — L64
- `_is_llama_local_model` — (no docstring) — L68
- `_meaning_rules` — Quy tắc chống dịch đen / lệch ngữ cảnh (lồng tiếng phim). — L84
- `_style_rules` — Quy tắc Manhua / short-drama: cứng Hán Việt + mềm hiện đại + xưng hô. — L147
- `_character_rules` — Chống nhầm nhân vật / sai giới tính khi dịch thoại. — L179
- `_is_ancient_fantasy_genre` — True khi phương án/genre thuộc tu tiên·cổ trang·wuxia·xianxia (không mixed đô thị). — L201
- `_is_mixed_genre` — (no docstring) — L225
- `_mixed_address_rules` — Đô thị dị năng + võ/KH: xưng hô hiện đại + cổ phong Hán Việt. — L239
- `_ancient_address_rules` — Chỉ inject khi genre tu tiên/cổ — không áp cho đô thị hiện đại. — L260
- `_translate_rules` — Gộp nghĩa + văn phong + nhân vật (+ xưng hô theo genre). — L281
- `_ocr_name_hints` — Tên/chữ trên hình từ ocr.json (nếu có) — gợi ý cho PLAN. — L290
- `_resolve_translate_mode` — Trả 'oneshot' | 'batch'. — L317
- `_has_cjk` — Còn ký tự Hán trong bản dịch = model dịch sót/hỏng (đặc biệt model nhỏ local). — L345
- `_salvage_mixed_vi` — Cứu VI lẫn Hán (vd «Đạt được 100% 增幅.») — không thì trả '' để vá lại. — L373
- `build_plan` — LLM đọc toàn transcript -> phương án dịch: nhân vật, thuật ngữ, XƯNG HÔ, PHÂN CẢNH, tone. — L420
- `_plan_block` — Đổ plan ra text nhét vào mọi prompt dịch. CHỐNG LỖI: model đôi khi trả — L588
- `_plan_block_for_qa` — Plan block gọn cho pronoun-QA / GPT vá đỏ — chỉ genre+style+pronouns. — L700
- `_resolve_scene_context` — Xác định phân cảnh hiện tại của lô câu thoại (Scene-based context injection). — L774
- `_norm_zh_cue` — Chuẩn hóa cue ZH để khớp lock (bỏ dấu câu/space). — L867
- `ensure_hard_terms` — Gắn seed chengyu/taunt vào glossary.terms (không đè bản tay đã có). — L875
- `hard_term_lock_map` — zh_norm → vi bắt buộc (từ glossary type chengyu/idiom/combat_taunt/lock + seed). — L925
- `apply_hard_term_locks` — Post-pass: cue ZH khớp lock → ghi đè VI (chuẩn, không phụ thuộc LLM). — L964
- `normalize_vi_thousands` — Dấu nghìn chuẩn Việt: 31 000 / 31,000 → 31.000. — L1011
- `apply_style_polish` — Post-pass deterministic: sửa calque / văn mẫu thường gặp (mixed short-drama). — L1027
- `_is_modernish_genre` — Đô thị / mixed / hiện đại — cấm Ta–Ngươi cổ. — L1278
- `_char_aliases` — vi_name_lower → {zh, vi, aliases…} để khớp tên trong câu. — L1302
- `_pronoun_pairs` — (no docstring) — L1320
- `_detox_modern_pronouns` — Ép Ta/Ngươi → Tôi/Cậu cho thoại đô thị (giữ «ông ta/cô ta/chúng ta»). — L1336
- `apply_pronoun_postpass` — Post-pass deterministic xưng hô — không phụ thuộc LLM nhớ ma trận. — L1362
- `_salvage_items` — Vớt từng object {"i":.., "vi":..} kể cả khi JSON TỔNG THỂ hỏng (model — L1428
- `translate_oneshot` — Dịch TOÀN BỘ danh sách câu trong 1 lần gọi LLM (llama-server ctx lớn). — L1453
- `translate_batch` — LƯỢT 1 — DỊCH NGHĨA KỊCH BẢN CHUẨN XÁC (Semantic Accuracy) theo Phân Cảnh (Scene) + Series Glossary. Trả {i: vi}. — L1521
- `_translate_safe` — Dịch 1 lô CÓ CHỐNG LỖI: nếu parse hỏng hoặc LLM nuốt câu, CHIA ĐÔI lô rồi thử lại. — L1596
- `review_batch` — LƯỢT 2 — BẢN ĐỊA HÓA LỜI THOẠI LỒNG TIẾNG & KHỚP NHỊP PHỤ ĐỀ (Voice Dubbing Localization). — L1624
- `run_review` — LƯỢT 2: soát bản dịch nháp (script.json) bằng model chính xác (minimax) rồi — L1697
- `count_script_missing` — Đếm câu trống trong script.json (nguồn sự thật cho UI / auto-vá). — L1894
- `_trivial_vi` — Câu chỉ cười/thán từ — không cần LLM (model hay trả lại chữ Hán → _has_cjk xoá). — L1906
- `_compress_zh_for_llm` — Rút chuỗi cười/spam trước khi gửi LLM (tránh timeout / trả Hán). — L1947
- `clean_zh_spam` — Rút 哈/呃/嗯/啊 spam + cụm chữ lặp (区域的区域的…) từ ASR. — L1952
- `run_translate` — (no docstring) — L1989
- `main` — (no docstring) — L2502

### engines/translate_alts.py
- `_heuristic_ambiguous` — Trả lý do ngắn nếu câu nên đưa phương án; None = bỏ qua. — L35
- `_alts_batch` — Trả {i: {alts[], pick, reason}} — tối ưu theo ngữ cảnh + văn phong. — L65
- `run_ambiguous_alts` — Quét script → vi_alts.json (phương án tối ưu theo ngữ cảnh + văn phong). — L164
- `analyze_pack_report` — Checklist pack Context Studio có đủ để dịch chunk không. — L305
- `main` — (no docstring) — L353

### engines/vram.py
- `_ollama_loaded` — (no docstring) — L14
- `_stop_ollama` — (no docstring) — L27
- `_empty_torch` — Xả cache CUDA — KHÔNG synchronize (dễ treo vô hạn khi GPU kẹt). — L38
- `free_gpu_vram` — Stop Ollama + xả torch cache. An toàn gọi nhiều lần, kể cả không có GPU. — L56
