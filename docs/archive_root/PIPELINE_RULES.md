# QUY TẮC BẢO VỆ VÀ QUẢN LÝ TRẠNG THÁI PIPELINE (PINELINE V4)

Tài liệu này xác định các nguyên tắc thiết kế bất biến (Invariants) của hệ thống Pineline V4 để ngăn chặn hiện tượng chạy loạn tiến trình (race conditions), đảm bảo tính toàn vẹn dữ liệu và giúp việc gỡ lỗi (debug) trở nên minh bạch, đơn giản.

---

## 1. NGUYÊN TẮC BĂNG CHUYỀN TUẦN TỰ (SEQUENTIAL PIPELINE)

Một job xử lý video gồm 5 trạm chính chạy theo chuỗi phụ thuộc nghiêm ngặt:

$$\text{Download} \longrightarrow \text{ASR (Bóc chữ)} \longrightarrow \text{Translate (Dịch)} \longrightarrow \text{TTS (Lồng tiếng)} \longrightarrow \text{MUX (Hòa âm/Dựng)}$$

### Bảng Điều Kiện Tiên Quyết (Prerequisite Guards):

| Trạm (Stage) | Điều kiện tiên quyết để được phép chạy | Không được phép chạy khi (Blocked if) |
| :--- | :--- | :--- |
| **Download** | Không có | Job đang chạy Download |
| **ASR** | `download.status == 'done'` VÀ file `audio.wav`/`source.mp4` tồn tại | Download đang chạy / lỗi |
| **Translate**| `asr.status == 'done'` VÀ file `asr.json` tồn tại | ASR chưa xong hoặc đang chạy |
| **TTS** | `translate.status == 'done'` VÀ file `script.json` tồn tại | **CẤM CHẠY** nếu `translate` đang `running` hoặc `pending` |
| **MUX** | **BẮT BUỘC CẢ HAI**: `translate.status == 'done'` VÀ `tts.status == 'done'` | **CẤM CHẠY** nếu `translate` hoặc `tts` đang `running`/`pending` |

---

## 2. NGUYÊN TẮC RESET BẬC THANG (CASCADE RESET / INVALIDATION)

Khi một trạm bất kỳ $N$ bị reset hoặc chạy lại, **toàn bộ các trạm đứng sau nó ($N+1, N+2, ...$) BẮT BUỘC PHẢI BỊ VÔ HIỆU HÓA**:

1. **Khi chạy lại `Translate`**:
   * Trạng thái `tts` lập tức đổi thành `pending` (không được phép báo `done` của bản dịch cũ).
   * Trạng thái `mux` lập tức đổi thành `pending`.
   * Xóa file audio cũ dở dang để tránh ghép nhầm tiếng cũ.
2. **Khi chạy lại `ASR`**:
   * Trạng thái `translate`, `tts`, `mux` lập tức đổi thành `pending`.
3. **Khi chạy lại `Download`**:
   * Toàn bộ các bước sau bị hủy bỏ về `pending`.

---

## 3. CƠ CHẾ KHÓA ĐƠN THỰC THI (SINGLE STAGE MUTEX)

1. **Một job chỉ được phép có duy nhất MỘT stage ở trạng thái `running` tại một thời điểm**:
   * Tuyệt đối không cho phép `translate` và `mux` cùng `running`.
   * Trước khi `_run_stage` đánh dấu `mark_running(stage)`, hệ thống phải kiểm tra:
     ```python
     if _manifest_running(work_dir) and _manifest_running(work_dir) != stage:
         raise StageConflictError(f"Job đang chạy bước {_manifest_running(work_dir)}, không thể chạy song song bước {stage}")
     ```
2. **Subprocess Cleanup**:
   * Trước khi khởi động một engine mới, tiến trình cũ của cùng job (nếu còn sót lại dạng zombie) phải được kill sạch qua `_PROCS`.

---

## 4. QUY TRÌNH TỰ ĐỘNG CHỮA LỖI (SELF-HEAL STANDARD)

Khi Bác sĩ Watchdog (`agent_watch.py`) phát hiện job bị `failed` hoặc treo quá 30 phút:
1. **Khoanh vùng chính xác trạm lỗi**:
   * Không reset bừa bãi toàn bộ job.
   * Chỉ dọn rác các file tạm thuộc riêng trạm bị lỗi.
2. **Kích hoạt Fallback phù hợp**:
   * Nếu lỗi LLM (Timeout / Out of quota) ➔ Tự động chuyển `model` từ `local` sang `openclaw` (fallback).
   * Nếu lỗi CUDA OOM (Hết VRAM) ➔ Hạ kích thước batch hoặc giải phóng cache VRAM trước khi thử lại.
3. **Giới hạn số lần thử (Max Retries)**:
   * Mỗi stage chỉ được tự động thử lại tối đa 2 lần (`RUNWATCH_MAX_HEAL=2`). Nếu vẫn lỗi, dừng lại để người dùng can thiệp, tránh vòng lặp vô tận (Stuck Loop).

---

## 5. NHẬT KÝ HỘP ĐEN (JOB EVENT LOGGING)

Mỗi job trong `work/{job_id}/manifest.json` duy trì mảng `events` để dễ dàng kiểm tra lịch sử:
```json
"events": [
  {"time": "2026-10-18T22:00:00Z", "stage": "translate", "action": "started", "model": "local"},
  {"time": "2026-10-18T22:12:18Z", "stage": "mux", "action": "blocked", "reason": "Translate is still running"},
  {"time": "2026-10-18T22:31:00Z", "stage": "translate", "action": "completed", "segments": 8734}
]
```
Nhờ đó, khi mở giao diện lên người dùng hoặc lập trình viên có thể đọc ngay được chính xác điều gì đã xảy ra mà không cần mở terminal server.
