import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

for endpoint in [
    "http://127.0.0.1:8801/api/queue",
    "http://127.0.0.1:8801/api/status",
    "http://127.0.0.1:8802/status",
]:
    try:
        res = urllib.request.urlopen(endpoint, timeout=3)
        data = json.loads(res.read().decode("utf-8"))
        print(f"=== {endpoint} ===")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1200])
    except Exception as e:
        print(f"=== {endpoint} FAILED: {e} ===")
