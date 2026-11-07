# Review — Hongguo 2.x license prove stack portability (other Windows PCs)

- **Date:** 2026-11-07
- **Scope:** Can Pineline browse / download Hongguo on a **second Windows PC** with the current prove stack? No secrets in this doc.
- **Inputs:** `Z:\PinelineV2\hongguo_rpc.py`, `hongguo_license_ensure.py`, `D:\PinelineV2_tmp\HgLicLive\Program.cs`, live layout `%LOCALAPPDATA%\HongguoWinUI\current`, durable patch tree `D:\PinelineV5_tmp\HgLicActivate_patch`, related [license prove review](./2026-11-07-hongguo-license-prove-review.md)
- **Constraint:** Legitimate user-owned key only. Paths and component names only — no key/token/proof bodies.

## Verdict (short)

| Mode | Portable today? | Must exist on new PC |
|------|-----------------|----------------------|
| **Browse-only** (search/rank/library via 2.x RPC) | Yes, if WinUI **engine** present | Pineline + `%LOCALAPPDATA%\HongguoWinUI\current\engine` (`java.exe` + `helper.jar`) or `HG_ENGINE_DIR` |
| **Download** (`downloads.add` / `downloadNewSeasons`) | **Partial / fragile** | Browse deps + DPAPI key (re-onboard) + activate host + **WinUI `current` Licensing stack** (net10) |

Shipping only the patched `%TEMP%` host is **not** enough. Each download PC still needs Hongguo WinUI 2.x (or an equivalent `current` tree) plus a **locally** DPAPI-wrapped key. `%TEMP%\HgLicActivate_patch` is already wiped on the authoring machine (`temp_patch=False`) while a ~294 MB copy remains under `D:\PinelineV5_tmp\HgLicActivate_patch`.

---

## Stack map (what talks to what)

```
Pineline :8801
  ├─ hongguo_rpc ──spawn──► LOCALAPPDATA\HongguoWinUI\current\engine
  │                         (bundled JRE + helper.jar JSON-RPC stdio)
  │                         browse OK without license; download needs proof in THIS process
  └─ hongguo_license_ensure
        ├─ DPAPI blob  LOCALAPPDATA\Pineline\hg_typed_key.dpapi  (CurrentUser)
        ├─ localhost HTTP bridge → same hongguo_rpc helper (challenge/prove)
        └─ HgLicActivate.exe (cwd = host dir)
              apphost patched to load HgLicProbe00.dll
              reflects Hongguo.Licensing from WinUI folder (source hardcodes …\HongguoWinUI\current)
              ActivateAsync(key) → IProofChannel → HTTP bridge → license.prove
```

Evidence on authoring PC (2026-11-07):

