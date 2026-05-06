# Report Format

## Overview

Project tạo 2 loại report:

1. **OCR Result Report** — Excel file chứa kết quả OCR check, export bởi `ui_runner.py`
2. **Script Test Report** — JSON object lưu trong `scripts.json`, managed bởi `script_manager.py`

---

## 1. OCR Result Report (Excel)

### Trigger

`ui_runner.py:run_script()` — sau khi tất cả actions chạy xong, nếu `results[]` không rỗng.

### File Location & Naming

```
Result/ocr_result_report_YYYYMMDD_HHMMSS.xlsx
```

- **Folder**: `Result/` (relative to `BASE_DIR`)
- **Filename pattern**: `ocr_result_report_{timestamp}.xlsx`
- **Timestamp**: `datetime.now().strftime("%Y%m%d_%H%M%S")` — thời điểm save report (KHÔNG phải thời điểm bắt đầu script)
- **Folder tự tạo nếu chưa tồn tại**: `os.makedirs(result_folder, exist_ok=True)`

### Report Generation

```python
df_report = pd.DataFrame(results)
report_path = os.path.join(result_folder, f"ocr_result_report_{timestamp}.xlsx")
df_report.to_excel(report_path, index=False)
```

- Sử dụng `pandas.DataFrame.to_excel()` với engine `openpyxl`
- `index=False` — không có index column
- Không có formatting, styling, hoặc auto-width
- Mỗi lần chạy script tạo 1 file mới (không overwrite)

### Columns

| Column | Type | Source | Mô tả |
|--------|------|--------|--------|
| `Label_ID` | string | `check_item["TC No."]` | Test case number (e.g., `LANGE-001`) |
| `Expected` | string | `check_item["Content"]` | Text mong đợi từ check item |
| `Detected` | string | `pytesseract.image_to_string().strip()` | Text OCR nhận dạng được |
| `Match` | string | `"✅"` or `"❌"` | Kết quả so sánh exact match |
| `ImagePath` | string | `os.path.join(output_dir, filename)` | Đường dẫn ảnh screenshot |

### Sample Report Data

| Label_ID | Expected | Detected | Match | ImagePath |
|----------|----------|----------|-------|-----------|
| LANGE-001 | Settings | Settings | ✅ | CapturedImg/ocr_20260506_120000/Settings.jpg |
| LANGE-002 | General | General | ✅ | CapturedImg/ocr_20260506_120000/General.jpg |
| LANGC-003 | 设置 | 设胃 | ❌ | CapturedImg/ocr_20260506_120000/设置.jpg |
| LANGC-004 | 通用 | 通用 | ✅ | CapturedImg/ocr_20260506_120000/通用.jpg |

### Report Conditions

| Scenario | Report được tạo? |
|----------|-----------------|
| Script có check actions → results không rỗng | ✅ Yes |
| Script không có check actions → results rỗng | ❌ No |
| Script fail ở giữa nhưng đã có results | ✅ Yes (report vẫn save) |
| Report save bị exception | ❌ No — log exception, không crash script |

### Error Handling

```python
try:
    df_report.to_excel(report_path, index=False)
    logging.info(f"Done. Report saved to: {report_path}")
except Exception as e:
    logging.exception("Failed to save Excel report")
```

- Report save failure **không làm script fail** — kết quả script vẫn pass/fail bình thường
- Error được log với `logging.exception()` (full traceback)

---

## 2. Screenshot Evidence

### File Location & Naming

```
CapturedImg/ocr_YYYYMMDD_HHMMSS/{cleaned_content}.jpg
```

- **Folder**: `CapturedImg/ocr_{timestamp}/` — 1 folder per script run
- **Timestamp**: `datetime.now().strftime("ocr_%Y%m%d_%H%M%S")` — thời điểm bắt đầu `run_script()`
- **Filename**: Content text → `clean_filename()` → replace spaces with `_` → append `.jpg`
- **Format**: JPEG, RGB color mode

### clean_filename Logic

```python
# utils.py:67-71
def clean_filename(s):
    return re.sub(r'[^\w一-鿿㐀-䶿぀-ヿ가-힯\s]', '', s)
```

- Giữ lại: `\w` (alphanumeric + underscore), CJK characters (U+4E00-9FFF, U+3400-4DBF), Hiragana/Katakana (U+3040-30FF), Korean Hangul (U+AC00-D7AF), whitespace
- Xóa: special characters, punctuation, symbols
- **Không có `.strip()`** — whitespace ở đầu/cuối được giữ nguyên
- **Không giữ hyphen `-`** — hyphen bị xóa bởi regex

### Filename Examples

| Content | Cleaned Filename |
|---------|-----------------|
| `Settings` | `Settings.jpg` |
| `User Name` | `User_Name.jpg` |
| `设置` | `设置.jpg` |
| `ログイン` | `ログイン.jpg` |
| `File (*.txt)` | `File_txt.jpg` |
| `Hello/World` | `HelloWorld.jpg` |
| `Test-Case` | `TestCase.jpg` |

### Filename Collision

- **Không có collision handling** — nếu 2 check items có cùng Content, file sau sẽ overwrite file trước
- Trong practice: ít xảy ra vì mỗi check item thường có Content khác nhau

---

## 3. Script Test Report (JSON in scripts.json)

### Structure

Mỗi script trong `scripts.json` lưu test report inline:

