# Fine-tune LoRA giọng **Res** (VieNeu-TTS 0.3B)

Workspace: `Z:\VieNeu-TTS`  
Source audio: `Z:\Pineline\rvc_data\Res.wav`  
Output: `Z:\VieNeu-TTS\finetune\output\Res-LoRA-v1`

## Quan trọng

- Official LoRA chỉ hỗ trợ **VieNeu-TTS-0.3B**, **không** phải v3 Turbo của Pineline.
- Đổi tên folder/run_name **không** làm giọng hay hơn — chỉ nhãn. Chất lượng phụ thuộc audio + transcript.
- Dataset hiện tại: ~856 clip từ `Res.wav` (ASR Whisper).

## Train

- `Z:\Pineline\TRAIN_LORA_Res.bat` hoặc `finetune_xuyenthanh\TRAIN_LORA.bat`
  1. Train ngay (dataset đã encode)
  2. Cắt + ASR + encode + train lại
  3. Chỉ prepare
  4. Resume từ checkpoint

Log: `finetune_xuyenthanh\train_lora.log`

## Nghe thử

`finetune_xuyenthanh\03_test_lora.bat`
