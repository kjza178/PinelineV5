import sys
sys.path.insert(0, r"Z:\PinelineV2")
from check_block import check_youtube_block

vids = [
    ("Variant A", "5A0cdccXruo"),
    ("Variant B", "IEbe0rITuG4"),
    ("Variant C", "MGrBarGXD5k"),
    ("Variant D", "YQ9EsDCSmb8"),
]

for name, vid in vids:
    res = check_youtube_block(vid)
    is_blocked = res.get("is_blocked")
    reason = str(res.get("reason", "")).encode("ascii", "replace").decode("ascii")
    print(f"[{name}] {vid} -> Blocked: {is_blocked} | {reason}")
