"""Bước 2: Plan (cloud) ∥ NMT nháp (GPU) — chạy SONG SONG bằng 2 thread.

Plan: dùng lại glossary.json nếu có (trừ force — như run_translate cũ; context_pack.skip_plan
luôn giữ), không thì translate.build_plan (PLAN_MODE=file → upload SRT; lỗi → sample), rồi
series_glossary.apply + ensure_hard_terms (+ pronoun analyze nếu SIMPLE_PRONOUN_ANALYZE=1).
Plan lỗi → plan rỗng (vẫn dịch, kém nhất quán) — y như luồng cũ.

NMT: mt_zh_vi.draft_rows cho câu chưa có vi (không manual). Vì chạy song song nên NMT chưa có plan
của tập này: flavor base/QT chọn theo glossary.json cũ hoặc bảng bộ (series) nếu có, không thì base
(mặc định cho mixed/chưa rõ). SIMPLE_NMT_WAIT_PLAN=1 → NMT chờ plan (tuần tự, đúng flavor).
NMT tắt / lỗi → nháp rỗng → review dịch mới các câu đó (cờ «dịch»).
"""
from __future__ import annotations

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import cfg
from .script_store import ScriptStore, has_cjk, is_manual


def _load_json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def _series_plan(work_dir: Path) -> dict | None:
    try:
        import series_glossary
        return series_glossary.load(series_glossary.series_key(work_dir))
    except Exception as e:  # noqa: BLE001
        print(f"[simple-plan] bảng bộ: {e}", flush=True)
        return None


def _plan_usable(plan) -> bool:
    """R1.2: glossary rỗng / plan_status=failed → không reuse (phải lập lại)."""
    if not isinstance(plan, dict):
        return False
    if str(plan.get("plan_status") or "").lower() == "failed":
        return False
    chars = plan.get("characters") or []
    pronouns = plan.get("pronouns") or []
    terms = plan.get("terms") or []
    if chars or pronouns or terms:
        return True
    # plan «ok» có chủ đích trống (phim không nhân vật) — hiếm; cho reuse nếu đánh dấu
    return str(plan.get("plan_status") or "").lower() == "ok"


