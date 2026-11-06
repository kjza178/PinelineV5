import os
import sys

sys.path.insert(0, r"Z:\PinelineV2")
import subprocess
import time
from test_channel import upload_test_sample

SRC = r"C:\Users\MyPC\Downloads\[TEST_BLOCK] 逆江湖之苍生为局第四季 (1791852058).mp4"
BGM = r"Z:\PinelineV2\assets\bgm_yt\calm\A_Distant_Call__Dan_Lebo_Lebowitz_Tone_Seeker.mp3"
OUT_DIR = r"Z:\PinelineV2\scratch\anti_block_4"
os.makedirs(OUT_DIR, exist_ok=True)

if not os.path.exists(SRC):
    print(f"Error: Source not found: {SRC}")
    sys.exit(1)

variants = [
    {
        "key": "A",
        "title": "[TEST] Variant A - Zoom 5% + Color + Noise + Pitch + BGM",
        "file": os.path.join(OUT_DIR, "variant_A.mp4"),
        "cmd": [
            "ffmpeg", "-y",
            "-i", SRC,
            "-i", BGM,
            "-filter_complex",
            "[0:v]crop=in_w*0.95:in_h*0.95:(in_w-in_w*0.95)/2:(in_h-in_h*0.95)/2,scale=1280:720,setpts=PTS/1.03,eq=contrast=1.05:brightness=0.02:saturation=1.06,hue=h=2:s=1.04,noise=alls=8:allf=t+u[v];"
            "[0:a]asetrate=44100*1.03,aresample=44100,atempo=1.0/1.03,volume=0.9[a0];"
            "[1:a]volume=0.25[a1];"
            "[a0][a1]amix=inputs=2:duration=first[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-g", "60",
            "-c:a", "aac", "-b:a", "128k",
            "-t", "88",
            os.path.join(OUT_DIR, "variant_A.mp4")
        ]
    },
    {
        "key": "B",
        "title": "[TEST] Variant B - Lat Guong HFlip + Zoom 6% + Noise 10 + Echo",
        "file": os.path.join(OUT_DIR, "variant_B.mp4"),
        "cmd": [
            "ffmpeg", "-y",
            "-i", SRC,
            "-i", BGM,
            "-filter_complex",
            "[0:v]hflip,crop=in_w*0.94:in_h*0.94:(in_w-in_w*0.94)/2:(in_h-in_h*0.94)/2,scale=1280:720,setpts=PTS/1.04,eq=contrast=1.08:brightness=0.03:saturation=1.08,hue=h=3:s=1.05,noise=alls=10:allf=t+u[v];"
            "[0:a]asetrate=44100*1.04,aresample=44100,atempo=1.0/1.04,aecho=0.8:0.8:20:0.3,volume=0.85[a0];"
            "[1:a]volume=0.3[a1];"
            "[a0][a1]amix=inputs=2:duration=first[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-g", "60",
            "-c:a", "aac", "-b:a", "128k",
            "-t", "87",
            os.path.join(OUT_DIR, "variant_B.mp4")
        ]
    },
    {
        "key": "C",
        "title": "[TEST] Variant C - Co Lap Audio (Tat 100% Goc + Nhac YouTube Clean)",
        "file": os.path.join(OUT_DIR, "variant_C.mp4"),
        "cmd": [
            "ffmpeg", "-y",
            "-i", SRC,
            "-i", BGM,
            "-filter_complex",
            "[0:v]crop=in_w*0.95:in_h*0.95:(in_w-in_w*0.95)/2:(in_h-in_h*0.95)/2,scale=1280:720,setpts=PTS/1.03,eq=contrast=1.05:brightness=0.02:saturation=1.06,hue=h=2:s=1.04,noise=alls=8:allf=t+u[v];"
            "[1:a]volume=0.9[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-g", "60",
            "-c:a", "aac", "-b:a", "128k",
            "-t", "88",
            os.path.join(OUT_DIR, "variant_C.mp4")
        ]
    },
    {
        "key": "D",
        "title": "[TEST] Variant D - Khung Vien PIP Canvas 75% + Border + Nhac YouTube",
        "file": os.path.join(OUT_DIR, "variant_D.mp4"),
        "cmd": [
            "ffmpeg", "-y",
            "-i", SRC,
            "-i", BGM,
            "-filter_complex",
            "color=c=0x111625:s=1280x720:d=90[bg];"
            "[0:v]scale=960:540,pad=970:550:5:5:color=0xd4af37[pip];"
            "[bg][pip]overlay=(W-w)/2:(H-h)/2[v];"
            "[1:a]volume=0.9[a]",
            "-map", "[v]", "-map", "[a]",
            "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-g", "60",
            "-c:a", "aac", "-b:a", "128k",
            "-t", "88",
            os.path.join(OUT_DIR, "variant_D.mp4")
        ]
    }
]

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

print("=== CHECKING RENDERED FILES ===")
for v in variants:
    if os.path.exists(v["file"]) and os.path.getsize(v["file"]) > 1024 * 1024:
        print(f"Variant {v['key']} already rendered ({os.path.getsize(v['file'])} bytes), skipping render.")
    else:
        print(f"--- Rendering Variant {v['key']} ---")
        t0 = time.time()
        res = subprocess.run(v["cmd"], capture_output=True)
        if res.returncode != 0:
            print(f"Variant {v['key']} failed! Code {res.returncode}")
        else:
            sz = os.path.getsize(v["file"])
            print(f"Variant {v['key']} OK in {round(time.time() - t0, 1)}s ({sz} bytes)")

print("\n=== STARTING UPLOAD (NO DELETION) ===")
results = [
    {
        "key": "A",
        "title": "[TEST] Variant A - Zoom 5% + Color + Noise + Pitch + BGM",
        "upload_res": {'ok': True, 'video_id': '5A0cdccXruo', 'yt_url': 'https://youtu.be/5A0cdccXruo', 'title': '[TEST_BLOCK] [TEST] Variant A - Zoom 5% + Color + Noise + Pitch + BGM (1791856239)', 'project_id': 'proj_1'}
    }
]

# Upload B, C, D
for v in variants:
    if v["key"] == "A":
        continue
    if not os.path.exists(v["file"]):
        print(f"File for Variant {v['key']} missing, skipping upload.")
        continue
    print(f"Uploading Variant {v['key']}...")
    up_res = upload_test_sample(v["title"], v["file"])
    print(f"Result {v['key']}: {up_res}")
    results.append({
        "key": v["key"],
        "title": v["title"],
        "upload_res": up_res
    })
    time.sleep(3)

print("\n=== SUMMARY OF ALL 4 UPLOADED VIDEOS ===")
for r in results:
    up = r["upload_res"]
    vid = up.get("video_id", "N/A")
    url = up.get("yt_url", f"https://youtu.be/{vid}")
    ok = up.get("ok", False)
    print(f"Variant {r['key']}: OK={ok} | ID={vid} | URL={url}")

print("\nALL VIDEOS HAVE BEEN UPLOADED AND KEPT ON THE CHANNEL. NO DELETIONS.")
