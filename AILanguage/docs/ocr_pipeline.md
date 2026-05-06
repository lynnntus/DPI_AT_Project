# OCR Pipeline

> Source of truth cho OCR technical documentation. Bao gồm pipeline behavior, audit findings, và gaps.

## Overview

OCR pipeline chạy khi một action `type="check"` được thực thi trong `ui_runner.py:do_action()`. Pipeline gồm: lookup check item → screenshot vùng → save image → OCR → compare → collect result.

## Audit Summary

> Audit ngày 2026-05-06.

| # | Câu hỏi | Trả lời | Vị trí |
|---|---------|---------|--------|
| 1 | Capture image ở đâu? | `ui_runner.py:capture_check_region()` line 272 | `PIL.ImageGrab.grab(bbox)` |
| 2 | Crop image ở đâu? | Không có crop riêng biệt | `ImageGrab.grab(bbox)` chụp trực tiếp vùng đã crop |
| 3 | Gọi Tesseract ở đâu? | `ui_runner.py:capture_check_region()` line 291 | `pytesseract.image_to_string()` |
| 4 | Compare ở đâu? | `ui_runner.py:capture_check_region()` line 293 | `detected_text == content` |
| 5 | Có preprocess không? | **KHÔNG** | Chỉ `img.convert("RGB").save()` |
| 6 | Có confidence score không? | **KHÔNG** | Dùng `image_to_string()`, không dùng `image_to_data()` |
| 7 | Exact match hay fuzzy? | **Exact match** | `==` operator, case-sensitive |
| 8 | Fail evidence ở đâu? | `CapturedImg/ocr_*/` + `Result/*.xlsx` | JPEG images + Excel report |

---

## 1. Image Capture Flow

### Trigger

```python
# ui_runner.py:do_action(), line ~178
elif action['type'] == 'check':
    lang = action.get("Lang")
    word = action.get("Word(resx)")
    content = action.get("Content")
```

### Check Item Lookup

```python
# Tìm check item bằng exact match 3 fields
for item in check_items.values():
    if (item.get("Lang") == lang and
        item.get("Word(resx)") == word and
        item.get("Content") == content):
        found = item
        break
```

- Nếu **không tìm thấy** → raise `_ScriptStepError` → script fails
- Nếu tìm thấy → gọi `capture_check_region(found, timestamp_folder)`

### Screenshot Capture

```python
# ui_runner.py:capture_check_region()
x1 = int(check_item.get("TopLeft (x)", 0))
y1 = int(check_item.get("TopLeft (y)", 0))
x2 = int(check_item.get("BottomRight (x)", 0))
y2 = int(check_item.get("BottomRight (y)", 0))

bbox = (x1, y1, x2, y2)
img = ImageGrab.grab(bbox)
```

- Sử dụng `PIL.ImageGrab.grab(bbox)` — chụp vùng màn hình theo pixel coordinates
- Coordinates là **absolute screen pixels**, lưu trong check_items.json
- Nếu coordinates = 0 (chưa set) → chụp vùng (0,0,0,0) → ảnh rỗng

---

## 2. Crop Logic

**Không có crop riêng biệt.** `ImageGrab.grab(bbox)` trực tiếp chụp vùng đã crop sẵn.

- `bbox = (x1, y1, x2, y2)` — TopLeft to BottomRight
- Kết quả là image đúng kích thước vùng cần check
- Không có padding, margin, hay resize

---

## 3. Preprocessing

### Current State: KHÔNG CÓ PREPROCESSING

```python
img.convert("RGB").save(save_path, "JPEG")
```

- Image được convert sang RGB và save JPEG trực tiếp
- **Không có**: grayscale, contrast adjustment, threshold, noise reduction, resize, DPI normalization

### Implication

- OCR accuracy phụ thuộc hoàn toàn vào chất lượng screenshot gốc
- Dark theme, low contrast, anti-aliased text có thể giảm accuracy
- Font size nhỏ hoặc subpixel rendering có thể gây OCR errors

---

## 4. OCR Language Handling

### Language Mapping

```python
lang_map = {
    "English": "eng",
    "Chinese": "chi_sim",
    "Japanese": "jpn"
}
lang_str = check_item.get("Lang", "English")
lang_code = lang_map.get(lang_str, "eng")  # default: eng
```

### Supported Languages

| App Language | Tesseract Code | traineddata File |
|-------------|---------------|-----------------|
| English | `eng` | `eng.traineddata` |
| Chinese | `chi_sim` | `chi_sim.traineddata` (Simplified Chinese) |
| Japanese | `jpn` | `jpn.traineddata` |

### Not Supported

- Korean (`kor`) — có radio button trong UI editor nhưng **không có trong lang_map**
- Traditional Chinese (`chi_tra`)
- Multi-language trong cùng 1 check item

