# Architecture

## Layer Diagram

```
UI Layer              →  Logic Layer           →  Data Layer
────────────────────     ───────────────────      ──────────────
main.py                  script_manager.py        scripts.json
ui_script_list.py        check_item_manager.py    check_items.json
ui_editor.py             setting_manager.py       settings.csv
ui_runner.py             utils.py                 Log/
ui_check_list.py
ui_check_editor.py
import_dialog.py
```

Entry point: `main.py` → `ScriptRunnerApp` (Tkinter sidebar navigation, tabs)

## Key Concepts

**Script** — Chuỗi action (`click`, `type`, `hotkey`, `scroll`, `check`, `run_script`, `cmd_run`). Gọi script khác được (guard chống đệ quy). Lưu `scripts.json`, thứ tự qua `script_order`.

**Check Item** — Mục tiêu OCR: ngôn ngữ + nội dung mong đợi + vùng màn hình (TopLeft/BottomRight). Runner chụp → Tesseract OCR → so sánh.

**Excel Loop** — `pre-loop`/`post-loop` duyệt dòng Excel, truyền cell vào `type` qua column mapping (A, B, C...).

## Code Patterns

- File paths: `utils.py` → `BASE_DIR` (exe dir hoặc script dir)
- Data: JSON (structured), CSV (flat settings)
- UI tabs: `create_*_tab(parent, ...)`
- Editor: `tk.Toplevel` + `transient()` + `grab_set()`
- Long ops: daemon threads
- OCR: `eng`, `chi_sim`, `jpn`

## Tech Stack

| Mục đích | Thư viện |
|----------|----------|
| GUI | Python 3 + Tkinter |
| Automation | pyautogui, keyboard, pynput |
| OCR | pytesseract + Pillow |
| Excel | pandas + openpyxl |

Tesseract OCR path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
