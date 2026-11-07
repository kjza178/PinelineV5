# Hongguo 2.x bridge — post-:8801-restart test

- **Date:** 2026-11-07 (~22:05 local)
- **Live:** `http://127.0.0.1:8801`
- **Backend:** RPC (`agents.hongguo_bridge` → `hongguo_rpc` / WinUI helper)
- **Engine:** `%LOCALAPPDATA%\HongguoWinUI\current\engine` (helper `hongguo-helper-0.3.14`, protocol 2)
- **Secrets policy:** no keys/proofs/tokens/device secrets printed — lengths / status codes / state strings only
- **Status:** partial (browse OK; license-gated downloads blocked)

## Environment checks (no secrets)

| Check | Result |
|---|---|
| DPAPI key `%LOCALAPPDATA%\Pineline\hg_typed_key.dpapi` | exists, size=262 |
| Activate host `%TEMP%\HgLicActivate_patch\HgLicActivate.exe` (`TEMP=D:\Temp`) | **MISSING** |
| Engine dir | exists, 5 entries (`ffmpeg`, `lib`, `runtime`, `signer`, `engine.json`) |
| `:8000` TCP | closed (`connect_ex` non-zero) — optional OK |

## Matrix

| # | Test | Result | Evidence (redacted) |
|---|---|---|---|
| 1 | `GET /api/hg/ping` | **PASS** | http=200, `backend=rpc`, `license=none` (str state), `has_token=false`, `engineVersion=hongguo-helper-0.3.14`, `protocol=2`, capabilities list len=29 |
| 1b | `POST /api/hg/ping` | **FAIL** | http=405 Method Not Allowed (route is GET-only) |
| 2 | `GET /api/hg/search?q=…` | **PASS** | http=200, `backend=rpc`, `results` non-empty (sample len=6), item keys include `series_id,title,cover,episode_cnt,score,tags,intro,…` |
| 2b | `POST /api/hg/search` | **FAIL** | http=405 (GET-only) |
| 3 | `GET /api/hg/rank` | **PASS** | http=200, `backend=rpc`, `results` non-empty (sample len=6), same card shape |
| 3b | `GET /api/hg/feed` | **SKIP/FAIL** | http=404 — `hongguo_rpc.feed()` exists, no `/api/hg/feed` route |
| 4 | `GET /api/hg/library` | **PASS** | http=200, `backend=rpc`, `items` non-empty (payload ~28KB; item keys include `series_id,name,title,folder,local,merged,…`), `newSeasons` present |
| 5 | lookup / resolve | **PASS** (resolve+series) | `GET /api/hg/series/{id}` http=200; `POST /api/hg/resolve` with series_id http=200 `resolved`+`backend=rpc`. Title-only resolve may return empty/`links.resolve` miss (expected). |
| 5b | `/api/hg/lookup` | **SKIP** | http=404 — no alias route (UI uses `resolve` / `series/{id}`) |
| 6 | `GET /api/hg/status` | **PASS** | http=200, `backend=rpc`, `source=downloads.snapshot`, `running=false`, `series=[]`, `jobs=[]`, `active=0` |
| 7 | `hongguo_license_ensure.ensure_licensed` | **FAIL** | `ok=false`, `error=missing_activate_host`, hint=`D:\Temp\HgLicActivate_patch\HgLicActivate.exe`; `license_ready=False`; RPC `license.status.state=none` |
| 8 | `library.downloadNewSeasons` | **FAIL** | Direct `rpc.library_download_new_seasons()` → `HgRpcError` **code=-32010**, `data.reason=need_license` (ensure failed missing host). API `POST /api/hg/library/update` http=200 but **fallback refresh** with `warning` containing `missing_activate_host` (not a successful downloadNewSeasons) |
| 9 | `downloads.add` / submit dry | **FAIL** (licensed path) | Empty `series_ids` → http=502 `series_ids trống` (not `need_license`). Invalid id → http=502 / rpc **code=-32010** `need_license` / `missing_activate_host`. No download queued; `POST /api/hg/cancel` http=200 `{ok:true}` |
| 10 | `:8000` optional | **PASS** | Port closed; browse/RPC paths still work without Downloader 1.x |

## UI endpoints still calling 1.x HTTP (`:8000`) — broken while RPC-only

These are still invoked from `static/ui/hongguo.html` / `hongguo2.html` (via `:8801` routes that call `_req` → `http://127.0.0.1:8000`):

| UI → API | Live probe | Why broken on 2.x-only |
|---|---|---|
| `POST /api/hg/rank-episodes` | http=502, connection refused `:8000` | `hongguo_bridge.rank_episodes` is HTTP-only |
| `GET /api/hg/preview` | http=502, refused `:8000` | `preview_series` is HTTP-only |
| `POST /api/hg/library/seasons/decline` | http=502, refused `:8000` | `seasons_decline` is HTTP-only |

### UI calls that worked on this RPC session

`ping`, `search`, `rank`, `resolve`, `series/{id}`, `status`, `library`, `cancel`, `library/update` (refresh fallback), `library/seasons/discover`, `library/watchlist`, `merge-queue`, `web-search`, `baike-search` (and other local/Pineline helpers: poster/img/merge/translate — not re-probed exhaustively).

### Missing / unused aliases (not UI-critical)

- `/api/hg/feed` — 404 (RPC method exists, no FastAPI route)
- `/api/hg/lookup` — 404 (use `resolve` / `series/{id}`)
- `POST /api/hg/ping` / `POST /api/hg/search` — 405

## Root blocker for items 7–9

After restart, helper `license.state=none`. Re-prove requires activate host. At test time `%TEMP%\HgLicActivate_patch\` was **absent** (DPAPI key still present) → `missing_activate_host`.

## Follow-up (~22:07)

- Host installed durable: `%LOCALAPPDATA%\Pineline\tools\HgLicActivate\HgLicActivate.exe`
- `hongguo_license_ensure` resolves that path first (not TEMP)
- Recheck in-process: `ensure_licensed(force=True)` → **ok True**, `state=licensed`; `library.downloadNewSeasons` → `{added:[], busy:[]}` (no `-32010`)
- Note: `GET /api/hg/ping` `license` is **per helper process** — stays `none` until ensure runs inside **:8801** (on submit / downloadNewSeasons after module reload)

## Recheck (current)

1. `Test-Path $env:LOCALAPPDATA\Pineline\tools\HgLicActivate\HgLicActivate.exe`
2. `python -c "import hongguo_license_ensure as l; print(l._ACTIVATE_EXE); r=l.ensure_licensed(); print(r.get('ok'), r.get('status',{}).get('state'))"`
3. After ensure in server process: download / submit must not return `-32010`
4. Optional dry `POST /api/hg/submit` with one library `series_id` then `POST /api/hg/cancel`

## Liên quan

- License design: `docs/reviews/2026-11-07-hongguo-license-prove-review.md`
- Portability: `docs/reviews/2026-11-07-hongguo-lic-host-portability.md`
- Modules: `Z:\PinelineV2\hongguo_license_ensure.py`, `Z:\PinelineV5\agents\hongguo_rpc.py`, `Z:\PinelineV5\agents\hongguo_bridge.py`, `Z:\PinelineV5\http_routes\routes_hg.py`
