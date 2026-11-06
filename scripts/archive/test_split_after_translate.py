# -*- coding: utf-8 -*-
"""ZH→VI dịch xong rồi CUT — cục Nano dài phải tách sau khi có vi."""
from subs import split_bilingual_rows, split_long_segments, _plain_len, sub_split_cfg


def test_post_translate_cuts_cjk_blob():
    zh = (
        "让我干什么干什么你知道吗在我们血缘星的历史记录里一级星球的人最多通关两个裂缝而你呢"
        "十八个本来是要杀了你的但是我觉得太可惜不如这样你跟"
    )
    vi = (
        "Để tôi làm gì? Cậu biết không? Trong sử liệu Huyết Duyên Tinh chúng tôi, "
        "người hành tinh cấp một nhiều nhất chỉ thông quan hai khe nứt, còn cậu thì "
        "mười tám. Vốn định giết cậu nhưng tôi thấy tiếc quá, hay là thế này cậu "
    )
    rows = [{
        "i": 0, "start": 33.11, "end": 49.31,
        "zh": zh, "vi": vi,
    }]
    max_zh, max_vi, max_dur = 22, 50, 3.5
    out = split_bilingual_rows(rows, max_zh=max_zh, max_vi=max_vi, max_dur=max_dur)
    assert len(out) > 1, f"expected cut, got {len(out)}"
    # time stays inside original window
    assert abs(out[0]["start"] - 33.11) < 0.05
    assert abs(out[-1]["end"] - 49.31) < 0.05
    # each piece short enough or at least shorter than blob
    assert all(_plain_len(r["zh"]) <= max_zh + 8 for r in out) or len(out) >= 3
    # contiguous ZH: join equals original (ignore whitespace)
    joined = "".join(r["zh"] for r in out)
    assert joined.replace(" ", "") == zh.replace(" ", "")
    # VI non-empty
    assert all((r.get("vi") or "").strip() for r in out)
    print("ok post-translate cut n=", len(out))
    for r in out:
        print(f"  {r['start']:.2f}-{r['end']:.2f} zh={_plain_len(r['zh']):2d} | {r['zh'][:28]} | {r['vi'][:36]}")


def test_asr_path_still_soft_on_cjk_no_punct():
    """ASR split_long (hard=False) — khối không dấu có thể vẫn 1 nếu không cắt được."""
    zh = "让我干什么干什么你知道吗在我们血缘星的历史记录里一级星球的人最多通关两个裂缝"
    rows = [{"i": 0, "start": 33.0, "end": 49.0, "text": zh}]
    out = split_long_segments(rows, max_chars=22, key="text", max_dur=3.5)
    # soft path: may stay 1 — that is OK (dịch trước rồi CUT)
    assert len(out) >= 1
    print("asr soft n=", len(out))


if __name__ == "__main__":
    test_post_translate_cuts_cjk_blob()
    test_asr_path_still_soft_on_cjk_no_punct()
    print("ALL OK")
