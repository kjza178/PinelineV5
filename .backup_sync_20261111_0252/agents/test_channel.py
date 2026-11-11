"""
test_channel.py — Quản lý Kênh Phụ Test (Burner Channel) độc lập trong Pineline.

Chức năng:
- Đăng nhập Google OAuth Kênh Phụ / Gmail Test riêng (tách biệt hoàn toàn với kênh Sage Review).
- Upload clip mẫu 90s ngầm trực tiếp qua YouTube API ở chế độ Unlisted.
- Tự động chờ YouTube Content ID quét (Clean, Blocked, Claim nhạc).
- Tự động xoá video test trên YouTube sau khi có kết quả để giữ kênh test sạch.
- Hỗ trợ Test All chạy ngầm tự động theo hàng đợi.
"""
from __future__ import annotations

import json
import os
import sys
import threading
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

import check_block
import film_db
import lib_check
import importlib
try:
    lib_check = importlib.reload(lib_check)
except Exception:
    pass


def _safe_resolve_title_vi(name: str, title_vi: str = "") -> str:
    """Gọi lib_check.resolve_title_vi an toàn, tự động reload nếu module bị cache cũ."""
    global lib_check
    t_vi = (title_vi or "").strip()
    if t_vi and t_vi != name:
        return t_vi
    try:
        if not hasattr(lib_check, "resolve_title_vi"):
            import importlib
            lib_check = importlib.reload(lib_check)
        if hasattr(lib_check, "resolve_title_vi"):
            return lib_check.resolve_title_vi(name, title_vi)
    except Exception:
        pass
    return t_vi or ""


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "test_channel"
CLIENT_SECRET_FILE = DATA_DIR / "client_secret.json" if (DATA_DIR / "client_secret.json").is_file() else Path(os.getenv("TEST_YT_SECRET") or r"Z:\yt_uploader\client_secret.json")
TOKEN_FILE = DATA_DIR / "token.json"
CHANNEL_FILE = DATA_DIR / "channel.json"
PROJECTS_FILE = DATA_DIR / "projects.json"
TOKENS_DIR = DATA_DIR / "tokens"
EXHAUSTED_FILE = DATA_DIR / "exhausted.json"

os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = "1"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube",
]

_lock = threading.Lock()

