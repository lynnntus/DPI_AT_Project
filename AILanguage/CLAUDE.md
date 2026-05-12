# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Team

- **Owner**: Lynn Nguyen
- **Group**: vnsqa
- **Role**: Senior QA Automation Engineer

## Project Overview

**DPI Automation Tool** (v1.0.0) — Desktop QA automation framework để test UI của hệ thống Display Product Inspection (DPI) của Koh Young Technology.

Chức năng chính:
- Tạo automation scripts bằng cách ghi tọa độ click, keystroke, hotkey, scroll, OCR check points
- Chạy scripts tự động qua pyautogui (ẩn app, countdown 5s, drive target application)
- OCR validate UI text — chụp vùng màn hình, chạy Tesseract (English/Chinese/Japanese), so sánh kết quả
- Excel loop — duyệt dòng Excel, fill form fields theo column mapping
- Report kết quả — pass/fail per script, export Excel report OCR results

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

## Architecture Summary

```
main.py → ScriptRunnerApp (Tkinter)
  ├── Script List tab → ui_script_list.py → ui_editor.py → ui_runner.py
  ├── Check List tab  → ui_check_list.py → ui_check_editor.py / import_dialog.py
  ├── About Us tab    → about_us.py
  └── Setting tab     → (inline in main.py)

Data:     scripts.json, check_items.json, settings.csv
Managers: script_manager.py, check_item_manager.py, setting_manager.py
Shared:   utils.py (paths, helpers, logging)
OCR:      ui_runner.py → pytesseract → CapturedImg/ + Result/
```

## Module Map

| File | Vai trò | Ghi chú |
|------|---------|---------|
| `main.py` | Entry point, Tkinter sidebar, tab routing | Class `ScriptRunnerApp` |
| `utils.py` | Path constants, shared utilities | `BASE_DIR`, `init_logging()`, `show_click_indicator()` |
| `script_manager.py` | CRUD scripts.json | Stateless functions, quản lý `script_order` |
| `check_item_manager.py` | Load/save check_items.json | Class `CheckItemManager` |
| `setting_manager.py` | Load/save settings.csv | Class `SettingManager` |
| `ui_script_list.py` | Script list tab — treeview, checkboxes, actions | Run selected, test report, move up/down |
| `ui_runner.py` | **Core engine** — chạy scripts, OCR capture | `run_script()`, `do_action()`, `capture_check_region()` |
| `ui_editor.py` | Script editor dialog — thêm/sửa actions | `open_script_editor_window()`, recursive guard |
| `ui_check_list.py` | Check list tab — quản lý OCR items | Filter, Get XY Position (F5/F6) |
| `ui_check_editor.py` | Check item editor dialog | Validate coordinates |
| `import_dialog.py` | Import check items từ Excel | Sheet "Chinese"/"Japanese", column mapping |
| `about_us.py` | About Us tab | Version, developer info |

## Key Data Flows

### Script Execution
```
ui_script_list.py:on_run_selected() → 5s countdown → hide window
  → ui_runner.py:run_script(actions, ...) → iterate actions
    → do_action(): click/type/hotkey/scroll/check/run_script/cmd_run
    → nếu có pre-loop/post-loop: đọc Excel, lặp actions cho mỗi row
  → check OCR results → save Result/*.xlsx → mark_pass/mark_fail
```

### OCR Check
```
do_action(type="check") → capture_check_region(check_item, timestamp_folder)
  → PIL.ImageGrab.grab(bbox) → save JPEG to CapturedImg/
  → pytesseract.image_to_string(lang=eng|chi_sim|jpn)
  → return {Label_ID, Expected, Detected, Match: ✅/❌, ImagePath}
```

### Excel Loop
```
pre-loop action → mở Excel file (openpyxl)
  → iterate rows → mỗi row: chạy enclosed actions
    → type action với excel_col → đọc cell value từ row
post-loop action → kết thúc loop
```

## Data Files

| File | Format | Nội dung |
|------|--------|---------|
| `scripts.json` | JSON | 9 scripts + script_order, mỗi script có actions array |
| `check_items.json` | JSON | 2,399 OCR check items (801 EN, 799 CN, 799 JP) |
| `settings.csv` | CSV | resolution, start_app, delay |
| `Result/*.xlsx` | Excel | OCR result reports (Label_ID, Expected, Detected, Match, ImagePath) |
| `CapturedImg/` | JPEG | Screenshots vùng OCR, organized by timestamp folder |
| `Log/` | Text | Daily log files (YYYYMMDD.log) |

