# Architecture

## Module Map

```
┌─────────────────────────────────────────────────────────────────┐
│  UI Layer                                                       │
│  ┌──────────┐  ┌────────────────┐  ┌──────────────┐            │
│  │ main.py  │  │ui_script_list  │  │ui_check_list │            │
│  │(entry)   │  │    .py         │  │    .py       │            │
│  └────┬─────┘  └──────┬─────┬──┘  └──────┬───┬───┘            │
│       │               │     │             │   │                 │
│       │         ┌─────┘     │       ┌─────┘   │                │
│       │         v           │       v         v                 │
│       │  ┌────────────┐     │  ┌──────────┐ ┌───────────────┐  │
│       │  │ui_editor.py│     │  │ui_check_ │ │import_dialog  │  │
│       │  └────────────┘     │  │editor.py │ │    .py        │  │
│       │                     │  └──────────┘ └───────────────┘  │
│       │                     v                                   │
│       │              ┌─────────────┐   ┌──────────┐            │
│       │              │ui_runner.py │   │about_us  │            │
│       │              │(core engine)│   │   .py    │            │
│       │              └─────────────┘   └──────────┘            │
├─────────────────────────────────────────────────────────────────┤
│  Logic Layer                                                    │
│  ┌─────────────────┐ ┌───────────────────┐ ┌─────────────────┐ │
│  │script_manager.py│ │check_item_manager │ │setting_manager  │ │
│  │                 │ │       .py         │ │     .py         │ │
│  └────────┬────────┘ └────────┬──────────┘ └────────┬────────┘ │
│           │                   │                      │          │
│  ┌────────┴───────────────────┴──────────────────────┘          │
│  │                                                              │
│  │  utils.py  (paths, helpers, logging)                         │
│  └──────────────────────────────────────────────────────────────│
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                     │
│  ┌──────────────┐ ┌────────────────┐ ┌──────────────┐          │
│  │scripts.json  │ │check_items.json│ │settings.csv  │          │
│  └──────────────┘ └────────────────┘ └──────────────┘          │
│  ┌──────────────┐ ┌────────────────┐ ┌──────────────┐          │
│  │CapturedImg/  │ │Result/         │ │Log/          │          │
│  └──────────────┘ └────────────────┘ └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Dependency Map

### Import Chain (who imports whom)

```
main.py
  ├── script_manager       (load_scripts_and_order)
  ├── ui_runner             (create_run_script_tab_content)
  ├── ui_script_list        (create_script_list_tab)
  ├── setting_manager       (SettingManager)
  ├── check_item_manager    (CheckItemManager)
  ├── ui_check_list         (create_check_list_tab)
  ├── about_us              (show_about_us)
  └── utils                 (setting_path, check_items_path, init_logging)

ui_script_list.py
  ├── script_manager        (save_scripts_and_order, now_iso, mark_*)
  ├── ui_editor             (open_script_editor_window)
  ├── ui_runner             (run_script)
  └── utils                 (all_check_items_exist, beep)

ui_runner.py
  ├── pyautogui
  ├── pytesseract
  ├── PIL.ImageGrab
  ├── pandas
  └── utils                 (all_check_items_exist, clean_filename, beep, ocr_folder, result_folder, show_click_indicator, run_cmd_block)

ui_editor.py
  ├── pyautogui
  └── utils                 (all_check_items_exist, beep)

ui_check_list.py
  ├── ui_check_editor       (open_check_editor)
  ├── import_dialog          (open_import_dialog)
  ├── keyboard
  └── pyautogui

ui_check_editor.py          (no project imports)

import_dialog.py
  └── pandas

script_manager.py
  └── utils                 (scripts_path)

check_item_manager.py       (no project imports)

setting_manager.py          (no project imports)

