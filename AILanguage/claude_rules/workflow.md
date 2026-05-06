# Workflow

## Mandatory Rules

1. **Screenshot comparison** — so sánh screen với bản gốc sau mỗi thay đổi UI
2. **Code refinement** — tinh chỉnh code sau mỗi lần build

## Core Workflow

```
Hiểu objective → Xác định UI/behavior → Thiết kế steps → Implement → Verify → Detect flakiness → Refine (≥99% confidence)
```

## Task Flow

```
Jira Task → Phân tích → Implement → Test → Confluence docs → Update Jira
```

## Development Process (Bắt buộc)

> Áp dụng cho MỌI task: code mới, fix bug, refactor. Không được bỏ bước.

### 9 Steps

#### 1. Phân tích yêu cầu
- Hiểu rõ task/bug
- Xác định affected files/functions
- Xác định root cause trước khi sửa

#### 2. Đề xuất giải pháp (nếu thay đổi có rủi ro)
- Nêu các phương án + ưu/nhược điểm
- Khuyến nghị phương án
- **Chờ user approve** nếu thay đổi lớn hoặc ảnh hưởng nhiều module

#### 3. Code fix
- Sửa đúng root cause
- Không refactor lớn nếu không cần
- Giữ backward compatibility

#### 4. Unit Test
- Chạy/tạo test nhỏ cho logic đã sửa nếu phù hợp
- Nếu fail → fix tiếp

#### 5. Integration Test
- Test flow liên quan giữa các module
- Verify data truyền giữa các bước đúng

#### 6. System / E2E Test
- Chạy app như user thật nếu có thể
- Verify output thực tế (vd: file report tạo đúng folder)

#### 7. Regression Test
- Đảm bảo behavior cũ không bị hỏng

#### 8. Fix loop
- Nếu test fail → quay lại sửa → lặp đến khi pass

#### 9. Báo cáo cuối

**Chỉ được ghi DONE khi đã**: sửa xong code, chạy test liên quan, verify output thực tế, không còn lỗi blocking.

Báo cáo bắt buộc gồm:

| Mục | Nội dung |
|-----|---------|
| Root cause | Nguyên nhân gốc |
| Files đã sửa | Danh sách file + dòng/logic đã sửa |
| Unit test result | Pass/Fail/N/A |
| Integration test result | Pass/Fail/N/A |
| System/E2E test result | Pass/Fail/N/A |
| Regression check | Behavior cũ còn hoạt động không |
| Cách user test lại | Hướng dẫn cụ thể |
| Lỗi còn tồn tại | Liệt kê nếu có |

### Conclusion (bắt buộc cuối mỗi task)

| Status | Điều kiện |
|--------|-----------|
| **DONE** | Đã sửa + test pass + verify output thực tế |
| **PARTIAL** | Chưa test đủ hoặc còn lỗi non-blocking |
| **FAILED** | Không sửa được hoặc còn lỗi blocking |

**Không được báo DONE nếu chưa chạy test hoặc chưa verify output thực tế.**
