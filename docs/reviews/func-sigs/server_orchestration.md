# Server orchestration helpers (spine subset ~35)

- **Module:** `server.py`
- **Date:** 2026-11-06
- **Source:** AST extract (`scripts/_tmp_extract_sigs.py`)
- **Count:** 35 signatures in this doc

## Signatures

### `_maybe_auto_split_guarded` — L80

```python
def _maybe_auto_split_guarded(job_id: str, **kwargs)
```

**Doc:** Wrap maybe_auto_split_job với lock chống gọi chồng cùng job_id.

### `_job_any_busy` — L162

```python
def _job_any_busy(job_id: str) -> str | None
```

**Doc:** Trả tên stage đang claim, hoặc None.

### `_claim_stage` — L171

```python
def _claim_stage(job_id: str, stage: str) -> bool
```

**Doc:** Giữ chỗ trước khi submit thread — chống bấm 2-3 lần tạo nhiều task.

**Callers (spine):** _queue_run_one; _auto_pipeline

### `_release_stage` — L180

```python
def _release_stage(job_id: str, stage: str) -> None
```

### `_manifest_running` — L217

```python
def _manifest_running(work_dir: Path) -> str | None
```

**Doc:** Stage đang 'running' trong manifest (nếu có).

### `_heal_stale_running` — L309

```python
def _heal_stale_running(work_dir: Path) -> list[str]
```

**Doc:** Sửa stage status=running mồ côi (kill/crash/skip không mark_done).

**Callers (spine):** _queue_run_one

### `_next_incomplete_stage` — L380

```python
def _next_incomplete_stage(work_dir: Path) -> str | None
```

**Doc:** Bước WIRED đầu tiên chưa done (để mark_running đúng — không ép lại ASR).

### `_run_engine` — L390

```python
def _run_engine(script: str, work_dir: Path, *args: str) -> None
```

**Doc:** Chạy engine NẶNG (ASR/TTS) ở TIẾN TRÌNH RIÊNG.

**Callers (spine):** _auto_gpu ASR/OCR/separate; _run_translate_engine

### `_auto_pipeline` — L1254

```python
def _auto_pipeline(job_id: str, audio_mode: str, voice_vol: float, orig_vol: float, use_ocr: bool, fit: bool=True, resolution: str='source', translate_mode: str | None=None, render_kw: dict | None=None, asr_engine: str | None=None)
```

**Doc:** 1-CLICK (chạy ở hàng _dl): tải (nếu cần) -> đẩy phần GPU sang hàng _gpu.

**Callers (spine):** 1-click / run-all UI

### `_run_requested_review` — L1341

```python
def _run_requested_review(wd: Path, target: str) -> dict | None
```

**Doc:** Rà soát do Agent/user yêu cầu (manifest.agent.review_request): rà tên nhân vật theo bảng

### `_save_series_glossary` — L1402

```python
def _save_series_glossary(wd: Path) -> None
```

### `_auto_gpu` — L1413

```python
def _auto_gpu(job_id: str, target: str, audio_mode: str, voice_vol: float, orig_vol: float, use_ocr: bool, fit: bool=True, resolution: str='source', translate_mode: str | None=None, render_kw: dict | None=None, asr_engine: str | None=None)
```

**Doc:** Phần GPU của 1-click (hàng _gpu, tuần tự): ASR -> Dịch -> TTS -> [Tách nền]

**Callers (spine):** _queue_run_one via _gpu.submit; _auto_pipeline

### `_create` — L1882

```python
def _create(url: str, target: str, cookies_from_browser: str | None, group: dict | None=None) -> str
```

**Doc:** Tạo 1 job ở trạng thái CHỜ (chưa chạy). Người dùng bấm ▶ Bắt đầu mới chạy.

**Callers (spine):** create_job; expand_meta loop

### `_create_local_shell` — L1902

```python
def _create_local_shell(target: str, *, job_key: str, title: str | None=None, orig_path: str | None=None, group: dict | None=None) -> tuple[str, Path]
```

**Doc:** Tạo job local (không URL). job_key ổn định theo path để resume cùng file.

### `create_job` — L1997

```python
def create_job(job: NewJob)
```

**Doc:** Thêm link -> tạo job CHỜ. 1 link ra NHIỀU video (multi-P/playlist) -> gom

**Callers (spine):** UI/API NewJob

### `api_queue_jobs_add` — L2201

```python
def api_queue_jobs_add(req: JobQueueReq)
```

**Callers (spine):** UI queue add

### `_save_tts_voice` — L2839

```python
def _save_tts_voice(work_dir: Path, voice: str) -> None
```