def build_full_movie_plan(
    work_dir: Path,
    segments: list[dict],
    target: str = "Tiếng Việt",
    *,
    model: str | None = None,
    name_hints: list[str] | None = None,
    series_plan: dict | None = None,
) -> dict | None:
    """A7: Lập glossary toàn phim bằng cách đưa toàn bộ text thoại ASR vào LLM context lớn.

    Tận dụng DeepSeek/Aurora/Qwen với context window lớn:
    - Đọc xuyên suốt toàn bộ phim để nhận diện đầy đủ nhân vật, vai trò, quan hệ xưng hô và bối cảnh.
    - Giới hạn text sạch ~26.000 ký tự để vừa vặn ngưỡng prompt mà không bị lỗi length/payload.
    - Trả về dict chuẩn schema glossary.json (characters, pronouns, terms, summary, style_lock).
    """
    valid_segs = [s for s in segments if (s.get("text") or "").strip()]
    if len(valid_segs) < 5:
        return None

    texts = [(s.get("text") or "").strip() for s in valid_segs]
    total_len = sum(len(t) for t in texts)
    max_chars = 26000

    if total_len <= max_chars:
        full_text = " ".join(texts)
    else:
        # Lấy mẫu dày đều từ đầu đến cuối phim để bảo toàn 100% dòng thời gian
        n_segs = len(texts)
        target_count = max(10, int(n_segs * (max_chars / total_len) * 0.95))
        indices = [int(round(k * (n_segs - 1) / max(1, target_count - 1))) for k in range(target_count)]
        indices = sorted(list(dict.fromkeys(indices)))
        sampled = []
        cur_chars = 0
        for idx in indices:
            t = texts[idx]
            if cur_chars + len(t) + 1 > max_chars:
                break
            sampled.append(t)
            cur_chars += len(t) + 1
        full_text = " ".join(sampled)

    import translate as T
    seed = T._plan_seed_blocks(name_hints, series_plan, soft_ocr=True)

    sys_prompt = (
        "Bạn là Chuyên gia Cao Cấp phân tích kịch bản và ngôn ngữ phim Trung Quốc, chuẩn bị phương án dịch "
        f"và lồng tiếng sang {target}.\n"
        "Nhiệm vụ của bạn là ĐỌC TOÀN BỘ thoại ASR của cả bộ phim và lập HỒ SƠ PHIM TOÀN DIỆN (bảng nhân vật, "
        "mối quan hệ xưng hô thực tế, thuật ngữ, bối cảnh xuyên suốt).\n"
        "CHỈ trả về DUY NHẤT một JSON object hợp lệ, không bọc markdown, không thêm bất kỳ văn bản nào ngoài JSON."
    )
    user_prompt = (
        f"Dưới đây là TOÀN BỘ thoại tiếng Trung (ASR) của cả bộ phim:\n\"\"\"{full_text}\"\"\"\n\n"
        f"{seed}\n\n"
        "Hãy phân tích toàn bộ câu chuyện và trả về JSON với cấu trúc chuẩn sau:\n"
        "{\n"
        '  "summary": "Tóm tắt ngắn gọn cốt truyện chính và bối cảnh toàn phim (3-5 câu)",\n'
        '  "genre": "thể loại phim (ví dụ: Đô thị, Tu tiên, Tổng tài, Cổ trang...)",\n'
        '  "tone": "văn phong chủ đạo (ví dụ: Hài hước, Kịch tính, Trầm lắng...)",\n'
        '  "characters": [\n'
        '    {\n'
        '      "zh": "tên tiếng Trung trong thoại",\n'
        '      "vi": "tên Hán-Việt chuẩn",\n'
        '      "gender": "nam | nữ",\n'
        '      "role": "vai trò / chức vụ / thân phận / quan hệ",\n'
        '      "aliases": ["tên gọi khác hoặc lỗi đồng âm ASR bị nghe nhầm sang"]\n'
        '    }\n'
        '  ],\n'
        '  "pronouns": [\n'
        '    {\n'
        '      "who": "tên VI người nói",\n'
        '      "to": "tên VI người nghe",\n'
        '      "self": "tự xưng (ví dụ: anh, tôi, muội...)",\n'
        '      "call": "cách gọi đối phương (ví dụ: em, cô, sư huynh...)",\n'
        '      "note": "ngữ cảnh / thái độ"\n'
        '    }\n'
        '  ],\n'
        '  "terms": [\n'
        '    {\n'
        '      "zh": "từ tiếng Trung",\n'
        '      "vi": "nghĩa Hán-Việt hoặc bản dịch chuẩn",\n'
        '      "type": "place | org | title | skill | object"\n'
        '    }\n'
        '  ],\n'
        '  "style_lock": {\n'
        '    "mode": "modern | ancient | mixed",\n'
        '    "pronoun_policy": "quy tắc xưng hô chung của phim"\n'
        '  }\n'
        "}"
    )

    from .stage_review import _decode
    import cloud_retry
    from llm import chat

    mt = {"v": cfg.max_tokens()}

    def _call():
        # 2026-11-18: DeepSeek trả rỗng vì hết max_tokens (finish_reason=length) → thử lại 1 lần với gấp đôi
        # (≤32768). Rỗng vì lý do khác → LLMEmptyResponse lên luôn: cloud_retry không lặp, build_plan rơi
        # xuống file/sample (trước: «thất bại …: None» bị coi là 5xx → gửi lại cả phim tới 16 lần).
        from llm import LLMEmptyResponse
        for _ in range(2):
            try:
                out = chat(
                    [{"role": "system", "content": sys_prompt}, {"role": "user", "content": user_prompt}],
                    model=model,
                    temperature=cfg.temperature(),
                    json_mode=True,
                    max_tokens=mt["v"],
                    timeout=max(cfg.timeout(), 420),
                )
                return _decode(out)
            except LLMEmptyResponse as e:
                if getattr(e, "finish_reason", "") != "length" or mt["v"] >= 32768:
                    raise
                mt["v"] = min(32768, mt["v"] * 2)
                print(f"[simple-plan-a7] hết max_tokens → thử lại với max_tokens={mt['v']}", flush=True)
        raise RuntimeError("A7: hết lượt thử max_tokens")

    try:
        data = cloud_retry.call_with_cloud_retry(
            _call,
            model=model,
            label="[simple-plan-a7]",
            what=f"plan cả phim ({len(valid_segs)} câu ASR)",
            cfg_get=cfg.get,
        )
        if isinstance(data, dict) and (data.get("characters") or data.get("terms") or data.get("pronouns")):
            data.setdefault("plan_status", "ok")
            data.setdefault("plan_source", "full_movie_asr")
            return data
    except Exception as e:
        print(f"[simple-plan] A7 full-movie plan lỗi ({e})", flush=True)
    return None


