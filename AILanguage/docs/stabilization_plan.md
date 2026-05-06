# Stabilization Plan

> DPI Automation Tool v1.0.0 — Kế hoạch ổn định hóa và cải thiện từng bước.
> Tài liệu này tổng hợp toàn bộ analysis từ 5 docs hiện có + stability rules.
> **Nguyên tắc: Không refactor. Chỉ cải thiện từng bước nhỏ, backward compatible.**

---

## 1. Current Stable Features

### Chức năng đang hoạt động ổn định

| # | Feature | Module chịu trách nhiệm | Status |
|---|---------|-------------------------|--------|
| 1 | **Script automation** — 8 action types: click, type, hotkey, scroll, check, run_script, cmd_run, pre-loop/post-loop | `ui_runner.py:do_action()`, `ui_editor.py` | Stable |
| 2 | **OCR validation** — Chụp vùng màn hình, chạy Tesseract (English/Chinese/Japanese), so sánh exact match | `ui_runner.py:capture_check_region()` | Stable (known limitations) |
| 3 | **Excel loop** — Đọc Excel file, iterate rows, fill form fields theo column mapping A-Z | `ui_runner.py:run_script()` (pre-loop/post-loop) | Stable |
| 4 | **Check item management** — CRUD, import from Excel, filter, F5/F6 position capture | `ui_check_list.py`, `ui_check_editor.py`, `import_dialog.py` | Stable |
| 5 | **Script management** — CRUD, copy, reorder, checkbox selection, batch run, 5s countdown | `ui_script_list.py`, `script_manager.py` | Stable |
| 6 | **Report export** — OCR result Excel report + script status JSON in scripts.json | `ui_runner.py` (Excel), `script_manager.py` (JSON) | Stable |
| 7 | **Settings** — Resolution, start_app path, delay | `setting_manager.py`, `main.py` (Setting tab) | Stable |
| 8 | **Logging** — Daily log file, append mode, DEBUG level | `utils.py:init_logging()` | Stable |

### Data Assets

| Asset | Số lượng | File |
|-------|---------|------|
| Check items | 2,399 (801 EN + 799 CN + 799 JP) | `check_items.json` |
| Scripts | 9 scripts + script_order | `scripts.json` |
| Settings | 3 fields (resolution, start_app, delay) | `settings.csv` |

### Core File Inventory

11 core Python files, tất cả đều active và import lẫn nhau:

```
main.py → ui_script_list.py → ui_editor.py → ui_runner.py
                             → script_manager.py
        → ui_check_list.py  → ui_check_editor.py
                             → import_dialog.py
        → about_us.py
        → setting_manager.py
        → check_item_manager.py
        → utils.py (shared by all)
```

Chi tiết dependency: xem `docs/architecture.md` → Import Chain.

---

## 2. Known Risks

### 2.1 OCR Accuracy

> Source: `docs/ocr_pipeline.md`

| Risk | Severity | Mô tả |
|------|----------|--------|
| Không có image preprocessing | **Critical** | Không grayscale, không contrast, không threshold → accuracy phụ thuộc hoàn toàn screenshot quality |
| Exact string match | **Critical** | `detected_text == content` — single char error = FAIL, trailing space = FAIL, case difference = FAIL |
| Không có confidence scoring | **High** | Không dùng `image_to_data()` → không biết OCR đọc "gần đúng" hay "sai hoàn toàn" |
| Korean unsupported | **High** | UI editor có Korean radio button nhưng `lang_map` thiếu entry → fallback `eng` → OCR sai hoàn toàn |
| Expected text không strip | **Medium** | Chỉ `.strip()` detected text, expected text dùng raw → whitespace mismatch |

### 2.2 Runtime Reliability

> Source: `docs/runtime_flow.md`

| Risk | Severity | Mô tả |
|------|----------|--------|
| Không có retry logic | **High** | Mỗi action chạy 1 lần. App chưa load xong khi click → fail, không retry |
| Không có timeout per action | **High** | 1 action hang → script hang vĩnh viễn |
| UI freeze khi chạy script | **Medium** | Main thread blocked bởi `run_script()`, không cancel được |
| Stale "Running" status | **Medium** | Nếu crash giữa chừng → testStatus = "Running" mãi mãi, không recovery |
| First-fail chỉ report 1 mismatch | **Medium** | Phải chạy lại nhiều lần để tìm tất cả OCR mismatches |

