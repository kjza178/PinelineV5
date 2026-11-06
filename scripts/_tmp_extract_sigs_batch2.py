"""One-shot AST signature extract for func-sigs batch2. Delete after use OK."""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(r"Z:\PinelineV5")
OUTDIR = ROOT / "docs" / "reviews" / "func-sigs"

MODS = [
    ("engines/download.py", "download.md", "Download engine — yt-dlp source fetch"),
    ("engines/asr/asr.py", "asr.md", "ASR engine — Whisper path"),
    ("engines/clone_tts.py", "clone_tts.md", "Clone TTS engine"),
    ("engines/assemble.py", "assemble.md", "Assemble / fit dub audio"),
    ("engines/mux.py", "mux.md", "Simple A/V mux (ffmpeg copy)"),
    ("engines/render.py", "render.md", "Render / hardsub / filtergraph"),
    ("core/manifest.py", "manifest.md", "Job Manifest JSON"),
    ("core/film_db.py", "film_db.md", "Films SQLite DB"),
    ("core/config.py", "config.md", "Config / env inject"),
    ("http_routes/routes_hg.py", "routes_hg.md", "HTTP Hongguo routes"),
    ("http_routes/routes_ui.py", "routes_ui.md", "HTTP UI static routes"),
    ("agents/agent_feeder.py", "agent_feeder.md", "Agent feeder"),
    ("agents/auto_publisher.py", "auto_publisher.md", "Auto publisher daemon"),
]

# Spine callers from docs/reviews/2026-11-06-v5-func-catalog.md §1 (evidence only)
CALLERS = {
    "job_id_from_url": "server._create / create_job",
    "download_video": "server._auto_pipeline / _queue_run_one download stage",
    "run_asr": "server._do_asr / _auto_gpu Whisper path",
    "run_clone_tts": "server._do_tts",
    "assemble": "server assemble stage (short / fit=False)",
    "assemble_fit": "server assemble stage (default / long)",
    "run_render": "server._do_render (queue 1-click; not run_mux)",
    "run_mux": "simple mux; queue uses run_render instead",
    "Manifest.save": "spine stamp queue_opts / stages",
    "publish_job": "auto_publisher daemon thread",
}


def format_args(args: ast.arguments) -> str:
    parts: list[str] = []

    def ann(a: ast.arg) -> str:
        if a.annotation:
            try:
                return ": " + ast.unparse(a.annotation)
            except Exception:
                return ""
        return ""

    def with_default(arg: ast.arg, default) -> str:
        s = arg.arg + ann(arg)
        if default is not None:
            try:
                s += "=" + ast.unparse(default)
            except Exception:
                s += "=..."
        return s

    posonly = list(args.posonlyargs)
    normal = list(args.args)
    defaults_all = list(args.defaults)
    all_pos = posonly + normal
    n_pos = len(all_pos)
    n_defaults = len(defaults_all)
    pos_defaults = [None] * (n_pos - n_defaults) + defaults_all

    for i, a in enumerate(posonly):
        parts.append(with_default(a, pos_defaults[i]))
    if posonly:
        parts.append("/")
    for i, a in enumerate(normal):
        parts.append(with_default(a, pos_defaults[len(posonly) + i]))

    if args.vararg:
        parts.append("*" + args.vararg.arg + ann(args.vararg))
    elif args.kwonlyargs:
        parts.append("*")

    for a, d in zip(args.kwonlyargs, args.kw_defaults):
        parts.append(with_default(a, d))

    if args.kwarg:
        parts.append("**" + args.kwarg.arg + ann(args.kwarg))

    return ", ".join(parts)


def sig_of(node, class_name: str | None = None) -> dict:
    name = node.name
    display = f"{class_name}.{name}" if class_name else name
    argstr = format_args(node.args)
    ret = ""
    if node.returns:
        try:
            ret = " -> " + ast.unparse(node.returns)
        except Exception:
            ret = ""
    kind = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    code = f"{kind} {name}({argstr}){ret}"
    doc = ast.get_docstring(node)
    first = ""
    if doc:
        first = doc.strip().splitlines()[0].strip()
        low = first.lower()
        for bad in ("sk-", "api_key", "password", "secret", "token="):
            if bad in low:
                first = "(doc redacted)"
                break
    return {
        "name": display,
        "code_name": name,
        "lineno": node.lineno,
        "code": code,
        "doc": first,
    }


def extract(path: Path) -> list[dict]:
    src = path.read_text(encoding="utf-8", errors="replace")
    tree = ast.parse(src)
    out: list[dict] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out.append(sig_of(node))
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out.append(sig_of(item, class_name=node.name))
    return out


def count_existing(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    return len(re.findall(r"^### `", text, re.M))


def main() -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    results: list[tuple[str, str, int, bool]] = []
    for rel, slug, title in MODS:
        out_path = OUTDIR / slug
        if out_path.exists() and out_path.stat().st_size > 50:
            c = count_existing(out_path)
            print(f"SKIP {slug} (exists, count={c})")
            results.append((slug, rel, c, True))
            continue
        path = ROOT / rel
        if not path.exists():
            print(f"MISSING {rel}")
            continue
        sigs = extract(path)
        lines: list[str] = [
            f"# {title}",
            "",
            f"- **Module:** `{rel}`",
            "- **Date:** 2026-11-06",
            "- **Source:** AST",
            f"- **Count:** {len(sigs)}",
            "",
            "## Signatures",
            "",
        ]
        for s in sigs:
            lines.append(f"### `{s['name']}` — L{s['lineno']}")
            lines.append("")
            lines.append("```python")
            lines.append(s["code"])
            lines.append("```")
            lines.append("")
            if s["doc"]:
                lines.append(f"**Doc:** {s['doc']}")
                lines.append("")
            caller = CALLERS.get(s["name"]) or CALLERS.get(s["code_name"])
            if caller:
                lines.append(f"**Callers (spine):** {caller}")
                lines.append("")
        text = "\n".join(lines).rstrip() + "\n"
        out_path.write_text(text, encoding="utf-8")
        print(f"WROTE {slug} count={len(sigs)}")
        results.append((slug, rel, len(sigs), False))

    print("--- results ---")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