def build_plan(work_dir: Path, segments: list[dict], target: str, *, force: bool = False) -> dict:
    import translate as T
    from fileio import atomic_write_json

    plan_path = work_dir / "glossary.json"
    skip_plan = bool((_load_json(work_dir / "context_pack.json") or {}).get("skip_plan"))
    plan = None
    if plan_path.exists() and (not force or skip_plan):
        loaded = _load_json(plan_path)
        if _plan_usable(loaded):
            plan = loaded
            print("[simple-plan] dùng lại glossary.json có sẵn", flush=True)
            if skip_plan:
                try:
                    from context_studio.schema import apply_style_lock_from_genre
                    plan = apply_style_lock_from_genre(plan)
                except Exception:  # noqa: BLE001
                    pass
        else:
            print("[simple-plan] glossary.json rỗng/failed — lập lại plan", flush=True)
            plan = None
    if plan is None:
        try:
            pm_fn = getattr(cfg, "plan_model", None)
            plan_m = pm_fn(work_dir) if callable(pm_fn) else None
            plan = T.build_plan(
                segments, target=target, model=plan_m,
                name_hints=T._ocr_name_hints(work_dir) or None,
                series_plan=_series_plan(work_dir), work_dir=work_dir,
                before_local_llm=None,  # simple: KHÔNG đổi preset local
            )
            if isinstance(plan, dict):
                plan.setdefault("plan_status", "ok")
            # review 2026-11-12: ghi plan vừa lập TRƯỚC save_from (như run_translate cũ) — trước đây
            # save_from đọc glossary.json chưa tồn tại / cũ → bảng bộ không học được tập mới.
            atomic_write_json(plan_path, plan, fsync=False)
        except Exception as e:  # noqa: BLE001
            print(f"[simple-plan] LỖI lập plan ({e}) → không ghi glossary.json rỗng (R1.2)", flush=True)
            plan = {"content_type": "", "genre": "", "tone": "", "characters": [], "terms": [],
                    "pronouns": [], "scenes": [], "pronoun_notes": "",
                    "plan_status": "failed", "plan_error": str(e)[:300]}
            try:
                atomic_write_json(work_dir / "glossary.plan_failed.json", plan, fsync=False)
            except Exception:  # noqa: BLE001
                pass
    try:
        import series_glossary
        plan = series_glossary.apply(work_dir, plan)
        if _plan_usable(plan):
            series_glossary.save_from(work_dir, reason="cập nhật plan tập mới (simple)")
    except Exception as e:  # noqa: BLE001
        print(f"[simple-plan] bảng bộ: {e}", flush=True)
    plan = T.ensure_hard_terms(plan)
    if cfg.pronoun_analyze() and _plan_usable(plan):
        try:
            from pronoun_consistency import ensure_analyze_before_translate
            plan, _pa = ensure_analyze_before_translate(work_dir, plan, segments=segments, force=False)
            plan = T.ensure_hard_terms(plan)
        except Exception as e:  # noqa: BLE001
            print(f"[simple-plan] pronoun-analyze bỏ qua: {e}", flush=True)
    # R1.2: chỉ ghi glossary.json khi plan dùng được (tránh khoá lần sau vào bản rỗng)
    if _plan_usable(plan):
        atomic_write_json(plan_path, plan, fsync=False)
    sl = plan.get("style_lock") if isinstance(plan, dict) else None
    if isinstance(sl, dict):
        atomic_write_json(work_dir / "style_lock.json", sl, fsync=False)
    return plan


