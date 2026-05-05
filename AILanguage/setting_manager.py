import csv
import os


class SettingManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.settings = self.load_settings()

    def load_settings(self):
        # Kiểm tra nếu file cấu hình tồn tại
        if os.path.exists(self.filepath):
            with open(self.filepath, mode='r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                settings = {}
                for row in reader:
                    settings.update(row)  # Cập nhật từ file vào dict
                return settings
        else:
            # Nếu không tồn tại, trả về giá trị mặc định
            return {
                "resolution": "HD",
                "start_app": "",
                "delay": "1",  # Mặc định delay là 1 giây
            }

    def save_settings(self, settings):
        # Thêm "delay" vào danh sách fieldnames
        fieldnames = ["resolution", "start_app", "delay"]

        # Lưu lại các giá trị vào file CSV
        with open(self.filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # Nếu file chưa tồn tại, viết tiêu đề vào
            if f.tell() == 0:
                writer.writeheader()

            writer.writerow(settings)
