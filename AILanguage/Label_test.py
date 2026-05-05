import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import pyautogui
import time

from utils import scripts_path

SCRIPT_FILE = scripts_path

# Tải danh sách script từ file
def load_scripts():
    if os.path.exists(SCRIPT_FILE):
        with open(SCRIPT_FILE, 'r') as f:
            return json.load(f)
    return {}

# Lưu danh sách script vào file
def save_scripts(scripts):
    with open(SCRIPT_FILE, 'w') as f:
        json.dump(scripts, f, indent=2)

# Chạy script
def run_script(actions, delay_value):
    for action in actions:
        if action['type'] == 'click':
            pyautogui.click(action['x'], action['y'])
        elif action['type'] == 'release':
            pyautogui.mouseUp()
        elif action['type'] == 'type':
            pyautogui.write(action['text'], interval=0.05)
        time.sleep(delay_value)

class ScriptRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Script Runner")
        self.root.geometry("800x600")

        self.scripts = load_scripts()

        self.create_sidebar()
        self.create_run_script_tab()

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, width=150, bg='lightgray')
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)

        self.tabs = ["Main screen", "Script list", "Action list", "About", "Setting"]
        for tab in self.tabs:
            btn = tk.Button(self.sidebar, text=tab, width=20, anchor='w', command=lambda t=tab: self.show_tab(t))
            btn.pack(pady=2, padx=5, anchor='w')

        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

    def show_tab(self, tab_name):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if tab_name == "Main screen":
            self.create_run_script_tab()
        else:
            label = tk.Label(self.content_frame, text=f"{tab_name} tab content will be here.", font=("Arial", 14))
            label.pack(pady=20)

    def create_run_script_tab(self):
        label = tk.Label(self.content_frame, text="Start app:", font=("Arial", 12))
        label.pack(anchor='nw', pady=(10, 5), padx=10)

        self.start_app_entry = tk.Entry(self.content_frame, width=50)
        self.start_app_entry.pack(anchor='nw', padx=10, pady=(0, 10))

        frame = tk.Frame(self.content_frame)
        frame.pack(anchor='nw', padx=10, pady=10)

        tk.Label(frame, text="Script Name:", font=("Arial", 12)).pack(side=tk.LEFT, padx=(0, 10))

        self.script_combo = ttk.Combobox(frame, values=list(self.scripts.keys()), state="readonly")
        self.script_combo.pack(side=tk.LEFT, padx=(0, 10))

        run_button = tk.Button(frame, text="Run", command=self.run_selected_script)
        run_button.pack(side=tk.LEFT)

    def run_selected_script(self):
        script_name = self.script_combo.get()
        delay_value = float(self.settings.get("delay", 1))
        if not script_name:
            messagebox.showwarning("Warning", "Please select a script.")
            return

        actions = self.scripts.get(script_name, {}).get("actions", [])
        if not actions:
            messagebox.showwarning("Warning", "Script has no actions.")
            return

        self.root.withdraw()
        time.sleep(2)  # Cho phép chuyển sang app khác nếu cần
        run_script(actions, delay_value)
        self.root.deiconify()

if __name__ == '__main__':
    root = tk.Tk()
    app = ScriptRunnerApp(root)
    root.mainloop()
