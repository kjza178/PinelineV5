# Meta studio

- **Module:** `agents/meta_studio.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 30

## Signatures

### `to_series_slug` — L30

```python
def to_series_slug(text: str) -> str
```

**Doc:** Chuyển tên series sang slug không dấu (vd: 'Sinh Tồn Sa Mạc' -> 'sinh_ton_sa_mac').

### `clean_series_name` — L42

```python
def clean_series_name(name: str, fallback: str='') -> str
```

**Doc:** Làm sạch tên series, loại bỏ toàn bộ chữ Hán, số phần P1/P2 thừa, và ký tự thừa.

### `hooks_from_series_title` — L78

```python
def hooks_from_series_title(title_vi: str, title_zh: str='') -> list[str]
```

**Doc:** Tách hook 2 dòng từ tên phim thật — không bịa cụm sáo rỗng.

### `_hook_anchored_to_title` — L115

```python
def _hook_anchored_to_title(hook: str, title_vi: str) -> bool
```

**Doc:** ≥75% token (≥3 ký tự) của hook phải nằm trong tên phim — chặn bịa «ẨN NHẪN».

### `sanitize_hook_texts` — L125

```python
def sanitize_hook_texts(hooks: list | None, title_vi: str='', title_zh: str='') -> list[str]
```

**Doc:** Loại hook sáo / trống / không neo tên phim; fallback tách từ tên phim.

### `pick_badge_text` — L150

```python
def pick_badge_text(raw: str | None='', *, job_id: str='', title_vi: str='') -> str
```

**Doc:** Badge góc trên: chỉ NEW hoặc HOT — không dùng «TRỌN BỘ THUYẾT MINH».

### `vi_to_image_latin` — L164

```python
def vi_to_image_latin(text: str) -> str
```

**Doc:** Bỏ dấu tiếng Việt → LATIN HOA để model ảnh ít vỡ chữ (₫/ơ/ệ hay bị gen sai).

### `build_master_image_prompt` — L181

```python
def build_master_image_prompt(*, title_vi: str='', title_zh: str='', story_moment: str='', visual_dna: str='', palette: str='', layout: str='', emotional_trigger: str='', hook_texts: list | None=None, badge_text: str='NEW', sub_text: str='', font_material: str='') -> str
```

**Doc:** Prompt ảnh AI: scene + chữ 3D LATIN (không dấu) — giảm gen sai chữ Việt có dấu.

### `finalize_thumb_meta_fields` — L243

```python
def finalize_thumb_meta_fields(data: dict, title_vi: str='', title_zh: str='', job_id: str='') -> dict
```

**Doc:** Sanitize hook + badge NEW/HOT; dựng lại master_image_prompt (AI vẽ chữ, không Pillow).

### `get_series_key` — L294

```python
def get_series_key(job_id: str) -> tuple[str, str]
```

**Doc:** Trả về (series_key, series_display_name).

### `get_series_meta` — L332

```python
def get_series_meta(series_key: str, series_name: str='') -> dict | None
```

**Doc:** Lấy metadata đã lưu của series (hỗ trợ tra cứu chéo qua group_id hoặc tên series).

### `save_series_meta` — L373

```python
def save_series_meta(series_key: str, data: dict, series_name: str='') -> None
```

**Doc:** Lưu metadata dùng chung cho cả series (lưu cả group_id và slug tên bộ).

### `get_series_thumbnail` — L390

```python
def get_series_thumbnail(series_key: str, series_name: str='') -> Path | None
```

**Doc:** Lấy đường dẫn ảnh thumbnail dùng chung của series.

### `save_series_thumbnail` — L429

```python
def save_series_thumbnail(series_key: str, src_path_or_bytes, series_name: str='') -> Path
```

**Doc:** Lưu ảnh thumbnail mẫu của cả series thành series_{series_key}.jpg (và bản alias slug).

### `_build_fallback_part_meta` — L447

```python
def _build_fallback_part_meta(clean_series: str, season: int, episode_info: str='', base_tags: list=None) -> dict
```

**Doc:** Tạo bộ Title & Description fallback đầy đủ 4 khối chuẩn YouTube SEO khi không kết nối được LLM.

### `get_film_story_info` — L515

```python
def get_film_story_info(job_id: str='', title_zh: str='', title_vi: str='', summary: str='', episode_info: str='') -> dict
```

**Doc:** Trích xuất thông tin Tên gốc tiếng Trung, Tên tiếng Việt và Tóm tắt Cốt truyện chuẩn (Baike / Intro / Desc)

### `generate_youtube_titles` — L626

```python
def generate_youtube_titles(series_name: str, season: int=1, episode_info: str='', summary: str='', job_id: str='', tone: str='', count: int=5, title_zh: str='') -> dict[str, Any]
```

**Doc:** Gọi LLM sinh danh sách 5 Tiêu Đề YouTube kịch tính theo phong cách Hán Việt chuẩn,

### `generate_title_only` — L786

```python
def generate_title_only(series_name: str, season: int=1, episode_info: str='', summary: str='', job_id: str='', title_zh: str='') -> str
```

**Doc:** Gọi LLM sinh 1 Tiêu Đề YouTube kịch tính, bám sát nội dung thực tế của tập.

### `generate_part_metadata` — L792

```python
def generate_part_metadata(series_name: str, season: int=1, episode_info: str='', shared_meta: dict | None=None, job_id: str='', summary: str='', title_zh: str='') -> dict
```

**Doc:** Sinh TITLE và DESCRIPTION chuẩn SEO cho từng Phần của Series khi dùng chung Thumbnail:

### `_clean_json_response` — L921

```python
def _clean_json_response(raw: str) -> dict
```

**Doc:** Bóc tách và tự động sửa lỗi JSON bị cắt cụt (truncated) từ phản hồi LLM.

### `_get_chatgpt_token` — L989

```python
def _get_chatgpt_token() -> str
```

**Doc:** Đọc Access Token của ChatGPT từ data/chatgpt_token.txt hoặc biến môi trường.

### `extract_job_summary` — L1000

```python
def extract_job_summary(job_id: str, max_chars: int=5500) -> str
```

**Doc:** Trích xuất kịch bản thực tế từ phụ đề tiếng Việt (sub.vi.srt / script.json) trải đều 6 giai đoạn

### `_normalize_ref_jpeg` — L1096

```python
def _normalize_ref_jpeg(raw_bytes: bytes, max_dim: int=1024) -> bytes | None
```

**Doc:** Chuẩn hoá ảnh tham chiếu (Poster hoặc Frame) về RGB JPEG <= 1024px để gửi lên Aurora /v1/images/edits.

### `_extract_best_video_frame` — L1115

```python
def _extract_best_video_frame(video_path: Path) -> bytes | None
```

**Doc:** Trích xuất khung hình sắc nét và giàu chi tiết nhất từ video làm ảnh tham chiếu nhân vật.

### `get_job_reference_images` — L1157

```python
def get_job_reference_images(job_id: str='', poster_name: str='') -> list[bytes]
```

**Doc:** Lấy danh sách ảnh gốc tham chiếu (Poster gốc + Khung hình sắc nét trong phim) của Job

### `_call_chatgpt` — L1232

```python
def _call_chatgpt(messages: list[dict], model: str='gpt-5-6') -> str
```

**Doc:** Gọi LLM qua Aurora / Chat2Api chạy trên Raspberry Pi 5.

### `_decode_aurora_image_response` — L1292

```python
def _decode_aurora_image_response(resp_json: dict, timeout: int=60) -> bytes | None
```

**Doc:** Giải mã ảnh từ phản hồi của Aurora (/v1/images/edits hoặc /v1/images/generations).

### `generate_ai_image` — L1309

```python
def generate_ai_image(prompt: str, size: str='1024x1024', timeout: int=150, ref_images: list[bytes] | bytes | None=None, job_id: str='', poster_name: str='') -> bytes | None
```

**Doc:** Gọi Aurora trên Pi 5 để sinh ảnh Thumbnail 16:9 chất lượng cao:

### `generate_metadata` — L1436

```python
def generate_metadata(title_vi: str='', title_zh: str='', info_text: str='', prompt_guide: str='', tone: str='giật gân, kịch tính', job_id: str='') -> dict
```

**Doc:** Dùng ChatGPT (qua Pi 5 với GPT-5.6 Luna mới nhất) hoặc Local LLM đọc Tên gốc & Cốt truyện Baike chuẩn

### `create_thumbnail` — L1679

```python
def create_thumbnail(poster_source: str | Path | bytes | Image.Image, hook_text_1: str='', hook_text_2: str='', badge_text: str='NEW', sub_text: str='', bg_frame_source: str | Path | bytes | Image.Image | None=None, style: str='fire_gold', out_filename: str | None=None, include_poster: bool=True) -> Path
```

**Doc:** Tạo ảnh Thumbnail 16:9 (1280x720) — legacy Pillow (auto-publish không dùng; AI typography chính).