## Standalone Files (không thuộc main app)

| File | Mục đích | Lưu ý |
|------|----------|-------|
| `check_label.py` | Standalone OCR test | Dùng pywinauto (không có trong main app) |
| `testocr.py` | PaddleOCR experiment cho Japanese | PaddleOCR, không phải Tesseract |
| `mouse_tracker.py` | Track mouse position mỗi 5s | Standalone utility, dùng pynput |
| `Label_test.py` | Early prototype ScriptRunnerApp | Legacy, không import |
| `test.py` | Ad-hoc pyautogui demo | Reference snippet |

## Rules Index

| File | Mục đích | Khi nào đọc |
|------|----------|-------------|
| [architecture.md](claude_rules/architecture.md) | Layer diagram, key concepts, tech stack | Hiểu cấu trúc project |
| [coding.md](claude_rules/coding.md) | Automation pattern, verification & refinement | Implement / review code |
| [workflow.md](claude_rules/workflow.md) | Mandatory rules, core workflow, task flow | Bắt đầu task mới |
| [stability.md](claude_rules/stability.md) | **Rules bảo vệ code, roadmap cải thiện** | **Trước khi sửa bất kỳ code nào** |
| [jira.md](claude_rules/jira.md) | Status flow, fields, comments, links | Tương tác Jira |
| [confluence.md](claude_rules/confluence.md) | Page format, test report template | Tạo/cập nhật docs |
| [crm.md](claude_rules/crm.md) | Issue template, 5 Whys, translation | Viết bug report |
| [ocr.md](claude_rules/ocr.md) | **OCR config, language, matching, evidence rules** | **Sửa OCR pipeline** |
| [prompt_guidelines.md](claude_rules/prompt_guidelines.md) | Prompt format, anti-patterns | Tối ưu prompt |
| [ai_workflow.md](claude_rules/ai_workflow.md) | **AI coding workflow, stability, investigation rules** | **Mọi task — đọc trước khi bắt đầu** |

## AI Workflow Rules (Quick Reference)

> Chi tiết đầy đủ: [ai_workflow.md](claude_rules/ai_workflow.md) — **đọc trước khi bắt đầu mọi task**

| # | Rule | Key Point |
|---|------|-----------|
| 1 | **Investigation First** | Không assume root cause. Check reflog, runtime, branches, pyc cache. Screenshot evidence > grep |
| 2 | **Minimal Change Policy** | Edit (patch) only. Không rewrite file. Không refactor/cleanup ngoài scope |
| 3 | **Approval Before Write** | Report file, function, scope, risk trước khi sửa. Large patch cần explicit approval |
| 4 | **Phase Isolation** | Investigate → Plan → Implement → Test. Không merge phases. Không mix feature + refactor |
| 5 | **Regression Safety** | Preserve existing behavior. Thêm mới OK, đổi/xóa cũ cần approval |
| 6 | **Import/Export Conventions** | TSV (UTF-8 BOM) = primary DRM-safe format. Excel = convenience. Round-trip guarantee |
| 7 | **Token Efficiency** | Patch nhỏ, reuse code, targeted reads. Không generate large rewrites |
| 8 | **Runtime Verification** | Verify widget/behavior tại runtime. Source reading alone = insufficient |
| 9 | **AI Coding Workflow** | 6-step: Investigate → Report → Propose → Approve → Implement → Verify. Không skip |
| 10 | **Desktop Utility Stability** | Stability > architecture. Simple > clever. No unnecessary patterns/frameworks |

### Standard Workflow (mọi task)

```
Step 1: INVESTIGATE  → đọc code, git history/reflog, thu thập evidence
Step 2: REPORT       → báo cáo findings + assumptions + uncertainty
Step 3: PROPOSE      → đề xuất solutions (scope, risk, effort)
Step 4: APPROVE      → user chọn solution, confirm scope
Step 5: IMPLEMENT    → minimal patches, phase isolation
Step 6: VERIFY       → tests + runtime verify + regression check
```

Bugfix/small change: before editing code, read and follow [`claude_rules/bugfix-small-change.md`](claude_rules/bugfix-small-change.md).
