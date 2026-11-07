# Hongguo 2.x UI plan (post RPC + license prove)

- **Date:** 2026-11-07
- **Status:** plan only (docs) — no UI/code yet
- **Depends on:** [RPC bridge](./2026-11-07-hongguo-rpc-bridge-design.md) · [license prove review](../../reviews/2026-11-07-hongguo-license-prove-review.md)
- **Archive UX:** `hongguo2.html` (V4 root / V5 `static/ui/`) — useful patterns only; route `/hongguo2` still 302 → `/hongguo` (DECISIONS 11-06 Drop Hongguo2)

## Quyết định đề xuất (chờ user)

| Option | Ý | Effort | Risk |
|---|---|---|---|
| **A — Extend classic `/hongguo`** (khuyến nghị) | Giữ 1 URL quen thuộc; thêm license strip + gate download; polish tab/IA nhẹ | L–M | Thấp (không đụng DECISIONS drop) |
| **B — Revive 2.x skin** | Mở lại `/hongguo2` với IA 2 cột đã sửa (Discover \| Ops) + license | M–H | User đã bỏ vì “quá tệ”; cần redesign rõ trước ship |

**Khuyến nghị mặc định trong plan này:** **A**. Archive `hongguo2.html` chỉ lấy ý (CTA enqueue-only, seasons banner, ops tabs) — không restore route cho đến khi user chọn B.

## Bối cảnh sản phẩm

- Browse / search / rank / library đã chạy qua helper RPC **không cần license**.
- Download (`POST /api/hg/submit`, `library/update` → `downloadNewSeasons`) cần `ensure_licensed()` (DPAPI key + Activate host + challenge/prove).
- Hiện **chưa có** HTTP `/api/hg/license/*` — UI sẽ cần 2–3 endpoint mỏng (P0) bọc `hongguo_license_ensure`.
- Không bao giờ hiển thị / log / trả về license key trong JSON hoặc DOM (chỉ `has_key: true|false`).

---

## 1. Screens (IA)

Một shell `/hongguo` — top bar + tab trái (Discover/Ops) như classic; thêm **License pill** + panel Settings.

| Screen / pane | Mục đích | Primary actions |
|---|---|---|
| **Browse / Search** | Tìm series (API + baike + web expand) | Search, resolve paste-id, enqueue, detail |
| **Rank (Hot)** | Leaderboard + category chips | Load rank, fill eps, enqueue |
| **Catalog** (sub của Rank hoặc Discover) | Explorer genres/pager (`EXPLORER_API` + `/api/hg/web-search` fallback) | Filter, page, enqueue |
| **Library** | Series đã tải / local vs total / new | Open folder, delete, merge, ＋Job UI3, **Update Lib / New seasons** |
| **Downloads** | Hàng đợi tải Pineline-side + poll Hongguo status | Submit selected, cancel, live progress |
| **Merge queue** | Gộp tuần tự Pineline | Merge selected / all pending, clear |
| **Seasons (Mùa mới)** | Board từ `status.seasons` + watchlist discover | Discover (no download), Update all (gated), decline, add series |
| **Settings / License** | Backend mode, key once, prove, portability hints | Paste key → store; Prove now; Clear key; show status |

Films UI seasons (`:8802 …/films/ui?tab=seasons`) giữ deep-link như hiện tại — không thay bằng Hongguo pane.

### Shell chrome (mọi pane)

- **Ping pill:** `GET /api/hg/ping` → online / backend=`rpc|http|auto` / helper alive.
- **License pill:** `licensed` (ok) \| `none` (bad) \| `proving…` — click → Settings pane.
- Không show key; nếu `has_key` thì pill phụ `key ✓` (muted).

---

## 2. Endpoint map (mỗi screen)

### Existing `/api/hg/*` (giữ shape; bridge `HG_BACKEND=auto`)