utils.py                    (no project imports, only stdlib)
```

## Data Flow

### Write Paths (who saves what)

| Data File | Written By | When |
|-----------|-----------|------|
| `scripts.json` | `script_manager.save_scripts_and_order()` | Create/update/delete/copy script, mark status |
| `check_items.json` | `check_item_manager.save_check_items()` | Create/update/delete check item, import, position capture |
| `settings.csv` | `setting_manager.save_settings()` | Save settings from Setting tab |
| `Result/*.xlsx` | `ui_runner.run_script()` | After script execution with OCR results |
| `CapturedImg/ocr_*/*.jpg` | `ui_runner.capture_check_region()` | During OCR check action |
| `Log/YYYYMMDD.log` | Python `logging` module | Throughout execution |

### Read Paths (who loads what)

| Data File | Read By | When |
|-----------|---------|------|
| `scripts.json` | `script_manager.load_scripts_and_order()` | App start |
| `check_items.json` | `check_item_manager.load_check_items()` | App start |
| `settings.csv` | `setting_manager.load_settings()` | App start |
| Excel test data | `ui_runner.run_script()` via `pd.read_excel` | pre-loop action |
| Excel import file | `import_dialog.import_data()` via `pd.ExcelFile` | Import check items |

## Key Classes and Functions

### Classes

| Class | File | Responsibility |
|-------|------|----------------|
| `ScriptRunnerApp` | `main.py` | Root app, sidebar navigation, tab routing, holds all managers |
| `SettingManager` | `setting_manager.py` | Load/save settings.csv |
| `CheckItemManager` | `check_item_manager.py` | Load/save check_items.json |
| `_ScriptStepError` | `ui_runner.py` | Structured error for failed automation steps |

### Critical Functions

| Function | File | Purpose |
|----------|------|---------|
| `run_script()` | `ui_runner.py` | Core automation engine, iterates actions |
| `do_action()` | `ui_runner.py` | Executes single action (click/type/check/...) |
| `capture_check_region()` | `ui_runner.py` | Screenshot + OCR + compare |
| `load_scripts_and_order()` | `script_manager.py` | Load scripts with order reconciliation |
| `save_scripts_and_order()` | `script_manager.py` | Persist scripts + order |
| `open_script_editor_window()` | `ui_editor.py` | Script editor dialog |
| `open_action_dialog()` | `ui_editor.py` | Action editor dialog |
| `has_recursive_script_call()` | `ui_editor.py` | DFS cycle detection for sub-scripts |
| `create_script_list_tab()` | `ui_script_list.py` | Script list UI with checkboxes |
| `create_check_list_tab()` | `ui_check_list.py` | Check list UI with filters |
| `get_positions_for_check_item()` | `ui_check_list.py` | F5/F6 coordinate capture |
| `open_import_dialog()` | `import_dialog.py` | Excel import dialog |
| `init_logging()` | `utils.py` | Daily log file setup |
| `all_check_items_exist()` | `utils.py` | Validate check actions have matching items |

## Folder Responsibility

```
AILanguage/
├── *.py                    # Application source code
├── scripts.json            # User-created automation scripts
├── check_items.json        # OCR check items database (2,399 items)
├── settings.csv            # User preferences
├── requirements.txt        # Python dependencies
├── main.spec               # PyInstaller build config
├── claude_rules/           # Claude Code rules
├── docs/                   # Project documentation
├── CapturedImg/            # OCR screenshots organized by timestamp
│   └── ocr_YYYYMMDD_HHMMSS/
│       └── *.jpg
├── Result/                 # OCR result Excel reports
│   └── ocr_result_report_YYYYMMDD_HHMMSS.xlsx
├── Log/                    # Daily log files
│   └── YYYYMMDD.log
├── build/                  # PyInstaller build artifacts
├── dist/                   # Built executable
│   └── main.exe
└── .venv/                  # Python virtual environment
```

## External Dependencies

| Library | Version | Purpose | Used In |
|---------|---------|---------|---------|
| `pyautogui` | >=0.9.54 | Mouse/keyboard automation | `ui_runner.py`, `ui_editor.py`, `ui_check_list.py` |
| `pytesseract` | >=0.3.10 | OCR text recognition | `ui_runner.py` |
| `Pillow` | >=9.0.0 | Image capture (`ImageGrab`), checkbox icons (`ImageTk`) | `ui_runner.py`, `ui_script_list.py` |
| `pandas` | >=1.3.0 | Excel read/write, DataFrame | `ui_runner.py`, `import_dialog.py` |
| `openpyxl` | >=3.0.0 | Excel engine for pandas | `ui_runner.py` (indirect via pandas) |
| `keyboard` | >=0.13.5 | Global hotkey capture (F5/F6) | `ui_check_list.py` |
| `pynput` | >=1.7.6 | Mouse tracking | `mouse_tracker.py` (standalone only) |
| `tkinter` | stdlib | GUI framework | All UI files |

### System Dependencies

| Dependency | Path | Required By |
|------------|------|-------------|
| Tesseract OCR | `C:\Program Files\Tesseract-OCR\tesseract.exe` | `ui_runner.py` |
| Tesseract language data | `eng.traineddata`, `chi_sim.traineddata`, `jpn.traineddata` | OCR check actions |

### Not Used in Main App (requirements.txt only)

| Library | Purpose | Used In |
|---------|---------|---------|
| `paddleocr` | Alternative OCR engine | `testocr.py` (standalone experiment) |
| `opencv-python` | Image preprocessing | `testocr.py` (standalone experiment) |
| `pywinauto` | Windows UI automation | `check_label.py` (standalone test) |