**Doc:** Lưu giọng vào manifest + sidecar — KHÔNG được wipe stages khác.

### `_save_tts_speed` — L2844

```python
def _save_tts_speed(work_dir: Path, speed: float) -> None
```

### `_save_tts_engine` — L2848

```python
def _save_tts_engine(work_dir: Path, engine: str) -> None
```

### `_resolve_voice` — L2906

```python
def _resolve_voice(work_dir: Path, voice: str | None) -> str
```

**Doc:** Giọng: arg → stages.tts → tts_config → queue_opts/opts → list[0].

### `_resolve_queue_voice` — L2931

```python
def _resolve_queue_voice(work_dir: Path, voice: str | None) -> str
```

**Doc:** Queue chỉ dùng giọng được chọn rõ ràng hoặc đã lưu cho chính job.

### `_asr_script` — L2996

```python
def _asr_script(engine: str) -> str
```

### `_save_asr_engine` — L3033

```python
def _save_asr_engine(work_dir: Path, engine: str) -> None
```

**Doc:** Lưu engine. Nếu đã có sidecar tương ứng → promote luôn (tránh lệch nhãn/nội dung).

### `_run_translate_engine` — L3063

```python
def _run_translate_engine(work_dir: Path, batch: int | None=None, target: str | None=None, force: bool=False, model: str | None=None, mode: str | None=None, review_only: bool=False, review_force: bool=False) -> None
```

**Doc:** Chạy stage dịch ở TIẾN TRÌNH RIÊNG (subprocess) giống như ASR và TTS.

**Callers (spine):** _auto_gpu

### `_resolve_asr_engine` — L3098

```python
def _resolve_asr_engine(work_dir: Path, engine: str | None) -> str
```

### `_do_tts` — L3135

```python
def _do_tts(work_dir: Path, voice: str, speed: float, engine: str, force: bool)
```

**Doc:** Chạy TTS clone tiếng Việt (vieneu/omnivoice). Điều phối worker venv riêng

**Callers (spine):** _auto_gpu

### `_do_render` — L3151

```python
def _do_render(work_dir: Path, force: bool=True, audio_mode: str='voice_bgm', voice_vol: float=0.2, orig_vol: float=0.6, add_sub: bool=True, fit: bool=True, resolution: str='source', flip: str='', zoom: float=1.12, motion: bool=True, lut: bool=True, grain: str='weak', brand: bool=False, brand_text: str='', frame: str='off', brand_mode: str='off', brand_logo: str='off', vbitrate: str='8M', speed_factor: float=1.0)
```

**Doc:** Ghép giọng (assemble nếu chưa) rồi render video localize (che+sub+trộn nền).

**Callers (spine):** _auto_gpu

### `_queue_run_one` — L3737

```python
def _queue_run_one(job_id: str, opts: dict) -> tuple[str, str]
```

**Doc:** Run one queued job synchronously through mux and return status + detail.

**Callers (spine):** job_queue.set_runner → _worker_loop

### `_promote_asr_source` — L4104

```python
def _promote_asr_source(work_dir: Path, source: str) -> dict
```

**Doc:** Copy sidecar → asr.json + sub.zh.srt; backup asr.json cũ.

### `select_asr_source` — L4334

```python
def select_asr_source(job_id: str, req: AsrSelectReq)
```

**Doc:** Promote file ASR (vd asr.fun_nano.json) → asr.json + sub.zh.srt.

### `_do_context_studio` — L4358

```python
def _do_context_studio(work_dir: Path, use_llm: bool=True) -> dict
```

**Doc:** Chạy PRE-SCAN → ghi pack vào work_dir.

### `run_context_studio_api` — L4476

```python
def run_context_studio_api(job_id: str, req: ContextStudioReq)
```

**Doc:** Chạy Context Studio PRE-SCAN → glossary/style_lock/qa_flags trong work/<job>.

### `_place_source` — L4849

```python
def _place_source(src: Path, work_dir: Path, move: bool) -> tuple[Path, str]
```

**Doc:** Trả (đường dẫn video job dùng, cách đặt: direct/move/link/copy).

### `_finalize_imported_source` — L4862

```python
def _finalize_imported_source(work_dir: Path, dest: Path, *, orig_name: str | None=None, source_kind: str='imported', source_mode: str | None=None) -> dict
```

**Doc:** Ghi meta + mark download done. `dest` có thể nằm ngoài job (source_mode=direct: file thư viện).

### `_find_video` — L4906

```python
def _find_video(work_dir: Path) -> Path | None
```

**Doc:** Tìm file video đã tải: ưu tiên video_path trong manifest, fallback glob.

**Callers (spine):** _queue_run_one
