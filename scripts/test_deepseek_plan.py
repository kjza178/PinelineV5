# -*- coding: utf-8 -*-
"""Thử lập plan cả phim (A7) bằng DeepSeek cho 1 job — KHÔNG đụng job (chạy trên bản sao asr.json ở thư mục tạm).

Dùng (2026-11-18, kiểm lỗi «DeepSeek trả rỗng» + tắt thinking):
    python scripts\\test_deepseek_plan.py b138b16bef8f_p01                 :: thinking TẮT (mặc định mới)
    python scripts\\test_deepseek_plan.py b138b16bef8f_p01 --thinking enabled
    python scripts\\test_deepseek_plan.py b138b16bef8f_p01 --compare      :: chạy cả 2 để so (tốn token x2)
In mỗi lần gọi API: HTTP, finish_reason, prompt/completion/reasoning tokens, thời gian. Không in key.
Chạy process riêng → dùng code llm.py mới mà KHÔNG cần restart :8801.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def _hook_requests(log: list) -> None:
    import engines.llm as llm
    real = llm.requests.post

    def post(url, *a, **k):
        t0 = time.time()
        r = real(url, *a, **k)
        info = {"url": url.split("?")[0], "http": r.status_code, "sec": round(time.time() - t0, 1),
                "thinking": ((k.get("json") or {}).get("thinking") or {}).get("type"),
                "max_tokens": (k.get("json") or {}).get("max_tokens")}
        try:
            d = r.json()
            ch = (d.get("choices") or [{}])[0] or {}
            msg = ch.get("message") or {}
            u = d.get("usage") or {}
            info.update(finish_reason=ch.get("finish_reason"), prompt_tokens=u.get("prompt_tokens"),
                        completion_tokens=u.get("completion_tokens"),
                        reasoning_tokens=(u.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                        content_chars=len(msg.get("content") or ""),
                        reasoning_chars=len(msg.get("reasoning_content") or ""))
        except Exception:  # noqa: BLE001
            info["body"] = (r.text or "")[:200]
        log.append(info)
        print(f"  [api] {json.dumps(info, ensure_ascii=False)}", flush=True)
        return r
    llm.requests.post = post


def run_once(job: str, thinking: str, work: Path) -> dict:
    os.environ["DEEPSEEK_THINKING"] = thinking
    src = work / job / "asr.json"
    if not src.is_file():
        raise SystemExit(f"không thấy {src}")
    segments = json.loads(src.read_text(encoding="utf-8"))
    import core.config as config
    model = config.get("PLAN_MODEL") or "deepseek/deepseek-flash"
    tmp = Path(tempfile.mkdtemp(prefix="ds_plan_"))
    shutil.copy2(src, tmp / "asr.json")
    from engines.translate_simple import stage_draft
    print(f"\n=== {job} · model={model} · thinking={thinking} · {len(segments)} câu ASR ===", flush=True)
    t0 = time.time()
    plan = None
    err = ""
    try:
        plan = stage_draft.build_full_movie_plan(tmp, segments, model=model)
    except Exception as e:  # noqa: BLE001
        err = str(e)
    sec = round(time.time() - t0, 1)
    shutil.rmtree(tmp, ignore_errors=True)
    if plan:
        res = {"ok": True, "sec": sec, "characters": len(plan.get("characters") or []),
               "pronouns": len(plan.get("pronouns") or []), "terms": len(plan.get("terms") or [])}
        names = [str(c.get("name") or c.get("vi") or "") for c in (plan.get("characters") or [])[:8]]
        print(f"KẾT QUẢ: OK sau {sec}s · nhân vật={res['characters']} cặp xưng hô={res['pronouns']} "
              f"thuật ngữ={res['terms']} · vd: {', '.join(names)}", flush=True)
    else:
        res = {"ok": False, "sec": sec, "error": err or "A7 trả None (xem dòng [simple-plan] phía trên)"}
        print(f"KẾT QUẢ: LỖI sau {sec}s · {res['error']}", flush=True)
    return res


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("job")
    ap.add_argument("--thinking", default="disabled")
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--work", default="work")
    a = ap.parse_args()
    log: list = []
    _hook_requests(log)
    modes = ["disabled", "enabled"] if a.compare else [a.thinking]
    out = {m: run_once(a.job, m, Path(a.work)) for m in modes}
    print("\nTÓM TẮT:", json.dumps(out, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
