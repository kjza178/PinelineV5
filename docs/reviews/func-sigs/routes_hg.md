# HTTP Hongguo routes

- **Module:** `http_routes/routes_hg.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 34

## Signatures

### `_hg_base` — L51

```python
def _hg_base(override: str | None=None) -> str
```

**Doc:** Luôn DEFAULT_BASE: `base` từ client từng cho server gửi token Hongguo tới URL bất kỳ.

### `_hg_err` — L57

```python
def _hg_err(e: Exception)
```

### `hg_ping` — L69

```python
def hg_ping(base: str | None=None)
```

### `hg_search` — L77

```python
def hg_search(q: str, base: str | None=None, expand: bool=True)
```

### `hg_resolve` — L90

```python
def hg_resolve(body: dict | None=None, base: str | None=None)
```

**Doc:** Dán link Hongguo / series_id → meta (khi search không ra, vd. 第十一季).

### `hg_baike_search` — L107

```python
def hg_baike_search(q: str, base: str | None=None)
```

**Doc:** Nhận diện trên duanjubaike → danh sách version → match Hongguo từng cái.

### `hg_baike_info` — L122

```python
def hg_baike_info(series_id: str | None=None, title: str | None=None, translate: bool=True)
```

**Doc:** Chi tiết sâu từ duanjubaike (intro/tags/score/同系列).

### `hg_web_search` — L169

```python
def hg_web_search(q: str)
```

**Doc:** Scrape hongguoduanju.com/search — dùng khi API Downloader sót mùa.

### `hg_series` — L192

```python
def hg_series(series_id: str, base: str | None=None)
```

### `hg_status` — L203

```python
def hg_status(base: str | None=None)
```

### `hg_cancel` — L214

```python
def hg_cancel(body: S.HgBaseIn | None=None)
```

### `hg_submit` — L225

```python
def hg_submit(body: S.HgSubmitIn)
```

### `hg_rank` — L236

```python
def hg_rank(category: str='all', board: str='recommend', offset: int=0, size: int=100, base: str | None=None)
```

**Doc:** Bảng hot giống app Downloader (Leaderboard /dl/rank).

### `hg_rank_episodes` — L255

```python
def hg_rank_episodes(body: HgRankEpsIn)
```

**Doc:** Lazy fill episode_cnt cho series trên bảng hot.

### `hg_translate_titles` — L271

```python
def hg_translate_titles(body: HgTranslateTitlesIn)
```

**Doc:** Dịch thô title Trung→Việt (Google gtx + cache) — chỉ để duyệt Hongguo.

### `hg_library` — L283

```python
def hg_library(base: str | None=None)
```

### `hg_preview` — L294

```python
def hg_preview(series_id: str, ep: int=1, fresh: int=0, base: str | None=None)
```

**Doc:** URL MP4 tập miễn phí (hongguoduanju /dl/preview) — không cần tải về.

### `hg_library_preview` — L310

```python
def hg_library_preview(name: str, base: str | None=None)
```

**Doc:** Stream video thư viện Hongguo (merged hoặc tập đầu) — tua được (Range).

### `hg_img` — L335

```python
def hg_img(url: str, base: str | None=None)
```

**Doc:** Proxy ảnh cover qua Hongguo /img (HEIC → JPEG) — kèm UI token.

### `hg_poster` — L352

```python
def hg_poster(name: str, base: str | None=None)
```

**Doc:** Poster thư viện: /dl/poster (auth) hoặc file local poster.jpg.

### `hg_merge` — L369

```python
def hg_merge(body: S.HgMergeIn)
```

**Doc:** Enqueue merge tuần tự (Hongguo chỉ chạy 1 merge / lúc).

### `hg_merge_queue` — L381

```python
def hg_merge_queue(base: str | None=None)
```

### `hg_merge_queue_clear` — L387

```python
def hg_merge_queue_clear()
```

### `hg_library_open` — L393

```python
def hg_library_open(body: dict | None=None)
```

### `hg_library_delete` — L403

```python
def hg_library_delete(body: dict | None=None)
```

### `hg_library_update` — L416

```python
def hg_library_update(body: dict | None=None)
```

### `hg_seasons_decline` — L429

```python
def hg_seasons_decline(body: dict | None=None)
```

### `meta_generate` — L443

```python
def meta_generate(body: dict)
```

### `meta_generate_title` — L462

```python
def meta_generate_title(body: dict)
```

**Doc:** Sinh tiêu đề YouTube (port từ V2) — giữ nguyên meta/ai-image + meta/baike của V4.

### `meta_thumbnail` — L493

```python
def meta_thumbnail(body: dict)
```

### `meta_thumbnail_get` — L523

```python
def meta_thumbnail_get(file: str)
```

### `meta_series_info` — L535

```python
def meta_series_info(job_id: str='')
```

### `meta_ai_image` — L552

```python
def meta_ai_image(body: dict)
```

### `meta_baike` — L585

```python
def meta_baike(q: str='', title: str='')
```
