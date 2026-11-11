# `pineline.server.routes.jobs`

[← Index](../generated/module-index.md) · [Brain home](../README.md)

<!-- AUTO:START — sinh bởi scripts/brain_build.py 2026-11-11 02:38. Đừng sửa tay khối này. -->
**File:** `pineline/server/routes/jobs.py` · **Lớp:** `misc` · **79 dòng** (68 code) · **1 hàm**, **0 class** · sha1 `381520cd4a`

> Jobs API: /api/jobs/* — LIVE registry trong khung pineline V5. Thân handler vẫn trong root `server.py` (xen helper). Module này chỉ đăng ký path → hàm trên `S`, để bản đồ API nằm trong `pineline/`.

### Phụ thuộc

- **Gọi tới (import nội bộ):** —
- **Được dùng bởi:** —
- **Test:** `tests/test_queue_http_state.py`
- **Thư viện ngoài:** `fastapi`

```mermaid
flowchart LR
  pineline_server_routes_jobs[[pineline.server.routes.jobs]]
```

### Hàm & class top-level

| Tên | Dòng | Dài | Tham số | Docstring |
|---|---:|---:|---|---|
| `attach` | 62 | 15 | `server_mod` | Gắn handler từ server module lên router; gọi trước include_router. |

### Lịch sử (từ docs/)

- **Fix logs (1):**
  - [V5: queue/jobs dual-route + queue_state đọc N lần](../../fixes/2026-11-04-v5-queue-ssot.md)
- **Reviews:** [_atoms_http_agents](../../reviews/_atoms_http_agents.md), [2026-11-06-v5-part-atoms](../../reviews/2026-11-06-v5-part-atoms.md), [2026-11-06-v5-func-catalog](../../reviews/2026-11-06-v5-func-catalog.md)
- Nhắc trong CHANGELOG: **0** lần · DECISIONS: **1** lần

<!-- AUTO:END -->

<!-- MANUAL:START -->
## Vai trò (viết tay)

_Chưa viết. 2–4 câu: module này chịu trách nhiệm gì trong pipeline, ai gọi nó, nó KHÔNG làm gì._

## Luồng chính

_Các hàm vào (entry) → bước chính → output/side effect. Ghi tên hàm thật._

## Bất biến & hợp đồng

_Điều luôn phải đúng (vd: chỉ ghi manifest qua `Manifest.update`; 1 job / ghế). Vi phạm = bug._

## Bẫy đã biết

_Lỗi từng gặp + link `docs/fixes/...`. Những chỗ dễ sửa sai._

## Ghi chú vận hành

_Config key quan trọng, cần restart gì khi sửa (:8801 / :8802 / hot-reload), cách test._
<!-- MANUAL:END -->
