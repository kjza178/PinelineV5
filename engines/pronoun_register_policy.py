#!/usr/bin/env python3
"""Policy xưng hô tổng quát cho mix #1+#3 — không gắn 1 job/phim.

Mục tiêu:
  - Phát hiện cửa sổ CÓ DANH XƯNG BẬC (title hierarchy) + ngôi 2 thân mật «cậu»
  - Ép hướng sửa nhất quán: mặc định «ngươi» (cổ phong / tu luyện / đối đầu)
  - Không để LLM tự do nhảy cậu→ông lung tung (gây ông/ngươi kề nhau)
  - Áp dụng cho mọi job sau này (Điện chủ / Môn chủ / Tộc trưởng / …)

Production: agent_pronoun_pass + REVIEW mask (#1+#3).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

# Danh xưng bậc / chức vị — ZH + VI (mở rộng dần, không hardcode tên nhân vật)
TITLE_RE = re.compile(
    r"(?ix)"
    r"("
    r"门主|殿主|族长|掌门|城主|帮主|盟主|宗主|教主|岛主|阁主|庄主|"
    r"仙尊|仙帝|魔尊|魔帝|帝君|尊者|长老|前辈|师父|师尊|师伯|师叔|"
    r"王爷|殿下|陛下|大人|将军|少主|家主|"
    r"Môn\s*chủ|Điện\s*chủ|Tộc\s*trưởng|Chưởng\s*môn|Thành\s*chủ|"
    r"Bang\s*chủ|Minh\s*chủ|Tông\s*chủ|Giáo\s*chủ|"
    r"Tiền\s*bối|Sư\s*phụ|Sư\s*tôn|Đại\s*nhân|Tướng\s*quân|"
    r"lão\s*già|lão\s*gia|lão\s*tiền\s*bối|"
    r"老家伙|老头"
    r")"
)

INTIMATE_2ND_RE = re.compile(r"(?i)(?<!\w)cậu(?!\w)")  # thô: mọi «cậu» (chỉ để quét nhanh)

# fix 2026-11-11 translate-b1 C3: «cậu» chỉ là ĐẠI TỪ NGÔI 2 ĐỨNG ĐỘC LẬP khi KHÔNG thuộc
# các cụm dưới đây (ngôi 3, danh từ họ hàng, danh xưng + tên…). Không chắc → KHÔNG thay.
#   sau «cậu»: ấy/ta/bé/nhỏ/nhóc/trai/bạn/em/chủ/ấm/ruột/họ/mợ/út/cả/hai/ba/tư/năm/sáu/
#              bảy/tám/chín/mười/của/kia/thanh niên/học sinh/sinh viên
#   trước «cậu»: ông/bà (ông cậu = em/anh của bà), «thằng»
#   sau «cậu» là Tên Riêng viết hoa (cậu Lâm, Cậu Ba …)
_CAU_NOT_2ND_AFTER = (
    "ấy", "ta", "bé", "nhỏ", "nhóc", "trai", "bạn", "em", "chủ", "ấm", "ruột", "họ",
    "mợ", "út", "cả", "hai", "ba", "tư", "năm", "sáu", "bảy", "tám", "chín", "mười",
    "của", "kia", "thanh niên", "học sinh", "sinh viên",
    # review 2026-11-11: chỉ định / danh từ đi sau «cậu» = ngôi 3 («cậu này là ai», «cậu con trai
    # nhà họ Lâm», «cậu thiếu gia», «cậu chàng», «cậu cháu»…) — không chắc → không thay
    "này", "đó", "nọ", "con", "chàng", "thiếu gia", "thiếu niên", "công tử", "cháu",
)
_CAU_NOT_2ND_BEFORE = ("ông", "bà", "thằng")
CAU_RE = re.compile(r"(?i)(?<!\w)cậu(?!\w)")
_CAU_AFTER_RE = re.compile(
    r"(?i)^\s+(?:" + "|".join(re.escape(w) for w in _CAU_NOT_2ND_AFTER) + r")(?!\w)"
)
_CAU_BEFORE_RE = re.compile(
    r"(?i)(?<!\w)(?:" + "|".join(re.escape(w) for w in _CAU_NOT_2ND_BEFORE) + r")\s+$"
)
_CAU_AFTER_PROPER_RE = re.compile(r"^\s+([^\W\d_])")


def _is_standalone_2nd_cau(text: str, m: re.Match) -> bool:
    """«cậu» tại m có phải đại từ ngôi 2 đứng độc lập không (xem danh sách ngoại lệ trên)."""
    after = text[m.end():]
    before = text[: m.start()]
    if _CAU_AFTER_RE.match(after):
        return False
    if _CAU_BEFORE_RE.search(before):
        return False
    mp = _CAU_AFTER_PROPER_RE.match(after)
    if mp and mp.group(1).isupper():
        return False  # cậu + Tên riêng / danh xưng viết hoa
    return True


def standalone_2nd_cau_spans(text: str) -> list[tuple[int, int]]:
    """Vị trí các «cậu» là đại từ ngôi 2 độc lập (để thay máy an toàn)."""
    t = text or ""
    return [(m.start(), m.end()) for m in CAU_RE.finditer(t) if _is_standalone_2nd_cau(t, m)]
FORMAL_2ND_NGUOI_RE = re.compile(r"(?i)(?<!\w)ngươi(?!\w)")
FORMAL_2ND_ONG_RE = re.compile(r"(?i)(?<!\w)ông(?!\w)(?!\s*ta\b)")

# Genre hints từ style_lock / plan
ANCIENT_HINT_RE = re.compile(
    r"(?i)cổ\s*phong|tiên\s*hiệp|tu\s*luyện|xianxia|wuxia|ngươi|tại\s*hạ|bổn\s*tọa"
)
URBAN_HINT_RE = re.compile(r"(?i)đô\s*thị|đời\s*thường|anh/em|tôi·anh|modern|urban")


@dataclass
class RegisterPlan:
    """Kế hoạch ngôi cho 1 job (suy từ style_lock, không từ job id)."""

    mode: str  # ancient | urban | mixed
    preferred_formal_2nd: str  # ngươi | ông
    allow_ong_fallback: bool

    def prompt_rules(self) -> str:
        pref = self.preferred_formal_2nd
        return (
            "QUY TẮC XƯNG HÔ (áp mọi phim, không theo tên nhân vật):\n"
            "1) Nếu cửa sổ có DANH XƯNG BẬC (Môn chủ/Điện chủ/Tộc trưởng/掌门/殿主/族长/"
            "tiền bối/lão già/…) VÀ câu đang dùng «cậu» thân mật → ĐỔI ngôi 2 sang "
            f"«{pref}» (ưu tiên). CẤM giữ cậu.\n"
            "2) CẤM nhảy lung tung ông↔ngươi trong cùng cửa sổ cùng đối tượng. "
            f"Chuẩn hóa về «{pref}».\n"
            "3) «Các cậu» trong cửa sổ bậc → «Các {pref}» / «Các vị» nếu hợp nghĩa.\n"
            "4) Đô thị thuần (không title bậc): giữ tôi/cậu/anh/em — đừng ép ngươi.\n"
            "5) CHỈ đổi đại từ/xưng hô; giữ nghĩa còn lại. "
            "JSON {\"fixes\":[{\"i\":0,\"vi\":\"...\"}]}."
        )


def detect_mode(plan: dict | None) -> str:
    plan = plan or {}
    lock = plan.get("style_lock") if isinstance(plan.get("style_lock"), dict) else {}
    blob = " ".join(
        str(plan.get(k) or lock.get(k) or "")
        for k in ("mode", "default_register", "note", "pronoun_policy", "register", "genre", "tone")
    )
    if isinstance(plan.get("style"), dict):
        blob += " " + " ".join(str(v) for v in plan["style"].values())
    if lock:
        blob += " " + " ".join(
            str(v) for v in lock.values() if not isinstance(v, (dict, list))
        )
    ancient = bool(ANCIENT_HINT_RE.search(blob))
    urban = bool(URBAN_HINT_RE.search(blob))
    mode = (
        plan.get("mode")
        or lock.get("mode")
        or plan.get("default_register")
        or lock.get("default_register")
        or ""
    ).strip().lower()
    if mode in ("ancient", "urban", "mixed"):
        return mode
    if ancient and urban:
        return "mixed"
    if ancient:
        return "ancient"
    if urban:
        return "urban"
    return "mixed"


def build_register_plan(plan: dict | None) -> RegisterPlan:
    mode = detect_mode(plan)
    # mixed/ancient → ngươi (ổn định cho phim có cổ phong + title)
    # urban thuần → ông chỉ khi thật sự gọi người lớn tuổi; mặc định ít đụng title
    if mode == "urban":
        return RegisterPlan(mode=mode, preferred_formal_2nd="ông", allow_ong_fallback=True)
    return RegisterPlan(mode=mode, preferred_formal_2nd="ngươi", allow_ong_fallback=False)


def window_has_title(texts: Iterable[str]) -> bool:
    blob = " ".join(t or "" for t in texts)
    return bool(TITLE_RE.search(blob))


def cue_has_intimate_2nd(vi: str) -> bool:
    # fix 2026-11-11 translate-b1 C3: chỉ tính «cậu» ngôi 2 độc lập (không «cậu ấy/ruột/bé»…)
    return bool(standalone_2nd_cau_spans(vi or ""))


def scan_title_intimate_issues(
    rows: list[dict],
    *,
    window: int = 2,
    existing_ids: set | None = None,
) -> list[dict]:
    """Thêm issue khi cue có «cậu» và cửa sổ ±window có title bậc."""
    existing_ids = existing_ids or set()
    issues: list[dict] = []
    n = len(rows)
    for idx, r in enumerate(rows):
        i = r.get("i")
        if i in existing_ids:
            continue
        if r.get("manual"):
            continue  # fix 2026-11-11 translate-b1 C2: câu sửa tay không đưa vào lô LLM
        vi = r.get("vi") or ""
        if not cue_has_intimate_2nd(vi):
            continue
        win = rows[max(0, idx - window) : idx + window + 1]
        texts = [(x.get("vi") or "") + " " + (x.get("zh") or "") for x in win]
        if not window_has_title(texts):
            continue
        titles = sorted({m.group(0) for m in TITLE_RE.finditer(" ".join(texts))})
        issues.append(
            {
                "i": i,
                "zh": r.get("zh"),
                "vi": vi,
                "reasons": [
                    "title_intimate_mismatch: cửa sổ có danh xưng bậc "
                    f"({', '.join(titles[:6])}) nhưng câu dùng «cậu» — "
                    "đổi ngôi 2 sang hình thức trang trọng theo register plan"
                ],
                "policy_tag": "title_intimate",
            }
        )
        existing_ids.add(i)
    return issues


def mechanical_cau_to_formal(vi: str, preferred: str) -> str:
    """Fallback máy: cậu → preferred; Các cậu → Các preferred / Các vị."""
    if not vi or not preferred:
        return vi
    out = vi
    # fix 2026-11-11 translate-b1 C3: chỉ thay «cậu» ngôi 2 ĐỘC LẬP; «cậu ấy/ta/ruột/bé»,
    # «ông cậu», «cậu Lâm»… giữ nguyên. Thay từ phải sang trái để không lệch vị trí.
    spans = standalone_2nd_cau_spans(out)
    for a, b in reversed(spans):
        pre = out[:a]
        mc = re.search(r"(?i)(?<!\w)các\s+$", pre)
        if mc:
            # «các cậu» → «các {preferred}»; viết hoa «Các» khi bản gốc viết hoa hoặc ở đầu câu
            # (review 2026-11-11: trước đây luôn «Các» → «Tôi bảo Các ngươi» giữa câu)
            head = pre[: mc.start()]
            cap = pre[mc.start()].isupper() or not head.strip() or bool(
                re.search(r"[.!?…:\n]\s*$", head)
            )
            out = head + ("Các " if cap else "các ") + preferred + out[b:]
        else:
            out = pre + preferred + out[b:]
    # capital first if whole-sentence start
    if out and out[0].islower() and (vi[:1].isupper() if vi else False):
        out = out[0].upper() + out[1:]
    # Ngươi/Ông đầu câu
    if preferred == "ngươi":
        out = re.sub(r"(^|[.!?…]\s*)ngươi\b", lambda m: m.group(1) + "Ngươi", out)
    elif preferred == "ông":
        out = re.sub(r"(^|[.!?…]\s*)ông\b", lambda m: m.group(1) + "Ông", out)
    return out


def normalize_ong_nguoi_in_title_window(
    rows: list[dict],
    changed_ids: set[int],
    preferred: str,
    *,
    window: int = 2,
) -> int:
    """Sau LLM: nếu cue vừa sửa còn ông+ngươi loạn quanh title → ép preferred."""
    n_fix = 0
    pos = {int(r["i"]): j for j, r in enumerate(rows)}
    for i in list(changed_ids):
        j = pos.get(int(i))
        if j is None:
            continue
        win = rows[max(0, j - window) : j + window + 1]
        texts = [(x.get("vi") or "") + " " + (x.get("zh") or "") for x in win]
        if not window_has_title(texts):
            continue
        if rows[j].get("manual"):
            continue  # fix 2026-11-11 translate-b1 C2
        vi = rows[j].get("vi") or ""
        if preferred == "ngươi" and FORMAL_2ND_ONG_RE.search(vi) and not re.search(
            r"(?i)\bông\s+ta\b", vi
        ):
            # ông (hô ngữ) → ngươi trong cửa sổ title
            new = re.sub(r"(?i)(?<!\w)Các\s+ông(?!\w)", "Các ngươi", vi)
            new = re.sub(r"(?i)(?<!\w)ông(?!\w)(?!\s*ta\b)", "ngươi", new)
            new = re.sub(r"(^|[.!?…]\s*)ngươi\b", lambda m: m.group(1) + "Ngươi", new)
            if new != vi:
                rows[j]["vi"] = new
                n_fix += 1
        if cue_has_intimate_2nd(rows[j].get("vi") or ""):
            new = mechanical_cau_to_formal(rows[j].get("vi") or "", preferred)
            if new != rows[j].get("vi"):
                rows[j]["vi"] = new
                n_fix += 1
    return n_fix


def enforce_remaining_cau(
    rows: list[dict],
    preferred: str,
    *,
    window: int = 2,
) -> list[dict]:
    """Sau cùng: còn cậu trong title window → máy đổi (không chờ LLM)."""
    changes = []
    for idx, r in enumerate(rows):
        if not isinstance(r, dict) or r.get("manual"):
            continue  # fix 2026-11-11 translate-b1 C2/C3: không thay máy câu sửa tay
        vi = r.get("vi") or ""
        if not cue_has_intimate_2nd(vi):
            continue
        win = rows[max(0, idx - window) : idx + window + 1]
        texts = [(x.get("vi") or "") + " " + (x.get("zh") or "") for x in win]
        if not window_has_title(texts):
            continue
        new = mechanical_cau_to_formal(vi, preferred)
        if new != vi:
            changes.append(
                {
                    "stage": "pronoun_qa_mech",
                    "i": int(r["i"]),
                    "zh": r.get("zh"),
                    "vi_before": vi,
                    "vi_after": new,
                    "policy": f"mech_cau_to_{preferred}",
                }
            )
            r["vi"] = new
    return changes