| Screen | Endpoints |
|---|---|
| Shell / health | `GET /api/hg/ping` |
| Search | `GET /api/hg/search?q=` · `POST /api/hg/resolve` · `GET /api/hg/baike-search` · `GET /api/hg/baike-info` · `GET /api/hg/web-search` · `GET /api/hg/series/{id}` · `POST /api/hg/translate-titles` · `GET /api/hg/img` |
| Rank | `GET /api/hg/rank` · `POST /api/hg/rank-episodes` · same img/translate/detail as search |
| Catalog | Explorer host (sidecar) + `GET /api/hg/web-search` fallback |
| Library | `GET /api/hg/library` · `GET /api/hg/poster` · `POST /api/hg/library/open` · `POST /api/hg/library/delete` · `GET /api/hg/library/preview` · `GET /api/hg/preview` |
| Downloads | `POST /api/hg/submit` ⚠ · `GET /api/hg/status` · `POST /api/hg/cancel` |
| Merge | `POST /api/hg/merge` · `GET /api/hg/merge-queue` · `POST /api/hg/merge-queue/clear` |
| Seasons | `GET /api/hg/status` (seasons blob) · `POST /api/hg/library/update` ⚠ · `POST /api/hg/library/seasons/discover` · `POST /api/hg/library/seasons/decline` · `GET /api/hg/library/watchlist` · submit ⚠ for “add series” |
| Jobs (library) | `POST /api/jobs/local-path` · `POST /api/queue/jobs` (ngoài `/api/hg`) |

⚠ = **gated by `ensure_licensed`** khi backend RPC 2.x; UI phải xử lý `need_license`.

### New thin license API (P0 — chưa có)

| Method | Path | Behavior | Response (no secrets) |
|---|---|---|---|
| `GET` | `/api/hg/license/status` | `license.status` + `has_key` + `activate_host_ok` + `backend` | `{ state: licensed\|none\|…, has_key, proving?:bool }` |
| `POST` | `/api/hg/license/key` | Body `{ key }` → DPAPI write `%LOCALAPPDATA%\Pineline\hg_typed_key.dpapi`; **never echo key** | `{ ok, has_key: true }` |
| `DELETE` | `/api/hg/license/key` | Xoá blob DPAPI | `{ ok, has_key: false }` |
| `POST` | `/api/hg/license/prove` | `ensure_licensed(force=?)`; optional progress via status poll | `{ ok, status, error?: missing_key\|missing_activate_host\|bad_signature\|… }` |

Errors map: `missing_key` / `need_license` → UI mở Settings + paste; không hang download button.

---

## 3. License UX

1. **Display only status:** pill + Settings: `Licensed` / `Not licensed` / `Proving…`. Never show key, proof, token, nonce.
2. **Paste once:** Settings textarea/password field → `POST /api/hg/license/key` → clear input immediately → `has_key ✓`. Hint: “Lưu DPAPI user Windows; không sync máy khác.”
3. **Prove progress:** `POST /api/hg/license/prove` → disable CTA, spinner 30–180s; poll `GET …/status` mỗi 2s; success → pill green; fail → message thân thiện (`missing_key`, `missing_activate_host`, generic prove fail) — không dump activate log có secret.
4. **Auto path:** submit / Update Lib gọi backend `ensure_licensed` im lặng; nếu fail → toast “Cần license” + deep-link Settings (`?pane=license`).
5. **Clear key:** confirm dialog → `DELETE …/key`; state → none.

---

## 4. Download gates (`ensure_licensed`)

| Action | UI control | API | Unlicensed behavior |
|---|---|---|---|
| Add series / submit queue | «Tải» / «Thêm vào hàng đợi» → submit | `POST /api/hg/submit` | Disable hoặc allow click → `need_license` → Settings |
| Download all new seasons / Update Lib | «Update all» / «Cập nhật thư viện» | `POST /api/hg/library/update` | Same gate |
| Discover only | «Tìm mùa mới» | `POST …/seasons/discover` | **Không** cần license (browse) |
| Decline seasons | Bỏ qua | `POST …/seasons/decline` | Không cần license |
| Merge / open / delete / preview | Ops library | merge / open / delete / preview | Không cần license (local / Pineline) |

