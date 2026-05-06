# OCR Rules

> Rules cho OCR validation pipeline. Áp dụng khi sửa `ui_runner.py:capture_check_region()` hoặc bất kỳ code nào liên quan OCR.

---

## 1. OCR Configuration — Không Sửa Nếu Chưa Xác Nhận

| Config | Current Value | Protected? |
|--------|--------------|------------|
| PSM mode | `--psm 7` (single text line) | **Yes** — thay đổi ảnh hưởng accuracy toàn bộ 2,399 items |
| OEM mode | Default (3 = LSTM + legacy) | **Yes** |
| Tesseract path | Hardcoded `C:\Program Files\Tesseract-OCR\tesseract.exe` | No — cần làm configurable (Phase 2.6) |
| Language map | `{"English": "eng", "Chinese": "chi_sim", "Japanese": "jpn"}` | **Chỉ thêm, không sửa/xóa** entries hiện có |
| API function | `image_to_string()` | Có thể đổi sang `image_to_data()` (Phase 2.5) |

## 2. Language Support

### Supported

| App Language | Tesseract Code | traineddata | Status |
|-------------|---------------|-------------|--------|
| English | `eng` | `eng.traineddata` | Stable |
| Chinese (Simplified) | `chi_sim` | `chi_sim.traineddata` | Stable |
| Japanese | `jpn` | `jpn.traineddata` | Stable |

### Not Supported

| Language | Issue | Fix |
|----------|-------|-----|
| Korean | UI editor có radio button nhưng `lang_map` thiếu entry → fallback `eng` | Thêm `"Korean": "kor"` + cài `kor.traineddata` |
| Chinese (Traditional) | Không có trong lang_map | Cần `chi_tra.traineddata` |
| Multi-language | 1 check item = 1 language | Giới hạn Tesseract |

### Rule khi thêm language mới

1. Thêm entry vào `lang_map` trong `capture_check_region()`
2. Cài traineddata tương ứng
3. Thêm radio button trong `ui_editor.py` nếu chưa có
4. Test với ít nhất 10 check items
5. **Không xóa/sửa entries hiện có** — backward compatibility

## 3. Image Capture Rules

### Current Implementation

```
PIL.ImageGrab.grab(bbox) → trực tiếp chụp vùng (x1,y1,x2,y2)
```

### Rules

| Rule | Lý do |
|------|-------|
| Dùng `ImageGrab.grab(bbox)`, KHÔNG chụp full screen rồi crop | Memory efficient, đã proven stable |
| Coordinates là absolute screen pixels | 2,399 items phụ thuộc hệ tọa độ này |
| Không validate bbox trước khi grab | Known limitation — (0,0,0,0) tạo ảnh rỗng |
| Save JPEG RGB trước khi OCR | Evidence image = raw screenshot |

### Coordinate Rules

| Rule | Chi tiết |
|------|---------|
| Source | `check_items.json` → `TopLeft (x/y)`, `BottomRight (x/y)` |
| Capture tool | F5 (TopLeft) + F6 (BottomRight) trong Check List tab |
| Dependency | Resolution + DPI scaling → đổi resolution = invalidate toàn bộ coordinates |
| Validation | **Hiện chưa có** — không check x1 < x2, y1 < y2, không check giá trị > 0 |

## 4. Matching Rules

### Current: Cascade Compare (v1.1)

```python
# OCR_CONFIG controls cascade — default all OFF = exact match only
exact → normalized (opt-in) → lowercase (opt-in)
```

### `OCR_CONFIG` (module-level trong `ui_runner.py`)

| Key | Default | Khi bật |
|-----|---------|---------|
| `normalize` | `False` | strip + collapse spaces + unicode NFC trước compare |
| `lowercase` | `False` | `.lower()` trước compare |

### Rules

| Aspect | Behavior | Protected? |
|--------|----------|------------|
| Default | Exact match (`==`) | **Yes** — KHÔNG đổi default |
| Normalize | Opt-in via `OCR_CONFIG["normalize"]` | Thêm OK, KHÔNG bật mặc định |
| Lowercase | Opt-in via `OCR_CONFIG["lowercase"]` | Thêm OK, KHÔNG bật mặc định |
| Strip detected | `.strip()` luôn chạy | **Yes** |
| `_normalize_text()` | `strip → collapse spaces → NFC` | Helper mới, dùng khi normalize=True |
| Return dict | 5 keys gốc + `Match_Exact`, `Match_Method` | **Không đổi/xóa keys gốc**, chỉ thêm |

### Rule quan trọng

- **Default behavior phải giữ exact match** — thay đổi default = ảnh hưởng tất cả scripts
- `OCR_CONFIG` nằm ở module level — có thể wire vào Settings tab trong future phase
- Return dict `{Label_ID, Expected, Detected, Match, ImagePath}` — **không đổi keys hiện có**, chỉ thêm keys mới
- `Match_Method` ghi lại method nào đã match: `"exact"`, `"normalized"`, `"lowercase"`

## 5. Preprocessing Rules

### Current: Không Có

```python
img.convert("RGB").save(save_path, "JPEG")  # Chỉ save, không preprocess
```

### Rules khi thêm preprocessing

| Rule | Lý do |
|------|-------|
| Preprocessing = opt-in, không mặc định | Thay đổi mặc định ảnh hưởng toàn bộ OCR results |
| Save ảnh GỐC trước khi preprocess | Evidence phải là raw screenshot |
| Nếu preprocess, save cả 2 ảnh (raw + processed) | Để debug false positives/negatives |
| Reference implementation | `testocr.py:14-24` (PaddleOCR preprocessing, cần adapt) |

## 6. Evidence Rules

### Image Evidence

| Rule | Chi tiết |
|------|---------|
| Folder | `CapturedImg/ocr_YYYYMMDD_HHMMSS/` — 1 folder per script run |
| Filename | `clean_filename(content).replace(" ", "_") + ".jpg"` |
| Save cả pass và fail | Tất cả check actions đều save image |
| Collision handling | **Không có** — cùng Content = overwrite |
| Retention | Không tự xóa — user quản lý |

### Excel Report Evidence

| Rule | Chi tiết |
|------|---------|
| File | `Result/ocr_result_report_YYYYMMDD_HHMMSS.xlsx` |
| Columns | `Label_ID, Expected, Detected, Match, ImagePath` — **không đổi** |
| Thêm columns mới | OK — append phía sau (backward compatible) |
| Contains | Tất cả results (cả pass và fail) |
| Save condition | Chỉ khi `results[]` không rỗng |

### Script Status Evidence

| Rule | Chi tiết |
|------|---------|
| Storage | `scripts.json` → `lastTestReport` (inline) |
| First-fail | Chỉ report mismatch đầu tiên trong status |
| History | **Không lưu** — chỉ last test report |
| Excel report có đầy đủ | Tất cả mismatches đều có trong Excel |

## 7. Cross-References

| Tài liệu | Nội dung |
|-----------|---------|
| [ocr_pipeline.md](../docs/ocr_pipeline.md) | OCR pipeline behavior, audit findings, gaps |
| [stabilization_plan.md](../docs/stabilization_plan.md) | Phase 2 roadmap cho OCR improvements |
| [stability.md](stability.md) | Protected areas chung |
