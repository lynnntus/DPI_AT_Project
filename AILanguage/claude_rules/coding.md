# Coding Rules

## Automation Pattern

**Wait → Detect → Act → Verify**

Giả định: UI lag, tọa độ thay đổi theo resolution, element có thể không truy cập trực tiếp.

- LUÔN thêm delay (`time.sleep()` / `pyautogui.pause`)
- Ưu tiên `locateOnScreen(confidence=...)` thay vì hardcode tọa độ
- Retry loop + timeout + fallback cho mọi thao tác UI
- Xử lý unexpected states (popup, loading, fail)

## Verification & Refinement

Mỗi script PHẢI đạt 4 tiêu chí trước khi finalize:

| Tiêu chí | Câu hỏi kiểm tra |
|----------|-------------------|
| Correctness | Đạt mục tiêu đề ra? |
| Stability | Fail nếu UI chậm / resolution khác? |
| Edge cases | Element not found, wrong screen, popup? |
| Repeatability | Chạy nhiều lần vẫn ổn định? |

**KHÔNG finalize nếu**: flaky, thiếu retry, thiếu failure handling.

→ Phát hiện issue → fix → re-check → lặp đến khi stable.
