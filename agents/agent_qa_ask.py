# -*- coding: utf-8 -*-
"""Second Brain — HOLD QA hỏi người qua Telegram + tự xử lý khi quá hạn (2026-11-17 qaask).

Vì sao: HOLD QA trước đây chỉ báo «cần người duyệt» (không nói câu nào, sai gì, nên sửa sao) và job
giữ ghế hàng đợi vô hạn → 1 job lỗi chặn cả hàng. Giờ:

1. Khi job vào HOLD QA (sig cờ high mới): LLM đề xuất cho TỪNG câu bị cờ (verdict fix / false_positive,
   VI mới, lý do, độ chắc `conf`) → gửi 1 tin Telegram: số câu, loại lỗi, ZH, VI hiện tại, VI đề xuất + lý do,
   kèm 3 nút  ✅ Áp đề xuất · ⏭ Cờ sai – bỏ qua · ▶️ Chạy tiếp nguyên trạng.
   Reply thẳng vào tin bằng câu VI mới → ghi câu đó (nhiều câu: mỗi dòng `#số: câu`) rồi chạy tiếp.
2. Không ai trả lời sau QA_HOLD_MAX_MIN (10'):
   - cờ mềm (SOFT_KINDS)                     → tự áp đề xuất (không có đề xuất = giữ nguyên) rồi chạy tiếp;
   - cờ cứng + đề xuất chắc (conf ≥ QA_ASK_SURE_CONF) → áp đề xuất + báo lại;
   - cờ cứng còn lại                         → GÁC job (bỏ khỏi hàng đợi, nhường ghế), Telegram nhắc mỗi
     QA_ASK_REMIND_MIN; trả lời lúc nào cũng được → job xếp lại đầu hàng.

State: work/<job>/qa_ask.json; tra tin → job: work/logs/qa_ask_index.json («chat:message_id» → job_id).
Mọi câu đã xử lý được gắn row["qa_ack"] += [kind] để scan_script không cờ lại, và row["qa_ask"] để audit.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ASK_FILE = "qa_ask.json"
INDEX_FILE = "qa_ask_index.json"
MARK = "HOLD QA"                       # sidecar nhận diện reply vào tin hỏi
SOFT_KINDS = {"name_echo", "hang", "stutter", "calque"}
BATCH = 10


def _cfg(key: str, default: str | None = None) -> str | None:
    try:
        from core.config import get
        v = get(key, default)
    except Exception:  # noqa: BLE001
        v = os.getenv(key, default)
    return default if v is None or str(v).strip() == "" else str(v).strip()


def _f(key: str, default: float) -> float:
    try:
        return float(_cfg(key, str(default)) or default)
    except ValueError:
        return default


def sure_conf() -> float:
    return _f("QA_ASK_SURE_CONF", 0.85)


def remind_min() -> float:
    return _f("QA_ASK_REMIND_MIN", 60.0)


def max_items() -> int:
    return int(_f("QA_ASK_MAX_ITEMS", 12))


def _model() -> str:
    return (_cfg("QA_ASK_MODEL") or _cfg("QA_FIX_MODEL") or _cfg("HANG_FIX_MODEL")
            or _cfg("PRONOUN_MODEL") or "chatgpt/gpt-5-6-mini")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def is_soft(kind: str) -> bool:
    return str(kind or "") in SOFT_KINDS


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------
def load_ask(wd: Path) -> dict | None:
    p = Path(wd) / ASK_FILE
    if not p.is_file():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else None
    except Exception:  # noqa: BLE001
        return None


def save_ask(wd: Path, ask: dict) -> None:
    try:
        from core.fileio import atomic_write_json
        atomic_write_json(Path(wd) / ASK_FILE, ask, fsync=False)
    except Exception:  # noqa: BLE001
        (Path(wd) / ASK_FILE).write_text(json.dumps(ask, ensure_ascii=False, indent=2), encoding="utf-8")


def _index_path(work_root: Path) -> Path:
    d = Path(work_root) / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d / INDEX_FILE


def _index_load(work_root: Path) -> dict:
    p = _index_path(work_root)
    try:
        d = json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}
    except Exception:  # noqa: BLE001
        d = {}
    return d if isinstance(d, dict) else {}


def _index_add(work_root: Path, chat_id: str, mid: int, jid: str) -> None:
    d = _index_load(work_root)
    d[f"{chat_id}:{mid}"] = {"job_id": jid, "at": time.time()}
    if len(d) > 400:                                      # giữ 400 tin gần nhất
        d = dict(sorted(d.items(), key=lambda kv: float((kv[1] or {}).get("at") or 0))[-400:])
    _index_path(work_root).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


def job_for_message(work_root: Path, chat_id: str, mid: int | str) -> str | None:
    e = _index_load(work_root).get(f"{chat_id}:{mid}") or {}
    return e.get("job_id") or None


def _rows(wd: Path) -> list[dict] | None:
    sp = Path(wd) / "script.json"
    if not sp.is_file():
        return None
    try:
        rows = json.loads(sp.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None
    return rows if isinstance(rows, list) else None


def _write_rows(wd: Path, rows: list[dict], *, vi_changed: bool) -> None:
    sp = Path(wd) / "script.json"
    try:
        from core.fileio import atomic_write_json
        atomic_write_json(sp, rows, fsync=False)
    except Exception:  # noqa: BLE001
        sp.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    if vi_changed:
        try:
            from engines.subs import to_srt
            (Path(wd) / "sub.vi.srt").write_text(to_srt(rows, key="vi"), encoding="utf-8")
        except Exception:  # noqa: BLE001
            pass
    try:                                                  # qa_brain.json mới → gate/park thấy sạch
        from agents.agent_quality import scan_script, write_qa_brain
        write_qa_brain(Path(wd), scan_script(rows))
    except Exception:  # noqa: BLE001
        pass


# ---------------------------------------------------------------------------
# Tạo câu hỏi
# ---------------------------------------------------------------------------
def _window(rows: list[dict], j: int, radius: int = 2) -> list[dict]:
    out = []
    for k in range(max(0, j - radius), min(len(rows), j + radius + 1)):
        r = rows[k]
        if isinstance(r, dict):
            out.append({"i": r.get("i"), "zh": (r.get("zh") or "").strip(),
                        "vi": (r.get("vi") or "").strip(), "focus": k == j})
    return out


def collect_items(rows: list[dict] | None, fallback_flags: list[dict] | None = None) -> list[dict]:
    """Cờ HIGH còn mở → item (gộp theo câu: 1 câu nhiều loại lỗi = 1 item)."""
    flags: list[dict] = []
    if rows is not None:
        try:
            from agents.agent_quality import scan_script
            flags = scan_script(rows)
        except Exception:  # noqa: BLE001
            flags = []
    else:
        flags = list(fallback_flags or [])
    pos = {}
    for j, r in enumerate(rows or []):
        if isinstance(r, dict) and "i" in r:
            try:
                pos[int(r["i"])] = j
            except (TypeError, ValueError):
                pass
    by_i: dict[int, dict] = {}
    for f in flags:
        if f.get("sev") != "high":
            continue
        try:
            i = int(f["i"])
        except (KeyError, TypeError, ValueError):
            continue
        it = by_i.get(i)
        if it is None:
            j = pos.get(i)
            r = rows[j] if (rows is not None and j is not None) else f
            it = {"i": i, "kinds": [], "notes": [],
                  "zh": (r.get("zh") or "").strip(), "vi": (r.get("vi") or "").strip(),
                  "window": _window(rows, j) if (rows is not None and j is not None) else []}
            by_i[i] = it
        k = str(f.get("kind") or "")
        if k and k not in it["kinds"]:
            it["kinds"].append(k)
            it["notes"].append(str(f.get("note") or ""))
    items = sorted(by_i.values(), key=lambda x: x["i"])
    for it in items:
        it["soft"] = all(is_soft(k) for k in it["kinds"])
    return items


_SYS = (
    "Bạn là biên tập phụ đề tiếng Việt cho phim Trung (lồng tiếng). Mỗi CASE là 1 câu bị bộ quét tự động "
    "gắn cờ HIGH (kinds + notes); bộ quét dùng regex nên CÓ THỂ BÁO SAI, và lần sửa tự động trước KHÔNG "
    "gỡ được cờ. Đọc cửa sổ ZH/VI quanh câu focus rồi đề xuất cho người duyệt:\n"
    "- verdict=false_positive: VI focus đúng nghĩa ZH, tự nhiên → vi rỗng.\n"
    "- verdict=fix: lỗi có thật → vi = câu VI mới cho focus, bám nghĩa ZH, giữ tên riêng/xưng hô như câu "
    "xung quanh, độ dài tương đương (lồng tiếng vừa khung). VI trống bắt buộc fix.\n"
    "why = lý do ngắn (≤20 từ, tiếng Việt). conf = độ chắc 0..1 (chỉ ≥0.85 khi rất chắc: nghĩa ZH rõ, "
    "câu mới tự nhiên, không đoán tên/xưng hô).\n"
    "CHỈ JSON: {\"items\":[{\"i\":int,\"verdict\":\"false_positive\"|\"fix\",\"vi\":str,\"why\":str,"
    "\"conf\":number}]}"
)


def _llm_batch(cases: list[dict]) -> list[dict]:
    from engines.llm import chat, parse_json
    payload = [{"i": c["i"], "kinds": c["kinds"], "notes": c["notes"], "zh": c["zh"], "vi": c["vi"],
                "window": c.get("window") or []} for c in cases]
    out = chat(
        [{"role": "system", "content": _SYS},
         {"role": "user", "content": "CASES:\n" + json.dumps(payload, ensure_ascii=False)}],
        model=_model(), temperature=0.1, json_mode=True, max_tokens=4096, timeout=180,
    )
    data = parse_json(out)
    items = data.get("items", []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
    clean = []
    for it in items if isinstance(items, list) else []:
        if not isinstance(it, dict) or "i" not in it:
            continue
        try:
            conf = float(it.get("conf") or 0)
        except (TypeError, ValueError):
            conf = 0.0
        try:
            clean.append({"i": int(it["i"]), "verdict": str(it.get("verdict") or "").strip().lower(),
                          "vi": str(it.get("vi") or "").strip(), "why": str(it.get("why") or "")[:200],
                          "conf": max(0.0, min(1.0, conf))})
        except (TypeError, ValueError):
            continue
    return clean


def propose(items: list[dict]) -> list[str]:
    """Điền prop_verdict/prop_vi/prop_why/prop_conf cho từng item. Trả danh sách lỗi (nếu có)."""
    errors: list[str] = []
    for k in range(0, len(items), BATCH):
        chunk = items[k:k + BATCH]
        try:
            res = {x["i"]: x for x in _llm_batch(chunk)}
        except Exception as e:  # noqa: BLE001
            errors.append(str(e)[:200])
            continue
        for it in chunk:
            p = res.get(it["i"])
            if not p:
                continue
            v = p["verdict"] if p["verdict"] in ("fix", "false_positive") else ""
            if v == "fix" and (not p["vi"] or p["vi"] == it["vi"]):
                v = ""                                    # «fix» mà không có câu mới → coi như không đề xuất
            it["prop_verdict"] = v
            it["prop_vi"] = p["vi"] if v == "fix" else ""
            it["prop_why"] = p["why"]
            it["prop_conf"] = p["conf"] if v else 0.0
    return errors


def has_prop(it: dict) -> bool:
    return it.get("prop_verdict") in ("fix", "false_positive")


def is_sure(it: dict) -> bool:
    return has_prop(it) and float(it.get("prop_conf") or 0) >= sure_conf()


def create_ask(wd: Path, jid: str, sig: str, *, fallback_flags: list[dict] | None = None,
               use_llm: bool = True) -> dict:
    wd = Path(wd)
    items = collect_items(_rows(wd), fallback_flags)
    errors = propose(items[: max_items() * 2]) if (use_llm and items) else []
    ask = {"job_id": jid, "sig": sig, "created_at": _now(), "since": time.time(), "status": "open",
           "model": _model(), "items": items, "errors": errors, "msgs": [], "events": []}
    save_ask(wd, ask)
    return ask


def open_items(ask: dict | None) -> list[dict]:
    return [it for it in (ask or {}).get("items") or [] if not it.get("done")]


# ---------------------------------------------------------------------------
# Telegram
# ---------------------------------------------------------------------------
def _cut(s: str, n: int) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def render_text(ask: dict, *, title: str = "") -> str:
    jid = ask.get("job_id") or "?"
    its = open_items(ask)
    n_hard = sum(1 for it in its if not it.get("soft"))
    head = title or f"⏸ {MARK} {jid} — {len(its)} câu bị cờ (cứng {n_hard} · mềm {len(its) - n_hard})"
    if f"{MARK} {jid}" not in head:
        head = f"{head}\n[{MARK} {jid}]"
    parts = [head, ""]
    shown = 0
    budget = 3300
    for it in its:
        tag = "mềm" if it.get("soft") else "CỨNG"
        notes = "; ".join(n for n in it.get("notes") or [] if n)
        blk = [f"#{it['i']} · {', '.join(it.get('kinds') or [])} ({tag})" + (f" — {_cut(notes, 80)}" if notes else ""),
               f"ZH: {_cut(it.get('zh', ''), 140)}",
               f"VI: {_cut(it.get('vi', ''), 160) or '(trống)'}"]
        v = it.get("prop_verdict")
        conf = f"{float(it.get('prop_conf') or 0):.2f}"
        if v == "fix":
            blk.append(f"→ Đề xuất ({conf}): {_cut(it.get('prop_vi', ''), 160)}")
        elif v == "false_positive":
            blk.append(f"→ Đề xuất ({conf}): giữ nguyên — cờ báo sai")
        else:
            blk.append("→ Chưa có đề xuất (LLM lỗi/không chắc)")
        if it.get("prop_why"):
            blk.append(f"   Lý do: {_cut(it['prop_why'], 140)}")
        txt = "\n".join(blk) + "\n"
        if sum(len(p) for p in parts) + len(txt) > budget:
            break
        parts.append(txt)
        shown += 1
    if shown < len(its):
        parts.append(f"… còn {len(its) - shown} câu (xem work/{jid}/{ASK_FILE})\n")
    mx = _cfg("QA_HOLD_MAX_MIN", "10")
    parts.append("Reply tin này bằng câu VI mới để ghi đè rồi chạy tiếp (nhiều câu: mỗi dòng `#số: câu mới`). "
                 "Reply `?` hoặc `#số ?` = xem 3 câu trước/sau.")
    parts.append(f"Không ai trả lời sau {mx}' → mềm: tự áp đề xuất · cứng chắc: áp + báo · "
                 "cứng còn lại: gác job, hàng đợi chạy job sau.")
    return "\n".join(parts)


def keyboard(jid: str) -> dict:
    return {"inline_keyboard": [
        [{"text": "✅ Áp đề xuất", "callback_data": f"qa:apply:{jid}"}],
        [{"text": "⏭ Cờ sai – bỏ qua", "callback_data": f"qa:skip:{jid}"},
         {"text": "▶️ Chạy tiếp nguyên trạng", "callback_data": f"qa:go:{jid}"}],
    ]}


def _tg_enabled() -> bool:
    return (os.getenv("AGENT_TELEGRAM") or "").strip() in ("1", "true", "yes")


def send(work_root: Path, wd: Path, ask: dict, text: str, *, buttons: bool = True) -> int:
    """Gửi tin (kèm nút) tới mọi user được phép; ghi message_id vào ask + index. Trả số tin gửi được."""
    if not _tg_enabled():
        return 0
    try:
        from agents.agent_watch import telegram_config
        token, uids = telegram_config()
    except Exception:  # noqa: BLE001
        return 0
    if not token or not uids:
        return 0
    jid = ask.get("job_id") or Path(wd).name
    n = 0
    for uid in uids:
        payload = {"chat_id": uid, "text": text[:3900], "disable_web_page_preview": "1"}
        if buttons:
            payload["reply_markup"] = json.dumps(keyboard(jid), ensure_ascii=False)
        try:
            req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage",
                                         data=urllib.parse.urlencode(payload).encode(), method="POST")
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8") or "{}")
            mid = int(((data.get("result") or {}).get("message_id")) or 0)
            if data.get("ok") and mid:
                ask.setdefault("msgs", []).append({"chat_id": str(uid), "message_id": mid, "at": time.time()})
                _index_add(work_root, str(uid), mid, jid)
                n += 1
        except Exception as e:  # noqa: BLE001
            print(f"[qa_ask] telegram lỗi: {e}", flush=True)
    if n:
        ask["sent_at"] = time.time()
        save_ask(wd, ask)
    return n


# ---------------------------------------------------------------------------
# Áp quyết định
# ---------------------------------------------------------------------------
def parse_reply(text: str, items: list[dict]) -> dict[int, str]:
    """`#12: câu` / `12. câu` mỗi dòng → {12: câu}. Không có số + đúng 1 câu đang mở → cả tin là câu mới."""
    want = {int(it["i"]) for it in items}
    out: dict[int, str] = {}
    for line in (text or "").splitlines():
        m = re.match(r"^\s*#?(\d{1,6})\s*[:：.)\-–]\s*(.+?)\s*$", line)
        if m and int(m.group(1)) in want:
            out[int(m.group(1))] = m.group(2)
    if not out and len(items) == 1 and (text or "").strip():
        out[int(items[0]["i"])] = " ".join((text or "").split())
    return out


def apply_decision(wd: Path, ask: dict, mode: str, *, only: set[int] | None = None,
                   user_lines: dict[int, str] | None = None, by: str = "telegram") -> dict:
    """mode: apply | skip | go | reply. Gắn qa_ack để scan không cờ lại. Trả {n_fix, n_ack, done, left}."""
    wd = Path(wd)
    rows = _rows(wd)
    pos = {}
    for j, r in enumerate(rows or []):
        if isinstance(r, dict) and "i" in r:
            try:
                pos[int(r["i"])] = j
            except (TypeError, ValueError):
                pass
    n_fix = n_ack = 0
    done: list[int] = []
    stamp = {"mode": mode, "by": by, "at": _now()}
    for it in open_items(ask):
        i = int(it["i"])
        if only is not None and i not in only:
            continue
        if mode == "reply" and i not in (user_lines or {}):
            continue
        r = rows[pos[i]] if (rows is not None and i in pos) else None
        new_vi = None
        if mode == "reply":
            new_vi = (user_lines or {})[i].strip()
        elif mode == "apply" and it.get("prop_verdict") == "fix" and it.get("prop_vi"):
            new_vi = it["prop_vi"]
        if r is not None:
            if new_vi and new_vi != (r.get("vi") or "").strip():
                r["vi_before_qa_ask"] = r.get("vi")
                r["vi"] = new_vi
                if mode == "reply":
                    r["manual"] = 1
                n_fix += 1
            ack = list(r.get("qa_ack") or [])
            for k in it.get("kinds") or []:
                if k and k not in ack and not (k == "empty_vi" and not (r.get("vi") or "").strip()):
                    ack.append(k)
                    n_ack += 1
            r["qa_ack"] = ack
            r["qa_ask"] = dict(stamp)
            if "empty_vi" in (it.get("kinds") or []) and not (r.get("vi") or "").strip():
                continue                                  # VI trống không «bỏ qua» được — phải có câu
        it["done"] = {**stamp, **({"vi": new_vi} if new_vi else {})}
        done.append(i)
    if rows is not None and done:
        _write_rows(wd, rows, vi_changed=bool(n_fix))
    left = len(open_items(ask))
    ask.setdefault("events", []).append({**stamp, "done": done, "n_fix": n_fix, "n_ack": n_ack, "left": left})
    if left == 0:
        ask["status"] = "resolved"
        ask["resolved_at"] = _now()
    save_ask(wd, ask)
    return {"n_fix": n_fix, "n_ack": n_ack, "done": done, "left": left}


def auto_resolve(wd: Path, ask: dict) -> dict:
    """Quá hạn: mềm → áp đề xuất (không có đề xuất = giữ nguyên); cứng chắc → áp đề xuất.
    Trả {soft: [...], sure: [...], left_items: [...], ...}."""
    its = open_items(ask)
    soft = {int(it["i"]) for it in its if it.get("soft")}
    sure = {int(it["i"]) for it in its if not it.get("soft") and is_sure(it)}
    res = apply_decision(wd, ask, "apply", only=soft | sure, by="timeout") if (soft | sure) else \
        {"n_fix": 0, "n_ack": 0, "done": [], "left": len(its)}
    res["soft"] = sorted(soft)
    res["sure"] = sorted(sure)
    res["left_items"] = [int(it["i"]) for it in open_items(ask)]
    return res


def clear_hold(wd: Path) -> None:
    """Gỡ cờ HOLD QA trên manifest (dùng cho part job khi người xếp lại job cha)."""
    from core.manifest import Manifest

    def _fn(d: dict) -> None:
        a = dict(d.get("agent") or {})
        a["hold_after_translate"] = False
        if a.get("qa_blocked"):
            a["qa_override"] = True
        a["qa_blocked"] = False
        for k in ("held_at", "hold_reason", "qa_deferred"):
            a.pop(k, None)
        d["agent"] = a
    Manifest(Path(wd)).update(_fn)


def mark_deferred(wd: Path, ask: dict, ids: list[str]) -> None:
    from core.manifest import Manifest
    ask["status"] = "deferred"
    ask["deferred_at"] = _now()
    ask["deferred_ids"] = list(ids)
    ask["reminded_at"] = time.time()
    save_ask(wd, ask)

    def _fn(d: dict) -> None:
        a = dict(d.get("agent") or {})
        a["qa_deferred"] = {"at": _now(), "ids": list(ids), "left": [int(it["i"]) for it in open_items(ask)]}
        a["hold_reason"] = (f"QA gác: {len(open_items(ask))} câu cờ cứng chờ người trả lời Telegram "
                            "— trả lời là job tự xếp lại đầu hàng")[:300]
        d["agent"] = a
    try:
        Manifest(Path(wd)).update(_fn)
    except Exception:  # noqa: BLE001
        pass


def summary_line(res: dict) -> str:
    bits = []
    if res.get("n_fix"):
        bits.append(f"sửa {res['n_fix']} câu")
    if res.get("n_ack"):
        bits.append(f"bỏ cờ {res['n_ack']}")
    return ", ".join(bits) or "không đổi câu nào"


def answer(work_root: Path, *, job_id: str | None = None, action: str = "", text: str = "",
           chat_id: str = "", reply_to: int | str | None = None, by: str = "telegram") -> dict[str, Any]:
    """Người trả lời (nút hoặc reply). Không tự resume — route gọi resume khi `release` = True."""
    work_root = Path(work_root)
    jid = job_id
    if not jid and reply_to:
        jid = job_for_message(work_root, str(chat_id), reply_to)
        if not jid:
            return {"ok": True, "matched": False}
    if not jid:
        return {"ok": False, "error": "thiếu job_id"}
    wd = work_root / jid
    ask = load_ask(wd)
    if not ask:
        return {"ok": False, "matched": True, "job_id": jid, "error": "không có câu hỏi QA cho job này"}
    its = open_items(ask)
    if not its:
        return {"ok": True, "matched": True, "job_id": jid, "release": False, "left": 0,
                "message": f"{jid}: câu hỏi QA đã xử lý xong rồi."}
    if action in ("apply", "skip", "go"):
        res = apply_decision(wd, ask, action, by=by)
    elif is_context_query(text):
        return {"ok": True, "matched": True, "job_id": jid, "release": False, "left": len(its),
                "context": True, "message": context_text(wd, ask, context_nums(text, its))}
    elif text.strip():
        lines = parse_reply(text, its)
        if not lines:
            nums = ", ".join(f"#{it['i']}" for it in its)
            return {"ok": False, "matched": True, "job_id": jid,
                    "error": f"Có {len(its)} câu đang hỏi ({nums}) — reply mỗi dòng dạng `#số: câu mới`."}
        res = apply_decision(wd, ask, "reply", user_lines=lines, by=by)
    else:
        return {"ok": False, "matched": True, "job_id": jid, "error": "thiếu action/text"}
    label = {"apply": "Áp đề xuất", "skip": "Cờ sai – bỏ qua", "go": "Chạy tiếp nguyên trạng",
             "reply": "Ghi câu của bạn"}.get(action or "reply", action)
    out = {"ok": True, "matched": True, "job_id": jid, **res,
           "deferred_ids": list(ask.get("deferred_ids") or []), "release": res["left"] == 0,
           "msgs": list(ask.get("msgs") or [])}
    if res["left"]:
        nums = ", ".join(f"#{i}" for i in [int(it["i"]) for it in open_items(ask)])
        out["message"] = f"{jid}: {label} — {summary_line(res)}. Còn {res['left']} câu chờ ({nums})."
    else:
        out["message"] = f"{jid}: {label} — {summary_line(res)}. Hết cờ → chạy tiếp lồng tiếng + render."
    return out


# ---------------------------------------------------------------------------
# 2026-11-17 qaask2: xem ngữ cảnh (reply «?»), /qa <job>, agent sửa câu → đánh dấu đã xử lý
# ---------------------------------------------------------------------------
_CTX_RE = re.compile(r"^\s*(?:#?\d{1,6}\s*\?\s*[,;\s]*)+$|^\s*\?\s*$")


def is_context_query(text: str) -> bool:
    return bool(_CTX_RE.match(text or ""))


def context_nums(text: str, items: list[dict]) -> list[int]:
    nums = [int(x) for x in re.findall(r"(\d{1,6})", text or "")]
    return nums or [int(it["i"]) for it in items]


def context_text(wd: Path, ask: dict | None, nums: list[int], *, radius: int | None = None) -> str:
    """±radius câu quanh mỗi câu (ZH/VI), câu bị cờ đánh ▶. Không gọi LLM."""
    radius = int(_f("QA_ASK_CONTEXT", 3)) if radius is None else radius
    rows = _rows(Path(wd)) or []
    pos = {}
    for j, r in enumerate(rows):
        if isinstance(r, dict) and "i" in r:
            try:
                pos[int(r["i"])] = j
            except (TypeError, ValueError):
                pass
    flagged = {int(it["i"]) for it in open_items(ask)}
    jid = (ask or {}).get("job_id") or Path(wd).name
    out = [f"🔎 Ngữ cảnh {MARK} {jid} (±{radius} câu, ▶ = câu bị cờ)"]
    shown = 0
    for i in nums:
        j = pos.get(int(i))
        if j is None:
            out.append(f"\n#{i}: không thấy trong script")
            continue
        blk = [""]
        for k in range(max(0, j - radius), min(len(rows), j + radius + 1)):
            r = rows[k]
            if not isinstance(r, dict):
                continue
            ri = r.get("i")
            mark = "▶" if (k == j or ri in flagged) else " "
            blk.append(f"{mark}#{ri} ZH: {_cut(r.get('zh', ''), 90)}")
            blk.append(f"   VI: {_cut(r.get('vi', ''), 110) or '(trống)'}")
        txt = "\n".join(blk)
        if sum(len(x) for x in out) + len(txt) > 3300:
            out.append(f"\n… còn {len(nums) - shown} câu — reply `#số ?` để xem từng câu.")
            break
        out.append(txt)
        shown += 1
    out.append("\nSửa: reply tin HOLD QA bằng `#số: câu mới`.")
    return "\n".join(out)


def resolve_job(work_root: Path, ref: str) -> str | None:
    """Job id đầy đủ hoặc tiền tố duy nhất (≥4 ký tự).

    Agent hay cắt id thành ``9aa089_p01`` trong khi folder thật
    ``9aa0891fbfd1_p01`` — nhận diện dạng ``prefix_pNN``.
    """
    import re
    ref = (ref or "").strip()
    if not ref:
        return None
    root = Path(work_root)
    if not root.is_dir():
        return None
    if (root / ref / "manifest.json").is_file():
        return ref
    if len(ref) < 4:
        return None

    def _with_mf(names: list[str]) -> list[str]:
        return [n for n in names if (root / n / "manifest.json").is_file()]

    # «abc123_p01» / «abc123_p1» → job bắt đầu bằng abc123 và kết thúc _p01
    m = re.match(r"^([0-9a-fA-F]{4,})_p0*(\d+)$", ref)
    if m:
        pref, part_n = m.group(1), int(m.group(2))
        part_re = re.compile(rf"^{re.escape(pref)}[0-9a-fA-F]*_p0*{part_n}$", re.I)
        hits = _with_mf([d.name for d in root.iterdir() if d.is_dir() and part_re.match(d.name)])
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            return None  # mơ hồ — caller báo candidates

    hits = _with_mf([d.name for d in root.iterdir() if d.is_dir() and d.name.startswith(ref)])
    return hits[0] if len(hits) == 1 else None


def resolve_job_candidates(work_root: Path, ref: str, *, limit: int = 8) -> list[str]:
    """Gợi ý khi resolve_job trả None (prefix/_pNN mơ hồ hoặc sai)."""
    import re
    ref = (ref or "").strip()
    root = Path(work_root)
    if not ref or len(ref) < 3 or not root.is_dir():
        return []
    m = re.match(r"^([0-9a-fA-F]{4,})_p0*(\d+)$", ref)
    if m:
        pref, part_n = m.group(1), int(m.group(2))
        part_re = re.compile(rf"^{re.escape(pref)}[0-9a-fA-F]*_p0*{part_n}$", re.I)
        hits = [d.name for d in root.iterdir()
                if d.is_dir() and part_re.match(d.name) and (d / "manifest.json").is_file()]
        if hits:
            return sorted(hits)[:limit]
    pref = ref.split("_p")[0] if "_p" in ref.lower() else ref
    hits = [d.name for d in root.iterdir()
            if d.is_dir() and d.name.startswith(pref) and (d / "manifest.json").is_file()]
    return sorted(hits)[:limit]


def current_sig(rows: list[dict]) -> str:
    """Cùng cách brain tính sig (summarize_flags.high_i, sort) → brain không hỏi trùng."""
    try:
        from agents.agent_quality import scan_script, summarize_flags
        hi = summarize_flags(scan_script(rows)).get("high_i") or []
    except Exception:  # noqa: BLE001
        hi = []
    return ",".join(str(i) for i in sorted(hi))


def show(work_root: Path, ref: str) -> dict[str, Any]:
    """/qa <job>: câu hỏi đang mở (hoặc tạo mới từ cờ high hiện tại) → text + nút."""
    jid = resolve_job(work_root, ref)
    if not jid:
        cands = resolve_job_candidates(work_root, ref)
        hint = f" · ứng viên: {', '.join(cands[:5])}" if cands else ""
        return {"ok": False, "error": (
            f"không thấy job «{ref}» (id đủ / ≥4 ký tự đầu / dạng «9aa089_p01»){hint}"
        )}
    wd = Path(work_root) / jid
    ask = load_ask(wd)
    if not (ask and ask.get("status") in ("open", "deferred") and open_items(ask)):
        rows = _rows(wd)
        if rows is None:
            return {"ok": False, "job_id": jid, "error": "job chưa có script.json"}
        sig = current_sig(rows)
        if not sig:
            return {"ok": True, "job_id": jid, "empty": True,
                    "message": f"{jid}: không còn cờ QA high nào — không có gì cần duyệt."}
        ask = create_ask(wd, jid, sig)
        if not open_items(ask):
            return {"ok": True, "job_id": jid, "empty": True,
                    "message": f"{jid}: không còn cờ QA high nào — không có gì cần duyệt."}
    held = False
    try:
        from core.manifest import Manifest
        import agents.agent_hold as agent_hold
        held = agent_hold.is_held(Manifest(wd).data.get("agent") or {})
    except Exception:  # noqa: BLE001
        pass
    text = render_text(ask)
    if not held:
        text += "\n(Job hiện KHÔNG bị HOLD — trả lời chỉ ghi script, không xếp lại job.)"
    return {"ok": True, "job_id": jid, "text": text, "keyboard": keyboard(jid), "held": held}


def flags_for_agent(work_root: Path, job_id: str) -> dict[str, Any]:
    """Tool agent: câu đang bị cờ QA high (+ đề xuất nếu đã có câu hỏi). Không gọi LLM."""
    jid = resolve_job(work_root, job_id)
    if not jid:
        cands = resolve_job_candidates(work_root, job_id)
        return {"ok": False, "job_id": job_id, "error": "không resolve được job",
                "candidates": cands[:8]}
    wd = Path(work_root) / jid
    ask = load_ask(wd)
    if ask and ask.get("status") in ("open", "deferred") and open_items(ask):
        items = open_items(ask)
        src = "qa_ask"
    else:
        items = collect_items(_rows(wd))
        src = "scan"
    out = [{"i": it["i"], "kinds": it.get("kinds"), "notes": it.get("notes"), "soft": it.get("soft"),
            "zh": it.get("zh"), "vi": it.get("vi"),
            "proposal": ({"verdict": it.get("prop_verdict"), "vi": it.get("prop_vi"),
                          "why": it.get("prop_why"), "conf": it.get("prop_conf")} if has_prop(it) else None)}
           for it in items[:40]]
    return {"job_id": jid, "source": src, "status": (ask or {}).get("status"), "n_open": len(items),
            "items": out,
            "hint": "Sửa bằng pineline_script_edit_line/edit_many → câu được đánh dấu đã xử lý (qa_ack), "
                    "hết câu thì job HOLD tự chạy tiếp."}


def mark_edited(wd: Path, nums: list[int], *, by: str = "agent") -> dict[str, Any]:
    """Sau khi sửa tay câu (agent): gắn qa_ack cho cờ high còn lại trên câu đó + đóng item câu hỏi.
    Trả {acked, left, release} — release=True khi câu hỏi hết item (caller resume nếu job HOLD)."""
    wd = Path(wd)
    nums = {int(x) for x in nums}
    rows = _rows(wd)
    acked = 0
    if rows is not None and nums:
        try:
            from agents.agent_quality import scan_script
            flags = scan_script(rows)
        except Exception:  # noqa: BLE001
            flags = []
        kinds: dict[int, set] = {}
        for f in flags:
            try:
                i = int(f.get("i"))
            except (TypeError, ValueError):
                continue
            if i in nums and f.get("sev") == "high" and f.get("kind") != "empty_vi":
                kinds.setdefault(i, set()).add(str(f.get("kind")))
        stamp = {"mode": "edit", "by": by, "at": _now()}
        touched = False
        for r in rows:
            if not isinstance(r, dict):
                continue
            try:
                i = int(r.get("i", -1))
            except (TypeError, ValueError):
                continue
            if i not in nums:
                continue
            ack = list(r.get("qa_ack") or [])
            for k in sorted(kinds.get(i, ())):
                if k not in ack:
                    ack.append(k)
                    acked += 1
            r["qa_ack"] = ack
            r["qa_ask"] = dict(stamp)
            touched = True
        if touched:
            _write_rows(wd, rows, vi_changed=False)
    ask = load_ask(wd)
    left = None
    release = False
    if ask and ask.get("status") in ("open", "deferred"):
        rr = {int(r.get("i", -1)): r for r in (rows or []) if isinstance(r, dict)}
        done = []
        for it in open_items(ask):
            i = int(it["i"])
            if i not in nums:
                continue
            if "empty_vi" in (it.get("kinds") or []) and not ((rr.get(i) or {}).get("vi") or "").strip():
                continue
            it["done"] = {"mode": "edit", "by": by, "at": _now(), "vi": (rr.get(i) or {}).get("vi")}
            done.append(i)
        left = len(open_items(ask))
        ask.setdefault("events", []).append({"mode": "edit", "by": by, "at": _now(), "done": done, "left": left})
        if done and left == 0:
            ask["status"] = "resolved"
            ask["resolved_at"] = _now()
            release = True
        save_ask(wd, ask)
    return {"acked": acked, "left": left, "release": release,
            "deferred_ids": list((ask or {}).get("deferred_ids") or []), "msgs": list((ask or {}).get("msgs") or [])}
