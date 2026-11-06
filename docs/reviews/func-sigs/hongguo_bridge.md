# Hongguo library bridge

- **Module:** `agents/hongguo_bridge.py`
- **Date:** 2026-11-06
- **Source:** AST extract (`scripts/_tmp_extract_sigs.py`)
- **Count:** 84 signatures in this doc

## Signatures

### `_save_merge_state` — L67

```python
def _save_merge_state() -> None
```

**Doc:** Gọi khi đang giữ _merge_lock.

### `_load_merge_state` — L82

```python
def _load_merge_state() -> None
```

### `_set_phase` — L106

```python
def _set_phase(name: str | None, phase: str='', pct: float | None=None) -> None
```

### `season_stem` — L121

```python
def season_stem(title: str) -> str
```

**Doc:** Bỏ hậu tố mùa để gom series cùng tên gốc.

### `franchise_core` — L136

```python
def franchise_core(title: str) -> str
```

**Doc:** Lấy tên thương hiệu/series chuẩn để nhóm mùa chính xác mà không gộp nhầm thể loại (như 高武：, 游戏入侵：).

### `_parse_cn_int` — L147

```python
def _parse_cn_int(s: str) -> int | None
```

### `season_timeline_key` — L167

```python
def season_timeline_key(title: str, series_id: str | None=None) -> tuple
```

**Doc:** Thứ tự phát hành ≈ series_id (snowflake). Phụ: cung/第N季 để ổn định khi thiếu id.

### `order_franchise_items` — L188

```python
def order_franchise_items(items: list[dict]) -> list[dict]
```

**Doc:** Sort theo thời gian phát hành (series_id) + gắn SS1→SSN.

### `web_search_hongguoduanju` — L271

```python
def web_search_hongguoduanju(q: str, timeout: float=20) -> list[dict]
```

**Doc:** Search trên hongguoduanju.com — thường ra đủ 第N季 mà /dl/search sót.

### `_ingest_web_into` — L334

```python
def _ingest_web_into(by_id: dict[str, dict], q: str, core_filter: str | None=None) -> int
```

**Doc:** Ingest web results; nếu có core_filter chỉ giữ title cùng thương hiệu.

### `web_expand_queries` — L363

```python
def web_expand_queries(q: str) -> list[str]
```

**Doc:** Query web tối thiểu nhưng phủ cao: exact + stem + vài mốc mùa.

### `web_expand_into` — L389

```python
def web_expand_into(by_id: dict[str, dict], q: str, workers: int=6) -> int
```

**Doc:** Chạy song song vài web search → gộp vào by_id (lọc theo core).

### `_load_title_cache` — L419

```python
def _load_title_cache() -> dict
```

### `_save_title_cache` — L437

```python
def _save_title_cache(data: dict) -> None
```

### `lookup_series` — L447

```python
def lookup_series(series_id: str, base: str=DEFAULT_BASE) -> dict
```

**Doc:** Lấy meta từ series_id (khi search không ra).

### `resolve_text` — L463

```python
def resolve_text(text: str, base: str=DEFAULT_BASE) -> dict
```

**Doc:** Parse link/share → series. Nhận URL detail/player hoặc series_id thuần.

### `_cache_put` — L496

```python
def _cache_put(r: dict) -> None
```

### `_fill_missing_from_cache` — L511

```python
def _fill_missing_from_cache(by_id: dict[str, dict], stem: str, base: str) -> None
```

**Doc:** Với stem gốc, dò cache/seed cho 第1–15季 nếu search bỏ sót.

### `expand_queries` — L549

```python
def expand_queries(q: str) -> list[str]
```

**Doc:** Sinh thêm query để bắt mùa đổi tên (灵界篇/仙界篇…).

### `_base_port` — L579

```python
def _base_port(base: str) -> str
```

### `_read_process_env_win` — L589

```python
def _read_process_env_win(pid: int) -> dict[str, str]
```

**Doc:** Đọc môi trường process khác (x64) qua PEB — lấy HG_UI_TOKEN.

### `_hongguo_pids` — L645

```python
def _hongguo_pids() -> list[int]
```

**Doc:** PID process Hongguo Downloader (pythonw trong thư mục cài đặt).

### `discover_ui_token` — L663

```python
def discover_ui_token(force: bool=False) -> str | None
```

**Doc:** Lấy HG_UI_TOKEN: env Pineline → cache → env process Downloader.

### `_auth_headers` — L696

```python
def _auth_headers(base: str) -> dict[str, str]
```

### `_is_ui_auth_error` — L707

```python
def _is_ui_auth_error(detail: Any) -> bool
```

### `_req` — L718

```python
def _req(method: str, base: str, path: str, payload: dict | None=None, query: dict | None=None, timeout: float=_TIMEOUT, _retry_auth: bool=True) -> Any
```

### `ping` — L773

```python
def ping(base: str=DEFAULT_BASE) -> dict
```

### `search` — L809

```python
def search(q: str, base: str=DEFAULT_BASE, expand: bool=True) -> dict
```

### `status` — L936

```python
def status(base: str=DEFAULT_BASE) -> dict
```