# Trạng thái tiến trình Test All
BATCH_STATE: dict[str, Any] = {
    "running": False,
    "cancel": False,
    "total": 0,
    "current": 0,
    "current_name": "",
    "stage": "idle",       # "cutting", "uploading", "scheduled", "waiting_recheck", "idle"
    "step_text": "",
    "percent": 0,
    "uploaded_count": 0,
    "clean": 0,
    "blocked": 0,
    "claim": 0,
    "errors": 0,
    "started_at": "",
    "finished_at": "",
    "last_result": None,
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _utc_now_plus_minutes(minutes: int = 5) -> str:
    return (datetime.now(timezone.utc) + timedelta(minutes=minutes)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


HEALTH_FILE = DATA_DIR / "projects_health.json"
CHANNEL_LIMIT_FILE = DATA_DIR / "channel_limit.json"


def get_channel_limit_state() -> dict[str, Any]:
    """Kiểm tra xem kênh YouTube đã bị dính uploadLimitExceeded hôm nay chưa."""
    if not CHANNEL_LIMIT_FILE.is_file():
        return {"reached": False}
    try:
        data = json.loads(CHANNEL_LIMIT_FILE.read_text(encoding="utf-8"))
        if data.get("exhausted_date") == _today_utc():
            return {"reached": True, **data}
    except Exception:
        pass
    return {"reached": False}


def mark_channel_limit_reached(channel_title: str = "Sai Kira"):
    """Đánh dấu Kênh YouTube chạm giới hạn upload hôm nay."""
    CHANNEL_LIMIT_FILE.write_text(json.dumps({
        "exhausted_date": _today_utc(),
        "channel_title": channel_title,
        "reached_at": _utc_now(),
        "reason": "uploadLimitExceeded",
        "message": f"Kênh YouTube '{channel_title}' đã hết lượt upload tối đa hôm nay (uploadLimitExceeded). YouTube khóa upload 24 giờ."
    }, ensure_ascii=False, indent=2), encoding="utf-8")


def get_projects_health() -> dict[str, dict[str, Any]]:
    """Đọc dữ liệu kiểm tra tính khả dụng của từng Project."""
    if not HEALTH_FILE.is_file():
        return {}
    try:
        return json.loads(HEALTH_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def update_project_health(
    project_id: str,
    api_enabled: bool,
    channel_title: str | None = None,
    channel_id: str | None = None,
    email: str | None = None,
    enable_url: str | None = None,
    *,
    replace_identity: bool = False,
):
    """Cập nhật trạng thái API của Project.

    replace_identity=True (sau OAuth): ghi đè channel/email kể cả chuỗi rỗng,
    tránh giữ cứng tên cũ «Sai Kira» khi đổi kênh.
    """
    h = get_projects_health()
    cur = h.get(project_id) or {}
    if replace_identity:
        new_title = (channel_title or "").strip()
        new_cid = (channel_id or "").strip()
        new_email = (email or "").strip()
    else:
        new_title = (channel_title or "").strip() or cur.get("channel_title", "")
        new_cid = (channel_id or "").strip() or cur.get("channel_id", "")
        new_email = (email or "").strip() or cur.get("email", "")
    h[project_id] = {
        "api_enabled": api_enabled,
        "channel_title": new_title,
        "channel_id": new_cid,
        "email": new_email,
        "enable_url": (enable_url or "").strip() or cur.get("enable_url", ""),
        "checked_at": _today_utc(),
        "updated_at": _utc_now(),
    }
    HEALTH_FILE.write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding="utf-8")


def verify_all_projects_health(force: bool = False) -> dict[str, dict[str, Any]]:
    """Kiểm tra thực tế trạng thái YouTube API và kênh kết nối cho từng Project."""
    if not PROJECTS_FILE.is_file():
        return {}
    try:
        projs = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

    from google.auth.transport.requests import Request
    health = get_projects_health()

    for p in projs:
        pid = p["id"]
        tok_file = TOKENS_DIR / f"{pid}.json"
        if not tok_file.is_file():
            continue

        cid = p.get("client_id") or ""
        pnum = cid.split("-")[0] if "-" in cid else ""
        default_enable_url = f"https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project={pnum}" if pnum else ""

        cur = health.get(pid) or {}
        if not force and cur.get("api_enabled") and cur.get("checked_at") == _today_utc():
            continue

        try:
            creds_data = json.loads(tok_file.read_text(encoding="utf-8"))
            creds = Credentials.from_authorized_user_info(creds_data, scopes=SCOPES)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                tok_file.write_text(creds.to_json(), encoding="utf-8")
            yt = build("youtube", "v3", credentials=creds)
            res = yt.channels().list(mine=True, part="snippet").execute()
            items = res.get("items") or []
            ch_title = items[0].get("snippet", {}).get("title", "") if items else "Sai Kira"
            ch_id = items[0].get("id", "") if items else ""

            email = cur.get("email") or ""
            try:
                from googleapiclient.discovery import build as build_service
                oa = build_service("oauth2", "v2", credentials=creds)
                u = oa.userinfo().get().execute()
                email = u.get("email") or email
            except Exception:
                pass

            health[pid] = {
                "api_enabled": True,
                "channel_title": ch_title,
                "channel_id": ch_id,
                "email": email,
                "enable_url": default_enable_url,
                "checked_at": _today_utc(),
            }
            # Nếu gọi API thành công -> Xóa đánh dấu 429 quota cho project này
            ex_now = get_exhausted_projects()
            if pid in ex_now:
                ex_now.pop(pid, None)
                EXHAUSTED_FILE.write_text(json.dumps(ex_now, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception as e:
            err_s = str(e).lower()
            is_disabled = "accessnotconfigured" in err_s or "has not been used in project" in err_s
            health[pid] = {
                "api_enabled": not is_disabled,
                "channel_title": cur.get("channel_title") or "Sai Kira",
                "channel_id": cur.get("channel_id") or "",
                "email": cur.get("email") or "",
                "enable_url": default_enable_url,
                "checked_at": _today_utc(),
                "error": str(e),
            }

    HEALTH_FILE.write_text(json.dumps(health, ensure_ascii=False, indent=2), encoding="utf-8")
    return health


def get_exhausted_projects() -> dict[str, str]:
    if not EXHAUSTED_FILE.is_file():
        return {}
    try:
        return json.loads(EXHAUSTED_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def mark_project_exhausted(project_id: str):
    ex = get_exhausted_projects()
    ex[project_id] = _today_utc()
    EXHAUSTED_FILE.write_text(json.dumps(ex, ensure_ascii=False, indent=2), encoding="utf-8")


def reset_exhausted_projects(project_id: str | None = None) -> dict[str, Any]:
    """Reset cờ hết quota 429 hoặc khóa upload cho project cụ thể hoặc toàn bộ."""
    ex = get_exhausted_projects()
    if project_id:
        ex.pop(project_id, None)
    else:
        ex.clear()
        if CHANNEL_LIMIT_FILE.is_file():
            try:
                CHANNEL_LIMIT_FILE.unlink()
            except Exception:
                pass
    EXHAUSTED_FILE.write_text(json.dumps(ex, ensure_ascii=False, indent=2), encoding="utf-8")
    return get_status()


def list_projects() -> list[dict[str, Any]]:
    TOKENS_DIR.mkdir(parents=True, exist_ok=True)
    if not PROJECTS_FILE.is_file():
        return []
    try:
        projs = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

    ex = get_exhausted_projects()
    health = get_projects_health()
    today = _today_utc()
    out = []
    for p in projs:
        pid = p["id"]
        tok_file = TOKENS_DIR / f"{pid}.json"
        is_conn = tok_file.is_file()
        is_ex = (ex.get(pid) == today)
        cid = p.get("client_id") or ""
        pnum = cid.split("-")[0] if "-" in cid else ""
        default_enable_url = f"https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project={pnum}" if pnum else ""

        h = health.get(pid) or {}
        api_enabled = h.get("api_enabled", True) if is_conn else False
        enable_url = h.get("enable_url") or default_enable_url
        ch_title = h.get("channel_title") or ""
        ch_email = h.get("email") or ""

        out.append({
            "id": pid,
            "name": p.get("name") or pid,
            "client_id": cid,
            "connected": is_conn,
            "exhausted_today": is_ex,
            "api_enabled": api_enabled,
            "enable_url": enable_url,
            "channel_title": ch_title,
            "email": ch_email,
        })
    return out


# ─── Quản lý Xác thực & Tài khoản ─────────────────────────────────────────

_UPLOAD_COUNT_CACHE = {"ts": 0.0, "count_vn": 0, "count_utc": 0, "total": 0}

def get_today_uploads_count(force: bool = False) -> dict[str, int]:
    """Đếm số video đã upload trong ngày trên Kênh Test qua YouTube Data API (cache 120s, tốn chỉ 1-2 quota units)."""
    global _UPLOAD_COUNT_CACHE
    now = time.time()
    if not force and (now - _UPLOAD_COUNT_CACHE["ts"] < 120):
        return {
            "today_vn": _UPLOAD_COUNT_CACHE["count_vn"],
            "today_utc": _UPLOAD_COUNT_CACHE["count_utc"],
            "total_all": _UPLOAD_COUNT_CACHE["total"],
        }
    try:
        yt = get_read_service()
        if not yt:
            return {"today_vn": 0, "today_utc": 0, "total_all": 0}
        ch_resp = yt.channels().list(mine=True, part="snippet,contentDetails").execute()
        items = ch_resp.get("items", [])
        if not items:
            return {"today_vn": 0, "today_utc": 0, "total_all": 0}
        curr_ch = items[0]
        uploads_pl = curr_ch.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
        if not uploads_pl:
            return {"today_vn": 0, "today_utc": 0, "total_all": 0}

        # Không ghi đè CHANNEL_FILE từ project «đầu pool» — sẽ làm UI tưởng Đổi kênh
        # thất bại (ví dụ vừa OAuth proj_2 nhưng count lại kéo kênh proj_1).
        # Identity kênh chỉ cập nhật trong finish_oauth / update_project_health.

        now_utc = datetime.now(timezone.utc)
        today_utc_start = now_utc.replace(hour=0, minute=0, second=0, microsecond=0)
        today_vn_start = (now_utc + timedelta(hours=7)).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=7)

        count_vn = 0
        count_utc = 0
        total = 0
        page_token = None
        for _ in range(3):
            resp = yt.playlistItems().list(
                playlistId=uploads_pl,
                part="snippet",
                maxResults=50,
                pageToken=page_token
            ).execute()
            items = resp.get("items", [])
            if not items:
                break
            for it in items:
                total += 1
                pub_at = it["snippet"].get("publishedAt", "")
                pub_dt = datetime.fromisoformat(pub_at.replace("Z", "+00:00"))
                if pub_dt >= today_vn_start:
                    count_vn += 1
                if pub_dt >= today_utc_start:
                    count_utc += 1
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

        _UPLOAD_COUNT_CACHE = {"ts": now, "count_vn": count_vn, "count_utc": count_utc, "total": total}
        return {"today_vn": count_vn, "today_utc": count_utc, "total_all": total}
    except Exception:
        return {
            "today_vn": _UPLOAD_COUNT_CACHE["count_vn"],
            "today_utc": _UPLOAD_COUNT_CACHE["count_utc"],
            "total_all": _UPLOAD_COUNT_CACHE["total"],
        }


def get_status() -> dict[str, Any]:
    """Kiểm tra trạng thái kết nối Kênh Phụ Test và danh sách Projects."""
    projs = list_projects()
    conn_count = sum(1 for p in projs if p["connected"])
    avail_count = sum(1 for p in projs if p["connected"] and not p["exhausted_today"] and p.get("api_enabled", True))
    info = json.loads(CHANNEL_FILE.read_text(encoding="utf-8")) if CHANNEL_FILE.is_file() else {}
    connected = conn_count > 0 or TOKEN_FILE.is_file()
    ch_limit = get_channel_limit_state()
    upload_stats = get_today_uploads_count()

    return {
        "connected": connected,
        "channel_title": info.get("channel_title") or "",
        "email": info.get("email") or "",
        "channel_id": info.get("channel_id") or "",
        "connected_at": info.get("connected_at") or "",
        "last_connected_project": info.get("last_connected_project") or "",
        "channel_limit_reached": ch_limit.get("reached", False),
        "channel_limit_info": ch_limit,
        "projects": projs,
        "total_projects": len(projs),
        "connected_projects": conn_count,
        "available_projects": avail_count,
        "today_uploads": upload_stats.get("today_vn", 0),
        "today_uploads_utc": upload_stats.get("today_utc", 0),
        "total_uploads": upload_stats.get("total_all", 0),
    }


def disconnect() -> bool:
    """Ngắt kết nối Kênh Phụ Test."""
    with _lock:
        try:
            if TOKEN_FILE.is_file():
                TOKEN_FILE.unlink()
            if CHANNEL_FILE.is_file():
                CHANNEL_FILE.unlink()
            return True
        except Exception:
            return False


def get_auth_url(redirect_uri: str, project_id: str | None = None) -> dict[str, Any]:
    """Tạo URL đăng nhập Google OAuth cho Project được chọn hoặc project chưa kết nối tiếp theo."""
    TOKENS_DIR.mkdir(parents=True, exist_ok=True)
    if not PROJECTS_FILE.is_file():
        raise FileNotFoundError(f"Không tìm thấy file {PROJECTS_FILE}")

    projs = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
    if not project_id:
        for p in projs:
            if not (TOKENS_DIR / f"{p['id']}.json").is_file():
                project_id = p["id"]
                break
    if not project_id:
        project_id = projs[0]["id"]

    target_proj = next((p for p in projs if p["id"] == project_id), None)
    if not target_proj:
        raise ValueError(f"Không tìm thấy cấu hình cho project {project_id}")

    client_config = {
        "web": {
            "client_id": target_proj["client_id"],
            "client_secret": target_proj["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )
    auth_url, _ = flow.authorization_url(
        prompt="select_account consent",
        access_type="offline",
        include_granted_scopes="true",
        state=project_id,
    )
    if flow.code_verifier:
        (DATA_DIR / f"code_verifier_{project_id}.txt").write_text(flow.code_verifier, encoding="utf-8")
        (DATA_DIR / "code_verifier.txt").write_text(flow.code_verifier, encoding="utf-8")
    (DATA_DIR / "current_oauth_project.txt").write_text(project_id, encoding="utf-8")

    return {
        "ok": True,
        "auth_url": auth_url,
        "project_id": project_id,
        "project_name": target_proj.get("name") or project_id,
    }


def finish_oauth(code: str, redirect_uri: str, project_id: str | None = None) -> dict[str, Any]:
    """Hoàn tất đăng nhập OAuth và lưu token cho Project tương ứng."""
    if not project_id:
        cpf = DATA_DIR / "current_oauth_project.txt"
        if cpf.is_file():
            project_id = cpf.read_text(encoding="utf-8").strip()
    if not project_id:
        project_id = "proj_1"

    projs = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
    target_proj = next((p for p in projs if p["id"] == project_id), None)
    if not target_proj:
        raise ValueError(f"Không tìm thấy cấu hình cho project {project_id}")

    client_config = {
        "web": {
            "client_id": target_proj["client_id"],
            "client_secret": target_proj["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [redirect_uri],
        }
    }
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )

    vf = DATA_DIR / f"code_verifier_{project_id}.txt"
    if not vf.is_file():
        vf = DATA_DIR / "code_verifier.txt"
    if vf.is_file():
        try:
            flow.code_verifier = vf.read_text(encoding="utf-8").strip()
        except Exception:
            pass

    flow.fetch_token(code=code)
    if vf.is_file():
        try:
            vf.unlink()
        except Exception:
            pass

    creds = flow.credentials
    TOKENS_DIR.mkdir(parents=True, exist_ok=True)
    proj_token_file = TOKENS_DIR / f"{project_id}.json"
    proj_token_file.write_text(creds.to_json(), encoding="utf-8")
    TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    # Lấy thông tin kênh và email
    channel_title = ""
    channel_id = ""
    email = ""
    try:
        yt = build("youtube", "v3", credentials=creds)
        res = yt.channels().list(mine=True, part="snippet").execute()
        items = res.get("items") or []
        if items:
            snippet = items[0].get("snippet") or {}
            channel_title = snippet.get("title") or ""
            channel_id = items[0].get("id") or ""
    except Exception:
        pass

    try:
        from googleapiclient.discovery import build as build_service
        oauth2 = build_service("oauth2", "v2", credentials=creds)
        user_info = oauth2.userinfo().get().execute()
        email = user_info.get("email") or ""
    except Exception:
        pass

    display_title = (channel_title or "").strip() or "(chưa lấy được tên kênh — kiểm tra quyền YouTube)"
    info = {
        "channel_title": display_title,
        "channel_id": channel_id,
        "email": email,
        "connected_at": _utc_now(),
        "last_connected_project": project_id,
    }
    CHANNEL_FILE.write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    update_project_health(
        project_id=project_id,
        api_enabled=True,
        channel_title=channel_title or display_title,
        channel_id=channel_id,
        email=email,
        replace_identity=True,
    )
    return {"ok": True, "project_id": project_id, **info}


def get_available_service():
    """Lấy YouTube service từ project khả dụng đầu tiên trong pool (chưa hết quota hôm nay và đã bật API).

    Nếu mọi project còn quota đều fail auth (token chết), fallback sang project còn cờ
    exhausted — tránh kẹt ở Acc token-revoked trong khi Kênh 1/2 chỉ bị cờ local.
    """
    projs = list_projects()
    from google.auth.transport.requests import Request

    connected = [p for p in projs if p["connected"]]
    if not connected:
        raise RuntimeError("Chưa có Project nào được đăng nhập. Vui lòng bấm '🔗 Đăng nhập Kênh Test'.")

    preferred = [p for p in connected if not p["exhausted_today"] and p.get("api_enabled", True)]
    exhausted_ok = [p for p in connected if p["exhausted_today"] and p.get("api_enabled", True)]
    # Prefer quota-ok; nếu không còn / auth fail hết → thử exhausted (cờ có thể stale sau Reset Quota)
    candidates = preferred + exhausted_ok
    if not candidates:
        disabled_projs = [p for p in connected if not p.get("api_enabled", True)]
        if disabled_projs and len(disabled_projs) == len(connected):
            raise RuntimeError(
                f"Các Project ({', '.join(p['name'] for p in disabled_projs)}) "
                "chưa bật 'YouTube Data API v3' trong Google Cloud Console."
            )
        raise RuntimeError("Toàn bộ các Google Cloud Project đều đã dùng hết quota upload hôm nay.")

    errors: list[str] = []

    def _try_build(p: dict[str, Any]):
        pid = p["id"]
        name = p.get("name") or pid
        tok_file = TOKENS_DIR / f"{pid}.json"
        if not tok_file.is_file():
            raise RuntimeError(f"{name}: thiếu token")
        creds_data = json.loads(tok_file.read_text(encoding="utf-8"))
        creds = Credentials.from_authorized_user_info(creds_data, scopes=SCOPES)
        # Refresh sớm để bắt invalid_grant (token local còn hạn nhưng grant đã thu hồi).
        if creds.refresh_token:
            creds.refresh(Request())
            tok_file.write_text(creds.to_json(), encoding="utf-8")
        elif creds.expired:
            raise RuntimeError(f"{name}: access token hết hạn, không có refresh_token — đăng nhập lại")
        yt = build("youtube", "v3", credentials=creds, cache_discovery=False)
        return yt, pid

    for p in candidates:
        name = p.get("name") or p["id"]
        try:
            return _try_build(p)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            low = msg.lower()
            if "invalid_grant" in low or "revoked" in low:
                hint = "token hết hạn/bị thu hồi — mở Kênh Test → Đăng nhập lại project này"
            elif "access_denied" in low or "accessnotconfigured" in low or "has not been used" in low:
                hint = "chưa bật YouTube Data API v3 trên Google Cloud của project"
            elif "quota" in low or "ratelimitexceeded" in low or "dailylimitexceeded" in low:
                hint = "hết quota / rate limit"
            elif msg.startswith(f"{name}:"):
                hint = msg.split(":", 1)[1].strip()
            else:
                hint = msg[:180].replace("\n", " ")
            tag = " [cờ hết quota]" if p.get("exhausted_today") else ""
            errors.append(f"{name}{tag}: {hint}")
            continue

    detail = "; ".join(errors) if errors else "không có chi tiết"
    if preferred and exhausted_ok:
        detail += (
            f". Đã thử cả {len(preferred)} project còn quota và {len(exhausted_ok)} project còn cờ exhausted."
        )
    elif not preferred and exhausted_ok:
        detail += (
            f". Chỉ còn project cờ hết quota ({len(exhausted_ok)}) — bấm ⚡ Reset Quota nếu GCP còn hạn mức."
        )
    raise RuntimeError(
        "Không thể khởi tạo YouTube API từ các Project khả dụng. " + detail
    )


def get_read_service():
    """Lấy YouTube service từ bất kỳ project nào đã kết nối để đọc metadata (chỉ tốn 1 quota unit, không phụ thuộc quota upload)."""
    projs = list_projects()
    from google.auth.transport.requests import Request
    for p in projs:
        if not p.get("connected"):
            continue
        pid = p["id"]
        tok_file = TOKENS_DIR / f"{pid}.json"
        try:
            creds_data = json.loads(tok_file.read_text(encoding="utf-8"))
            creds = Credentials.from_authorized_user_info(creds_data, scopes=SCOPES)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                tok_file.write_text(creds.to_json(), encoding="utf-8")
            return build("youtube", "v3", credentials=creds)
        except Exception:
            continue
    return None


def get_youtube_service():
    """Lấy YouTube API service khả dụng."""
    yt, _ = get_available_service()
    return yt


# ─── Upload, Check Content ID & Tự động xoá ──────────────────────────────

def upload_test_sample(name: str, sample_path: str, title_vi: str = "") -> dict[str, Any]:
    """Upload clip mẫu 90s lên Kênh Phụ Test ở chế độ Unlisted, tự động xoay vòng Project khi gặp Quota 429."""
    p = Path(sample_path)
    if not p.is_file():
        return {"ok": False, "error": f"Không tìm thấy file mẫu: {sample_path}"}

    max_attempts = 5
    if not title_vi:
        title_vi = _safe_resolve_title_vi(name)

    display_title = f"[{title_vi}] {name}" if (title_vi and title_vi.strip().lower() != name.strip().lower()) else name
    title = f"[TEST_BLOCK] {display_title} ({int(time.time())})"
    body = {
        "snippet": {
            "title": title[:100],
            "description": f"Content ID Test clip for {display_title}. Unlisted temporary check.",
            "tags": ["test"],
            "categoryId": "22",
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False,
        },
    }

    for _ in range(max_attempts):
        try:
            yt, proj_id = get_available_service()
        except RuntimeError as e:
            return {"ok": False, "error": str(e)}

        try:
            media = MediaFileUpload(str(p), chunksize=256 * 1024 * 1024, resumable=True)
            req = yt.videos().insert(part="snippet,status", body=body, media_body=media)
            response = None
            while response is None:
                _, response = req.next_chunk()

            video_id = response.get("id")
            if not video_id:
                return {"ok": False, "error": "Upload không trả về video_id"}

            yt_url = f"https://youtu.be/{video_id}"
            return {"ok": True, "video_id": video_id, "yt_url": yt_url, "title": title, "project_id": proj_id}

        except Exception as e:
            err_str = str(e)
            if "uploadlimitexceeded" in err_str.lower() or "exceeded the number of videos" in err_str.lower():
                print(f"[upload-limit] Kenh cua Project {proj_id} da cham gioi han upload trong ngay (uploadLimitExceeded)! Dang chuyen sang Project tiep theo...", flush=True)
                mark_project_exhausted(proj_id)
                continue
            if "accessnotconfigured" in err_str.lower() or "has not been used in project" in err_str.lower():
                print(f"[api-disabled] Project {proj_id} chua bat YouTube Data API v3!", flush=True)
                update_project_health(proj_id, api_enabled=False)
                continue
            if "429" in err_str or "quota" in err_str.lower() or "ratelimit" in err_str.lower():
                print(f"[quota-pool] Project {proj_id} da het quota hom nay (429)! Dang chuyen sang project tiep theo...", flush=True)
                mark_project_exhausted(proj_id)
                continue
            return {"ok": False, "error": f"Loi upload ({proj_id}): {e}"}

    return {
        "ok": False,
        "channel_limit_reached": True,
        "error": "Tất cả các Kênh / Project đều đã hết quota hoặc chạm giới hạn upload hôm nay."
    }


def delete_test_video(video_id: str) -> bool:
    """Xoá video test trên YouTube sau khi đã kiểm tra xong."""
    projs = list_projects()
    from google.auth.transport.requests import Request
    for p in projs:
        if not p["connected"]:
            continue
        pid = p["id"]
        tok_file = TOKENS_DIR / f"{pid}.json"
        try:
            creds_data = json.loads(tok_file.read_text(encoding="utf-8"))
            creds = Credentials.from_authorized_user_info(creds_data, scopes=SCOPES)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            yt = build("youtube", "v3", credentials=creds)
            yt.videos().delete(id=video_id).execute()
            return True
        except Exception:
            continue
    return False


def wait_and_check_test_video(video_id: str, name: str, max_wait_sec: int = 150) -> dict[str, Any]:
    """Chờ YouTube xử lý xong video và kiểm tra bản quyền Content ID chính xác."""
    yt = get_read_service()
    if not yt:
        try:
            yt = get_youtube_service()
        except Exception:
            pass

    start_time = time.time()
    
    # Giai đoạn 1: Chờ YouTube API hoàn tất bước processing (hoặc phát hiện rejection)
    while yt and (time.time() - start_time < max_wait_sec):
        try:
            res = yt.videos().list(part="status,processingDetails,contentDetails", id=video_id).execute()
            items = res.get("items") or []
            if not items:
                break
            v_status = items[0].get("status") or {}
            v_proc = items[0].get("processingDetails") or {}
            v_content = items[0].get("contentDetails") or {}
            
            rej = v_status.get("rejectionReason")
            if rej:
                return {"status": "blocked", "reason": f"YouTube từ chối video: {rej}"}

            # Kiểm tra hạn chế vùng / quốc gia (Partially blocked) từ contentDetails
            reg = v_content.get("regionRestriction") or {}
            b_regs = reg.get("blocked") or []
            a_regs = reg.get("allowed") or []
            if b_regs:
                if len(b_regs) >= 200:
                    return {"status": "blocked", "reason": f"YouTube Content ID chặn toàn cầu ({len(b_regs)} quốc gia)"}
                else:
                    return {"status": "partially_blocked", "reason": f"Bị chặn tại một số quốc gia (Partially blocked: {', '.join(b_regs[:6])}...)"}
            elif a_regs:
                return {"status": "partially_blocked", "reason": f"Bị giới hạn chỉ xem được ở {len(a_regs)} quốc gia: {', '.join(a_regs[:6])}..."}

            upload_st = v_status.get("uploadStatus")
            proc_st = v_proc.get("processingStatus")
            
            if proc_st == "succeeded" or upload_st == "processed":
                break
            elif proc_st in ("failed", "terminated"):
                return {"status": "failed", "reason": f"YouTube xử lý video thất bại: {proc_st}"}
        except Exception:
            pass
        time.sleep(8)
        
    # Giai đoạn 2: Đợi thêm 15s để Content ID Checks hoàn tất
    time.sleep(15)
    
    # Giai đoạn 3: Kiểm tra playability qua check_block
    last_res = {"status": "unknown", "reason": "Chưa có kết quả"}
    for _ in range(5):
        last_res = check_block.check_youtube_block(video_id)
        st = last_res.get("status")
        if st in ("clean", "blocked", "partially_blocked", "claim"):
            break
        if st == "processing":
            time.sleep(10)
            continue
        break

    # Nếu check_block thấy clean, kiểm tra lại qua YouTube API 1 lần nữa để đảm bảo không bị sót partially_blocked
    if last_res.get("status") == "clean" and yt:
        try:
            res = yt.videos().list(part="status,contentDetails", id=video_id).execute()
            items = res.get("items") or []
            if items:
                v_content = items[0].get("contentDetails") or {}
                reg = v_content.get("regionRestriction") or {}
                b_regs = reg.get("blocked") or []
                a_regs = reg.get("allowed") or []
                if b_regs:
                    if len(b_regs) >= 200:
                        return {"status": "blocked", "reason": f"YouTube Content ID chặn toàn cầu ({len(b_regs)} quốc gia)"}
                    return {"status": "partially_blocked", "reason": f"Bị chặn tại một số quốc gia (Partially blocked: {', '.join(b_regs[:6])}...)"}
                elif a_regs:
                    return {"status": "partially_blocked", "reason": f"Bị giới hạn chỉ xem được ở {len(a_regs)} quốc gia: {', '.join(a_regs[:6])}..."}
        except Exception:
            pass
        
    return last_res


# ─── Kiểm tra lại sau 15 phút (Recheck Engine) ───────────────────────────

def recheck_single(name: str) -> dict[str, Any]:
    """Kiểm tra bản quyền Content ID của 1 video đã upload lên Kênh Phụ."""
    rec = film_db.get_library_block(name)
    if not rec:
        return {"ok": False, "error": f"Không tìm thấy bản ghi cho {name}"}
    vid = rec.get("test_yt_id") or ""
    yt_url = rec.get("test_yt_url") or ""
    if not vid and yt_url:
        vid = check_block.extract_video_id(yt_url)
    if not vid:
        return {"ok": False, "error": f"Không có video_id để kiểm tra cho {name}"}

    check_res = check_block.check_youtube_block(vid)
    st = check_res.get("status") or "unknown"
    reason = check_res.get("reason") or ""

    if st == "processing":
        # Video vẫn đang xử lý, hẹn lại 5 phút nữa
        next_recheck = _utc_now_plus_minutes(5)
        film_db.upsert_library_block(
            name=name,
            status="testing",
            reason=f"YouTube đang xử lý/quét: {reason}. Hẹn recheck lại sau 5 phút.",
            recheck_at=next_recheck,
        )
        return {
            "ok": True,
            "name": name,
            "status": "processing",
            "reason": reason or "YouTube đang xử lý",
            "recheck_at": next_recheck,
            "video_id": vid,
        }

    if st == "deleted" and any(k in reason.lower() for k in ("chặn", "block", "bản quyền", "copyright", "quyền sở hữu", "sở hữu trí tuệ", "khiếu nại", "takedown", "kuaikan")):
        st = "blocked"

    # Nếu watch page thấy clean, thử gọi YouTube API qua bất kỳ token khả dụng nào để phát hiện Partially Blocked (regionRestriction)
    if st == "clean":
        yt = get_read_service()
        if yt:
            try:
                res = yt.videos().list(part="status,contentDetails", id=vid).execute()
                items = res.get("items") or []
                if items:
                    v_content = items[0].get("contentDetails") or {}
                    reg = v_content.get("regionRestriction") or {}
                    b_regs = reg.get("blocked") or []
                    a_regs = reg.get("allowed") or []
                    if b_regs:
                        if len(b_regs) >= 200:
                            st = "blocked"
                            reason = f"Bị chặn toàn cầu ({len(b_regs)} quốc gia)"
                        else:
                            st = "partially_blocked"
                            reason = f"Bị chặn tại một số quốc gia (Partially blocked: {', '.join(b_regs[:6])}...)"
                    elif a_regs:
                        st = "partially_blocked"
                        reason = f"Bị giới hạn chỉ xem được ở {len(a_regs)} quốc gia: {', '.join(a_regs[:6])}..."
            except Exception:
                pass

    # Đã có kết quả rõ ràng (clean, partially_blocked, blocked, claim, deleted, failed)
    r = film_db.upsert_library_block(
        name=name,
        status=st,
        reason=reason,
        recheck_at="",  # Xoá hẹn giờ vì đã có kết quả
    )
    return {
        "ok": True,
        "name": name,
        "status": st,
        "reason": reason,
        "video_id": vid,
        "record": r,
    }


def check_and_process_pending_rechecks(force: bool = False) -> list[dict[str, Any]]:
    """Quét và kiểm tra lại các video đang chờ (mặc định kiểm tra những video đã qua 15p)."""
    pending = film_db.list_pending_rechecks()
    now_iso = _utc_now()
    results = []

    for item in pending:
        nm = item.get("name") or ""
        r_at = item.get("recheck_at") or ""
        if not nm:
            continue
        # Nếu force=True hoặc không có hẹn giờ hoặc đã tới/quá giờ hẹn
        if force or not r_at or r_at <= now_iso:
            try:
                res = recheck_single(nm)
                results.append(res)
                log_msg = f"[recheck-daemon] Da kiem tra '{nm}': {res.get('status')} ({res.get('reason')})"
                sys.stdout.buffer.write((log_msg + "\n").encode("utf-8", errors="replace"))
                sys.stdout.flush()
            except Exception as e:
                err_msg = f"[recheck-daemon] Loi kiem tra '{nm}': {e}"
                sys.stdout.buffer.write((err_msg + "\n").encode("utf-8", errors="replace"))
                sys.stdout.flush()
            time.sleep(1)

    return results


_recheck_thread: threading.Thread | None = None

def start_recheck_daemon():
    """Khởi động daemon định kỳ kiểm tra các video đến hạn 5 phút."""
    global _recheck_thread
    if _recheck_thread is not None and _recheck_thread.is_alive():
        return

    def _loop():
        while True:
            try:
                check_and_process_pending_rechecks(force=False)
            except Exception as e:
                err_msg = f"[recheck-daemon] Loi vong lap: {e}"
                sys.stdout.buffer.write((err_msg + "\n").encode("utf-8", errors="replace"))
                sys.stdout.flush()
            time.sleep(30)

    _recheck_thread = threading.Thread(target=_loop, daemon=True)
    _recheck_thread.start()


# ─── Quy trình Test 1 Phim & Test All ──────────────────────────────────────

def run_full_test_for_season(name: str, auto_delete: bool = False, wait_for_result: bool = False, title_vi: str = "") -> dict[str, Any]:
    """Thực hiện quy trình test 1 bộ phim:
    1. Cắt mẫu 90s (mất ~1s) kèm tên tiếng Việt.
    2. Upload lên Kênh Phụ Test (Unlisted) kèm tên tiếng Việt.
    3. Hẹn giờ recheck Content ID sau 5 phút.
    4. Cập nhật kết quả vào database films.db.
    """
    if not title_vi:
        title_vi = _safe_resolve_title_vi(name)

    # Bước 1: Cắt clip mẫu 90s
    cut_res = lib_check.cut_sample(name, start_sec=60, dur_sec=90, title_vi=title_vi)
    if not cut_res.get("ok"):
        return cut_res
    sample_path = cut_res["sample_path"]

    # Đánh dấu đang test
    film_db.upsert_library_block(name=name, title_vi=title_vi, status="testing", reason="Đang upload lên Kênh Phụ Test…", test_sample_path=sample_path)

    # Bước 2: Upload lên Kênh Phụ
    try:
        up_res = upload_test_sample(name, sample_path, title_vi=title_vi)
    except Exception as e:
        film_db.upsert_library_block(name=name, title_vi=title_vi, status="failed", reason=f"Lỗi upload: {e}")
        try:
            Path(sample_path).unlink(missing_ok=True)
        except Exception:
            pass
        return {"ok": False, "error": f"Lỗi upload: {e}"}

    # Luôn dọn dẹp file sample sau khi upload xong để không tốn ổ cứng
    try:
        Path(sample_path).unlink(missing_ok=True)
    except Exception:
        pass

    if not up_res.get("ok"):
        if up_res.get("channel_limit_reached") or "uploadlimitexceeded" in str(up_res.get("error", "")).lower():
            # Đây là giới hạn upload trong ngày của Kênh YouTube (24h), KHÔNG PHẢI lỗi của phim!
            film_db.upsert_library_block(name=name, title_vi=title_vi, status="unknown", reason="")
            return up_res
        film_db.upsert_library_block(name=name, title_vi=title_vi, status="failed", reason=up_res.get("error") or "Upload thất bại")
        return up_res

    video_id = up_res["video_id"]
    yt_url = up_res["yt_url"]
    proj_id = up_res.get("project_id", "")
    recheck_at_iso = _utc_now_plus_minutes(5)

    if wait_for_result:
        # Nếu yêu cầu đợi kết quả trực tiếp ngay lập tức
        check_res = wait_and_check_test_video(video_id, name)
        status = check_res.get("status") or "unknown"
        reason = check_res.get("reason") or ""
        rec = film_db.upsert_library_block(
            name=name,
            title_vi=title_vi,
            status=status,
            reason=reason,
            test_yt_url=yt_url,
            test_yt_id=video_id,
            test_sample_path=sample_path,
            recheck_at="",
        )
        if auto_delete:
            delete_test_video(video_id)
        return {
            "ok": True,
            "name": name,
            "title_vi": title_vi,
            "status": status,
            "reason": reason,
            "video_id": video_id,
            "yt_url": yt_url,
            "record": rec,
        }

    # Mặc định: Upload xong -> Hẹn giờ 5 phút -> Không block luồng
    rec = film_db.upsert_library_block(
        name=name,
        title_vi=title_vi,
        status="testing",
        reason=f"Đã upload qua {proj_id}. Đang chờ 5p YouTube duyệt Content ID...",
        test_yt_url=yt_url,
        test_yt_id=video_id,
        test_sample_path=sample_path,
        recheck_at=recheck_at_iso,
    )
    return {
        "ok": True,
        "name": name,
        "title_vi": title_vi,
        "status": "testing",
        "reason": f"Đã upload xong link test ({yt_url}). Hẹn giờ recheck sau 5 phút.",
        "video_id": video_id,
        "yt_url": yt_url,
        "recheck_at": recheck_at_iso,
        "record": rec,
    }


def _batch_worker(names: list[str], auto_delete: bool, title_vi_map: dict[str, str] | None = None):
    global BATCH_STATE
    BATCH_STATE["running"] = True
    BATCH_STATE["cancel"] = False
    BATCH_STATE["total"] = len(names)
    BATCH_STATE["current"] = 0
    BATCH_STATE["uploaded_count"] = 0
    BATCH_STATE["clean"] = 0
    BATCH_STATE["blocked"] = 0
    BATCH_STATE["claim"] = 0
    BATCH_STATE["errors"] = 0
    BATCH_STATE["started_at"] = _utc_now()
    BATCH_STATE["finished_at"] = ""
    BATCH_STATE["stage"] = "starting"
    BATCH_STATE["step_text"] = f"Khởi động tiến trình test cho {len(names)} mùa phim..."
    BATCH_STATE["percent"] = 0

    for i, nm in enumerate(names, 1):
        if BATCH_STATE.get("cancel"):
            BATCH_STATE["stage"] = "stopped"
            BATCH_STATE["step_text"] = f"⏹ Đã dừng Test All tại [{i-1}/{len(names)}]."
            break
        t_vi = (title_vi_map or {}).get(nm) or _safe_resolve_title_vi(nm)
        display_name = f"[{t_vi}] {nm}" if (t_vi and t_vi.strip().lower() != nm.strip().lower()) else nm
        BATCH_STATE["current"] = i
        BATCH_STATE["current_name"] = display_name
        BATCH_STATE["percent"] = int(((i - 1) / len(names)) * 100)

        # 1. Cắt clip 90s
        BATCH_STATE["stage"] = "cutting"
        BATCH_STATE["step_text"] = f"✂️ [{i}/{len(names)}] Đang cắt clip mẫu 90s từ {display_name}..."
        print(f"[batch-test] {BATCH_STATE['step_text']}", flush=True)

        cut_res = lib_check.cut_sample(nm, start_sec=60, dur_sec=90, title_vi=t_vi)
        if not cut_res.get("ok"):
            BATCH_STATE["errors"] += 1
            film_db.upsert_library_block(name=nm, title_vi=t_vi, status="failed", reason=f"Lỗi cắt mẫu: {cut_res.get('error')}")
            continue
        sample_path = cut_res["sample_path"]

        # 2. Upload lên Kênh Phụ
        BATCH_STATE["stage"] = "uploading"
        BATCH_STATE["step_text"] = f"📤 [{i}/{len(names)}] Đang upload clip mẫu lên Kênh Phụ: {display_name}..."
        print(f"[batch-test] {BATCH_STATE['step_text']}", flush=True)

        try:
            up_res = upload_test_sample(nm, sample_path, title_vi=t_vi)
        except Exception as e:
            BATCH_STATE["errors"] += 1
            film_db.upsert_library_block(name=nm, title_vi=t_vi, status="failed", reason=f"Lỗi upload: {e}")
            continue

        if not up_res.get("ok"):
            BATCH_STATE["errors"] += 1
            err_msg = up_res.get("error") or "Upload thất bại"
            if up_res.get("channel_limit_reached") or "uploadlimitexceeded" in err_msg.lower():
                BATCH_STATE["step_text"] = f"⚠️ {err_msg} Đã dừng batch."
                print(f"[batch-test] {BATCH_STATE['step_text']}", flush=True)
                film_db.upsert_library_block(name=nm, title_vi=t_vi, status="unknown", reason="")
                try:
                    Path(sample_path).unlink(missing_ok=True)
                except OSError:
                    pass
                break
            film_db.upsert_library_block(name=nm, title_vi=t_vi, status="failed", reason=err_msg)
            try:
                Path(sample_path).unlink(missing_ok=True)
            except OSError:
                pass
            if "hết quota" in err_msg.lower():
                BATCH_STATE["step_text"] = f"⚠️ Toàn bộ các Project đều đã hết quota hôm nay. Dừng tại bộ [{display_name}]."
                break
            continue

        video_id = up_res["video_id"]
        yt_url = up_res["yt_url"]
        proj_id = up_res.get("project_id", "")
        recheck_at_iso = _utc_now_plus_minutes(5)

        # 3. Lập lịch hẹn 5 phút
        BATCH_STATE["uploaded_count"] += 1
        BATCH_STATE["stage"] = "scheduled"
        BATCH_STATE["step_text"] = f"⏳ [{i}/{len(names)}] Đã upload {display_name} ({yt_url}). Hẹn giờ recheck sau 5 phút!"
        print(f"[batch-test] {BATCH_STATE['step_text']}", flush=True)

        film_db.upsert_library_block(
            name=nm,
            title_vi=t_vi,
            status="testing",
            reason=f"Đã upload qua {proj_id}. Đang chờ 5p YouTube duyệt Content ID...",
            test_yt_url=yt_url,
            test_yt_id=video_id,
            test_sample_path=sample_path,
            recheck_at=recheck_at_iso,
        )

        # Dọn dẹp file mẫu 90s trên ổ đĩa để giải phóng dung lượng (YouTube đã lưu clip)
        try:
            Path(sample_path).unlink(missing_ok=True)
        except OSError:
            pass

        time.sleep(2)

    BATCH_STATE["running"] = False
    BATCH_STATE["current_name"] = ""
    BATCH_STATE["percent"] = 100
    if BATCH_STATE["uploaded_count"] > 0:
        BATCH_STATE["stage"] = "waiting_recheck"
        BATCH_STATE["step_text"] = f"🎉 Đã upload xong {BATCH_STATE['uploaded_count']}/{len(names)} video! Hệ thống sẽ tự động recheck sau 5 phút."
    else:
        BATCH_STATE["stage"] = "stopped"
        if not BATCH_STATE.get("step_text") or "Đang upload" in BATCH_STATE.get("step_text"):
            BATCH_STATE["step_text"] = "⚠️ Tiến trình đã dừng: Kênh YouTube đã hết lượt upload tối đa hôm nay (uploadLimitExceeded)."
    BATCH_STATE["finished_at"] = _utc_now()
    print(f"[batch-test] {BATCH_STATE['step_text']}", flush=True)


def stop_batch_test() -> dict[str, Any]:
    """Yêu cầu dừng Test All sau item hiện tại (không kill giữa upload)."""
    if not BATCH_STATE.get("running"):
        BATCH_STATE["cancel"] = False
        return {"ok": True, "stopped": False, "message": "Không có tiến trình đang chạy."}
    BATCH_STATE["cancel"] = True
    BATCH_STATE["step_text"] = "⏹ Đang dừng sau bộ hiện tại…"
    return {"ok": True, "stopped": True, "message": "Đã gửi lệnh dừng."}


def start_batch_test(names: list[str] | None = None, limit: int = 500, auto_delete: bool = False, title_vi_map: dict[str, str] | None = None) -> dict[str, Any]:
    """Bắt đầu chạy Test All hàng loạt ngầm."""
    if not get_status().get("connected"):
        return {"ok": False, "error": "Chưa kết nối Kênh Phụ Test. Vui lòng bấm '🔗 Đăng nhập Kênh Test'."}

    if BATCH_STATE["running"]:
        return {"ok": False, "error": "Một tiến trình Test All đang chạy ngầm rồi."}

    if not names:
        # Lấy các mùa chưa test trong D:\Lib
        tested = film_db.list_library_blocks()
        candidates = []
        lib_root = lib_check.LIB_ROOT
        if lib_root.is_dir():
            for f in sorted(lib_root.iterdir(), key=lambda x: x.stat().st_mtime if x.exists() else 0, reverse=True):
                if f.is_dir():
                    st = (tested.get(f.name) or {}).get("status")
                    if not st or st in ("unknown", "failed"):
                        candidates.append(f.name)
        names = candidates[:limit]

    if not names:
        return {"ok": True, "started": False, "message": "Không có phim nào chưa test trong thư viện."}

    th = threading.Thread(target=_batch_worker, args=(names, auto_delete, title_vi_map), daemon=True)
    th.start()
    return {"ok": True, "started": True, "total": len(names), "names": names}


def get_batch_progress() -> dict[str, Any]:
    """Lấy tiến độ Test All hiện tại và thống kê số video đang chờ 15p."""
    res = dict(BATCH_STATE)
    try:
        pending = film_db.list_pending_rechecks()
        res["pending_count"] = len(pending)
        res["pending_items"] = [{"name": p["name"], "recheck_at": p.get("recheck_at"), "yt_url": p.get("test_yt_url")} for p in pending[:10]]
    except Exception:
        res["pending_count"] = 0
        res["pending_items"] = []
    return res


# Tự khởi động background recheck daemon khi file được nạp
start_recheck_daemon()
