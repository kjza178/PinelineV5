# Agent HTTP routes

- **Module:** `http_routes/routes_agent.py`
- **Date:** 2026-11-06
- **Source:** AST
- **Count:** 40

## Signatures

### `_agent_get_job` — L77

```python
def _agent_get_job(job_id: str) -> dict
```

### `_agent_queue_add` — L84

```python
def _agent_queue_add(job_ids: list[str], opts: dict) -> dict
```

### `_agent_edit_line` — L90

```python
def _agent_edit_line(job_id: str, i: int, vi: str | None, zh: str | None)
```

### `_agent_set_hold` — L101

```python
def _agent_set_hold(job_id: str, enabled: bool) -> dict
```

### `_agent_get_hold` — L128

```python
def _agent_get_hold(job_id: str) -> dict
```

### `_agent_run_stage` — L136

```python
def _agent_run_stage(job_id: str, stage: str, opts: dict) -> dict
```

**Doc:** Chạy 1 stage qua API nội bộ (vd tts sau duyệt).

### `_agent_stop_job` — L155

```python
def _agent_stop_job(job_id: str)
```

### `_agent_tts_set_voice` — L165

```python
def _agent_tts_set_voice(job_id: str, opts: dict)
```

### `_agent_mux_run` — L179

```python
def _agent_mux_run(job_id: str, opts: dict)
```

**Doc:** Render lại theo đúng opts job đã chạy (queue_opts) ⊕ config batch, chỉ đè key agent truyền.

### `_agent_asr_set_engine` — L201

```python
def _agent_asr_set_engine(job_id: str, engine: str)
```

### `_job_in_pipeline` — L211

```python
def _job_in_pipeline(job_id: str) -> bool
```

### `_agent_script_review` — L218

```python
def _agent_script_review(job_id: str, review_model: str | None)
```

**Doc:** Rà soát tên nhân vật + văn phong trước lồng tiếng.

### `_agent_resume` — L265

```python
def _agent_resume(job_id: str) -> dict
```

**Doc:** Duyệt xong → bỏ HOLD/QA block và xếp lại job lên ĐẦU hàng chờ: pipeline bỏ qua bước đã xong,

### `api_agent_review` — L297

```python
def api_agent_review(job_id: str, body: dict | None=None)
```

### `api_agent_resume` — L302

```python
def api_agent_resume(job_id: str)
```

### `_agent_script_review_legacy` — L306

```python
def _agent_script_review_legacy(job_id: str, review_model: str | None)
```

**Doc:** Rà soát văn phong = translate API review_only (run_review).

### `_agent_heal_stale` — L320

```python
def _agent_heal_stale(job_id: str)
```

### `_agent_translate_fill` — L329

```python
def _agent_translate_fill(job_id: str)
```

### `_agent_translate_rerun` — L339

```python
def _agent_translate_rerun(job_id: str)
```

### `_agent_tts_run_simple` — L349

```python
def _agent_tts_run_simple(job_id: str)
```

### `_agent_mux_retry` — L353

```python
def _agent_mux_retry(job_id: str)
```

### `_agent_asr_force` — L357

```python
def _agent_asr_force(job_id: str)
```

### `_agent_assemble_fit` — L361

```python
def _agent_assemble_fit(job_id: str, max_speed: float=1.3)
```

### `_agent_mux_force_av` — L369

```python
def _agent_mux_force_av(job_id: str, audio_mode: str | None=None)
```

### `_agent_reset_state` — L379

```python
def _agent_reset_state(job_id: str, stages: list[str] | str | None=None, keep_asr: bool=True, restart: bool=False)
```

### `_agent_notify` — L403

```python
def _agent_notify(text: str) -> None
```

### `api_agent_status` — L435

```python
def api_agent_status()
```

**Doc:** Snapshot jobs cho panel Agent (không cần LLM).

### `api_agent_chat` — L444

```python
def api_agent_chat(req: S.AgentChatReq)
```

**Doc:** Chat với AI Agent — tools gọi hàm nội bộ (queue/manifest), không HTTP self.

### `api_agent_pending` — L470

```python
def api_agent_pending()
```

### `api_agent_confirm` — L475

```python
def api_agent_confirm(req: S.AgentConfirmReq)
```

**Doc:** Chạy (approve) hoặc huỷ thao tác agent đã đỗ lại chờ xác nhận.

### `api_agent_scan_failed` — L496

```python
def api_agent_scan_failed()
```

**Doc:** Quét mọi job lỗi/kẹt (không sửa).

### `api_agent_heal_failed` — L506

```python
def api_agent_heal_failed(req: AgentHealBatchReq)
```

**Doc:** Heal hàng loạt job lỗi. apply=false chỉ plan.

### `api_agent_review_diff` — L531

```python
def api_agent_review_diff(job_id: str)
```

### `api_agent_qa_gate` — L540

```python
def api_agent_qa_gate(job_id: str, req: AgentQaGateReq)
```

### `api_agent_reset_state` — L559

```python
def api_agent_reset_state(job_id: str, req: AgentResetStateReq | None=None)
```

**Doc:** Reset sạch trạng thái các stage bị kẹt/lỗi của job (xóa artifact dở, gỡ .stop, đưa manifest về pending).

### `api_agent_watch_once` — L569

```python
def api_agent_watch_once()
```

**Doc:** Chạy 1 vòng watcher ngay (scan→heal safe nếu GPU rảnh).

### `api_agent_av_sync` — L588

```python
def api_agent_av_sync(job_id: str)
```

### `api_agent_av_sync_heal` — L597

```python
def api_agent_av_sync_heal(job_id: str, req: AgentAvSyncHealReq)
```

### `api_agent_av_sync_scan` — L615

```python
def api_agent_av_sync_scan(req: AgentAvSyncScanReq)
```

### `api_agent_av_sync_heal_batch` — L626

```python
def api_agent_av_sync_heal_batch(req: AgentAvSyncScanReq)
```
