"""Unit tests — merge hardsub text into ASR timing."""
from hardsub_asr import merge_hardsub_into_asr, zh_sim, _samples_to_cues


def test_zh_sim_basic():
    assert zh_sim("先下手为强", "先下手为强，") == 1.0
    assert zh_sim("嘲讽看", "嘲讽") >= 0.5
    assert zh_sim("你好", "世界") < 0.3


def test_samples_to_cues_groups():
    samples = [
        (1.0, "可恶"),
        (1.5, "可恶"),
        (2.0, "这家伙有追踪手段"),
        (2.5, "这家伙有追踪手段"),
        (5.0, "既然跑不掉"),
    ]
    cues = _samples_to_cues(samples, gap=0.6)
    assert len(cues) == 3
    assert "追踪" in cues[1]["zh"]


def test_merge_replaces_on_overlap():
    asr = [
        {"i": 1, "start": 1.0, "end": 2.0, "text": "可亚，"},  # ASR lệch
        {"i": 2, "start": 5.0, "end": 6.0, "text": "hello"},
    ]
    hs = [
        {"start": 0.9, "end": 2.2, "zh": "可恶，"},
        {"start": 10.0, "end": 11.0, "zh": "别的"},
    ]
    out, st = merge_hardsub_into_asr(asr, hs, min_sim=0.55)
    assert st["replaced"] >= 1
    assert "恶" in out[0]["text"]
    assert out[0].get("text_asr") == "可亚，"
    assert out[1]["text"] == "hello"


def test_merge_keeps_longer_asr_when_hs_fragment():
    asr = [{"i": 1, "start": 3.4, "end": 7.0, "text": "可恶，这家伙有追踪手段。"}]
    hs = [{"start": 4.5, "end": 5.7, "zh": "这家伙有追踪手段"}]
    out, st = merge_hardsub_into_asr(asr, hs, min_sim=0.55)
    assert out[0]["text"] == "可恶，这家伙有追踪手段。"
    assert st["replaced"] == 0


def test_merge_rejects_neighbor_line():
    """Không lấy câu hardsub bên cạnh chỉ vì overlap thời gian."""
    asr = [{"i": 1, "start": 9.8, "end": 11.0, "text": "那就放手一搏，"}]
    hs = [
        {"start": 9.0, "end": 11.5, "zh": "这个二星星球的人有什么不一样"},
        {"start": 8.0, "end": 9.5, "zh": "那就放手一搏"},
    ]
    out, st = merge_hardsub_into_asr(asr, hs, min_sim=0.55)
    # ASR đã đúng chữ (chỉ khác dấu câu) → giữ nguyên, không thay bằng câu bên cạnh
    assert out[0]["text"] == "那就放手一搏，"
    assert "二星" not in out[0]["text"]
    assert st["replaced"] == 0


if __name__ == "__main__":
    test_zh_sim_basic()
    test_samples_to_cues_groups()
    test_merge_replaces_on_overlap()
    print("ok")
