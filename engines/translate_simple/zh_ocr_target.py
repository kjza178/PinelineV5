"""OCR hardsub CÓ CHỌN LỌC cho luồng simple — SIMPLE_ZH_OCR_MODE=targeted (mặc định) — 2026-11-14.

Thay vì OCR cả phim (1efd1014ac77_p03: 16.702 khung, hàng giờ), chỉ OCR 1 khung GIỮA câu ở những câu mà chữ
Trung đúng/sai làm đổi bản dịch:

  Lượt A (zh_source.prepare, sau ASR, TRƯỚC plan) — câu ASR có:
    • 他/她/它 (cùng âm tā — ASR không phân biệt nổi; quyết định anh ấy / cô ấy / nó),
    • tên / thuật ngữ trong hồ sơ phim (zh_source.profile_names),
    • số / tuổi / cấp (ASR hay nghe nhầm).
  Lượt B (pipeline, sau review + kiểm, TRƯỚC vá) — câu kém chắc người nói (s_conf < SIMPLE_CONF_MIN), người nghe
    '?' hoặc bị cờ, kèm 1 câu trước + 1 câu sau (ngữ cảnh). Câu OCR khác ASR → thay chữ, bỏ rv → lượt soát bổ sung
    (_review_missing) soát lại; OCR trùng ASR → không tốn thêm lần gọi model.

OCR KHÔNG cho biết ai nói — nó cho đúng CHỮ (tên người được gọi, 他/她, xưng hô) để plan/review suy đúng hơn.
Ghép: align() chỉ lấy đoạn của dòng hardsub khớp câu ASR (dòng hardsub hay chứa 2 câu ASR → không chép cả dòng).
"""
from __future__ import annotations

import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

TA = re.compile("[他她它]")
NUM = re.compile(r"[0-9０-９]|[零一二两三四五六七八九十百千万亿]+[岁年级个位天层阶重品星段代]")
_TAIL = re.compile(r"[。！？!?，,、…~～：:；;」』\"']+$")


def _core(s: str | None) -> str:
    return re.sub(r"[^一-鿿0-9A-Za-z]", "", s or "")


def accept_conf() -> float:
    """Độ tin cậy OCR tối thiểu (chữ thấp nhất của dòng) để THAY chữ ASR — OCR_HS_ACCEPT_CONF (0.8)."""
    try:
        from .cfg import get
        return float(get("OCR_HS_ACCEPT_CONF", "0.8") or 0.8)
    except Exception:  # noqa: BLE001
        return 0.8


