import json
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8")

payload = {
    "model": "gemma4-26b-qat-uncen-mtp",
    "messages": [
        {"role": "user", "content": "Dịch sang tiếng Việt: 你好世界"}
    ],
    "max_tokens": 50,
    "temperature": 0.3
}

req = urllib.request.Request(
    "http://127.0.0.1:8083/v1/chat/completions",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        print("Status code:", resp.status)
        print("Response:", resp.read().decode("utf-8"))
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code, e.reason)
    print(e.read().decode("utf-8"))
except Exception as e:
    print("Error:", e)