- `HongguoWinUI.exe` size **=** `HgLicActivate.exe` (495 616) — classic apphost rename/patch.
- Activate apphost ASCII contains `HgLicProbe00`; stock WinUI apphost does not.
- Both WinUI and patch `*.runtimeconfig.json`: **`tfm: net10.0`**, `includedFrameworks` → `Microsoft.NETCore.App` **10.0.12** (self-contained style).
- Prior prove review: plain **net8 host FAIL**; Licensing load needs **net10 WinUI host**.
- `HgLicLive` `Program.cs` still has `WinUi = @"…\HongguoWinUI\current"` and `DirAlc` loads `Hongguo.Licensing.dll` / BouncyCastle / `System.Net.Http` from that directory.
- Default activate path in Python: `%TEMP%\HgLicActivate_patch\HgLicActivate.exe` (`HG_LIC_ACTIVATE_EXE` override). That TEMP tree is **gone**; durable rebuild source ≈ `D:\PinelineV5_tmp\HgLicActivate_patch` (~310 files, ~294 MB, **no** `engine\` — engine stays under WinUI install ~62 MB).

---

## 1. Browse-only vs download — checklist for another machine

### Browse-only (no prove)

Must exist:

1. **Pineline** with `hongguo_rpc` / `hongguo_bridge` (`HG_BACKEND=rpc|auto`).
2. **Hongguo 2.x engine** at  
   `%LOCALAPPDATA%\HongguoWinUI\current\engine\`  
   with `runtime\bin\java.exe` + `lib\helper.jar` (+ `lib\*`, signer/ffmpeg/native as shipped).  
   Or set **`HG_ENGINE_DIR`** to a portable copy of that engine folder.
3. Network reachability for helper / explorer APIs as used by bridge.

Does **not** need:

- `hg_typed_key.dpapi`
- `HgLicActivate` / `HgLicProbe00`
- Successful `license.prove`

Gate evidence: prove review — browse/search/rank/library OK with `license.status=none`; download RPC returns `-32010` / `no_proof` until prove.

Fallback without 2.x engine: `HG_BACKEND=http` + Hongguo **1.x** `:8000` (separate install/ops; not a 2.x prove solution).

### Download (prove + add / downloadNewSeasons)

Everything for browse, **plus**:

1. **User license key** stored only as DPAPI at  
   `%LOCALAPPDATA%\Pineline\hg_typed_key.dpapi`  
   (entropy label `Pineline/hongguo-key/v1` — not a secret by itself).
2. **Activate host** reachable via `HG_LIC_ACTIVATE_EXE` or default TEMP path: at least `HgLicActivate.exe` + `HgLicProbe00.dll` (+ matching `HgLicProbe00.runtimeconfig.json` / deps as required by the host).
3. **Hongguo WinUI `current` tree** with `Hongguo.Licensing.dll` and loadable deps (probe `DirAlc` target). Today that means a normal WinUI 2.x install under LOCALAPPDATA (same major as authoring: **net10** self-contained).
4. Outbound HTTPS to Hongguo license/pay hosts used by `LicenseClient` (see prove review: api/pay hosts).
5. Pineline process that can open a short-lived **127.0.0.1** HTTP bridge while the activate host runs.

Optional: WinUI UI itself need not be open; helper reuse across WinUI↔Pineline is dead (separate java stdio).

---

## 2. Is shipping the patched TEMP host enough?

**No.**

| Piece | Ship TEMP/`HgLicActivate_patch` alone? | Why |
|-------|----------------------------------------|-----|
| RPC helper | No | Lives under WinUI `current\engine` (not in the ~294 MB patch tree). Need install or `HG_ENGINE_DIR`. |
| `Hongguo.Licensing` load | No (current code) | `HgLicLive` hardcodes `…\HongguoWinUI\current`. Adjacent DLL in patch folder is unused unless probe is rebuilt to use `BaseDirectory` / `HG_WINUI_DIR`. |
| .NET 10 runtime | Patch folder is self-contained **if** you ship the full tree | Still coupled to WinUI’s **net10.0.12** layout; stock machine-wide `dotnet` net8 is insufficient for this host design. |
| DPAPI key | No | Per user+machine; must re-protect on the new PC. |
| Stability | TEMP is wrong home | Authoring PC: `%TEMP%\HgLicActivate_patch` already missing. |

**Practical rule:** each download PC should have **Hongguo WinUI 2.x installed** (provides `engine` + `Hongguo.Licensing` + matching apphost/runtime). Pineline should ship only a **small overlay** (patched apphost + `HgLicProbe00.dll` + thin configs), not rely on TEMP, and rebuild overlay when WinUI updates.

Copying the entire 294 MB patch tree to another PC without WinUI still fails browse (no engine) and fails prove until probe paths are fixed to load Licensing from the shipped directory.

---

## 3. DPAPI key onboarding (safe, no cross-machine blob copy)

`ProtectedData` scope = **`CurrentUser`** (see `hongguo_license_ensure._unprotect_key`). Blob is useless on another Windows user or PC.

**Do:**

1. On the new PC, under the same Windows account that runs Pineline, run a **one-shot** protect step: typed key → `ProtectedData.Protect(..., CurrentUser, entropy)` → write `%LOCALAPPDATA%\Pineline\hg_typed_key.dpapi`.
2. Prefer interactive paste / secure prompt in a Pineline “Set Hongguo key” action; never commit key or `.dpapi` to shared zips/git.
3. Confirm with `ensure_licensed()` / `license.status` ∈ `{licensed, grace}` — do not log key length beyond coarse diagnostics already redacted in activate logs.
4. Re-onboard after Windows profile reset or new user account.

**Do not:**

- Copy `hg_typed_key.dpapi` between machines “as portable config”.
- Leave `HG_TYPED_KEY` in user/system env permanently (ensure only injects into activate child env briefly).
- Store raw key in worklog, CHANGELOG, or shared folders.

---

## 4. Risks

| Risk | Detail | Mitigation |
|------|--------|------------|
| **WinUI update breaks patched apphost** | Overlay is a renamed/patched `HongguoWinUI.exe`; update replaces `current`, may change deps / TFM / assembly layout. Probe reflection assumes Licensing type surface. | Record WinUI version/hash next to tools; rebuild overlay after update; smoke `ensure_licensed`. |
| **`%TEMP%` wiped** | Default path under TEMP; already absent on authoring PC. | Default to `%LOCALAPPDATA%\Pineline\tools\HgLicActivate\`; keep `HG_LIC_ACTIVATE_EXE`. |
| **net10 runtime coupling** | Host + WinUI `includedFrameworks` 10.0.12; net8 probe path failed historically. | Stay on WinUI’s self-contained host; don’t “simplify” to framework-dependent net8. |
| **Hardcoded WinUI path in probe source** | Machine-specific absolute path in `HgLicLive`. | Rebuild with `HG_WINUI_DIR` / `LOCALAPPDATA\HongguoWinUI\current` resolution before multi-PC ship. |
| **Helper license TTL / process death** | Proof is per Pineline-spawned helper; kill/idle restart clears status. | `ensure_licensed` before download; optional force re-prove. |
| **Legal/ops** | Overlay patches vendor apphost. | Keep for owned license automation only; prefer official APIs if Hongguo ships a supported CLI later. |

---

## 5. Recommended packaging for Pineline

### Layout

```
%LOCALAPPDATA%\Pineline\
  hg_typed_key.dpapi          # per-PC, never ship
  tools\HgLicActivate\        # durable overlay (not TEMP)
    HgLicActivate.exe         # patched apphost
    HgLicProbe00.dll
    HgLicProbe00.runtimeconfig.json
    HgLicProbe00.deps.json    # if required
    BUILD_META.json           # winui version, hash, built_at (no secrets)

# Optional for air-gap recreate (large):
Pineline\tools\HgLicActivate_full\   # last-known-good full self-contained tree (~300MB)
```

Code defaults:

- `HG_LIC_ACTIVATE_EXE` → LocalAppData tools path above.
- `HG_ENGINE_DIR` → optional portable engine; else WinUI `current\engine`.
- Probe: resolve WinUI dir = `HG_WINUI_DIR` or `%LOCALAPPDATA%\HongguoWinUI\current` (never hardcode one username).

### Build script (sketch)

1. Require installed WinUI `current` (check `Hongguo.Licensing.dll` + `engine\lib\helper.jar`).
2. `dotnet publish` HgLicLive → managed `HgLicProbe00.dll` compatible with WinUI’s net10 host (same pattern as today: run under patched apphost, not a lone net8 exe).
3. Copy `HongguoWinUI.exe` → `tools\HgLicActivate\HgLicActivate.exe`; patch apphost managed entry name → `HgLicProbe00` (existing method).
4. Copy minimal runtimeconfig/deps beside host.
5. Write `BUILD_META.json` (WinUI file version / hash).
6. Smoke: unprotect key present → `ensure_licensed` → `license.status` licensed (CI/manual on each PC after onboard).

### Fallback ladder

1. **Primary:** tools overlay + installed WinUI 2.x + DPAPI key → prove → download RPC.
2. **Host missing:** error `missing_activate_host` with path hint; offer “rebuild overlay” script from current WinUI.
3. **Key missing:** `missing_key` → onboard UI (no download).
4. **Prove/update break:** clear `need_license`; keep browse.
5. **Ops escape:** `HG_BACKEND=http` (1.x) or manual download in WinUI → Pineline merge from save folder (already documented escape hatch).

### What not to package

- Raw typed key, proof bodies, `license.dat` contents.
- Assumption that TEMP survives reboot/cleaner.
- Single zip that claims “download-ready” without WinUI engine + local DPAPI onboard steps.

---

## Answers to the five questions

1. **Browse:** Pineline + WinUI `current\engine` (or `HG_ENGINE_DIR`). **Download:** that + DPAPI key + activate host + WinUI Licensing/`current` (net10) + network to license API.
2. **Patched TEMP host alone:** insufficient. Need WinUI 2.x (engine + Licensing path) on each PC; TEMP is non-durable.
3. **DPAPI:** re-protect typed key on the new user/PC into `Pineline\hg_typed_key.dpapi`; never copy the blob across machines.
4. **Risks:** WinUI updates break apphost/reflection; TEMP wipe (already observed); hard net10 self-contained coupling; hardcoded WinUI path in probe source.
5. **Packaging:** durable `%LOCALAPPDATA%\Pineline\tools\HgLicActivate\` + build script from installed WinUI + path env vars + fallbacks (rebuild / http 1.x / manual WinUI download).

## Liên quan

- `hongguo_license_ensure.py` — `_KEY_PATH`, `_ACTIVATE_EXE`, HTTP bridge
- `hongguo_rpc.py` — `DEFAULT_ENGINE_DIR`, `_ensure_licensed_quiet` on submit/downloadNewSeasons
- `D:\PinelineV2_tmp\HgLicLive` — probe source
- `D:\PinelineV5_tmp\HgLicActivate_patch` — last full overlay tree (not TEMP)
- Docs: `docs/reviews/2026-11-07-hongguo-license-prove-review.md`, worklog 2026-11-07 ~21:45
