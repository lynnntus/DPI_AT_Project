# Coding Rules

## Automation Pattern (Target)

> **Note:** Đây là pattern MỤC TIÊU cho code mới và cải thiện. Code hiện tại (v1.0.0) chưa implement đầy đủ — xem "Current State" bên dưới.

**Wait → Detect → Act → Verify**

Giả định: UI lag, tọa độ thay đổi theo resolution, element có thể không truy cập trực tiếp.

- LUÔN thêm delay (`time.sleep()` / `pyautogui.pause`)
- Ưu tiên `locateOnScreen(confidence=...)` thay vì hardcode tọa độ
- Retry loop + timeout + fallback cho mọi thao tác UI
- Xử lý unexpected states (popup, loading, fail)

### Current State (v1.0.0)

Actual pattern: **Sleep → Act → Sleep → Next**

| Aspiration | Actual |
|-----------|--------|
| `locateOnScreen(confidence=...)` | Hardcoded pixel coordinates (TopLeft/BottomRight) |
| Retry loop + timeout | Không có — mỗi action chạy 1 lần |
| Failure handling | Exception → script fail ngay lập tức |
| Wait for element | `time.sleep(delay)` cố định |

Xem `docs/runtime_flow.md` để biết chi tiết flow thực tế.

## Verification & Refinement

Mỗi script PHẢI đạt 4 tiêu chí trước khi finalize:

| Tiêu chí | Câu hỏi kiểm tra |
|----------|-------------------|
| Correctness | Đạt mục tiêu đề ra? |
| Stability | Fail nếu UI chậm / resolution khác? |
| Edge cases | Element not found, wrong screen, popup? |
| Repeatability | Chạy nhiều lần vẫn ổn định? |

**KHÔNG finalize nếu**: flaky, thiếu error handling cơ bản.

→ Phát hiện issue → fix → re-check → lặp đến khi stable.
