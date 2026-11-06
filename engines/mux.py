"""
mux.py — STAGE cuối: ghép track lồng tiếng vào video -> output.mp4 (thuyết minh).

Kiểu thuyết minh: GIỮ video + GIỮ tiếng gốc nhưng hạ nhỏ, phủ giọng Việt lên trên.
Dùng ducking ĐỘNG (sidechaincompress): tiếng gốc chỉ tụt xuống KHI có giọng Việt,
hết câu lại lên -> nghe "pro", không bị lấn hẳn.

Nguồn audio lồng tiếng (ưu tiên từ trên xuống):
  1. Audio ngoài đã nhập   (manifest['dub'].source == 'imported' -> dub.<ext>)
  2. dub_fit.wav           (track đã KHỚP TIME - nên có sẵn từ bước ghép)
  3. tts.json              (chưa ghép -> tự ghép fit trước)

Chạy tay:
    python mux.py work/<job>
    python mux.py work/<job> --orig-vol 0.25   # tiếng gốc nhỏ hơn

Yêu cầu: ffmpeg (có sidechaincompress, amix - bản chuẩn đều có).
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from core.manifest import Manifest

STAGE = "mux"
_VIDEO_EXT = {".mp4", ".mkv", ".webm", ".mov"}


def _find_video(work_dir: Path, m: Manifest) -> Path | None:
    dl = m.stage("download") or {}
    vp = dl.get("video_path")
    if vp and Path(vp).exists():
        return Path(vp)
    cands = [c for c in sorted(work_dir.glob("source.*")) if c.suffix.lower() in _VIDEO_EXT]
    return cands[0] if cands else None


def _pick_dub(work_dir: Path, m: Manifest) -> Path:
    """Chọn track lồng tiếng: audio ngoài > dub_fit.wav > (tự ghép fit)."""
    dub = m.data.get("dub")
    if dub and dub.get("source") == "imported":
        p = work_dir / dub["file"]
        if p.exists():
            return p
    fit = work_dir / "dub_fit.wav"
    if fit.exists():
        return fit
    # chưa ghép -> ghép khớp time bây giờ
    if (work_dir / "tts.json").exists():
        from engines.assemble import assemble_fit
        assemble_fit(work_dir)
        if fit.exists():
            return fit
    raise RuntimeError("Không có nguồn audio (nhập audio ngoài hoặc tạo giọng trước).")


def _has_audio(path: Path) -> bool:
    """Video gốc có luồng audio không (để biết có ducking được không)."""
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
             "stream=index", "-of", "csv=p=0", str(path)],
            check=True, capture_output=True, text=True,
        )
        return bool(out.stdout.strip())
    except Exception:  # noqa: BLE001
        return False


def run_mux(work_dir: str | Path, orig_vol: float = 0.35,
            out_name: str = "output.mp4", force: bool = False) -> dict:
    work_dir = Path(work_dir)
    m = Manifest(work_dir)

    if m.is_done(STAGE) and not force:
        st = m.stage(STAGE)
        if st and Path(st.get("output", "")).exists():
            print(f"[skip] Đã render: {st['output']}")
            return st

    video = _find_video(work_dir, m)
    if not video:
        raise RuntimeError("Không tìm thấy video nguồn.")
    dub = _pick_dub(work_dir, m)
    out = work_dir / out_name

    m.mark_running(STAGE)
    try:
        if _has_audio(video):
            # Giữ tiếng gốc (nhỏ) + duck động dưới giọng Việt + trộn.
            from engines.media_ts import AUDIO_TS_FIX
            filt = (
                f"[0:a]{AUDIO_TS_FIX},volume={orig_vol}[bg];"
                f"[bg][1:a]sidechaincompress=threshold=0.015:ratio=8:attack=15:release=350[dk];"
                f"[dk][1:a]amix=inputs=2:duration=first:normalize=0[a]"
            )
            cmd = ["ffmpeg", "-y", "-i", str(video), "-i", str(dub),
                   "-filter_complex", filt, "-map", "0:v:0", "-map", "[a]",
                   "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(out)]
        else:
            # Video không có tiếng -> chỉ gắn giọng Việt
            cmd = ["ffmpeg", "-y", "-i", str(video), "-i", str(dub),
                   "-map", "0:v:0", "-map", "1:a:0", "-shortest",
                   "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", str(out)]
        print(f"[mux] video={video.name} + dub={dub.name} (tiếng gốc {int(orig_vol*100)}%)...")
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        err = (e.stderr or b"").decode("utf-8", "ignore")[-500:]
        m.mark_failed(STAGE, err)
        raise RuntimeError(f"ffmpeg lỗi: {err}") from e
    except Exception as e:  # noqa: BLE001
        m.mark_failed(STAGE, e)
        raise

    size = out.stat().st_size
    result = m.mark_done(STAGE, output=str(out), dub_source=dub.name,
                         orig_vol=orig_vol, size=size)
    print(f"[ok] Render xong: {out} ({size // 1_000_000}MB)")
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Stage cuối — ghép lồng tiếng vào video.")
    ap.add_argument("work_dir")
    ap.add_argument("--orig-vol", type=float, default=0.35,
                    help="Âm lượng tiếng gốc (0-1). Nhỏ hơn = thuyết minh rõ hơn.")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args(argv)
    run_mux(args.work_dir, orig_vol=args.orig_vol, force=args.force)


if __name__ == "__main__":
    main()
