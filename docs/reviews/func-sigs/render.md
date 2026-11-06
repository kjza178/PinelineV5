# Render / hardsub / filtergraph

- **Module:** `engines/render.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 72

## Signatures

### `_ass_colour` — L64

```python
def _ass_colour(val: str, default: str='&H00FFFFFF') -> str
```

**Doc:** #RRGGBB hoặc &HAABBGGRR -> ASS.

### `_sum_expr` — L79

```python
def _sum_expr(terms: list[str]) -> str
```

**Doc:** a+b+…; ffmpeg chỉ nhận ≤100 hạng tử cộng phẳng → dài thì gom ngoặc cân bằng.

### `_pw_expr` — L92

```python
def _pw_expr(ends: list[float], vals: list) -> str
```

**Doc:** Theo t: vals[i] với i nhỏ nhất có t < ends[i] (ends tăng dần, len = len(vals) - 1), hết → vals[-1].

### `_censor_expr` — L109

```python
def _censor_expr(work_dir: Path | None=None) -> str | None
```

**Doc:** enable=... cho blur cảnh nhạy cảm. Config CENSOR_RANGES='12-18,90-102' (giây)

### `_probe_dur` — L136

```python
def _probe_dur(path: Path) -> float
```

**Doc:** Độ dài video (giây) để tính % render.

### `_ffmpeg_progress` — L152

```python
def _ffmpeg_progress(cmd: list, total: float, m: Manifest, cwd: str | Path | None=None, lo: float=0.0, hi: float=100.0) -> tuple[int, str]
```

**Doc:** Chạy ffmpeg + đọc -progress -> cập nhật % vào manifest (mux). Trả (mã, lỗi).

### `_no_power_throttle` — L286

```python
def _no_power_throttle(pid: int) -> None
```

**Doc:** Tắt EcoQoS của Windows cho ffmpeg con (tránh bị dồn sang E-core khi console thu nhỏ).

### `_mp4_video_stts` — L309

```python
def _mp4_video_stts(video: Path) -> tuple[int, list[int]] | None
```

**Doc:** (timescale, [count, delta, ...]) từ box stts của track video mp4/mov.

### `_probe_pts` — L365

```python
def _probe_pts(video: Path, a: float, b: float) -> list[float]
```

### `squeeze_fixes` — L379

```python
def squeeze_fixes(video: Path) -> list[dict]
```

**Doc:** Đoạn mốc thời gian bị nén khi gộp tập khác fps: N khung dài ~0 rồi 1 khung dài hàng phút.

### `squeeze_setpts` — L436

```python
def squeeze_setpts(fixes: list[dict]) -> str
```

**Doc:** setpts trải lại các đoạn bị nén (rỗng nếu không có).

### `_cfg_num` — L450

```python
def _cfg_num(key: str, default: str) -> float
```

### `chunk_plan` — L458

```python
def chunk_plan(total: float) -> tuple[float, int]
```

**Doc:** (giây mỗi khúc, số khúc chạy cùng lúc). RENDER_CHUNK_SEC=0 hoặc RENDER_CHUNK_PAR<2 → 1 lượt.

### `chunk_cuts` — L468

```python
def chunk_cuts(video: Path, total: float, sec: float, avoid: list[dict]) -> list[float]
```

**Doc:** Điểm cắt mỗi ~sec giây, nằm GIỮA 2 khung liền nhau (không trùng mốc khung → không lặp/mất khung).

### `_run_chunked` — L489

```python
def _run_chunked(video: Path, work_dir: Path, graph: str, venc: list[str], pre_in: list[str], cuts: list[float], total: float, mixed: Path, abit: str, out_tmp: Path, m: Manifest, lo: float, par: int=3) -> tuple[int, str]
```

**Doc:** Render video theo khúc (giữ mốc gốc), tối đa `par` khúc chạy cùng lúc, ghép copy, gắn audio 1 lần.

### `_encoder_pref` — L687

```python
def _encoder_pref() -> str
```

### `_nvenc_state` — L700

```python
def _nvenc_state() -> dict
```

### `_nvenc_save` — L711

```python
def _nvenc_save(d: dict) -> None
```

### `_want_nvenc` — L718

```python
def _want_nvenc() -> bool
```

### `_nvenc_mark_ok` — L734

```python
def _nvenc_mark_ok() -> None
```

### `_nvenc_mark_fail` — L738

```python
def _nvenc_mark_fail(err: str) -> None
```

### `_attach_filter_complex` — L756

```python
def _attach_filter_complex(cmd: list[str], graph: str, work_dir: Path) -> Path
```

**Doc:** Ghi filtergraph ra file — tránh cắt cmdline Windows (~8191 ký tự).

### `_ff_input` — L764

```python
def _ff_input(path: Path | str, work_dir: Path) -> str
```

**Doc:** Đường dẫn -i khi ffmpeg cwd=work_dir: file trong job → tên/relative; ngoài → absolute.

### `_x264_cmd` — L774

```python
def _x264_cmd(cmd: list[str]) -> list[str]
```

**Doc:** Đổi lệnh nvenc → libx264 (bỏ flag chỉ GPU).

### `normalize_vbitrate` — L791

```python
def normalize_vbitrate(v: str | None, W: int=1920, H: int=1080) -> tuple[str, str]
```

**Doc:** Chuẩn hoá bitrate H264: trả (vbit, buf). Cho phép 2M | 4M | 8M.

### `_find_video` — L813

```python
def _find_video(work_dir: Path) -> Path | None
```

### `_size` — L824

```python
def _size(video: Path) -> tuple[int, int]
```

### `_fps` — L833

```python
def _fps(video: Path) -> float
```

### `_esc` — L847

```python
def _esc(t: str) -> str
```

**Doc:** Escape text cho drawtext.

### `_map_pt` — L853

```python
def _map_pt(fx: float, fy: float, zoom: float) -> tuple[float, float]
```

**Doc:** Toạ độ fraction (0-1) sau khi zoom+crop giữa.

### `_map_box` — L859

```python
def _map_box(x0: float, y0: float, x1: float, y1: float, zoom: float, pad: float=0.0) -> tuple[float, float, float, float] | None
```

**Doc:** Map hộp nguồn → sau zoom/crop; None nếu gần như bị crop hết.

### `_flip_box` — L881

```python
def _flip_box(x0: float, y0: float, x1: float, y1: float, hflip: bool, vflip: bool) -> tuple[float, float, float, float]
```

### `_default_wm_corners` — L890

```python
def _default_wm_corners() -> list[dict]
```

**Doc:** Fallback góc kênh khi OCR không bắt được logo hình (ô nhỏ, chỉ mép).

### `_uploader_hint` — L921

```python
def _uploader_hint(work_dir: Path) -> str
```

### `_is_wm_text` — L929

```python
def _is_wm_text(txt: str, uploader: str='') -> bool
```

### `_wm_quadrant` — L944

```python
def _wm_quadrant(cx: float, cy: float) -> str | None
```

### `_expand_logo_pad` — L957

```python
def _expand_logo_pad(q: str, x0, y0, x1, y1) -> tuple[float, float, float, float]
```

**Doc:** OCR chữ → snap nhẹ về mép góc; giữ kích thước gần bbox, cap nhỏ.

### `_cap_wm_frac` — L986

```python
def _cap_wm_frac(x0: float, y0: float, x1: float, y1: float, q: str='') -> tuple[float, float, float, float]
```

**Doc:** Giới hạn hộp che sau map — không cho phình quá mép góc.

### `_wm_sample_times` — L1005

```python
def _wm_sample_times(full_dur: float) -> tuple[list[float], float]
```

**Doc:** Mốc giây lấy mẫu watermark trên TOÀN bộ video (không chỉ 3 phút đầu).

### `_extract_wm_frames` — L1032

```python
def _extract_wm_frames(video: Path, out_dir: Path, times: list[float]) -> list[tuple[Path, float]]
```

**Doc:** Seek từng mốc → 1 frame JPEG. Nhanh hơn decode cả file.

### `_merge_wm_timeline` — L1055

```python
def _merge_wm_timeline(hits: list[tuple[float, str, float, float, float, float, str]], stride: float, full_dur: float, uploader: str) -> list[dict]
```

**Doc:** Gộp hit (t,q,x0,y0,x1,y1,txt) → [{t0,t1,x,y,w,h}, …] theo góc + thời gian.

### `_parse_wm_cache` — L1129

```python
def _parse_wm_cache(raw: dict) -> list
```

**Doc:** Đọc cache: list dict timed, hoặc list [x,y,w,h] cũ → coi full video.

### `detect_overlays` — L1150

```python
def detect_overlays(work_dir, n_frames: int=40, force: bool=False)
```

**Doc:** Dò hardsub (đầu phim) + watermark THEO THỜI GIAN trên cả video.

### `detect_hardsub_band` — L1286

```python
def detect_hardsub_band(work_dir, n_frames: int=40, force: bool=False)
```

**Doc:** Tương thích cũ: chỉ trả band.

### `_hs_cluster_band` — L1295

```python
def _hs_cluster_band(rows: list[tuple]) -> tuple[float, float]
```

**Doc:** (y0,y1) của 1 cụm vị trí — bỏ 5% ngoại lai mỗi phía khi đủ mẫu.

### `detect_hardsub_track` — L1303

```python
def detect_hardsub_track(work_dir, force: bool=False) -> dict | None
```

**Doc:** Dò toạ độ hardsub THEO THỜI GIAN trên toàn video (file merge đổi vị trí giữa các tập).

### `_even` — L1522

```python
def _even(n: int | float) -> int
```

### `_rounded_bar_alpha` — L1526

```python
def _rounded_bar_alpha(w: int, h: int, r: int, alpha: float) -> str
```

**Doc:** Biểu thức geq alpha cho hình chữ nhật bo góc (0–255).

### `_boxblur_r` — L1544

```python
def _boxblur_r(desired: int, w: int, h: int, sub: int=0) -> int
```

**Doc:** Radius boxblur hợp lệ: ffmpeg yêu cầu 2*r < min(w,h) của plane.

### `_safe_crop` — L1554

```python
def _safe_crop(w: int, h: int, x: int, y: int) -> str
```

**Doc:** crop ffmpeg an toàn khi iw/ih đổi giữa chừng (biểu thức min).

### `_hardsub_bar_filter` — L1563

```python
def _hardsub_bar_filter(bw: int, bh: int, bx: int, by: int) -> str
```

**Doc:** Che hardsub: 1× boxblur + lớp đen geq bo góc (không desat).

### `_hardsub_cover_fullw` — L1596

```python
def _hardsub_cover_fullw() -> bool
```

**Doc:** Luôn phủ hết ngang khi che hardsub — OCR x0/x1 thường chỉ ~50% giữa → chữ Trung lòi 2 mép.

### `_hardsub_track_boxes` — L1602

```python
def _hardsub_track_boxes(track: dict, W: int, H: int, hflip: bool, vflip: bool) -> list[tuple[int, int, int, int, list, float]]
```

**Doc:** Dải hardsub (tỉ lệ nguồn) → ô pixel trên canvas TRƯỚC zoom: (bx,by,bw,bh,ranges,tổng giây).

### `_stretch_cfg` — L1660

```python
def _stretch_cfg() -> tuple[float, float, bool]
```

**Doc:** (sigma ngang, sigma dọc, phủ hết bề ngang) cho kiểu che stretch.

### `_stretch_chain` — L1671

```python
def _stretch_chain(tag: str, bx: int, bw: int, bh: int, ty: str, oy: str, en: str) -> str
```

**Doc:** Che hardsub kiểu kéo giãn: trung bình vài hàng ngay trên ô, kéo dọc phủ ô rồi làm mềm

### `_stretch_track_filter` — L1685

```python
def _stretch_track_filter(boxes: list[tuple[int, int, int, int, list, float]], W: int, H: int) -> str
```

**Doc:** Kiểu stretch cho mọi dải: khoảng nào nhiều dải cùng hiện thì phủ 1 ô gộp (không chồng 2 lớp).

### `_hardsub_track_filter` — L1722

```python
def _hardsub_track_filter(boxes: list[tuple[int, int, int, int, list, float]], W: int, H: int) -> str
```

**Doc:** Che đúng ô hardsub theo thời gian (không lớp đen).

### `_srt_to_ass_margins` — L1759

```python
def _srt_to_ass_margins(srt: Path, out: Path, W: int, H: int, mv_at) -> int
```

**Doc:** SRT → ASS với MarginV riêng từng câu (mv_at(t_giữa_câu) → px). Trả số câu.

### `_hardsub_track_filter_dyn` — L1803

```python
def _hardsub_track_filter_dyn(boxes: list[tuple[int, int, int, int, list, float]], W: int, H: int, margin: int) -> str
```

**Doc:** Nhiều dải → 1 chuỗi blur chính + 1 chuỗi phụ (chỉ bật lúc 2 dải chồng nhau).

### `resolve_canvas` — L1867

```python
def resolve_canvas(src_w: int, src_h: int, resolution: str='source') -> tuple[int, int, str]
```

**Doc:** Chọn khung xuất: source = giữ gốc; 1080/1k = Full HD (giữ tỉ lệ, tối đa 1920×1080).

### `_parse_flip` — L1880

```python
def _parse_flip(flip: str | None) -> tuple[bool, bool]
```

### `build_video_filter` — L1891

```python
def build_video_filter(W: int, H: int, zoom: float, ocr: list[dict], srt: Path | None, hardsub_blur: bool, band: tuple | None=None, src_w: int | None=None, src_h: int | None=None, flip: str | None=None, censor_expr: str | None=None, wm_fracs: list | None=None, motion: bool=True, lut: bool=True, grain: str='weak', fps: float=25.0, work_dir: Path | None=None, brand: bool | None=None, brand_text: str | None=None, brand_mode: str | None=None, brand_logo: str | None=None, frame: str | None=None, hs_track: dict | None=None) -> tuple[str, dict]
```

**Doc:** Trả (filter_comma_chain_without_final_vout, meta).

### `_pick_dub` — L2228

```python
def _pick_dub(work_dir: Path) -> Path | None
```

### `_normalize_audio_mode` — L2239

```python
def _normalize_audio_mode(audio_mode: str | None, have_nv: bool=True) -> str
```

### `_uses_sidechain` — L2252

```python
def _uses_sidechain(mode: str) -> bool
```

**Doc:** duck / duck_bgm / sfx_lib dùng sidechaincompress — KHÔNG chạy cùng encode video

### `_stage_note` — L2258

```python
def _stage_note(m: Manifest)
```

**Doc:** Callback ghi dòng log tiến trình con vào cur_text của stage render (thưa ≥2 s).

### `_ensure_mixed_audio` — L2276

```python
def _ensure_mixed_audio(work_dir: Path, video: Path, dub: Path | None, no_vocals: Path, vocals: Path, audio_mode: str, voice_vol: float, orig_vol: float, total: float, m: Manifest, force: bool=False) -> tuple[Path, str]
```

**Doc:** Pass 1: mixed_audio.wav (audio-only + sidechain). Trả (path, used_mode).

### `_mix_signature` — L2349

```python
def _mix_signature(cmd: list[str], af: str | None, total: float, work_dir: Path) -> dict
```

**Doc:** Filter + (đường dẫn, size, mtime) mọi input -i + độ dài — đổi thì phải trộn lại.

### `_write_mix_signature` — L2366

```python
def _write_mix_signature(path: Path, sig: dict) -> None
```

### `_build_audio_filter` — L2375

```python
def _build_audio_filter(cmd: list, work_dir: Path, dub: Path | None, no_vocals: Path, vocals: Path, audio_mode: str, voice_vol: float, orig_vol: float) -> tuple[str | None, str]
```

**Doc:** Dựng filter audio + THÊM input vào cmd. Trả (filter, tên_chế_độ_thực).

### `run_render` — L2518

```python
def run_render(work_dir: str | Path, zoom: float=1.12, add_sub: bool=True, hardsub_blur: bool=True, out_name: str='output.mp4', force: bool=False, audio_mode: str | None=None, voice_vol: float=0.2, orig_vol: float=0.6, resolution: str='source', flip: str='', motion: bool=True, lut: bool=True, grain: str='weak', brand: bool | None=None, brand_text: str | None=None, brand_mode: str | None=None, brand_logo: str | None=None, frame: str | None=None, vbitrate: str | None=None, speed_factor: float | None=None) -> dict
```

**Callers (spine):** server._do_render (queue 1-click; not run_mux)

### `main` — L3003

```python
def main(argv=None)
```
