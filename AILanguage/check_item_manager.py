import json
import os

class CheckItemManager:
    def __init__(self, filepath):
        self.filepath = filepath  # Đường dẫn đến file lưu check items
        self.check_items = self.load_check_items()  # Tải check items từ file

    def load_check_items(self):
        """Tải check items từ file JSON."""
        if os.path.exists(self.filepath):
            with open(self.filepath, mode='r', encoding='utf-8') as f:
                return json.load(f)  # Đọc check items từ file JSON
        else:
            return {}  # Trả về một dict trống nếu không có file

    def save_check_items(self, check_items):
        """Lưu check items vào file JSON."""
        with open(self.filepath, mode='w', encoding='utf-8') as f:
            json.dump(check_items, f, ensure_ascii=False, indent=4)  # Lưu check items vào file JSON
