import threading
import time
import pyautogui
import tkinter as tk
import tkinter.filedialog as fd
from tkinter import messagebox, ttk, simpledialog

from utils import all_check_items_exist, beep


def open_action_dialog(editor, scripts, name_var, on_confirm, check_items, parent_windows, in_loop=False,
                       can_add_pre_loop=True, can_add_post_loop=True, existing_action=None):
    dialog = tk.Toplevel(editor)
    dialog.title("Edit Action" if existing_action else "Add Action")

    dialog.update_idletasks()
    width, height = 500, 400
    screen_width = dialog.winfo_screenwidth()
    screen_height = dialog.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    dialog.geometry(f"{width}x{height}+{x}+{y}")

    dialog.transient(editor)
    dialog.grab_set()

    main_frame = tk.Frame(dialog)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    left_frame = tk.Frame(main_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

    tk.Label(left_frame, text="Action type:", font=("Arial", 12)).pack(anchor='w', pady=(0, 10))

    action_var = tk.StringVar(value="click")
    # Ẩn/hiện tuỳ chọn pre-loop, post-loop
    btns = []

    # Radio buttons
    rb_click = tk.Radiobutton(left_frame, text="Click", variable=action_var, value="click")
    rb_click.pack(anchor='w', pady=2)
    rb_type = tk.Radiobutton(left_frame, text="Type", variable=action_var, value="type")
    rb_type.pack(anchor='w', pady=2)
    rb_hotkey = tk.Radiobutton(left_frame, text="Hot Key", variable=action_var, value="hotkey")
    rb_hotkey.pack(anchor='w', pady=2)
    rb_scroll = tk.Radiobutton(left_frame, text="Mouse Scroll", variable=action_var, value="scroll")
    rb_scroll.pack(anchor='w', pady=2)
    rb_check = tk.Radiobutton(left_frame, text="Check", variable=action_var, value="check")
    rb_check.pack(anchor='w', pady=2)
    rb_run_script = tk.Radiobutton(left_frame, text="Run Script", variable=action_var, value="run_script")
    rb_run_script.pack(anchor='w', pady=2)
    rb_cmd = tk.Radiobutton(left_frame, text="Command Line Run", variable=action_var, value="cmd_run")
    rb_cmd.pack(anchor='w', pady=2)
    rb_delay = tk.Radiobutton(left_frame, text="Delay", variable=action_var, value="delay")
    rb_delay.pack(anchor='w', pady=2)
    if can_add_pre_loop:
        rb_pre = tk.Radiobutton(left_frame, text="Pre-Loop (Import Excel)", variable=action_var, value="pre-loop")
        rb_pre.pack(anchor='w', pady=2)
        btns.append(rb_pre)
    if can_add_post_loop:
        rb_post = tk.Radiobutton(left_frame, text="Post-Loop", variable=action_var, value="post-loop")
        rb_post.pack(anchor='w', pady=2)
        btns.append(rb_post)

    right_frame = tk.Frame(main_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Biến dữ liệu cho các loại input
    # x_var, y_var, text_var, hotkey_mod_var, hotkey_key_var, check_var = (
    #     tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar(value="ctrl"), tk.StringVar(), tk.StringVar()
    # )

    # Biến cho từng action
    x_var, y_var = tk.StringVar(), tk.StringVar()
    button_var = tk.StringVar(value="left")
    text_var = tk.StringVar()
    hotkey_mod_var = tk.StringVar(value="ctrl")
    hotkey_key_var = tk.StringVar()
    check_var = tk.StringVar()
    cmd_text_widget = [None]
    excel_col_var = tk.StringVar()

    # Cho action check
    lang_var = tk.StringVar(value="English")
    wordresx_var = tk.StringVar()
    content_var = tk.StringVar()
    tclabel_var = tk.StringVar()
    prlabel_var = tk.StringVar()

    # Cho action command line
    cmd_text_widget = [None]  # dùng list để closure truy cập

    def clear_right_frame():
        for widget in right_frame.winfo_children():
            widget.destroy()
        cmd_text_widget[0] = None

    def show_click_fields():
        clear_right_frame()
        tk.Label(right_frame, text="Mouse Button:").pack(anchor='w')
        btn_frame_click = tk.Frame(right_frame)
        btn_frame_click.pack(anchor='w', pady=(0, 5))
        tk.Radiobutton(btn_frame_click, text="Left", variable=button_var, value="left").pack(side=tk.LEFT)
        tk.Radiobutton(btn_frame_click, text="Right", variable=button_var, value="right").pack(side=tk.LEFT)

        tk.Label(right_frame, text="X:").pack(anchor='w')
        x_entry = tk.Entry(right_frame, textvariable=x_var, width=15)
        x_entry.pack(anchor='w', pady=(0, 5))
        tk.Label(right_frame, text="Y:").pack(anchor='w')
        y_entry = tk.Entry(right_frame, textvariable=y_var, width=15)
        y_entry.pack(anchor='w')

        def minimize_all_and_countdown():
            # Minimize tất cả cửa sổ hiện tại (chỉ ví dụ, tùy GUI của bạn)
            dialog.withdraw()  # Ẩn cửa sổ Add Action

            # Ẩn tất cả các cửa sổ cha truyền vào
            if parent_windows:
                for win in parent_windows:
                    try:
                        win.withdraw()
                    except:
                        pass

            for i in range(5, 0, -1):
                beep()
                time.sleep(1)
            # Lấy tọa độ chuột
            x, y = pyautogui.position()

            # # Copy vào clipboard
            # coord_str = f"{x},{y}"
            # dialog.clipboard_clear()
            # dialog.clipboard_append(coord_str)
            # dialog.update()  # Đảm bảo clipboard hoạt động

            # Cập nhật entry
            x_var.set(str(x))
            y_var.set(str(y))

            # Hiện lại cửa sổ
            dialog.deiconify()
            if parent_windows:
                for win in parent_windows:
                    try:
                        win.deiconify()
                    except:
                        pass

        def on_get_mouse_pos():
            # Dùng thread để không block GUI
            threading.Thread(target=minimize_all_and_countdown, daemon=True).start()

        # Tạo nút "Get Mouse Position"
        btn_get_pos = tk.Button(right_frame, text="Get Mouse position", command=on_get_mouse_pos)
        btn_get_pos.pack(anchor='w', pady=10)

    # def show_type_fields():
    #     clear_right_frame()
    #     tk.Label(right_frame, text="Text:").pack(anchor='w')
    #     tk.Entry(right_frame, textvariable=text_var, width=30).pack(anchor='w')

    def show_type_fields():
        clear_right_frame()
        if in_loop:
            # Điều khiển 2 radio button "Text" và "Excel column"
            type_input_mode = tk.StringVar(value="text")
            # Text field và Column field
            text_var = tk.StringVar()
            col_var = tk.StringVar()

            radio_frame = tk.Frame(right_frame)
            radio_frame.pack(anchor='w', pady=(0, 5))
            tk.Radiobutton(radio_frame, text="Text", variable=type_input_mode, value="text").pack(side=tk.LEFT)
            tk.Radiobutton(radio_frame, text="Excel column", variable=type_input_mode, value="excel").pack(side=tk.LEFT)

            # Nhãn và field nhập Text
            label_text = tk.Label(right_frame, text="Text:")
            entry_text = tk.Entry(right_frame, textvariable=text_var, width=30)
            # Nhãn và field nhập cột Excel
            label_col = tk.Label(right_frame, text="Column (A, B, ...):")
            entry_col = tk.Entry(right_frame, textvariable=col_var, width=6)

            # Hiện/ẩn theo trạng thái radio
            def update_field(*_):
                label_text.pack_forget()
                entry_text.pack_forget()
                label_col.pack_forget()
                entry_col.pack_forget()
                if type_input_mode.get() == "text":
                    label_text.pack(anchor='w')
                    entry_text.pack(anchor='w')
                else:
                    label_col.pack(anchor='w')
                    entry_col.pack(anchor='w')

            type_input_mode.trace_add('write', update_field)
            update_field()

            # Lưu biến để callback dùng được ngoài scope show_type_fields
            show_type_fields.text_var = text_var
            show_type_fields.col_var = col_var
            show_type_fields.type_input_mode = type_input_mode
        else:
            tk.Label(right_frame, text="Text:").pack(anchor='w')
            text_var = tk.StringVar()
            tk.Entry(right_frame, textvariable=text_var, width=30).pack(anchor='w')
            show_type_fields.text_var = text_var
            show_type_fields.col_var = None
            show_type_fields.type_input_mode = None

    def show_hotkey_fields():
        clear_right_frame()
        tk.Label(right_frame, text="Modifier:").pack(anchor='w')
        # Combo box hoặc radio chọn ctrl/alt
        mod_frame = tk.Frame(right_frame)
        mod_frame.pack(anchor='w', pady=(0, 5))
        rb_ctrl = tk.Radiobutton(mod_frame, text="Ctrl", variable=hotkey_mod_var, value="ctrl")
        rb_ctrl.pack(side=tk.LEFT)
        rb_alt = tk.Radiobutton(mod_frame, text="Alt", variable=hotkey_mod_var, value="alt")
        rb_alt.pack(side=tk.LEFT)

        tk.Label(right_frame, text="Key (single character):").pack(anchor='w')
        tk.Entry(right_frame, textvariable=hotkey_key_var, width=5).pack(anchor='w')

    def show_check_fields():
        # --- LOGIC UPDATE COMBOBOX ---
        def unique_wordresx_for_lang():
            vals = set()
            for item in (check_items or {}).values():
                if item.get('Lang') == lang_var.get() and item.get('Word(resx)'):
                    vals.add(item['Word(resx)'])
            return sorted(vals)

        def contents_for_lang_wordresx():
            vals = []
            # for item in (check_items or {}).values():
            #     if item.get('Lang') == lang_var.get() and item.get('Word(resx)') == wordresx_var.get():
            #         if item.get('Content') not in vals:
            #             vals.append(item.get('Content'))

            for item in (check_items or {}).values():
                if item.get('Lang') == lang_var.get() and item.get('Word(resx)') == wordresx_var.get():
                    # Kiểm tra 4 trường tọa độ tồn tại và không rỗng
                    required_fields = ["TopLeft (x)", "TopLeft (y)", "BottomRight (x)", "BottomRight (y)"]
                    if all(item.get(f) not in (None, "", " ") for f in required_fields):
                        if item.get('Content') not in vals:
                            vals.append(item.get('Content'))

            return vals

        def details_for_current_selection():
            for item in (check_items or {}).values():
                if (item.get('Lang') == lang_var.get() and
                        item.get('Word(resx)') == wordresx_var.get() and
                        item.get('Content') == content_var.get()):
                    return item.get('TC No.'), item.get('Priority')
            return "", ""

        def update_wordresx(*_):
            vals = unique_wordresx_for_lang()
            wordresx_cb['values'] = vals
            wordresx_var.set('')
            update_content()

        def update_content(*_):
            vals = contents_for_lang_wordresx()
            content_cb['values'] = vals
            content_var.set('')
            update_details()

        def update_details(*_):
            tc, pr = details_for_current_selection()
            tclabel_var.set(tc)
            prlabel_var.set(pr)

        clear_right_frame()
        # 1. Language
        tk.Label(right_frame, text="Language:").pack(anchor='w', pady=(0, 3))
        lang_frame = tk.Frame(right_frame)
        lang_frame.pack(anchor='w', pady=(0, 10))
        langs = ["English", "Chinese", "Japanese"]
        for lang in langs:
            tk.Radiobutton(lang_frame, text=lang, variable=lang_var, value=lang, command=update_wordresx).pack(
                side=tk.LEFT)

        # 2. Function combobox
        tk.Label(right_frame, text="Function:").pack(anchor='w')
        wordresx_cb = ttk.Combobox(right_frame, textvariable=wordresx_var, state="readonly")
        wordresx_cb.pack(anchor='w', fill=tk.X, pady=(0, 10))

        # 3. Content combobox
        tk.Label(right_frame, text="Content:").pack(anchor='w')
        content_cb = ttk.Combobox(right_frame, textvariable=content_var, state="readonly")
        content_cb.pack(anchor='w', fill=tk.X, pady=(0, 10))

        # 4. TC No. & Priority
        frame_details = tk.Frame(right_frame)
        frame_details.pack(anchor='w', pady=(10, 0), fill=tk.X)
        tk.Label(frame_details, text="TC No.:").grid(row=0, column=0, sticky='w')
        tk.Label(frame_details, textvariable=tclabel_var, fg="blue").grid(row=0, column=1, sticky='w', padx=(10, 20))
        tk.Label(frame_details, text="Priority:").grid(row=1, column=0, sticky='w')
        tk.Label(frame_details, textvariable=prlabel_var, fg="blue").grid(row=1, column=1, sticky='w', padx=(10, 20))

        # Bind logic động
        lang_var.trace_add('write', lambda *_: update_wordresx())
        wordresx_var.trace_add('write', lambda *_: update_content())
        content_var.trace_add('write', lambda *_: update_details())

        update_wordresx()

    delay_var = tk.StringVar(value="1")

    scroll_var = tk.StringVar(value="1")  # Số nấc cuộn chuột

    def show_scroll_fields():
        clear_right_frame()
        tk.Label(right_frame, text="Scroll amount (positive: up, negative: down):").pack(anchor='w')
        tk.Entry(right_frame, textvariable=scroll_var, width=10).pack(anchor='w')

    # def show_run_script_fields():
    #     clear_right_frame()
    #     tk.Label(right_frame, text="Script to run:").pack(anchor='w')
    #     scripts_var = tk.StringVar()
    #     scripts_combo = ttk.Combobox(right_frame, textvariable=scripts_var, values=list(scripts.keys()),
    #                                  state="readonly")
    #     scripts_combo.pack(anchor='w', pady=(0, 5))
    #     return scripts_var

    def show_run_script_fields():
        clear_right_frame()
        tk.Label(right_frame, text="Scripts to run (multi-select):").pack(anchor='w')
        listbox_scripts = tk.Listbox(right_frame, selectmode='multiple', exportselection=False, width=30, height=8)
        for script_name in scripts.keys():
            listbox_scripts.insert(tk.END, script_name)
        listbox_scripts.pack(anchor='w', pady=(0, 5))
        return listbox_scripts

    def show_cmd_fields():
        clear_right_frame()
        tk.Label(right_frame, text="Command line commands (multi-line):").pack(anchor='w')
        cmd_text = tk.Text(right_frame, height=7, width=35)
        cmd_text.pack(anchor='w', pady=(0, 5))
        # Khi confirm lấy nội dung bằng .get("1.0", "end-1c")
        # right_frame.cmd_text = cmd_text  # để truy cập sau
        cmd_text_widget[0] = cmd_text  # lưu để dùng khi xác nhận

    def show_preloop_fields():
        clear_right_frame()
        tk.Label(right_frame, text="Enter Excel Loop: \nImport an Excel file. \nFor each line in the file Excel, \nrun "
                "the group of following \nactivities once.", fg="blue").pack(anchor='w', pady=40, padx=40)
        excel_file_var = tk.StringVar()
        tk.Entry(right_frame, textvariable=excel_file_var, width=30).pack(anchor='w', pady=(0, 5))

        def browse():
            fname = fd.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")], title="Select Excel file")
            if fname:
                excel_file_var.set(fname)

        tk.Button(right_frame, text="Browse...", command=browse).pack(anchor='w')

        # Để lấy biến ra ngoài (xử lý trong confirm):
        show_preloop_fields.excel_file_var = excel_file_var

    def show_delay_fields():
        clear_right_frame()
        tk.Label(right_frame, text="Delay duration (seconds):").pack(anchor='w')
        tk.Entry(right_frame, textvariable=delay_var, width=10).pack(anchor='w', pady=(0, 5))
        tk.Label(right_frame, text="Supports decimal values (e.g. 0.5, 1.5)", fg="gray").pack(anchor='w')

    def show_postloop_fields():
        clear_right_frame()
        tk.Label(right_frame, text="Exit Excel Loop:: \nStop looping. The following \nactivities will only run once.",
                 fg="blue").pack(anchor='w', pady=20)

    def update_right_frame(*args):
        t = action_var.get()
        if t == "click":
            show_click_fields()
        elif t == "type":
            show_type_fields()
        elif t == "hotkey":
            show_hotkey_fields()
        elif t == "check":
            show_check_fields()
        elif t == "scroll":
            show_scroll_fields()
        elif t == "run_script":
            global run_script_listbox
            run_script_listbox = show_run_script_fields()
        elif t == "cmd_run":
            show_cmd_fields()
        elif t == "delay":
            show_delay_fields()
        elif t == "pre-loop":
            show_preloop_fields()
        elif t == "post-loop":
            show_postloop_fields()

    action_var.trace_add('write', update_right_frame)
    update_right_frame()

    def prefill_action(action):
        t = action['type']
        if t == 'click':
            x_var.set(str(action.get('x', '')))
            y_var.set(str(action.get('y', '')))
            button_var.set(action.get('button', 'left'))
        elif t == 'type':
            if 'excel_col' in action and in_loop:
                if hasattr(show_type_fields, 'type_input_mode') and show_type_fields.type_input_mode:
                    show_type_fields.type_input_mode.set('excel')
                    dialog.after(50, lambda: show_type_fields.col_var.set(action.get('excel_col', '')))
            else:
                if hasattr(show_type_fields, 'text_var') and show_type_fields.text_var:
                    show_type_fields.text_var.set(action.get('text', ''))
        elif t == 'hotkey':
            hotkey_mod_var.set(action.get('modifier', 'ctrl'))
            hotkey_key_var.set(action.get('key', ''))
        elif t == 'check':
            lang_var.set(action.get('Lang', 'English'))
            dialog.after(50, lambda: wordresx_var.set(action.get('Word(resx)', '')))
            dialog.after(100, lambda: content_var.set(action.get('Content', '')))
        elif t == 'scroll':
            scroll_var.set(str(action.get('amount', 1)))
        elif t == 'run_script':
            scripts_to_select = action.get('scripts', [])
            for i in range(run_script_listbox.size()):
                if run_script_listbox.get(i) in scripts_to_select:
                    run_script_listbox.selection_set(i)
        elif t == 'cmd_run':
            if cmd_text_widget[0]:
                cmd_text_widget[0].insert('1.0', action.get('cmd', ''))
        elif t == 'delay':
            delay_var.set(str(action.get('seconds', 1)))
        elif t == 'pre-loop':
            if hasattr(show_preloop_fields, 'excel_file_var'):
                show_preloop_fields.excel_file_var.set(action.get('file', ''))

    if existing_action:
        action_var.set(existing_action['type'])
        dialog.after(50, lambda: prefill_action(existing_action))

    bottom_frame = tk.Frame(dialog)
    bottom_frame.pack(fill=tk.X, pady=10)

    def confirm():
        t = action_var.get()
        if t == "click":
            try:
                x = int(x_var.get())
                y = int(y_var.get())
                on_confirm({"type": "click", "x": x, "y": y, "button": button_var.get()})
            except:
                messagebox.showerror("Error", "Invalid X or Y value.")
                return
        elif t == "type":
            # text = text_var.get()
            # on_confirm({"type": "type", "text": text})
            if in_loop:
                if show_type_fields.type_input_mode.get() == "excel":
                    col = show_type_fields.col_var.get().strip().upper()
                    if not col or not (len(col) == 1 and col in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
                        messagebox.showerror("Error", "Column must be a single letter (A-Z)")
                        return
                    on_confirm({"type": "type", "excel_col": col})
                else:
                    txt = show_type_fields.text_var.get()
                    on_confirm({"type": "type", "text": txt})
            else:
                txt = show_type_fields.text_var.get()
                on_confirm({"type": "type", "text": txt})
        elif t == "hotkey":
            mod = hotkey_mod_var.get()
            key = hotkey_key_var.get()
            if len(key) != 1:
                messagebox.showerror("Error", "Key must be a single character.")
                return
            on_confirm({"type": "hotkey", "modifier": mod, "key": key})
        elif t == "check":
            if not (lang_var.get() and wordresx_var.get() and content_var.get()):
                messagebox.showerror("Error", "Please select Language, Function, and Content.")
                return
            tc = tclabel_var.get()
            pr = prlabel_var.get()
            on_confirm({
                "type": "check",
                "Lang": lang_var.get(),
                "Word(resx)": wordresx_var.get(),
                "Content": content_var.get(),
                "TC No.": tc,
                "Priority": pr
            })
        elif t == "scroll":
            try:
                amount = int(scroll_var.get())
                on_confirm({"type": "scroll", "amount": amount})
            except:
                messagebox.showerror("Error", "Scroll amount must be an integer.")
                return
        elif t == "run_script":
            # Lấy các script được chọn
            selected_indices = run_script_listbox.curselection()
            selected_scripts = [run_script_listbox.get(i) for i in selected_indices]
            # Validate: Không cho chọn chính script đang sửa
            # name_var = tk.StringVar(value=script_name if script_name else "")
            current_script_name = name_var.get().strip() if 'name_var' in locals() else None
            if current_script_name in selected_scripts:
                messagebox.showerror("Error", "Cannot select the current script itself to avoid recursion.")
                return
            # Validate cả trong những script con của script được chọn.
            is_cyclic, path = has_recursive_script_call(scripts, current_script_name, selected_scripts)
            if is_cyclic:
                messagebox.showerror("Recursion error", f"Recursive sub-script detected: {' -> '.join(path)}")
                return
            if not selected_scripts:
                messagebox.showerror("Error", "Please select at least one script to run.")
                return
            on_confirm({"type": "run_script", "scripts": selected_scripts})
        elif t == "cmd_run":
            cmd_widget = cmd_text_widget[0]
            if cmd_widget is None:
                messagebox.showerror("Error", "CMD command(s) required.")
                return
            cmd_text = cmd_widget.get("1.0", "end-1c").strip()
            if not cmd_text:
                messagebox.showerror("Error", "CMD command(s) required.")
                return
            on_confirm({"type": "cmd_run", "cmd": cmd_text})
        elif t == "delay":
            try:
                seconds = float(delay_var.get())
                if seconds <= 0:
                    raise ValueError
                on_confirm({"type": "delay", "seconds": seconds})
            except ValueError:
                messagebox.showerror("Error", "Delay must be a positive number.")
                return
        elif t == "pre-loop":
            # on_confirm({"type": "pre-loop"})
            excel_path = show_preloop_fields.excel_file_var.get().strip()
            if not excel_path:
                messagebox.showerror("Error", "Please select an Excel file.")
                return
            on_confirm({"type": "pre-loop", "file": excel_path})
        elif t == "post-loop":
            on_confirm({"type": "post-loop"})

        dialog.destroy()

    btn_ok = tk.Button(bottom_frame, text="Update" if existing_action else "OK", width=12, command=confirm)
    btn_ok.pack(side=tk.LEFT, padx=10)

    btn_cancel = tk.Button(bottom_frame, text="Cancel", width=12, command=dialog.destroy)
    btn_cancel.pack(side=tk.LEFT, padx=10)


def open_script_editor_window(parent, scripts, check_items, script_name=None, on_save=None):
    if script_name and script_name in scripts:
        actions = scripts[script_name]["actions"].copy()
        is_update = True
    else:
        actions = []
        is_update = False

    editor = tk.Toplevel(parent)
    editor.title("Edit Script" if is_update else "Create New Script")

    # Cân đối cửa sổ ở giữa màn hình
    editor.update_idletasks()  # Đảm bảo widget được tạo đủ để tính kích thước
    width, height = 520, 450
    screen_width = editor.winfo_screenwidth()
    screen_height = editor.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    editor.geometry(f"{width}x{height}+{x}+{y}")

    editor.transient(parent)
    editor.grab_set()

    tk.Label(editor, text="Script name:").pack(anchor='w', padx=10, pady=(10, 0))
    name_var = tk.StringVar(value=script_name if script_name else "")
    name_entry = tk.Entry(editor, textvariable=name_var, width=40)
    name_entry.pack(anchor='w', padx=10, pady=(0, 10))

    actions_frame = tk.Frame(editor)
    actions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    listbox = tk.Listbox(actions_frame, height=10)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(actions_frame, orient=tk.VERTICAL, command=listbox.yview)
    scrollbar.pack(side=tk.LEFT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    # for act in actions:
    #     if act['type'] == 'click':
    #         listbox.insert(tk.END, f"Click at ({act['x']},{act['y']})")
    #     elif act['type'] == 'type':
    #         listbox.insert(tk.END, f"Type: {act['text']}")
    #     elif act['type'] == 'hotkey':
    #         listbox.insert(tk.END, f"Hotkey: {act['modifier']} + {act['key']}")
    #     elif act['type'] == 'check':
    #         s = f"Check ({act.get('Lang', '')}, {act.get('Word(resx)', '')}, {act.get('Content', '')})"
    #         listbox.insert(tk.END, s)
    #     elif act['type'] == 'scroll':
    #         listbox.insert(tk.END, f"Mouse scroll amount (positive: up, negative: down): {act['amount']}")
    #     elif act['type'] == 'run_script':
    #         listbox.insert(tk.END, f"Run Script: {', '.join(act['scripts'])}")
    #     elif act['type'] == 'cmd_run':
    #         preview = act.get('cmd', '').split('\n')[0]
    #         listbox.insert(tk.END, f"Command line: {preview} ...")

    def is_in_loop(idx):
        """Kiểm tra vị trí action có nằm giữa pre-loop và post-loop không"""
        idx_pre = next((i for i, a in enumerate(actions) if a['type'] == 'pre-loop'), -1)
        idx_post = next((i for i, a in enumerate(actions) if a['type'] == 'post-loop'), -1)
        if idx_pre == -1:
            return False  # chưa có pre-loop thì không nằm trong loop
        if idx_post == -1:
            return idx > idx_pre  # chưa có post-loop thì sau pre-loop đến hết đều là in-loop
        return idx_pre < idx < idx_post

    def refresh_listbox():
        listbox.delete(0, tk.END)
        for i, act in enumerate(actions):
            # Thụt lề: dùng chuỗi tiền tố '   ' khi cần
            prefix = "   |- " if is_in_loop(i) else ""
            if act['type'] == 'click':
                btn_label = "Right Click" if act.get('button') == 'right' else "Click"
                listbox.insert(tk.END, prefix + f"{btn_label} at ({act['x']},{act['y']})")
            elif act['type'] == 'type':
                if act.get("excel_col"):
                    listbox.insert(tk.END, prefix + f"Type: [Excel column {act['excel_col']}]")
                else:
                    listbox.insert(tk.END, prefix + f"Type: \"{act['text']}\"")
            elif act['type'] == 'hotkey':
                listbox.insert(tk.END, prefix + f"Hotkey: {act['modifier']}+{act['key']}")
            elif act['type'] == 'check':
                listbox.insert(tk.END, prefix + f"Check: {act.get('info', '')}")
            elif act['type'] == 'scroll':
                listbox.insert(tk.END, prefix + f"Mouse scroll amount (positive: up, negative: down): {act['amount']}")
            elif act['type'] == 'run_script':
                listbox.insert(tk.END, prefix + f"Run Script: {', '.join(act['scripts'])}")
            elif act['type'] == 'cmd_run':
                preview = act.get('cmd', '').split('\n')[0]
                listbox.insert(tk.END, prefix + f"CMD: {preview} ...")
            elif act['type'] == 'delay':
                listbox.insert(tk.END, prefix + f"Delay: {act.get('seconds', 1)}s")
            elif act['type'] == 'pre-loop':
                file_name = act.get("file", "")
                listbox.insert(tk.END, f"[Pre-Loop] -- Import from Excel: {file_name} --")
            elif act['type'] == 'post-loop':
                listbox.insert(tk.END, "[Post-Loop] -- End loop --")

    # refresh_listbox()

    btn_frame = tk.Frame(actions_frame)
    btn_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

    # Xác định trạng thái pre-loop/post-loop
    def has_pre_loop(): return any(a['type'] == 'pre-loop' for a in actions)
    def has_post_loop(): return any(a['type'] == 'post-loop' for a in actions)
    def can_add_pre_loop(): return not has_pre_loop()
    def can_add_post_loop(): return has_pre_loop() and not has_post_loop()

    # def add_action():
    #     open_action_dialog(editor, scripts, name_var, lambda action: add_action_to_list(action, listbox, actions), check_items,
    #                        parent_windows=[editor, parent])

    def add_action():
        idx = listbox.curselection()
        insert_idx = idx[0]+1 if idx else len(actions)

        # Truyền trạng thái pre-loop, post-loop để open_action_dialog quyết định option nào hiện/ẩn
        open_action_dialog(
            editor, scripts, name_var,
            lambda action: do_add_action(action, insert_idx), check_items, parent_windows=[editor, parent],
            in_loop=is_in_loop(insert_idx),   # truyền True nếu đang chèn vào trong loop
            can_add_pre_loop=can_add_pre_loop(),
            can_add_post_loop=can_add_post_loop()
        )

    def do_add_action(action, insert_idx):
        # Nếu là pre-loop/post-loop, remove action cũ cùng loại (chỉ được 1 cái)
        if action['type'] == 'pre-loop':
            actions[:] = [a for a in actions if a['type'] != 'pre-loop']
        if action['type'] == 'post-loop':
            actions[:] = [a for a in actions if a['type'] != 'post-loop']
        actions.insert(insert_idx, action)
        refresh_listbox()

    def add_action_to_list(action, listbox, actions):
        actions.append(action)
        if action['type'] == 'click':
            btn_label = "Right Click" if action.get('button') == 'right' else "Click"
            listbox.insert(tk.END, f"{btn_label} at ({action['x']},{action['y']})")
        elif action['type'] == 'type':
            listbox.insert(tk.END, f"Type: {action['text']}")
        elif action['type'] == 'hotkey':
            listbox.insert(tk.END, f"Hotkey: {action['modifier']} + {action['key']}")
        elif action['type'] == 'check':
            # THÊM MỚI: hiện lên đầy đủ
            s = f"Check ({action.get('Lang', '')}, {action.get('Word(resx)', '')}, {action.get('Content', '')})"
            listbox.insert(tk.END, s)
        elif action['type'] == 'scroll':
            listbox.insert(tk.END, f"Mouse scroll amount (positive: up, negative: down): {action['amount']}")
        elif action['type'] == 'run_script':
            listbox.insert(tk.END, f"Run Script: {', '.join(action['scripts'])}")
        elif action['type'] == 'cmd_run':
            cmd_preview = action.get('cmd', '').split('\n')[0]
            listbox.insert(tk.END, f"Command line: {cmd_preview} ...")

    # def remove_action():
    #     idx = listbox.curselection()
    #     if idx:
    #         del actions[idx[0]]
    #         listbox.delete(idx[0])

    def remove_action():
        idx = listbox.curselection()
        if idx:
            del actions[idx[0]]
            refresh_listbox()

    def update_action():
        idx = listbox.curselection()
        if not idx:
            messagebox.showwarning("Warning", "Please select an action to update.")
            return
        idx = idx[0]
        current_action = actions[idx]

        def on_update_confirm(new_action):
            actions[idx] = new_action
            refresh_listbox()

        open_action_dialog(
            editor, scripts, name_var,
            on_update_confirm, check_items, parent_windows=[editor, parent],
            in_loop=is_in_loop(idx),
            can_add_pre_loop=can_add_pre_loop() or current_action['type'] == 'pre-loop',
            can_add_post_loop=can_add_post_loop() or current_action['type'] == 'post-loop',
            existing_action=current_action
        )

    def move_up():
        idx = listbox.curselection()
        if not idx or idx[0] == 0:
            return
        i = idx[0]
        actions[i], actions[i - 1] = actions[i - 1], actions[i]
        refresh_listbox()
        listbox.selection_set(i - 1)

    def move_down():
        idx = listbox.curselection()
        if not idx or idx[0] >= len(actions) - 1:
            return
        i = idx[0]
        actions[i], actions[i + 1] = actions[i + 1], actions[i]
        refresh_listbox()
        listbox.selection_set(i + 1)

    tk.Button(btn_frame, text="Add", command=add_action).pack(pady=2, fill=tk.X)
    tk.Button(btn_frame, text="Update", command=update_action).pack(pady=2, fill=tk.X)
    tk.Button(btn_frame, text="Remove", command=remove_action).pack(pady=2, fill=tk.X)
    tk.Button(btn_frame, text="Move Up", command=move_up).pack(pady=2, fill=tk.X)
    tk.Button(btn_frame, text="Move Down", command=move_down).pack(pady=2, fill=tk.X)

    listbox.bind("<Double-1>", lambda e: update_action())

    # Nút Save và Cancel nằm ngang cùng hàng
    bottom_frame = tk.Frame(editor)
    bottom_frame.pack(pady=10)

    def save():
        new_name = name_var.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Script name is required")
            return
        if not actions:
            messagebox.showerror("Error", "At least one action is required")
            return

        # --- KIỂM TRA CHECK ITEM TỒN TẠI ---
        ok, missing = all_check_items_exist(actions, check_items)
        if not ok:
            messagebox.showerror(
                "Check item missing",
                "Cannot save script because these check items do not exist:\n" + "\n".join(missing)
            )
            return

        if (not is_update or new_name != script_name) and new_name in scripts:
            if not messagebox.askyesno("Confirm overwrite", f"Script '{new_name}' already exists. Overwrite?"):
                return

        if is_update and new_name != script_name and script_name in scripts:
            del scripts[script_name]

        editor.destroy()
        if on_save:
            on_save(new_name, actions)

    save_btn = tk.Button(bottom_frame, text="Save", command=save, width=10)
    save_btn.pack(side=tk.LEFT, padx=10)

    cancel_btn = tk.Button(bottom_frame, text="Cancel", command=editor.destroy, width=10)
    cancel_btn.pack(side=tk.LEFT, padx=10)

    refresh_listbox()

def has_recursive_script_call(scripts, parent_name, candidate_subscripts):
    """
    scripts: dict chứa tất cả script {'name': {'actions': [...]}, ...}
    parent_name: tên script đang kiểm tra
    candidate_subscripts: list tên các script dự định chèn làm sub-script

    return: (bool, [danh sách chuỗi gây lặp nếu có])
    """
    visited = set()

    def dfs(current, path):
        if current == parent_name:
            # Phát hiện vòng lặp
            return True, path + [current]
        if current not in scripts or current in visited:
            return False, []
        visited.add(current)
        for action in scripts[current].get("actions", []):
            if action.get("type") == "run_script":
                for sub in action.get("scripts", []):
                    found, cycle_path = dfs(sub, path + [current])
                    if found:
                        return True, cycle_path
        return False, []

    # Kiểm tra tất cả script sẽ được gán làm sub-script
    for sub in candidate_subscripts:
        found, cycle_path = dfs(sub, [])
        if found:
            return True, cycle_path
    return False, []
