# Design review — Hongguo 2.x license prove (legitimate only)

- **Date:** 2026-11-07
- **Scope:** Unlock `downloads.add` / `library.downloadNewSeasons` on Pineline’s **own** RPC helper
- **Inputs:** [RPC bridge spec](../superpowers/specs/2026-11-07-hongguo-rpc-bridge-design.md) · `Z:\PinelineV2\hongguo_rpc.py` · worklog 2026-11-07 (~21:10–21:25)
- **Constraint:** User owns a paid Hongguo license. No crack / steal / memory dump.

## Verdict

**Ship MVP = official challenge → Ed25519 prove with the user’s key** (via `Hongguo.Licensing` or equivalent supported signing path), then call download RPC. Do **not** bet on `license.dat` restore or `license.set mode=free`. Keep browse paths as-is (already work unlicensed).

### Follow-up — helper reuse (agent test)

Live map: WinUI PID owns helper `java` via exclusive stdio; Pineline `:8801` owns a **second** `java` (same cmdline, `license=none`). No TCP/named-pipe/file IPC; `-XX:+DisableAttachMechanism`; wrapping `java.exe` blocked by 156-file integrity. **Helper reuse = dead.** Escape hatch without prove: WinUI downloads → Pineline merge from save folder.

### Follow-up — DPAPI restore (agent test)

Decrypt OK; `token`/`key`/`deviceSecret` null; only one blob; mtime unchanged ~89m while WinUI live. Any `license.restore {token:{…}}` → `-32012 clock_untrusted` before validate; fake prove → `bad_signature`. **Disk restore = dead** until real prove.

### Follow-up — alt stores (agent test)

No CredMan/PasswordVault/Paddle artifacts; no Pineline `HG_*` persisted. 1.x `licenses.json` / `offline_licenses.json` look `active` but **`:8000` down**; WinUI log *Import: no key in the other Hongguo apps* → 1.x keys ≠ 2.x prove. Downloader `license.json` = `device_id` only.

### Follow-up — Hongguo.Licensing prove (agent test)

DLL load **PASS** under WinUI **net10** host (plain net8 FAIL). `IProofChannel` assignable; API hosts `api.hongguodownloader.com` / `pay.hongguodownloader.com`. Prove payload = `ProveParams{Nonce,Ts,Sig,Kid,Body}` (not free-form). Store path expected `%LOCALAPPDATA%\HongguoWinUI\license.dat` — on this PC credentials empty / null (note also `Hongguo.WinUI\license.dat` DPAPI blob with null token). **Real prove blocked by missing Key/OfflineToken**, not by RPC. Sketch: `RpcProofChannel` → `hongguo_rpc` + `LicenseClient.Start` / one-time `ActivateAsync(key)`.

### Follow-up — prove với key user (~21:45) **PASS**

Activate Ok; `license.prove` OK khi challenge+prove cùng helper (HTTP bridge / daemon). `license.status=licensed`; `downloadNewSeasons` hết `no_proof`. Module `hongguo_license_ensure` + DPAPI key store (path only in docs).

## Evidence (frozen)

| Fact | Implication |
|------|-------------|
| Browse / search / rank / library OK without proof | License gate is **download-only** |
| `downloads.add` / `downloadNewSeasons` → `-32010` `no_proof` | Bridge helper starts `license.status=none` |
| WinUI proves Ed25519 to **its** helper (~10 min) | Bridge spawn is a **separate** process → no shared proof |
| `license.dat` DPAPI OK but `token` / `key` / `deviceSecret` = null | Disk blob ≠ restorable token object |
| `license.restore` needs `token:{…}` + trusted clock (after prove) | Restore is **secondary**, not bootstrap |
| `license.set mode=free` does **not** unlock downloads | Free mode is a dead end for MVP |
| Fake `license.prove` → `bad_signature` | Helper verifies signatures for real |

## 1. Ranked options (best → worst)

