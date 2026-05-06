# Runtime Flow

## App Start

```
run_app.bat
  → cd /d F:\DPI_AT_Project\AILanguage
  → python main.py
```

### Initialization Sequence (`main.py:ScriptRunnerApp.__init__`)

```
1. SettingManager(setting_path)         → load settings.csv
2. CheckItemManager(check_items_path)   → load check_items.json
3. load_scripts_and_order()             → load scripts.json → (scripts dict, script_order list)
4. init_logging()                       → create Log/YYYYMMDD.log, start session
5. Tkinter root window                  → title "DPI AI Test", 1200x700, centered
6. create_sidebar()                     → 4 tabs: Script list, Check list, About Us, Setting
7. show_tab("Script list")              → default tab
```

### Config Loading Details

**settings.csv** (via `SettingManager.load_settings`):
- Reads CSV with `csv.DictReader`
- Fields: `resolution`, `start_app`, `delay`
- Default if file missing: `{"resolution": "HD", "start_app": "", "delay": "1"}`

**check_items.json** (via `CheckItemManager.load_check_items`):
- Reads JSON with `json.load`, UTF-8 encoding
- Returns empty dict `{}` if file missing

**scripts.json** (via `script_manager.load_scripts_and_order`):
- Reads JSON: `{"scripts": {...}, "script_order": [...]}`
- Reconciles order vs actual keys (removes orphan orders, appends missing scripts)
- Returns `({}, [])` if file missing

---

## Script Execution Flow

### Trigger: User clicks "Run" in Script List tab

```
ui_script_list.py:on_run_selected()
  │
  ├─ 1. Collect checked scripts from checkbox_states
  ├─ 2. Validate: at least 1 script selected
  ├─ 3. root.withdraw()  ← hide app window
  ├─ 4. Beep countdown: 5 beeps, 1 per second
  │
  ├─ 5. FOR EACH selected script:
  │     ├─ Validate: all_check_items_exist(actions, check_items)
  │     │   → checks every "check" action has matching entry in check_items
  │     │   → if missing: show error, abort, deiconify
  │     │
  │     ├─ Validate: script has at least 1 action
  │     ├─ mark_running(scripts, name, order)  → save "Running" status
  │     │
  │     ├─ result = run_script(actions, scripts, check_items, delay)
  │     │   └─ (see Script Execution Engine below)
  │     │
  │     ├─ IF result.success:
  │     │     mark_pass(scripts, name, order)
  │     └─ ELSE:
  │           mark_fail(scripts, name, order, failedStep, errorMessage, ...)
  │
  ├─ 6. root.deiconify()  ← show app window
  └─ 7. refresh()  ← update treeview
```

### Script Execution Engine (`ui_runner.py:run_script`)

```
run_script(actions, scripts, check_items, delay)
  │
  ├─ Create results = []
  ├─ Create timestamp_folder = "ocr_YYYYMMDD_HHMMSS"
  │
  ├─ WHILE i < len(actions):
  │     action = actions[i]
  │     │
  │     ├─ IF action.type == "pre-loop":
  │     │     ├─ Get Excel file path (from action or file dialog)
  │     │     ├─ df = pd.read_excel(excel_path)
  │     │     ├─ Collect loop_actions until "post-loop"
  │     │     ├─ FOR EACH row in df:
  │     │     │     FOR EACH loop_action:
  │     │     │       do_action(action, ..., row=row)
  │     │     │       time.sleep(delay)
  │     │     └─ Skip past post-loop action
  │     │
  │     └─ ELSE:
  │           do_action(action, scripts, check_items, results, timestamp_folder, delay)
  │           time.sleep(delay)
  │
  ├─ POST-EXECUTION: Check OCR results
  │     FOR EACH result in results:
  │       IF result.Match == "❌":
  │         return _fail_result(...)  ← FIRST mismatch fails entire script
  │
  ├─ SAVE REPORT (if results exist):
  │     pd.DataFrame(results).to_excel("Result/ocr_result_report_YYYYMMDD_HHMMSS.xlsx")
  │
  └─ return {"success": True}
```

