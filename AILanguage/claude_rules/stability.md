# Stability Rules

## Nguyên tắc bắt buộc

### 1. Không refactor lớn nếu chưa được yêu cầu
- Không restructure modules, không tách/gộp files
- Không thay đổi class hierarchy hoặc design pattern
- Chỉ sửa code khi có yêu cầu cụ thể hoặc fix bug rõ ràng

### 2. Không đổi tên file/function đang được dùng
- 11 core files đều đang active và import lẫn nhau
- Function names trong `ui_runner.py`, `script_manager.py` là internal API
- Đổi tên = phá vỡ toàn bộ import chain

### 3. Không thay đổi format Excel/report nếu chưa xác nhận
- `Result/*.xlsx`: columns `Label_ID, Expected, Detected, Match, ImagePath`
- `check_items.json`: keys `Lang, TC No., Word(resx), Content, Priority, TopLeft (x/y), BottomRight (x/y)`
- `scripts.json`: structure `{"scripts": {...}, "script_order": [...]}`
- `settings.csv`: fields `resolution, start_app, delay`

### 4. Backward compatibility là ưu tiên số 1
- Mọi thay đổi phải tương thích với data hiện có (2,399 check items, 9 scripts)
- Không đổi key names trong JSON/CSV
- Không đổi function signatures đang được gọi từ module khác
- Thêm field mới phải có default value

### 5. Mỗi thay đổi phải nhỏ, rõ mục tiêu, dễ rollback
- 1 commit = 1 mục tiêu rõ ràng
- Không bundle nhiều thay đổi không liên quan
- Test trước khi commit

### 6. Không xóa file/code mà chưa xác nhận
- Legacy files (`check_label.py`, `testocr.py`, `Label_test.py`, `test.py`, `mouse_tracker.py`) giữ nguyên
- Commented-out code giữ nguyên cho đến khi owner xác nhận

---

## Rủi ro refactor không có kế hoạch

| Rủi ro | Hậu quả |
|--------|---------|
| Đổi key names trong JSON/CSV | Mất 2,399 check items + 9 scripts |
| Thay đổi function signatures trong ui_runner.py | Phá vỡ ui_script_list.py |
| Đổi cấu trúc Excel import | Phá vỡ import_dialog.py (sheet names, column positions cố định) |
| Thay đổi resolution logic | Invalidate toàn bộ pixel coordinates |
| Restructure file layout | Phá vỡ main.spec + dist/main.exe build |
| Đổi scripts.json format | Cần data migration cho scripts đã tạo |

---

## Roadmap Cải Thiện

> Chi tiết đầy đủ: [`docs/stabilization_plan.md`](../docs/stabilization_plan.md)

| Phase | Mục tiêu | Status |
|-------|----------|--------|
| 1 | Document Current Behavior | ✅ Done |
| 2 | Stabilize OCR/Compare | Pending |
| 3 | Excel/Report | Pending |
| 4 | Maintainability | Pending |