### `cancel` — L940

```python
def cancel(base: str=DEFAULT_BASE) -> dict
```

### `submit` — L944

```python
def submit(series_ids: list[str], base: str=DEFAULT_BASE, scores: dict | None=None) -> dict
```

**Callers (spine):** routes_hg Hongguo enqueue

### `library_update` — L954

```python
def library_update(base: str=DEFAULT_BASE, names: list[str] | None=None) -> dict
```

### `seasons_decline` — L961

```python
def seasons_decline(series_ids: list[str], base: str=DEFAULT_BASE) -> dict
```

### `rank` — L968

```python
def rank(category: str='all', board: str='recommend', offset: int=0, size: int=100, base: str=DEFAULT_BASE) -> dict
```

**Doc:** Bảng hot giống app Hongguo Downloader (GET /dl/rank).

### `genres` — L1023

```python
def genres(limit: int=25) -> list[str]
```

**Doc:** Lấy danh sách các thể loại phim từ Hongguo Catalog Explorer.

### `catalog` — L1040

```python
def catalog(genre: str='', sort: str='newest', status: str='', q: str='', page: int=1, size: int=100) -> dict
```

**Doc:** Khám phá kho phim Hongguo Catalog (Explorer).

### `rank_episodes` — L1104

```python
def rank_episodes(series_ids: list[str], base: str=DEFAULT_BASE) -> dict
```

**Doc:** Bổ sung số tập cho list rank (POST /dl/rank-episodes).

### `preview_series` — L1113

```python
def preview_series(series_id: str, ep: int=1, fresh: bool=False, base: str=DEFAULT_BASE) -> dict
```

**Doc:** URL MP4 tập miễn phí (hongguoduanju) — GET /dl/preview. Không cần tải về.

### `library` — L1127

```python
def library(base: str=DEFAULT_BASE) -> dict
```

### `_output_dir` — L1155

```python
def _output_dir(base: str) -> Path | None
```

### `inspect_series_folder` — L1164

```python
def inspect_series_folder(folder: Path) -> dict
```

**Doc:** Quét folder series: có file (merged)? còn bao nhiêu mảnh tập?

### `safe_child` — L1205

```python
def safe_child(root: Path | None, name: str) -> Path | None
```

**Doc:** root/name chỉ khi name là 1 cấp thư mục ngay dưới root.

### `resolve_preview_path` — L1220

```python
def resolve_preview_path(name: str, base: str=DEFAULT_BASE) -> Path | None
```

**Doc:** Đường dẫn file xem thử trong thư viện (merged hoặc tập đầu).

### `resolve_poster_path` — L1233

```python
def resolve_poster_path(name: str, base: str=DEFAULT_BASE) -> Path | None
```

**Doc:** poster.jpg/png trong folder series (local).

### `fetch_poster` — L1248

```python
def fetch_poster(name: str, base: str=DEFAULT_BASE) -> tuple[bytes, str]
```

**Doc:** Bytes poster: ưu tiên /dl/poster (auth), fallback file local.

### `fetch_img_proxy` — L1286

```python
def fetch_img_proxy(url: str, base: str=DEFAULT_BASE) -> tuple[bytes, str]
```

**Doc:** Proxy ảnh cover: ByteDance/Hongguo đi qua :8000/img; ảnh ngoài tự fetch trực tiếp.

### `_trash_root` — L1339

```python
def _trash_root(folder: Path) -> Path
```

**Doc:** Thùng rác NGOÀI thư viện (D:\Lib → D:\Lib_trash): Hongguo/Pineline quét thư viện

### `purge_trash` — L1348

```python
def purge_trash(folder: Path, days: float=TRASH_KEEP_DAYS) -> int
```

**Doc:** Xoá hẳn các lô trong thùng rác cũ hơn `days` ngày. Trả số lô đã xoá.

### `merged_covers_fragments` — L1374

```python
def merged_covers_fragments(folder: Path, merged_file: str | None=None) -> dict
```

**Doc:** Kiểm file gộp có chứa đủ các tập lẻ đang nằm trong folder không.

### `_move_to_trash` — L1410

```python
def _move_to_trash(folder: Path, files: list[Path]) -> tuple[list[str], list[str], Path]
```

### `cleanup_fragments` — L1424

```python
def cleanup_fragments(folder: Path) -> dict
```

**Doc:** Dọn tập lẻ sau khi đã có (merged) ĐỦ nội dung: chỉ file đúng mẫu tên tập,

### `_list_episode_frags` — L1456

```python
def _list_episode_frags(folder: Path) -> list[Path]
```

### `_probe_wh` — L1472

```python
def _probe_wh(path: Path) -> tuple[int, int] | None
```

### `_probe_dur` — L1494

```python
def _probe_dur(path: Path) -> float
```

### `_frame_wh_at` — L1507

```python
def _frame_wh_at(path: Path, t: float) -> tuple[int, int] | None
```

**Doc:** Decode 1 frame tại t — bắt size thật (kể cả mid-stream đổi res).

### `_pick_h264_encoder` — L1533

