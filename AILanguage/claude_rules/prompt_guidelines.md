# Prompt Guidelines

## Nguyên tắc

- Nêu chính xác input + output mong muốn
- Cung cấp đủ context (file path, data mẫu)
- Kèm example khi pattern phức tạp
- Rút gọn nếu > 500 từ

## Format theo loại yêu cầu

| Loại | Format |
|------|--------|
| Phân tích | "Phân tích [X], trả về bảng: [cột 1], [cột 2]" |
| Tạo doc | "Tạo [loại] cho [chủ đề], format [docx/xlsx/pdf]" |
| Fix bug | "File [path] dòng [N]: [lỗi]. Expected: [X]. Actual: [Y]" |

## Anti-patterns

| Sai | Đúng |
|-----|------|
| "Sửa lỗi cho tôi" | "File main.py:42 TypeError khi gọi func(). Fix và giải thích" |
| "Làm đẹp code" | "Refactor hàm X trong file Y: tách logic, rename biến" |
| "Viết test" | "Unit test cho load_scripts(): empty, valid, corrupted JSON" |
