import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

WORK = Path(r"Z:\PinelineV2\work")
running_jobs = []
failed_jobs = []
translate_states = []

for d in WORK.iterdir():
    if not d.is_dir():
        continue
    mf = d / "manifest.json"
    if not mf.is_file():
        continue
    try:
        data = json.loads(mf.read_text(encoding="utf-8"))
        req = data.get("request") or {}
        stages = data.get("stages") or {}
        title = req.get("title") or d.name
        
        # Check any running stage
        has_running = False
        for sname, sinfo in stages.items():
            if isinstance(sinfo, dict) and sinfo.get("status") == "running":
                has_running = True
                running_jobs.append((d.name, title, sname, sinfo))
                
        # Check translate specifically
        tr = stages.get("translate") or {}
        tr_st = tr.get("status")
        if tr_st:
            translate_states.append((d.name, title, tr_st, tr.get("error"), tr.get("model"), tr.get("backend")))
            
        # Check failed
        for sname, sinfo in stages.items():
            if isinstance(sinfo, dict) and sinfo.get("status") in ("failed", "error"):
                failed_jobs.append((d.name, title, sname, sinfo.get("error")))
    except Exception as e:
        pass

print("=== RUNNING STAGES ===")
for jid, t, sname, sinfo in running_jobs:
    print(f"[{jid}] {t} -> Stage: {sname} | Info: {sinfo}")

print("\n=== RECENT FAILED STAGES ===")
for jid, t, sname, err in failed_jobs[-10:]:
    print(f"[{jid}] {t} -> Stage: {sname} | Error: {err}")

print("\n=== RECENT TRANSLATE STAGES ===")
for jid, t, st, err, model, backend in translate_states[-10:]:
    print(f"[{jid}] {t} -> Status: {st} | Model: {model} | Backend: {backend} | Error: {err}")
