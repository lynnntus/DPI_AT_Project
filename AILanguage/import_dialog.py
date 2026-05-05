import math
import tkinter as tk
from tkinter import messagebox, filedialog
import pandas as pd


def open_import_dialog(parent, app, check_items, refresh_callback):
    """Mở cửa sổ để nhập dữ liệu từ file Excel"""
    import_dialog = tk.Toplevel(parent)
    import_dialog.title("Import Check Items from Excel")

    # Tăng kích thước cửa sổ và căn giữa màn hình
    import_dialog.geometry("550x300")
    import_dialog.update_idletasks()
    width = import_dialog.winfo_width()
    height = import_dialog.winfo_height()
    screen_width = import_dialog.winfo_screenwidth()
    screen_height = import_dialog.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    import_dialog.geometry(f"{width}x{height}+{x}+{y}")

    import_dialog.transient(parent)
    import_dialog.grab_set()

    file_path_var = tk.StringVar()

    # Khung cho các control
    frame = tk.Frame(import_dialog)
    frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)

    # Khung chứa label, entry và nút browse nằm cùng hàng, căn trái

    file_frame = tk.Frame(frame)
    file_frame.pack(fill=tk.X, pady=10)

    tk.Label(file_frame, text="Select Excel file:").pack(anchor='w')

    # Tạo 1 frame nhỏ chứa entry và button bên cạnh nhau
    path_frame = tk.Frame(file_frame)
    path_frame.pack(fill=tk.X, pady=5)

    entry = tk.Entry(path_frame, textvariable=file_path_var)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    def browse_file():
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        file_path_var.set(file_path)

    tk.Button(path_frame, text="Browse", command=browse_file, width=12).pack(side=tk.LEFT)

    # Mode lựa chọn - Radio buttons
    mode_var = tk.StringVar(value="append")  # Default mode is "Append"
    tk.Label(frame, text="Mode:").pack(pady=5, anchor='w')

    tk.Radiobutton(frame, text="Delete All and Import", variable=mode_var, value="delete_all").pack(anchor='w', padx=20)
    tk.Radiobutton(frame, text="Append to current list", variable=mode_var, value="append").pack(anchor='w', padx=20)

    # Nút Start Importing
    def import_data():
        file_path = file_path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select an Excel file.")
            return

        try:
            xls = pd.ExcelFile(file_path)
            sheets = xls.sheet_names

            # Kiểm tra tồn tại sheet Chinese và Japanese
            if "Chinese" not in sheets or "Japanese" not in sheets:
                messagebox.showerror("Error", "Excel file must contain sheets named 'Chinese' and 'Japanese'.")
                return

            if mode_var.get() == "delete_all":
                check_items.clear()

            # Hàm phụ để import từng lần
            def import_sheet(lang, sheet_name, text_col):
                df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=0)

                last_word_resx = ""
                for idx, row in df.iterrows():
                    tc_no = str(row['TC No.']) if 'TC No.' in df.columns else str(
                        row[1])  # Cột B là cột số 1 (0-based index)
                    if lang == "English":
                        tc_no = tc_no.replace("C", "E", 1)  # Thay chữ "C" đầu tiên thành "E"
                    word_resx_raw = row['Word(resx)'] if 'Word(resx)' in df.columns else row[2]

                    # Kiểm tra giá trị nan hoặc rỗng cho Word(resx)
                    if isinstance(word_resx_raw, float) and math.isnan(word_resx_raw):
                        word_resx = last_word_resx
                    elif str(word_resx_raw).strip() == "" or str(word_resx_raw).lower() == "nan":
                        word_resx = last_word_resx
                    else:
                        word_resx = str(word_resx_raw).strip()
                        last_word_resx = word_resx

                    priority = row['Priority'] if 'Priority' in df.columns else row[5]
                    # Default value for priority
                    if str(priority).strip() == "" or str(priority).lower() == "nan":
                        priority = "중"

                    if priority == "중":
                        priority = "중 (Middle)"
                    elif priority == "상":
                        priority = "상 (High)"
                    else:
                        priority = "하 (Low)"

                    # Dữ liệu Text ở cột được truyền vào
                    text_val = row[text_col]

                    check_items[tc_no] = {
                        "Lang": lang,
                        "TC No.": tc_no,
                        "Word(resx)": word_resx,
                        "Content": text_val,
                        "Priority": priority,
                        "TopLeft (x)": "",
                        "TopLeft (y)": "",
                        "BottomRight (x)": "",
                        "BottomRight (y)": ""
                    }

            # Import lần 1: English từ sheet Chinese, cột D (index 3)
            import_sheet("English", "Chinese", 3)

            # Import lần 2: Chinese từ sheet Chinese, cột E (index 4)
            import_sheet("Chinese", "Chinese", 4)

            # Import lần 3: Japanese từ sheet Japanese, cột E (index 4)
            import_sheet("Japanese", "Japanese", 4)

            # Lưu lại check items
            app.save_check_items()

            messagebox.showinfo("Import Successful", "Check items imported successfully.")
            refresh_callback()
            import_dialog.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Error importing data: {e}")

    # Nút Start Importing và Cancel nằm ngang hàng
    button_frame = tk.Frame(frame)
    button_frame.pack(pady=20)

    tk.Button(button_frame, text="Start Importing", command=import_data, width=15).pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Cancel", command=import_dialog.destroy, width=15).pack(side=tk.LEFT, padx=10)
