import logging
import os
import time
import traceback
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import tkinter.filedialog as fd
import pandas as pd
import pyautogui
from PIL import ImageGrab
import pytesseract

from utils import all_check_items_exist, clean_filename, beep, ocr_folder, result_folder, show_click_indicator, \
    run_cmd_block

# Cấu hình nếu cần (đường dẫn Tesseract trên máy)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def _describe_action(action, step_num):
    t = action.get("type", "unknown")
    if t == "click":
        return f"Step {step_num}: Click at ({action.get('x')}, {action.get('y')})"
    elif t == "type":
        if 'excel_col' in action:
            return f"Step {step_num}: Type from Excel column {action.get('excel_col')}"
        text = action.get('text', '')
        preview = (text[:30] + "...") if len(text) > 30 else text
        return f"Step {step_num}: Type '{preview}'"
    elif t == "hotkey":
        return f"Step {step_num}: Hotkey {action.get('modifier', '')}+{action.get('key', '')}"
    elif t == "check":
        return f"Step {step_num}: OCR check '{action.get('Content', '')}'"
    elif t == "scroll":
        return f"Step {step_num}: Scroll {action.get('amount', 0)}"
    elif t == "cmd_run":
        preview = action.get('cmd', '').split('\n')[0][:30]
        return f"Step {step_num}: Run command '{preview}'"
    elif t == "run_script":
        return f"Step {step_num}: Run sub-script {action.get('scripts', [])}"
    elif t == "pre-loop":
        return f"Step {step_num}: Start Excel loop"
    elif t == "post-loop":
        return f"Step {step_num}: End Excel loop"
    return f"Step {step_num}: {t}"


class _ScriptStepError(Exception):
    def __init__(self, step="", message="", expected="", actual="", exception_str=""):
        self.step = step
        self.message = message
        self.expected = expected
        self.actual = actual
        self.exception_str = exception_str
        super().__init__(message)


def _fail_result(failed_step, error_message, expected="", actual="", exception_str="", results=None):
    return {
        "success": False,
        "failedStep": failed_step,
        "errorMessage": error_message,
        "expected": expected,
        "actual": actual,
        "exception": exception_str,
        "results": results if results is not None else []
    }


def run_script(actions, scripts, check_items, delay):
    results = []
    timestamp_folder = datetime.now().strftime("ocr_%Y%m%d_%H%M%S")
    i = 0
    n = len(actions)
    step_num = 0

    while i < n:
        action = actions[i]
        step_num += 1
        step_desc = _describe_action(action, step_num)

        try:
            if action['type'] == 'pre-loop':
                excel_path = action.get("file")
                if not excel_path:
                    excel_path = fd.askopenfilename(
                        filetypes=[("Excel files", "*.xlsx *.xls")],
                        title="Select Excel file")
                if not excel_path:
                    return _fail_result(step_desc,
                        "User cancelled Excel file selection",
                        "Excel file selected for loop execution",
                        "No file was selected",
                        results=results)
                df = pd.read_excel(excel_path)
                loop_actions = []
                i += 1
                while i < n and actions[i]['type'] != 'post-loop':
                    loop_actions.append(actions[i])
                    i += 1
                for row_idx, row in df.iterrows():
                    for loop_step, a in enumerate(loop_actions, 1):
                        loop_desc = _describe_action(a, f"{step_num}.{loop_step}")
                        try:
                            do_action(a, scripts, check_items, results, timestamp_folder, delay, row)
                        except _ScriptStepError as e:
                            return _fail_result(e.step or loop_desc, e.message,
                                                e.expected, e.actual, e.exception_str,
                                                results=results)
                        except Exception as ex:
                            return _fail_result(loop_desc, str(ex),
                                "Action completes without error",
                                f"{type(ex).__name__}: {ex}",
                                traceback.format_exc(),
                                results=results)
                        if a['type'] != 'check':
                            time.sleep(_STEP_DELAY)
                while i < n and actions[i]['type'] == 'post-loop':
                    i += 1
            else:
                do_action(action, scripts, check_items, results, timestamp_folder, delay)
                i += 1
        except _ScriptStepError as e:
            return _fail_result(e.step or step_desc, e.message,
                                e.expected, e.actual, e.exception_str,
                                results=results)
        except Exception as ex:
            return _fail_result(step_desc, str(ex),
                "Action completes without error",
                f"{type(ex).__name__}: {ex}",
                traceback.format_exc(),
                results=results)

        if action['type'] != 'check':
            time.sleep(_STEP_DELAY)

    # Check OCR results for mismatches
    for r in results:
        if r.get("Match") == "❌":
            return _fail_result(
                f"OCR Check: {r.get('Label_ID', 'unknown')}",
                f"OCR text mismatch for '{r.get('Expected', '')}'",
                r.get("Expected", ""),
                r.get("Detected", ""),
                results=results)

    return {"success": True, "results": results}


