# Máy mới (RTX 5060 Ti) — cài GÌ ngoài file zip

Zip **chỉ có code**. Phải cài thêm phần dưới. Driver NVIDIA trên 5060 Ti phải **mới** (Blackwell).

---

## Bắt buộc (không có là không chạy)

| Cái | Để làm gì | Ghi chú |
|-----|-----------|---------|
| **NVIDIA Driver** mới | CUDA / NVENC | `nvidia-smi` ra GPU. 50-series cần driver mới. |
| **Python 3.11 hoặc 3.12** | 64-bit, tick **Add to PATH** | https://python.org — không dùng Store 3.13 nếu chưa test. |
| **FFmpeg** | tách audio, render, lật video | `winget install Gyan.FFmpeg` rồi **mở lại** CMD. Gõ `ffmpeg -version`. |
| **Ollama** | bước **Dịch** (Gemma) | https://ollama.com |

Sau khi có Ollama:

```bat
ollama pull gemma4
ollama pull gemma3:12b
```

(lần đầu vài GB). Pineline dịch nháp = gemma4, soát = gemma3:12b.

**Ổ trống:** ~25–40 GB (2 venv torch CUDA + model HF + Ollama).

---

## Cài Pineline (từ zip)

```bat
cd D:\Pineline
python install.py --gpu --cuda cu128
```

**5060 Ti = Blackwell → `--cuda cu128`**, đừng để mặc định `cu121` (dễ lỗi DLL/CUDA).

`install.py` tạo:

- `D:\pineline_env` — app, Whisper, Demucs, OCR, render  
- `D:\vieneu_env` — TTS VieNeu  

rồi ghi `pineline.config.json`.

Chạy: `dung-may-5060ti.bat` (áp CPU threads=2) hoặc `start.bat`.

---

## Bắt buộc nếu dùng Fun-ASR / Paraformer (engine mới)

`install.py` **không** cài FunASR. Sau khi env chính xong:

```bat
D:\pineline_env\Scripts\python.exe -m pip install funasr modelscope tiktoken jieba librosa soundfile
```

Rồi **khóa lại torch CUDA** (nếu `pip` kéo torch CPU):

```bat
install_funasr_safe.bat
```

Tốt hơn: sửa bat trỏ `PY=D:\pineline_env\Scripts\python.exe` rồi chạy — **đừng** `pip install --user` vào Python hệ thống.

Lần ASR Fun/Paraformer đầu: tự tải model HF (cần mạng, vài GB vào `HF_HOME`).

Whisper (`faster-whisper`) đã nằm trong `install.py` — không cần bước này nếu chỉ dùng Whisper.

---

## Tùy chọn

| Cái | Khi nào cần |
|-----|-------------|
| **OmniVoiceStudio** + venv | Engine TTS phụ. Điền `OMNI_PY` + `OMNI_CWD`. Không có vẫn chạy **VieNeu**. |
| Giọng mẫu `voices/` | Zip đã kèm wav clone. Thiếu thì clone lại trên máy mới. |
| `work/` job cũ | Zip **không** gồm. Copy tay nếu cần resume. |

---

## Không cần cài tay (tự có khi chạy)

- VieNeu-TTS v3-Turbo (HF, lần TTS đầu)  
- faster-whisper / RapidOCR / Demucs  
- yt-dlp (trong requirements)

---

## Checklist 30 giây

```
nvidia-smi
python --version
ffmpeg -version
ollama --version
ollama list          ← có gemma4 và gemma3:12b
```

Rồi `python install.py --gpu --cuda cu128` → `dung-may-5060ti.bat`.