### Tesseract Configuration

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
detected_text = pytesseract.image_to_string(img, lang=lang_code, config='--psm 7').strip()
```

- `--psm 7`: "Treat the image as a single text line" — phù hợp cho UI label validation
- Không có custom `--oem` (default OEM 3: LSTM + legacy)
- Không có whitelist/blacklist characters
- Không có custom tessdata config

---

## 5. Threshold / Confidence Logic

### Current State: Cascade Compare (v1.1)

```python
OCR_CONFIG = {
    "normalize": False,    # strip + collapse spaces + unicode NFC
    "lowercase": False,    # case-insensitive compare
}
```

Compare cascade (chỉ khi option được bật):

1. **Exact match** (`==`) — luôn chạy, là default
2. **Normalized match** — strip + collapse spaces + unicode NFC (nếu `normalize=True`)
3. **Lowercase match** — so sánh sau khi `.lower()` (nếu `lowercase=True`)

Mặc định `normalize=False`, `lowercase=False` → behavior = exact match như v1.0.

### Return dict

```python
{
    "Label_ID": ..., "Expected": ..., "Detected": ...,
    "Match": "✅"/"❌",       # final result (exact hoặc cascade)
    "Match_Exact": True/False, # exact match result (luôn có)
    "Match_Method": "exact",   # "exact" | "normalized" | "lowercase"
    "ImagePath": ...
}
```

### Implications (khi tất cả options OFF — default)

- "Login" vs "Logln" → FAIL (single character error)
- "Hello " vs "Hello" → FAIL (trailing space) — ✅ nếu `normalize=True`
- "Settings" vs "settings" → FAIL (case sensitive) — ✅ nếu `lowercase=True`
- Whitespace differences → FAIL — ✅ nếu `normalize=True`

---

## 6. Expected vs Actual Compare

### Match Logic

```python
detected_text = pytesseract.image_to_string(img, lang=lang_code, config='--psm 7').strip()

# 1. Exact match (always)
exact_match = (detected_text == content)
final_match = exact_match

# 2. Normalized match (opt-in)
if not final_match and OCR_CONFIG["normalize"]:
    final_match = _normalize_text(detected_text) == _normalize_text(content)

# 3. Lowercase match (opt-in)
if not final_match and OCR_CONFIG["lowercase"]:
    final_match = cmp_detected.lower() == cmp_expected.lower()
```

### `_normalize_text(text)`

```python
text.strip() → re.sub(r'\s+', ' ', text) → unicodedata.normalize('NFC', text)
```

### Processing Steps

1. OCR output → `.strip()` (remove leading/trailing whitespace)
2. Expected text → raw from `check_item["Content"]` (no processing)
3. Compare cascade: exact → normalized (opt-in) → lowercase (opt-in)
4. `Match_Method` ghi lại method nào match thành công

### Known Edge Cases

| Scenario | Default (exact) | normalize=True | lowercase=True |
|----------|----------------|----------------|----------------|
| Extra whitespace in OCR output | `.strip()` handles leading/trailing | ✅ | ✅ |
| Internal whitespace differences ("Hello  World" vs "Hello World") | FAIL | ✅ collapse spaces | ✅ |
| Case difference ("Settings" vs "settings") | FAIL | FAIL | ✅ |
| Unicode NFC vs NFD | FAIL | ✅ NFC normalize | ✅ |
| OCR returns empty string | FAIL (unless expected empty) | FAIL | FAIL |
| Special characters (©, ™, ®) | Depends on Tesseract | Depends on Tesseract | Depends on Tesseract |
| CJK punctuation vs ASCII punctuation | FAIL | FAIL | FAIL |

---

## 7. Fail Evidence Handling

### Image Evidence

```python
output_dir = os.path.join(ocr_folder, timestamp_folder)  # CapturedImg/ocr_YYYYMMDD_HHMMSS/
os.makedirs(output_dir, exist_ok=True)

clean_content = clean_filename(content).replace(" ", "_")
filename = f"{clean_content}.jpg"
save_path = os.path.join(output_dir, filename)
img.convert("RGB").save(save_path, "JPEG")
```

- Mỗi run tạo 1 folder: `CapturedImg/ocr_YYYYMMDD_HHMMSS/`
- Filename = cleaned content text + `.jpg`
- Image format: JPEG, RGB color

### Result Collection

Mỗi check action append 1 dict vào `results[]`:

```python
{
    "Label_ID": "LANGE-001",      # TC No. from check item
    "Expected": "Settings",        # Content from check item
    "Detected": "Settlngs",        # OCR output
    "Match": "❌",                 # ✅ or ❌
    "ImagePath": "CapturedImg/ocr_20260506_120000/Settings.jpg"
}
```

### Script-Level Failure

Sau khi tất cả actions chạy xong, `run_script()` kiểm tra results:

```python
for r in results:
    if r.get("Match") == "❌":
        return _fail_result(...)  # FIRST mismatch → entire script fails
