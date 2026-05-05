import logging
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from ui_check_editor import open_check_editor
from import_dialog import open_import_dialog  # Import hàm open_import_dialog

import keyboard
import threading
import pyautogui

# Mẫu lưu trữ check items (tạm dùng dict tương tự scripts)
# Mỗi item có cấu trúc:
# { "Lang": ..., "TC No.": ..., "Word(resx)": ..., "Content": ..., "Priority": ... , Tọa độ TopLeft và BottomRight}


def refresh_check_list_async(app):
    def worker():
        # Xử lý dữ liệu (nặng) ở đây, lấy danh sách items
        data = []
        for key, item in app.check_items.items():
            values = (
                item.get("Lang", ""),
                item.get("TC No.", ""),
                item.get("Word(resx)", ""),
                item.get("Content", ""),
                item.get("Priority", ""),
                item.get("TopLeft (x)", ""),
                item.get("TopLeft (y)", ""),
                item.get("BottomRight (x)", ""),
                item.get("BottomRight (y)", "")
            )
            data.append((key, values))

        # Đẩy lên main thread để update UI
        def update_ui():
            tree = app.check_list_tree  # Ví dụ lưu treeview trong app
            tree.delete(*tree.get_children())
            for key, values in data:
                tree.insert("", "end", iid=key, values=values)

        app.root.after(0, update_ui)

    threading.Thread(target=worker, daemon=True).start()


def get_positions_for_check_item(app, selected_key):
    def position_listener():
        try:
            app.root.withdraw()  # Ẩn cửa sổ chính

            messagebox.showinfo("Info",
                "Move mouse to TOP LEFT point and press F5.\n"
                "Then move mouse to BOTTOM RIGHT point and press F6."
            )

            logging.info("Waiting for F5 (TopLeft)...")
            keyboard.wait('f5')
            top_left = pyautogui.position()
            logging.info(f"TopLeft recorded at {top_left}")

            # messagebox.showinfo("Info", f"TopLeft saved at {top_left}. Now move mouse to BottomRight and press F6.")

            logging.info("Waiting for F6 (BottomRight)...")
            keyboard.wait('f6')
            bottom_right = pyautogui.position()
            logging.info(f"BottomRight recorded at {bottom_right}")

            # Cập nhật check item
            if selected_key in app.check_items:
                app.check_items[selected_key]["TopLeft (x)"] = top_left.x
                app.check_items[selected_key]["TopLeft (y)"] = top_left.y
                app.check_items[selected_key]["BottomRight (x)"] = bottom_right.x
                app.check_items[selected_key]["BottomRight (y)"] = bottom_right.y

                # Lưu check items
                try:
                    app.check_item_manager.save_check_items(app.check_items)
                    logging.info("Check items saved after position update.")
                except Exception as e:
                    logging.error(f"Error saving check items: {e}")

            else:
                logging.warning(f"Selected check item '{selected_key}' not found.")

        except Exception as e:
            logging.error(f"Error in position_listener: {e}")
            messagebox.showerror("Error", f"Error getting positions: {e}")
        finally:
            app.root.deiconify()
            # app.show_tab("Check list")
            refresh_check_list_async(app)

    threading.Thread(target=position_listener, daemon=True).start()


