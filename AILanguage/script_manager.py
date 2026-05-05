import json
import os
from datetime import datetime

from utils import scripts_path

SCRIPT_FILE = scripts_path

def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_scripts():
    if os.path.exists(SCRIPT_FILE):
        with open(SCRIPT_FILE, 'r') as f:
            return json.load(f)
    return {}


def load_scripts_and_order():
    """Trả về tuple: (scripts_dict, script_order_list)"""
    if not os.path.exists(SCRIPT_FILE):
        return {}, []
    with open(SCRIPT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    scripts = data.get("scripts", {})
    script_order = data.get("script_order", list(scripts.keys()))
    # Đảm bảo script_order không có key thừa/thiếu
    script_order = [name for name in script_order if name in scripts]
    for name in scripts:
        if name not in script_order:
            script_order.append(name)
    return scripts, script_order


def save_scripts(scripts):
    with open(SCRIPT_FILE, 'w') as f:
        json.dump(scripts, f, indent=2)


def save_scripts_and_order(scripts, script_order):
    with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
        json.dump({"scripts": scripts, "script_order": script_order}, f, indent=2, ensure_ascii=False)


def create_script(scripts, name, actions, script_order):
    if name not in scripts:
        scripts[name] = {
            "actions": actions,
            "created_at": now_iso(),
            "modified_at": now_iso()
        }
    else:
        # Nếu script đã tồn tại, ta không overwrite ở đây
        raise ValueError(f"Script {name} already exists.")
    # save_scripts(scripts)
    save_scripts_and_order(scripts, script_order)


def update_script(scripts, name, actions, script_order):
    if name in scripts:
        scripts[name]["actions"] = actions
        # Giữ created_at cũ, cập nhật modified_at
        if "created_at" not in scripts[name]:
            scripts[name]["created_at"] = now_iso()
        scripts[name]["modified_at"] = now_iso()
    else:
        # Nếu script không tồn tại thì tạo mới
        scripts[name] = {
            "actions": actions,
            "created_at": now_iso(),
            "modified_at": now_iso()
        }
    # save_scripts(scripts)
    save_scripts_and_order(scripts, script_order)

def delete_script(scripts, name, script_order):
    if name in scripts:
        del scripts[name]
        # save_scripts(scripts)
        save_scripts_and_order(scripts, script_order)

def copy_script(scripts, name, new_name, script_order):
    if name in scripts:
        scripts[new_name] = {
            "actions": scripts[name]["actions"].copy(),
            "created_at": now_iso(),
            "modified_at": now_iso()
        }
        # save_scripts(scripts)
        save_scripts_and_order(scripts, script_order)


def mark_running(scripts, script_name, script_order):
    if script_name in scripts:
        scripts[script_name]["testStatus"] = "Running"
        scripts[script_name]["lastTestedAt"] = now_iso()
        save_scripts_and_order(scripts, script_order)


def mark_pass(scripts, script_name, script_order):
    if script_name in scripts:
        scripts[script_name]["testStatus"] = "Pass"
        scripts[script_name]["lastTestedAt"] = now_iso()
        scripts[script_name]["lastTestReport"] = {
            "scriptName": script_name,
            "runTime": now_iso(),
            "result": "Pass",
            "failedStep": "",
            "errorMessage": "",
            "expected": "",
            "actual": "",
            "exception": ""
        }
        save_scripts_and_order(scripts, script_order)


def mark_fail(scripts, script_name, script_order, failed_step="", error_message="",
              expected="", actual="", exception_str=""):
    if script_name in scripts:
        scripts[script_name]["testStatus"] = "Fail"
        scripts[script_name]["lastTestedAt"] = now_iso()
        scripts[script_name]["lastTestReport"] = {
            "scriptName": script_name,
            "runTime": now_iso(),
            "result": "Fail",
            "failedStep": failed_step,
            "errorMessage": error_message,
            "expected": expected,
            "actual": actual,
            "exception": exception_str
        }
        save_scripts_and_order(scripts, script_order)