### 2.3 Data Integrity

> Source: `docs/excel_format.md`

| Risk | Severity | Mô tả |
|------|----------|--------|
| Import NaN Content | **High** | Cell rỗng trong cột text → import thành string `"nan"` → OCR check luôn fail |
| Không validate duplicate TC No. | **Medium** | Import sau silently overwrite import trước nếu trùng TC No. |
| Screenshot filename collision | **Medium** | 2 check items cùng Content → image bị overwrite |
| pyautogui.write() cho CJK | **Medium** | `pyautogui.write()` chỉ hỗ trợ ASCII → CJK typing trong loop fail |

### 2.4 Deployment

> Source: `docs/architecture.md`

| Risk | Severity | Mô tả |
|------|----------|--------|
| Hardcoded Tesseract path | **High** | `r"C:\Program Files\Tesseract-OCR\tesseract.exe"` — deploy sang máy khác phải sửa code |
| Absolute pixel coordinates | **High** | 2,399 items có pixel coordinates → đổi resolution hoặc DPI scaling = toàn bộ check sai |
| Single letter column mapping | **Low** | Excel loop chỉ map A-Z (26 columns) → test data >26 columns không thể dùng |

---

## 3. Priority Order

| Priority | Category | Lý do | Impact |
|----------|----------|-------|--------|
| **P1** | OCR Accuracy | Core value của tool. Nếu OCR sai → tool không đáng tin cậy | Toàn bộ 2,399 check items bị ảnh hưởng |
| **P2** | Resilience | Report toàn bộ mismatches, configurable paths → giảm manual work | Giảm số lần chạy lại script |
| **P3** | Data Integrity | Bảo vệ 2,399 check items khỏi import bugs | Ngăn data corruption |
| **P4** | Maintainability | Dễ maintain lâu dài, nhưng không urgent vì code đang hoạt động | Long-term |

---

## 4. 4-Phase Stabilization Roadmap

### Phase 1: Document Current Behavior ✅ DONE

| Task | File | Status |
|------|------|--------|
| Architecture documentation | `docs/architecture.md` | ✅ Done |
| Runtime flow documentation | `docs/runtime_flow.md` | ✅ Done |
| OCR pipeline documentation | `docs/ocr_pipeline.md` | ✅ Done |
| Excel format documentation | `docs/excel_format.md` | ✅ Done |
| Report format documentation | `docs/report_format.md` | ✅ Done |
| CLAUDE.md update | `CLAUDE.md` | ✅ Done |
| Stability rules | `claude_rules/stability.md` | ✅ Done |
| Stabilization plan | `docs/stabilization_plan.md` | ✅ Done |

### Phase 2: Stabilize OCR/Compare

> Target files: `ui_runner.py`, `utils.py`
> Priority: **P1 + P2**

| # | Task | Mô tả | Risk nếu không làm |
|---|------|-------|---------------------|
| 2.1 | Strip expected text | Thêm `.strip()` cho `content` trước khi compare | Whitespace mismatch false negatives |
| 2.2 | Case-insensitive option | Thêm option compare `lower()` (opt-in, không break existing) | Case difference = FAIL |
| 2.3 | Image preprocessing | Grayscale + contrast enhancement trước OCR | Low accuracy với dark theme, small font |
| 2.4 | Korean lang_map | Thêm `"Korean": "kor"` vào `lang_map` + cài `kor.traineddata` | Korean check items sai hoàn toàn |
| 2.5 | Confidence score | Dùng `image_to_data()` thay vì `image_to_string()`, log confidence | Không phân biệt "gần đúng" vs "sai hoàn toàn" |
| 2.6 | Configurable Tesseract path | Đọc từ `settings.csv` hoặc environment variable | Deploy fail trên máy khác |

**Nguyên tắc Phase 2:**
- Mỗi task = 1 commit riêng biệt
- Không thay đổi function signature `capture_check_region(check_item, timestamp_folder)`
- Không thay đổi return format `{Label_ID, Expected, Detected, Match, ImagePath}`
- Có thể thêm fields mới vào return dict (backward compatible)

