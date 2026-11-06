"""Unit test asr_spam — detect + rút + ưu tiên bản sạch."""
from asr_spam import (
    is_bg_filler_spam,
    is_phrase_loop_remnant,
    clean_filler_text,
    prefer_non_spam,
    sanitize_asr_rows,
)


def test_detect_ha_spam():
    assert is_bg_filler_spam("还是没做到" + "哈" * 50)
    assert is_bg_filler_spam("啊，啊，啊，啊，啊，啊，啊，啊，啊，啊")
    assert not is_bg_filler_spam("还是没做到。")
    assert not is_bg_filler_spam("哈哈，来得好。")  # cười ngắn OK


def test_clean_keeps_dialogue():
    t = clean_filler_text("还是没做到" + "哈" * 40 + "。")
    assert "还是没做到" in t
    assert t.count("哈") <= 6


def test_prefer_non_spam():
    a = "啊，" + "啊，" * 40
    b = "苏林对不起。"
    pick, tag = prefer_non_spam(a, b, prefer_a=True)
    assert pick == b
    assert "spam_a" in tag


def test_sanitize_heal():
    rows = [
        {"i": 0, "start": 10.0, "end": 12.0, "text": "你好。"},
        {"i": 1, "start": 20.0, "end": 22.0, "text": "啊，" + "啊，" * 30},
    ]
    # heal từ list giả lập: truyền work_dir=None → chỉ clean, không heal file
    out, info = sanitize_asr_rows(rows, heal=False)
    assert info["n_cleaned"] == 1
    assert out[1]["text"] == "啊" or out[1]["text"].count("啊") <= 3


def test_phrase_loop_remnant():
    assert is_phrase_loop_remnant("把你们全部的区域的区域")
    assert is_bg_filler_spam("把你们全部的区域的区域")
    assert not is_phrase_loop_remnant("封锁直径十公里的区域，")
    assert not is_phrase_loop_remnant("好好学习。")
    # Thoại lặp có dấu phẩy — không phải remnant loop
    assert not is_phrase_loop_remnant("不是，不是，不是。")
    assert not is_phrase_loop_remnant("我操，我操，我操。")
    assert not is_phrase_loop_remnant("啊，好痛啊，好痛啊。")


if __name__ == "__main__":
    test_detect_ha_spam()
    test_clean_keeps_dialogue()
    test_prefer_non_spam()
    test_sanitize_heal()
    test_phrase_loop_remnant()
    print("ok")

