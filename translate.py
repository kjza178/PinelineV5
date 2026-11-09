"""
translate.py — STAGE dịch: "lập phương án" (hồ sơ nhân vật + XƯNG HÔ) rồi dịch
CÓ NGỮ CẢNH, khớp độ dài.

Nâng cấp so với bản cũ:
  1) PLAN pass đọc toàn transcript -> hồ sơ nhân vật + thuật ngữ + MA TRẬN XƯNG HÔ
     (ai gọi ai xưng gì) + genre/tone. Đây là thứ giữ bản dịch nhất quán & tự nhiên.
  2) Dịch theo lô nhưng LUÔN kèm: plan + vài câu NGỮ CẢNH liền trước (nguồn+dịch)
     -> mạch thoại, đại từ, tham chiếu đúng.
  3) Khớp độ dài: mỗi câu kèm 'sec' (ô phụ đề) -> ép dịch súc tích, vừa thời lượng.

Đầu vào : work/<job>/asr.json
Đầu ra  : work/<job>/glossary.json  (plan: characters/terms/pronouns/tone...)
          work/<job>/script.json     ({i,start,end,zh,vi})

Model: đặt TRANSLATE_MODEL (vd kr/claude-sonnet-4.5) để dùng model mạnh riêng cho
dịch; không đặt thì dùng LLM_MODEL mặc định.

Chạy tay:
    export LLM_API_KEY=... LLM_BASE_URL=... TRANSLATE_MODEL=kr/claude-sonnet-4.5
    python translate.py work/<job>
    python translate.py work/<job> --batch 30 --force
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# Đảm bảo stdout/stderr luôn UTF-8 trên Windows console
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from llm import chat, parse_json, unload_local, is_local, LLMUnavailable
from vram import free_gpu_vram
from fileio import atomic_write_json, read_json_checkpoint
from manifest import Manifest

STAGE = "translate"
MODEL = os.getenv("TRANSLATE_MODEL") or None    # None -> chat() dùng LLM_MODEL
# Model RÀ VĂN PHONG (lượt 2). Ưu tiên REVIEW_MODEL → TRANSLATE_MODEL → LLM_MODEL.
# Tất cả đi qua 9router API (không dùng Ollama local).
REVIEW_MODEL = os.getenv("REVIEW_MODEL") or MODEL or None
try:
    from config import get as _cfg_get
except Exception:  # noqa: BLE001
    def _cfg_get(key: str, default: str | None = None) -> str | None:
        return os.getenv(key) or default


def _tmodel() -> str | None:
    """TRANSLATE_MODEL đọc lúc gọi (server import module 1 lần — MODEL ở trên bị đóng băng)."""
    return _cfg_get("TRANSLATE_MODEL") or None


def _rmodel() -> str | None:
    return _cfg_get("REVIEW_MODEL") or _tmodel()


def _is_llama_local_model(m: str | None) -> bool:
    if not m:
        return False
    mc = m.lower().strip()
    if mc.startswith("llama/"):
        return True
    if mc in ("local", "llama", "default"):
        return True
    return any(p in mc for p in ("gemma4-12b", "gemma4-26b", "qwen36", "qat", "mtp"))

# Ngữ cảnh trước mỗi lô — lô nhỏ + ctx vừa phải = nhớ tên riêng tốt hơn
CTX_LINES = int(_cfg_get("TRANSLATE_CTX_LINES", "6") or 6)
# oneshot: dịch cả danh sách 1 lần (llama-server ctx lớn). auto = bật nếu không phải Ollama local/.
ONESHOT_MAX = int(os.getenv("TRANSLATE_ONESHOT_MAX") or "350")


def _meaning_rules() -> str:
    """Quy tắc chống dịch đen / lệch ngữ cảnh (lồng tiếng phim)."""
    return (
        "NGHĨA & NGỮ CẢNH (quan trọng):\n"
        "- Ưu tiên NGHĨA THOẠI trong cảnh, không dịch từng chữ.\n"
        "- Thành ngữ / châm biếm / đá xoáy phải dịch ĐÚNG Ý tiếng Việt thông dụng, "
        "không dịch đen. Ví dụ: 吃醋 ≈ «ghen», không «uống giấm»; "
        "打天下 ≈ «đánh thiên hạ / dựng nghiệp», KHÔNG «đánh hạ thiên hạ».\n"
        "- 脑子进水: nếu câu trước/chiêu có 水·Thủy·úng (vd Thánh Trảm Thủy Mộng, "
        "盛产水) → GIỮ đòn chữ «úng nước / não úng nước»; "
        "không có setup nước → «não cậu có vấn đề rồi / điên à». "
        "CẤM «não vào nước / ngập nước».\n"
        "- 穷酸 (khinh ngoại hình/khí thế): «thảm hại / xơ xác / tệ hại», "
        "KHÔNG «nghèo nàn» (nghĩa tiền bạc).\n"
        "- 眼馋: «thèm muốn / thèm đến chảy nước miếng», không cụt «thèm».\n"
        "- MẠCH XƯNG HÔ (bắt buộc): giữ cùng quan hệ trong cụm thoại liền nhau "
        "(cậu/tôi/hắn…). "
        "CẤM nhảy sang mẹ–con / phụ–mẫu chỉ vì gặp chữ 娘/妈 nếu cảnh đang đối đầu, "
        "mời nô lệ, chiến đấu — trừ khi bảng pronouns hoặc ngữ cảnh rõ là thoại với mẹ. "
        "Trong đô thị dị năng, 娘 đứng đầu câu thường là ASR lệch của 那 "
        "(«này / thế này»), không phải gọi mẹ.\n"
        "- 先下手为强 / vài 成语 hay gặp: ưu tiên Hán Việt "
        "«Tiên hạ thủ vi cường» (không ép mọi thành ngữ cổ). "
        "Thành ngữ khác: dịch tự nhiên hoặc HV tùy mạch — không nhồi từ điển.\n"
        "- 嘲讽 (game/chiến đấu): theo ngữ cảnh — khiêu khích / khích tướng / mỉa mai…; "
        "KHÔNG mặc định «nhạo báng». "
        "Cụm lạ «嘲讽看» thường ASR thiếu dấu — TÁCH xem 1–2 câu trước/sau; "
        "KHÔNG bịa nghĩa cho 看; KHÔNG khóa cứng một bản dịch cố định.\n"
        "- Đọc cả CỤM thoại liền nhau: câu sau thường đáp / đá / chơi chữ câu trước "
        "(setup → punchline). Giữ mối liên hệ đó trong bản Việt.\n"
        "- Giữ: nghĩa, cảm xúc, hài, mỉa, thứ bậc, quan hệ xã hội, thuật ngữ "
        "game/fantasy, và GIÁ TRỊ SỐ.\n"
        "- SỐ & ĐƠN VỊ TRUNG (bắt buộc — hay dịch TỆ):\n"
        "  · Giữ đúng bậc 万/亿/兆/万亿; không bịa số.\n"
        "  · CẤM calque Hán–Việt: «ba vạn», «hai ba vạn», «3 vạn tỷ», "
        "«ba vạn một nghìn một», «mười vạn năm». Nghe như máy dịch.\n"
        "  · Ưu tiên SỐ Ả RẬP + đơn vị Việt/game, hoặc đọc Việt tự nhiên:\n"
        "    万 = 10 000 → «30 000» / «ba chục nghìn» (KHÔNG «ba vạn»);\n"
        "    亿 = 100 triệu → N亿 = N/10 tỷ (八百亿=80 tỷ; 3100亿=310 tỷ);\n"
        "    万亿 = 1 000 tỷ (10^12) → «3 000 tỷ» / «ba nghìn tỷ» "
        "(KHÔNG «3 vạn tỷ»);\n"
        "    十万年 → «trăm nghìn năm» (KHÔNG «mười vạn năm»).\n"
        "  · Viết số lớn bằng DẤU CÁCH nghìn: «31 000 tỷ», «30 000 người» "
        "(CẤM «31.000» / «31,000» — dễ cắt nhầm khi tách sub).\n"
        "  · Máu/HP/sát thương trong hệ thống·game: viết số rõ; "
        "ưu tiên đơn vị tỷ khi gốc có 亿.\n"
        "  · HP combat (bắt buộc): 三万一千亿/三万一千一血 = **31 000 tỷ** máu "
        "(CẤM 3 100 tỷ máu / 31.001); 3100亿 hồi = **310 tỷ** = 1% máu; "
        "八百亿 = 80 tỷ. ASR sót「亿」cạnh đấm/hồi → vẫn hệ 亿. "
        "百分之十 của 31 000 = 3 100; 1% = 310.\n"
        "  · Ngoài ngữ cảnh máu·亿: 三万一千一 ≈ 31 001; 两三万 ≈ "
        "hai–ba chục nghìn.\n"
        "  · CẤM calque «ba vạn tỷ», «3,1 vạn tỷ», «vạn tỷ» lẫn với 万亿 "
        "(万亿 = 1 000 tỷ).\n"
        "- Tên riêng / địa danh / chiêu thức / thuật ngữ game giữ nhất quán theo "
        "phương án; phần còn lại phải tự nhiên như người Việt nói trong phim.\n"
        "- TÊN RIÊNG (hay dịch đen): 2 chữ đứng đầu câu rồi 他/她/你 "
        "(vd «过山他现在…») → Hán Việt tên người («Quá Sơn»), "
        "CẤM dịch động từ đen («qua núi»). "
        "Ưu tiên bảng characters/terms; không có thì phiên HV, giữ nguyên suốt phim.\n"
    )


def _style_rules() -> str:
    """Quy tắc Manhua / short-drama: cứng Hán Việt + mềm hiện đại + xưng hô."""
    return (
        "VĂN PHONG MANHUA / SHORT DRAMA (bắt buộc):\n"
        "- Yếu tố CỨNG (world-building): ưu tiên Hán Việt, nhất quán theo bảng nhân vật/"
        "thuật ngữ — tên riêng, địa danh, cấp bậc, kỹ năng, chỉ số, khí tức, ấn ký, "
        "tông môn, vật phẩm, hệ thống. Ví dụ phong cách: Huyết Viêm Tinh, Nhị Tinh Hành, "
        "Giác Tỉnh Giả, Thập Bát Tầng Ấn Ký, Huyết Tế, Phản Thương, Sinh Lực. "
        "Không phiên âm bừa; không dịch đen nếu đã có trong phương án.\n"
        "- Yếu tố MỀM (thoại + cảm xúc): tiếng Việt nói tự nhiên như phim short drama VN "
        "— NGẮN, GÃY, có lực, đúng cảm xúc bá đạo/châm biếm. "
        "KHÔNG văn mẫu / thơ hóa / cổ kính thừa / sến kiếm hiệp / giải thích thừa. "
        "VD: tránh «Đầu óc ngu muội rồi ngươi» → «Đúng là não có vấn đề rồi.»; "
        "tránh «Ngươi có muốn chết không» → «Muốn chết à?»; "
        "tránh «Tôi cảm nhận được một luồng sức mạnh kỳ lạ» → «Tôi cảm thấy một luồng lực kỳ lạ.»; "
        "tránh «Phải tốn rất nhiều công sức mới đến được đây» → «Khó khăn lắm mới đến được đây.»\n"
        "- Xưng hô: có bảng trong phương án → BÁM ĐÚNG. Không có bảng → suy theo "
        "THỂ LOẠI (KHÔNG mặc định Ta–Ngươi):\n"
        "  · hiện đại/đô thị đời thường → tôi·anh·em·mày·tao… "
        "(CẤM Ta–Ngươi; CẤM tại hạ/bổn tọa…).\n"
        "  · đô thị dị năng / tinh cầu / hệ thống + võ·KH (mixed): xưng hô đời thường "
        "như hiện đại; thoại chiến & thuật ngữ cứng = Hán Việt + sắc võ/cổ nhẹ "
        "(chiêu, khí tức, ấn ký…); danh phận (công chúa…) giữ; "
        "CẤM tại hạ/trẫm/bệ hạ mặc định.\n"
        "  · tu tiên·cổ trang·wuxia·xianxia·huyền ảo vị thế rõ → Ta–Ngươi + "
        "địa chỉ cổ phù hợp cảnh (xem khối XƯNG HÔ CỔ trong phương án nếu có); "
        "câu thoại vẫn tự nhiên, không sến.\n"
        "- Mục tiêu: nghe đúng thể loại, còn màu Trung (Hán Việt đúng chỗ), thoại trôi — "
        "không nặng Hán Việt toàn bài; không calque máy.\n"
    )


def _character_rules() -> str:
    """Chống nhầm nhân vật / sai giới tính khi dịch thoại."""
    return (
        "NHÂN VẬT & GIỚI TÍNH (bắt buộc):\n"
        "- Bám ĐÚNG bảng NHÂN VẬT: mỗi tên zh ↔ đúng 1 tên vi; CẤM đổi/gộp/hoán tên "
        "gần nhau (vd 苏林 ≠ 苏尘).\n"
        "- Giới tính trong bảng quyết định cách gọi: nam → anh/cậu/chú/ông…; "
        "nữ → chị/cô/em gái/bà… — CẤM gọi nhầm giới (gọi nữ là «anh» trừ khi thoại "
        "gốc cố ý).\n"
        "- Xưng hô theo cặp who→to trong bảng; không áp một kiểu cho cả cast.\n"
        "- Biệt danh/alias trong bảng phải map về đúng nhân vật đó.\n"
        "- Không bịa thêm nhân vật; không đổi giới tính đã ghi trong phương án.\n"
    )


_ANCIENT_GENRE_KEYS = (
    "tu tiên", "tu tien", "cổ trang", "co trang", "kiếm hiệp", "kiem hiep",
    "wuxia", "xianxia", "xuanhuan", "huyền ảo", "huyen ao", "tiên hiệp", "tien hiep",
    "võ hiệp", "vo hiep", "cổ đại", "co dai", "ancient", "fantasy cổ",
)


def _is_ancient_fantasy_genre(plan: dict | None) -> bool:
    """True khi phương án/genre thuộc tu tiên·cổ trang·wuxia·xianxia (không mixed đô thị)."""
    if not isinstance(plan, dict):
        return False
    lock = plan.get("style_lock") if isinstance(plan.get("style_lock"), dict) else {}
    if (lock.get("mode") or "").lower() == "mixed":
        return False  # mixed dùng luật riêng, không inject full ancient bank
    if (lock.get("mode") or "").lower() == "xianxia":
        return True
    blob = " ".join(
        str(plan.get(k) or "") for k in ("genre", "tone", "content_type", "pronoun_notes")
    ).lower()
    if not blob.strip():
        return False
    # hiện đại / đô thị rõ → không ancient dù có chữ "huyền"
    modern = ("đô thị", "do thi", "hiện đại", "hien dai", "đời thường", "doi thuong",
              "vlog", "urban", "modern", "học đường", "hoc duong", "dị năng", "tinh cầu")
    if any(m in blob for m in modern) and not any(k in blob for k in (
        "tu tiên", "tu tien", "cổ trang", "co trang", "wuxia", "xianxia",
    )):
        return False
    return any(k in blob for k in _ANCIENT_GENRE_KEYS)


def _is_mixed_genre(plan: dict | None) -> bool:
    if not isinstance(plan, dict):
        return False
    lock = plan.get("style_lock") if isinstance(plan.get("style_lock"), dict) else {}
    if (lock.get("mode") or "").lower() == "mixed":
        return True
    blob = " ".join(
        str(plan.get(k) or "") for k in ("genre", "tone", "content_type")
    ).lower()
    urban = any(k in blob for k in ("đô thị", "dị năng", "tinh cầu", "hệ thống"))
    combat = any(k in blob for k in ("võ", "chiến", "khoa huyễn", "huyền ảo", "combat"))
    return urban and combat


def _mixed_address_rules() -> str:
    """Đô thị dị năng + võ/KH: xưng hô hiện đại + cổ phong Hán Việt."""
    return (
        "VĂN PHONG MIXED — ĐÔ THỊ + CỔ PHONG (bắt buộc):\n"
        "- Xưng hô đời thường: tôi/anh/em/cậu/mày/tao — CẤM tại hạ/bổn tọa/trẫm/bệ hạ.\n"
        "- CỔ PHONG Hán Việt cho thuật ngữ cứng (chiêu, ấn ký, tinh cầu, cấp) "
        "và vài 成语 hay dùng (vd Tiên hạ thủ vi cường) — không nhồi thành ngữ hiếm.\n"
        "- Thoại chiến / bá đạo: NGẮN, GÃY, có lực — như phim short drama VN, "
        "không văn mẫu / không «xin vui lòng» / không giải thích thừa.\n"
        "  · BAD→GOOD: «Mà lại nghèo nàn đến thế» → «Mà lại thảm hại đến thế.»\n"
        "  · BAD→GOOD: «Sau này giúp tôi chinh phục thiên hạ, được không?» "
        "→ «Sau này giúp tôi đánh thiên hạ, được không?»\n"
        "  · BAD→GOOD: «Não cậu có vấn đề rồi» (khi có setup Thủy/úng) "
        "→ «…làm não cậu úng nước rồi.»\n"
        "  · BAD→GOOD: «Để cậu mở mang tầm mắt» → «Để cậu biết tay.»\n"
        "- 嘲讽 / «嘲讽看»: theo ngữ cảnh (không hard-lock); "
        "nghi ASR — đối chiếu câu trước/sau; CẤM «nhạo báng xem».\n"
        "- Danh phận (công chúa, thiếu gia…) giữ khi là chức vị.\n"
    )


def _ancient_address_rules() -> str:
    """Chỉ inject khi genre tu tiên/cổ — không áp cho đô thị hiện đại."""
    return (
        "XƯNG HÔ CỔ / FANTASY (tu tiên·cổ trang·wuxia·xianxia·cung đấu):\n"
        "- Chọn theo quan hệ & địa vị (không nhồi hết mọi câu). Nhóm chính:\n"
        "  · Khiêm xưng: tại hạ, tiểu nhân, tiểu nữ, vãn bối, hạ thần, vi thần, "
        "nô tài, nô tỳ, thần thiếp, thảo dân, bần đạo…\n"
        "  · Tự tôn: ta, bổn tọa, bản tôn, bản vương, bản cung, trẫm, quả nhân, ai gia…\n"
        "  · Gọi đối phương: ngươi, các hạ, túc hạ, huynh đài, cô nương, tiểu thư, "
        "công tử, thiếu gia, đại nhân, điện hạ, bệ hạ, tiền bối, đạo hữu…\n"
        "  · Sư môn: sư phụ/sư tôn, đồ nhi, sư huynh/tỷ/đệ/muội, chưởng môn, bang chủ…\n"
        "  · Vợ chồng: phu quân, nương tử, tướng công, lang quân, phu nhân…\n"
        "- Cặp thường đi đôi: tại hạ↔các hạ; hạ thần↔bệ hạ; nô tài↔chủ tử; "
        "đồ nhi↔sư phụ.\n"
        "- Nếu có style_lock.address_bank / prefer trong phương án → bám theo đó.\n"
        "- CẤM mặc định đổ «ta/ngươi» mọi câu; CẤM bạn/mình/tớ/cậu hiện đại "
        "(trừ nhân vật cố ý lệch thời / thể loại lẫn).\n"
        "- Thoại như phim cổ trang VN nghe được — không thơ hóa, không nhồi từ cổ.\n"
    )


def _translate_rules(plan: dict | None = None) -> str:
    """Gộp nghĩa + văn phong + nhân vật (+ xưng hô theo genre)."""
    out = _meaning_rules() + _style_rules() + _character_rules()
    if _is_mixed_genre(plan):
        out += _mixed_address_rules()
    elif _is_ancient_fantasy_genre(plan):
        out += _ancient_address_rules()
    return out

def _ocr_name_hints(work_dir: Path | None) -> list[str]:
    """Tên/chữ trên hình từ ocr.json (nếu có) — gợi ý cho PLAN."""
    if not work_dir:
        return []
    p = Path(work_dir) / "ocr.json"
    if not p.exists():
        return []
    try:
        rows = json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return []
    seen: set[str] = set()
    out: list[str] = []
    for r in rows if isinstance(rows, list) else []:
        zh = (r.get("zh") or r.get("text") or "").strip()
        if len(zh) < 2 or zh in seen:
            continue
        # Ưu tiên cụm ngắn (tên), bỏ câu dài
        if len(zh) > 12:
            continue
        seen.add(zh)
        out.append(zh)
        if len(out) >= 40:
            break
    return out


def _resolve_translate_mode(mode: str | None, model: str | None, n_todo: int) -> str:
    """Trả 'oneshot' | 'batch'.

    Mặc định **batch** (lô TRANSLATE_BATCH) — oneshot full-file hay sót/lẫn số/tên.
    """
    raw = mode
    if not raw:
        try:
            raw = _cfg_get("TRANSLATE_MODE", None)
        except Exception:  # noqa: BLE001
            raw = None
    m = (raw or os.getenv("TRANSLATE_MODE") or "batch").strip().lower()
    if m in ("oneshot", "full", "1"):
        return "oneshot"
    if m in ("batch", "lô", "lo"):
        return "batch"
    # auto
    if is_local(model or _tmodel()):
        return "batch"   # Ollama: oneshot dễ rỗng/timeout
    if n_todo <= 0:
        return "batch"
    if n_todo > ONESHOT_MAX:
        print(f"[trans] auto: {n_todo} câu > ONESHOT_MAX={ONESHOT_MAX} -> batch")
        return "batch"
    # auto + llama-server + file ngắn: vẫn batch (ổn định hơn oneshot)
    return "batch"


def _has_cjk(text: str) -> bool:
    """Còn ký tự Hán trong bản dịch = model dịch sót/hỏng (đặc biệt model nhỏ local)."""
    return any("一" <= c <= "鿿" for c in (text or ""))


_CJK_RUN_RE = re.compile(r"[\u3400-\u9fff]+")

# Thuật ngữ hay bị model local để nguyên Hán trong câu VI → kẹt forever vì _has_cjk xoá
_CJK_LEFTOVER_VI: dict[str, str] = {
    "增幅": "tăng cường",
    "技能": "kỹ năng",
    "冷却": "hồi chiêu",
    "等级": "cấp",
    "经验": "kinh nghiệm",
    "血量": "máu",
    "攻击": "tấn công",
    "防御": "phòng thủ",
    "伤害": "sát thương",
    "暴击": "bạo kích",
    "闪避": "né tránh",
    "护盾": "lá chắn",
    "复活": "hồi sinh",
    "传送": "dịch chuyển",
    "驻地": "cứ địa",
    "封锁": "phong tỏa",
}


def _salvage_mixed_vi(vi: str, *, zh: str = "", plan: dict | None = None) -> str:
    """Cứu VI lẫn Hán (vd «Đạt được 100% 增幅.») — không thì trả '' để vá lại.

    Trước đây `_has_cjk` xoá cả câu → «增幅» kẹt missing mãi dù đã bấm Dịch vá.
    """
    t = (vi or "").strip()
    if not t:
        return ""
    if not _has_cjk(t):
        return t
    # Phần Latin gốc (trước khi thay thuật ngữ) — tránh biến câu toàn Hán thành «tăng cường»
    latin0_plain = re.sub(r"\s+", "", _CJK_RUN_RE.sub("", t))
    repl: dict[str, str] = dict(_CJK_LEFTOVER_VI)
    if isinstance(plan, dict):
        for term in plan.get("terms") or []:
            if not isinstance(term, dict):
                continue
            z = (term.get("zh") or "").strip()
            v = (term.get("vi") or "").strip()
            if z and v and _has_cjk(z) and not _has_cjk(v):
                repl[z] = v
    try:
        for seed in _DEFAULT_HARD_TERMS:
            z = (seed.get("zh") or "").strip()
            v = (seed.get("vi") or "").strip()
            if z and v and _has_cjk(z) and not _has_cjk(v):
                repl.setdefault(z, v)
    except NameError:
        pass
    for z, v in sorted(repl.items(), key=lambda kv: -len(kv[0])):
        if z in t:
            t = t.replace(z, v)
    if not _has_cjk(t):
        return re.sub(r"\s{2,}", " ", t).strip()
    # Chỉ gỡ CJK sót khi câu vốn đã có đủ chữ Việt/Latin
    if len(latin0_plain) < 4:
        return ""
    cjk_n = sum(1 for c in t if "一" <= c <= "鿿")
    if cjk_n <= 8:
        t2 = _CJK_RUN_RE.sub("", t)
        t2 = re.sub(r"\s{2,}", " ", t2)
        t2 = re.sub(r"\s+([.,!?;:])", r"\1", t2).strip(" ,.;:")
        if t2 and not _has_cjk(t2):
            return t2
    return ""


def _plan_mode() -> str:
    """file = upload full ZH SRT (Aurora); sample = mẫu cũ (head/mid/tail)."""
    return (_cfg_get("PLAN_MODE", "file") or "file").strip().lower()


def _plan_json_schema(target: str) -> str:
    return f"""Trả JSON đúng cấu trúc:
{{
  "content_type": "doi_thoai | dan_chuyen | tai_lieu | khac",
  "genre": "thể loại cụ thể",
  "tone": "văn phong + quy ước xưng hô khớp thể loại",
  "style_lock": {{"mode": "mixed|modern|xianxia|ancient", "default_register": "mixed|toi-cau|anh-em|ancient-ta-nguoi", "note": "phim có thể đổi đô thị↔tu tiên — ưu tiên mixed"}},
  "characters": [
    {{"zh": "tên gốc chuẩn", "vi": "tên {target} chuẩn", "gender": "nam|nữ|?", "role": "vai trò", "aliases": ["biến thể ASR"], "personality": "tính cách"}}
  ],
  "relationship_matrix": {{}},
  "terms": [
    {{"zh": "từ gốc", "vi": "Hán Việt", "type": "lock|chiêu thức|cấp bậc|môn phái|địa danh|khác"}}
  ],
  "pronouns": [
    {{"who": "tên vi", "to": "tên vi hoặc chung", "self": "tôi/mày/tao/ta", "call": "anh/cậu/mày/ngươi"}}
  ],
  "scenes": [
    {{"scene_id": 1, "range": [0, 50], "location": "", "characters": [], "situation": "", "tone": "", "pronouns_in_scene": ""}}
  ],
  "asr_patch_rules": [
    {{"pattern_zh": "", "correct_meaning_vi": "", "note": ""}}
  ]
}}"""


def _plan_seed_blocks(
    name_hints: list[str] | None,
    series_plan: dict | None,
    *,
    soft_ocr: bool = True,
) -> str:
    """OCR = seed mềm (có thể sai). Series characters = kế thừa mạnh."""
    parts: list[str] = []
    if name_hints:
        if soft_ocr:
            parts.append(
                "GỢI Ý OCR (CHỮ TRÊN HÌNH — THƯỜNG SAI / DƯ THỪA):\n"
                "- Chỉ nhận vào characters/terms KHI cụm ZH khớp ≥2 lần trong thoại SRT "
                "hoặc rõ là tên riêng lặp.\n"
                "- CẤM đưa OCR vào glossary nếu chỉ xuất hiện 1 lần hoặc giống watermark/UI.\n"
                f"- Danh sách gợi ý: {', '.join(name_hints[:40])}\n"
            )
        else:
            parts.append(
                "GỢI Ý TÊN OCR (chỉ đưa vào characters nếu khớp thoại):\n"
                + ", ".join(name_hints[:40]) + "\n"
            )
    if series_plan and isinstance(series_plan, dict):
        chars_list = [
            f"{c.get('zh')}={c.get('vi')} ({c.get('gender', '?')})"
            for c in series_plan.get("characters", [])
            if isinstance(c, dict) and c.get("zh") and c.get("vi")
        ]
        # terms series chỉ soft-list (kho đã gầy type=lock)
        terms_list = [
            f"{t.get('zh')}={t.get('vi')}"
            for t in series_plan.get("terms", [])
            if isinstance(t, dict)
            and t.get("zh") and t.get("vi")
            and str(t.get("type") or "").lower() == "lock"
        ]
        pr_list = [
            f"{p.get('who')}->{p.get('to')}: xưng '{p.get('self')}', gọi '{p.get('call')}'"
            for p in series_plan.get("pronouns", [])
            if isinstance(p, dict) and p.get("who")
        ]
        if chars_list or terms_list or pr_list:
            block = "\n[SERIES SEED — nhân vật/xưng hô đã chốt bộ trước]:\n"
            if chars_list:
                block += f"- Characters (GIỮ tên VI trừ khi ASR chứng minh sai rõ): {'; '.join(chars_list[:30])}\n"
            if terms_list:
                block += f"- Terms lock (chỉ type=lock): {'; '.join(terms_list[:20])}\n"
            if pr_list:
                block += f"- Pronouns: {'; '.join(pr_list[:20])}\n"
            block += "Chỉ BỔ SUNG nhân vật/term mới có trong file thoại này.\n"
            parts.append(block)
    return "".join(parts)


def _normalize_plan_data(data: dict | None) -> dict:
    if not isinstance(data, dict):
        data = {}
    for k in ("characters", "terms", "pronouns", "asr_patch_rules", "scenes"):
        if not isinstance(data.get(k), list):
            data[k] = []
    data.setdefault("content_type", "doi_thoai")
    data.setdefault("genre", "Đô thị dị năng / Huyền ảo")
    data.setdefault("tone", "")
    if not isinstance(data.get("relationship_matrix"), dict):
        data["relationship_matrix"] = {}
    chars_ok = []
    for c in data["characters"]:
        if not isinstance(c, dict):
            continue
        g = str(c.get("gender") or "?").strip().lower()
        if g in ("male", "m", "nam", "男"):
            c["gender"] = "nam"
        elif g in ("female", "f", "nữ", "nu", "女"):
            c["gender"] = "nữ"
        elif g not in ("nam", "nữ", "?"):
            c["gender"] = "?"
        if not isinstance(c.get("aliases"), list):
            c["aliases"] = []
        chars_ok.append(c)
    data["characters"] = chars_ok
    return data


def _remap_scenes_cue_to_i(plan: dict, cue_to_i: list[int]) -> dict:
    """Nếu GPT trả range theo số thứ tự cue SRT (1..N) → map về segment i."""
    if not cue_to_i or not isinstance(plan, dict):
        return plan
    scenes = plan.get("scenes")
    if not isinstance(scenes, list):
        return plan
    n = len(cue_to_i)

    def _map_one(v) -> int | None:
        try:
            x = int(v)
        except (TypeError, ValueError):
            return None
        # cue 1-based
        if 1 <= x <= n:
            return cue_to_i[x - 1]
        return x  # đã là i thật

    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        rng = sc.get("range")
        if isinstance(rng, list) and len(rng) >= 2:
            a, b = _map_one(rng[0]), _map_one(rng[1])
            if a is not None and b is not None:
                sc["range"] = [min(a, b), max(a, b)]
        for key in ("start_i", "end_i"):
            if key in sc:
                m = _map_one(sc.get(key))
                if m is not None:
                    sc[key] = m
    return plan


def _build_plan_from_file(
    work_dir: Path,
    segments: list[dict],
    target: str,
    model: str | None,
    name_hints: list[str] | None,
    series_plan: dict | None,
) -> dict:
    """Upload full ZH SRT → GPT đọc file (Aurora) → glossary. OCR chỉ seed mềm."""
    from pronoun_consistency import write_zh_srt
    from llm import aurora_upload_file, chatgpt_chat_with_file

    lines = []
    cue_to_i: list[int] = []
    for s in segments:
        zh = (s.get("text") or "").strip()
        if not zh:
            continue
        try:
            ii = int(s.get("i"))
        except (TypeError, ValueError):
            continue
        lines.append({"i": ii, "zh": zh})
        cue_to_i.append(ii)
    if not lines:
        return {}
    srt_path = write_zh_srt(work_dir, lines, segments=segments, annotate_i=True)
    print(f"[plan] upload full ZH SRT {srt_path.name} ({len(lines)} câu)…", flush=True)
    up = aurora_upload_file(srt_path, purpose="assistants")
    file_id = up["id"]
    seed = _plan_seed_blocks(name_hints, series_plan, soft_ocr=True)
    prompt = (
        f"Bạn là chuyên gia lập glossary dịch phim Trung → {target}.\n"
        "File đính kèm = TOÀN BỘ phụ đề ZH (SRT từ ASR, có thể nghe nhầm).\n"
        "Mỗi cue có tag [i=N] — N là chỉ số segment thật.\n"
        "ĐỌC HẾT file — không đoán từ mẫu ngắn.\n"
        "1) Thể loại + văn phong; style_lock.mode ưu tiên mixed nếu phim có cả đô thị và tu tiên/cổ.\n"
        "2) Nhân vật: gom đồng âm ASR về 1 tên VI; aliases = biến thể nghe nhầm.\n"
        "3) Terms: chỉ type=lock cho danh hiệu/máu/số cứng; còn lại type thường.\n"
        "4) Pronouns + scenes: range=[start_i,end_i] theo số trong tag [i=…] "
        "(KHÔNG dùng số thứ tự block SRT 1..N).\n"
        "5) asr_patch_rules cho cụm hay nhầm.\n"
        f"{seed}\n"
        f"{_plan_json_schema(target)}\n"
        "CHỈ trả JSON."
    )
    # PLAN_MODEL thắng; model từ UI chỉ dùng nếu đã là chatgpt/aurora
    plan_cfg = (_cfg_get("PLAN_MODEL") or "chatgpt/gpt-5-6-mini").strip()
    m_in = (model or "").strip()
    if m_in.lower().startswith(("chatgpt/", "aurora/")):
        use_model = m_in
    else:
        use_model = plan_cfg
    try:
        timeout = int(_cfg_get("PLAN_FILE_TIMEOUT", "180") or 180)
    except ValueError:
        timeout = 180
    timeout = max(60, min(timeout, 420))
    out = chatgpt_chat_with_file(
        file_id,
        prompt,
        model=use_model,
        temperature=0.15,
        max_tokens=8192,
        json_mode=True,
        timeout=timeout,
        base=up.get("base"),
        account_id=up.get("account_id") or None,
    )
    data = parse_json(out) if out else {}
    if not isinstance(data, dict):
        raise RuntimeError("plan-file: JSON không phải object")
    if data.get("error") and not data.get("characters"):
        raise RuntimeError(f"plan-file: GPT không đọc file — {data.get('error')}")
    if not (data.get("characters") or data.get("terms")):
        raise RuntimeError("plan-file: JSON rỗng / thiếu characters")
    data = _remap_scenes_cue_to_i(data, cue_to_i)
    data["_meta"] = {
        **(data.get("_meta") if isinstance(data.get("_meta"), dict) else {}),
        "plan_mode": "file",
        "plan_model": use_model,
        "n_asr_lines": len(lines),
        "srt": str(srt_path.name),
        "plan_file_timeout": timeout,
    }
    return data


def _build_plan_sample(
    segments: list[dict],
    target: str,
    model: str | None,
    name_hints: list[str] | None,
    series_plan: dict | None,
) -> dict:
    """Fallback: mẫu head/mid/tail (plan cũ)."""
    valid_segs = [s for s in segments if (s.get("text") or "").strip()]
    tot = len(valid_segs)
    if tot <= 250:
        sample_segs = valid_segs
    else:
        head = valid_segs[:80]
        mid_idx = tot // 2
        mid = valid_segs[mid_idx:mid_idx + 80]
        tail = valid_segs[-80:]
        kw = ("苏", "林", "战", "嫣", "烈", "影", "灵", "黎", "天宫", "神域", "级", "血", "哥", "姐", "弟", "妹")
        extras = [
            s for s in valid_segs[80:mid_idx] + valid_segs[mid_idx + 80:-80]
            if any(k in (s.get("text") or "") for k in kw)
        ][:120]
        sample_segs = sorted(head + mid + tail + extras, key=lambda s: s.get("i", 0))

    lines = [f"{s.get('i', idx)}|{(s.get('text') or '').strip()}" for idx, s in enumerate(sample_segs)]
    full_text = "\n".join(lines)
    seed = _plan_seed_blocks(name_hints, series_plan, soft_ocr=True)

    sys_prompt = (
        "Bạn là Chuyên gia Cao Cấp phân tích kịch bản và ngôn ngữ phim Trung Quốc "
        f"chuẩn bị phương án dịch sang {target}.\n"
        "Lập HỒ SƠ BẤT BIẾN: thể loại, nhân vật (gom ASR đồng âm), xưng hô, thuật ngữ, "
        "phân cảnh, asr_patch_rules. OCR seed có thể SAI.\n"
        "CHỈ trả JSON hợp lệ."
    )
    user_prompt = (
        f"Transcript mẫu (i|câu):\n\"\"\"{full_text}\"\"\"\n{seed}\n"
        + _plan_json_schema(target)
    )

    primary_model = model or _cfg_get("LLM_MODEL") or None
    fallback_model = _tmodel() or primary_model or "local"
    data: dict = {}
    print(f"[plan] sample-mode model={primary_model or 'default'}…", flush=True)
    try:
        out = chat(
            [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
            model=primary_model, temperature=0.2, json_mode=True, max_tokens=6000, timeout=120,
        )
        if out and out.strip():
            data = parse_json(out)
    except Exception as e:
        print(f"[plan] Model chính lỗi: {e}", flush=True)

    if not data or not data.get("characters"):
        print(f"[plan] fallback sample → {fallback_model}", flush=True)
        try:
            out_fb = chat(
                [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                model=fallback_model, temperature=0.2, json_mode=False, max_tokens=4000, timeout=120,
            )
            if out_fb and out_fb.strip():
                data = parse_json(out_fb)
        except Exception as e2:
            print(f"[plan] fallback lỗi: {e2}", flush=True)

    if not data:
        data = {
            "content_type": "doi_thoai",
            "genre": "Đô thị dị năng / Chiến đấu",
            "tone": "Hành động kịch tính, ngắn gọn, xưng hô mày/tao/tôi/anh",
            "characters": [], "terms": [], "pronouns": [],
            "relationship_matrix": {}, "asr_patch_rules": [],
        }
    data["_meta"] = {
        **(data.get("_meta") if isinstance(data.get("_meta"), dict) else {}),
        "plan_mode": "sample",
        "n_sample": len(sample_segs),
    }
    return data


def build_plan(
    segments: list[dict],
    target: str = "Tiếng Việt",
    model: str | None = None,
    name_hints: list[str] | None = None,
    series_plan: dict | None = None,
    work_dir: str | Path | None = None,
) -> dict:
    """Lập glossary: mặc định upload full ZH SRT (PLAN_MODE=file); fallback sample."""
    mode = _plan_mode()
    data: dict = {}
    if mode in ("file", "upload", "srt") and work_dir:
        try:
            data = _build_plan_from_file(
                Path(work_dir), segments, target, model, name_hints, series_plan,
            )
            print(
                f"[plan] file-mode OK · chars={len(data.get('characters') or [])} "
                f"terms={len(data.get('terms') or [])}",
                flush=True,
            )
        except Exception as e_file:  # noqa: BLE001
            print(f"[plan] file-mode lỗi ({e_file}) → fallback sample", flush=True)
            data = {}
    if not data or not (data.get("characters") or data.get("terms")):
        data = _build_plan_sample(segments, target, model, name_hints, series_plan)

    data = _normalize_plan_data(data)
    try:
        from context_studio.schema import apply_style_lock_from_genre
        data = apply_style_lock_from_genre(data)
    except Exception:  # noqa: BLE001
        pass
    print(
        f"[plan] ✅ Global Plan: {len(data['characters'])} NV, {len(data['terms'])} terms, "
        f"mode={(data.get('_meta') or {}).get('plan_mode', '?')}",
        flush=True,
    )
    return data


def _plan_block(p: dict) -> str:
    """Đổ plan ra text nhét vào mọi prompt dịch. CHỐNG LỖI: model đôi khi trả
    characters/terms/pronouns là list of STRING (không phải dict) -> né 'str.get'."""
    if not isinstance(p, dict):
        return ""

    def _lst(key):
        v = p.get(key)
        return v if isinstance(v, list) else []

    lines = []
    if p.get("content_type") or p.get("genre") or p.get("tone"):
        lines.append(f"LOẠI: {p.get('content_type','')} | THỂ LOẠI: {p.get('genre','')} | VĂN PHONG: {p.get('tone','')}")
    if _lst("characters"):
        lines.append("NHÂN VẬT (KHÔNG nhầm tên / giới tính):")
        for c in _lst("characters"):
            if isinstance(c, dict):
                al = c.get("aliases") or []
                al_s = f", alias={','.join(al)}" if al else ""
                gh = c.get("gender_hint") or ""
                gh_s = f", chứng={gh}" if gh else ""
                lines.append(
                    f"  - {c.get('zh')} = {c.get('vi')} "
                    f"[giới={c.get('gender','?')}] ({c.get('role','')}){al_s}{gh_s}"
                    + (f", tự xưng={c.get('self_ref')}" if c.get("self_ref") else "")
                    + (f", quan hệ={c.get('relation')}" if c.get("relation") else "")
                    + (f", ngôi 3 (他/她)={c.get('ref3')}" if c.get("ref3") else "")
                )
            elif isinstance(c, str) and c.strip():
                lines.append(f"  - {c.strip()}")
    lock = p.get("style_lock") if isinstance(p.get("style_lock"), dict) else None
    if lock and lock.get("mode") and lock.get("mode") != "unknown":
        lines.append(
            f"STYLE LOCK: mode={lock.get('mode')} | "
            f"policy={lock.get('pronoun_policy') or ''}"
        )
        emo = (lock.get("emotional_style") or "").strip()
        if emo:
            lines.append(f"  GIỌNG CẢM XÚC (bám sát khi viết thoại): {emo}")
        forbid = lock.get("forbid") or []
        prefer = lock.get("prefer") or []
        if forbid:
            # mixed: chỉ liệt kê forbid quan trọng (tránh nhồi bank cổ dài)
            if _is_mixed_genre(p):
                key_forb = [str(x) for x in forbid if isinstance(x, str) and any(
                    k in str(x).lower() for k in (
                        "tại hạ", "bổn tọa", "trẫm", "bệ hạ", "nhạo", "ta/ngươi", "phiên âm",
                    )
                )][:12]
                lines.append("  CẤM: " + ", ".join(key_forb or [str(x) for x in forbid[:8]]))
            else:
                lines.append("  CẤM: " + ", ".join(str(x) for x in forbid[:24]))
        # Ưu tiên cụm văn phong dài trước, rồi địa chỉ ngắn
        soft_pref = [str(x) for x in prefer if isinstance(x, str) and len(str(x)) > 12][:8]
        short_pref = [str(x) for x in prefer if isinstance(x, str) and len(str(x)) <= 12][:20]
        if soft_pref:
            lines.append("  ƯU TIÊN VĂN: " + "; ".join(soft_pref))
        if short_pref:
            lines.append("  ƯU TIÊN địa chỉ: " + ", ".join(short_pref))
        bank = lock.get("address_bank") if isinstance(lock.get("address_bank"), dict) else None
        if bank and _is_ancient_fantasy_genre(p):
            # gợi ý ngắn theo nhóm chính — chỉ tu tiên/cổ; mixed không nhồi bank cổ
            for bk in ("self_humble", "self_noble", "call_female", "sect_order", "court"):
                vals = bank.get(bk) or []
                if vals:
                    lines.append(f"  bank.{bk}: " + ", ".join(str(x) for x in vals[:10]))
    if _lst("terms"):
        hard = [t for t in _lst("terms") if isinstance(t, dict)
                and str(t.get("type") or "").lower() in ("chengyu", "idiom", "combat_taunt", "lock")]
        soft = [t for t in _lst("terms") if t not in hard]
        if hard:
            lines.append("THÀNH NGỮ / LOCK (BẮT BUỘC đúng chữ VI — không dịch lại):")
            for t in hard:
                lines.append(f"  - {t.get('zh')} = {t.get('vi')} [{t.get('type','')}]")
        if soft:
            lines.append("THUẬT NGỮ (dùng đúng):")
            for t in soft:
                if isinstance(t, dict):
                    lines.append(f"  - {t.get('zh')} = {t.get('vi')} [{t.get('type','')}]")
                elif isinstance(t, str) and t.strip():
                    lines.append(f"  - {t.strip()}")
    if _lst("pronouns"):
        lines.append("XƯNG HÔ (BẮT BUỘC theo đúng cặp who→to):")
        for pr in _lst("pronouns"):
            if isinstance(pr, dict):
                lines.append(f"  - {pr.get('who')} nói với {pr.get('to')}: tự xưng \"{pr.get('self')}\", gọi là \"{pr.get('call')}\"")
            elif isinstance(pr, str) and pr.strip():
                lines.append(f"  - {pr.strip()}")
    try:
        from pronoun_consistency import lock_banner
        lb = lock_banner(p)
        if lb:
            lines.append(lb.rstrip())
    except Exception:
        pass
    if p.get("pronoun_notes"):
        lines.append(f"Ghi chú xưng hô: {p['pronoun_notes']}")
    if _lst("scenes"):
        lines.append("TỔNG QUAN PHÂN CẢNH TẬP NÀY:")
        for sc in _lst("scenes")[:5]:
            if isinstance(sc, dict):
                rng = sc.get("range") or [sc.get("start_i", 0), sc.get("end_i", 0)]
                loc = sc.get("location") or "Cảnh"
                chars = ", ".join(sc.get("characters") or [])
                lines.append(f"  - Phân cảnh {sc.get('scene_id', '?')} [câu {rng[0]}->{rng[1]}]: {loc} (Có mặt: {chars})")
    if _is_mixed_genre(p):
        lines.append(_mixed_address_rules().rstrip())
    elif _is_ancient_fantasy_genre(p):
        lines.append(_ancient_address_rules().rstrip())
    return "\n".join(lines)


def _plan_block_for_qa(p: dict) -> str:
    """Plan block gọn cho pronoun-QA / GPT vá đỏ — chỉ genre+style+pronouns.

    Bỏ characters + terms (analyze đã upload file / không cần dump lại) để tránh
    Aurora 413 khi nhét full `_plan_block` (~97KB) vào `_chatgpt_chat`.
    """
    if not isinstance(p, dict):
        return ""

    def _lst(key):
        v = p.get(key)
        return v if isinstance(v, list) else []

    lines = []
    if p.get("content_type") or p.get("genre") or p.get("tone"):
        lines.append(
            f"LOẠI: {p.get('content_type','')} | THỂ LOẠI: {p.get('genre','')} | "
            f"VĂN PHONG: {p.get('tone','')}"
        )
    lock = p.get("style_lock") if isinstance(p.get("style_lock"), dict) else None
    if lock and lock.get("mode") and lock.get("mode") != "unknown":
        lines.append(
            f"STYLE LOCK: mode={lock.get('mode')} | "
            f"policy={lock.get('pronoun_policy') or ''}"
        )
        emo = (lock.get("emotional_style") or "").strip()
        if emo:
            lines.append(f"  GIỌNG CẢM XÚC (bám sát khi viết thoại): {emo}")
        forbid = lock.get("forbid") or []
        prefer = lock.get("prefer") or []
        if forbid:
            if _is_mixed_genre(p):
                key_forb = [str(x) for x in forbid if isinstance(x, str) and any(
                    k in str(x).lower() for k in (
                        "tại hạ", "bổn tọa", "trẫm", "bệ hạ", "nhạo", "ta/ngươi", "phiên âm",
                    )
                )][:12]
                lines.append("  CẤM: " + ", ".join(key_forb or [str(x) for x in forbid[:8]]))
            else:
                lines.append("  CẤM: " + ", ".join(str(x) for x in forbid[:24]))
        soft_pref = [str(x) for x in prefer if isinstance(x, str) and len(str(x)) > 12][:8]
        short_pref = [str(x) for x in prefer if isinstance(x, str) and len(str(x)) <= 12][:20]
        if soft_pref:
            lines.append("  ƯU TIÊN VĂN: " + "; ".join(soft_pref))
        if short_pref:
            lines.append("  ƯU TIÊN địa chỉ: " + ", ".join(short_pref))
        bank = lock.get("address_bank") if isinstance(lock.get("address_bank"), dict) else None
        if bank and _is_ancient_fantasy_genre(p):
            for bk in ("self_humble", "self_noble", "call_female", "sect_order", "court"):
                vals = bank.get(bk) or []
                if vals:
                    lines.append(f"  bank.{bk}: " + ", ".join(str(x) for x in vals[:10]))
    if _lst("pronouns"):
        lines.append("XƯNG HÔ (BẮT BUỘC theo đúng cặp who→to):")
        for pr in _lst("pronouns"):
            if isinstance(pr, dict):
                lines.append(
                    f"  - {pr.get('who')} nói với {pr.get('to')}: "
                    f"tự xưng \"{pr.get('self')}\", gọi là \"{pr.get('call')}\""
                )
            elif isinstance(pr, str) and pr.strip():
                lines.append(f"  - {pr.strip()}")
    if p.get("pronoun_notes"):
        lines.append(f"Ghi chú xưng hô: {p['pronoun_notes']}")
    try:
        from pronoun_consistency import lock_banner
        lb = lock_banner(p)
        if lb:
            lines.append(lb.rstrip())
    except Exception:
        pass
    return "\n".join(lines)


def _resolve_scene_context(plan: dict | None, rows: list[dict]) -> str:
    """Xác định phân cảnh hiện tại của lô câu thoại (Scene-based context injection)."""
    if not isinstance(plan, dict) or not rows:
        return ""
    scenes = plan.get("scenes") or []
    if not scenes or not isinstance(scenes, list):
        return ""

    idxs = [r.get("i", 0) for r in rows if isinstance(r, dict) and "i" in r]
    if not idxs:
        return ""
    start_i = min(idxs)
    end_i = max(idxs)

    matched = []
    for sc in scenes:
        if not isinstance(sc, dict):
            continue
        rng = sc.get("range") or []
        s_from = rng[0] if len(rng) > 0 else sc.get("start_i", 0)
        s_to = rng[1] if len(rng) > 1 else sc.get("end_i", 999999)
        if max(start_i, s_from) <= min(end_i, s_to):
            matched.append(sc)

    if not matched:
        return ""

    blocks = []
    for sc in matched[:2]:
        loc = sc.get("location") or "Bối cảnh phim"
        sit = sc.get("situation") or ""
        chars = ", ".join(sc.get("characters") or [])
        tone = sc.get("tone") or ""
        pr = sc.get("pronouns_in_scene") or ""

        b = f"🎬 [PHÂN CẢNH HIỆN TẠI]: {loc}\n"
        if sit:
            b += f"  - Tình huống: {sit}\n"
        if chars:
            b += f"  - Nhân vật có mặt: {chars}\n"
        if pr:
            b += f"  - ⚠️ XƯNG HÔ TRONG CẢNH (BẮT BUỘC): {pr}\n"
        if tone:
            b += f"  - Giọng điệu/Cảm xúc: {tone}\n"
        # Ghép rule who→to khớp nhân vật có mặt trong cảnh
        if chars and isinstance(plan.get("pronouns"), list):
            char_set = {c.strip() for c in (sc.get("characters") or []) if str(c).strip()}
            hit = []
            for pru in plan.get("pronouns") or []:
                if not isinstance(pru, dict):
                    continue
                who, to = (pru.get("who") or "").strip(), (pru.get("to") or "").strip()
                if who and (who in char_set or any(who in x for x in char_set)):
                    hit.append(
                        f"{who}→{to or '?'}: xưng «{pru.get('self') or '?'}», "
                        f"gọi «{pru.get('call') or '?'}»"
                    )
            if hit:
                b += "  - Ma trận xưng hô (lọc theo cảnh): " + "; ".join(hit[:8]) + "\n"
        blocks.append(b.strip())

    return "\n" + "\n---\n".join(blocks) + "\n\n"


# --- Hard lock: glossary terms + post-pass (không phụ thuộc LLM nhớ rule) -----

# Seed gọn: thành ngữ hay gặp + số máu dễ calque (không lock 嘲讽 — cần ngữ cảnh)
_DEFAULT_HARD_TERMS: list[dict] = [
    {"zh": "先下手为强", "vi": "Tiên hạ thủ vi cường.", "type": "chengyu"},
    # Máu hệ 亿: 三万一千亿 = 31 000 tỷ (ASR hay sót「亿」→ 三万一千一血).
    # 1% = 310 (= hồi 3100亿 → 310 tỷ). CẤM «3 100 tỷ máu» / «31.001».
    {"zh": "我一共三万一千一血", "vi": "Tổng cộng tôi có 31 000 tỷ máu.", "type": "lock"},
    {"zh": "我一共三万一千亿血", "vi": "Tổng cộng tôi có 31 000 tỷ máu.", "type": "lock"},
    {"zh": "八百亿", "vi": "80 tỷ.", "type": "lock"},
    {"zh": "不过我每秒回血3100亿，这点伤", "vi": "Nhưng mỗi giây tôi hồi 310 tỷ máu, chút sát thương này.", "type": "lock"},
    {"zh": "不过我每秒回血三千一百亿", "vi": "Nhưng mỗi giây tôi hồi 310 tỷ máu.", "type": "lock"},
    # Tên riêng hay bị dịch đen
    {"zh": "过山", "vi": "Quá Sơn", "type": "lock"},
    # 逆 = nghịch (KHÔNG nghị ← nhầm 议/議). Thành ngữ / danh hiệu nhân vật hay gặp.
    {"zh": "逆天而行", "vi": "Nghịch Thiên Nhi Hành", "type": "lock"},
    # Cạnh đấm 亿: 两三万 ≈ 两三万亿
    {"zh": "我总是两三万", "vi": "Tôi luôn quanh mức hai–ba nghìn tỷ.", "type": "lock"},
]

# Soft style: nhét glossary để LLM thấy — KHÔNG hard-lock cả câu (cần ngữ cảnh)
_DEFAULT_STYLE_TERMS: list[dict] = [
    {"zh": "穷酸", "vi": "thảm hại / xơ xác (KHÔNG nghèo nàn)", "type": "style"},
    {"zh": "打天下", "vi": "đánh thiên hạ / dựng nghiệp (KHÔNG chinh phục thiên hạ)", "type": "style"},
    {"zh": "脑子进水", "vi": "úng nước / não úng nước (khi có setup Thủy·水); không thì «não có vấn đề»", "type": "style"},
    {"zh": "眼馋", "vi": "thèm muốn / thèm đến chảy nước miếng", "type": "style"},
    {"zh": "好大力气", "vi": "khó khăn lắm / tốn công lắm (KHÔNG «tốn rất nhiều công sức»)", "type": "style"},
    {"zh": "废什么话", "vi": "phí lời làm gì / nói làm gì", "type": "style"},
]


def _norm_zh_cue(zh: str) -> str:
    """Chuẩn hóa cue ZH để khớp lock (bỏ dấu câu/space)."""
    import re
    t = (zh or "").strip()
    t = re.sub(r"[\s。．，、！？!?,.…·\-—~～\"'“”‘’（）()【】\[\]<>《》]+", "", t)
    return t


def ensure_hard_terms(plan: dict | None) -> dict:
    """Gắn seed chengyu/taunt vào glossary.terms (không đè bản tay đã có)."""
    if not isinstance(plan, dict):
        plan = {}
    terms = list(plan.get("terms") or []) if isinstance(plan.get("terms"), list) else []
    by_zh = {}
    for t in terms:
        if isinstance(t, dict) and (t.get("zh") or "").strip():
            by_zh[_norm_zh_cue(str(t["zh"]))] = t
    mode = ""
    lock = plan.get("style_lock") if isinstance(plan.get("style_lock"), dict) else {}
    if isinstance(lock, dict):
        mode = str(lock.get("mode") or "").lower()
    # modern thuần: không nhồi chengyu HV (tránh lệch đời thường)
    if mode == "modern" and not _is_mixed_genre(plan):
        plan["terms"] = terms
        return plan
    added = 0
    fixed = 0
    for seed in _DEFAULT_HARD_TERMS + _DEFAULT_STYLE_TERMS:
        key = _norm_zh_cue(seed["zh"])
        if key in by_zh:
            cur = by_zh[key]
            if not cur.get("type"):
                cur["type"] = seed["type"]
            # Lock: đè bản sai đã biết (HP 31.001 / 逆→Nghị…)
            if seed.get("type") == "lock":
                cur_vi = str(cur.get("vi") or "")
                seed_vi = str(seed.get("vi") or "")
                bad = (
                    "31.001" in cur_vi
                    or "31,001" in cur_vi
                    or ("3.100 tỷ máu" in cur_vi and "31 000" in seed_vi)
                    or ("3 100 tỷ máu" in cur_vi and "31 000" in seed_vi)
                    or ("máu" in seed_vi and "tỷ" in seed_vi and "tỷ" not in cur_vi)
                    or (
                        seed["zh"] == "逆天而行"
                        and "Nghị Thiên" in cur_vi
                        and "Nghịch" not in cur_vi
                    )
                )
                if bad and seed_vi:
                    cur["vi"] = seed_vi
                    cur["type"] = "lock"
                    fixed += 1
            continue
        terms.append(dict(seed))
        by_zh[key] = terms[-1]
        added += 1
    plan["terms"] = terms
    # Nhân vật: cùng trap 逆天而行 hay bị PLAN ghi sai âm «Nghị»
    chars = list(plan.get("characters") or []) if isinstance(plan.get("characters"), list) else []
    char_fixed = 0
    for c in chars:
        if not isinstance(c, dict):
            continue
        zh = str(c.get("zh") or "")
        vi = str(c.get("vi") or "")
        if "逆天而行" not in zh and zh.strip() != "逆天而行":
            continue
        if "Nghị Thiên" in vi and "Nghịch" not in vi:
            c["vi"] = vi.replace("Nghị Thiên", "Nghịch Thiên")
            if c["vi"] == vi:
                c["vi"] = "Nghịch Thiên Nhi Hành"
            char_fixed += 1
            fixed += 1
    plan["characters"] = chars
    if added or fixed:
        print(
            f"[plan] +{added} hard/style terms"
            + (f", fixed {fixed} lock" if fixed else "")
            + (f" (chars {char_fixed})" if char_fixed else ""),
            flush=True,
        )
    # Unihan HV auditor + consistency (1+2) — không phụ thuộc whitelist dài
    try:
        from hv_auditor import audit_and_fix_plan
        audit_and_fix_plan(plan, fix=True)
    except Exception as e_hv:  # noqa: BLE001
        print(f"[hv-auditor] skip: {e_hv}", flush=True)
    return plan


def hard_term_lock_map(plan: dict | None) -> dict[str, str]:
    """zh_norm → vi bắt buộc — CHỈ type=lock (+ seed lock). Chengyu/idiom = mềm trong prompt."""
    out: dict[str, str] = {}
    if not isinstance(plan, dict):
        plan = {}
    mode = ""
    lock = plan.get("style_lock") if isinstance(plan.get("style_lock"), dict) else {}
    if isinstance(lock, dict):
        mode = str(lock.get("mode") or "").lower()
    soft_modern = mode == "modern" and not _is_mixed_genre(plan)
    if soft_modern:
        return out
    for t in plan.get("terms") or []:
        if not isinstance(t, dict):
            continue
        typ = str(t.get("type") or "").lower()
        if typ != "lock":
            continue
        zh, vi = (t.get("zh") or "").strip(), (t.get("vi") or "").strip()
        if not zh or not vi:
            continue
        key = _norm_zh_cue(zh)
        if "31.001" in vi or "31,001" in vi:
            continue
        out[key] = vi if vi[-1:] in ".,!?;:…" or vi.endswith(".") else vi
    # seed DEFAULT type=lock luôn thắng (máu / 逆天而行 / 过山)
    for seed in _DEFAULT_HARD_TERMS:
        if seed.get("type") == "lock":
            out[_norm_zh_cue(seed["zh"])] = seed["vi"]
    return out


def apply_hard_term_locks(rows: list[dict], plan: dict | None = None) -> int:
    """Post-pass: cue ZH khớp lock → ghi đè VI (chuẩn, không phụ thuộc LLM).

    Chỉ khóa cả câu (sau chuẩn hóa). Cụm nằm giữa câu dài → bỏ qua (tránh phá thoại).
    """
    locks = hard_term_lock_map(plan)
    if not locks:
        return 0
    n = 0
    for r in rows:
        if not isinstance(r, dict):
            continue
        if r.get("manual"):
            continue
        key = _norm_zh_cue(r.get("zh") or "")
        if not key or key not in locks:
            continue
        want = locks[key].strip()
        # khớp dấu câu nguồn nhẹ
        src = (r.get("zh") or "").strip()
        core = want.rstrip(".,!?;:…。，！？")
        if src.endswith(("，", ",")):
            want = core + ","
        elif src.endswith(("！", "!")):
            want = core + "!"
        elif src.endswith(("？", "?")):
            want = core + "?"
        elif src.endswith(("。", ".")) or not src[-1:].isalnum():
            want = core + "."
        else:
            want = core
        cur = (r.get("vi") or "").strip()
        if cur == want:
            continue
        r["vi"] = want
        n += 1
    if n:
        print(f"[lock] hard terms ép {n} câu", flush=True)
    return n


_TA_KEEP_RE = re.compile(
    r"\b(người|cậu|hắn|nó|nhà|bên|phe|chúng|ông|bà|cô|anh|chị|chú|bác|dì|lão|gã|mụ|thằng|ả)\s+ta\b",
    re.IGNORECASE,
)


def normalize_vi_thousands(text: str) -> str:
    """Dấu nghìn chuẩn Việt: 31 000 / 31,000 → 31.000.

    CUT phụ đề đã che dấu «.» trong số (subs._mask_number_dots); TTS gộp về 31000
    (clone_tts.vi_for_tts). Không đụng thập phân ngắn kiểu «3,5».
    """
    t = text or ""
    t = re.sub(r"(\d) {2,}(\d)", r"\1 \2", t)
    t = re.sub(
        r"\b\d{1,3}(?:[ ,]\d{3})+\b",
        lambda m: m.group(0).replace(" ", ".").replace(",", "."),
        t,
    )
    return t


def apply_style_polish(rows: list[dict], plan: dict | None = None) -> int:
    """Post-pass deterministic: sửa calque / văn mẫu thường gặp (mixed short-drama).

    An toàn: chỉ thay cụm VI cứng khi ZH có tín hiệu tương ứng; không đụng manual.
    """
    if not _is_mixed_genre(plan) and not (
        isinstance(plan, dict)
        and "dị năng" in str(plan.get("genre") or "").lower()
    ):
        # vẫn cho phép vài fix phổ biến nếu không clear genre
        pass
    n = 0
    # window zh để bắt setup Thủy trước 脑子进水
    zh_win: list[str] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        zh = (r.get("zh") or "").strip()
        vi = (r.get("vi") or "").strip()
        zh_win.append(zh)
        if len(zh_win) > 4:
            zh_win.pop(0)
        if r.get("manual") or not vi:
            continue
        new = vi
        ctx = "".join(zh_win)
        if "穷酸" in zh and "nghèo nàn" in new:
            new = new.replace("nghèo nàn", "thảm hại")
        if "打天下" in zh:
            new = new.replace("chinh phục thiên hạ", "đánh thiên hạ")
            new = new.replace("chinh phục thiên hạ", "đánh thiên hạ")
        if "好大力气" in zh and "rất nhiều công sức" in new:
            new = new.replace("Phải tốn rất nhiều công sức mới đến được đây",
                              "Khó khăn lắm mới đến được đây")
            new = new.replace("phải tốn rất nhiều công sức mới đến được đây",
                              "khó khăn lắm mới đến được đây")
            new = new.replace("tốn rất nhiều công sức", "khó khăn lắm")
        if "眼馋" in zh:
            if new.rstrip(".").endswith("thèm") and "thèm muốn" not in new:
                new = new.rstrip(".") + " muốn."
            new = new.replace("thật khiến người ta thèm.", "thật khiến người ta thèm muốn.")
            new = new.replace("khiến người ta thèm.", "khiến người ta thèm muốn.")
        if "脑子进水" in zh:
            water = any(x in ctx for x in ("水", "Thủy", "thủy", "圣斩", "盛产水"))
            if water and ("có vấn đề" in new or "điên" in new) and "úng" not in new:
                # giữ cấu trúc câu, thay punchline
                import re
                new2 = re.sub(
                    r"(Não|não)\s*(cậu|mày|em|anh)?\s*(có vấn đề rồi|điên rồi|điên à)",
                    r"não \2 úng nước rồi",
                    new,
                    count=1,
                )
                if new2 != new:
                    new = new2.replace("não  úng", "não úng").replace("não úng", "não úng")
                    # dọn khoảng trắng đôi / thiếu chủ ngữ
                    new = re.sub(r"\s{2,}", " ", new).strip()
                    if new.startswith("não "):
                        new = "Não" + new[3:]
                elif "Não cậu có vấn đề rồi" in new:
                    new = new.replace("Não cậu có vấn đề rồi", "Não cậu úng nước rồi")
                elif "não cậu có vấn đề rồi" in new:
                    new = new.replace("não cậu có vấn đề rồi", "não cậu úng nước rồi")
            # gỡ dư thừa «Đúng là làm não…»
            if "úng nước" in new and new.startswith("Đúng là làm "):
                new = new.replace("Đúng là làm ", "", 1)
                if new:
                    new = new[0].upper() + new[1:]
        # 嘲讽看 / 嘲讽 — tránh bịa dài; ưu tiên ngắn
        if _norm_zh_cue(zh) in ("嘲讽看", "嘲讽"):
            if len(new) > 28 or "khinh khỉnh" in new or "nhạo báng" in new.lower():
                new = "Khiêu khích."
        if "废什么话" in zh and "phí lời với" in new and "làm gì" not in new:
            new = new.replace("phí lời với", "phí lời với").rstrip(".")
            if not new.endswith("làm gì"):
                # «Công chúa, phí lời với thằng nhóc này làm gì»
                if "làm gì" not in new:
                    new = new.replace("phí lời với thằng nhóc này",
                                      "phí lời với thằng nhóc này làm gì")
        if "一股奇怪的力量" in zh and "luồng sức mạnh kỳ lạ" in new:
            new = new.replace("luồng sức mạnh kỳ lạ", "luồng lực kỳ lạ")
        # gọn câu mở đầu hay gặp
        if new.startswith("Tôi đã đến từ "):
            new = "Tôi đến từ " + new[len("Tôi đã đến từ "):]
        if "觉醒者" in zh and "Người thức tỉnh" in new:
            new = new.replace("Người thức tỉnh", "Giác Tỉnh Giả")
        if "觉醒者" in zh and "người thức tỉnh" in new:
            new = new.replace("người thức tỉnh", "Giác Tỉnh Giả")
        # Số máu hệ 亿 — sửa calque / ASR sót 亿
        import re
        # Soft-fix ASR 叶→亿 trên ZH (cùng câu đấm 八百亿)
        if "八百叶" in zh:
            r["zh"] = zh.replace("八百叶", "八百亿")
            zh = r["zh"]
        if re.search(r"三万一千一血|三万一千亿血", zh):
            # ép luôn: 31 000 tỷ (không 3 100 / 31.001)
            want = "Tổng cộng tôi có 31 000 tỷ máu"
            if zh.rstrip().endswith(("，", ",")):
                want += ","
            else:
                want += "."
            new = want
        # Lượng máu … 三万一千… (không chỉ câu «我一共»)
        if re.search(r"血量三万一千(?:一|亿)?", zh) and "百分之" not in zh:
            new = re.sub(
                r"(lượng máu[^=]{0,40}?)(?:là\s*)?(?:3[\s\.]100\s*tỷ|31[\s\.,]?001|31[\s\.,]?100)",
                r"\1là 31 000 tỷ",
                new,
                count=1,
                flags=re.I,
            )
            new = new.replace("3.100 tỷ máu", "31 000 tỷ máu").replace(
                "3.100 tỷ", "31 000 tỷ"
            ).replace("3 100 tỷ máu", "31 000 tỷ máu")
        if "3100亿" in zh or "三千一百亿" in zh:
            if re.search(r"hồi|máu", new, re.I) or "回血" in zh:
                # 3100亿 = 310 tỷ = 1% của 31 000
                new = re.sub(r"3[\s\.]100\s*tỷ", "310 tỷ", new)
                new = re.sub(
                    r"(?:hồi(?:\s*máu)?\s*)?(?:được\s*)?(?:31[\s\.,]?001|31[\s\.,]?00|3[\s\.]100)\s*(?:tỷ\s*)?máu",
                    "hồi 310 tỷ máu",
                    new,
                    count=1,
                    flags=re.I,
                )
                if "310 tỷ" not in new and "回血" in zh:
                    new = re.sub(
                        r"(Nhưng mỗi giây (?:tôi )?hồi(?: máu)?\s*)[^.，,]*",
                        r"\g<1>310 tỷ máu",
                        new,
                        count=1,
                        flags=re.I,
                    )
        if "八百亿" in zh or "八百叶" in zh:
            new = new.replace("tám trăm lá", "80 tỷ")
            new = new.replace("Tám trăm lá", "80 tỷ")
            new = new.replace("tám trăm tỷ", "80 tỷ")
            new = new.replace("Tám trăm tỷ", "80 tỷ")
            new = re.sub(r"(?:là\s*)?80 tỷ", "80 tỷ", new, count=1)
            if "这一拳" in zh or "一拳" in zh:
                if "80 tỷ" not in new:
                    new = re.sub(
                        r"Cú đấm[^.]*",
                        "Cú đấm 80 tỷ của tôi mà mẹ kiếp cậu vẫn chưa chết.",
                        new,
                        count=1,
                    )
        # Mash ASR: 血量三万一千一百分之十就是三千一百… = 31 000 → 10%=3 100; 1%=310
        if "血量三万一千" in zh and "百分之十" in zh:
            new = re.sub(
                r"(lượng máu[^=]{0,50}?)(?:là\s*)?(?:3[\s\.]100\s*tỷ|31[\s\.,]?0?01|31[\s\.,]?100|ba mươi mốt nghìn[^.，,]*)",
                r"\1là 31 000 tỷ",
                new,
                count=1,
                flags=re.I,
            )
            new = re.sub(
                r"(mười phần trăm là\s*)(?:310\s*tỷ|3[\s\.,]?110|3100|ba nghìn một trăm)(?!\s*tỷ)?",
                r"\g<1>3 100 tỷ",
                new,
                count=1,
                flags=re.I,
            )
            new = new.replace("31.001", "31 000 tỷ").replace("31.100", "31 000 tỷ")
            if "31 000 tỷ" not in new and "31.000 tỷ" not in new:
                new = re.sub(
                    r"(lượng máu[^=]{0,50}?là\s*)\d[\d\s\.,]*\s*tỷ?",
                    r"\g<1>31 000 tỷ",
                    new,
                    count=1,
                    flags=re.I,
                )
        # calque vạn tỷ (không đụng 31 000)
        new = new.replace("3,1 vạn tỷ", "31 000 tỷ")
        new = new.replace("3.1 vạn tỷ", "31 000 tỷ")
        new = new.replace("ba vạn tỷ", "3 000 tỷ")
        new = new.replace("Ba vạn tỷ", "3 000 tỷ")
        new = new.replace("Một đòn vạn tỷ", "Một đòn 1 000 tỷ")
        new = new.replace("31.000 tỷ", "31 000 tỷ").replace("3.000 tỷ", "3 000 tỷ")
        new = new.replace("3.100 tỷ", "3 100 tỷ").replace("1.000 tỷ", "1 000 tỷ")
        # Tên riêng hay dịch đen: 过山 → Quá Sơn (CẤM «qua núi»)
        if "过山" in zh:
            import re
            new = re.sub(r"(?i)\bqua núi\b", "Quá Sơn", new)
            if new.lower().startswith("quá sơn") and (not new[:1].isupper()):
                new = "Q" + new[1:] if new.lower().startswith("quá sơn") else new
                new = re.sub(r"(?i)^quá sơn", "Quá Sơn", new, count=1)
        # Mixed: ép xưng hô đời thường (CẤM Ta–Ngươi)
        # CẤM đụng «cậu ta»/«hắn ta» — \bta\b từng biến «cậu ta» → «cậu tôi».
        if _is_mixed_genre(plan):
            import re
            # «ông ta/cô ta/chúng ta…» = ngôi 3 / ngôi 1 gộp — đổi «ta»→«tôi» thành «ông tôi» (sai nghĩa).
            new = _TA_KEEP_RE.sub(lambda m: m.group(1) + "\0TA\0", new)
            new = re.sub(r"\bNgươi\b", "Cậu", new)
            new = re.sub(r"\bngươi\b", "cậu", new)
            new = re.sub(r"\bTa\b", "Tôi", new)
            new = re.sub(r"\bta\b", "tôi", new)
            new = new.replace("\0TA\0", " ta")
            # «cậu tôi» = lỗi (cậu ta→tôi). 他 → hắn.
            if "cậu tôi" in new.lower() or "hắn tôi" in new.lower():
                if re.search(r"他|把他|他的|他是|他有|他会|他能|他不|他呢", zh):
                    new = re.sub(r"\bCậu tôi\b", "Hắn", new)
                    new = re.sub(r"\bcậu tôi\b", "hắn", new)
                elif "她" in zh:
                    new = re.sub(r"\bCậu tôi\b", "Cô ấy", new)
                    new = re.sub(r"\bcậu tôi\b", "cô ấy", new)
                else:
                    new = re.sub(r"\bCậu tôi\b", "Cậu ấy", new)
                    new = re.sub(r"\bcậu tôi\b", "cậu ấy", new)
                new = re.sub(r"\bHắn tôi\b", "Hắn", new)
                new = re.sub(r"\bhắn tôi\b", "hắn", new)
            # 把他变成你的奴隶 — chỉ sửa «cậu tôi»→hắn; giữ «của con» nếu đúng bố→con
            if "奴隶" in zh and ("你的" in zh.replace(" ", "") or "变成" in zh):
                new = re.sub(r"(?i)biến\s+cậu tôi\s+thành", "biến hắn thành", new, count=1)
                new = re.sub(r"(?i)biến\s+cậu ấy\s+thành", "biến hắn thành", new, count=1)
            # HV ấn ký số Ả Rập → Thập Bát khi là 18 tầng
            new = new.replace("Ấn ký 18 tầng", "Thập Bát Tầng Ấn Ký")
            new = new.replace("Ấn ký Thập Bát Tầng", "Thập Bát Tầng Ấn Ký")
            new = new.replace("hành tinh thứ hai", "Tinh cầu hai sao")
            new = new.replace("hành tinh cấp một", "tinh cầu cấp một")
            # ASR/LLM hay bịa danh riêng từ 血缘性
            if "血缘" in zh:
                import re
                new = re.sub(
                    r"Huyết duyên Tân Tô Lý|Huyết duyên tính|huyết duyên Tân Tô Lý",
                    "huyết thống",
                    new,
                )
                if "hồ sơ lịch sử của huyết thống" in new.lower() or "huyết thống chúng" in new:
                    pass
                elif "血缘性的历史记录" in zh.replace(" ", ""):
                    new = "Trong hồ sơ lịch sử huyết thống của chúng tôi,"
            # 废什么话
            if "废什么话" in zh:
                new = new.replace("nói nhảm với", "phí lời với")
            # tránh «hai sao sao»
            new = new.replace("Tinh cầu hai sao sao", "Tinh cầu hai sao")
        new = normalize_vi_thousands(new)
        if new != vi:
            r["vi"] = new
            n += 1
    if n:
        print(f"[style] polish {n} câu (calque/văn mẫu)", flush=True)
    try:
        from script_lint import autofix_rows
        n += autofix_rows(rows, plan)["n"]
    except Exception as e:  # noqa: BLE001
        print(f"[lint] bỏ qua ({e})", flush=True)
    return n


def _is_modernish_genre(plan: dict | None) -> bool:
    """Chỉ đô thị THUẦN — không ép detox khi mixed (phim có thể sang tu tiên)."""
    if not isinstance(plan, dict):
        return False
    lock = plan.get("style_lock") if isinstance(plan.get("style_lock"), dict) else {}
    mode = str(lock.get("mode") or "").lower()
    if mode in ("mixed", "xianxia", "ancient"):
        return False
    if mode == "modern":
        return True
    if _is_mixed_genre(plan):
        return False
    blob = " ".join(
        str(plan.get(k) or "") for k in ("genre", "tone", "content_type", "pronoun_notes")
    ).lower()
    ancient = any(
        k in blob
        for k in ("tu tiên", "tu tien", "cổ trang", "wuxia", "xianxia", "tiên hiệp")
    )
    if ancient:
        return False
    return any(
        k in blob
        for k in (
            "đô thị", "do thi", "hiện đại", "hien dai",
            "học đường", "urban", "modern", "short drama", "short-drama",
        )
    )


def _char_aliases(plan: dict | None) -> dict[str, set[str]]:
    """vi_name_lower → {zh, vi, aliases…} để khớp tên trong câu."""
    out: dict[str, set[str]] = {}
    if not isinstance(plan, dict):
        return out
    for c in plan.get("characters") or []:
        if not isinstance(c, dict):
            continue
        vi = (c.get("vi") or "").strip()
        zh = (c.get("zh") or "").strip()
        if not vi and not zh:
            continue
        keys = {x for x in (vi, zh, *(c.get("aliases") or [])) if str(x).strip()}
        label = vi or zh
        out[label] = keys
    return out


def _pronoun_pairs(plan: dict | None) -> list[dict]:
    if not isinstance(plan, dict):
        return []
    out = []
    for pr in plan.get("pronouns") or []:
        if not isinstance(pr, dict):
            continue
        who = (pr.get("who") or "").strip()
        to = (pr.get("to") or "").strip()
        self_f = (pr.get("self") or "").strip()
        call = (pr.get("call") or "").strip()
        if who and (self_f or call):
            out.append({"who": who, "to": to, "self": self_f, "call": call})
    return out


def _detox_modern_pronouns(vi: str, zh: str) -> str:
    """Ép Ta/Ngươi → Tôi/Cậu cho thoại đô thị (giữ «ông ta/cô ta/chúng ta»)."""
    import re
    new = vi
    new = _TA_KEEP_RE.sub(lambda m: m.group(1) + "\0TA\0", new)
    new = re.sub(r"\bNgươi\b", "Cậu", new)
    new = re.sub(r"\bngươi\b", "cậu", new)
    new = re.sub(r"\bTa\b", "Tôi", new)
    new = re.sub(r"\bta\b", "tôi", new)
    new = new.replace("\0TA\0", " ta")
    # cậu tôi / hắn tôi
    if "cậu tôi" in new.lower() or "hắn tôi" in new.lower():
        if re.search(r"他|把他|他的|他是|他有|他会|他能|他不|他呢", zh):
            new = re.sub(r"\bCậu tôi\b", "Hắn", new)
            new = re.sub(r"\bcậu tôi\b", "hắn", new)
        elif "她" in zh:
            new = re.sub(r"\bCậu tôi\b", "Cô ấy", new)
            new = re.sub(r"\bcậu tôi\b", "cô ấy", new)
        else:
            new = re.sub(r"\bCậu tôi\b", "Cậu ấy", new)
            new = re.sub(r"\bcậu tôi\b", "cậu ấy", new)
        new = re.sub(r"\bHắn tôi\b", "Hắn", new)
        new = re.sub(r"\bhắn tôi\b", "hắn", new)
    return new


def apply_pronoun_postpass(rows: list[dict], plan: dict | None = None) -> int:
    """Post-pass deterministic xưng hô — không phụ thuộc LLM nhớ ma trận.

    1) Genre đô thị/mixed: tẩy Ta–Ngươi.
    2) Khi ZH có đủ tên who+to theo glossary.pronouns: ép self/call lệch rõ
       (vd call=cậu mà vi còn «ngươi»; self=tôi mà mở đầu «Ta …»).
    """
    import re
    n = 0
    modern = _is_modernish_genre(plan)
    pairs = _pronoun_pairs(plan)
    aliases = _char_aliases(plan)

    def _mentions(blob: str, name: str) -> bool:
        if not name:
            return False
        if name in blob:
            return True
        for keys in aliases.values():
            if name in keys or any(name == k for k in keys):
                return any(k and k in blob for k in keys)
        # fuzzy: name là vi label
        keys = aliases.get(name) or {name}
        return any(k and k in blob for k in keys)

    for r in rows:
        if not isinstance(r, dict) or r.get("manual"):
            continue
        zh = (r.get("zh") or "").strip()
        vi = (r.get("vi") or "").strip()
        if not vi:
            continue
        new = vi
        if modern:
            new = _detox_modern_pronouns(new, zh)
        # Pair rules khi cả who và to xuất hiện trong ZH (hoặc VI)
        blob = zh + "\n" + new
        for pr in pairs:
            who, to = pr["who"], pr["to"]
            if not _mentions(blob, who):
                continue
            if to and to not in ("*", "chung", "narrator") and not _mentions(blob, to):
                # vẫn áp self nếu who nói (tên who trong ZH)
                if not _mentions(zh, who):
                    continue
            self_f, call = pr["self"], pr["call"]
            if modern or _is_modernish_genre(plan):
                if call and call.lower() in ("cậu", "mày", "anh", "em", "chị", "bạn"):
                    if re.search(r"\b[Nn]gươi\b", new):
                        new = re.sub(r"\bNgươi\b", call[:1].upper() + call[1:], new)
                        new = re.sub(r"\bngươi\b", call, new)
                if self_f and self_f.lower() in ("tôi", "tao", "mình", "anh", "em"):
                    # Chỉ sửa «Ta » đầu câu / sau dấu — tránh ông ta
                    if re.search(r"(?:^|[.!?…]\s*)Ta\b", new) and self_f.lower() == "tôi":
                        new = re.sub(r"(^|[.!?…]\s*)Ta\b", r"\1Tôi", new)
                    if re.search(r"(?:^|[.!?…]\s*)\bta\b", new) and self_f.lower() == "tôi":
                        new = re.sub(r"(^|[.!?…]\s*)\bta\b", r"\1tôi", new)
        if new != vi:
            r["vi"] = new
            r["pr"] = 1
            n += 1
    if n:
        print(f"[pronoun] post-pass sửa {n} câu (genre/ma trận)", flush=True)
    return n


def _salvage_items(text: str) -> dict:
    """Vớt từng object {\"i\":.., \"vi\":..} kể cả khi JSON TỔNG THỂ hỏng (model
    chèn ký tự lạ, thiếu dấu phẩy, xuống dòng trong chuỗi, bị cắt cụt...). Quét
    tuần tự bằng raw_decode: gặp object hợp lệ thì lấy, gặp rác thì nhích 1 ký tự.
    Nhờ vậy 1 chỗ hỏng không làm mất toàn bộ câu trong lô."""
    dec = json.JSONDecoder()
    out: dict = {}
    i, n = 0, len(text)
    while i < n:
        b = text.find("{", i)
        if b == -1:
            break
        try:
            obj, end = dec.raw_decode(text, b)
            i = end
            if isinstance(obj, dict) and "i" in obj and ("vi" in obj or "text" in obj):
                try:
                    out[int(obj["i"])] = (obj.get("vi") or obj.get("text") or "").strip()
                except (ValueError, TypeError):
                    pass
        except json.JSONDecodeError:
            i = b + 1
    return out


def translate_oneshot(
    rows: list[dict],
    plan_block: str,
    target: str = "Tiếng Việt",
    model: str | None = None,
    plan: dict | None = None,
) -> dict:
    """Dịch TOÀN BỘ danh sách câu trong 1 lần gọi LLM (llama-server ctx lớn).

    Prompt gọn + cấm chữ Hán; phù hợp OpenAI-compatible local (:8083).
    Trả {i: vi}. Caller nên fallback batch nếu rỗng/thiếu nhiều.
    """
    n = len(rows)
    if not n:
        return {}
    lines = "\n".join(
        f'{r["i"]}|{round(float(r.get("end", 0) or 0) - float(r.get("start", 0) or 0), 1)}|{_compress_zh_for_llm(r["text"])}'
        for r in rows
    )
    sys = (
        f"Bạn là biên dịch phụ đề lồng tiếng Trung→{target} "
        "(short drama / manhua hóa: huyền ảo · hành động · đô thị dị năng).\n"
        "QUY TẮC BẮT BUỘC:\n"
        "1) CHỈ trả JSON hợp lệ, không markdown, không giải thích, không thinking.\n"
        "2) Dịch ĐỦ đúng số câu, giữ nguyên id i.\n"
        f"3) Bản dịch VIỆT THUẦN — CẤM để lại chữ Hán trong 'vi'.\n"
        "4) Xưng hô/thuật ngữ nhất quán theo phương án (cứng Hán Việt đúng chỗ).\n"
        "5) Độ dài khớp 'sec' (~4–5 tiếng/giây), ngắn gọn như thoại phim.\n"
        f"6) Schema: {{\"items\":[{{\"i\":...,\"vi\":\"...\"}}, ...]}} — đúng {n} phần tử.\n"
        + _translate_rules(plan)
    )
    user = (
        f"{plan_block}\n\n"
        f"Dịch TOÀN BỘ {n} dòng sau (định dạng: i|sec|zh).\n"
        f"Các dòng là thoại LIỀN MẠCH — đọc cả đoạn rồi dịch từng câu, giữ đá xoáy/đáp lời.\n"
        f"Trả JSON đúng {n} items.\n\n"
        f"{lines}"
    )
    max_tok = min(24000, max(2048, n * 60))
    # Oneshot dài: cho timeout lớn hơn lô thường
    timeout = min(900, 120 + n * 3)
    out = chat(
        [{"role": "system", "content": sys}, {"role": "user", "content": user}],
        model=model or _tmodel(),
        temperature=0.2,
        json_mode=True,
        max_tokens=max_tok,
        timeout=timeout,
        retries=2,
    )
    res: dict = {}
    try:
        data = parse_json(out)
        items = data.get("items", data if isinstance(data, list) else [])
        res = {
            int(it["i"]): (it.get("vi") or "").strip()
            for it in items
            if isinstance(it, dict) and "i" in it
        }
    except Exception:  # noqa: BLE001
        pass
    if not res:
        res = _salvage_items(out or "")
    if not res:
        raise ValueError(f"oneshot: không parse được (out_len={len(out or '')})")
    return res


def translate_batch(rows: list[dict], plan_block: str, prev_ctx: list[dict],
                    target: str = "Tiếng Việt", model: str | None = None,
                    plan: dict | None = None) -> dict:
    """LƯỢT 1 — DỊCH NGHĨA KỊCH BẢN CHUẨN XÁC (Semantic Accuracy) theo Phân Cảnh (Scene) + Series Glossary. Trả {i: vi}."""
    scene_ctx = _resolve_scene_context(plan, rows)
    try:
        from pronoun_consistency import lock_banner, ledger_from_prev
        lock_ctx = lock_banner(plan)
        ledger_ctx = ledger_from_prev(prev_ctx)
    except Exception:
        lock_ctx, ledger_ctx = "", ""
    sys = (
        f"Bạn là BIÊN DỊCH KỊCH BẢN PHIM {target} CHUYÊN NGHIỆP (LƯỢT 1: CHUẨN XÁC NGỮ CẢNH & NGHĨA THOẠI).\n"
        "MỤC TIÊU DUY NHẤT: Dịch ĐÚNG NGHĨA kịch bản, ĐÚNG NHÂN VẬT ĐANG NÓI theo Phân cảnh, ĐÚNG VAI VẾ XƯNG HÔ.\n"
        "1. BÁM SÁT [NGỮ CẢNH PHÂN CẢNH HIỆN TẠI]: Nắm chắc bối cảnh, tình huống mâu thuẫn, ai đang nói với ai (kẻ thù đối đầu, sư đồ, đồng đội hay hệ thống).\n"
        "2. TUYỆT ĐỐI KHÔNG DỊCH ĐEN / TỪ ĐIỂN THÔ: Thoát ý các câu thành ngữ, tiếng lóng, hàm ý mỉa mai của tiếng Trung (vd: 吃醋 -> ghen; 打天下 -> dựng nghiệp; 脑子进水 -> não úng nước/có vấn đề).\n"
        "3. ĐẠI TỪ XƯNG HÔ NHẤT QUÁN: Bám chắc ma trận who→to. Cùng một cặp phải giữ đúng self/call đã chốt. CẤM nhảy anh–em ↔ ông–tôi / cậu–tôi trong cùng đoạn. CẤM Ta/Ngươi nếu đô thị/mixed; CẤM đảo ('Đến lượt ngươi' ≠ 'Đến lượt ta').\n"
        "4. THUẬT NGỮ CỨNG & SỐ LƯỢNG: Giữ đúng tên nhân vật, chiêu thức Hán Việt oai phong, giữ đúng số 万/亿/兆 (vạn = 10 000, ức = 100 triệu).\n"
        "5. Giữ nguyên chỉ số i, ĐỦ SỐ CÂU, không bỏ dòng. Câu cực ngắn (ừ, được rồi) vẫn dịch ĐÚNG câu đó.\n"
        + _translate_rules(plan)
        + "\nCHỈ trả JSON."
    )
    ctx = ""
    if prev_ctx:
        ctx = "NGỮ CẢNH liền trước (KHÔNG dịch lại, chỉ để giữ mạch thoại):\n" + "\n".join(
            f"  {c.get('zh','')} -> {c.get('vi','')}" for c in prev_ctx
        ) + "\n\n"
    if ledger_ctx:
        ctx = ledger_ctx + ctx
    if lock_ctx:
        ctx = lock_ctx + "\n" + ctx
    payload = []
    for r in rows:
        item = {
            "i": r["i"],
            "sec": round((r.get("end", 0) - r.get("start", 0)), 1),
            "zh": _compress_zh_for_llm(r["text"]),
        }
        mt_hint = (r.get("mt_vi") or "").strip()
        if mt_hint:
            item["mt_vi"] = mt_hint[:240]
        payload.append(item)
    mt_note = ""
    if any(p.get("mt_vi") for p in payload):
        mt_note = (
            "Một số câu có 'mt_vi' = bản NMT (HachimiMT). Ưu tiên giữ nhịp/ý NMT; "
            "CHỈ sửa khi lệch tên characters, danh hiệu lock, hoặc sai nghĩa rõ. "
            "CẤM dịch nghĩa danh hiệu (vd 逆天而行 = tên đã chốt).\n"
        )
    user = (
        f"{plan_block}\n{scene_ctx}{ctx}"
        "Dịch các câu sau (khớp 'sec' giây/câu). "
        "Đây là đoạn thoại LIỀN — câu sau có thể đá/đáp câu trước; dịch đúng ý, không dịch đen. "
        f"{mt_note}"
        "Trả JSON: {\"items\":[{\"i\":<int>,\"vi\":\"<bản dịch>\"}]}\n\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )
    # Local: 50 câu JSON ~6–8k token. Trần 4096 cắt giữa lô; 16384 + ctx 128k thì timeout.
    m = model or _tmodel()
    max_tok = 8192 if is_local(m) else 16384
    out = chat(
        [{"role": "system", "content": sys}, {"role": "user", "content": user}],
        model=m, temperature=0.3, json_mode=True, max_tokens=max_tok,
    )
    # 1) parse chuẩn; 2) JSON hỏng -> VỚT từng câu; 3) rỗng hẳn -> raise (để splitter chia nhỏ)
    res = {}
    try:
        data = parse_json(out)
        items = data.get("items", data if isinstance(data, list) else [])
        res = {int(it["i"]): (it.get("vi") or "").strip()
               for it in items if isinstance(it, dict) and "i" in it}
    except Exception:  # noqa: BLE001
        pass
    if not res:
        res = _salvage_items(out)
    if not res:
        raise ValueError(f"không parse/vớt được câu nào (len output={len(out)})")

    # Phát hiện và chống lỗi LLM nuốt/bỏ sót câu trong lô:
    if len(rows) > 1:
        missing_keys = [r["i"] for r in rows if r["i"] not in res or not (res.get(r["i"]) or "").strip()]
        if missing_keys and (len(missing_keys) >= 2 or len(missing_keys) / len(rows) > 0.15):
            raise ValueError(f"LLM bỏ sót {len(missing_keys)}/{len(rows)} câu (vd i={missing_keys[:3]}) -> chia nhỏ lô để dịch đủ 100%")

    return res


def _translate_safe(rows: list[dict], plan_block: str, prev_ctx: list[dict],
                    target: str, model: str | None,
                    plan: dict | None = None) -> dict:
    """Dịch 1 lô CÓ CHỐNG LỖI: nếu parse hỏng hoặc LLM nuốt câu, CHIA ĐÔI lô rồi thử lại.
    Xuống tới 1 câu vẫn lỗi thì thử cứu bằng model fallback trước khi chấp nhận để trống."""
    try:
        return translate_batch(rows, plan_block, prev_ctx, target=target, model=model, plan=plan)
    except LLMUnavailable:
        raise
    except Exception as e:  # noqa: BLE001
        if len(rows) <= 1:
            i = rows[0]["i"] if rows else "?"
            print(f"[trans] câu i={i} lỗi: {str(e)[:80]}, thử cứu bằng fallback...", flush=True)
            try:
                fb_model = _cfg_get("FALLBACK_MODEL") or _rmodel() or _tmodel()
                if fb_model and fb_model != model:
                    return translate_batch(rows, plan_block, prev_ctx, target=target, model=fb_model, plan=plan)
            except Exception:
                pass
            print(f"[trans] câu i={i} để trống sau khi thử cứu: {str(e)[:80]}", flush=True)
            return {}
        mid = len(rows) // 2
        print(f"[trans] lô {len(rows)} câu parse lỗi/thiếu ({str(e)[:50]}) -> chia đôi thử lại", flush=True)
        a = _translate_safe(rows[:mid], plan_block, prev_ctx, target, model, plan)
        b = _translate_safe(rows[mid:], plan_block, prev_ctx, target, model, plan)
        return {**a, **b}


def _style_voice_banner(plan: dict | None) -> str:
    """Gợi ý văn phong linh hoạt — KHÔNG khóa modern↔cổ (phim có thể đổi cảnh)."""
    try:
        if not isinstance(plan, dict):
            return ""
        lock = plan.get("style_lock") if isinstance(plan.get("style_lock"), dict) else {}
        mode = str(lock.get("mode") or "").lower()
        if mode == "unknown":
            mode = ""
        genre = str(plan.get("genre") or "")
        tone = str(plan.get("tone") or "")
        if not (mode or genre or tone):
            return ""
        lines = [
            "=== RÀ NMT TỐI THIỂU ===",
            "NMT là bản chính — GIỮ khi đã đúng nghĩa/tên; đừng polish đồng nghĩa.",
            "Phim có thể đô thị ↔ tu tiên: không ép một thanh ngữ cả phim.",
            "Chỉ vá: tên/lock sai, nghĩa ngược ZH, Hán thô, quá dài TTS.",
        ]
        if mode or genre or tone:
            lines.append(f"gợi ý plan: mode={mode or '?'} | genre={genre} | tone={tone}")
        return "\n".join(lines) + "\n"
    except Exception:  # noqa: BLE001
        return ""


def _style_exemplars(plan: dict | None, rows_pool: list[dict] | None, limit: int = 5) -> str:
    """3–5 câu mẫu giữ giọng (ưu tiên có tên NV glossary)."""
    try:
        if not rows_pool:
            return ""
        names = []
        if isinstance(plan, dict):
            for c in plan.get("characters") or []:
                if not isinstance(c, dict):
                    continue
                vi_n = str(c.get("vi") or "").strip()
                if len(vi_n) >= 2:
                    names.append(vi_n)
        named: list[str] = []
        head: list[str] = []
        for idx, r in enumerate(rows_pool):
            if not isinstance(r, dict):
                continue
            zh = str(r.get("zh") or "").strip()
            vi = str(r.get("vi") or "").strip()
            if not zh or not vi or len(vi) < 4:
                continue
            line = f"  ZH: {zh[:80]}\n  VI: {vi[:100]}"
            if names and any(n and n in vi for n in names[:12]):
                if line not in named:
                    named.append(line)
            elif idx < 12 and line not in head:
                head.append(line)
            if len(named) >= limit:
                break
        picked = (named + head)[:limit]
        if not picked:
            return ""
        return "MẪU THOẠI GIỮ GIỌNG (bám cùng văn phong khi sửa):\n" + "\n".join(picked) + "\n\n"
    except Exception:  # noqa: BLE001
        return ""


def review_batch(rows: list[dict], plan_block: str, prev_ctx: list[dict],
                 target: str = "Tiếng Việt", model: str | None = None,
                 plan: dict | None = None,
                 exemplars_pool: list[dict] | None = None) -> dict:
    """LƯỢT 2 — BẢN ĐỊA HÓA LỜI THOẠI LỒNG TIẾNG & KHỚP NHỊP PHỤ ĐỀ (Voice Dubbing Localization).
    Đối chiếu zh với vi_nhap và Phân cảnh, CHỈ trả câu cần sửa. Bắt lỗi ngược đại từ, từ Hán-Nôm thô, lệch nhịp."""
    scene_ctx = _resolve_scene_context(plan, rows)
    try:
        from pronoun_consistency import lock_banner, ledger_from_prev, review_lock_rules
        lock_ctx = lock_banner(plan)
        ledger_ctx = ledger_from_prev(prev_ctx)
        rule3 = review_lock_rules(plan)
    except Exception:
        lock_ctx, ledger_ctx, rule3 = "", "", (
            "3. SỬA LỖI NGƯỢC ĐẠI TỪ: bám phân cảnh; CẤM đảo ngôi.\n"
        )
    try:
        voice = _style_voice_banner(plan)
        exemplars = _style_exemplars(plan, exemplars_pool or prev_ctx or rows, limit=5)
    except Exception:  # noqa: BLE001
        voice, exemplars = "", ""
    sys = (
        f"Bạn là biên tập viên TỐI THIỂU cho phụ đề {target} (LƯỢT 2: chỉ vá lỗi NMT).\n"
        f"{voice}"
        "vi_nhap = bản DỊCH CHÍNH từ NMT. MẶC ĐỊNH: GIỮ NGUYÊN — không viết lại.\n"
        "CHỈ trả câu trong fixes KHI có ÍT NHẤT một lỗi cứng sau:\n"
        "  (A) Sai/thiếu tên nhân vật so với bảng characters / type=lock.\n"
        "  (B) Sai nghĩa RÕ so với ZH (đảo ngôi trong cùng câu, hiểu ngược idiom).\n"
        "  (C) Còn chữ Hán / Hán-Nôm thô cứng (tiến vào→vào; uống giấm→ghen; ba vạn→30 000).\n"
        "  (D) Quá dài so với 'sec' (~5 âm tiết/giây) khiến TTS dí hơi — chỉ RÚT, giữ ý NMT.\n"
        "CẤM tuyệt đối:\n"
        "  - Đổi từ đồng nghĩa / 'hay hơn' (vd Lão tử→Tôi, chúng ta→bọn tôi) khi NMT đã đúng.\n"
        "  - Viết lại cả câu chỉ vì văn phong.\n"
        "  - Ép modern↔cổ khi NMT đã khớp ngữ cảnh.\n"
        + rule3
        + "YẾU TỐ CỨNG giữ: tên NV, type=lock, chiêu thức.\n"
        "Câu NMT đã ổn → KHÔNG đưa vào fixes (thiếu sót còn hơn sửa thừa).\n"
        + _translate_rules(plan)
        + "\nCHỈ trả JSON."
    )
    ctx = ""
    if exemplars:
        ctx = exemplars
    if prev_ctx:
        ctx += "NGỮ CẢNH liền trước (bản đã chốt, giữ mạch):\n" + "\n".join(
            f"  {c.get('zh','')} -> {c.get('vi','')}" for c in prev_ctx
        ) + "\n\n"
    if ledger_ctx:
        ctx = ledger_ctx + ctx
    if lock_ctx:
        ctx = lock_ctx + "\n" + ctx
    payload = [
        {"i": r["i"], "sec": round((r.get("end", 0) - r.get("start", 0)), 1),
         "zh": r.get("zh", ""), "vi_nhap": r.get("vi", "")}
        for r in rows
    ]
    user = (
        f"{plan_block}\n{scene_ctx}{ctx}"
        "Dưới đây là NMT chính. CHỈ trả fixes cho câu LỖI CỨNG (A–D). "
        "Nếu NMT đã ổn (vd thoại miệng tự nhiên như «Lão tử…») → BỎ QUA, đừng đổi sang tôi/bọn tôi. "
        "Trả JSON: {\"fixes\":[{\"i\":<int>,\"vi\":\"<bản sửa>\"}]} — fixes=[] nếu không cần sửa.\n\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )
    out = chat(
        [{"role": "system", "content": sys}, {"role": "user", "content": user}],
        model=model or _tmodel(), temperature=0.1, json_mode=True,
        # chỉ trả câu cần sửa → output ngắn; 4096 đủ cho ~30 câu sửa
        max_tokens=4096,
    )
    try:
        data = parse_json(out)
        fixes = data.get("fixes", data if isinstance(data, list) else [])
        raw = {int(f["i"]): (f.get("vi") or "").strip()
               for f in fixes if isinstance(f, dict) and "i" in f and (f.get("vi") or "").strip()}
    except Exception:  # noqa: BLE001
        raw = _salvage_items(out)     # JSON hỏng -> vớt; rỗng = không câu nào cần sửa
    raw = _filter_cosmetic_nmt_fixes(raw, rows, plan)
    try:
        from pronoun_consistency import filter_review_fixes_for_lock
        return filter_review_fixes_for_lock(raw, rows, plan)
    except Exception:
        return raw


def _filter_cosmetic_nmt_fixes(
    fixes: dict[int, str],
    rows: list[dict],
    plan: dict | None,
) -> dict[int, str]:
    """Chỉ giữ A/C/D cứng; mặc định GIỮ NMT (bỏ polish GPT)."""
    if not fixes:
        return fixes
    import re
    from difflib import SequenceMatcher

    by_i = {int(r["i"]): r for r in rows if isinstance(r, dict) and "i" in r}
    names: list[str] = []
    if isinstance(plan, dict):
        for c in plan.get("characters") or []:
            if isinstance(c, dict) and str(c.get("vi") or "").strip():
                names.append(str(c.get("vi")).strip())
        for t in plan.get("terms") or []:
            if isinstance(t, dict) and str(t.get("type") or "").lower() == "lock":
                vi = str(t.get("vi") or "").strip()
                if vi:
                    names.append(vi)

    def _has_cjk(s: str) -> bool:
        return bool(re.search("[\u4e00-\u9fff]", s or ""))

    def _toks(s: str) -> set[str]:
        return {t for t in re.findall(r"[A-Za-zÀ-ỹà-ỹ0-9]+", (s or "").lower()) if len(t) >= 2}

    # Xưng hô miệng NMT — GPT đổi sang tôi/chúng ta = cosmetic
    _colloq = (
        "lão tử", "lao tu", "bản tôn", "ban ton", "tiểu đệ", "tieu de",
        "ta ", " lão ", "bản vương", "ban vuong",
    )
    _formal = (
        "tôi ", "tôi,", "tôi.", "chúng ta", "chung ta", "bọn tôi", "bon toi",
        "mình ", "minh ",
    )

    out: dict[int, str] = {}
    dropped = 0
    for i, vi_fix in fixes.items():
        r = by_i.get(i) or {}
        nhap = (r.get("vi") or "").strip()
        fix = (vi_fix or "").strip()
        if not nhap or not fix or fix == nhap:
            if fix == nhap:
                dropped += 1
            continue

        # (C) còn chữ Hán trong NMT, fix đã sạch
        if _has_cjk(nhap) and not _has_cjk(fix):
            out[i] = fix
            continue

        # (A) chèn tên lock thiếu
        if any(n and len(n) >= 2 and n in fix and n not in nhap for n in names[:40]):
            out[i] = fix
            continue

        n_l, f_l = nhap.lower(), fix.lower()
        # đổi xưng hô miệng → tôi/chúng ta: luôn bỏ
        if any(c in n_l for c in _colloq) and any(f in f_l for f in _formal):
            dropped += 1
            continue

        # (D) TTS: chỉ giữ khi NMT vượt nhiều nhịp VÀ fix là rút ngắn (overlap cao), không viết lại
        try:
            sec = float(r.get("end", 0) or 0) - float(r.get("start", 0) or 0)
        except (TypeError, ValueError):
            sec = 0.0
        budget = max(12, int(sec * 5 * 1.3)) if sec > 0 else 9999
        over = len(nhap) > budget + 20 and len(nhap) > int(budget * 1.6)
        a, b = _toks(nhap), _toks(fix)
        overlap = (len(a & b) / max(1, min(len(a), len(b)))) if a and b else 0.0
        ratio = SequenceMatcher(None, n_l, f_l).ratio()
        shortened = len(fix) <= int(len(nhap) * 0.75)
        # chỉ chấp nhận RÚT (từ mới ≤15%), không viết lại đồng nghĩa
        new_ratio = (len(b - a) / max(1, len(b))) if b else 1.0
        if over and shortened and overlap >= 0.65 and new_ratio <= 0.15 and ratio >= 0.45:
            out[i] = fix
            continue

        dropped += 1
    if dropped:
        print(f"[review] bỏ {dropped} fix cosmetic (giữ NMT)", flush=True)
    return out



def run_review(
    work_dir: str | Path,
    batch: int = 40,
    target: str = "Tiếng Việt",
    model: str | None = None,
    force: bool = False,
) -> dict:
    """LƯỢT 2: soát bản dịch nháp (script.json) bằng model chính xác (minimax) rồi
    vá tại chỗ. Lô lớn hơn dịch (output chỉ là câu cần sửa). Checkpoint từng lô,
    resume phần chưa soát (cờ 'rv'). Cập nhật tiến độ 'review' vào manifest."""
    work_dir = Path(work_dir)
    m = Manifest(work_dir)
    script_path = work_dir / "script.json"
    if not script_path.exists():
        raise RuntimeError("Chưa có bản dịch nháp (script.json) để soát.")
    rows = json.loads(script_path.read_text(encoding="utf-8"))
    plan_path = work_dir / "glossary.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8")) if plan_path.exists() else {}
    plan = ensure_hard_terms(plan)
    if plan_path.exists() or plan.get("terms"):
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    plan_block = _plan_block(plan)

    # 0. BẢO ĐẢM 100% CÂU CÓ BẢN DỊCH: Tự động phát hiện và dịch lấp đầy các câu còn trống trước khi rà soát
    missing_indices = [idx for idx, r in enumerate(rows) if not (r.get("vi") or "").strip()]
    if missing_indices:
        print(f"[review] ⚠️ Phát hiện {len(missing_indices)} câu trống chưa có bản dịch! Tự động dịch vá ngay trước khi rà soát...", flush=True)
        k_miss = 0
        while k_miss < len(missing_indices):
            if (work_dir / ".stop").exists():
                raise RuntimeError("stopped by user")
            chunk_indices = [missing_indices[k_miss]]
            k_miss += 1
            while k_miss < len(missing_indices) and len(chunk_indices) < 20:
                chunk_indices.append(missing_indices[k_miss])
                k_miss += 1
            chunk_payload = []
            for p_idx in chunk_indices:
                r_item = rows[p_idx]
                chunk_payload.append({
                    "i": r_item.get("i", p_idx),
                    "start": r_item.get("start", 0),
                    "end": r_item.get("end", 0),
                    "text": r_item.get("zh") or r_item.get("text") or "",
                })
            p0 = chunk_indices[0]
            prev_ctx_fill = [
                {"zh": rows[j].get("zh", ""), "vi": rows[j].get("vi", "")}
                for j in range(max(0, p0 - CTX_LINES), p0)
                if rows[j].get("vi")
            ]
            fill_map = _translate_safe(chunk_payload, plan_block, prev_ctx_fill, target=target, model=model or _tmodel(), plan=plan)
            for p_idx, s_item in zip(chunk_indices, chunk_payload):
                vi_val = (fill_map.get(s_item["i"]) or "").strip()
                if _has_cjk(vi_val):
                    vi_val = _salvage_mixed_vi(vi_val, zh=s_item.get("text") or "", plan=plan)
                if vi_val and not _has_cjk(vi_val):
                    rows[p_idx]["vi"] = normalize_vi_thousands(vi_val)
                    rows[p_idx].pop("rv", None)  # câu mới dịch cần được soát
            atomic_write_json(script_path, rows, fsync=False)
            print(f"  [review-fill] ...đã vá {min(k_miss, len(missing_indices))}/{len(missing_indices)} câu", flush=True)

        # Cứu từng câu đơn nếu còn sót
        still_miss = [idx for idx, r in enumerate(rows) if not (r.get("vi") or "").strip()]
        for idx in still_miss:
            r_single = rows[idx]
            single_payload = [{
                "i": r_single.get("i", idx),
                "start": r_single.get("start", 0),
                "end": r_single.get("end", 0),
                "text": r_single.get("zh") or r_single.get("text") or "",
            }]
            single_map = _translate_safe(single_payload, plan_block, [], target=target, model=model or _tmodel(), plan=plan)
            if single_map.get(r_single.get("i", idx)):
                rows[idx]["vi"] = normalize_vi_thousands(single_map[r_single.get("i", idx)])
                rows[idx].pop("rv", None)
        atomic_write_json(script_path, rows, fsync=False)

    rmodel = model or _rmodel()          # lượt rà văn phong: mặc định gemma3:12b
    pos_by_i = {r["i"]: idx for idx, r in enumerate(rows)}
    total = len(rows)
    todo = [r for r in rows if force or not r.get("rv")]
    n_done = total - len(todo)
    print(f"[review] Model={rmodel} | soát {len(todo)}/{total} câu, lô {batch}.", flush=True)

    # Chuyển đổi model preset AI local (Lượt 2: Rà soát chuẩn xác) nếu rmodel là local
    # Nếu rmodel là 31B (9router) thì KHÔNG nạp 26B trước để tiết kiệm trọn vẹn VRAM
    auto_switch = (_cfg_get("AUTO_SWITCH_PRESETS", "1") or "1").strip() in ("1", "true", "yes")
    if auto_switch and todo and _is_llama_local_model(rmodel):
        try:
            import preset_switcher
            target_preset = _cfg_get("REVIEW_PRESET", "qwen36-turbo")
            if target_preset:
                preset_switcher.switch_preset(target_preset, max_wait_sec=180)
        except Exception as e_ps:
            print(f"[preset_switcher] Cảnh báo switch preset lượt 2: {e_ps}", flush=True)

    m.mark_running(STAGE)
    if is_local(rmodel):
        free_gpu_vram("trước soát")
    try:
        for k in range(0, len(todo), batch):
            chunk = todo[k : k + batch]
            pos = pos_by_i.get(chunk[0]["i"], 0)
            prev_ctx = [rows[j] for j in range(max(0, pos - CTX_LINES), pos) if rows[j].get("vi")]
            fixes = {}
            try:
                fixes = review_batch(
                    chunk, plan_block, prev_ctx, target=target, model=rmodel, plan=plan,
                    exemplars_pool=rows,
                )
            except Exception as e:
                err_str = str(e).lower()
                is_out_of_tokens_or_quota = (
                    any(w in err_str for w in ("429", "token", "quota", "exhausted", "rate limit", "exceeded", "timeout", "unavailable", "500", "502", "503"))
                    or isinstance(e, LLMUnavailable)
                    or "requests" in type(e).__module__
                )
                if is_out_of_tokens_or_quota and not _is_llama_local_model(rmodel):
                    local_rev = _cfg_get("REVIEW_PRESET", "qwen36-turbo")
                    print(f"\n[review] ⚠️ Model 31B (9router) gặp sự cố / hết tokens / quota: {e}", flush=True)
                    print(f"[review] 🚀 KÍCH HOẠT DỰ PHÒNG: Tự động nạp Local REVIEW ({local_rev}) trên llama-server :8083...", flush=True)
                    try:
                        import preset_switcher
                        preset_switcher.switch_preset(local_rev, max_wait_sec=180)
                        rmodel = f"llama/{local_rev}"
                        print(f"[review] ✅ Đã mở xong {local_rev}. Tiếp tục soát bằng Local!", flush=True)
                        fixes = review_batch(
                            chunk, plan_block, prev_ctx, target=target, model=rmodel, plan=plan,
                            exemplars_pool=rows,
                        )
                    except Exception as e_fallback:
                        print(f"[review] ❌ Lỗi khi chuyển sang fallback local ({local_rev}): {e_fallback}", flush=True)
                        fixes = {}
                elif isinstance(e, LLMUnavailable):
                    raise
                else:
                    print(f"[review] Lô {k // batch} lỗi, bỏ qua tạm: {e}")
                    fixes = {}
            for r in chunk:
                if fixes.get(r["i"]):
                    r["vi"] = normalize_vi_thousands(fixes[r["i"]])
                r["rv"] = 1                      # đã soát (để resume)
            n_done += len(chunk)
            atomic_write_json(script_path, rows)
            print(f"  ...soát {min(k + batch, len(todo))}/{len(todo)} (sửa {len(fixes)} câu)", flush=True)
            st = m.data["stages"].get("translate", {})
            st.update({
                "status": "running", "review": True,
                "review_progress": round(n_done / total * 100, 1) if total else 100,
                "review_done": n_done, "review_total": total,
                "review_model": rmodel, "updated_at": time.time(),
            })
            m.data["stages"]["translate"] = st
            m.save()

        apply_hard_term_locks(rows, plan)
        apply_style_polish(rows, plan)
        try:
            from pronoun_consistency import run_post_translate_consistency
            run_post_translate_consistency(work_dir, rows, plan, fix_with_gpt=True)
        except Exception as e_pc:  # noqa: BLE001
            print(f"[pronoun-qa] {e_pc}", flush=True)
            apply_pronoun_postpass(rows, plan)
        from subs import to_srt, split_bilingual_rows, sub_split_cfg
        max_zh, max_vi, max_dur = sub_split_cfg()
        n_before = len(rows)
        # Giữ script.json = bản 1–1 với ASR (không đánh lại i). Chỉ tách khi xuất SRT.
        display = split_bilingual_rows(
            [dict(r) for r in rows], max_zh=max_zh, max_vi=max_vi, max_dur=max_dur
        )
        if len(display) != n_before:
            print(f"[review] Tách câu dài (chỉ SRT): {n_before} -> {len(display)} dòng", flush=True)
            (work_dir / "script.display.json").write_text(
                json.dumps(display, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        atomic_write_json(script_path, rows)
        n_missing = sum(1 for r in rows if not (r.get("vi") or "").strip())
        if n_missing:
            print(f"[review] ⚠️ CẢNH BÁO: Còn {n_missing} câu trống sau khi rà soát!", flush=True)
        else:
            print(f"[review] ✅ Đã soát đủ 100% ({len(rows)} câu, missing=0)", flush=True)
        try:
            import series_glossary
            series_glossary.save_from(work_dir, reason="hoàn thành rà soát")
        except Exception:
            pass
    except Exception as e:  # noqa: BLE001
        m.mark_failed(STAGE, e)
        raise

    prev = m.stage(STAGE) or {}
    result = m.mark_done(
        STAGE, script_path=str(script_path), glossary_path=str(plan_path),
        n_segments=len(rows), n_missing=n_missing,
        model=prev.get("model", _tmodel() or "default"),
        reviewed=True, review_model=rmodel,
    )
    unload_local(rmodel)          # nhả VRAM cho bước TTS
    print(f"[ok] Soát xong -> {script_path}")
    return result


def count_script_missing(work_dir: str | Path) -> int:
    """Đếm câu trống trong script.json (nguồn sự thật cho UI / auto-vá)."""
    sp = Path(work_dir) / "script.json"
    if not sp.exists():
        return -1
    try:
        rows = json.loads(sp.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return -1
    return sum(1 for r in rows if isinstance(r, dict) and not (r.get("vi") or "").strip())


def translate_coverage_gap(work_dir: str | Path) -> int:
    """Số câu ASR chưa có trong script (salvage lúc Dừng hay ghi thiếu).

    Trước đây salvage chỉ ghi các câu đã dịch → script 398 dòng đủ VI trong khi
    ASR 2698 → count_script_missing=0 → auto nhảy TTS dở. Gap > 0 = chưa xong dịch.
    Cho phép script ngắn hơn ASR một chút (heal số gãy ~vài %).
    """
    work_dir = Path(work_dir)
    asr_p, sp = work_dir / "asr.json", work_dir / "script.json"
    if not asr_p.exists():
        return -1
    if not sp.exists():
        try:
            return len(json.loads(asr_p.read_text(encoding="utf-8")))
        except Exception:  # noqa: BLE001
            return -1
    try:
        asr = json.loads(asr_p.read_text(encoding="utf-8"))
        rows = json.loads(sp.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return -1
    if not isinstance(asr, list) or not asr:
        return 0
    if not isinstance(rows, list):
        return len(asr)
    asr_n, script_n = len(asr), len(rows)
    if script_n <= 0:
        return asr_n
    gap = asr_n - script_n
    if gap <= 0:
        return 0
    # heal số/gộp: script có thể ngắn hơn ASR vài % — dưới 90% = salvage dừng giữa chừng
    if script_n < asr_n * 0.90:
        return gap
    return 0


def translate_ready_for_tts(work_dir: str | Path) -> tuple[bool, str]:
    """True chỉ khi dịch đủ coverage ASR + không còn VI trống."""
    miss = count_script_missing(work_dir)
    if miss < 0:
        return False, "chưa có script.json"
    if miss > 0:
        return False, f"còn {miss} câu VI trống"
    gap = translate_coverage_gap(work_dir)
    if gap < 0:
        return False, "không đọc được asr/script"
    if gap > 0:
        return False, f"script thiếu ~{gap} câu so với ASR (dịch dừng giữa chừng)"
    return True, "ok"


def _trivial_vi(zh: str) -> str | None:
    """Câu chỉ cười/thán từ — không cần LLM (model hay trả lại chữ Hán → _has_cjk xoá)."""
    import re
    raw = (zh or "").strip()
    if not raw:
        return "…"
    t = clean_zh_spam(raw)
    if not t or re.fullmatch(r"[\s。．，、！？!?,.…]+\Z", t):
        return "…"
    n_ha_raw = sum(raw.count(c) for c in "哈呵嘿嘻")
    # Cười spam dài (ASR hay dính hàng trăm 哈) — cắt gọn, có thể kèm vài chữ trước
    if n_ha_raw >= 8:
        core = re.sub(r"[哈呵嘿嘻呃嗯]+", "", t)
        core = re.sub(r"[\s。．，、！？!?,.…]+\Z", "", core).strip()
        laugh = "Haha" if n_ha_raw <= 12 else "Hahaha"
        if not core:
            return laugh
        if len(core) <= 24 and not re.search(r"[A-Za-z]", core):
            if "还是没做到" in core or core.endswith("没做到"):
                return f"Vẫn chưa làm được. {laugh}"
            if "没做到" in core:
                return f"Chưa làm được. {laugh}"
            return f"{laugh}"
        return None
    # toàn cười / thở / ừ (đã rút spam → chuỗi ngắn)
    if re.fullmatch(r"[哈呵嘿嘻哼啊哦噢嗯呃唉哎。．，、！？!?,.…\s]+\Z", t):
        if any(c in t for c in "哈呵嘿嘻"):
            n = min(8, max(2, sum(t.count(c) for c in "哈呵嘿嘻")))
            return ("Ha" if n <= 2 else "Haha" if n <= 4 else "Hahaha")
        if "哼" in t:
            return "Hử."
        if any(c in t for c in "啊哦噢"):
            return "À."
        if any(c in t for c in "嗯呃"):
            return "Ừ."
        if any(c in t for c in "唉哎"):
            return "Ối."
        return "…"
    return None


def _compress_zh_for_llm(zh: str) -> str:
    """Rút chuỗi cười/spam trước khi gửi LLM (tránh timeout / trả Hán)."""
    return clean_zh_spam(zh, max_rep=6, max_len=120)


def clean_zh_spam(zh: str, max_rep: int = 3, max_len: int = 0) -> str:
    """Rút 哈/呃/嗯/啊 spam + cụm chữ lặp (区域的区域的…) từ ASR.

    Xử cả ``哈哈哈哈…`` và ``啊，啊，啊，…`` (cách nhau dấu phẩy).
    Không đụng dấu ``，`` cuối câu thoại bình thường.
    """
    import re
    t = (zh or "").strip()
    if not t:
        return t
    # ký tự lặp liên tiếp → giữ tối đa max_rep
    t = re.sub(
        r"([哈呵嘿嘻呃嗯啊哦噢哼])\1{" + str(max_rep) + r",}",
        lambda m: m.group(1) * max_rep,
        t,
    )
    # cụm cười/ư cực dài (dù không cùng 1 char liên tục theo pattern trên vẫn cắt)
    t = re.sub(r"[哈呵嘿嘻]{8,}", "哈哈哈", t)
    t = re.sub(r"[呃嗯]{6,}", "呃", t)
    t = re.sub(r"[啊哦噢]{5,}", "啊", t)
    # ``啊，啊，啊，…`` / ``哈，哈，哈…`` (ASR Nano hay tách bằng dấu phẩy)
    t = re.sub(r"(?:啊[，,\s]*){4,}", "啊", t)
    t = re.sub(r"(?:[哈呵嘿嘻][，,\s]*){4,}", "哈哈哈", t)
    t = re.sub(r"(?:[呃嗯][，,\s]*){4,}", "呃", t)
    # Cụm 2–12 chữ lặp (vd «区域的»×N, «你们»×N) → giữ tối đa 2 lần
    prev = None
    while prev != t:
        prev = t
        t = re.sub(r"(.{2,12}?)\1{2,}", lambda m: m.group(1) * 2, t)
    # chỉ gỡ dấu phẩy mồ côi sau khi rút spam (vd ``，啊`` còn sót), không cắt ``，`` cuối câu
    t = re.sub(r"^[，,\s]+", "", t)
    t = re.sub(r"\s{2,}", " ", t).strip()
    if max_len and len(t) > max_len:
        t = t[: max_len - 1] + "…"
    return t


def run_translate(
    work_dir: str | Path,
    batch: int = 20,           # lô nhỏ: model nhớ glossary/tên riêng tốt hơn (tránh dịch đen)
    target: str = "Tiếng Việt",
    force: bool = False,
    model: str | None = None,
    mode: str | None = None,   # oneshot | batch | auto (None -> TRANSLATE_MODE / auto)
    auto_review: bool | None = None,
) -> dict:
    work_dir = Path(work_dir)
    m = Manifest(work_dir)
    # Cho ép cỡ lô qua env/config (model yếu: 15–25; máy mạnh có thể 40).
    try:
        batch = int(_cfg_get("TRANSLATE_BATCH", str(batch)) or batch)
    except Exception:
        batch = int(os.getenv("TRANSLATE_BATCH") or batch)
    except ValueError:
        pass
    use_model = model or _tmodel()
    # 3060 12GB + ctx 8k: 40–60 câu/lô ổn. 100 câu + ctx 128k mới timeout.
    if is_local(use_model) and batch > 60:
        print(f"[trans] Ollama: lô {batch} > 60 (dễ timeout) -> hạ còn 50")
        batch = 50

    asr_path = work_dir / "asr.json"
    if not asr_path.exists():
        raise RuntimeError("Chưa có asr.json. Chạy asr.py trước.")
    segments = json.loads(asr_path.read_text(encoding="utf-8"))

    if not force:
        st = m.stage(STAGE) or {}
        script_existing = work_dir / "script.json"
        sp = Path(st.get("script_path") or script_existing)
        if sp.exists():
            try:
                rows0 = json.loads(sp.read_text(encoding="utf-8"))
                n_miss = sum(1 for r in rows0 if not (r.get("vi") or "").strip())
            except Exception:  # noqa: BLE001
                n_miss = int(st.get("n_missing") or 0)
            gap = translate_coverage_gap(work_dir)
            if n_miss <= 0 and gap <= 0:
                if not m.is_done(STAGE):
                    m.mark_done(
                        STAGE,
                        script_path=str(sp),
                        glossary_path=st.get("glossary_path"),
                        n_segments=len(rows0) if isinstance(rows0, list) else (st.get("n_segments") or 0),
                        n_missing=0,
                        model=st.get("model"),
                        mode=st.get("mode"),
                    )
                    st = m.stage(STAGE) or {}
                print(f"[skip] Đã dịch xong: {st.get('script_path') or sp}")
                return st
            # Còn câu trống HOẶC script ngắn hơn ASR (salvage lúc Dừng) → không skip
            if gap > 0:
                print(
                    f"[fill] script thiếu ~{gap} câu so với ASR → dịch tiếp (không skip)",
                    flush=True,
                )
            elif n_miss > 0:
                print(f"[fill] còn {n_miss} câu trống → dịch vá (không skip)", flush=True)

    m.mark_running(STAGE)

    # Chuyển đổi model preset AI local (Lượt 1: Dịch nhanh) và chờ AI mở sẵn sàng 100%
    auto_switch = (_cfg_get("AUTO_SWITCH_PRESETS", "1") or "1").strip() in ("1", "true", "yes")
    if auto_switch:
        try:
            import preset_switcher
            target_preset = _cfg_get("TRANSLATE_PRESET", "gemma4-12b-qat-mtp-fast")
            if target_preset:
                preset_switcher.switch_preset(target_preset, max_wait_sec=180)
        except Exception as e_ps:
            print(f"[preset_switcher] Cảnh báo switch preset lượt 1: {e_ps}", flush=True)

    if is_local(model or _tmodel()):
        free_gpu_vram("trước dịch")
    done: dict[int, dict] = {}
    script_path = work_dir / "script.json"
    plan_path = work_dir / "glossary.json"
    if force:
        # Xoá bản cũ ngay để UI/resume không đọc nhầm file cũ
        for p in (script_path, work_dir / "sub.vi.srt"):
            try:
                if p.exists():
                    p.unlink()
            except OSError:
                pass
        st0 = m.data.setdefault("stages", {}).setdefault(STAGE, {})
        st0.update({
            "progress": 0, "n_done": 0, "n_total": len(segments),
            "n_missing": len(segments), "cur_text": "force: dịch lại từ đầu…",
            "updated_at": time.time(),
        })
        m.data["stages"][STAGE] = st0
        m.save()
        print(f"[force] xoá script cũ · dịch lại {len(segments)} câu", flush=True)
    try:
        # --- PLAN: hồ sơ nhân vật + xưng hô (cache / Context Studio) ---
        ctx_pack_path = work_dir / "context_pack.json"
        skip_plan = False
        if ctx_pack_path.exists():
            try:
                skip_plan = bool(
                    json.loads(ctx_pack_path.read_text(encoding="utf-8")).get("skip_plan")
                )
            except Exception:  # noqa: BLE001
                skip_plan = False

        if plan_path.exists() and (not force or skip_plan):
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            if skip_plan:
                print("[plan] context_pack.skip_plan → giữ glossary Context Studio "
                      "(không gọi build_plan).")
                # đảm bảo style_lock lexicon nếu pack cũ thiếu
                try:
                    from context_studio.schema import apply_style_lock_from_genre
                    plan = apply_style_lock_from_genre(plan)
                except Exception:  # noqa: BLE001
                    pass
            else:
                print("[plan] Dùng lại glossary.json có sẵn.")
        else:
            print("[plan] Lập hồ sơ nhân vật + xưng hô + phân cảnh (Scene-based)...")
            try:
                hints = _ocr_name_hints(work_dir)
                if hints:
                    print(f"[plan] {len(hints)} gợi ý tên từ OCR.")
                series_plan = None
                try:
                    import series_glossary
                    s_key = series_glossary.series_key(work_dir)
                    series_plan = series_glossary.load(s_key)
                    if series_plan:
                        print(f"[series_memory] Kế thừa bộ nhớ series «{s_key}»: {len(series_plan.get('characters', []))} nhân vật, {len(series_plan.get('terms', []))} thuật ngữ", flush=True)
                except Exception as e_sm:
                    print(f"[series_memory] Chưa tải được bộ nhớ series: {e_sm}", flush=True)

                plan = build_plan(
                    segments,
                    target=target,
                    model=model,
                    name_hints=hints or None,
                    series_plan=series_plan,
                    work_dir=work_dir,
                )
                plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"[plan] {len(plan.get('characters', []))} nhân vật, {len(plan.get('terms', []))} thuật ngữ, "
                      f"{len(plan.get('scenes', []))} phân cảnh, {len(plan.get('pronouns', []))} quy tắc xưng hô.")
            except Exception as e:  # noqa: BLE001
                # Lập hồ sơ lỗi KHÔNG được làm sập cả bước dịch: dịch tiếp không có
                # bảng nhân vật (kém nhất quán hơn, nhưng vẫn ra bản dịch). Chạy lại
                # sau để có hồ sơ đầy đủ.
                print(f"[plan] LỖI lập hồ sơ ({e}) -> dịch KHÔNG có bảng nhân vật.")
                plan = {"content_type": "", "genre": "", "tone": "",
                        "characters": [], "terms": [], "pronouns": [], "scenes": [], "pronoun_notes": ""}
        try:
            import series_glossary
            plan = series_glossary.apply(work_dir, plan)
            # Tự động gộp vào kho bộ nhớ Series chung
            series_glossary.save_from(work_dir, reason="cập nhật plan tập mới")
        except Exception as e:  # noqa: BLE001
            print(f"[plan] không nạp/lưu được bảng bộ: {e}", flush=True)
        plan = ensure_hard_terms(plan)
        # A) Analyze full ZH → lock ma trận xưng hô (GPT/Aurora, quét theo lô + memory)
        try:
            from pronoun_consistency import ensure_analyze_before_translate
            plan, _pa = ensure_analyze_before_translate(
                work_dir, plan, segments=segments, force=False,
            )
            if not _pa.get("skipped"):
                print(
                    f"[plan] pronoun-analyze: pronouns={_pa.get('n_pronouns')} "
                    f"locked={_pa.get('locked')} model={_pa.get('model')}",
                    flush=True,
                )
        except Exception as e_pa:  # noqa: BLE001
            print(f"[plan] pronoun-analyze bỏ qua: {e_pa}", flush=True)
        plan = ensure_hard_terms(plan)
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        # style_lock.json mirror nếu có
        try:
            sl = plan.get("style_lock")
            if isinstance(sl, dict):
                (work_dir / "style_lock.json").write_text(
                    json.dumps(sl, ensure_ascii=False, indent=2), encoding="utf-8"
                )
        except Exception:  # noqa: BLE001
            pass
        plan_block = _plan_block(plan)

        # --- Dịch tuần tự (để có ngữ cảnh liền trước), resume phần thiếu ---
        # QUAN TRỌNG: sau split_bilingual_rows, script có nhiều dòng hơn ASR và i bị
        # đánh lại 0..N — KHÔNG được map done[i] theo ASR (sẽ lệch cặp ZH–VI).
        script_rows_existing: list[dict] = []
        post_split = False
        if script_path.exists() and not force:
            script_rows_existing = read_json_checkpoint(script_path, default=[])
            if isinstance(script_rows_existing, list) and script_rows_existing:
                post_split = (
                    len(script_rows_existing) > len(segments) + 5
                    or any(isinstance(r, dict) and r.get("src_i") is not None
                           for r in script_rows_existing)
                )
                if post_split:
                    print(
                        f"[resume] script post-split ({len(script_rows_existing)} dòng "
                        f"> ASR {len(segments)}) → chỉ vá câu trống tại chỗ, không remap ASR.",
                        flush=True,
                    )
                    rows = [r for r in script_rows_existing if isinstance(r, dict)]
                    miss_idx = [i for i, r in enumerate(rows) if not (r.get("vi") or "").strip()]
                    if miss_idx:
                        print(f"[fill] vá {len(miss_idx)} câu trống trên script đã cắt", flush=True)
                        # dịch theo cụm index liên tiếp
                        k = 0
                        while k < len(miss_idx):
                            if (work_dir / ".stop").exists():
                                print(f"[trans] {work_dir.name}: nhận .stop → dừng vá tại chỗ", flush=True)
                                raise RuntimeError("stopped by user")
                            chunk_pos = [miss_idx[k]]
                            k += 1
                            while k < len(miss_idx) and miss_idx[k] == chunk_pos[-1] + 1 and len(chunk_pos) < min(batch, 25):
                                chunk_pos.append(miss_idx[k])
                                k += 1
                            chunk = []
                            for pos in chunk_pos:
                                r = rows[pos]
                                chunk.append({
                                    "i": r.get("i", pos),
                                    "start": r.get("start", 0),
                                    "end": r.get("end", 0),
                                    "text": r.get("zh") or r.get("text") or "",
                                })
                            prev_ctx = []
                            p0 = chunk_pos[0]
                            for j in range(max(0, p0 - CTX_LINES), p0):
                                if rows[j].get("vi"):
                                    prev_ctx.append({
                                        "zh": rows[j].get("zh", ""),
                                        "vi": rows[j].get("vi", ""),
                                    })
                            vi_map = _translate_safe(chunk, plan_block, prev_ctx, target, model, plan)
                            for pos, s in zip(chunk_pos, chunk):
                                vi = (vi_map.get(s["i"]) or "").strip()
                                if _has_cjk(vi):
                                    vi = _salvage_mixed_vi(
                                        vi, zh=s.get("text") or "", plan=plan
                                    )
                                if vi and not _has_cjk(vi):
                                    rows[pos]["vi"] = normalize_vi_thousands(vi)
                            atomic_write_json(script_path, rows, fsync=False)
                            print(f"  ...vá {min(k, len(miss_idx))}/{len(miss_idx)}", flush=True)
                    apply_hard_term_locks(rows, plan)
                    apply_style_polish(rows, plan)
                    apply_pronoun_postpass(rows, plan)
                    from subs import to_srt
                    atomic_write_json(script_path, rows)
                    (work_dir / "sub.vi.srt").write_text(to_srt(rows, key="vi"), encoding="utf-8")
                    n_missing = sum(1 for r in rows if not (r.get("vi") or "").strip())
                    unload_local(use_model)
                    result = m.mark_done(
                        STAGE, script_path=str(script_path), glossary_path=str(plan_path),
                        n_segments=len(rows), n_missing=n_missing,
                        model=use_model or "default", mode="fill-inplace",
                    )
                    print(f"[ok] Vá tại chỗ xong -> {script_path}  (còn {n_missing} trống)", flush=True)
                    return result
                else:
                    for r in script_rows_existing:
                        if isinstance(r, dict) and r.get("vi"):
                            done[r["i"]] = r
                    if done:
                        print(f"[resume] Đã có {len(done)} câu dịch trước đó.")

        # Prefill cười/thán từ (tránh LLM trả Hán → bị xoá → kẹt forever)
        n_triv = 0
        for s in segments:
            if s["i"] in done and done[s["i"]].get("vi"):
                continue
            zh0 = s.get("text") or ""
            zh = clean_zh_spam(zh0) or zh0
            tv = _trivial_vi(zh0)
            if tv:
                done[s["i"]] = {
                    "i": s["i"], "start": s["start"], "end": s["end"],
                    "zh": zh, "vi": tv,
                }
                n_triv += 1
        if n_triv:
            print(f"[fill] prefill {n_triv} câu cười/thán từ", flush=True)

        todo = [s for s in segments if not done.get(s["i"], {}).get("vi")]
        # NMT = DỊCH CHÍNH (mặc định). LLM chỉ vá sót + run_review rà soát.
        # Auto model: modern/mixed → base 60-zh-vi; xianxia/cổ → QT
        try:
            import mt_zh_vi
            if mt_zh_vi.enabled() and todo:
                mid = mt_zh_vi.resolve_model_id(plan)
                flavor = "QT" if "qt" in mid.lower() else "base"
                primary = mt_zh_vi.primary_mode()
                print(
                    f"[mt-zh-vi] {'PRIMARY' if primary else 'hint'} "
                    f"{len(todo)} câu · {flavor} · {mid}",
                    flush=True,
                )
                drafts = mt_zh_vi.draft_rows(
                    [{"i": s["i"], "text": s.get("text") or ""} for s in todo],
                    plan=plan,
                )
                if primary:
                    n_mt = 0
                    for s in todo:
                        vi = (drafts.get(s["i"]) or "").strip()
                        if not vi or _has_cjk(vi):
                            continue
                        zh = clean_zh_spam(s.get("text") or "") or (s.get("text") or "")
                        done[s["i"]] = {
                            "i": s["i"], "start": s["start"], "end": s["end"],
                            "zh": zh, "vi": normalize_vi_thousands(vi), "mt": 1,
                        }
                        n_mt += 1
                    # khóa cứng ngay trên bản NMT (tên/danh hiệu type=lock)
                    try:
                        apply_hard_term_locks(list(done.values()), plan)
                    except Exception as e_lock:  # noqa: BLE001
                        print(f"[mt-zh-vi] hard-lock skip: {e_lock}", flush=True)
                    todo = [s for s in segments if not done.get(s["i"], {}).get("vi")]
                    print(
                        f"[mt-zh-vi] NMT chính {n_mt} câu · còn {len(todo)} câu "
                        f"LLM vá (CJK/trống) · review sau = {_rmodel()}",
                        flush=True,
                    )
                else:
                    for s in todo:
                        if s["i"] in drafts:
                            s["mt_vi"] = drafts[s["i"]]
                    print(f"[mt-zh-vi] gắn hint {len(drafts)} câu → LLM dịch", flush=True)
        except Exception as e_mt:  # noqa: BLE001
            print(f"[mt-zh-vi] bỏ qua: {e_mt}", flush=True)

        # Vá câu trống: luôn batch (oneshot hay sót/CJK với gemma)
        if mode is None and todo and len(todo) <= 80:
            mode = "batch"
        tmode = _resolve_translate_mode(mode, use_model, len(todo))
        print(
            f"[trans] Model={use_model or 'mặc định'} | mode={tmode} | "
            f"cần dịch {len(todo)}/{len(segments)} câu"
            + (f", lô {batch}" if tmode == "batch" else ""),
            flush=True,
        )

        def _apply_map(vi_map: dict, chunk: list[dict]) -> None:
            for s in chunk:
                vi = (vi_map.get(s["i"], "") or "").strip()
                if _has_cjk(vi):
                    # Cứu «100% 增幅» thay vì xoá → tránh kẹt missing forever
                    vi = _salvage_mixed_vi(vi, zh=s.get("text") or "", plan=plan)
                if vi and _has_cjk(vi):
                    vi = ""
                if vi:
                    vi = normalize_vi_thousands(vi)
                zh0 = s.get("text") or ""
                done[s["i"]] = {
                    "i": s["i"], "start": s["start"], "end": s["end"],
                    "zh": clean_zh_spam(zh0) or zh0, "vi": vi,
                }

        def _checkpoint() -> None:
            ordered = [done[s["i"]] for s in segments if s["i"] in done]
            atomic_write_json(script_path, ordered, fsync=False)
            st = m.data["stages"].get("translate", {})
            st.update({"status": "running", "progress": round(len(done) / len(segments) * 100, 1),
                       "n_done": len(done), "n_total": len(segments), "updated_at": time.time(),
                       "mode": tmode})
            m.data["stages"]["translate"] = st
            m.save()

        if todo and tmode == "oneshot":
            try:
                vi_map = translate_oneshot(todo, plan_block, target=target, model=model, plan=plan)
                _apply_map(vi_map, todo)
                _checkpoint()
                n_ok = sum(1 for s in todo if done.get(s["i"], {}).get("vi"))
                print(f"  ...oneshot xong {n_ok}/{len(todo)} câu có vi", flush=True)
                # còn trống (CJK/sót) -> vá bằng batch nhỏ
                miss = [s for s in todo if not done.get(s["i"], {}).get("vi")]
                if miss:
                    print(f"[trans] oneshot còn {len(miss)} câu trống/CJK -> vá batch", flush=True)
                    for k in range(0, len(miss), min(batch, 40)):
                        chunk = miss[k : k + min(batch, 40)]
                        first_i = chunk[0]["i"]
                        pos = next((idx for idx, s in enumerate(segments) if s["i"] == first_i), 0)
                        prev_ctx = [done[segments[j]["i"]] for j in range(max(0, pos - CTX_LINES), pos)
                                    if segments[j]["i"] in done]
                        vi_map = _translate_safe(chunk, plan_block, prev_ctx, target, model, plan)
                        _apply_map(vi_map, chunk)
                        _checkpoint()
                        print(f"  ...vá {min(k + len(chunk), len(miss))}/{len(miss)}", flush=True)
            except LLMUnavailable:
                raise
            except Exception as e:  # noqa: BLE001
                print(f"[trans] oneshot lỗi ({e}) -> fallback batch", flush=True)
                tmode = "batch"

        if todo and tmode == "batch":
            # chỉ dịch câu còn trống (oneshot fail giữa chừng vẫn resume)
            todo = [s for s in segments if not done.get(s["i"], {}).get("vi")]
            for k in range(0, len(todo), batch):
                if (work_dir / ".stop").exists():
                    print(f"[trans] {work_dir.name}: nhận .stop → dừng dịch theo yêu cầu", flush=True)
                    raise RuntimeError("stopped by user")
                chunk = todo[k : k + batch]
                # ngữ cảnh: CTX_LINES câu ngay trước câu đầu của lô (theo thứ tự phim)
                first_i = chunk[0]["i"]
                pos = next((idx for idx, s in enumerate(segments) if s["i"] == first_i), 0)
                prev_ctx = [done[segments[j]["i"]] for j in range(max(0, pos - CTX_LINES), pos)
                            if segments[j]["i"] in done]
                vi_map = _translate_safe(chunk, plan_block, prev_ctx, target, model, plan)
                _apply_map(vi_map, chunk)
                _checkpoint()
                print(f"  ...dịch {min(k + batch, len(todo))}/{len(todo)}")

        # --- KIỂM TRA MISSING: đếm thật + tự vá vài vòng (oneshot/batch hay sót) ---
        fill_rounds = max(0, int(os.getenv("TRANSLATE_FILL_ROUNDS") or "3"))
        fill_batch = min(25, max(8, int(batch) if batch else 25))
        for round_i in range(fill_rounds + 1):  # vòng 0 = chỉ kiểm tra; 1..N = vá
            # bảo đảm mọi câu ASR đều có slot trong done
            for s in segments:
                zh0 = s.get("text") or ""
                zh = clean_zh_spam(zh0) or zh0
                if s["i"] not in done:
                    done[s["i"]] = {
                        "i": s["i"], "start": s["start"], "end": s["end"],
                        "zh": zh, "vi": "",
                    }
                else:
                    # giữ vi đã có; rút spam ZH nếu chưa sửa tay
                    cur = done[s["i"]]
                    if not cur.get("manual") and (cur.get("zh") or "") != zh:
                        cur["zh"] = zh
                if not (done[s["i"]].get("vi") or "").strip():
                    tv = _trivial_vi(zh0)
                    if tv:
                        done[s["i"]]["vi"] = tv
                        done[s["i"]]["zh"] = zh

            miss = [s for s in segments if not (done.get(s["i"], {}).get("vi") or "").strip()]
            n_missing = len(miss)
            ordered = [done[s["i"]] for s in segments]
            atomic_write_json(script_path, ordered)
            st = m.data.setdefault("stages", {}).setdefault(STAGE, {})
            st.update({
                "status": "running",
                "n_missing": n_missing,
                "n_done": len(segments) - n_missing,
                "n_total": len(segments),
                "progress": round((len(segments) - n_missing) / max(1, len(segments)) * 100, 1),
                "cur_text": (
                    f"kiểm tra missing: đủ {len(segments)} câu"
                    if n_missing <= 0
                    else f"kiểm tra missing: thiếu {n_missing} — vá vòng {min(round_i, fill_rounds)}/{fill_rounds}"
                ),
                "updated_at": time.time(),
            })
            m.data["stages"][STAGE] = st
            m.save()
            print(
                f"[check] missing={n_missing}/{len(segments)}"
                + (f" → vá batch (vòng {round_i}/{fill_rounds})" if n_missing and round_i < fill_rounds else ""),
                flush=True,
            )
            if n_missing <= 0 or round_i >= fill_rounds:
                break
            # Vá lô nhỏ
            for k in range(0, len(miss), fill_batch):
                if (work_dir / ".stop").exists():
                    print(f"[trans] {work_dir.name}: nhận .stop → dừng vá missing", flush=True)
                    raise RuntimeError("stopped by user")
                chunk = miss[k : k + fill_batch]
                first_i = chunk[0]["i"]
                pos = next((idx for idx, s in enumerate(segments) if s["i"] == first_i), 0)
                prev_ctx = [
                    done[segments[j]["i"]]
                    for j in range(max(0, pos - CTX_LINES), pos)
                    if segments[j]["i"] in done and done[segments[j]["i"]].get("vi")
                ]
                vi_map = _translate_safe(chunk, plan_block, prev_ctx, target, model, plan)
                _apply_map(vi_map, chunk)
                _checkpoint()
                print(f"  ...vá missing {min(k + len(chunk), len(miss))}/{len(miss)}", flush=True)

        n_missing = sum(1 for s in segments if not (done.get(s["i"], {}).get("vi") or "").strip())
        from subs import to_srt, split_bilingual_rows, sub_split_cfg
        ordered = [done[s["i"]] for s in segments]
        apply_hard_term_locks(ordered, plan)
        apply_style_polish(ordered, plan)
        try:
            from pronoun_consistency import run_post_translate_consistency
            run_post_translate_consistency(work_dir, ordered, plan, fix_with_gpt=True)
        except Exception as e_pc:  # noqa: BLE001
            print(f"[pronoun-qa] {e_pc}", flush=True)
            apply_pronoun_postpass(ordered, plan)
        from subs import heal_script_broken_numbers
        ordered, n_num_heal = heal_script_broken_numbers(ordered)
        if n_num_heal:
            print(f"[trans] gộp {n_num_heal} cặp số gãy (vd 31, + 000亿)", flush=True)
        # script: sau heal số có thể ít hơn ASR vài câu (đúng — số gãy đã gộp)
        atomic_write_json(script_path, ordered)
        # CUT → display + SRT (LUÔN chạy, kể cả còn thiếu vài câu — trước đây
        # n_missing>0 bỏ qua → dịch xong nhìn như không tách).
        max_zh, max_vi, max_dur = sub_split_cfg()
        display = split_bilingual_rows(
            [dict(r) for r in ordered], max_zh=max_zh, max_vi=max_vi, max_dur=max_dur
        )
        if len(display) != len(ordered):
            print(f"[trans] Tách câu dài (display): {len(ordered)} -> {len(display)}", flush=True)
        else:
            print(f"[trans] CUT display: {len(display)} dòng (không đổi số)", flush=True)
        (work_dir / "script.display.json").write_text(
            json.dumps(display, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        (work_dir / "sub.vi.srt").write_text(to_srt(display, key="vi"), encoding="utf-8")
        if n_missing:
            print(f"[trans] WARN còn {n_missing} câu trống — vẫn đã CUT phần có vi", flush=True)
    except Exception as e:  # noqa: BLE001
        # Giữ script.json — ghi ĐỦ khung ASR (câu chưa dịch vi="") để
        # count_script_missing / coverage_gap không bị 0 giả → auto nhảy TTS.
        try:
            script_path = work_dir / "script.json"
            if done or segments:
                ordered = []
                for s in segments:
                    hit = done.get(s["i"]) if done else None
                    if hit and (hit.get("vi") or "").strip():
                        ordered.append(hit)
                    else:
                        zh = (s.get("text") or s.get("zh") or "").strip()
                        ordered.append({
                            "i": s.get("i"),
                            "start": s.get("start", 0),
                            "end": s.get("end", 0),
                            "zh": zh,
                            "text": zh,
                            "vi": ((hit or {}).get("vi") or "").strip(),
                            "rv": False,
                        })
                atomic_write_json(script_path, ordered)
            st = m.data.setdefault("stages", {}).setdefault(STAGE, {})
            n = sum(1 for s in segments if done and s["i"] in done and (done[s["i"]].get("vi") or "").strip())
            tot = len(segments)
            n_miss = sum(1 for s in segments if not (done.get(s["i"], {}).get("vi") or "").strip()) if done else tot
            st.update({
                "status": "pending",
                "progress": round(n / tot * 100, 1) if tot else 0,
                "n_done": n, "n_total": tot, "n_missing": n_miss,
                "script_path": str(script_path) if script_path.exists() else None,
                "cur_text": f"đã lưu {n}/{tot} · thiếu {n_miss} — bấm Tiếp tục",
                "last_error": str(e)[:200],
                "updated_at": time.time(),
            })
            m.data["stages"][STAGE] = st
            m.save()
            print(f"[resume] salvage dịch {n}/{tot} missing={n_miss} -> pending ({e})", flush=True)
        except Exception as se:  # noqa: BLE001
            print(f"[trans] salvage lỗi: {se}", flush=True)
            m.mark_failed(STAGE, e)
        raise

    # n_missing cuối cùng: đếm trên file (sau tách sub)
    n_missing = count_script_missing(work_dir)
    if n_missing < 0:
        n_missing = sum(1 for r in ordered if not (r.get("vi") or "").strip())
    if auto_review is None:
        auto_review = (_cfg_get("AUTO_REVIEW", "1") or "1").strip().lower() in ("1", "true", "yes", "on")

    # TỰ ĐỘNG CHẠY LƯỢT 2 (Rà soát văn phong và chuẩn hóa xưng hô)
    if auto_review:
        print(
            f"\n[pipeline] NMT/L1 xong → LƯỢT 2 RÀ SOÁT (LLM={_rmodel()}) "
            f"— sửa tên/lock/sai nghĩa, không dịch lại toàn bộ...",
            flush=True,
        )
        try:
            rv_res = run_review(
                work_dir=work_dir,
                batch=min(40, max(batch or 25, 20)),
                target=target,
                force=force,
            )
            print(f"[pipeline] ✅ XONG: NMT dịch chính + LLM rà soát", flush=True)
            return rv_res
        except Exception as e_rv:
            print(f"[pipeline] ⚠️ Lượt 2 rà soát lỗi ({e_rv}) → giữ bản NMT/L1.", flush=True)

    result = m.mark_done(
        STAGE, script_path=str(script_path), glossary_path=str(plan_path),
        n_segments=len(ordered),
        n_missing=max(0, n_missing), model=(model or _tmodel() or "default"),
        mode=(m.stage(STAGE) or {}).get("mode") or "batch",
        cur_text=(
            f"thiếu {n_missing} câu — bấm Dịch vá"
            if n_missing > 0 else "đủ bản dịch"
        ),
    )
    unload_local(model or _tmodel())          # nhả VRAM cho bước TTS
    print(f"[ok] Dịch xong -> {script_path}"
          + (f"  (còn {n_missing} câu trống sau kiểm tra)" if n_missing else " · missing=0"))
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage dịch — hồ sơ nhân vật + xưng hô + ngữ cảnh.")
    ap.add_argument("work_dir")
    ap.add_argument("--batch", type=int, default=20)
    ap.add_argument("--target", default="Tiếng Việt")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--mode", default=None, help="oneshot | batch | auto")
    ap.add_argument("--review", action="store_true",
                    help="Chỉ chạy lượt 2 soát văn phong (script.json đã có).")
    ap.add_argument("--review-force", action="store_true",
                    help="Soát lại cả câu đã rv=1.")
    args = ap.parse_args(argv)
    if args.review or args.review_force:
        run_review(work_dir=args.work_dir, batch=min(args.batch, 40),
                   target=args.target, force=args.review_force)
        return
    run_translate(work_dir=args.work_dir, batch=args.batch, target=args.target,
                  force=args.force, mode=args.mode)


if __name__ == "__main__":
    main()