### Phase 3: Excel/Report

> Target files: `import_dialog.py`, `ui_runner.py`
> Priority: **P2 + P3**

| # | Task | Mô tả | Risk nếu không làm |
|---|------|-------|---------------------|
| 3.1 | Validate NaN Content | Skip hoặc warn rows có Content = NaN khi import | Check items với Content "nan" |
| 3.2 | Validate duplicate TC No. | Warn user khi TC No. đã tồn tại, cho chọn overwrite/skip | Silent data overwrite |
| 3.3 | Report ALL mismatches | Thay đổi post-execution check: collect tất cả ❌, không return ở first | Phải chạy nhiều lần |
| 3.4 | Summary statistics | Thêm summary row: total checks, pass count, fail count, pass rate | Thiếu overview |
| 3.5 | Filename collision handling | Thêm suffix counter nếu filename trùng | Image bị overwrite |

**Nguyên tắc Phase 3:**
- Không đổi Excel import sheet names ("Chinese"/"Japanese")
- Không đổi column positions (B=TC No., C=Word(resx), D=English, E=Chinese/Japanese)
- Không đổi report columns (Label_ID, Expected, Detected, Match, ImagePath) — chỉ thêm columns mới
- Import modes (Delete All / Append) giữ nguyên

### Phase 4: Improve Maintainability

> Target files: `ui_runner.py`, `script_manager.py`
> Priority: **P4**

| # | Task | Mô tả | Dependency |
|---|------|-------|------------|
| 4.1 | Tách OCR module | Extract OCR logic từ `ui_runner.py` thành `ocr_engine.py` | Phase 2 done |
| 4.2 | Unit tests | Tests cho `script_manager.py`, `check_item_manager.py`, `setting_manager.py` | None |
| 4.3 | Stale status recovery | Detect "Running" status khi app start → reset to "Not Tested" | None |
| 4.4 | Structured logging | Thêm context fields: script_name, action_type, step_num | None |

**Nguyên tắc Phase 4:**
- Phase 4 chỉ bắt đầu khi Phase 2 + 3 ổn định
- Tách module phải giữ nguyên public API
- Unit tests không yêu cầu Tesseract installed (mock OCR)

---

## 5. Files/Modules Cần Xử Lý Trước

| Priority | File | Phase | Lý do | Thay đổi dự kiến |
|----------|------|-------|-------|-------------------|
| **1** | `ui_runner.py` | 2, 3 | Core OCR pipeline + report logic — cải thiện accuracy là ưu tiên #1 | preprocessing, matching, confidence, report all mismatches |
| **2** | `utils.py` | 2 | Tesseract path configurable, shared across modules | Thêm function đọc Tesseract path từ config |
| **3** | `import_dialog.py` | 3 | NaN Content bug + duplicate TC No. validation | Thêm validation trong `import_sheet()` |
| **4** | `script_manager.py` | 3, 4 | Stale status recovery + report improvements | Thêm status check khi load |

### Files KHÔNG cần sửa (các phase)

| File | Lý do giữ nguyên |
|------|-------------------|
| `main.py` | Entry point ổn định, chỉ gọi các modules |
| `ui_script_list.py` | UI layer, chỉ cần sửa nếu UI thay đổi |
| `ui_editor.py` | Script editor ổn định |
| `ui_check_list.py` | Check list UI ổn định |
| `ui_check_editor.py` | Check editor ổn định |
| `about_us.py` | Static content |
| `check_item_manager.py` | Simple load/save, không có logic phức tạp |
| `setting_manager.py` | Simple load/save (trừ khi thêm Tesseract path setting) |

---

## 6. Phần Tuyệt Đối Không Được Sửa Nếu Chưa Xác Nhận

### Data Formats

| Protected Area | Chi tiết | Hậu quả nếu sửa |
|----------------|----------|------------------|
| `check_items.json` key names | `Lang`, `TC No.`, `Word(resx)`, `Content`, `Priority`, `TopLeft (x)`, `TopLeft (y)`, `BottomRight (x)`, `BottomRight (y)` | **Mất toàn bộ 2,399 check items** |
| `scripts.json` structure | `{"scripts": {...}, "script_order": [...]}` + per-script keys: `actions`, `created_at`, `modified_at`, `testStatus`, `lastTestedAt`, `lastTestReport` | **Mất toàn bộ 9 scripts** |
| `settings.csv` field names | `resolution`, `start_app`, `delay` | **App crash khi start** |
| Report Excel columns | `Label_ID`, `Expected`, `Detected`, `Match`, `ImagePath` | **Phá vỡ downstream tools** |

