# Agent feeder

- **Module:** `agents/agent_feeder.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 65

## Signatures

### `_now_s` — L54

```python
def _now_s() -> str
```

### `_today` — L58

```python
def _today() -> str
```

### `load_state` — L64

```python
def load_state() -> dict
```

### `save_state` — L83

```python
def save_state(st: dict) -> None
```

### `normalize_spec` — L89

```python
def normalize_spec(d: dict) -> dict
```

### `describe_spec` — L120

```python
def describe_spec(s: dict) -> str
```

### `_get` — L145

```python
def _get(base: str, path: str, timeout: float=30, **params) -> dict
```

### `_post` — L151

```python
def _post(base: str, path: str, body: dict | None=None, timeout: float=120) -> dict
```

### `_hg` — L157

```python
def _hg()
```

### `_job_manifests` — L162

```python
def _job_manifests() -> list[tuple[str, dict]]
```

### `_norm` — L177

```python
def _norm(p: str) -> str
```

### `imported_paths` — L181

```python
def imported_paths() -> set[str]
```

**Doc:** Nguồn đã làm: job hiện có + database (kể cả job đã xoá thư mục).

### `lib_root` — L191

```python
def lib_root(spec: dict | None=None) -> Path | None
```

### `_match` — L206

```python
def _match(spec: dict, *texts: str) -> bool
```

### `library` — L213

```python
def library(base: str) -> list[dict]
```

### `candidates` — L246

```python
def candidates(base: str, st: dict, items: list[dict] | None=None, *, manual: bool=False) -> list[dict]
```

**Doc:** Phim (merged) chưa làm job, đã lọc + sắp: gom theo bộ, trong bộ theo thứ tự mùa.

### `_db_series_info` — L309

```python
def _db_series_info() -> dict[str, dict]
```

**Doc:** series → {done, uploaded, max_season} từ database phim.

### `group_score` — L326

```python
def group_score(core: str, seasons: list[dict], st: dict, info: dict) -> tuple[float, list[str]]
```

**Doc:** Điểm gợi ý 1 bộ: nối mạch bộ đang làm > mùa kế tiếp > đủ mùa sẵn > mới tải.

### `_season_no` — L363

```python
def _season_no(s: dict) -> int
```

### `_probe_dur` — L368

```python
def _probe_dur(path: str, st: dict) -> float | None
```

### `process_ratio` — L389

```python
def process_ratio() -> float
```

**Doc:** Thời gian xử lý / thời lượng phim — trung vị từ lịch sử các job xong liên tiếp.

### `_translate` — L412

```python
def _translate(base: str, titles: list[str], st: dict) -> dict[str, str]
```

### `library_view` — L426

```python
def library_view(base: str) -> dict
```

**Doc:** Tab «Thư viện chưa làm»: bộ có mùa ghép sẵn chưa làm job hoặc còn tập lẻ chờ ghép, kèm điểm gợi ý.

### `library_action` — L544

```python
def library_action(base: str, action: str, names: list[str] | None=None, cores: list[str] | None=None) -> dict
```

### `_probe_stream_meta` — L693

```python
def _probe_stream_meta(path: Path) -> dict
```

**Doc:** Lấy width, height, vcodec, duration của 1 file video.

### `_concat_videos_smart` — L725

```python
def _concat_videos_smart(inputs: list[Path], out_mp4: Path) -> dict
```

**Doc:** Nối danh sách file MP4 thành 1 file out_mp4 duy nhất.

### `_sanitize_folder_name` — L863

```python
def _sanitize_folder_name(name: str) -> str
```

### `combine_library_seasons` — L868

```python
def combine_library_seasons(base: str, names: list[str] | None=None, cores: list[str] | None=None, move_to_trash: bool=True, add_to_queue: bool=False) -> dict
```

**Doc:** Gộp nhiều mùa (SS1 + SS2 + SS3...) trong thư viện D:\Lib thành 1 thư mục phim duy nhất

### `_fmt_srt_ts` — L1021

```python
def _fmt_srt_ts(sec: float) -> str
```

### `combine_rendered_jobs` — L1030

```python
def combine_rendered_jobs(base: str, job_ids: list[str], custom_title_vi: str | None=None, auto_publish: bool=False) -> dict
```

**Doc:** Nối các Job ĐÃ RENDER xong (work/<jid>/output.mp4) thành 1 Job video dài hoàn chỉnh

### `pick` — L1210

```python
def pick(spec: dict, cands: list[dict]) -> list[dict]
```

### `_have` — L1221

```python
def _have(spec: dict, cands: list[dict]) -> int
```

### `_existing_group` — L1227

```python
def _existing_group(core: str) -> str | None
```

### `add_jobs` — L1235

```python
def add_jobs(base: str, chosen: list[dict]) -> dict
```

**Doc:** Tạo job local cho từng file, gom nhóm theo bộ, rồi xếp hàng theo config batch.

### `_merge_busy` — L1276

```python
def _merge_busy(base: str) -> bool
```

### `_hg_status` — L1284

```python
def _hg_status(base: str) -> dict
```

### `_downloading_sids` — L1291

```python
def _downloading_sids(hg_st: dict) -> set[str]
```

**Doc:** series_id đang tải dở. /dl/status trả khoá «sid» (không phải series_id) và giữ cả bộ đã xong.

### `mergeable` — L1303

```python
def mergeable(spec: dict, items: list[dict], hg_st: dict) -> list[dict]
```

### `hongguo_pick` — L1320

```python
def hongguo_pick(base: str, spec: dict, items: list[dict], k: int) -> list[dict]
```

### `prefetch` — L1352

```python
def prefetch(base: str, st: dict, items: list[dict], n_cands: int) -> list[str]
```

### `pipeline_idle` — L1392

```python
def pipeline_idle(brief: dict) -> bool
```

### `feed_tick` — L1399

```python
def feed_tick(base: str, *, force: bool=False) -> dict
```

**Doc:** 1 vòng: prefetch (ghép/tải) + nếu pipeline rảnh thì thêm job. force=True: thêm ngay kể cả đang chạy.

### `preview` — L1434

```python
def preview(base: str) -> str
```

### `_llm_cfg` — L1473

```python
def _llm_cfg() -> tuple[str, str, list[str]]
```

**Doc:** Cùng nguồn với agent chat (config.agent_llm): sidecar không còn cần key trong .bat.

### `_extract_json` — L1480

```python
def _extract_json(text: str) -> dict
```

### `parse_request_llm` — L1486

```python
def parse_request_llm(text: str, cur: dict) -> dict
```

### `parse_request_rules` — L1510

```python
def parse_request_rules(text: str) -> dict
```

### `set_request` — L1541

```python
def set_request(text: str) -> dict
```

### `_server_tree_cpu` — L1560

```python
def _server_tree_cpu(lib: Path | None) -> float | None
```

**Doc:** Tổng CPU-seconds của server Pineline + tiến trình con (bỏ ffmpeg ghép thư viện Hongguo).

### `_job_activity` — L1592

```python
def _job_activity(job_id: str) -> float
```

### `_running_stage` — L1607

```python
def _running_stage(job_id: str) -> tuple[str | None, dict, dict]
```

### `_running_jobs` — L1618

```python
def _running_jobs(base: str) -> tuple[list[str], dict]
```

### `_fmt_dur` — L1632

```python
def _fmt_dur(sec: float) -> str
```

### `_requeue_front` — L1638

```python
def _requeue_front(base: str, job_id: str, m: dict) -> None
```

### `runwatch_tick` — L1654

```python
def runwatch_tick(base: str, *, heal: bool, notify) -> dict
```

**Doc:** Kiểm job đang chạy. notify(text) để báo. heal=True: tự stop + xếp lại khi treo.

### `running_text` — L1731

```python
def running_text(base: str) -> str
```

### `lib_verb` — L1779

```python
def lib_verb(word: str) -> str | None
```

**Doc:** Động từ /lib làm thay đổi trạng thái (add/priority/…) hoặc None.

### `_fold` — L1785

```python
def _fold(s: str) -> str
```

### `lib_key` — L1791

```python
def lib_key(core: str) -> str
```

### `_lib_find` — L1796

```python
def _lib_find(groups: list[dict], token: str) -> list[dict]
```

**Doc:** token = số thứ tự (theo /lib gần nhất) · key nút bấm · tên gốc / tên Việt (không dấu cũng được).

### `_lib_line` — L1815

```python
def _lib_line(i: int, g: dict) -> str
```

### `_lib_buttons` — L1823

```python
def _lib_buttons(g: dict, i: int | None=None) -> list[list[tuple[str, str]]]
```

### `_lib_detail` — L1837

```python
def _lib_detail(g: dict) -> str
```

### `lib_command` — L1853

```python
def lib_command(base: str, arg: str) -> tuple[str, list]
```

**Doc:** /lib [all | <số|tên> | add|star|unstar|skip|unskip|merge <số|tên> ...] → (text, nút inline).

### `lib_callback` — L1923

```python
def lib_callback(base: str, data: str) -> str
```

**Doc:** Nút inline «lib:<action>:<key>».
