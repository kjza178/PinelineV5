import os
import sys
import time
import json
import subprocess
from pathlib import Path

# Fix stdout encoding for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import test_channel

SOURCE_DIR = Path(r"Z:\bilibili_downloader\downloads\【1-10季】镇压九天！")
SAMPLE_DIR = Path(r"Z:\PinelineV2\data\samples\zhenya")
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_FILE = Path(r"Z:\PinelineV2\scratch\zhenya_uploads.json")

def cut_clip(src_file: Path, out_file: Path, start_sec: int = 120, dur_sec: int = 90) -> bool:
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-i", str(src_file),
        "-t", str(dur_sec),
        "-c", "copy",
        "-movflags", "+faststart",
        str(out_file)
    ]
    try:
        p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
        if p.returncode == 0 and out_file.is_file() and out_file.stat().st_size > 50000:
            return True
    except Exception as e:
        print(f"Copy stream failed ({e}), trying re-encode...", flush=True)

    # Fallback re-encode
    cmd_fb = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-i", str(src_file),
        "-t", str(dur_sec),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
        "-c:a", "aac", "-b:a", "96k",
        "-movflags", "+faststart",
        str(out_file)
    ]
    p2 = subprocess.run(cmd_fb, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    return p2.returncode == 0 and out_file.is_file() and out_file.stat().st_size > 0

def load_results():
    if RESULTS_FILE.is_file():
        try:
            with open(RESULTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_results(data):
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    files = sorted([f for f in SOURCE_DIR.iterdir() if f.is_file() and f.suffix.lower() == ".mp4"])
    print(f"=======================================================", flush=True)
    print(f"📁 Thư mục nguồn: {SOURCE_DIR}", flush=True)
    print(f"📋 Tìm thấy {len(files)} file video cần cắt mẫu và upload:", flush=True)
    for idx, f in enumerate(files, 1):
        print(f"   {idx}. {f.name} ({round(f.stat().st_size / (1024*1024*1024), 2)} GB)", flush=True)
    print(f"=======================================================\n", flush=True)

    results = load_results()

    for idx, file_path in enumerate(files, 1):
        fname = file_path.name
        print(f"\n[{idx}/{len(files)}] 🎬 Đang xử lý: {fname}", flush=True)

        if fname in results and results[fname].get("ok"):
            print(f"   ⏭️ Đã upload trước đó: {results[fname].get('yt_url')}", flush=True)
            continue

        sample_name = f"镇压九天_{file_path.stem}"
        sample_file = SAMPLE_DIR / f"{sample_name}_sample.mp4"

        print(f"   ✂️ Đang cắt mẫu 90 giây (từ phút thứ 2)...", flush=True)
        ok = cut_clip(file_path, sample_file, start_sec=120, dur_sec=90)
        if not ok:
            print(f"   ❌ Lỗi cắt mẫu video!", flush=True)
            results[fname] = {"ok": False, "error": "Cắt mẫu thất bại"}
            save_results(results)
            continue

        sample_mb = round(sample_file.stat().st_size / (1024*1024), 2)
        print(f"   ✓ Đã cắt mẫu ({sample_mb} MB)", flush=True)

        print(f"   📤 Đang upload mẫu lên YouTube (Unlisted)...", flush=True)
        up_res = test_channel.upload_test_sample(sample_name, str(sample_file))

        # Dọn dẹp file local ngay sau khi upload
        try:
            sample_file.unlink(missing_ok=True)
        except Exception:
            pass

        if not up_res.get("ok"):
            err = up_res.get("error", "Lỗi upload")
            print(f"   ❌ Upload thất bại: {err}", flush=True)
            results[fname] = {"ok": False, "error": err}
            save_results(results)
        else:
            vid = up_res["video_id"]
            yt_url = up_res["yt_url"]
            print(f"   ✅ Upload thành công: {yt_url}", flush=True)
            results[fname] = {
                "ok": True,
                "video_id": vid,
                "yt_url": yt_url,
                "project_id": up_res.get("project_id", ""),
                "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            save_results(results)

        time.sleep(2)

    print("\n\n=======================================================", flush=True)
    print("🎉 HOÀN TẤT UPLOAD TẤT CẢ CÁC TẬP!", flush=True)
    print("Danh sách video trên kênh phụ YouTube để bạn tự check bản quyền:\n", flush=True)
    for fname, data in results.items():
        if data.get("ok"):
            print(f"- {fname}: {data.get('yt_url')}", flush=True)
        else:
            print(f"- {fname}: ❌ {data.get('error')}", flush=True)
    print("=======================================================", flush=True)

if __name__ == "__main__":
    main()