### Code Structure

| Protected Area | Chi tiết | Hậu quả nếu sửa |
|----------------|----------|------------------|
| 11 core file names | `main.py`, `utils.py`, `script_manager.py`, `check_item_manager.py`, `setting_manager.py`, `ui_script_list.py`, `ui_runner.py`, `ui_editor.py`, `ui_check_list.py`, `ui_check_editor.py`, `import_dialog.py` | **Import chain phá vỡ → build fail** |
| Function signatures cross-module | `run_script(actions, scripts, check_items, delay)`, `capture_check_region(check_item, timestamp_folder)`, `do_action(action, scripts, check_items, results, timestamp_folder, delay, row=None)` | **Runtime crash** |
| Excel import sheet names | `"Chinese"`, `"Japanese"` (case-sensitive) | **Import fail** |
| TC No. transformation | English: `tc_no.replace("C", "E", 1)` | **TC No. mismatch** giữa import và lookup |
| Coordinate system | Absolute screen pixels trong `TopLeft (x/y)`, `BottomRight (x/y)` | **Toàn bộ 2,399 OCR check positions sai** |
| OCR config | `--psm 7` (single text line mode) | **OCR accuracy thay đổi không kiểm soát** |

### Legacy Files

| File | Lý do giữ nguyên |
|------|-------------------|
| `check_label.py` | Standalone OCR test, có thể dùng reference |
| `testocr.py` | PaddleOCR experiment, alternative OCR approach |
| `mouse_tracker.py` | Standalone utility |
| `Label_test.py` | Early prototype, historical reference |
| `test.py` | Ad-hoc demo |

---

## 7. Checklist Trước Khi Sửa Code

> Áp dụng cho **mọi** thay đổi code trong project. Hoàn thành tất cả items trước khi commit.

### Pre-Implementation

- [ ] **Đọc `claude_rules/stability.md`** — nắm 6 nguyên tắc bắt buộc
- [ ] **Đọc docs liên quan** — tùy scope: `ocr_pipeline.md`, `excel_format.md`, `report_format.md`, `runtime_flow.md`, `architecture.md`
- [ ] **Xác nhận scope** — 1 commit = 1 mục tiêu duy nhất, không bundle
- [ ] **Xác nhận thuộc phase nào** trong roadmap (Phase 2/3/4)

### During Implementation

- [ ] **Backward compatibility** — data hiện có (2,399 check items, 9 scripts, settings) vẫn hoạt động
- [ ] **Function signatures** — không thay đổi signatures của functions được gọi từ module khác
- [ ] **Import chain** — không phá vỡ (kiểm tra `docs/architecture.md` → Import Chain)
- [ ] **Data format** — không đổi key names trong JSON/CSV, không đổi report columns

### Pre-Commit

- [ ] **Test với data thật** — chạy app với 2,399 check items và 9 scripts hiện có
- [ ] **Verify report format** — 5 columns giữ nguyên: Label_ID, Expected, Detected, Match, ImagePath
- [ ] **Git diff review** — chỉ files đúng mục tiêu, không có thay đổi ngoài scope
- [ ] **Chạy `python main.py`** — app start bình thường, navigate tất cả 4 tabs

---

## Cross-References

| Tài liệu | Nội dung liên quan |
|-----------|--------------------|
| [architecture.md](architecture.md) | Module map, dependency map, data flow |
| [runtime_flow.md](runtime_flow.md) | App start → script execution → error handling |
| [ocr_pipeline.md](ocr_pipeline.md) | Image capture → OCR → compare → evidence |
| [excel_format.md](excel_format.md) | Import format, loop format, column mapping |
| [report_format.md](report_format.md) | Excel report, JSON status, pass/fail logic |
| [stability.md](../claude_rules/stability.md) | 6 stability rules, risk table, roadmap overview |
