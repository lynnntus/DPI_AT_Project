import ctypes
import re
import logging
import os
import sys
import subprocess
import tempfile
import tkinter as tk
import threading

from datetime import datetime


def show_click_indicator(x, y, size=30, duration=0.8):
    def _indicator():
        # Tạo cửa sổ top-level không border, luôn-on-top, không focus
        ind = tk.Tk()
        ind.overrideredirect(True)
        ind.attributes("-topmost", True)
        ind.attributes("-transparentcolor", "white")

        # Đặt cửa sổ đúng vị trí (center hình tròn vào x, y)
        ind.geometry(f"{size}x{size}+{x-size//2}+{y-size//2}")
        canvas = tk.Canvas(ind, width=size, height=size, highlightthickness=0, bg='white')
        canvas.pack()
        # Vẽ hình tròn đỏ, nét vàng
        canvas.create_oval(5, 5, size-5, size-5, fill="red", outline="yellow", width=3)
        # Hiển thị trong duration giây
        ind.after(int(duration * 1000), ind.destroy)
        ind.mainloop()
    # Chạy trên thread riêng để không block app chính
    threading.Thread(target=_indicator, daemon=True).start()


def get_base_dir():
    if getattr(sys, 'frozen', False):  # Nếu chạy từ exe
        return os.path.dirname(sys.executable)
    else:  # Nếu chạy file .py gốc
        return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()

img_path = os.path.join(BASE_DIR, "CapturedImg/GUI.jpg")
setting_path = os.path.join(BASE_DIR, "settings.csv")
scripts_path = os.path.join(BASE_DIR, "scripts.json")
check_items_path = os.path.join(BASE_DIR, "check_items.json")
result_folder = os.path.join(BASE_DIR, "Result")
ocr_folder = os.path.join(BASE_DIR, "CapturedImg")
log_folder = os.path.join(BASE_DIR, "Log")


def run_cmd_block(commands):
    # Ghi tất cả lệnh vào một file batch tạm
    with tempfile.NamedTemporaryFile('w', delete=False, suffix='.bat', encoding='utf-8') as f:
        f.write(commands.replace('\r\n', '\n').replace('\r', '\n'))
        batch_path = f.name
    # Mở 1 cửa sổ CMD và chạy file batch đó
    subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/K', batch_path], shell=True)
    # Không xóa batch_path ngay lập tức, chờ user đóng CMD xong có thể xóa sau

def beep():
    # Windows beep
    ctypes.windll.user32.MessageBeep(0)


def clean_filename(s):
    # Loại bỏ mọi ký tự không phải chữ, số, dấu gạch dưới, khoảng trắng và mọi ký tự Unicode chữ/cụm từ
    # \w là chữ, số và _, \u4e00-\u9fff là tiếng Trung, \u3040-\u30ff là Hiragana/Katakana, \u3400-\u4dbf là CJK extension, \uac00-\ud7af là tiếng Hàn, \s là khoảng trắng
    # Bạn có thể mở rộng nếu muốn
    return re.sub(r'[^\w\u4e00-\u9fff\u3400-\u4dbf\u3040-\u30ff\uac00-\ud7af\s]', '', s)


def all_check_items_exist(script_actions, check_items):
    """
    Kiểm tra các action "check" trong script có tồn tại trong check_items hay không.
    Trả về (True, None) nếu hợp lệ, (False, list_missing) nếu thiếu.
    """
    missing = []
    for action in script_actions:
        if action.get('type') == 'check':
            lang = action.get('Lang')
            word = action.get('Word(resx)')
            content = action.get('Content')
            found = False
            for item in check_items.values():
                if (item.get('Lang') == lang and
                    item.get('Word(resx)') == word and
                    item.get('Content') == content):
                    found = True
                    break
            if not found:
                s = f"{lang} - {word} - {content}"
                missing.append(s)
    if missing:
        return False, missing
    return True, None


def init_logging():
    # Tạo thư mục Log nếu chưa có
    os.makedirs(log_folder, exist_ok=True)

    # Tạo file log theo ngày
    today_str = datetime.now().strftime("%Y%m%d")
    logfile = os.path.join(log_folder, f"{today_str}.log")

    logging.basicConfig(
        filename=logfile,
        filemode='a',
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    logging.info("===== Start new session =====")