```

- **First-fail**: chỉ report mismatch đầu tiên
- Các mismatch sau không được report trong fail result (nhưng vẫn có trong Excel report)

---

## 8. Multilingual Validation Notes

### Chinese (Simplified)

- Tesseract code: `chi_sim`
- Cần `chi_sim.traineddata` trong Tesseract tessdata folder
- Simplified Chinese only — Traditional Chinese text sẽ OCR sai
- CJK character spacing có thể gây false mismatches

### Japanese

- Tesseract code: `jpn`
- Cần `jpn.traineddata`
- Hỗ trợ Kanji, Hiragana, Katakana
- Mixed Japanese-English text có thể OCR sai (chỉ dùng 1 language)

### English

- Tesseract code: `eng`
- Default fallback nếu language không nhận diện được
- Phù hợp nhất cho UI labels

### Korean

- **Không hỗ trợ trong OCR pipeline** mặc dù UI editor có Korean radio button
- `lang_map` không có entry cho Korean
- Nếu check item có Lang="Korean" → fallback sang `eng` → OCR sai hoàn toàn

---

## Pipeline Diagram

```
┌──────────────────────────────────────────────────────────────┐
│  do_action(type="check")                                      │
│                                                                │
│  1. Lookup check_item by (Lang, Word(resx), Content)          │
│     └─ NOT FOUND → _ScriptStepError → script fails            │
│                                                                │
│  2. capture_check_region(check_item, timestamp_folder)         │
│     ├─ Extract bbox: (TopLeft x,y) → (BottomRight x,y)       │
│     ├─ ImageGrab.grab(bbox)                                    │
│     ├─ Save as JPEG → CapturedImg/ocr_*/cleaned_content.jpg   │
│     ├─ lang_map: English→eng, Chinese→chi_sim, Japanese→jpn   │
│     ├─ pytesseract.image_to_string(img, lang, '--psm 7')      │
│     ├─ .strip() detected text                                  │
│     ├─ Exact match: detected == expected                       │
│     └─ Return {Label_ID, Expected, Detected, Match, ImagePath}│
│                                                                │
│  3. results.append(result)                                     │
│                                                                │
│  POST: run_script checks all results for ❌                    │
│     ├─ Any ❌ → _fail_result (first mismatch only)             │
│     └─ All ✅ → save Excel report → {"success": True}          │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Standalone OCR Files (không dùng trong production)

| File | OCR Engine | Preprocessing | Confidence | Capture Method |
|------|-----------|---------------|------------|----------------|
| `ui_runner.py` (production) | Tesseract | **KHÔNG** | **KHÔNG** | `ImageGrab.grab(bbox)` — direct region |
| `check_label.py` (standalone) | Tesseract | **KHÔNG** | **KHÔNG** | `ImageGrab.grab()` → `.crop()` — 2 bước |
| `testocr.py` (experiment) | PaddleOCR | **CÓ** | **CÓ** (built-in) | N/A |

### testocr.py — Preprocessing Reference

```python
def preprocess_for_paddleocr(pil_img):
    img = pil_img.convert('L')                          # Grayscale
    np_img = np.array(img)
    np_img = cv2.equalizeHist(np_img)                   # Histogram equalization
    np_img = cv2.GaussianBlur(np_img, (1, 1), 0)        # Gaussian blur
    np_img = cv2.adaptiveThreshold(                     # Adaptive threshold
        np_img, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8
    )
    return Image.fromarray(np_img)
```

Code này **chưa tích hợp** vào production. Có thể dùng làm reference cho Phase 2.3.

---

## 10. Gaps Summary

| # | Gap | Severity | Reference implementation? |
|---|-----|----------|--------------------------|
| 1 | Không có image preprocessing | Critical | `testocr.py:14-24` (cần adapt cho Tesseract) |
| 2 | Exact match chứ không fuzzy | Critical | Chưa có |
| 3 | Không có confidence score | High | `pytesseract.image_to_data()` sẵn có |
| 4 | Korean không support | High | Thêm 1 line vào `lang_map` + `kor.traineddata` |
| 5 | Expected text không strip | Medium | Thêm `.strip()` |
| 6 | Hardcoded Tesseract path | Medium | Chưa có |
| 7 | Filename collision | Low | Chưa có |
| 8 | No JPEG quality control | Low | Chưa có |

Roadmap fix: xem [`docs/stabilization_plan.md`](stabilization_plan.md) Phase 2.
Rules: xem [`claude_rules/ocr.md`](../claude_rules/ocr.md).
