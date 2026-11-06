# -*- coding: utf-8 -*-
"""Test asr_compare — Nano vs Para + OCR trọng tài."""
from asr_compare import compare_tracks, consensus_rows


def test_agree_keeps_nano():
    a = [{"start": 0.0, "end": 2.0, "text": "我从很远很远的血岩星来的"}]
    b = [{"start": 0.1, "end": 2.1, "text": "我从很远很远的血岩星来的，"}]
    r = compare_tracks(a, b, a_name="nano", b_name="para")
    assert r["stats"]["agree"] == 1
    assert r["items"][0]["pick_from"] == "nano"


def test_disagree_ocr_picks_better():
    a = [{"start": 0.0, "end": 2.0, "text": "血炎星圣斩水梦"}]
    b = [{"start": 0.0, "end": 2.0, "text": "血岩星盛产水吗"}]
    ocr = [{"start": 0.0, "end": 2.0, "text": "血炎星圣斩水梦"}]
    r = compare_tracks(a, b, ocr, a_name="nano", b_name="para")
    assert r["stats"]["disagree"] == 1
    assert r["items"][0]["pick"] == "血炎星圣斩水梦"
    assert r["items"][0]["pick_from"] in ("nano", "ocr")


def test_disagree_ocr_picks_b():
    a = [{"start": 1.0, "end": 3.0, "text": "血炎星圣斩水梦让你脑子进水"}]
    b = [{"start": 1.0, "end": 3.0, "text": "让你脑子进水了"}]
    ocr = [{"start": 1.0, "end": 3.0, "text": "让你脑子进水了"}]
    r = compare_tracks(a, b, ocr, a_name="nano", b_name="para")
    it = r["items"][0]
    assert it["status"] == "disagree"
    assert it["pick_from"] in ("para", "ocr")
    assert "进水了" in it["pick"]


def test_only_b_listed_not_auto_insert():
    a = [{"start": 0.0, "end": 1.0, "text": "可恶"}]
    b = [
        {"start": 0.0, "end": 1.0, "text": "可恶"},
        {"start": 5.0, "end": 7.0, "text": "额外一句只在B"},
    ]
    r = compare_tracks(a, b)
    assert r["stats"]["only_b"] == 1
    cons = consensus_rows(r)
    assert len(cons) == 1  # không chèn only_b (tránh nhân bản)


def test_shifted_dup_not_created():
    """A có 1 câu; B cùng chữ lệch giờ — only khớp 1, không nhân."""
    a = [{"start": 25.0, "end": 28.0, "text": "我从很远很远的血岩星来的"}]
    b = [
        {"start": 25.0, "end": 28.0, "text": "我从很远很远的血岩星来的"},
        {"start": 40.0, "end": 44.0, "text": "我从很远很远的血岩星来的"},
    ]
    r = compare_tracks(a, b)
    cons = consensus_rows(r)
    assert len(cons) == 1
    assert r["stats"]["only_b"] == 1  # bản 40s nằm only_b, không chèn


if __name__ == "__main__":
    test_agree_keeps_nano()
    test_disagree_ocr_picks_better()
    test_disagree_ocr_picks_b()
    test_only_b_listed_not_auto_insert()
    test_shifted_dup_not_created()
    print("ok")
