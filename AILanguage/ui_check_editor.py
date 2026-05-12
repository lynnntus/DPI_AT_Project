import tkinter as tk
from tkinter import messagebox


def open_check_editor(parent, app, check_items, key=None, on_save=None):
    is_update = key is not None
    editor = tk.Toplevel(parent)
    editor.title("Update Check Item" if is_update else "Create New Check Item")

    # Cập nhật kích thước và căn giữa
    editor.geometry("600x500")
    editor.update_idletasks()  # Đảm bảo kích thước đã được cập nhật
    width = editor.winfo_width()
    height = editor.winfo_height()
    screen_width = editor.winfo_screenwidth()
    screen_height = editor.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    editor.geometry(f"{width}x{height}+{x}+{y}")

    editor.transient(parent)
    editor.grab_set()

    data = check_items[key] if is_update else {"Lang": "English", "TC No.": "", "Word(resx)": "", "Content": "",
                                               "Priority": "상", "TopLeft (x)": "", "TopLeft (y)": "",
                                               "BottomRight (x)": "", "BottomRight (y)": ""}

    # Các label và radio buttons
    labels = ["Lang", "TC No.", "Word(resx)", "Content", "Priority", "TopLeft (x)", "TopLeft (y)", "BottomRight (x)",
              "BottomRight (y)"]

    vars_ = {k: tk.StringVar(value=data.get(k, "")) for k in labels}

    # Lang field: 4 radio buttons
    tk.Label(editor, text="Lang:").grid(row=0, column=0, sticky='w', padx=10, pady=5)
    lang_var = tk.StringVar(value=data["Lang"])
    langs = ["English", "Chinese", "Japanese", "Korean"]
    for idx, lang in enumerate(langs):
        tk.Radiobutton(editor, text=lang, variable=lang_var, value=lang).grid(row=0, column=1 + idx, sticky='w', padx=5)

    # TC No. field
    tk.Label(editor, text="TC No.:").grid(row=1, column=0, sticky='w', padx=10, pady=5)
    tk.Entry(editor, textvariable=vars_["TC No."], width=40).grid(row=1, column=1, columnspan=4, padx=10, pady=5, sticky='w')

    # Function field
    tk.Label(editor, text="Function:").grid(row=2, column=0, sticky='w', padx=10, pady=5)
    tk.Entry(editor, textvariable=vars_["Word(resx)"], width=40).grid(row=2, column=1, columnspan=4, padx=10, pady=5, sticky='w')

    # Content field
    tk.Label(editor, text="Content:").grid(row=3, column=0, sticky='w', padx=10, pady=5)
    # tk.Entry(editor, textvariable=vars_["Content"], width=40).grid(row=3, column=1, padx=10, pady=5)
    tk.Entry(editor, textvariable=vars_["Content"], width=40).grid(row=3, column=1, columnspan=4, padx=10, pady=5, sticky='w')

    # Priority field: 3 radio buttons
    tk.Label(editor, text="Priority:").grid(row=4, column=0, sticky='w', padx=10, pady=5)
    priority_var = tk.StringVar(value=data["Priority"])
    priorities = ["상 (High)", "중 (Middle)", "하 (Low)"]
    for idx, priority in enumerate(priorities):
        tk.Radiobutton(editor, text=priority, variable=priority_var, value=priority).grid(row=4, column=1 + idx,
                                                                                          sticky='w', padx=5)

    # TopLeft (x) and TopLeft (y)
    tk.Label(editor, text="TopLeft (x):").grid(row=5, column=0, sticky='w', padx=10, pady=5)
    tk.Entry(editor, textvariable=vars_["TopLeft (x)"], width=10).grid(row=5, column=1, padx=10, pady=5)

    tk.Label(editor, text="TopLeft (y):").grid(row=6, column=0, sticky='w', padx=10, pady=5)
    tk.Entry(editor, textvariable=vars_["TopLeft (y)"], width=10).grid(row=6, column=1, padx=10, pady=5)

    # BottomRight (x) and BottomRight (y)
    tk.Label(editor, text="BottomRight (x):").grid(row=7, column=0, sticky='w', padx=10, pady=5)
    tk.Entry(editor, textvariable=vars_["BottomRight (x)"], width=10).grid(row=7, column=1, padx=10, pady=5)

    tk.Label(editor, text="BottomRight (y):").grid(row=8, column=0, sticky='w', padx=10, pady=5)
    tk.Entry(editor, textvariable=vars_["BottomRight (y)"], width=10).grid(row=8, column=1, padx=10, pady=5)

    # Save function
    def save():

        """Validate dữ liệu"""
        try:
            tlx = int(vars_["TopLeft (x)"].get())
            tly = int(vars_["TopLeft (y)"].get())
            brx = int(vars_["BottomRight (x)"].get())
            bry = int(vars_["BottomRight (y)"].get())
        except ValueError:
            messagebox.showerror("Error", "TopLeft and BottomRight coordinates must be valid integers.")
            return

        if tlx > brx:
            messagebox.showerror("Error", "TopLeft X must be less than or equal to BottomRight X.")
            return
        if tly > bry:
            messagebox.showerror("Error", "TopLeft Y must be less than or equal to BottomRight Y.")
            return

        new_key = vars_["TC No."].get().strip()
        if not new_key:
            messagebox.showerror("Error", "TC No. is required")
            return

        if (not is_update or new_key != key) and new_key in check_items:
            if not messagebox.askyesno("Confirm overwrite", f"Check item '{new_key}' exists. Overwrite?"):
                return

        if is_update and new_key != key and key in check_items:
            del check_items[key]

        check_items[new_key] = {k: v.get() for k, v in vars_.items()}
        check_items[new_key]["Lang"] = lang_var.get()
        check_items[new_key]["Priority"] = priority_var.get()
        check_items[new_key]["TopLeft (x)"] = vars_["TopLeft (x)"].get()
        check_items[new_key]["TopLeft (y)"] = vars_["TopLeft (y)"].get()
        check_items[new_key]["BottomRight (x)"] = vars_["BottomRight (x)"].get()
        check_items[new_key]["BottomRight (y)"] = vars_["BottomRight (y)"].get()

        editor.destroy()
        if on_save:
            on_save(new_key, check_items[new_key])

        # Lưu lại check items sau khi tạo mới hoặc cập nhật
        app.save_check_items()

    # Buttons for Save and Cancel
    btn_frame = tk.Frame(editor)
    btn_frame.grid(row=9, column=0, columnspan=2, pady=15)

    tk.Button(btn_frame, text="Save", command=save, width=12).pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Cancel", command=editor.destroy, width=12).pack(side=tk.LEFT, padx=10)