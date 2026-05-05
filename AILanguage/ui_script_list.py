import tkinter as tk
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
from script_manager import save_scripts_and_order, now_iso, mark_running, mark_pass, mark_fail
from ui_editor import open_script_editor_window
from ui_runner import run_script
import time

from utils import all_check_items_exist, beep

checked_img = None
unchecked_img = None
checkbox_states = {}


def load_checkbox_icons():
    global checked_img, unchecked_img
    checked = Image.new("RGBA", (16, 16), (255,255,255,0))
    unchecked = Image.new("RGBA", (16, 16), (255,255,255,0))
    for x in range(16):
        for y in range(16):
            if x in (0,15) or y in (0,15):
                checked.putpixel((x,y),(0,0,0,255))
                unchecked.putpixel((x,y),(0,0,0,255))
    for x in range(4,12):
        for y in range(4,12):
            checked.putpixel((x,y),(0,150,0,255))
    checked_img = ImageTk.PhotoImage(checked)
    unchecked_img = ImageTk.PhotoImage(unchecked)


def create_script_list_tab(parent_frame, scripts, script_order, check_items, delay):
    frame = tk.Frame(parent_frame)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    title_label = tk.Label(frame, text="Script List", font=("Arial", 16, "bold"))
    title_label.pack(anchor='w', pady=(0, 10))

    def on_create_new():
        def on_save(new_name, actions):
            if not new_name or new_name in scripts:
                messagebox.showerror("Error", f"Script '{new_name}' is invalid or already exists.")
                return
            scripts[new_name] = {
                "actions": actions,
                "created_at": now_iso(),
                "modified_at": now_iso()
            }
            script_order.append(new_name)
            save_scripts_and_order(scripts, script_order)
            checkbox_states[new_name] = False
            refresh()
        open_script_editor_window(parent_frame, scripts, check_items, on_save=on_save)

    top_btn_frame = tk.Frame(frame)
    top_btn_frame.pack(anchor='w', pady=(0, 10))

    tk.Button(top_btn_frame, text="Create New", command=on_create_new, width=12).pack(side=tk.LEFT, padx=(0, 10))

    def on_run_selected(root):
        selected_scripts = [name for name, checked in checkbox_states.items() if checked]
        if not selected_scripts:
            messagebox.showinfo("No selection", "Please tick at least one script.")
            return

        root.withdraw()
        for i in range(5, 0, -1):
            beep()
            time.sleep(1)

        for script_name in selected_scripts:
            if script_name not in scripts:
                continue
            script = scripts[script_name]

            ok, missing = all_check_items_exist(script["actions"], check_items)
            if not ok:
                root.deiconify()
                messagebox.showerror(
                    "Check item missing",
                    "Cannot run script because these check items do not exist:\n" + "\n".join(missing)
                )
                refresh()
                return

            actions = scripts.get(script_name, {}).get("actions", [])
            if not actions:
                root.deiconify()
                messagebox.showwarning("Warning", f"Script '{script_name}' has no actions.")
                refresh()
                return

            mark_running(scripts, script_name, script_order)
            result = run_script(actions, scripts, check_items, delay)

            if result and result.get("success"):
                mark_pass(scripts, script_name, script_order)
            else:
                mark_fail(scripts, script_name, script_order,
                          result.get("failedStep", "") if result else "Unknown",
                          result.get("errorMessage", "") if result else "Script returned no result",
                          result.get("expected", "") if result else "",
                          result.get("actual", "") if result else "",
                          result.get("exception", "") if result else "")

        root.deiconify()
        refresh()

    run_btn = tk.Button(top_btn_frame, text="Run", command=lambda: on_run_selected(parent_frame), width=12)
    run_btn.pack(side=tk.LEFT)

    # Treeview
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 10), background="#cccccc", foreground="black", padding=5)
    style.configure("Treeview", rowheight=25, background="#f7f7f7", fieldbackground="#f7f7f7")
    style.map("Treeview", background=[("selected", "#3874f2")], foreground=[("selected", "#ffffff")])

    tree_frame = tk.Frame(frame)
    tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

    load_checkbox_icons()
    columns = ("title", "date", "status")
    tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=12, style="Treeview")
    tree.heading("#0", text="Run", anchor='center')
    tree.heading("title", text="Title", anchor='w')
    tree.heading("date", text="Last Modified/Create Date", anchor='center')
    tree.heading("status", text="Test Status", anchor='center')
    tree.column("#0", width=50, anchor='center')
    tree.column("title", width=280, anchor='w')
    tree.column("date", width=220, anchor='center')
    tree.column("status", width=150, anchor='center')
    tree.pack(side=tk.LEFT, fill=tk.BOTH)

    scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.LEFT, fill=tk.Y)

    def get_selected_script():
        sel = tree.selection()
        if not sel:
            return None
        return tree.item(sel[0])['values'][0]

    btn_frame = tk.Frame(frame)
    btn_frame.pack(side=tk.LEFT, padx=20, pady=5, fill=tk.Y)

    move_up_btn = tk.Button(btn_frame, text="Move Up", state=tk.DISABLED)
    move_down_btn = tk.Button(btn_frame, text="Move Down", state=tk.DISABLED)

    def update_move_buttons(*args):
        selected_scripts = [name for name, checked in checkbox_states.items() if checked]
        if not selected_scripts:
            run_btn.config(state=tk.DISABLED)
        else:
            run_btn.config(state=tk.NORMAL)

        sel = tree.selection()
        if not sel:
            move_up_btn.config(state=tk.DISABLED)
            move_down_btn.config(state=tk.DISABLED)
            return
        sname = tree.item(sel[0])['values'][0]
        idx = script_order.index(sname)
        if len(script_order) == 1:
            move_up_btn.config(state=tk.DISABLED)
            move_down_btn.config(state=tk.DISABLED)
        else:
            if idx == 0:
                move_up_btn.config(state=tk.DISABLED)
            else:
                move_up_btn.config(state=tk.NORMAL)
            if idx == len(script_order) - 1:
                move_down_btn.config(state=tk.DISABLED)
            else:
                move_down_btn.config(state=tk.NORMAL)

    def refresh():
        tree.delete(*tree.get_children())
        for name in script_order:
            script = scripts.get(name)
            if script:
                date_str = script.get("modified_at") or script.get("created_at") or ""
                status = script.get("testStatus", "Not Tested")
                checked = checkbox_states.get(name, False)
                status_tag = "status_" + status.lower().replace(" ", "_")
                tree.insert("", tk.END, text="", image=(checked_img if checked else unchecked_img),
                            values=(name, date_str, status), tags=(name, status_tag))

        tree.tag_configure("status_pass", foreground="#228B22")
        tree.tag_configure("status_fail", foreground="#CC0000")
        tree.tag_configure("status_running", foreground="#0066CC")
        tree.tag_configure("status_not_tested", foreground="#888888")
        update_move_buttons()

    refresh()

    def on_tree_click(event):
        region = tree.identify("region", event.x, event.y)
        if region == "tree":
            col = tree.identify_column(event.x)
            row = tree.identify_row(event.y)
            if col == "#0" and row:
                script_name = tree.item(row)['values'][0]
                checkbox_states[script_name] = not checkbox_states.get(script_name, False)
                refresh()

    tree.bind("<ButtonRelease-1>", on_tree_click)

    def on_read():
        sname = get_selected_script()
        if not sname:
            return
        script = scripts[sname]
        ok, missing = all_check_items_exist(script["actions"], check_items)
        if not ok:
            messagebox.showerror(
                "Check item missing",
                "Cannot read script because these check items do not exist:\n" + "\n".join(missing)
            )
            return
        actions = script["actions"]
        lines = []
        for idx, act in enumerate(actions, 1):
            t = act.get("type")
            if t == "click":
                lines.append(f"{idx}. Click at ({act.get('x')}, {act.get('y')})")
            elif t == "type":
                if 'excel_col' in act:
                    lines.append(f"{idx}. From Excel file, col: {act.get('excel_col')}")
                else:
                    lines.append(f"{idx}. Type: {act.get('text')}")
            elif t == "hotkey":
                lines.append(
                    f"{idx}. Hotkey: {act.get('modifier', '').capitalize()} + {act.get('key', '').upper()}")
            elif t == "check":
                check_info = ""
                if check_items:
                    for item in check_items.values():
                        if (item.get("Lang") == act.get("Lang") and
                                item.get("Word(resx)") == act.get("Word(resx)") and
                                item.get("Content") == act.get("Content")):
                            check_info = (f"Lang: {item.get('Lang')}, "
                                          f"Word(resx): {item.get('Word(resx)')}, "
                                          f"Content: {item.get('Content')}, "
                                          f"Priority: {item.get('Priority')}, "
                                          f"TL:({item.get('TopLeft (x)')},{item.get('TopLeft (y)')}), "
                                          f"BR:({item.get('BottomRight (x)')},{item.get('BottomRight (y)')})")
                            break
                if check_info:
                    lines.append(f"{idx}. Check: {check_info}")
                else:
                    lines.append(f"{idx}. Check: {act}")
            elif t == "scroll":
                lines.append(f"{idx}. Mouse scroll amount (positive: up, negative: down): {act.get('amount')}")
            elif t == "cmd_run":
                lines.append(f"{idx}. Command line: ")
                for item in act.get('cmd', '').split('\n'):
                    lines.append(f"{item}")
            elif t == 'pre-loop':
                lines.append(f"{idx}. Pre-loop, get Excel file from: {act.get('file')}")
            elif t == 'post-loop':
                lines.append(f"{idx}. Post-loop, end loop")
            else:
                lines.append(f"{idx}. Unknown action: {act}")
        msg = "\n".join(lines)
        messagebox.showinfo("Script content", msg)

    def on_test_report():
        sname = get_selected_script()
        if not sname:
            return
        script = scripts.get(sname)
        if not script:
            return

        status = script.get("testStatus", "Not Tested")
        report = script.get("lastTestReport")
        tested_at = script.get("lastTestedAt", "N/A")

        if status == "Not Tested":
            messagebox.showinfo("Test Report", f"Script '{sname}' has not been tested yet.")
            return

        report_win = tk.Toplevel(parent_frame)
        report_win.title(f"Test Report - {sname}")
        report_win.geometry("650x450")
        report_win.transient(parent_frame)
        report_win.grab_set()

        text_frame = tk.Frame(report_win)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text = tk.Text(text_frame, wrap=tk.WORD, padx=15, pady=15, font=("Consolas", 10))
        report_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text.yview)
        text.configure(yscrollcommand=report_scrollbar.set)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill=tk.BOTH, expand=True)

        if report:
            lines = [
                f"Script Name:   {sname}",
                f"Run Time:      {report.get('runTime', 'N/A')}",
                f"Result:        {report.get('result', 'N/A')}",
                "",
                f"Failed Step:   {report.get('failedStep') or 'N/A'}",
                f"Error Message: {report.get('errorMessage') or 'N/A'}",
                f"Expected:      {report.get('expected') or 'N/A'}",
                f"Actual:        {report.get('actual') or 'N/A'}",
                "",
                "Raw Exception:",
                report.get('exception') or 'None',
                "",
                f"Last Tested At: {tested_at}"
            ]
        else:
            lines = [
                f"Script Name:    {sname}",
                f"Status:         {status}",
                f"Last Tested At: {tested_at}",
                "",
                "No detailed report available."
            ]

        text.insert(tk.END, "\n".join(lines))
        text.config(state=tk.DISABLED)

        tk.Button(report_win, text="Close", command=report_win.destroy, width=10).pack(pady=10)

    def on_update_with_order():
        sname = get_selected_script()
        if not sname:
            return

        def on_save(new_name, actions):
            if not new_name:
                messagebox.showerror("Error", "Script name is required.")
                return
            if new_name != sname:
                if new_name in scripts:
                    messagebox.showerror("Error", f"Script '{new_name}' already exists.")
                    return
                idx = script_order.index(sname)
                script_order[idx] = new_name
                checkbox_states.pop(sname, None)
                checkbox_states[new_name] = False
            scripts[new_name] = {
                "actions": actions,
                "created_at": now_iso(),
                "modified_at": now_iso()
            }
            save_scripts_and_order(scripts, script_order)
            refresh()

        open_script_editor_window(parent_frame, scripts, check_items, script_name=sname, on_save=on_save)

    def on_delete_with_order():
        sname = get_selected_script()
        if not sname:
            return
        if messagebox.askyesno("Delete", f"Delete script '{sname}'?"):
            if sname in scripts:
                del scripts[sname]
            if sname in script_order:
                script_order.remove(sname)
            checkbox_states.pop(sname, None)
            save_scripts_and_order(scripts, script_order)
            refresh()

    def on_copy_with_order():
        sname = get_selected_script()
        if not sname:
            return
        new_name = sname + "_copy"
        i = 1
        while new_name in scripts:
            new_name = f"{sname}_copy{i}"
            i += 1
        scripts[new_name] = {
            "actions": scripts[sname]["actions"].copy(),
            "created_at": now_iso(),
            "modified_at": now_iso()
        }
        idx = script_order.index(sname)
        script_order.insert(idx + 1, new_name)
        save_scripts_and_order(scripts, script_order)
        checkbox_states[new_name] = False
        refresh()

    def on_move_up():
        sname = get_selected_script()
        if not sname:
            return
        idx = script_order.index(sname)
        if idx > 0:
            script_order[idx], script_order[idx - 1] = script_order[idx - 1], script_order[idx]
            save_scripts_and_order(scripts, script_order)
            refresh()
            tree.selection_set(tree.get_children()[idx - 1])

    def on_move_down():
        sname = get_selected_script()
        if not sname:
            return
        idx = script_order.index(sname)
        if idx < len(script_order) - 1:
            script_order[idx], script_order[idx + 1] = script_order[idx + 1], script_order[idx]
            save_scripts_and_order(scripts, script_order)
            refresh()
            tree.selection_set(tree.get_children()[idx + 1])

    tk.Button(btn_frame, text="Read", command=on_read, width=12).pack(fill=tk.X, pady=2)
    tk.Button(btn_frame, text="Test Report", command=on_test_report, width=12).pack(fill=tk.X, pady=2)
    tk.Button(btn_frame, text="Update", command=on_update_with_order, width=12).pack(fill=tk.X, pady=2)
    tk.Button(btn_frame, text="Delete", command=on_delete_with_order, width=12).pack(fill=tk.X, pady=2)
    tk.Button(btn_frame, text="Copy", command=on_copy_with_order, width=12).pack(fill=tk.X, pady=2)
    move_up_btn.pack(fill=tk.X, pady=2)
    move_down_btn.pack(fill=tk.X, pady=2)
    move_up_btn.config(command=on_move_up)
    move_down_btn.config(command=on_move_down)

    tree.bind("<<TreeviewSelect>>", update_move_buttons)
    refresh()
