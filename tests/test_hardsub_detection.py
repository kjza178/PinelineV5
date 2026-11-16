import pytest
from unittest.mock import patch
from pathlib import Path
import engines.render as render


def test_no_hardsub_detected_means_no_blur():
    """
    Khi video gốc không detect có hardsub (hs_track trống và band None),
    render KHÔNG được làm blur, giữ nguyên khung hình gốc.
    """
    hs_track_empty = {"v": 1, "zone": "bottom", "n": 40, "hits": 0, "bands": []}

    vf, fx_meta = render.build_video_filter(
        W=1920,
        H=1080,
        zoom=1.0,
        ocr=[],
        srt=None,
        hardsub_blur=True,
        band=None,
        hs_track=hs_track_empty,
    )

    assert fx_meta.get("hardsub") == "none"
    assert "hbl" not in vf
    assert "[blurred]" not in vf
    assert "[hardsub]" not in vf


def test_no_hs_track_and_no_band_means_no_blur():
    """
    Khi hs_track là None và band là None, render cũng KHÔNG được làm blur.
    """
    vf, fx_meta = render.build_video_filter(
        W=1920,
        H=1080,
        zoom=1.0,
        ocr=[],
        srt=None,
        hardsub_blur=True,
        band=None,
        hs_track=None,
    )

    assert fx_meta.get("hardsub") == "none"
    assert "hbl" not in vf
    assert "[blurred]" not in vf


def test_hardsub_detected_in_hs_track_applies_blur():
    """
    Khi video có hardsub (hs_track có bands), render PHẢI thực hiện blur.
    """
    hs_track_detected = {
        "v": 1,
        "zone": "bottom",
        "n": 40,
        "hits": 30,
        "x0": 0.08,
        "x1": 0.92,
        "bands": [
            {
                "y0": 0.88,
                "y1": 0.96,
                "ranges": [[0.0, 100.0]],
            }
        ],
    }

    vf, fx_meta = render.build_video_filter(
        W=1920,
        H=1080,
        zoom=1.0,
        ocr=[],
        srt=None,
        hardsub_blur=True,
        band=None,
        hs_track=hs_track_detected,
    )

    assert fx_meta.get("hardsub") != "none"
    assert fx_meta.get("hardsub").startswith("track:")
    assert "hbl" in vf or "boxblur" in vf


def test_hardsub_detected_in_band_applies_blur():
    """
    Khi hs_track không có nhưng band tĩnh được dò thấy, render blur theo band đó.
    """
    detected_band = (0.88, 0.96, 0.10, 0.90)

    vf, fx_meta = render.build_video_filter(
        W=1920,
        H=1080,
        zoom=1.0,
        ocr=[],
        srt=None,
        hardsub_blur=True,
        band=detected_band,
        hs_track=None,
    )

    assert fx_meta.get("hardsub") != "none"
    assert "blur:" in fx_meta.get("hardsub") or "track:" in fx_meta.get("hardsub")
    assert "hbl" in vf or "boxblur" in vf


def test_force_blur_override_applies_blur_even_without_detection(monkeypatch):
    """
    Nếu cấu hình HARDSUB_FORCE_BLUR=1 thì vẫn blur đáy cố định.
    """
    monkeypatch.setenv("HARDSUB_FORCE_BLUR", "1")
    vf, fx_meta = render.build_video_filter(
        W=1920,
        H=1080,
        zoom=1.0,
        ocr=[],
        srt=None,
        hardsub_blur=True,
        band=None,
        hs_track=None,
    )

    assert fx_meta.get("hardsub") != "none"
    assert "hbl" in vf or "boxblur" in vf
