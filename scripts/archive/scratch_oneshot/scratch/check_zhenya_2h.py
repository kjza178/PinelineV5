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
RESULTS_FILE = Path(r"Z:\PinelineV2\scratch\zhenya_2h_uploads.json")

def get_file_duration(fpath: Path) -> float:
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(fpath)]
    p = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(json.loads(p.stdout)["format"]["duration"])
    except Exception:
        return 0.0

def cut_clip(src_file: Path, out_file: Path, start_sec: int, dur_sec: int = 90) -> bool:
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
        print(f"   [copy-failed: {e}], fallback re-encode...", flush=True)

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
    print("=" * 65, flush=True)
    print(f"🎬 KHO MẪU TEST BẢN QUYỀN MỖI 2 GIỜ CHO TẤT CẢ TẬP PHIM", flush=True)
    print(f"📁 Thư mục: {SOURCE_DIR}", flush=True)
    print("=" * 65, flush=True)

    # Liệt kê danh sách các mốc cần lấy mẫu
    tasks = []
    for f in files:
        dur = get_file_duration(f)
        dur_h = round(dur / 3600, 2)
        step = 7200 # 2 giờ = 7200 giây
        
        # Mốc đầu tiên tại 120s (2m)
        offsets = [0]
        cur = step
        while cur + 90 <= dur:
            offsets.append(cur)
            cur += step

        for off in offsets:
            start_s = 120 if off == 0 else off
            label = "Mốc 0h (phút thứ 2)" if off == 0 else f"Mốc {off // 3600}h"
            sample_title = f"镇压九天_{f.stem}_{label}"
            task_key = f"{f.name}___{label}"
            tasks.append({
                "key": task_key,
                "file": f,
                "dur": dur,
                "dur_h": dur_h,
                "start_s": start_s,
                "label": label,
                "title": sample_title
            })

    print(f"📋 Tổng cộng có {len(tasks)} mẩu clip cần test trên kênh YouTube:")
    for i, t in enumerate(tasks, 1):
        print(f"  {i:02d}. {t['file'].name} -> {t['label']} (bắt đầu từ giây {t['start_s']})")
    print("=" * 65 + "\n", flush=True)

    results = load_results()

    # Nhận diện mẩu đầu tiên đã upload trước đó nếu có
    first_upload_key = "[01] 1.mp4___Mốc 0h (phút thứ 2)"
    if first_upload_key not in results:
        prev_file = Path(r"Z:\PinelineV2\scratch\zhenya_uploads.json")
        if prev_file.is_file():
            try:
                prev_data = json.loads(prev_file.read_text(encoding="utf-8"))
                if "[01] 1.mp4" in prev_data and prev_data["[01] 1.mp4"].get("ok"):
                    results[first_upload_key] = {
                        "file": "[01] 1.mp4",
                        "label": "Mốc 0h (phút thứ 2)",
                        "start_s": 120,
                        "ok": True,
                        "video_id": prev_data["[01] 1.mp4"]["video_id"],
                        "yt_url": prev_data["[01] 1.mp4"]["yt_url"],
                        "project_id": prev_data["[01] 1.mp4"].get("project_id", ""),
                        "uploaded_at": prev_data["[01] 1.mp4"].get("uploaded_at", "")
                    }
                    save_results(results)
            except Exception:
                pass

    total = len(tasks)
    for idx, t in enumerate(tasks, 1):
        k = t["key"]
        print(f"\n[{idx:02d}/{total:02d}] 🎥 {t['file'].name} | {t['label']} (tại {t['start_s']}s)", flush=True)

        if k in results and results[k].get("ok"):
            print(f"   ⏭️ Đã upload: {results[k].get('yt_url')}", flush=True)
            continue

        sample_file = SAMPLE_DIR / f"{t['title']}_sample.mp4"
        print(f"   ✂️ Đang cắt mẫu 90 giây...", flush=True)
        ok = cut_clip(t["file"], sample_file, start_sec=t["start_s"], dur_sec=90)
        if not ok:
            print(f"   ❌ Không cắt được mẫu!", flush=True)
            results[k] = {"file": t["file"].name, "label": t["label"], "ok": False, "error": "Lỗi cắt video"}
            save_results(results)
            continue

        size_mb = round(sample_file.stat().st_size / (1024*1024), 2)
        print(f"   ✓ Đã cắt xong ({size_mb} MB). Đang upload lên YouTube (Unlisted)...", flush=True)

        up_res = test_channel.upload_test_sample(t["title"], str(sample_file))

        # Dọn dẹp file local ngay lập tức
        try:
            sample_file.unlink(missing_ok=True)
        except Exception:
            pass

        if not up_res.get("ok"):
            err = up_res.get("error", "Lỗi upload")
            print(f"   ❌ Upload thất bại: {err}", flush=True)
            results[k] = {"file": t["file"].name, "label": t["label"], "ok": False, "error": err}
            save_results(results)
        else:
            vid = up_res["video_id"]
            yt_url = up_res["yt_url"]
            proj_id = up_res.get("project_id", "")
            print(f"   ✅ Upload thành công ({proj_id}): {yt_url}", flush=True)
            results[k] = {
                "file": t["file"].name,
                "label": t["label"],
                "start_s": t["start_s"],
                "ok": True,
                "video_id": vid,
                "yt_url": yt_url,
                "project_id": proj_id,
                "uploaded_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            save_results(results)

        time.sleep(2)

    print("\n\n" + "=" * 65, flush=True)
    print("🎉 HOÀN THÀNH TOÀN BỘ CÁC MẪU 2 GIỜ CHO TẤT CẢ CÁC TẬP!", flush=True)
    print("Danh sách video trên kênh phụ YouTube để bạn tự check bản quyền:\n", flush=True)
    for k, v in results.items():
        if v.get("ok"):
            print(f"- {v.get('file')} [{v.get('label')}]: {v.get('yt_url')}", flush=True)
        else:
            print(f"- {v.get('file')} [{v.get('label')}]: ❌ {v.get('error')}", flush=True)
    print("=" * 65, flush=True)

if __name__ == "__main__":
    main()