_DEFAULT_TIMEOUT = 10
_STEP_DELAY = 1


def _parse_timeout(value):
    try:
        t = float(value)
        return t if t >= 1 else _DEFAULT_TIMEOUT
    except (TypeError, ValueError):
        return _DEFAULT_TIMEOUT


def _wait_and_verify(check_item, timestamp_folder, timeout):
    deadline = time.time() + timeout
    retries = 0
    last_result = None
    while True:
        retries += 1
        result = capture_check_region(check_item, timestamp_folder)
        last_result = result
        if result["Match"] == "✅":
            logging.info(
                f"OCR verify PASS on retry #{retries}: '{result['Expected']}' "
                f"(elapsed={timeout - (deadline - time.time()):.1f}s)")
            return result
        if time.time() >= deadline:
            elapsed = timeout - (deadline - time.time())
            logging.warning(
                f"OCR verify TIMEOUT after {retries} retries ({elapsed:.1f}s): "
                f"expected='{result['Expected']}', detected='{result['Detected']}'")
            return last_result
        time.sleep(1)


def do_action(action, scripts, check_items, results, timestamp_folder, delay, row=None):
    if action['type'] == 'click':
        show_click_indicator(action['x'], action['y'])
        pyautogui.click(action['x'], action['y'])
    elif action['type'] == 'type':
        if 'excel_col' in action and row is not None:
            excel_col = action['excel_col'].strip().upper()
            col_idx = ord(excel_col) - ord('A')
            try:
                value = str(row.iloc[col_idx])
            except IndexError:
                value = ""
            pyautogui.write(value)
        else:
            pyautogui.write(action['text'])
    elif action['type'] == 'hotkey':
        mod = action.get('modifier', '').lower()
        key = action.get('key', '').lower()
        if mod and key:
            pyautogui.hotkey(mod, key)
    elif action['type'] == 'scroll':
        amount = action.get('amount', 1)
        pyautogui.scroll(amount)
    elif action['type'] == 'check':
        lang = action.get("Lang")
        word = action.get("Word(resx)")
        content = action.get("Content")
        found = None
        for item in check_items.values():
            if (item.get("Lang") == lang and
                    item.get("Word(resx)") == word and
                    item.get("Content") == content):
                found = item
                break
        if found:
            try:
                timeout = _parse_timeout(delay)
                result = _wait_and_verify(found, timestamp_folder, timeout)
                results.append(result)
            except Exception as ex:
                raise _ScriptStepError(
                    message=f"Error capturing check region: {ex}",
                    expected=f"OCR capture succeeds for '{content}'",
                    actual=str(ex),
                    exception_str=traceback.format_exc())
        else:
            raise _ScriptStepError(
                message=f"Check item not found: ({lang}, {word}, {content})",
                expected=f"Check item ({lang}, {word}, {content}) exists",
                actual="Check item was not found in check items list")
    elif action['type'] == 'run_script':
        for sub_script in action['scripts']:
            if sub_script in scripts:
                sub_result = run_script(scripts[sub_script]['actions'], scripts, check_items, delay)
                if not sub_result.get("success"):
                    raise _ScriptStepError(
                        step=f"Sub-script '{sub_script}': {sub_result.get('failedStep', '')}",
                        message=sub_result.get("errorMessage", f"Sub-script '{sub_script}' failed"),
                        expected=sub_result.get("expected", ""),
                        actual=sub_result.get("actual", ""),
                        exception_str=sub_result.get("exception", ""))
            else:
                raise _ScriptStepError(
                    message=f"Script '{sub_script}' not found",
                    expected=f"Script '{sub_script}' exists",
                    actual=f"Script '{sub_script}' was not found")
    elif action['type'] == 'cmd_run':
        run_cmd_block(action['cmd'])


