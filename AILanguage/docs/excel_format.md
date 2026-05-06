# Excel Format

## Overview

Project sử dụng Excel ở 2 context khác nhau:

1. **Import Check Items** — Import OCR check items từ Excel vào `check_items.json` qua `import_dialog.py`
2. **Excel Loop (Test Data)** — Đọc Excel file để fill form fields trong pre-loop/post-loop action qua `ui_runner.py`

---

## 1. Import Check Items Excel

### Trigger

`ui_check_list.py` → nút "Import from Excel" → `import_dialog.py:open_import_dialog()`

### Required Sheets

| Sheet Name | Bắt buộc | Chứa dữ liệu |
|-----------|----------|---------------|
| `Chinese` | ✅ Yes | English text (cột D) + Chinese text (cột E) |
| `Japanese` | ✅ Yes | Japanese text (cột E) |

- **Cả 2 sheet đều bắt buộc** — nếu thiếu 1 trong 2 → error: `"Excel file must contain sheets named 'Chinese' and 'Japanese'."`
- Sheet names **case-sensitive** — `"chinese"` hoặc `"CHINESE"` sẽ không được nhận

### Sheet "Chinese" — Column Layout

| Column | Index | Header | Nội dung | Bắt buộc |
|--------|-------|--------|----------|----------|
| A | 0 | (any) | Không sử dụng | - |
| B | 1 | `TC No.` | Test case number (fallback: raw index 1) | ✅ |
| C | 2 | `Word(resx)` | Resource key (fallback: raw index 2) | ✅ |
| D | 3 | (any) | **English text** — text_col cho English import | ✅ |
| E | 4 | (any) | **Chinese text** — text_col cho Chinese import | ✅ |
| F | 5 | `Priority` | Priority level (fallback: raw index 5) | Optional |

### Sheet "Japanese" — Column Layout

| Column | Index | Header | Nội dung | Bắt buộc |
|--------|-------|--------|----------|----------|
| A | 0 | (any) | Không sử dụng | - |
| B | 1 | `TC No.` | Test case number (fallback: raw index 1) | ✅ |
| C | 2 | `Word(resx)` | Resource key (fallback: raw index 2) | ✅ |
| D | 3 | (any) | Không sử dụng cho Japanese import | - |
| E | 4 | (any) | **Japanese text** — text_col cho Japanese import | ✅ |
| F | 5 | `Priority` | Priority level (fallback: raw index 5) | Optional |

### Import Execution Order

```
1. import_sheet("English",  "Chinese",  col_index=3)  → English text từ cột D
2. import_sheet("Chinese",  "Chinese",  col_index=4)  → Chinese text từ cột E
3. import_sheet("Japanese", "Japanese", col_index=4)  → Japanese text từ cột E
```

- **3 lần import liên tiếp**, mỗi lần iterate toàn bộ rows của sheet
- Key trong `check_items` dict = `TC No.` → nếu trùng TC No. giữa các import, **import sau sẽ overwrite import trước**

### TC No. Transformation

```python
tc_no = str(row['TC No.'])
if lang == "English":
    tc_no = tc_no.replace("C", "E", 1)  # Thay chữ "C" đầu tiên thành "E"
```

| Language | Input TC No. | Output TC No. |
|----------|-------------|---------------|
| Chinese | `LANGC-001` | `LANGC-001` (giữ nguyên) |
| Japanese | `LANGC-001` | `LANGC-001` (giữ nguyên) |
| English | `LANGC-001` | `LANGE-001` (C→E) |

### Word(resx) Inheritance

```python
if isinstance(word_resx_raw, float) and math.isnan(word_resx_raw):
    word_resx = last_word_resx  # Kế thừa giá trị trước đó
```

- Nếu `Word(resx)` cell rỗng hoặc `NaN` → **kế thừa giá trị từ row trước**
- Áp dụng per-import (reset `last_word_resx` cho mỗi lần gọi `import_sheet()`)
- Dùng cho trường hợp nhiều rows cùng 1 resource key nhưng khác content

### Priority Mapping

| Input Value | Output Value |
|-------------|-------------|
| `중` | `중 (Middle)` |
| `상` | `상 (High)` |
| Bất kỳ giá trị khác | `하 (Low)` |
| Empty / NaN | `중 (Middle)` (default) |

### Import Modes

| Mode | Hành vi |
|------|---------|
| `Delete All and Import` | `check_items.clear()` → xóa toàn bộ items hiện có → import mới |
| `Append to current list` | Giữ items hiện có → import thêm (overwrite nếu trùng TC No.) |

Default mode: **Append to current list**

### Generated Check Item Structure

```python
{
    "Lang": "English",           # "English" | "Chinese" | "Japanese"
    "TC No.": "LANGE-001",       # TC No. (transformed for English)
    "Word(resx)": "Settings",    # Resource key
    "Content": "Settings",       # Text content từ Excel
    "Priority": "중 (Middle)",   # Mapped priority
    "TopLeft (x)": "",           # Empty — phải set thủ công qua F5/F6
    "TopLeft (y)": "",
    "BottomRight (x)": "",
    "BottomRight (y)": ""
}
```

### Sample Import Excel

#### Sheet "Chinese"

| A | B (TC No.) | C (Word(resx)) | D (English) | E (Chinese) | F (Priority) |
|---|-----------|----------------|-------------|-------------|-------------|
| 1 | LANGC-001 | Settings | Settings | 设置 | 중 |
| 2 | LANGC-002 | Settings | General | 通用 | 상 |
| 3 | LANGC-003 | Login | Username | 用户名 | |
| 4 | LANGC-004 | | Password | 密码 | |

- Row 3: Priority rỗng → default `중 (Middle)`
- Row 4: Word(resx) rỗng → kế thừa `Login` từ row 3