```python
def _pick_h264_encoder() -> list[str]
```

**Doc:** Args -c:v … cho normalize (ưu tiên NVENC).

### `_scale_vf` — L1550

```python
def _scale_vf(w: int, h: int) -> str
```

### `episode_resolutions` — L1558

```python
def episode_resolutions(folder: Path) -> dict[str, Any]
```

**Doc:** Quét độ phân giải từng tập mảnh. mixed=True nếu lệch nhau.

### `merged_has_mixed_res` — L1580

```python
def merged_has_mixed_res(path: Path, samples: int=0) -> dict[str, Any]
```

**Doc:** Kiểm tra file (merged) có đổi res giữa chừng không.

### `normalize_merged_file` — L1612

```python
def normalize_merged_file(path: Path, target_wh: tuple[int, int] | None=None, on_pct: Callable[[float], None] | None=None) -> dict[str, Any]
```

**Doc:** Re-encode 1 file (merged) về canvas cố định (scale+pad).

### `merge_series_normalized` — L1686

```python
def merge_series_normalized(folder: Path, on_pct: Callable[[float], None] | None=None, target_wh: tuple[int, int] | None=None) -> dict[str, Any]
```

**Doc:** Merge các tập mảnh về 1 canvas (scale+pad) rồi concat.

### `mark_done` — L1774

```python
def mark_done(name: str, merged_file: str | None=None, removed: int=0) -> None
```

### `merge_one` — L1784

```python
def merge_one(name: str, base: str=DEFAULT_BASE) -> dict
```

### `merge_status` — L1791

```python
def merge_status(base: str=DEFAULT_BASE) -> dict
```

### `open_library` — L1795

```python
def open_library(name: str | None=None, base: str=DEFAULT_BASE) -> dict
```

### `delete_library_series` — L1800

```python
def delete_library_series(names: list[str], base: str=DEFAULT_BASE) -> dict
```

**Doc:** Xoá vĩnh viễn thư mục series tại ổ đĩa D:\Lib để giải phóng dung lượng.

### `merge_resume` — L1878

```python
def merge_resume(base: str | None=None) -> bool
```

**Doc:** Hàng đợi còn (nạp lại sau restart) mà không có worker → chạy tiếp, chỉ khi Hongguo đang mở

### `merge_queue_state` — L1895

```python
def merge_queue_state(base: str=DEFAULT_BASE) -> dict
```

### `merge_queue_add` — L1917

```python
def merge_queue_add(names: list[str], base: str=DEFAULT_BASE, skip_done: bool=True) -> dict
```

**Doc:** Chỉ xếp hàng rồi trả về ngay — kiểm tra/chuẩn hoá/dọn tập đều do worker làm (UI thấy tiến độ).

### `merge_queue_clear` — L1960

```python
def merge_queue_clear() -> dict
```

### `_start_worker` — L1969

```python
def _start_worker(base: str) -> None
```

### `_finish` — L1980

```python
def _finish(name: str) -> None
```

**Doc:** Kết thúc 1 series (xong hoặc lỗi): bỏ current, xoá phase, đếm vào batch, lưu state.

### `_merge_worker` — L1995

```python
def _merge_worker(base: str) -> None
```

### `_hist` — L2241

```python
def _hist(name: str, status: str, detail: str='') -> None
```

### `_baike_get` — L2265

```python
def _baike_get(url: str, timeout: float=25) -> str
```

### `_baike_clean_title` — L2271

```python
def _baike_clean_title(t: str) -> str
```

### `_titles_same_franchise` — L2278

```python
def _titles_same_franchise(root: str, other: str) -> bool
```

**Doc:** True nếu other cùng họ với root (bỏ ranking nhiễu trong 同系列).

### `baike_search` — L2301

```python
def baike_search(q: str, timeout: float=25) -> list[dict]
```

**Doc:** Search https://www.duanjubaike.net/so.html?keyword=…

### `baike_info` — L2357

```python
def baike_info(series_id: str, timeout: float=25) -> dict
```

**Doc:** Trang info-{id}: meta + 同系列 (đã lọc nhiễu ranking).

### `baike_deep` — L2548

```python
def baike_deep(series_id: str | None=None, title: str | None=None, timeout: float=25) -> dict
```

**Doc:** Lấy info sâu từ baike: ưu tiên series_id, không có thì search theo title.

### `baike_versions` — L2587

```python
def baike_versions(q: str, timeout: float=25) -> dict
```

**Doc:** Q → search baike → chọn hit khớp nhất → danh sách version (đã lọc).

### `_norm_title_key` — L2640

```python
def _norm_title_key(t: str) -> str
```

### `_hongguo_match_version` — L2647

```python
def _hongguo_match_version(ver: dict, base: str=DEFAULT_BASE) -> tuple[dict | None, str]
```

**Doc:** Map 1 version baike → Hongguo. Ưu tiên series_id, rồi search đúng tên.

### `search_via_baike` — L2743

```python
def search_via_baike(q: str, base: str=DEFAULT_BASE) -> dict
```

**Doc:** Baike nhận diện → versions → match từng cái trên Hongguo.
