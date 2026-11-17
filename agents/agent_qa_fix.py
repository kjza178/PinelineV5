# -*- coding: utf-8 -*-
"""Second Brain — xử lý cờ QA HIGH loại khác `hang` (2026-11-17).

Vì sao: trước đây chỉ `hang` có đường xử lý (agent_hang_fix). Cờ high khác (name_echo, calque,
vi_pattern, empty_vi, nonsense_shape…) chỉ làm job HOLD và chờ — LLM agent không sửa gì → kẹt
(ff8e66b475a7 kẹt ~12h vì 2 cờ báo sai).

Mỗi cờ: LLM đọc cửa sổ ZH/VI → verdict
  - false_positive → row["qa_ack"] += [kind]  (scan_script bỏ qua kind đó ở câu đó)
  - fix            → ghi VI mới (bám ZH)
Mỗi câu thử tối đa QA_FIX_MAX_TRIES lần (row["qa_fix_try"]) → không đốt LLM mỗi tick.
Ghi audit `qa_fix_trace.json`. Bật/tắt: BRAIN_QA_FIX (mặc định 1). Model: QA_FIX_MODEL → HANG_FIX_MODEL
→ PRONOUN_MODEL → chatgpt/gpt-5-6-mini.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BATCH = 10
SKIP_KINDS = {"hang"}          # hang → agent_hang_fix


def _cfg(key: str, default: str | None = None) -> str | None:
    try:
        from core.config import get
        v = get(key, default)
    except Exception:  # noqa: BLE001
        v = os.getenv(key, default)
    return default if v is None or str(v).strip() == "" else str(v).strip()


def enabled() -> bool:
    return (_cfg("BRAIN_QA_FIX", "1") or "1").lower() in ("1", "true", "yes", "on")


def _model() -> str:
    return (_cfg("QA_FIX_MODEL") or _cfg("HANG_FIX_MODEL") or _cfg("PRONOUN_MODEL")
            or "chatgpt/gpt-5-6-mini")


def _max_tries() -> int:
    try:
        return max(1, int(_cfg("QA_FIX_MAX_TRIES", "2") or "2"))
    except ValueError:
        return 2


def _window(rows: list[dict], j: int, radius: int = 2) -> list[dict]:
    out = []
    for k in range(max(0, j - radius), min(len(rows), j + radius + 1)):
        r = rows[k]
        if isinstance(r, dict):
            out.append({"i": r.get("i"), "zh": (r.get("zh") or "").strip(),
                        "vi": (r.get("vi") or "").strip(), "focus": k == j})
    return out


def collect_cases(rows: list[dict], flags: list[dict]) -> list[dict]:
    pos = {int(r["i"]): j for j, r in enumerate(rows) if isinstance(r, dict) and "i" in r}
    lim = _max_tries()
    cases: list[dict] = []
    for f in flags:
        if f.get("sev") != "high" or f.get("kind") in SKIP_KINDS:
            continue
        try:
            i = int(f["i"])
        except (KeyError, TypeError, ValueError):
            continue
        j = pos.get(i)
        if j is None:
            continue
        r = rows[j]
        if r.get("manual") or int((r.get("qa_fix_try") or {}).get(f["kind"], 0)) >= lim:
            continue
        cases.append({"i": i, "kind": f["kind"], "note": f.get("note") or "",
                      "zh": (r.get("zh") or "").strip(), "vi": (r.get("vi") or "").strip(),
                      "window": _window(rows, j)})
    return cases


_SYS = (
    "Bạn là biên tập phụ đề tiếng Việt cho phim Trung (lồng tiếng). Mỗi CASE là 1 câu bị bộ quét tự động "
    "gắn cờ HIGH (kind + note). Bộ quét dùng regex nên CÓ THỂ BÁO SAI.\n"
    "Đọc cửa sổ ZH/VI quanh câu focus, rồi chọn:\n"
    "- verdict=false_positive: VI focus đúng nghĩa ZH, tự nhiên, lỗi trong note không thật → vi để rỗng.\n"
    "- verdict=fix: lỗi có thật → vi = câu VI mới cho focus, bám nghĩa ZH, giữ tên riêng/xưng hô như các câu "
    "xung quanh, độ dài tương đương (để lồng tiếng vừa khung).\n"
    "Không sửa câu khác ngoài focus. Câu VI trống (empty_vi) bắt buộc fix.\n"
    "CHỈ JSON: {\"items\":[{\"i\":int,\"kind\":str,\"verdict\":\"false_positive\"|\"fix\",\"vi\":str,"
    "\"why\":str}]}"
)


def _llm_batch(cases: list[dict]) -> list[dict]:
    from engines.llm import chat, parse_json
    out = chat(
        [{"role": "system", "content": _SYS},
         {"role": "user", "content": "CASES:\n" + json.dumps(cases, ensure_ascii=False)}],
        model=_model(), temperature=0.1, json_mode=True, max_tokens=4096, timeout=180,
    )
    data = parse_json(out)
    items = data.get("items", data if isinstance(data, list) else []) if isinstance(data, (dict, list)) else []
    clean = []
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict) or "i" not in it:
            continue
        try:
            clean.append({"i": int(it["i"]), "kind": str(it.get("kind") or ""),
                          "verdict": str(it.get("verdict") or "").strip().lower(),
                          "vi": str(it.get("vi") or "").strip(), "why": str(it.get("why") or "")[:200]})
        except (TypeError, ValueError):
            continue
    return clean


def apply_items(rows: list[dict], cases: list[dict], items: list[dict]) -> tuple[int, int]:
    pos = {int(r["i"]): j for j, r in enumerate(rows) if isinstance(r, dict) and "i" in r}
    by = {(c["i"], c["kind"]): c for c in cases}
    n_fix = n_ack = 0
    for c in cases:                             # đếm lượt thử cho mọi case đã gửi
        r = rows[pos[c["i"]]]
        t = dict(r.get("qa_fix_try") or {})
        t[c["kind"]] = int(t.get(c["kind"], 0)) + 1
        r["qa_fix_try"] = t
    for it in items:
        j = pos.get(it["i"])
        if j is None:
            continue
        kinds = [it["kind"]] if (it["i"], it["kind"]) in by else [c["kind"] for c in cases if c["i"] == it["i"]]
        r = rows[j]
        if it["verdict"] in ("false_positive", "ok", "keep"):
            ack = list(r.get("qa_ack") or [])
            for k in kinds:
                if k and k not in ack and k != "empty_vi":
                    ack.append(k)
                    n_ack += 1
            r["qa_ack"] = ack
        elif it["verdict"] == "fix" and it["vi"] and it["vi"] != (r.get("vi") or "").strip():
            r["vi_before_qa_fix"] = r.get("vi")
            r["vi"] = it["vi"]
            r["qa_fix"] = 1
            n_fix += 1
    return n_fix, n_ack


def fix_qa_job(work_dir: str | Path, *, write: bool = True) -> dict[str, Any]:
    work_dir = Path(work_dir)
    sp = work_dir / "script.json"
    if not sp.is_file():
        return {"ok": False, "error": "no script.json"}
    try:
        from agents.agent_hang_fix import _review_or_translate_busy
        busy = _review_or_translate_busy(work_dir)
        if busy:
            return {"ok": True, "skipped": True, "reason": f"busy:{busy}"}
    except Exception:  # noqa: BLE001
        pass
    rows = json.loads(sp.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        return {"ok": False, "error": "script not list"}
    from agents.agent_quality import scan_script
    cases = collect_cases(rows, scan_script(rows))[:40]
    if not cases:
        return {"ok": True, "n_cases": 0, "n_fixed": 0, "n_ack": 0}
    items: list[dict] = []
    errors: list[str] = []
    for k in range(0, len(cases), BATCH):
        try:
            items.extend(_llm_batch(cases[k:k + BATCH]))
        except Exception as e:  # noqa: BLE001
            errors.append(str(e)[:200])
    if errors and not items:
        # LLM hỏng → KHÔNG đếm lượt thử (thử lại tick sau)
        return {"ok": False, "n_cases": len(cases), "error": errors[0]}
    n_fix, n_ack = apply_items(rows, cases, items)
    if write:
        try:
            from core.fileio import atomic_write_json
            atomic_write_json(sp, rows, fsync=False)
        except Exception:  # noqa: BLE001
            sp.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        if n_fix:
            try:
                from engines.subs import to_srt
                (work_dir / "sub.vi.srt").write_text(to_srt(rows, key="vi"), encoding="utf-8")
            except Exception:  # noqa: BLE001
                pass
        tp = work_dir / "qa_fix_trace.json"
        try:
            hist = json.loads(tp.read_text(encoding="utf-8")) if tp.is_file() else []
        except Exception:  # noqa: BLE001
            hist = []
        hist = (hist if isinstance(hist, list) else [])[-20:]
        hist.append({"at": datetime.now(timezone.utc).isoformat(), "model": _model(), "cases": cases,
                     "items": items, "n_fixed": n_fix, "n_ack": n_ack, "errors": errors})
        tp.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[qa_fix] {work_dir.name}: cases={len(cases)} fixed={n_fix} ack={n_ack}", flush=True)
    return {"ok": True, "n_cases": len(cases), "n_fixed": n_fix, "n_ack": n_ack, "items": items}
