# Jira Rules

## Status Flow

`To Do` → `In Progress` → `In Review` → `Done`

Bug phát hiện → tạo issue mới, link tới task gốc.

## Required Fields

| Field | Bắt buộc | Ghi chú |
|-------|----------|---------|
| Summary | Yes | Tiêu đề ngắn gọn |
| Description | Yes | Markdown |
| Assignee | Yes | |
| Priority | Yes | High / Medium / Low |
| Labels | No | automation, ocr, ui... |
| Fix Version | No | |

## Comments

- Cập nhật tiến độ qua comment, không chỉnh description
- Format: `[YYYY-MM-DD] Nội dung`
- Link PR/commit nếu có

## Link Types

| Loại | Khi nào |
|------|---------|
| `Blocks` | A chặn B |
| `Relates to` | Liên quan, không phụ thuộc |
| `is caused by` | Bug do task khác gây ra |
