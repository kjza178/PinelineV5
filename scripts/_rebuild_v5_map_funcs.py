# -*- coding: utf-8 -*-
"""Rebuild MODULE_FUNCS + funcKeys in static/ui/v5-map.html from func-sigs/*.md."""
from __future__ import annotations

import json
import re
from pathlib import Path

root = Path(r"Z:\PinelineV5")
sigs = root / "docs" / "reviews" / "func-sigs"
html_path = root / "static" / "ui" / "v5-map.html"

slug_to_node = {
    "job_queue": "job_queue",
    "manifest": "manifest",
    "download": "download",
    "asr": "asr",
    "translate": "translate",
    "pronoun_consistency": "pronoun_consistency",
    "clone_tts": "clone_tts",
    "mux": "mux",
    "split_parts": "split_parts",
    "hongguo_bridge": "hongguo_bridge",
    "routes_ui": "routes_ui",
    "server_orchestration": "server",
    "assemble": "assemble",
    "render": "render",
    "llm": "llm",
    "film_db": "film_db",
    "config": "config",
    "routes_hg": "routes_hg",
    "agent_feeder": "agent_feeder",
    "auto_publisher": "auto_publisher",
    "subs": "subs",
    "separate": "separate",
    "series_glossary": "series_glossary",
    "ocr": "ocr",
    "check_block": "check_block",
    "playlist": "playlist",
    "batch_config": "batch_config",
    "agent_core": "agent_core",
    "agent_qa_gate": "agent_qa_gate",
    "agent_pronoun_pass": "agent_pronoun_pass",
    "meta_studio": "meta_studio",
    "routes_agent": "routes_agent",
    "routes_films": "routes_films",
    "render_fx": "render",  # fold into render node if no dedicated
    "job_meta": "job_meta",
    "fileio": "fileio",
}

MODULE_FUNCS: dict[str, list[dict]] = {}
for md in sorted(sigs.glob("*.md")):
    if md.name == "README.md":
        continue
    node = slug_to_node.get(md.stem)
    if not node:
        continue
    text = md.read_text(encoding="utf-8")
    funcs: list[dict] = []
    for block in re.split(r"\n### ", text)[1:]:
        hm = re.match(r"`([^`]+)` [—-] L(\d+)", block)
        if not hm:
            continue
        name, line = hm.group(1), int(hm.group(2))
        dm = re.search(r"\*\*Doc:\*\*\s*(.+)", block)
        doc = (dm.group(1).strip() if dm else "(no docstring)")
        if len(doc) > 140:
            doc = doc[:137] + "..."
        funcs.append({"name": name, "doc": doc, "line": line})
    if not funcs:
        continue
    # merge if multiple slugs map to same node
    MODULE_FUNCS.setdefault(node, []).extend(funcs)
    print(f"{md.stem} -> {node}: {len(funcs)}")

html = html_path.read_text(encoding="utf-8")
m_gd = re.search(r"const GRAPH_DATA = (\{.*?\});", html, re.S)
m_mf = re.search(r"const MODULE_FUNCS = (\{.*?\});", html, re.S)
if not m_gd or not m_mf:
    raise SystemExit("GRAPH_DATA or MODULE_FUNCS marker missing")

gd = json.loads(m_gd.group(1))
existing = {n["id"] for n in gd["nodes"]}
# ensure nodes for keys we embedded
extra = {
    "agent_feeder": ("agent_feeder", "agents", 2),
    "subs": ("engines/subs", "engines", 3),
    "job_meta": ("core/job_meta", "core", 1),
    "routes_agent": ("routes_agent", "http_routes", 1),
    "routes_films": ("routes_films", "http_routes", 1),
    "agent_core": ("agent_core", "agents", 2),
    "agent_qa_gate": ("agent_qa_gate", "agents", 2),
    "agent_pronoun_pass": ("agent_pronoun_pass", "agents", 2),
    "meta_studio": ("meta_studio", "agents", 2),
    "playlist": ("engines/playlist", "engines", 2),
    "separate": ("engines/separate", "engines", 2),
    "ocr": ("engines/ocr", "engines", 2),
    "check_block": ("engines/check_block", "engines", 3),
    "series_glossary": ("series_glossary", "engines", 3),
    "batch_config": ("core/batch_config", "core", 1),
    "assemble": ("engines/assemble", "engines", 2),
    "llm": ("engines/llm", "engines", 3),
    "film_db": ("core/film_db", "core", 1),
    "config": ("core/config", "core", 1),
    "routes_hg": ("routes_hg", "http_routes", 1),
    "auto_publisher": ("auto_publisher", "agents", 2),
    "fileio": ("core/fileio", "core", 1),
}
for nid, (label, pkg, layer) in extra.items():
    if nid not in existing and nid in MODULE_FUNCS:
        gd["nodes"].append({"id": nid, "label": label, "pkg": pkg, "layer": layer})
        existing.add(nid)

gd["funcKeys"] = {n: n for n in MODULE_FUNCS}
mf_json = json.dumps(MODULE_FUNCS, ensure_ascii=False, separators=(",", ":"))
gd_json = json.dumps(gd, ensure_ascii=False, separators=(",", ":"))

html = html[: m_gd.start(1)] + gd_json + html[m_gd.end(1) :]
# re-find MODULE_FUNCS after GRAPH_DATA rewrite (offsets changed)
m_mf = re.search(r"const MODULE_FUNCS = (\{.*?\});", html, re.S)
assert m_mf
html = html[: m_mf.start(1)] + mf_json + html[m_mf.end(1) :]

html = html.replace(
    "Curated modules · not full 2118 catalog",
    f"Embedded from func-sigs · {sum(len(v) for v in MODULE_FUNCS.values())} funcs · catalog 2118",
)
html_path.write_text(html, encoding="utf-8")
# sync to V2/V4 if they have the file
for alt in (
    Path(r"Z:\PinelineV4\static\ui\v5-map.html"),
    Path(r"Z:\PinelineV2\static\ui\v5-map.html"),
):
    if alt.parent.exists():
        alt.parent.mkdir(parents=True, exist_ok=True)
        alt.write_text(html, encoding="utf-8")
        print("synced", alt)

print(
    "nodes_with_funcs",
    len(MODULE_FUNCS),
    "total_funcs",
    sum(len(v) for v in MODULE_FUNCS.values()),
    "bytes",
    html_path.stat().st_size,
)