def _lev(a: str, b: str) -> int:
    """Khoảng cách Levenshtein (thay/thêm/bớt = 1)."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def align(asr: str | None, ocr_line: str | None, *, min_ratio: float = 0.6) -> str | None:
    """Chữ thay cho câu ASR (giữ dấu câu cuối của ASR) hoặc None (không đổi / không đủ tin)."""
    a, o = _core(asr), _core(ocr_line)
    if len(a) < 2 or not o or a in o:  # trùng / OCR chứa nguyên câu ASR (dòng gộp 2 câu) → không sửa
        return None
    L = len(a)
    best = None                                   # (khoảng cách, -độ dài, đoạn)
    for ln in range(max(2, L - 2), L + 3):
        if ln > len(o):
            break
        for st in range(0, len(o) - ln + 1):
            w = o[st:st + ln]
            key = (_lev(a, w), -ln, w)            # hoà điểm → đoạn DÀI hơn (thay chữ, không bỏ chữ 她/他)
            if best is None or key[:2] < best[:2]:
                best = key
    if best is None or best[2] == a or best[0] > max(1, int(round((1 - min_ratio) * L))):
        return None
    best_w = best[2]
    if len(best_w) < L:
        return None  # KHÔNG bớt chữ: dòng hardsub giữa câu thường chỉ là một phần câu ASR dài (đo e00fcc006b57_p01)
    def _asc(s):
        return len(re.findall(r"[0-9A-Za-z]", s))
    def _cnum(s):
        return len(re.findall("[零一二两三四五六七八九十百千万亿]", s))
    add_asc = _asc(best_w) - _asc(a)
    if add_asc > 0 and (_cnum(a) - _cnum(best_w)) * 2 < add_asc:
        return None  # chữ Hán bị thay bằng số/Latinh không tương ứng (vd 至高精英 → 000点) = OCR đọc nhầm
    if L < 4 and (len(best_w) != L or TA.sub("T", best_w) != TA.sub("T", a)):
        return None  # câu ngắn: chỉ nhận đổi 他/她/它 (khác chữ khác dễ là ghép nhầm dòng bên cạnh)
    m = _TAIL.search(asr or "")
    return best_w + (m.group(0) if m else "")


def pick_a(segments: list[dict], names: list[str]) -> list[int]:
    """Vị trí (index) các câu cần OCR ở lượt A."""
    nm = [n for n in (names or []) if n and len(n) >= 2]
    out = []
    for k, s in enumerate(segments):
        t = s.get("text") or ""
        if len(_core(t)) < 2:
            continue
        if TA.search(t) or NUM.search(t) or any(n in t for n in nm):
            out.append(k)
    return out


def pick_b(rows: list[dict], flags: dict, conf_min: float, done: set) -> list[int]:
    """Vị trí các hàng script cần OCR ở lượt B (±1 câu ngữ cảnh), bỏ hàng đã OCR ở lượt A / manual / rác."""
    core = set()
    for k, r in enumerate(rows):
        if r.get("junk"):
            continue
        try:
            ii = int(r.get("i"))
        except (TypeError, ValueError):
            continue
        try:
            c = float(r.get("s_conf")) if r.get("s_conf") is not None else 1.0
        except (TypeError, ValueError):
            c = 1.0
        if c < conf_min or str(r.get("s_to") or "").strip() == "?" or ii in flags:
            core.update((k - 1, k, k + 1))
    out = []
    for k in sorted(core):
        if not 0 <= k < len(rows):
            continue
        r = rows[k]
        try:
            ii = int(r.get("i"))
        except (TypeError, ValueError):
            continue
        if ii in done or r.get("manual") or r.get("junk") or len(_core(r.get("zh"))) < 2:
            continue
        out.append(k)
    return out


# ----------------------------------------------------------------------------- khung + OCR
_HW = {"ok": None}   # None = chưa thử · True/False = -hwaccel cuda dùng được / không


def _grab_band(video: Path, t: float, rect: tuple[int, int, int, int]):
    """1 khung dải phụ đề tại t (xám). Thử giải mã GPU trước; không ra khung → CPU và nhớ lại."""
    import numpy as np
    x, y, w, h = rect

    def run(hw: bool):
        c = ["ffmpeg", "-v", "error", "-nostdin"]
        if hw:
            c += ["-hwaccel", "cuda"]
        c += ["-ss", f"{max(0.0, t):.3f}", "-i", str(video), "-frames:v", "1", "-an",
              "-vf", f"crop={w}:{h}:{x}:{y},format=gray", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
        try:  # ffmpeg treo (file hỏng / ổ mạng) không được kéo cả bước dịch treo theo
            return subprocess.run(c, capture_output=True, timeout=60).stdout
        except subprocess.TimeoutExpired:
            return b""

    out = b""
    if _HW["ok"] is not False:
        out = run(True)
        if _HW["ok"] is None:
            _HW["ok"] = len(out) >= w * h
    if len(out) < w * h:
        out = run(False)
    if len(out) < w * h:
        return None
    return np.frombuffer(out[: w * h], dtype=np.uint8).reshape(h, w)


def ocr_times(work_dir: Path, items: list[tuple[int, float]], *, ocr=None, grab=None, video=None,
              workers: int = 6, stop_check=None) -> tuple[dict, dict]:
    """items = [(key, t)] → ({key: chữ OCR}, thống kê). Lấy khung song song (ffmpeg), OCR tuần tự."""
    import engines.hs_ocr_fast as F
    from engines.asr.hardsub_asr import _find_video, _probe_size
    t0 = time.time()
    dev = "test"
    if not items:
        return {}, {"n": 0, "sec": 0.0}
    if grab is None:
        video = Path(video) if video else _find_video(work_dir)
        if not video:
            raise RuntimeError("Chưa có video")
        W, H = _probe_size(video)
        rect = F.band_rect(work_dir, W, H)

        def grab(t):  # noqa: E306
            return _grab_band(video, t, rect)
    if ocr is None:
        ocr, dev = F.make_ocr()
    out: dict = {}
    conf: dict = {}
    n_fail = 0
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        futs = [(key, ex.submit(grab, t)) for key, t in items]
        for key, fu in futs:
            if stop_check and stop_check():
                break
            try:
                g = fu.result()
            except Exception:  # noqa: BLE001
                g = None
            if g is None:
                n_fail += 1
                continue
            out[key] = ocr(g) or ""
            conf[key] = float(getattr(ocr, "last_conf", 1.0) or 0.0) if out[key] else 0.0
    return out, {"n": len(items), "grab_fail": n_fail, "sec": round(time.time() - t0, 1), "device": dev,
                 "hwdec": bool(_HW["ok"]), "conf": conf}


def _mid(s: dict) -> float:
    a, b = float(s.get("start") or 0), float(s.get("end") or 0)
    return (a + b) / 2 if b > a else a


# ----------------------------------------------------------------------------- lượt A / B
def pass_a(work_dir: str | Path, segments: list[dict], names: list[str], *, ocr=None, grab=None,
           video=None) -> tuple[list[dict], dict]:
    """Trả (segments mới, báo cáo). Câu được thay: text=OCR, zh_src='ocr', zh_asr=chữ cũ."""
    wd = Path(work_dir)
    segs = [dict(s) for s in segments]
    for s in segs:
        s.setdefault("zh_src", "asr")
    ks = pick_a(segs, names)
    texts, st = ocr_times(wd, [(k, _mid(segs[k])) for k in ks], ocr=ocr, grab=grab, video=video)
    cmap = st.pop("conf", {}) or {}
    cmin = accept_conf()
    changes = []
    n_lowconf = 0
    for k in ks:
        if cmap.get(k, 1.0) < cmin:
            n_lowconf += 1
            continue
        new = align(segs[k].get("text"), texts.get(k))
        if new is None:
            continue
        old = segs[k].get("text")
        segs[k]["zh_asr"] = old
        segs[k]["text"] = new
        segs[k]["zh_src"] = "ocr"
        changes.append({"i": segs[k].get("i"), "from": old, "to": new})
    done_i = []
    for k in ks:
        try:
            done_i.append(int(segs[k].get("i")))
        except (TypeError, ValueError):
            pass
    rep = {"n_target": len(ks), "n_changed": len(changes), "n_lowconf": n_lowconf, "changes": changes[:80],
           "done_i": done_i, **st}
    print(f"[simple-zh] OCR lượt A: {len(ks)} câu → đổi {len(changes)} · {st.get('sec')}s · {st.get('device')}",
          flush=True)
    return segs, rep


def pass_b(work_dir: str | Path, store, flags: dict, conf_min: float, *, done: set | None = None,
           ocr=None, grab=None, video=None, stop_check=None) -> dict:
    """Sửa TẠI CHỖ store.rows: câu OCR khác ASR → zh mới, zh_asr giữ, bỏ rv (soát lại). Trả báo cáo."""
    wd = Path(work_dir)
    rows = store.rows
    ks = pick_b(rows, flags, conf_min, set(done or ()))
    texts, st = ocr_times(wd, [(k, _mid(rows[k])) for k in ks], ocr=ocr, grab=grab, video=video,
                          stop_check=stop_check)
    cmap = st.pop("conf", {}) or {}
    cmin = accept_conf()
    changed = []
    for k in ks:
        r = rows[k]
        if cmap.get(k, 1.0) < cmin:
            continue
        new = align(r.get("zh"), texts.get(k))
        if new is None:
            continue
        old = r.get("zh")
        r.setdefault("zh_asr", old)
        r["zh"] = new
        r["zh_src"] = "ocr_b"
        r.pop("rv", None)
        r.pop("s_flags", None)
        store.note("zh_ocr_b", r.get("i"), f"OCR lượt B: {old} → {new}")
        try:
            changed.append(int(r.get("i")))
        except (TypeError, ValueError):
            pass
    rep = {"n_target": len(ks), "n_changed": len(changed), "changed_i": changed, **st}
    print(f"[simple] OCR lượt B: {len(ks)} câu → đổi {len(changed)} (soát lại) · {st.get('sec')}s", flush=True)
    return rep
