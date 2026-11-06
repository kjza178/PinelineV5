# -*- coding: utf-8 -*-
"""asr_compare.py — So khớp 2 bản ASR (+ OCR hardsub nếu có).

Luồng đúng ý:
  1) Nano (hoặc engine A) → SRT/JSON #1
  2) Para / Sense (engine B) → SRT/JSON #2
  3) Compare theo thời gian: khớp / lệch / chỉ A / chỉ B
  4) Có OCR hardsub → trọng tài chọn bên gần chữ hardsub hơn

Không align-DTW + gap-fill (tránh nhân bản). Chỉ đối chiếu + chọn.

  python asr_compare.py work/<job>
  python asr_compare.py work/<job> --a asr.fun_nano.json --b asr.paraformer_zh.json
  python asr_compare.py work/<job> --b asr.sensevoice.json --ocr hardsub_cues.json
  python asr_compare.py work/<job> --apply   # ghi asr.json + sub.zh.srt từ consensus

Đầu ra:
  asr.compare.json          — báo cáo chi tiết
  asr.compare.summary.txt   — lệch dễ đọc
  asr.consensus.json        — bản chọn
  sub.zh.consensus.srt
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from hardsub_asr import zh_sim, _norm_zh
from subs import to_srt

DEFAULT_A = "asr.fun_nano.json"
DEFAULT_B_CANDIDATES = (
    "asr.paraformer_zh.json",
    "asr.sensevoice.json",
    "asr.sensevoice_v2.json",
)
DEFAULT_OCR_CANDIDATES = (
    "hardsub_cues.json",
    "asr.hardsub.json",
)

AGREE_SIM = 0.88
OCR_MIN_SIM = 0.55
# cửa sổ tìm cặp B quanh mid A (giây) — Para/Nano thường lệch vài giây
MATCH_WINDOW_S = 8.0
# điểm tối thiểu để nhận cặp (sim*0.65 + time*0.35)
MATCH_MIN_SCORE = 0.42


def _load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict):
        rows = data.get("segments") or data.get("cues") or data.get("items") or []
    else:
        rows = []
    out = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        text = (r.get("text") or r.get("zh") or "").strip()
        st = float(r.get("start") or 0)
        en = float(r.get("end") or st)
        if en < st:
            st, en = en, st
        out.append({"start": st, "end": en, "text": text, "raw": r})
    return out


def _overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def _mid(c: dict) -> float:
    return (float(c["start"]) + float(c["end"])) / 2.0


def _time_affinity(a: dict, b: dict, window_s: float = MATCH_WINDOW_S) -> float:
    """1 = trùng mid; 0 = cách nhau >= window_s."""
    d = abs(_mid(a) - _mid(b))
    if d >= window_s:
        return 0.0
    return 1.0 - d / window_s


def _best_match(
    cue: dict,
    others: list[dict],
    used: set[int] | None = None,
    window_s: float = MATCH_WINDOW_S,
) -> tuple[int | None, float, float, float]:
    """Trả (index, sim, time_aff, score). Ưu tiên chữ + gần thời gian."""
    used = used or set()
    best_i = None
    best_score = -1.0
    best_sim = 0.0
    best_ta = 0.0
    for i, o in enumerate(others):
        if i in used:
            continue
        ta = _time_affinity(cue, o, window_s=window_s)
        if ta <= 0 and _overlap(cue["start"], cue["end"], o["start"], o["end"]) <= 0:
            continue
        sim = zh_sim(cue["text"], o["text"])
        # chữ nặng hơn time — tránh ghép nhầm câu kề khi timeline lệch
        score = sim * 0.65 + ta * 0.35
        if score > best_score:
            best_score = score
            best_sim = sim
            best_ta = ta
            best_i = i
    if best_i is None or best_score < MATCH_MIN_SCORE:
        return None, 0.0, 0.0, 0.0
    return best_i, best_sim, best_ta, best_score


def _ocr_best(cue: dict, ocr: list[dict]) -> tuple[dict | None, float]:
    if not ocr:
        return None, 0.0
    best = None
    best_score = -1.0
    best_sim = 0.0
    for o in ocr:
        ta = _time_affinity(cue, o, window_s=6.0)
        ov = _overlap(cue["start"], cue["end"], o["start"], o["end"])
        if ta <= 0 and ov <= 0:
            continue
        sim = zh_sim(cue["text"], o["text"])
        score = sim * 0.75 + ta * 0.25
        if score > best_score:
            best_score = score
            best_sim = sim
            best = o
    return best, best_sim


def compare_tracks(
    a: list[dict],
    b: list[dict],
    ocr: list[dict] | None = None,
    *,
    a_name: str = "nano",
    b_name: str = "para",
    agree_sim: float = AGREE_SIM,
) -> dict[str, Any]:
    """Đối chiếu A (neo thời gian) với B + OCR."""
    ocr = ocr or []
    used_b: set[int] = set()
    items: list[dict] = []
    stats = {
        "n_a": len(a),
        "n_b": len(b),
        "n_ocr": len(ocr),
        "agree": 0,
        "disagree": 0,
        "only_a": 0,
        "ocr_pick_a": 0,
        "ocr_pick_b": 0,
        "ocr_pick_ocr": 0,
        "ocr_tie": 0,
        "no_ocr": 0,
    }

    for i, ca in enumerate(a):
        bi, sim_ab, ta, score = _best_match(ca, b, used_b)
        cb = b[bi] if bi is not None else None
        matched = bi is not None
        if matched and bi is not None:
            used_b.add(bi)

        ta_txt = ca["text"]
        tb = (cb["text"] if cb else "")

        ocr_hit_a, sim_oa = _ocr_best(ca, ocr)
        ocr_hit_b, sim_ob = (None, 0.0)
        if cb:
            ocr_hit_b, sim_ob = _ocr_best(cb, ocr)
        ocr_text = ""
        sim_ocr = 0.0
        if ocr_hit_a and sim_oa >= (sim_ob or 0):
            ocr_text = ocr_hit_a["text"]
            sim_ocr = sim_oa
        elif ocr_hit_b:
            ocr_text = ocr_hit_b["text"]
            sim_ocr = sim_ob

        status = "only_a"
        pick = ta_txt
        pick_from = a_name
        reason = "chỉ có ở A"

        if matched and sim_ab >= agree_sim:
            status = "agree"
            pick = ta_txt  # ưu tiên Nano chữ
            pick_from = a_name
            reason = f"A≈B sim={sim_ab:.2f} → giữ {a_name}"
            # dù agree: nếu A là spam nền mà B sạch → lấy B
            try:
                from asr_spam import prefer_non_spam
                pick2, tag = prefer_non_spam(ta_txt, tb, prefer_a=True)
                if tag.startswith("spam_a"):
                    pick, pick_from = pick2, b_name
                    reason = f"A≈B nhưng A spam nền → {b_name}"
                    stats["spam_flip"] = stats.get("spam_flip", 0) + 1
            except Exception:  # noqa: BLE001
                pass
            stats["agree"] += 1
        elif matched:
            status = "disagree"
            stats["disagree"] += 1
            spam_resolved = False
            # Ưu tiên bản không phải filler nền trước OCR
            try:
                from asr_spam import prefer_non_spam, is_bg_filler_spam
                if is_bg_filler_spam(ta_txt) or is_bg_filler_spam(tb):
                    pick2, tag = prefer_non_spam(ta_txt, tb, prefer_a=True)
                    if tag != "ok":
                        pick = pick2
                        pick_from = b_name if tag.startswith("spam_a") else a_name
                        reason = f"spam nền → {pick_from} ({tag})"
                        stats["spam_flip"] = stats.get("spam_flip", 0) + 1
                        spam_resolved = True
            except Exception:  # noqa: BLE001
                pass
            if not spam_resolved and ocr_text and sim_ocr >= OCR_MIN_SIM:
                sa = zh_sim(ta_txt, ocr_text)
                sb = zh_sim(tb, ocr_text)
                if sa >= sb + 0.05 and sa >= OCR_MIN_SIM:
                    pick, pick_from = ta_txt, a_name
                    reason = f"OCR trọng tài → {a_name} (sim_a={sa:.2f} sim_b={sb:.2f})"
                    stats["ocr_pick_a"] += 1
                elif sb >= sa + 0.05 and sb >= OCR_MIN_SIM:
                    pick, pick_from = tb, b_name
                    reason = f"OCR trọng tài → {b_name} (sim_a={sa:.2f} sim_b={sb:.2f})"
                    stats["ocr_pick_b"] += 1
                elif sa < OCR_MIN_SIM and sb < OCR_MIN_SIM and len(_norm_zh(ocr_text)) >= 4:
                    pick, pick_from = ocr_text, "ocr"
                    reason = f"OCR thắng cả hai (sim_a={sa:.2f} sim_b={sb:.2f})"
                    stats["ocr_pick_ocr"] += 1
                else:
                    pick, pick_from = ta_txt, a_name
                    reason = f"OCR không phân định rõ → giữ {a_name}"
                    stats["ocr_tie"] += 1
            elif not spam_resolved:
                pick, pick_from = ta_txt, a_name
                reason = f"A≠B sim={sim_ab:.2f} score={score:.2f}, không OCR → giữ {a_name}"
                stats["no_ocr"] += 1
        else:
            stats["only_a"] += 1
            if ocr_text and sim_ocr >= 0.75 and zh_sim(ta_txt, ocr_text) < 0.55:
                pick, pick_from = ocr_text, "ocr"
                reason = "chỉ A nhưng OCR khác rõ → lấy OCR"
                stats["ocr_pick_ocr"] += 1

        items.append({
            "i": i,
            "start": round(ca["start"], 3),
            "end": round(ca["end"], 3),
            "status": status,
            "a": ta_txt,
            "b": tb if matched else "",
            "b_start": round(cb["start"], 3) if cb and matched else None,
            "b_end": round(cb["end"], 3) if cb and matched else None,
            "sim_ab": round(sim_ab, 3) if matched else None,
            "match_score": round(score, 3) if matched else None,
            "ocr": ocr_text,
            "sim_ocr": round(sim_ocr, 3) if ocr_text else None,
            "pick": pick,
            "pick_from": pick_from,
            "reason": reason,
        })

    # B không khớp A
    only_b = []
    for j, cb in enumerate(b):
        if j in used_b:
            continue
        only_b.append({
            "start": round(cb["start"], 3),
            "end": round(cb["end"], 3),
            "b": cb["text"],
            "status": "only_b",
        })
    stats["only_b"] = len(only_b)

    return {
        "a_name": a_name,
        "b_name": b_name,
        "stats": stats,
        "items": items,
        "only_b": only_b,
    }


def consensus_rows(report: dict) -> list[dict]:
    """Xuất rows asr từ report (timing theo A)."""
    rows = []
    for it in report["items"]:
        rows.append({
            "i": len(rows),
            "start": it["start"],
            "end": it["end"],
            "text": it["pick"],
            "align": f"compare_{it['pick_from']}",
            "compare": it["status"],
        })
    return rows


def _summary_text(report: dict) -> str:
    st = report["stats"]
    lines = [
        f"A={report['a_name']} ({st['n_a']})  B={report['b_name']} ({st['n_b']})  OCR={st['n_ocr']}",
        f"agree={st['agree']}  disagree={st['disagree']}  only_a={st['only_a']}  only_b={st['only_b']}",
        f"ocr_pick: a={st['ocr_pick_a']} b={st['ocr_pick_b']} ocr={st['ocr_pick_ocr']} tie={st['ocr_tie']} no_ocr={st['no_ocr']}",
        "",
        "=== DISAGREE (A ≠ B) ===",
    ]
    for it in report["items"]:
        if it["status"] != "disagree":
            continue
        lines.append(
            f"[{it['start']:.1f}-{it['end']:.1f}] sim={it.get('sim_ab')} → {it['pick_from']}"
        )
        lines.append(f"  A: {it['a']}")
        lines.append(f"  B: {it['b']}")
        if it.get("ocr"):
            lines.append(f"  OCR: {it['ocr']} (sim={it.get('sim_ocr')})")
        lines.append(f"  pick: {it['pick']}  ({it['reason']})")
        lines.append("")
    if report.get("only_b"):
        lines.append("=== ONLY B (có ở B, không khớp A) — không chèn tự động ===")
        for ob in report["only_b"][:40]:
            lines.append(f"[{ob['start']:.1f}-{ob['end']:.1f}] {ob['b']}")
        if len(report["only_b"]) > 40:
            lines.append(f"... +{len(report['only_b']) - 40} nữa")
    return "\n".join(lines)


def _pick_b(work: Path, explicit: str | None) -> Path:
    if explicit:
        p = work / explicit if not Path(explicit).is_absolute() else Path(explicit)
        return p
    for name in DEFAULT_B_CANDIDATES:
        p = work / name
        if p.exists():
            return p
    raise FileNotFoundError(
        f"Thiếu bản B trong {work}: {', '.join(DEFAULT_B_CANDIDATES)}"
    )


def _pick_ocr(work: Path, explicit: str | None) -> Path | None:
    if explicit:
        p = work / explicit if not Path(explicit).is_absolute() else Path(explicit)
        return p if p.exists() else None
    for name in DEFAULT_OCR_CANDIDATES:
        p = work / name
        if p.exists():
            return p
    return None


def _b_name_from_path(p: Path) -> str:
    n = p.name.lower()
    if "sense" in n:
        return "sense"
    if "para" in n:
        return "para"
    if "nano" in n:
        return "nano"
    return p.stem.replace("asr.", "").replace("sub.zh.", "")[:24]


def run_compare(
    work_dir: str | Path,
    a_name: str = DEFAULT_A,
    b_name: str | None = None,
    ocr_name: str | None = None,
    apply: bool = False,
    agree_sim: float = AGREE_SIM,
) -> dict:
    work = Path(work_dir)
    a_path = work / a_name if not Path(a_name).is_absolute() else Path(a_name)
    b_path = _pick_b(work, b_name)
    ocr_path = _pick_ocr(work, ocr_name)

    a_rows = _load_rows(a_path)
    b_rows = _load_rows(b_path)
    ocr_rows = _load_rows(ocr_path) if ocr_path else []

    report = compare_tracks(
        a_rows, b_rows, ocr_rows,
        a_name=_b_name_from_path(a_path) if "nano" not in a_path.name.lower() else "nano",
        b_name=_b_name_from_path(b_path),
        agree_sim=agree_sim,
    )
    report["files"] = {
        "a": str(a_path),
        "b": str(b_path),
        "ocr": str(ocr_path) if ocr_path else None,
    }

    cons = consensus_rows(report)
    try:
        from asr_spam import sanitize_asr_rows
        cons, spam_info = sanitize_asr_rows(cons, work_dir=work, heal=True)
        if spam_info.get("n_cleaned") or spam_info.get("n_healed"):
            print(
                f"[compare] spam: cleaned={spam_info['n_cleaned']} "
                f"healed={spam_info['n_healed']}",
                flush=True,
            )
    except Exception as _se:  # noqa: BLE001
        print(f"[compare] asr_spam skip: {_se}", flush=True)
    (work / "asr.compare.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (work / "asr.compare.summary.txt").write_text(
        _summary_text(report), encoding="utf-8",
    )
    (work / "asr.consensus.json").write_text(
        json.dumps(cons, ensure_ascii=False, indent=2), encoding="utf-8",
    )
    (work / "sub.zh.consensus.srt").write_text(
        to_srt(cons, key="text"), encoding="utf-8",
    )

    if apply:
        import shutil
        shutil.copy2(work / "asr.consensus.json", work / "asr.json")
        shutil.copy2(work / "sub.zh.consensus.srt", work / "sub.zh.srt")

    st = report["stats"]
    print(
        f"[ok] compare {report['a_name']}↔{report['b_name']}"
        f"{' +OCR' if ocr_path else ''} → "
        f"agree={st['agree']} disagree={st['disagree']} "
        f"only_a={st['only_a']} only_b={st['only_b']}"
        f"{' [applied→asr.json]' if apply else ''}",
        flush=True,
    )
    print(f"     {work / 'asr.compare.summary.txt'}", flush=True)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Compare Nano SRT vs Para/Sense SRT (+ OCR trọng tài)",
    )
    ap.add_argument("work_dir")
    ap.add_argument("--a", default=DEFAULT_A, help="Bản 1 (mặc định Nano)")
    ap.add_argument("--b", default=None, help="Bản 2 (Para/Sense — tự chọn nếu bỏ trống)")
    ap.add_argument("--ocr", default=None, help="hardsub_cues.json / asr.hardsub.json")
    ap.add_argument("--agree", type=float, default=AGREE_SIM)
    ap.add_argument("--apply", action="store_true", help="Ghi asr.json + sub.zh.srt từ consensus")
    args = ap.parse_args(argv)
    run_compare(
        args.work_dir, a_name=args.a, b_name=args.b, ocr_name=args.ocr,
        apply=args.apply, agree_sim=args.agree,
    )


if __name__ == "__main__":
    main()
