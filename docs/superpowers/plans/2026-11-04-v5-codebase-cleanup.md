# V5 Codebase Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Before each phase, dispatch `v5-structure-auditor` + `v5-deadcode-hunter` + `v5-ops-docs-auditor` for cross-check; do not proceed if they disagree on must-not-break items.

**Goal:** Làm gọn PinelineV5 thành codebase rõ LIVE/TARGET, hết footgun V2/V4 trong tree V5, docs khớp ops — không big-bang move pipeline.

**Architecture:** Giữ thân handler ở root `server.py`; `pineline.server.routes.*` chỉ registry `attach`. Dọn dead UI/script/docs; siết launcher/restart về `run_v5.bat`/:8805; mở rộng test attach. Chỉ sau đó mới carve `server/services` hoặc chuyển `routes_*`.

**Tech Stack:** FastAPI, `pineline.server.routes`, `job_queue`/`film_db`, pytest, docs-on-change (không git commit trừ khi user yêu cầu).

## Global Constraints

- Ports: V5 **:8805**, sidecar **:8802**, không đụng V2 **:8801** khi busy trừ user yes.
- Một thân handler / path — không copy body vào package.
- `MANIFEST_CONTRACT.md`: list = DB-first; live progress = 1 manifest `current`.
- `import server as S` / `sys.modules["server"]` phải còn cho routes + monkeypatch test.
- Backup zip + codebak trước mỗi đợt sửa code; CHANGELOG + worklog + STATE.
- Không port attach SSOT sang V2/V4 trừ DECISIONS mới.
- Không xoá empty `pineline/{pipeline,agents,…}` TARGET maps.
- Project không dùng git làm lịch sử — bước “Commit” = cập nhật `docs/CHANGELOG.md` + worklog (và git chỉ khi user hỏi).

**Evidence / synthesis:** `docs/design/2026-11-04-v5-structure-cleanup.md`  
**Already done (skip):** queue/jobs/assets/fs attach; `http_queue_state`; film-db queue meta; oneshot archive; tauri node_modules deleted.

---

### Task 1: Restart :8805 nạp assets/fs (ops gate)

**Files:**
- Modify: `docs/STATE.md` (PID / chờ restart)
- Test: HTTP OpenAPI smoke

**Interfaces:**
- Consumes: code on disk already stripped
- Produces: process PID mới; `/api/cookies` served via attach

- [ ] **Step 1: User yes/no restart :8805** (queue V5 phải idle — verify `GET :8805/api/queue/jobs` → `busy=false`)
- [ ] **Step 2: Restart**

```bat
cd /d Z:\PinelineV5
set PORT=8805
python restart_server.py --ignore-hg --clean-env
```

- [ ] **Step 3: Smoke**

```bat
python -c "import urllib.request,json; u=urllib.request.urlopen('http://127.0.0.1:8805/openapi.json'); p=json.load(u)['paths']; assert '/api/cookies' in p and '/api/fs/list-dirs' in p; print('ok', len(p))"
```

Expected: `ok` + path count ≥ 100; không Duplicate Operation ID job_video/hg trên stderr startup.

- [ ] **Step 4: Docs** — STATE PID mới; gạch mục chờ restart; worklog 1 dòng.

---

### Task 2: Docs truth pass (branding + LIVE map)

**Files:**
- Modify: `docs/STATE.md`, `docs/README.md`, `docs/ARCHITECTURE.md`, `docs/RUNBOOK.md`, `README.md` (root nếu claim TARGET sai), `pineline/README.md`
- Test: manual checklist cổng/path

**Interfaces:**
- Produces: docs nói V5/:8805; mermaid assets/fs LIVE

- [ ] **Step 1: Retitle** mọi header «PinelineV4» trong tree V5 docs → «PinelineV5» (giữ mục dual-tree rõ V2/V4).
- [ ] **Step 2: ARCHITECTURE** — mermaid `assets/fs LIVE`; pipeline note: `WIRED_STAGES` = download/asr/translate/tts/mux (assemble = helper trong render).
- [ ] **Step 3: RUNBOOK** — fork cổng 8805, `run_v5.bat`, TEMP `D:\PinelineV5_tmp`; mục «must stay dual» (films DB production = V2 khi sidecar BASE :8801).
- [ ] **Step 4: Root README / pineline README** — LIVE = queue|jobs|assets|fs; bỏ «assets TARGET».
- [ ] **Step 5: Recheck** — grep `TARGET` + `8804` trong `docs/ARCHITECTURE.md` và `pineline/README.md` không còn mô tả sai assets.

---

### Task 3: Archive dead UI twin `static/app.js`

**Files:**
- Move: `static/app.js` → `scripts/archive/ui_legacy/app.js`
- Modify: none required if no HTML links (verify first)
- Test: `tests/test_ui_no_app_js.py` (new)

**Interfaces:**
- Consumes: `routes_ui.find_index` → `index3.html` only
- Produces: no live twin drift

- [ ] **Step 1: Failing test**

```python
# tests/test_ui_no_app_js.py
from pathlib import Path

def test_index3_does_not_reference_app_js():
    html = (Path(__file__).resolve().parents[1] / "index3.html").read_text(encoding="utf-8")
    assert "app.js" not in html
    assert "static/app.js" not in html

def test_app_js_not_in_static_live():
    assert not (Path(__file__).resolve().parents[1] / "static" / "app.js").is_file()
```

- [ ] **Step 2: Run** `pytest tests/test_ui_no_app_js.py -q` → expect second assert fail if file still in static.
- [ ] **Step 3: Move file** to `scripts/archive/ui_legacy/app.js` (create dir if needed); keep `static/` mount for other assets.
- [ ] **Step 4: pytest pass**; CHANGELOG + worklog.

---

