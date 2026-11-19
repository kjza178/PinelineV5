"""Auto-publish thumb: ảnh gốc = reference + typo từ title (không giữ chữ Trung poster)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import agents.auto_publisher as auto_publisher
import agents.meta_studio as meta_studio


def test_master_prompt_requires_ref_and_title_typo():
    p = meta_studio.build_master_image_prompt(
        title_vi="Thời Đình Khởi Thủ Mùa 4",
        title_zh="时停起手第四季",
        hook_texts=["THOI DINH", "KHOI THU"],
        badge_text="NEW",
        typo_color="Ice Cyan",
        font_material="fractured ice crystal",
    )
    assert "REFERENCE IMAGE MANDATE" in p
    assert "APPEARANCE SOURCE OF TRUTH" in p or "ONLY source" in p
    assert "POSE / ACTION / ENERGY" in p
    assert "POSTER TEXT CLEANUP" in p
    assert "INTEGRATED 3D LATIN TYPOGRAPHY" in p
    assert "THOI DINH" in p and "KHOI THU" in p
    assert "Ice Cyan" in p or "ice" in p.lower()
    # Không còn khối «CHARACTER & POSE:» mô tả lại áo/mặt thay ref
    assert "CHARACTER & POSE:" not in p


def test_hooks_from_series_title_not_subplot():
    """Hook thumb neo title — không lấy «CẤM ĐỊA» từ subplot LLM."""
    hooks = meta_studio.hooks_from_series_title(
        "Tôi đã là Nguyên Anh rồi, bạn lại bảo tôi mới nhập học kỳ 5",
        "我都元婴期了，你跟我说开学第五季",
    )
    assert len(hooks) == 2 and all(hooks)
    joined = " ".join(hooks).upper()
    assert "CẤM ĐỊA" not in joined and "CAM DIA" not in joined
    assert "ANH" in joined or "NHẬP" in joined or "NHAP" in joined or "HỌC" in joined


def test_get_job_reference_images_skips_frame_by_default(tmp_path, monkeypatch):
    """include_video_frame=False → chỉ poster; True mới thêm frame."""
    poster = b"\xff\xd8\xff\xe0" + b"JPEGPOSTER" * 80
    frame = b"\xff\xd8\xff\xe0" + b"JPEGFRAME!" * 80
    monkeypatch.setattr(meta_studio, "ROOT", tmp_path)
    monkeypatch.setattr(meta_studio, "_normalize_ref_jpeg", lambda b, max_dim=1024: b)
    monkeypatch.setattr(meta_studio, "_extract_best_video_frame", lambda *_a, **_k: frame)

    work = tmp_path / "work" / "job_frame"
    work.mkdir(parents=True)
    (work / "output.mp4").write_bytes(b"x" * 200)
    (work / "video.mp4").write_bytes(b"v" * 200)
    (work / "poster.jpg").write_bytes(poster)
    (work / "manifest.json").write_text(
        json.dumps({"request": {"orig_path": str(work / "video.mp4")}}),
        encoding="utf-8",
    )

    refs0 = meta_studio.get_job_reference_images(job_id="job_frame", include_video_frame=False)
    assert len(refs0) == 1 and refs0[0] == poster
    refs1 = meta_studio.get_job_reference_images(job_id="job_frame", include_video_frame=True)
    assert len(refs1) == 2 and refs1[0] == poster and refs1[1] == frame


def test_autopub_passes_allow_edits_when_poster_ref(tmp_path):
    """Có poster bytes → generate_ai_image(..., allow_edits=True, ref_images=...)."""
    dummy_video = tmp_path / "output.mp4"
    dummy_video.write_bytes(b"dummy video content")
    poster = b"\xff\xd8\xff\xe0" + b"JPEGFAKE" * 40  # đủ dài >64

    row = {
        "job_id": "test_job_ref_typo",
        "output_path": str(dummy_video),
        "status": "ready_to_upload",
        "title_vi": "Thời Đình Khởi Thủ",
        "title": "时停起手",
        "hg_name": "时停起手第四季",
    }
    mock_db_con = MagicMock()
    mock_db_con.__enter__.return_value = MagicMock()

    meta_ok = {
        "ok": True,
        "titles": ["Thời Đình Khởi Thủ - Cao Trào"],
        "best_title": "Thời Đình Khởi Thủ - Cao Trào",
        "description": "desc",
        "tags": ["a"],
        # Hook LLM lệch — auto-publish phải bỏ, neo title
        "hook_texts": ["CAM DIA THUONG CO", "THAN CUNG AM MUU"],
        "badge_text": "HOT",
        "sub_text": "Thời Đình Khởi Thủ",
        "master_image_prompt": "INTEGRATED 3D LATIN TYPOGRAPHY with CAM DIA THUONG CO",  # vẫn rebuild
        "typography_direction": {
            "text_exact": ["CAM DIA THUONG CO", "THAN CUNG AM MUU"],
            "color": "Ice Cyan",
            "effects": "fractured ice",
            "graphic_integration": "rim glow",
        },
        "thumbnail_concept": {
            "story_moment": "ancient forbidden land conspiracy",
            "visual_dna": "blue hanfu woman spirit wolf",
            "selected_concept": "Ice Cyan",
            "layout": "character right",
        },
    }

    with patch("agents.auto_publisher.load_config", return_value={"enabled": True, "privacy": "unlisted", "generate_ai_thumb": True}), \
         patch("agents.auto_publisher.film_db.get", return_value=row), \
         patch("agents.auto_publisher.film_db.query", return_value=[row]), \
         patch("agents.auto_publisher.film_db.sync_one"), \
         patch("agents.auto_publisher.film_db.connect", return_value=mock_db_con), \
         patch("agents.auto_publisher.update_auto_state"), \
         patch("agents.auto_publisher._sync_queue_state_badge"), \
         patch("agents.auto_publisher.touch_active_locks"), \
         patch("agents.meta_studio.get_series_key", return_value=("thoi_dinh", "Thời Đình Khởi Thủ")), \
         patch("agents.meta_studio.get_series_meta", return_value=None), \
         patch("agents.meta_studio.get_series_thumbnail", return_value=None), \
         patch("agents.meta_studio.generate_metadata", return_value=meta_ok), \
         patch("agents.meta_studio.get_job_reference_images", return_value=[poster]), \
         patch("agents.meta_studio.generate_ai_image", return_value=None) as mock_ai, \
         patch("agents.meta_studio.create_thumbnail") as mock_pillow, \
         patch("agents.meta_studio.save_series_thumbnail"), \
         patch("agents.meta_studio.save_series_meta"), \
         patch("agents.agent_tele_cmd._fetch_poster_bytes", return_value=poster), \
         patch("agents.auto_publisher.upload_to_youtube", return_value={"ok": True, "yt_url": "https://youtu.be/x", "video_id": "x"}):

        res = auto_publisher._publish_job_internal("test_job_ref_typo", privacy="unlisted", force=True)
        assert res.get("ok") is True
        assert mock_ai.called
        kwargs = mock_ai.call_args.kwargs
        assert kwargs.get("allow_edits") is True
        assert kwargs.get("fallback_generations") is False  # có ref → chỉ edits, không generations
        assert kwargs.get("ref_images")
        assert kwargs.get("timeout", 0) >= 300
        mock_pillow.assert_not_called()  # không Pillow
        assert len(kwargs.get("ref_images") or []) == 1  # poster-only
        prompt = mock_ai.call_args.args[0] if mock_ai.call_args.args else kwargs.get("prompt", "")
        assert "INTEGRATED 3D" in prompt
        assert "TYPOGRAPHY" in prompt
        assert "POSTER TEXT CLEANUP" in prompt or "REFERENCE IMAGE" in prompt
        assert "CAM DIA" not in prompt.upper()
        assert "THAN CUNG" not in prompt.upper()
        assert "blue hanfu" not in prompt.lower()
        assert "THOI DINH" in prompt.upper() or "THỜI ĐÌNH" in prompt.upper() or "KHOI THU" in prompt.upper()