def nmt_drafts(rows: list[dict], hint_plan: dict | None) -> dict[int, str]:
    """{i: nháp} — chỉ câu chưa có vi, không manual, chưa rv. NMT tắt/lỗi → {}."""
    todo = [r for r in rows if not is_manual(r) and not r.get("rv") and not (r.get("vi") or "").strip()
            and (r.get("zh") or "").strip()]
    if not todo:
        return {}
    try:
        import mt_zh_vi
        if not mt_zh_vi.enabled():
            print("[simple-nmt] MT_ZH_VI tắt → review dịch mới mọi câu", flush=True)
            return {}
        t0 = time.time()
        out = mt_zh_vi.draft_rows([{"i": r["i"], "text": r.get("zh") or ""} for r in todo], plan=hint_plan)
        out = {int(k): (v or "").strip() for k, v in (out or {}).items()
               if (v or "").strip() and not has_cjk(v)}
        print(f"[simple-nmt] nháp {len(out)}/{len(todo)} câu ({time.time() - t0:.1f}s, "
              f"{mt_zh_vi.resolve_model_id(hint_plan)})", flush=True)
        if cfg.nmt_unload():
            try:
                mt_zh_vi.unload()
            except Exception:  # noqa: BLE001
                pass
        return out
    except Exception as e:  # noqa: BLE001
        print(f"[simple-nmt] lỗi ({e}) → nháp rỗng, review dịch mới", flush=True)
        return {}


def run(store: ScriptStore, segments: list[dict], target: str, *, force: bool = False,
        progress=None) -> tuple[dict, dict]:
    """Chạy plan ∥ NMT. Trả (plan, info). Ghi nháp NMT vào store (mt=1, trace 'nmt')."""
    wd = store.work_dir
    hint_plan = _load_json(wd / "glossary.json") if not force else None
    if not isinstance(hint_plan, dict):
        hint_plan = _series_plan(wd)
    rows_snapshot = [dict(r) for r in store.rows]
    info: dict = {"parallel": not cfg.nmt_wait_plan()}
    t0 = time.time()
    import mt_zh_vi
    nmt_active = mt_zh_vi.enabled()
    if not nmt_active:
        print("[simple-draft] NMT tắt → DeepSeek dịch trực tiếp 100% từ tiếng Trung (zh)", flush=True)
        plan = build_plan(wd, segments, target, force=force)
        drafts = {}
        info["t_plan"] = round(time.time() - t0, 2)
        info["t_nmt"] = 0.0
        info["parallel"] = False
    elif cfg.nmt_wait_plan():
        plan = build_plan(wd, segments, target, force=force)
        info["t_plan"] = round(time.time() - t0, 2)
        drafts = nmt_drafts(rows_snapshot, plan)
        info["t_nmt"] = round(time.time() - t0 - info["t_plan"], 2)
    else:
        marks: dict = {}

        def _p():
            marks["plan_start"] = time.time()
            try:
                return build_plan(wd, segments, target, force=force)
            finally:
                marks["plan_end"] = time.time()

        def _n():
            marks["nmt_start"] = time.time()
            try:
                return nmt_drafts(rows_snapshot, hint_plan)
            finally:
                marks["nmt_end"] = time.time()

        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="simple-draft") as ex:
            fp, fn = ex.submit(_p), ex.submit(_n)
            plan = fp.result()
            drafts = fn.result()
        info.update({k: round(v - t0, 3) for k, v in marks.items()})
    by_i = store.by_i()
    n = 0
    for i, vi in drafts.items():
        r = by_i.get(i)
        if r is None or is_manual(r) or (r.get("vi") or "").strip():
            continue
        if store.set_vi(r, vi, "nmt", "nháp NMT"):
            r["mt"] = 1
            n += 1
    store.save()
    info["n_nmt"] = n
    if progress:
        progress(f"plan ∥ NMT xong · nháp {n} câu")
    return plan, info
