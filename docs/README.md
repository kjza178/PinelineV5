# PinelineV4 — tài liệu dự án

(Port từ V2; docs lịch sử vẫn nhắc path/cổng V2 ở một số file cũ.) Project **không dùng git** → markdown trong `docs/` là nguồn lịch sử duy nhất. Mọi thay đổi (code, config, quy trình, quyết định của user) đều phải ghi lại ở đây — xem rule `.cursor/rules/docs-on-change.mdc`.

## Đọc gì trước

| File | Nội dung | Khi nào cập nhật |
|---|---|---|
| [STATE.md](./STATE.md) | **Hiện trạng**: dịch vụ đang chạy, job, cấu hình mặc định, việc còn treo, ràng buộc vận hành | Mỗi khi trạng thái thay đổi (job mới/xong, service restart, mặc định đổi) |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Kiến trúc: tiến trình, cổng, pipeline, bản đồ module, dữ liệu, thứ tự ưu tiên config | Khi thêm/bỏ module, đổi luồng dữ liệu, đổi cách khởi động |
| [RUNBOOK.md](./RUNBOOK.md) | Vận hành: khởi động/restart, script chẩn đoán, backup, xử lý sự cố thường gặp | Khi có lệnh/quy trình mới |
| [DECISIONS.md](./DECISIONS.md) | Quyết định của user (đã chọn gì, bác bỏ gì, vì sao) | Mỗi khi user chọn phương án |
| [CHANGELOG.md](./CHANGELOG.md) | Nhật ký thay đổi code/config theo ngày (mới nhất trên cùng) | **Mỗi lần sửa code/config** |
| [worklog/](./worklog/) | Nhật ký phiên làm việc theo ngày: yêu cầu → đã làm → kết quả | Mỗi phiên làm việc |
| [fixes/](./fixes/) | Fix log từng bug (root cause + cách recheck) — rule `fix-log-markdown.mdc` | Mỗi lần sửa bug |
| [reviews/](./reviews/) | Báo cáo review code | Mỗi lần review |
| [superpowers/](./superpowers/) | Spec/plan/report các đợt phát triển lớn (9/2026) | Theo đợt |
| [design/](./design/) | Research/design chưa implement | Khi khảo sát kiến trúc / migration |
| [MANIFEST_CONTRACT.md](./MANIFEST_CONTRACT.md) | Manifest vs films.db — field nào đọc/ghi đâu | Khi đổi ownership metadata / queue listing |
| [LAYOUT.md](./LAYOUT.md) | Bố cục thư mục Phase F+unity (app core 10 `.py`; packages live) | Khi đổi folder / import policy |
| [design/2026-11-04-v5-structure-unity.md](./design/2026-11-04-v5-structure-unity.md) | Unity decision: docs + xoá TARGET shells | Khi đổi khung pineline/ |
| [superpowers/plans/2026-11-04-v5-codebase-cleanup.md](./superpowers/plans/2026-11-04-v5-codebase-cleanup.md) | Plan làm gọn V5 (sau 3-auditor cross-check) | Khi thực thi / cập nhật phase cleanup |

Tài liệu cũ: `docs/archive_root/` (nếu còn), `scripts/install/INSTALL.md` (cài máy mới). `PROJECT_STATE.md` ở gốc (nếu còn) chỉ trỏ về `docs/STATE.md`.

## Quy ước ghi

- Ngày giờ theo giờ máy (UTC+7), dạng `YYYY-MM-DD HH:MM`.
- Ghi **file + hàm** bị đổi, **vì sao**, **cách kiểm tra lại**, và **có cần restart gì không** (server :8804 / sidecar :8802 / không).
- Không ghi secret (API key, OAuth client secret, token, cookie, mật khẩu proxy). Chỉ ghi tên biến/tên file.
- Thay đổi chưa có hiệu lực (chờ restart) → ghi rõ trong `STATE.md` mục *Chờ restart*.
