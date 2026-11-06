# Tauri desktop — archive (đã khôi phục lên root V5)

_Archive 2026-11-02 · **Restore 2026-11-05** → root `Z:\PinelineV5\`_

Bản live hiện tại:

| Mục root | Vai trò |
|---|---|
| `src-tauri/` | Rust/Tauri v2 (product **V5**, `devUrl` `:8805`) |
| `package.json` / `node_modules/` | `@tauri-apps/cli` |
| `run_tauri.bat` | Dev window (+ tự start `server.py` nếu chưa :8805) |
| `build_tauri.bat` | Release `.msi`/`.exe` |
| `install_rust.bat` | winget Rustup |
| `desktop/tauri_www/` | `frontendDist` (redirect → :8805) |

Desktop WebView2 vẫn còn: `app_desktop.py` / `build_desktop.bat`.

Thư mục này giữ skeleton cũ (V4 nhãn) để đối chiếu — **chạy từ root**, không chạy từ archive.