| Rank | Option | Effort | Risk | Needs user key? | Notes |
|------|--------|--------|------|-----------------|-------|
| **1** | **Legitimate prove:** `license.challenge` → sign with owned key (`Hongguo.Licensing` / WinUI-equivalent signer) → `license.prove` → then download | M (1–2d spike + wire) | Low legal / med tech (API surface unknown) | **Yes** | Matches how WinUI does it; re-prove on TTL/~10m or before download |
| **2** | **Prove then `license.restore`** with in-memory token for helper restart | M–H | Low if token never logged | **Yes** (same as #1) | Persistence layer on top of #1; disk alone insufficient today |
| **3** | **Fallback `HG_BACKEND=http` (1.x `:8000`)** for download only | L (already in bridge) | Med ops (dual engines) | 1.x license model | Unblocks pipeline without 2.x prove; not a 2.x solution |
| **4** | **Drive WinUI UI / already-licensed helper** (automation of the app, not bridge stdio) | H | High fragility / focus steal | Indirect | Avoid attaching to WinUI stdin |
| **5** | **Manual download in WinUI**; Pineline browse-only | None | None product | No | Fine for browse MVP; fails feed/auto-download |

**Recommendation:** implement **#1** as MVP; keep **#3** as documented escape hatch until prove is green; treat **#2** as follow-up once token shape is known from a successful prove.

## 2. What NOT to do

- Forge / crack Ed25519 proofs or strip helper verification.
- Hijack / steal WinUI **stdin** of the running licensed helper.
- Dump process memory / debug attach to extract keys or live tokens.
- Treat DPAPI `license.dat` as a secret dump target for offline reuse of null-token blobs.
- Expect `license.set mode=free` to unlock `downloadNewSeasons`.
- Log or commit license keys, proofs, or token objects (config var names only in docs).

## 3. Minimal MVP (download via bridge)

Goal: one successful `downloads.add` **or** `library.downloadNewSeasons` on bridge helper without touching WinUI stdio.

1. **Config (user-owned):** secure local store for Hongguo license key (DPAPI / existing secrets pattern). Never echo in logs / ping.
2. **`ensure_licensed()`** in `hongguo_rpc` (before submit / downloadNewSeasons):
   - `license.status` → if already licensed / has proof → return
   - else `license.challenge` `{purpose: licence}` → `(nonce, deviceId)`
   - sign via **official** `Hongguo.Licensing` path with user key → `proof`
   - `license.prove` `{proof, nonce, deviceId}` → expect licensed (not `bad_signature`)
3. **Gate:** `submit` / `library_download_new_seasons` call `ensure_licensed()`; keep existing `-32010` → `need_license` mapping if key missing.
4. **TTL:** re-prove before download if status degraded, or on a conservative interval (WinUI ~10m is a hint, not a hard contract).
5. **Out of MVP:** UI skin 2.x, `license.restore` persistence, attaching to WinUI process, changing browse APIs.

## 4. Test plan checklist (MVP)

- [ ] Helper cold start: `license.status` = `none` (baseline).
- [ ] No key configured → `downloads.add` / `downloadNewSeasons` → clear `need_license` (no hang).
- [ ] With user key: `challenge` → prove → `license.status` ≠ `none` / shows licensed.
- [ ] Bad / truncated proof → `bad_signature`; status still none; no download.
- [ ] After prove: `downloads.add` with one owned `seriesId` → accepted (not `-32010`).
- [ ] After prove: `library.downloadNewSeasons` → not `-32010` (may be empty jobs OK).
- [ ] `downloads.snapshot` shows queued/active after add.
- [ ] Kill helper / respawn → prove again required (or restore path if later implemented).
- [ ] Prove without prior trusted clock path: no stuck `clock_untrusted` on download path (prove-first).
- [ ] Confirm `license.set mode=free` still does **not** unlock (regression guard).
- [ ] Logs/redaction: no key, proof, or token body in worklog / CHANGELOG / API errors.
- [ ] Browse suite still green without license (ping/search/rank/library).
- [ ] `/api/hg/submit` end-to-end through bridge with `HG_BACKEND=rpc|auto`.

## 5. Open questions (user)

1. Cho phép implement phase prove bằng **Hongguo key bạn đã mua**? → **yes / no**
2. Key lấy từ đâu? → **paste một lần vào config** / **file path** / **chỉ có trong WinUI (chưa export được)**
3. MVP timing prove? → **mỗi lần spawn helper** / **chỉ trước download**
4. Giữ fallback **1.x HTTP `:8000`** khi prove chưa xong? → **yes / no**
5. OK gọi **`Hongguo.Licensing.dll`** (host .NET/Python) thay vì reverse protocol? → **yes / no**

## Liên quan

- Spec phase sau: `license.restore` từ disk — **revise**: disk alone insufficient; restore after live prove/token only.
- Code already surfaces `need_license`: `hongguo_rpc.submit` / `library_download_new_seasons`.
- WinUI path: `Hongguo.Licensing.dll` under `HongguoWinUI\current\`.