```json
{
  "scripts": {
    "EN_Setting": {
      "actions": [...],
      "created_at": "2026-05-01 10:00:00",
      "modified_at": "2026-05-05 14:30:00",
      "testStatus": "Pass",
      "lastTestedAt": "2026-05-06 12:00:00",
      "lastTestReport": {
        "scriptName": "EN_Setting",
        "runTime": "2026-05-06 12:00:00",
        "result": "Pass",
        "failedStep": "",
        "errorMessage": "",
        "expected": "",
        "actual": "",
        "exception": ""
      }
    }
  }
}
```

### testStatus Values

| Status | Khi nào set | Set bởi |
|--------|------------|---------|
| `"Running"` | Ngay trước khi chạy script | `mark_running()` |
| `"Pass"` | Script chạy xong, result.success == True | `mark_pass()` |
| `"Fail"` | Script chạy xong, result.success == False | `mark_fail()` |
| `"Not Tested"` | Script mới tạo (implicit — không có key testStatus) | Không set |

### lastTestReport Fields

| Field | Type | Pass Value | Fail Value |
|-------|------|-----------|------------|
| `scriptName` | string | Script name | Script name |
| `runTime` | string | ISO timestamp | ISO timestamp |
| `result` | string | `"Pass"` | `"Fail"` |
| `failedStep` | string | `""` (empty) | `"Step 3: OCR check 'Login'"` |
| `errorMessage` | string | `""` (empty) | `"OCR text mismatch for 'Login'"` |
| `expected` | string | `""` (empty) | `"Login"` |
| `actual` | string | `""` (empty) | `"Logln"` |
| `exception` | string | `""` (empty) | Traceback string |

### Timestamp Format

```python
def now_iso():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

- Format: `YYYY-MM-DD HH:MM:SS`
- Timezone: local system time (không có timezone info)
- Sử dụng cho: `lastTestedAt`, `runTime`, `created_at`, `modified_at`

### Status Lifecycle

```
Script created → (no testStatus)
     ↓
User clicks Run → mark_running → testStatus = "Running"
     ↓
run_script() returns
     ├── success: True  → mark_pass  → testStatus = "Pass"
     └── success: False → mark_fail  → testStatus = "Fail"
```

- `scripts.json` được save sau mỗi status change
- Nếu app crash giữa chừng → testStatus = "Running" (stale)

---

## 4. Pass/Fail Logic

### Script-Level Pass/Fail

```python
# ui_runner.py:run_script() — post-execution check
for r in results:
    if r.get("Match") == "❌":
        return _fail_result(
            f"OCR Check: {r.get('Label_ID', 'unknown')}",
            f"OCR text mismatch for '{r.get('Expected', '')}'",
            r.get("Expected", ""),
            r.get("Detected", ""))

return {"success": True}
```

### Pass Conditions

1. Tất cả actions chạy không exception
2. Tất cả OCR check results có Match = `"✅"`
3. → `{"success": True}`

### Fail Conditions

1. **Action exception** — bất kỳ action nào raise exception → fail ngay lập tức, report _fail_result
2. **OCR mismatch** — sau khi tất cả actions chạy xong, kiểm tra results → **first ❌ → fail**
3. **Sub-script fail** — sub-script trả về success=False → raise _ScriptStepError → parent fail
4. **User cancel** — user cancel Excel file dialog trong pre-loop → fail

### First-Fail Behavior

- Script chỉ report **mismatch đầu tiên** trong fail result
- Các mismatches sau **vẫn có trong Excel report** (vì results[] đã collect đầy đủ)
- Nhưng `_fail_result` chỉ chứa thông tin 1 mismatch

### _fail_result Structure

```python
{
    "success": False,
    "failedStep": "OCR Check: LANGE-001",
    "errorMessage": "OCR text mismatch for 'Settings'",
    "expected": "Settings",
    "actual": "Settlngs",
    "exception": ""  # Có giá trị nếu fail do exception
}
```

---

## 5. Logging

### Log File Location & Naming

```
Log/YYYYMMDD.log
```

- **Daily rotation**: mỗi ngày 1 file log
- **Append mode**: `filemode='a'`
- **Format**: `%(asctime)s [%(levelname)s] %(message)s`

### Log Events Related to Reports

| Event | Level | Message |
|-------|-------|---------|
| Report saved | INFO | `"Done. Report saved to: {report_path}"` |
| Report save failed | EXCEPTION | `"Failed to save Excel report"` + full traceback |
| Image saved | INFO | `"Image saved to: {save_path}"` |

---

## Summary: File Outputs per Script Run

| Output | Path Pattern | Condition |
|--------|-------------|-----------|
| OCR images | `CapturedImg/ocr_YYYYMMDD_HHMMSS/*.jpg` | Mỗi check action tạo 1 image |
| OCR report | `Result/ocr_result_report_YYYYMMDD_HHMMSS.xlsx` | Có ít nhất 1 check action |
| Script status | `scripts.json` (inline) | Luôn cập nhật |
| Log | `Log/YYYYMMDD.log` | Luôn ghi |

### Naming Convention

| Component | Format | Example |
|-----------|--------|---------|
| Date | `YYYYMMDD` | `20260506` |
| Time | `HHMMSS` | `120000` |
| OCR folder | `ocr_YYYYMMDD_HHMMSS` | `ocr_20260506_120000` |
| Report file | `ocr_result_report_YYYYMMDD_HHMMSS.xlsx` | `ocr_result_report_20260506_120005.xlsx` |
| Log file | `YYYYMMDD.log` | `20260506.log` |

**Note**: OCR folder timestamp = thời điểm `run_script()` bắt đầu. Report timestamp = thời điểm report save. Hai timestamp có thể khác nhau vài giây đến vài phút.