Rule: browse luôn xanh; download CTA xám + tooltip khi `state≠licensed` **và** `!has_key`; nếu `has_key` nhưng none → CTA vẫn bấm được (auto-prove) với progress.

---

## 5. Portability (máy khác)

Checklist Settings / docs tooltip (không ship secret):

1. Cài **Hongguo WinUI 2.x** (`HongguoWinUI\current\` + `engine/` + `Hongguo.Licensing`).
2. Paste **cùng license key** một lần vào Pineline → DPAPI **per Windows user** (không copy `hg_typed_key.dpapi` sang PC khác).
3. **Activate host** (`HgLicActivate` / `HG_LIC_ACTIVATE_EXE`) phải có trên máy (path env hoặc layout Pineline).
4. Pineline `:8801` spawn helper riêng — WinUI đang chạy **không** chia sẻ proof; mỗi process tự prove.
5. Escape hatch: tải trong WinUI → Pineline merge từ save folder / `HG_BACKEND=http` nếu còn 1.x `:8000`.

---

## 6. Phased delivery

### P0 — License-aware classic (ship first)

- **Scope:** Extend `/hongguo` only. License pill + Settings pane. Wire 4 license endpoints. Gate submit / library/update UX. Handle `need_license` toasts. Keep all browse tabs as-is.
- **Files (later impl):** `routes_hg.py`, thin wrap `hongguo_license_ensure`, `static/ui/hongguo.html` (+ sync V2/V4).
- **Effort:** **~0.5–1 ngày**
- **Restart:** `:8801` khi nạp routes license; hard refresh `/hongguo`.

### P1 — Discover/Ops polish (borrow archive, not revive route)

- **Scope:** Clearer CTA (enqueue-only then submit), seasons board + Update Lib status card, queue badges, optional compact Discover segment (Search|Hot|Catalog) **inside** classic tabs — no `/hongguo2`.
- **Effort:** **~1–1.5 ngày**
- **Restart:** không (HTML static) hoặc hard refresh.

### P2 — Optional 2.x skin / extras

- **Scope:** Chỉ nếu user chọn **B**: restore `/hongguo2` với IA đã sửa + license chrome; hoặc local-play `:33080` / richer prove TTL UI / `license.restore` after token known.
- **Effort:** **~2–3 ngày** (skin) hoặc **M** thêm nếu playback.
- **Restart:** `:8801` nếu đổi route; hard refresh.

| Phase | Deliverable | Effort | Gate |
|---|---|---|---|
| P0 | License UX + API + download gate on `/hongguo` | 0.5–1d | User OK extend classic |
| P1 | IA/CTA polish on classic | 1–1.5d | P0 green |
| P2 | Revive skin / playback / restore | 2–3d+ | User chọn B hoặc yêu cầu playback |

---

## 7. Open questions (user — chỉ yes/no hoặc chọn ngắn)

1. UI path? → **A extend `/hongguo`** / **B revive `/hongguo2` skin** / **A rồi B sau**
2. P0 ship license API + Settings trên classic ngay? → **yes / no**
3. Download CTA khi chưa license? → **disable cứng** / **cho bấm → mở Settings**
4. Sau paste key: prove **ngay** / **chỉ khi bấm Tải / Update Lib**
5. Giữ deep-link Films UI Mùa mới như hiện tại? → **yes / no**
6. Máy mới: Settings hiện checklist portability? → **yes / no**
7. P2 local-play preview trong UI? → **yes / later / no**

---

## Ngoài phạm vi (plan này)

- Implement HTML/routes (chỉ docs).
- Crack / stdin WinUI / dump key.
- Đổi shape browse `/api/hg/*`.
- Thay Films UI seasons board.

## Liên quan

- DECISIONS: 11-06 Drop Hongguo2; 11-07 license prove OK.
- Code: `hongguo_rpc`, `hongguo_license_ensure`, `hongguo_bridge`, `routes_hg.py`, `static/ui/hongguo.html`, archive `hongguo2.html`.
- DPAPI path (docs only): `%LOCALAPPDATA%\Pineline\hg_typed_key.dpapi`.
