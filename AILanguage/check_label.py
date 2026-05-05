from time import sleep
import pytesseract
from PIL import ImageGrab, Image
from pywinauto import Application
import pandas as pd
import datetime
from datetime import datetime
import os

# Thư mục lưu ảnh
output_dir = "venv/ocr_captures"
os.makedirs(output_dir, exist_ok=True)

# Cấu hình Tesseract nếu cần
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Load file Excel
df = pd.read_excel("./dict/reference_labels.xlsx") #case SUCCESS
# df = pd.read_excel("./dict/reference_labels_sai_pass.xlsx") #case fail PASSWORD

# Start the application
# app = Application(backend="uia").start(r".\dist\geniant_login.exe")
#
# # Wait for window to be ready
# dlg = app.window(title_re=".*ez-X.*")
print("switch the screen")
sleep(5)

results = []

# Chụp toàn màn hình
img_full = ImageGrab.grab()

for idx, row in df.iterrows():
    label_id = row['Label_ID']
    expected = str(row['Expected_Text']).strip()
    lang = row.get('Language', 'eng')

    # Xử lý tọa độ
    x1, y1 = map(int, row['TopLeft'].split(','))
    x2, y2 = map(int, row['BottomRight'].split(','))
    crop_img = img_full.crop((x1, y1, x2, y2))

    # Lưu ảnh
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ocr_{timestamp}_{label_id}.jpg"
    save_path = os.path.join(output_dir, filename)
    crop_img.convert("RGB").save(save_path, "JPEG")
    print(f"💾 Image saved to: {save_path}")

    # OCR vùng đã cắt
    detected = pytesseract.image_to_string(crop_img, lang=lang, config='--psm 7').strip()

    # So sánh
    match = detected == expected
    print("Label_ID: ", label_id, "Expected: ", expected, "Detected :", detected, "Match:", "✅" if match else "❌", "\n")
    results.append({
        "Label_ID": label_id,
        "Expected": expected,
        "Detected": detected,
        "Match": "✅" if match else "❌"
    })

# Xuất báo cáo
report_df = pd.DataFrame(results)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
report_path = f"ocr_result_report_{timestamp}.xlsx"
report_df.to_excel(report_path, index=False)

print(f"✅ Done. Report saved to: {report_path}")