def create_check_list_tab(parent_frame, app, check_items, refresh_callback):
    frame = tk.Frame(parent_frame)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    title_label = tk.Label(frame, text="Check List", font=("Arial", 16, "bold"))
    title_label.pack(anchor='w', pady=(0, 10))

    # Tạo một frame để chứa các nút "Create New" và "Import from Excel"
    button_frame = tk.Frame(frame)
    button_frame.pack(anchor='w', pady=(0, 10))

    # Nút Create New và Import from Excel
    tk.Button(button_frame, text="Create New", width=12, command=lambda: open_check_editor(
        parent_frame, app, check_items, on_save=lambda name, data: _create_check(check_items, name, data, refresh_callback)
    )).pack(side=tk.LEFT, padx=5)

    tk.Button(button_frame, text="Import from Excel",
              command=lambda: open_import_dialog(parent_frame, app, check_items, refresh_callback)).pack(side=tk.LEFT,
                                                                                                    padx=5)

    # Filter Frame
    filter_frame = tk.Frame(frame)
    filter_frame.pack(fill=tk.X, pady=(0, 10))

    # Biến filter ngôn ngữ
    lang_filter_var = tk.StringVar(value="All")

    # Radio button
    # radio_frame = tk.Frame(frame)
    # radio_frame.pack(side=tk.LEFT, pady=(0, 5))
    tk.Label(filter_frame, text="Filters by:").pack(side=tk.LEFT, padx=10)

    langs = ["English", "Chinese", "Japanese", "All"]
    for l in langs:
        tk.Radiobutton(filter_frame, text=l, variable=lang_filter_var, value=l,
                       command=lambda: refresh_after_search()).pack(side=tk.LEFT)

    # Word(resx) combobox
    tk.Label(filter_frame, text="Word(resx):").pack(side=tk.LEFT, padx=(12, 0))
    wordresx_filter_var = tk.StringVar(value="All")

    def get_all_wordresx():
        vals = set()
        for item in check_items.values():
            v = item.get("Word(resx)", "")
            if v:
                vals.add(v)
        vals = sorted(vals)
        return ["All"] + vals

    wordresx_combo = ttk.Combobox(filter_frame, textvariable=wordresx_filter_var, state="readonly", width=15)
    wordresx_combo['values'] = get_all_wordresx()
    wordresx_combo.current(0)
    wordresx_combo.pack(side=tk.LEFT, padx=(0,8))

    # Content Entry
    tk.Label(filter_frame, text="Content:").pack(side=tk.LEFT, padx=(12, 0))
    content_filter_var = tk.StringVar()
    content_entry = tk.Entry(filter_frame, textvariable=content_filter_var, width=16)
    content_entry.pack(side=tk.LEFT, padx=(0, 8))
    # Bind Enter to search
    content_entry.bind("<Return>", lambda event: refresh_after_search())

    # Search button
    def refresh_after_search():
        tree.delete(*tree.get_children())
        lang_val = lang_filter_var.get()
        wordresx_val = wordresx_filter_var.get()
        content_val = content_filter_var.get().strip().lower()
        for key, item in check_items.items():
            # Filter theo lang
            if lang_val != "All" and item.get("Lang") != lang_val:
                continue
            # Filter theo wordresx
            if wordresx_val != "All" and item.get("Word(resx)") != wordresx_val:
                continue
            # Filter theo content (partial match, ignore case)
            if content_val and content_val not in str(item.get("Content","")).lower():
                continue
            # Show row
            row = (
                item.get("Lang", ""), item.get("TC No.", ""), item.get("Word(resx)", ""),
                item.get("Content", ""), item.get("Priority", ""),
                item.get("TopLeft (x)", ""), item.get("TopLeft (y)", ""),
                item.get("BottomRight (x)", ""), item.get("BottomRight (y)", "")
            )
            tree.insert("", tk.END, values=row)

    search_btn = tk.Button(filter_frame, text="Search", command=refresh_after_search, width=12)
    search_btn.pack(side=tk.LEFT, padx=(10,0))

    # style of treeview
    style = ttk.Style()
    # style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#cccccc", foreground="black", padding=5)
    style.configure("Treeview.Heading", font=("Arial", 10), background="#cccccc", foreground="black", padding=5,
                    rowheight=32)
    style.configure("Treeview", rowheight=25, background="#f7f7f7", fieldbackground="#f7f7f7")
    style.map("Treeview", background=[("selected", "#3874f2")], foreground=[("selected", "#ffffff")])

    # ===== Tạo tree_frame để chứa tree và scrollbar =====
    tree_frame = tk.Frame(frame)
    tree_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)

    # Cập nhật cột để có thêm không gian
    columns = ("Lang", "TC No.", "Word(resx)", "Content", "Priority", "TopLeft (x)", "TopLeft (y)", "BottomRight (x)", "BottomRight (y)")
    tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12, style="Treeview")
    app.check_list_tree = tree

    tree.heading("Lang", text="Lang", anchor='w')
    tree.heading("TC No.", text="TC No.", anchor='w')
    tree.heading("Word(resx)", text="Word(resx)", anchor='w')
    tree.heading("Content", text="Content", anchor='w')
    tree.heading("Priority", text="Priority", anchor='w')
    tree.heading("TopLeft (x)", text="TL X", anchor='center')
    tree.heading("TopLeft (y)", text="TL Y", anchor='center')
    tree.heading("BottomRight (x)", text="BR X", anchor='center')
    tree.heading("BottomRight (y)", text="BR Y", anchor='center')

    tree.column("Lang", width=70, anchor='w')
    tree.column("TC No.", width=100, anchor='w')
    tree.column("Word(resx)", width=120, anchor='w')
    tree.column("Content", width=155, anchor='w')
    tree.column("Priority", width=85, anchor='w')
    tree.column("TopLeft (x)", width=70, anchor='center')
    tree.column("TopLeft (y)", width=70, anchor='center')
    tree.column("BottomRight (x)", width=70, anchor='center')
    tree.column("BottomRight (y)", width=70, anchor='center')
    tree.pack(side=tk.LEFT, fill=tk.BOTH)

    # # Thêm scrollbar dọc và ngang
    # scrollbar_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
    # scrollbar_y.pack(side=tk.LEFT, fill=tk.Y)
    #
    # scrollbar_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
    # scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    #
    # tree.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)
    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    # Update combobox value khi thêm/xóa item
    def update_wordresx_combo():
        vals = get_all_wordresx()
        wordresx_combo['values'] = vals
        if wordresx_filter_var.get() not in vals:
            wordresx_filter_var.set("All")

    # Khi đổi lang hoặc wordresx cũng search lại (giữ đúng yêu cầu ông chủ)
    lang_filter_var.trace_add('write', lambda *_: refresh_after_search())
    wordresx_filter_var.trace_add('write', lambda *_: refresh_after_search())

    # Gọi update_wordresx_combo khi cần, ví dụ khi import/check item thay đổi
    update_wordresx_combo()

    def refresh():
        tree.delete(*tree.get_children())
        selected_lang = lang_filter_var.get()
        for key, item in check_items.items():
            if selected_lang != "All" and item.get("Lang") != selected_lang:
                continue
            tree.insert("", tk.END, values=(
                item.get("Lang", ""),
                item.get("TC No.", ""),
                item.get("Word(resx)", ""),
                item.get("Content", ""),
                item.get("Priority", ""),
                item.get("TopLeft (x)", ""),
                item.get("TopLeft (y)", ""),
                item.get("BottomRight (x)", ""),
                item.get("BottomRight (y)", "")
            ))

    refresh()

    def get_selected_key():
        sel = tree.selection()
        if not sel:
            return None
        values = tree.item(sel[0])['values']
        return str(values[1])  # Đảm bảo rằng key là kiểu string

    def on_read():
        key = get_selected_key()
        if key and key in check_items:
            content = check_items[key]
            msg = "\n".join(f"{k}: {v}" for k, v in content.items())
            messagebox.showinfo("Check Item Content", msg)

    def on_update():
        key = get_selected_key()
        if key and key in check_items:
            open_check_editor(parent_frame, app, check_items, key, on_save=lambda name, data: _update_check(check_items, name, data, refresh_callback))

    def on_delete():
        key = get_selected_key()
        if key and key in check_items:
            if messagebox.askyesno("Delete", f"Delete check item TC No. '{key}'?"):
                del check_items[key]
                refresh_callback()
        # Lưu lại check items sau khi tạo mới hoặc cập nhật
        app.save_check_items()

    def on_delete_all():
        if messagebox.askyesno("Delete All", "Are you sure you want to delete all check items?"):
            check_items.clear()  # Clear all items from check_items
            refresh_callback()
            # Lưu lại check items sau khi tạo mới hoặc cập nhật
            app.save_check_items()

    def on_copy():
        key = get_selected_key()
        if key and key in check_items:
            new_key = key + "_copy"
            i = 1
            while new_key in check_items:
                new_key = f"{key}_copy{i}"
                i += 1
            check_items[new_key] = check_items[key].copy()
            refresh_callback()
            # Lưu lại check items sau khi tạo mới hoặc cập nhật
            app.save_check_items()

    def on_get_position():
        key = get_selected_key()
        if not key:
            messagebox.showwarning("Warning", "Please select a check item to get position.")
            return
        if not app:
            messagebox.showerror("Error", "App instance not passed to get position function.")
            return
        get_positions_for_check_item(app, key)

    # ===== Nút lệnh chuyển qua frame bên phải =====
    btn_frame = tk.Frame(frame)
    btn_frame.pack(side=tk.LEFT, padx=20, pady=5, fill=tk.Y)

    tk.Button(btn_frame, text="Read", command=on_read, width=12).pack(fill=tk.X, pady=2)
    tk.Button(btn_frame, text="Update", command=on_update, width=12).pack(fill=tk.X, pady=2)
    tk.Button(btn_frame, text="Delete", command=on_delete, width=12).pack(fill=tk.X, pady=2)
    tk.Button(btn_frame, text="Delete All", command=on_delete_all, width=12).pack(fill=tk.X, pady=2)  # Nút Delete All
    tk.Button(btn_frame, text="Copy", command=on_copy, width=12).pack(fill=tk.X, pady=2)
    tk.Button(btn_frame, text="Get XY Position", command=on_get_position, width=12).pack(fill=tk.X, pady=2)


def _create_check(check_items, name, data, refresh_callback):
    check_items[name] = data
    refresh_callback()

def _update_check(check_items, name, data, refresh_callback):
    check_items[name] = data
    refresh_callback()