### Task 4: Kill V4 footguns inside V5 tree

**Files:**
- Modify: `restart_server.py` (default bat → `run_v5.bat`), `migrate_work.py` similarly
- Move/Archive: root `run_v4.bat`, `PineLine_Studio_V4.spec` → `scripts/archive/launchers_legacy/`
- Test: unit or smoke assert default launcher name

- [ ] **Step 1: Grep** `run_v4` in `Z:\PinelineV5\*.py` — list call sites.
- [ ] **Step 2: Change defaults** to `run_v5.bat` / PORT 8805 / `D:\PinelineV5_tmp` where still V4.
- [ ] **Step 3: Archive** `run_v4.bat` + V4.spec from V5 root.
- [ ] **Step 4: Recheck** — `python -c "import restart_server; …"` or read source asserts no `run_v4.bat` string in default path; docs RUNBOOK updated.

---

### Task 5: Fix or quarantine `check_batch1/2` V2 hardcode

**Files:**
- Modify: `scripts/check_batch1.py`, `scripts/check_batch2.py` **or** `tests/test_review_batches.py`
- Test: `pytest -m batches -q` (or skip markers)

- [ ] **Step 1: Prefer** set `ROOT = Path(__file__).resolve().parents[1]` (V5) like batch3–5.
- [ ] **Step 2: batch2** — drop assert `index.html` exists (archived); assert `index3.html` instead.
- [ ] **Step 3: Run** `pytest tests/test_review_batches.py -q` — pass or `@pytest.mark.skip` with reason if still historical-only.
- [ ] **Step 4: Optionally** fix `scripts/check_sidecar_lock.py` off V2 path or archive it.

---

### Task 6: Attach registry regression tests

**Files:**
- Create: `tests/test_route_registries.py`
- Modify: none

**Interfaces:**
- Consumes: `pineline.server.routes.{queue,jobs,assets,fs}._ROUTES` + `attach`
- Produces: CI signal independent of old process RAM

- [ ] **Step 1: Write test**

```python
# tests/test_route_registries.py
from pineline.server.routes import assets, fs, jobs, queue

def test_route_counts():
    assert len(queue._ROUTES) >= 11
    assert len(jobs._ROUTES) >= 40
    assert len(assets._ROUTES) >= 8
    assert len(fs._ROUTES) == 3

def test_no_app_api_decorators_in_server_source():
    import re
    from pathlib import Path
    text = (Path(__file__).resolve().parents[1] / "server.py").read_text(encoding="utf-8")
    hits = re.findall(
        r"^@app\.(get|post|delete|put|api_route)\(",
        text,
        flags=re.M,
    )
    assert hits == []  # only middleware/on_event use @app.* differently
```

Note: adjust assert if `@app.middleware` / `on_event` also match — use negative lookahead for `api/` paths only:

```python
hits = re.findall(r'^@app\.(?:get|post|delete|put|api_route)\([^\n]*["\']/api/', text, flags=re.M)
assert hits == []
```

- [ ] **Step 2: pytest** `tests/test_route_registries.py tests/test_queue_http_state.py -q` → pass.
- [ ] **Step 3: Docs** CHANGELOG.

---

### Task 7 (optional later): Move root `routes_*` into `pineline.server.routes`

**Files:**
- Create: `pineline/server/routes/{ui,hg,agent,films,uploader}.py` (move or thin wrap)
- Modify: `server.py` include_router imports
- Test: OpenAPI path set diff before/after

- [ ] **Step 1: Backup** codebak đợt riêng.
- [ ] **Step 2: Move one module** (start `routes_ui.py` → `pineline.server.routes.ui`) keeping `import server as S`.
- [ ] **Step 3: OpenAPI path equality** script vs snapshot.
- [ ] **Step 4: Restart :8805** + smoke `/` UI.
- [ ] **Step 5: Repeat** hg → agent → films → uploader (one PR/đợt each).

**Stop condition:** nếu OpenAPI diff hoặc circular import — rollback đợt đó; không gộp 5 module một lần.

---

### Task 8 (optional later): Carve `pineline.server.services`

**Files:**
- Create: helpers extracted from `server.py` (group patch, cookie prep) only when editing that cluster
- Rule: extract **on touch**, not wholesale

- [ ] Chỉ làm khi sửa cụm đó; kèm test cụm; cập nhật ARCHITECTURE.

---

### Task 9 (wontfix unless user yes): Big items

- Port attach SSOT → V2/V4
- Gộp process `/films`+`/meta` vào một cổng
- Move `asr`/`translate`/`render` vào `pineline.pipeline`
- Xoá sâu toàn bộ `scripts/archive/**`

Mỗi mục cần DECISIONS mới + yes/no riêng.

---

## Phase order (execution)

| Order | Task | Restart? | User yes? |
|---|---|---|---|
| 1 | Task 1 restart :8805 | yes | **yes/no** |
| 2 | Task 2 docs | no | recommended |
| 3 | Task 3 archive app.js | no | recommended |
| 4 | Task 4 footguns | no* | recommended |
| 5 | Task 5 check_batch | no | recommended |
| 6 | Task 6 registry tests | no | recommended |
| 7+ | Task 7–8 | per đợt | yes trước mỗi đợt |
| never default | Task 9 | — | explicit |

\*Task 4 không restart trừ khi đổi file mà process đã import — `restart_server.py` chỉ ảnh hưởng lần restart sau.

## Cross-check ritual (mỗi phase)

1. Run skill `v5-ops-docs-auditor` — restart/lock OK?
2. Run skill `v5-deadcode-hunter` — action còn đúng severity?
3. Run skill `v5-structure-auditor` — không phá must-not-break?
4. Nếu conflict → dừng, ghi `docs/reviews/YYYY-MM-DD-cleanup-conflict.md`, hỏi user.
