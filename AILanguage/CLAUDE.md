# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Team

- **Owner**: Lynn Nguyen
- **Group**: vnsqa
- **Role**: Senior QA Automation Engineer

## Quick Start

```bash
.venv\Scripts\python.exe main.py                    # Chạy app
.venv\Scripts\pip.exe install -r requirements.txt    # Cài dependencies
```

## Build (.exe)

```bash
.venv\Scripts\pyinstaller.exe --onefile --noconsole main.py
```

Output: `dist/main.exe` | Troubleshooting: Missing DLL → VC++ Redist, AV block → whitelist, Tesseract → `C:\Program Files\Tesseract-OCR\tesseract.exe`

## Rules Index

| File | Mục đích | Khi nào đọc |
|------|----------|-------------|
| [architecture.md](claude_rules/architecture.md) | Layer diagram, key concepts, tech stack | Hiểu cấu trúc project |
| [coding.md](claude_rules/coding.md) | Automation pattern, verification & refinement | Implement / review code |
| [workflow.md](claude_rules/workflow.md) | Mandatory rules, core workflow, task flow | Bắt đầu task mới |
| [jira.md](claude_rules/jira.md) | Status flow, fields, comments, links | Tương tác Jira |
| [confluence.md](claude_rules/confluence.md) | Page format, test report template | Tạo/cập nhật docs |
| [crm.md](claude_rules/crm.md) | Issue template, 5 Whys, translation | Viết bug report |
| [prompt_guidelines.md](claude_rules/prompt_guidelines.md) | Prompt format, anti-patterns | Tối ưu prompt |
