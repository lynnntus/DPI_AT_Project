# Confluence Rules

## Khi nào tạo page

- Feature hoàn thành → trang tài liệu
- Bug phức tạp → trang root cause analysis
- Sprint review → trang tổng kết

## Format

- Tiêu đề có prefix: `[Feature]`, `[Bug]`, `[Report]`
- Heading: H1 → H2 → H3 (không skip)
- Screenshot bắt buộc cho UI changes
- Table cho data có cấu trúc
- Link tới Jira issues liên quan

## Template — Test Report

```markdown
# [YYYY-MM-DD] Test Report — [Feature]

## Tóm tắt
Kết quả: PASS/FAIL | X passed / Y failed

## Chi tiết
| # | Test Case | Kết quả | Ghi chú |
|---|-----------|---------|---------|
| 1 | ...       | PASS    |         |

## Screenshots
[Đính kèm]

## Issues
- [JIRA-XXX] Mô tả
```
