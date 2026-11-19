"""Meta Studio: decode poster_b64 (Up ảnh gốc) + films API shape."""
from __future__ import annotations

import base64
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _tiny_jpeg_b64() -> tuple[bytes, str]:
    from PIL import Image

    im = Image.new("RGB", (48, 48), (30, 120, 200))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=85)
    raw = buf.getvalue()
    return raw, base64.b64encode(raw).decode("ascii")


def test_decode_poster_b64_meta_studio():
    import agents.meta_studio as meta_studio

    raw, b64 = _tiny_jpeg_b64()
    assert meta_studio.decode_poster_b64(b64) == raw
    assert meta_studio.decode_poster_b64("data:image/jpeg;base64," + b64) == raw
    assert meta_studio.decode_poster_b64("") is None
    assert meta_studio.decode_poster_b64("@@@") is None


def test_routes_films_list_ok_shape():
    """Router phải trả ok=true giống sidecar (films_ui kiểm d.ok)."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    import http_routes.routes_films as routes_films

    app = FastAPI()
    app.include_router(routes_films.router)
    client = TestClient(app)
    r = client.get("/films?limit=2")
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert "films" in data
    assert "stats" in data
    r2 = client.get("/api/films?limit=1")
    assert r2.status_code == 200
    assert r2.json().get("ok") is True
