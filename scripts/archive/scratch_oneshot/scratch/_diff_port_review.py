# -*- coding: utf-8 -*-
import difflib
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

markers = [
    "queue/jobs/sort",
    "queue/jobs/move",
    "queue/jobs/reorder",
    "split-parts",
    "split-plan",
    "merge-parts",
    "combineCheckedLibrary",
    "combineSeriesSeasons",
    "generate-title",
    "ai-image",
    "meta/baike",
    "doFetchBaike",
    "btn-fetch-baike",
    "sortQueue",
    "moveJob",
    "generate_youtube_titles",
    "generate_ai_image",
]

print("=== UI MARKERS ===")
for name in ["films_ui.html", "index.html", "index3.html", "static/app.js"]:
    for root in [r"z:/PinelineV2", r"z:/PinelineV4"]:
        p = pathlib.Path(root) / name
        if not p.exists():
            print(pathlib.Path(root).name, name, "MISSING")
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        found = [m for m in markers if m in t]
        print(f"{pathlib.Path(root).name}/{name}: bytes={p.stat().st_size} hit={found}")
    print("---")

print("=== meta_studio funcs ===")
for root in [r"z:/PinelineV2", r"z:/PinelineV4"]:
    t = (pathlib.Path(root) / "meta_studio.py").read_text(encoding="utf-8", errors="replace")
    for fn in [
        "def generate_youtube_titles",
        "def generate_ai_image",
        "def generate_metadata",
        "def get_film_story_info",
    ]:
        print(pathlib.Path(root).name, fn, fn in t)

print("\n=== SMALL FILE DIFFS ===")
for name in ["agent_tele_cmd.py", "agent_feeder.py", "meta_studio.py"]:
    la = (pathlib.Path(r"z:/PinelineV2") / name).read_text(encoding="utf-8", errors="replace").splitlines()
    lb = (pathlib.Path(r"z:/PinelineV4") / name).read_text(encoding="utf-8", errors="replace").splitlines()
    d = list(difflib.unified_diff(la, lb, fromfile="V2", tofile="V4", lineterm="", n=1))
    print(f"==== {name} V2={len(la)} V4={len(lb)} diff_lines={len(d)} ====")
    shown = 0
    for line in d:
        if line.startswith(("@@", "---", "+++")):
            print(line)
            continue
        if line.startswith(("+", "-")):
            print(line[:220])
            shown += 1
            if shown >= 80:
                print("... truncated")
                break
    print()

print("=== HTML FUNC / SIMILARITY ===")
for name in ["films_ui.html", "index.html"]:
    la = (pathlib.Path(r"z:/PinelineV2") / name).read_text(encoding="utf-8", errors="replace").splitlines()
    lb = (pathlib.Path(r"z:/PinelineV4") / name).read_text(encoding="utf-8", errors="replace").splitlines()
    sm = difflib.SequenceMatcher(a=la, b=lb)
    ratio = sm.ratio()
    added = removed = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "delete":
            removed += i2 - i1
        elif tag == "insert":
            added += j2 - j1
        elif tag == "replace":
            removed += i2 - i1
            added += j2 - j1
    print(f"{name}: similarity={ratio:.3f} ~removed={removed} ~added={added} V2={len(la)} V4={len(lb)}")

    def funcs(lines):
        out = set()
        for l in lines:
            m = re.match(r"\s*(?:async\s+)?function\s+(\w+)\s*\(", l)
            if m:
                out.add(m.group(1))
        return out

    f2, f4 = funcs(la), funcs(lb)
    only2 = sorted(f2 - f4)
    only4 = sorted(f4 - f2)
    print("  funcs only V2:", only2)
    print("  funcs only V4:", only4)

print("\n=== server.py route-only + nearby non-route deltas (rough) ===")
# Check whether V4 index calls sort/move even if server lacks routes
for name in ["index.html", "films_ui.html", "static/app.js"]:
    for root in [r"z:/PinelineV2", r"z:/PinelineV4"]:
        t = (pathlib.Path(root) / name).read_text(encoding="utf-8", errors="replace")
        for kw in ["jobs/sort", "jobs/move", "jobs/reorder", "split-plan", "split-parts", "merge-parts"]:
            if kw in t:
                print(pathlib.Path(root).name, name, "uses", kw)

# generate-title usage
print("\n=== generate-title / ai-image call sites ===")
for root in [r"z:/PinelineV2", r"z:/PinelineV4"]:
    for pat in ["generate-title", "ai-image", "/meta/baike", "generate_youtube_titles"]:
        hits = []
        for fp in list(pathlib.Path(root).glob("*.py")) + list(pathlib.Path(root).glob("*.html")) + list(
            (pathlib.Path(root) / "static").glob("*.js")
        ):
            try:
                tt = fp.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue
            if pat in tt:
                hits.append(fp.name)
        print(pathlib.Path(root).name, pat, hits)

# Check V4 routes for generate_title elsewhere in server
print("\n=== V4 has generate_title string anywhere? ===")
count = 0
for fp in pathlib.Path(r"z:/PinelineV4").rglob("*"):
    if fp.suffix.lower() not in {".py", ".html", ".js", ".md"}:
        continue
    if any(x in fp.parts for x in ("node_modules", ".git", "__pycache__", "vendor", "work")):
        continue
    try:
        tt = fp.read_text(encoding="utf-8", errors="replace")
    except Exception:
        continue
    if "generate-title" in tt or "generate_youtube_titles" in tt:
        print(" ", fp.relative_to(r"z:/PinelineV4"))
        count += 1
print("hits", count)

# feeder combine signature diff summary
print("\n=== combine function line fingerprints ===")
for root in [r"z:/PinelineV2", r"z:/PinelineV4"]:
    t = (pathlib.Path(root) / "agent_feeder.py").read_text(encoding="utf-8", errors="replace")
    for name in ["def combine_library_seasons", "def combine_rendered_jobs"]:
        i = t.find(name)
        print(pathlib.Path(root).name, name, "at", i)
