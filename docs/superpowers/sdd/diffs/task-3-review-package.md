# Task 3 Review Package

### JobQueueReq
```python
class JobQueueReq(RunAllReq):
    job_ids: list[str]
    skip_done: bool = True


```

### route @app.post("/api/queue/jobs")
```python
@app.post("/api/queue/jobs")
def api_queue_jobs_add(req: JobQueueReq):
    ids = [str(x).strip() for x in (req.job_ids or []) if str(x).strip()]
    if not ids:
        return JSONResponse({"error": "chọn ≥1 job"}, status_code=400)
    opts = req.model_dump(exclude={"job_ids", "skip_done"})
    try:
        return job_queue.queue_add(ids, opts=opts, skip_done=bool(req.skip_done))
    except Exception as e:  # noqa: BLE001
        return JSONResponse({"error": str(e)}, status_code=400)


@app.get("/api/queue/jobs")
def api_queue_jobs_state():
    return job_queue.queue_state()


@app.post("/api/queue/jobs/stop")
def api_queue_jobs_stop():
    return job_queue.queue_stop()


@app.post("/api/queue/jobs/clear")
def api_queue_jobs_clear():
    return job_queue.queue_clear()


@app.post("/api/jobs/local-path")
def create_local_job_path(body: LocalJobIn):
    """Tạo job từ đường dẫn video local
```

### route @app.get("/api/queue/jobs")
```python
@app.get("/api/queue/jobs")
def api_queue_jobs_state():
    return job_queue.queue_state()


@app.post("/api/queue/jobs/stop")
def api_queue_jobs_stop():
    return job_queue.queue_stop()


@app.post("/api/queue/jobs/clear")
def api_queue_jobs_clear():
    return job_queue.queue_clear()


@app.post("/api/jobs/local-path")
def create_local_job_path(body: LocalJobIn):
    """Tạo job từ đường dẫn video local (không cần link) + import source luôn."""
    src = Path(body.path.strip().strip('"')).expanduser()
    try:
        src = src.resolve(strict=True)
    except FileNotFoundError:
        return JSONResponse({"error": f"không thấy file: {body.path}"}, status_code=400)
    except OSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    if not src.is_file():
        return JSONResponse({"error": "path không phải file"}, status_code=400)
    ext = src.suffix.lower()

```

### route @app.post("/api/queue/jobs/stop")
```python
@app.post("/api/queue/jobs/stop")
def api_queue_jobs_stop():
    return job_queue.queue_stop()


@app.post("/api/queue/jobs/clear")
def api_queue_jobs_clear():
    return job_queue.queue_clear()


@app.post("/api/jobs/local-path")
def create_local_job_path(body: LocalJobIn):
    """Tạo job từ đường dẫn video local (không cần link) + import source luôn."""
    src = Path(body.path.strip().strip('"')).expanduser()
    try:
        src = src.resolve(strict=True)
    except FileNotFoundError:
        return JSONResponse({"error": f"không thấy file: {body.path}"}, status_code=400)
    except OSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    if not src.is_file():
        return JSONResponse({"error": "path không phải file"}, status_code=400)
    ext = src.suffix.lower()
    if ext not in _VIDEO_EXT:
        return JSONResponse(
            {"error": f"định dạng 
```

### route @app.post("/api/queue/jobs/clear")
```python
@app.post("/api/queue/jobs/clear")
def api_queue_jobs_clear():
    return job_queue.queue_clear()


@app.post("/api/jobs/local-path")
def create_local_job_path(body: LocalJobIn):
    """Tạo job từ đường dẫn video local (không cần link) + import source luôn."""
    src = Path(body.path.strip().strip('"')).expanduser()
    try:
        src = src.resolve(strict=True)
    except FileNotFoundError:
        return JSONResponse({"error": f"không thấy file: {body.path}"}, status_code=400)
    except OSError as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    if not src.is_file():
        return JSONResponse({"error": "path không phải file"}, status_code=400)
    ext = src.suffix.lower()
    if ext not in _VIDEO_EXT:
        return JSONResponse(
            {"error": f"định dạng {ext or '?'} không hỗ trợ (dùng {', '.join(sorted(_VIDEO_EXT))})"},
            status_code=400,

```

### test_queue_jobs_api.py
```python
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import server


def _manifest(wd: Path) -> None:
    wd.mkdir(parents=True, exist_ok=True)
    (wd / "manifest.json").write_text(
        json.dumps({"stages": {"download": {"status": "done"}}}, ensure_ascii=False),
        encoding="utf-8",
    )


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(server, "WORK_ROOT", tmp_path)
    monkeypatch.setattr(server.job_queue, "WORK_ROOT", tmp_path)
    server.job_queue._reset_for_tests()
    monkeypatch.setattr(server.job_queue, "_ensure_worker_unlocked", lambda: None)
    return TestClient(server.app)


def test_queue_jobs_api_add_state_stop_clear(client, tmp_path):
    _manifest(tmp_path / "job-a")
    r = client.post(
        "/api/queue/jobs",
        json={"job_ids": ["job-a"], "voice": "v1", "audio_mode": "voice_bgm"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["queued"] == ["job-a"]

    st = client.get("/api/queue/jobs").json()
    assert st["queue"] == ["job-a"]
    assert st["opts"].get("voice") == "v1"

    stop = client.post("/api/queue/jobs/stop").json()
    assert stop["ok"] is True

    cleared = client.post("/api/queue/jobs/clear").json()
    assert cleared["ok"] is True
    assert cleared["queue"] == []


def test_queue_jobs_api_rejects_empty_ids(client):
    r = client.post("/api/queue/jobs", json={"job_ids": []})
    assert r.status_code == 400
    assert "chọn" in r.json()["error"]

```