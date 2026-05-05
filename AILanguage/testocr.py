# ocr_paddle.py
from paddleocr import PaddleOCR
from PIL import Image
import numpy as np
import cv2

from utils import img_path

# PaddleOCR 3.x: Định nghĩa global, dùng lại cho nhiều lần nhận diện
_ocr_jpn = PaddleOCR(
    lang="japan"
)

def preprocess_for_paddleocr(pil_img):
    # Chuyển sang gray, cân bằng sáng, tăng nét, threshold nhẹ
    img = pil_img.convert('L')
    np_img = np.array(img)
    np_img = cv2.equalizeHist(np_img)
    np_img = cv2.GaussianBlur(np_img, (1, 1), 0)
    np_img = cv2.adaptiveThreshold(
        np_img, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8
    )
    return Image.fromarray(np_img)

def ocr_japanese_pilimage(pil_img):
    np_img = np.array(pil_img)
    # PaddleOCR 3.x: trả về list các kết quả, mỗi cái là ((box), (text, confidence))
    results = _ocr_jpn.ocr(np_img)
    texts = []
    # results = [ [ [box, (text, score)], ...] ] (lồng nhiều cấp)
    for line in results[0]:
        text = line[1][0]
        texts.append(text)
    return "\n".join(texts)

if __name__ == "__main__":
    pil_img = Image.open("CapturedImg/GUI.jpg")
    # pil_img = preprocess_for_paddleocr(pil_img)
    # pil_img.save("preprocessed_sample.jpg")
    # text = ocr_japanese_pilimage(pil_img)
    # print("Detected:", text)
    # ocr1 = PaddleOCR(lang="japan", use_angle_cls=True, show_log=False)
    ocr2 = PaddleOCR(
        lang="japan",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False)
    # np_img = preprocess_for_paddleocr(pil_img)
    result = ocr2.ocr(pil_img)
    texts = []
    for line in result[0]:
        text = line[1][0]
        texts.append(text)
    print("\n".join(texts))

    # Initialize PaddleOCR instance


    # Run OCR inference on a sample image
    result2 = ocr2.predict(
        input=img_path)

    # Visualize the results and save the JSON results
    for res in result2:
        res.print()
        res.save_to_img("output")
        res.save_to_json("output")