def create_run_script_tab_content(parent, scripts, check_items, root, start_app_var, delay):
    tk.Label(parent, text="Script Name:", font=("Arial", 12)).grid(row=1, column=0, pady=5, sticky="e")

    script_combo = ttk.Combobox(parent, values=list(scripts.keys()), state="readonly")
    script_combo.grid(row=1, column=1, sticky="w", pady=5)

    def run_selected_script():
        script_name = script_combo.get()
        if not script_name or script_name not in scripts:
            messagebox.showwarning("Warning", "Please select a script.")
            return
        script = scripts[script_name]

        ok, missing = all_check_items_exist(script["actions"], check_items)
        if not ok:
            messagebox.showerror(
                "Check item missing",
                "Cannot run because these check items do not exist:\n" + "\n".join(missing)
            )
            return

        actions = scripts.get(script_name, {}).get("actions", [])
        if not actions:
            messagebox.showwarning("Warning", "Script has no actions.")
            return

        root.withdraw()

        for i in range(5, 0, -1):
            beep()
            time.sleep(1)

        result = run_script(actions, scripts, check_items, delay)

        ocr_results = result.get("results", []) if result else []
        if ocr_results:
            try:
                os.makedirs(result_folder, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_path = os.path.join(result_folder, f"ocr_result_report_{timestamp}.xlsx")
                pd.DataFrame(ocr_results).to_excel(report_path, index=False)
                logging.info(f"Done. Report saved to: {report_path}")
            except Exception as e:
                logging.exception("Failed to save Excel report")

        root.deiconify()

    tk.Button(parent, text="Run", command=run_selected_script, width=12).grid(row=2, column=1, pady=5, sticky="w")


def capture_check_region(check_item, timestamp_folder):
    x1 = int(check_item.get("TopLeft (x)", 0))
    y1 = int(check_item.get("TopLeft (y)", 0))
    x2 = int(check_item.get("BottomRight (x)", 0))
    y2 = int(check_item.get("BottomRight (y)", 0))

    output_dir = os.path.join(ocr_folder, timestamp_folder)
    os.makedirs(output_dir, exist_ok=True)

    bbox = (x1, y1, x2, y2)
    img = ImageGrab.grab(bbox)

    content = str(check_item.get("Content", ""))
    clean_content = clean_filename(content).replace(" ", "_")
    filename = f"{clean_content}.jpg"

    lang_map = {
        "English": "eng",
        "Chinese": "chi_sim",
        "Japanese": "jpn"
    }

    lang_str = check_item.get("Lang", "English")
    lang_code = lang_map.get(lang_str, "eng")

    save_path = os.path.join(output_dir, filename)
    img.convert("RGB").save(save_path, "JPEG")
    logging.info(f"Image saved to: {save_path}")

    detected_text = pytesseract.image_to_string(img, lang=lang_code, config='--psm 7').strip()

    match = (detected_text == content)
    return {
        "Label_ID": check_item.get("TC No."),
        "Expected": content,
        "Detected": detected_text,
        "Match": "✅" if match else "❌",
        "ImagePath": save_path
    }
