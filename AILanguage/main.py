import tkinter as tk
from tkinter import ttk, messagebox
from script_manager import load_scripts_and_order
from ui_runner import create_run_script_tab_content
from ui_script_list import create_script_list_tab
import setting_manager
from setting_manager import SettingManager
from check_item_manager import CheckItemManager  # Import CheckItemManager
import ui_check_list
from about_us import show_about_us
from utils import setting_path, check_items_path, init_logging


def center_window(root, width=800, height=600):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
class ScriptRunnerApp:
    def __init__(self, root):
        self.settings_manager = SettingManager(setting_path)  # Đảm bảo tạo một instance của SettingManager
        self.check_item_manager = CheckItemManager(check_items_path)  # Quản lý check items
        self.settings = self.settings_manager.settings
        self.check_items = self.check_item_manager.check_items  # Tải check items từ file
        # self.scripts = load_scripts()
        self.scripts, self.script_order = load_scripts_and_order()
        # self.tabs = ["Main screen", "Script list", "Check list", "About", "Setting"]
        self.tabs = ["Script list", "Check list", "About Us", "Setting"]
        self.tab_buttons = {}
        self.selected_tab = None
        init_logging()

        self.root = root
        self.root.title("DPI AI Test")
        center_window(self.root, 1200, 700)

        # self.check_items = self.check_item_manager.check_items  # Tải lại check items từ file JSON

        # Giữ biến cho Start App textbox 2 tab để đồng bộ
        self.start_app_var_run = tk.StringVar()
        self.start_app_var_setting = tk.StringVar()

        # Load start_app từ setting sang biến dùng chung
        self.start_app_var_run.set(self.settings.get("start_app", ""))
        self.start_app_var_setting.set(self.settings.get("start_app", ""))

        self.create_sidebar()
        # self.show_tab("Main screen")
        self.show_tab("Script list")

    def create_sidebar(self):
        self.sidebar = tk.Frame(self.root, width=160, bg='#f0f0f0')
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=15, pady=15)

        for tab in self.tabs:
            btn = tk.Button(
                self.sidebar,
                text=tab,
                width=18,
                height=2,
                anchor='center',
                relief='raised',
                borderwidth=2,
                bg='#f0f0f0',
                fg='black',
                command=lambda t=tab: self.show_tab(t)
            )
            btn.pack(pady=5)
            self.tab_buttons[tab] = btn

    def highlight_selected_tab(self, tab_name):
        for name, btn in self.tab_buttons.items():
            if name == tab_name:
                btn.configure(bg="#b3b3b3", fg="black", relief='sunken', borderwidth=3)
            else:
                btn.configure(bg="#f0f0f0", fg="black", relief='raised', borderwidth=2)

    def show_tab(self, tab_name):
        for widget in self.root.pack_slaves():
            if widget != self.sidebar:
                widget.destroy()

        self.highlight_selected_tab(tab_name)
        self.selected_tab = tab_name

        # if tab_name == "Main screen":
        #     self.show_run_script_tab()
        # el
        if tab_name == "Script list":
            create_script_list_tab(self.root, self.scripts, self.script_order, self.check_items,
                                   self.settings.get("delay", "1"))
        elif tab_name == "Setting":
            self.show_setting_tab()
        elif tab_name == "Check list":
            ui_check_list.create_check_list_tab(self.root, self, self.check_items, lambda: self.show_tab("Check list"))
        elif tab_name == "About Us":
            show_about_us(self.root)
        else:
            label = tk.Label(self.root, text=f"{tab_name}", font=("Arial", 14))
            label.pack(pady=20)

    def show_run_script_tab(self):
        # Tab Main screen có Start App textbox lấy từ biến start_app_var_run
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        label = tk.Label(frame, text="Start app:", font=("Arial", 12)).grid(row=0, column=0, sticky="e", pady=5)
        # label.pack(anchor='nw', pady=(10, 5))

        entry = tk.Entry(frame, textvariable=self.start_app_var_run, width=50).grid(row=0, column=1, pady=5)
        # entry.pack(anchor='nw', pady=(0, 10))

        # Combobox và nút Run, dùng cũ từ ui_runner.py
        create_run_script_tab_content(frame, self.scripts, self.check_items, self.root, self.start_app_var_run,
                                      self.settings.get("delay", "1"))

        # # Đồng bộ 2 biến start_app: khi thay đổi biến này thì cập nhật biến start_app_var_setting
        # def on_run_start_app_changed(*args):
        #     val = self.start_app_var_run.get()
        #     if val != self.start_app_var_setting.get():
        #         self.start_app_var_setting.set(val)
        # self.start_app_var_run.trace_add('write', on_run_start_app_changed)

    def show_setting_tab(self):
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(frame, text="Screen Resolution:", font=("Arial", 12)).pack(anchor='nw', pady=(10,5))

        resolution_var = tk.StringVar(value=self.settings.get("resolution", "HD"))

        rb_hd = tk.Radiobutton(frame, text="HD (720p): 1280px x 720px", variable=resolution_var, value="HD")
        rb_hd.pack(anchor='nw')

        rb_fhd = tk.Radiobutton(frame, text="FullHD (1080p): 1920px x 1080px", variable=resolution_var, value="FullHD")
        rb_fhd.pack(anchor='nw')

        # Delay setting: Add new field for Delay (in seconds)
        tk.Label(frame, text="Delay (seconds):", font=("Arial", 12)).pack(anchor='nw', pady=(20, 5))
        delay_var = tk.StringVar(value=self.settings.get("delay", "1"))  # Default value is 1 second

        delay_entry = tk.Entry(frame, textvariable=delay_var, width=10)
        delay_entry.pack(anchor='nw', pady=(0, 10))

        # Delay setting: Start app field
        tk.Label(frame, text="Start app:", font=("Arial", 12)).pack(anchor='nw', pady=(20,5))

        entry = tk.Entry(frame, textvariable=self.start_app_var_setting, width=50)
        entry.pack(anchor='nw', pady=(0, 10))

        save_btn = tk.Button(frame, text="Save", state='disabled')
        save_btn.pack(side=tk.BOTTOM, pady=10)

        # Khi thay đổi, bật nút Save
        def on_change(*args):
            save_btn.configure(state='normal')

        resolution_var.trace_add('write', on_change)
        self.start_app_var_setting.trace_add('write', on_change)
        delay_var.trace_add('write', on_change)

        def on_save():
            self.settings["resolution"] = resolution_var.get()
            self.settings["start_app"] = self.start_app_var_setting.get()
            self.settings["delay"] = delay_var.get()  # Save delay value
            self.settings_manager.save_settings(self.settings)  # Gọi phương thức từ đối tượng settings_manager

            save_btn.configure(state='disabled')
            messagebox.showinfo("Saved", "Settings saved successfully.")

            # Đồng bộ biến Start App trong Main screen
            if self.start_app_var_run.get() != self.start_app_var_setting.get():
                self.start_app_var_run.set(self.start_app_var_setting.get())

        save_btn.configure(command=on_save)

    def save_check_items(self):
        self.check_item_manager.save_check_items(self.check_items)

    def save_settings(self):
        # Lưu lại tất cả thông tin bao gồm delay
        self.settings["delay"] = self.delay_var.get()
        self.settings_manager.save_settings(self.settings)


if __name__ == '__main__':
    root = tk.Tk()
    app = ScriptRunnerApp(root)
    root.mainloop()