### Action Execution (`ui_runner.py:do_action`)

| Action Type | Behavior |
|-------------|----------|
| `click` | `show_click_indicator(x,y)` + `pyautogui.click(x,y)` |
| `type` | If `excel_col` + row: read cell by column letter (A=0, B=1...), `pyautogui.write(value)`. Else: `pyautogui.write(action.text)` |
| `hotkey` | `pyautogui.hotkey(modifier, key)` — modifier: ctrl/alt, key: single char |
| `scroll` | `pyautogui.scroll(amount)` — positive=up, negative=down |
| `check` | Lookup check_item by (Lang, Word(resx), Content) → `capture_check_region()` → append result |
| `run_script` | Recursive: `run_script(sub_actions, ...)`. If sub-script fails → raise `_ScriptStepError` |
| `cmd_run` | `run_cmd_block(cmd)` → writes to temp .bat → opens CMD window |

---

## Error Handling

### Error Flow

```
do_action() raises exception
  │
  ├─ _ScriptStepError  ← structured error with step, message, expected, actual, exception
  │     → caught by run_script()
  │     → returns _fail_result(...)
  │
  └─ Generic Exception
        → caught by run_script()
        → returns _fail_result(step_desc, str(ex), ..., traceback.format_exc())
```

### _fail_result Structure

```python
{
    "success": False,
    "failedStep": "Step 3: OCR check 'Login'",
    "errorMessage": "OCR text mismatch for 'Login'",
    "expected": "Login",
    "actual": "Logln",
    "exception": "traceback string..."
}
```

### Retry Logic

**Hiện tại KHÔNG có retry logic.** Mỗi action chạy đúng 1 lần. Nếu fail → script dừng ngay.

Không có:
- Retry on failure
- Timeout per action
- Wait for element
- Recovery from unexpected state

---

## Coordinate Interaction

### Click Coordinate Capture (ui_editor.py)

```
User clicks "Get Mouse Position" → minimize all windows
  → 5 beeps countdown (1/second)
  → pyautogui.position() → get (x, y)
  → fill x_var, y_var
  → restore all windows
```

### Check Item Position Capture (ui_check_list.py)

```
User clicks "Get XY Position" → hide main window
  → Show instruction: "Press F5 for TopLeft, F6 for BottomRight"
  → keyboard.wait('f5') → pyautogui.position() → TopLeft
  → keyboard.wait('f6') → pyautogui.position() → BottomRight
  → Save to check_items.json
  → Restore main window
```

---

## Logging

### Setup (`utils.py:init_logging`)

```python
Log/YYYYMMDD.log    # daily rotation
filemode='a'        # append mode
level=DEBUG
format="%(asctime)s [%(levelname)s] %(message)s"
```

### What Gets Logged

| Event | Level | Location |
|-------|-------|----------|
| Session start | INFO | `utils.py:init_logging` |
| Image saved | INFO | `ui_runner.py:capture_check_region` |
| Report saved | INFO | `ui_runner.py:run_script` |
| Report save failure | EXCEPTION | `ui_runner.py:run_script` |
| TopLeft/BottomRight recorded | INFO | `ui_check_list.py:get_positions_for_check_item` |
| Check items saved | INFO | `ui_check_list.py:get_positions_for_check_item` |
| Position errors | ERROR | `ui_check_list.py:get_positions_for_check_item` |

---

## Report Export

### OCR Result Report

Trigger: `run_script()` completes with OCR results.

```
Result/ocr_result_report_YYYYMMDD_HHMMSS.xlsx
```

Columns: `Label_ID`, `Expected`, `Detected`, `Match`, `ImagePath`

### Script Test Report

Saved in-memory in `scripts.json` per script:

```json
{
    "testStatus": "Pass|Fail|Running|Not Tested",
    "lastTestedAt": "YYYY-MM-DD HH:MM:SS",
    "lastTestReport": {
        "scriptName": "...",
        "runTime": "...",
        "result": "Pass|Fail",
        "failedStep": "...",
        "errorMessage": "...",
        "expected": "...",
        "actual": "...",
        "exception": "..."
    }
}
```
