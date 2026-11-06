import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

for url in [
    "http://127.0.0.1:8083/v1/models",
    "http://127.0.0.1:8083/health",
    "http://127.0.0.1:8083/props",
]:
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = resp.read().decode("utf-8")
            print(f"=== {url} -> Code {resp.status} ===")
            print(data[:600])
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"=== {url} -> HTTPError {e.code}: {e.reason} ===")
        print(body[:600])
    except Exception as e:
        print(f"=== {url} -> Error: {e} ===")
