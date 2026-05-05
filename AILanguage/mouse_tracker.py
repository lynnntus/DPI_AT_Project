import time
import threading
import ctypes
from pynput import keyboard
import pyautogui

stop_flag = False

def listen_keyboard():
    """Lắng nghe phím ESC để dừng chương trình"""
    global stop_flag
    def on_press(key):
        if key == keyboard.Key.esc:
            stop_flag = True
            return False
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def set_cursor_crosshair():
    """Đổi con trỏ chuột thành dấu cộng"""
    user32 = ctypes.windll.user32
    cross_cursor = user32.LoadCursorW(0, 32515)  # IDC_CROSS
    user32.SetSystemCursor(cross_cursor, 32512)  # OCR_NORMAL

def reset_cursor_default():
    """Reset con trỏ chuột về mặc định"""
    user32 = ctypes.windll.user32
    user32.SystemParametersInfoW(0x0057, 0, None, 0)  # SPI_SETCURSORS

def main():
    set_cursor_crosshair()
    threading.Thread(target=listen_keyboard, daemon=True).start()

    print("Đang theo dõi vị trí chuột mỗi 5 giây. Nhấn ESC để thoát.")
    try:
        while not stop_flag:
            x, y = pyautogui.position()
            print(f"Tọa độ chuột: ({x}, {y})")
            time.sleep(5)
    finally:
        reset_cursor_default()
        print("Con trỏ đã được reset về mặc định. Đã thoát chương trình.")

if __name__ == "__main__":
    main()
