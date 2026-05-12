### Bugfix / Small Change Checklist

> Áp dụng cho mọi bugfix hoặc thay đổi nhỏ. Claude phải làm việc như senior developer.

1. Đọc [workflow.md](workflow.md) → chọn workflow phù hợp
2. Tìm implementation hiện tại liên quan đến vấn đề
3. Xác định nguồn gốc dữ liệu/giá trị: UI, DB, file, metadata, config, resx, timezone, formatter, import/export, business logic
4. Phân tích root cause + phạm vi ảnh hưởng
5. Nhiều hướng sửa → liệt kê options, chọn hướng ít rủi ro nhất
6. **Không** dùng blind global replace
7. **Không** refactor ngoài phạm vi yêu cầu
8. Sau khi sửa → chạy build/test phù hợp nếu có
9. Báo cáo cuối (ngắn gọn): workflow đã dùng, root cause, files đã sửa, verify/test result, rủi ro còn lại