#### Sheet "Japanese"

| A | B (TC No.) | C (Word(resx)) | D | E (Japanese) | F (Priority) |
|---|-----------|----------------|---|-------------|-------------|
| 1 | LANGC-001 | Settings | | 設定 | 중 |
| 2 | LANGC-002 | Settings | | 一般 | 상 |

### Column Lookup Logic

```python
# Ưu tiên lookup by header name, fallback sang index
tc_no = str(row['TC No.']) if 'TC No.' in df.columns else str(row[1])
word_resx = row['Word(resx)'] if 'Word(resx)' in df.columns else row[2]
priority = row['Priority'] if 'Priority' in df.columns else row[5]
```

- Header names: `TC No.`, `Word(resx)`, `Priority`
- Nếu header không khớp → fallback sang column index (1, 2, 5)
- Text column (D hoặc E) luôn dùng index, không dùng header name

### skiprows Parameter

```python
df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=0)
```

- `skiprows=0` → **không skip row nào** → row đầu tiên được pandas tự động nhận là header
- Nếu Excel có row tiêu đề ở row 1 → OK (pandas dùng làm header)
- Nếu Excel không có header row → columns sẽ lấy giá trị row 1 làm header → fallback sang index

### Error Handling

| Scenario | Hành vi |
|----------|---------|
| Không chọn file | Error: `"Please select an Excel file."` |
| File không có sheet "Chinese" hoặc "Japanese" | Error: `"Excel file must contain sheets named 'Chinese' and 'Japanese'."` |
| File format không phải Excel | Exception: pandas ExcelFile error |
| Column thiếu | Fallback sang column index |
| Cell value = NaN (text column) | Import NaN as-is → check item Content = "nan" |
| Cell value = NaN (Word(resx)) | Kế thừa giá trị trước |
| Cell value = NaN (Priority) | Default `중 (Middle)` |
| Row thiếu TC No. | Fallback sang column index 1 |

---

## 2. Excel Loop (Test Data)

### Trigger

Script action `type="pre-loop"` trong `ui_runner.py:run_script()`

### Excel File Selection

```python
excel_path = action.get("file")         # Path lưu trong action
if not excel_path:
    excel_path = fd.askopenfilename(...)  # Mở file dialog nếu chưa set
```

- Nếu action có key `"file"` → dùng path đó
- Nếu không có → mở file dialog cho user chọn
- Nếu user cancel dialog → script fail: `"User cancelled Excel file selection"`

### Excel Read

```python
df = pd.read_excel(excel_path)
```

- **Không có sheet_name** → đọc sheet đầu tiên (default)
- **Không có skiprows** → row 1 là header
- **Không có dtype** → pandas tự infer types
- Toàn bộ file được đọc vào memory 1 lần

### Column Mapping trong Type Action

```python
if 'excel_col' in action and row is not None:
    excel_col = action['excel_col'].strip().upper()
    col_idx = ord(excel_col) - ord('A')  # A=0, B=1, C=2, ...
    value = str(row.iloc[col_idx])
    pyautogui.write(value)
```

| Excel Column Letter | col_idx | Mapping |
|--------------------|---------|---------|
| A | 0 | First column |
| B | 1 | Second column |
| C | 2 | Third column |
| ... | ... | ... |
| Z | 25 | 26th column |

- **Single letter only** (A-Z) — không hỗ trợ AA, AB, etc.
- `excel_col` được strip + uppercase trước khi convert
- Nếu col_idx vượt quá số columns → `IndexError` → value = `""`

### Loop Execution Flow

```
pre-loop action
  → đọc Excel file
  → collect tất cả actions đến post-loop
  → iterate mỗi row:
      → chạy tất cả enclosed actions với row data
      → time.sleep(delay) sau mỗi action
post-loop action
  → kết thúc loop, skip post-loop marker
```

### Sample Test Data Excel (Loop)

| A (Username) | B (Password) | C (Expected) |
|-------------|-------------|---------------|
| admin | pass123 | Welcome |
| user1 | test456 | Welcome |
| guest | guest789 | Access Denied |

- Trong script action: `{"type": "type", "excel_col": "A"}` → pyautogui.write("admin") cho row 1
- Header row (Username, Password, Expected) không phải data — pandas skip tự động

### Supported File Types

```python
filetypes=[("Excel files", "*.xlsx *.xls")]
```

- `.xlsx` (Open XML, via openpyxl)
- `.xls` (Legacy format, via xlrd)

### Error Handling (Loop)

| Scenario | Hành vi |
|----------|---------|
| User cancel file dialog | Script fail: `"User cancelled Excel file selection"` |
| File không tồn tại | Exception → script fail |
| File format sai | Exception → script fail |
| Column index out of range | `IndexError` caught → value = `""` |
| Cell value = NaN | `str(NaN)` → pyautogui.write("nan") |
| Empty cell | `str(None)` or `str("")` → pyautogui.write("") |
| No rows in Excel | Loop body không chạy lần nào → script tiếp tục bình thường |
| Missing post-loop action | Loop actions collect đến hết script → chạy tất cả trong loop |

---

## Limitations

1. **Import chỉ hỗ trợ 3 ngôn ngữ**: English, Chinese, Japanese — không có Korean
2. **Sheet names phải exact match**: "Chinese" và "Japanese" (case-sensitive)
3. **NaN handling không nhất quán**: Word(resx) NaN → inherit, Content NaN → import "nan", Priority NaN → default
4. **Excel loop single letter columns**: Chỉ A-Z (26 columns), không hỗ trợ multi-letter
5. **Không có data validation khi import**: Không kiểm tra duplicate TC No., không kiểm tra empty Content
6. **Không có progress indicator**: Import chạy synchronous, UI freeze nếu file lớn
