# AI Development Workflow Rules

> Project: DPI Automation Tool — Internal desktop utility app
> Context: Project chủ yếu implement bởi Claude Code. User không trực tiếp code.
> Mục tiêu: Stability > architecture perfection. Predictable behavior > over-engineering.

---

## 1. Investigation First

**Nguyên tắc**: Không assume root cause. Không kết luận sớm.

### Bắt buộc kiểm tra trước khi kết luận:
- `git log` — commit history visible
- `git reflog --all` — orphan commits, reset history, lost work
- `git stash list` — stashed changes
- `git branch -a` — tất cả branches (local + remote)
- `__pycache__/*.pyc` — compiled bytecode có thể chứa logic cũ
- Runtime state — widget/process/file thực tế tại thời điểm chạy

### Với UI issues, verify đầy đủ:
- Widget creation — code tạo widget có được execute không?
- Runtime visibility — widget `.winfo_viewable()`, `.winfo_ismapped()`
- Layout — `.pack()`, `.grid()`, `.place()` có đúng không?
- Geometry — widget có bị che, overlap, hoặc nằm ngoài viewport?
- Dynamic rendering — widget có tạo conditional (if/else, feature flag)?
- Git history — file từng có code tạo widget? Bị xóa khi nào?
- Reflog — có orphan commit chứa code bị mất?
- Branch/build mismatch — đang chạy binary từ branch khác?

### Với screenshot evidence:
- Nếu user cung cấp screenshot chứng minh feature tồn tại → **KHÔNG ĐƯỢC** kết luận "chưa từng tồn tại"
- Phải reconcile screenshot vs runtime vs source trước khi kết luận
- Nếu mâu thuẫn → report cả hai phía kèm evidence, yêu cầu user clarify

### Anti-patterns:
- Chỉ grep string trong current HEAD → kết luận feature không tồn tại
- Chỉ đọc `git log` (bỏ qua reflog) → miss orphan commits
- Chỉ đọc source code → bỏ qua runtime conditional logic

---

## 2. Minimal Change Policy

**Nguyên tắc**: Smallest viable change. Patch, không rewrite.

### Rules:
- Dùng **Edit tool** (patch) thay vì **Write tool** (full rewrite) cho file hiện có
- Chỉ sửa đúng phần liên quan đến task, không touch phần khác
- Mỗi thay đổi phải có mục tiêu rõ ràng, có thể verify độc lập
- Reuse existing code, layout, components, patterns tối đa

### Không được:
- Rewrite toàn bộ file khi chỉ cần thêm/sửa vài dòng
- Cleanup/refactor code xung quanh "tiện tay"
- Optimize performance ngoài scope task
- Đổi architecture/pattern nếu chưa được yêu cầu rõ ràng
- Rename variables/functions không liên quan
- Thêm abstraction layer mới khi chưa cần

### Ví dụ đúng:
```
Task: Thêm button "Export TSV" vào Check List
Đúng: Edit ui_check_list.py, thêm 1 function + 1 tk.Button
Sai:  Rewrite toàn bộ ui_check_list.py, refactor button layout, thêm toolbar class
```

---

## 3. Approval Before Write

**Nguyên tắc**: Report trước, write sau.

### Trước khi sửa code, Claude phải báo:
1. **File(s)** sẽ sửa — đường dẫn đầy đủ
2. **Function(s)** sẽ sửa — tên function, line number
3. **Patch scope** — thêm/sửa/xóa bao nhiêu dòng, ở đâu
4. **Risk level** — Low (additive) / Medium (modify existing) / High (delete/replace)
5. **Regression possibility** — feature nào có thể bị ảnh hưởng

### Large patch (>30 dòng hoặc >2 files):
- Cần **explicit approval** trước khi write
- Liệt kê từng file + scope thay đổi
- User phải confirm "OK" hoặc "Approved" trước khi proceed

### Không cần approval:
- Fix typo/syntax error rõ ràng (1-2 dòng)
- Thêm import statement đã xác định cần
- Update comment/docstring

### Không bao giờ được:
- Tự ý replace toàn bộ file lớn bằng Write tool
- Sửa nhiều files cùng lúc mà chưa báo trước
- Xóa code block mà chưa confirm lý do

---

## 4. Phase Isolation

**Nguyên tắc**: Mỗi phase riêng biệt. Không trộn lẫn.

### Phases:
1. **Investigation** — đọc code, tìm root cause, thu thập evidence
2. **Report** — báo cáo findings, propose solutions
3. **Plan** — user approve solution, xác định scope
4. **Implement** — viết code theo plan đã approved
5. **Test** — verify implementation, regression check
6. **Review** — user review kết quả

### Không được merge vào cùng 1 task:
- Feature implementation + refactor
- Bug fix + optimization
- Cleanup + architecture change
- Investigation + implementation (phải tách)

### Ví dụ đúng:
```
Phase 1: Implement Export TSV → test → user review → done
Phase 2: Restore Export Excel → test → user review → done
Không: Implement cả TSV + Excel + refactor import_dialog cùng lúc
```

### Khi user request nhiều thứ:
- Tách thành phases rõ ràng
- Implement từng phase, verify xong mới chuyển phase tiếp
- Nếu phase trước fail → fix xong mới tiếp phase sau

---

## 5. Regression Safety

**Nguyên tắc**: Preserve existing behavior. Backward compatibility first.

### Rules:
- Không đổi function signature hiện có trừ khi cần thiết (thêm param optional = OK)
- Không đổi return type/structure hiện có (thêm key mới = OK)
- Không rename/remove existing UI controls nếu chưa approved
- Không đổi existing keyboard shortcuts, hotkeys, event bindings
- Không đổi file format, encoding, delimiter của data files hiện có

### Sau mỗi thay đổi, verify:
- Existing workflow vẫn hoạt động (run script, check OCR, export report)
- UI controls hiện có vẫn ở đúng vị trí, đúng behavior
- Data files (scripts.json, check_items.json, settings.csv) vẫn load được
- Import/Export features hiện có vẫn hoạt động

### Khi cần thay đổi breaking:
- Report rõ: "Thay đổi này sẽ break X, Y, Z"
- Đề xuất migration path hoặc backward compatibility layer
- Chờ explicit approval

---

## 6. Import/Export Conventions

**Nguyên tắc**: TSV/TXT là stable format. Excel là convenience.

### Format priority:
1. **TSV** (tab-separated values) — primary internal exchange format
   - Encoding: UTF-8 with BOM (`﻿` prefix)
   - Delimiter: Tab (`\t`)
   - DRM-safe: không bị Fasoo DRM encrypt
   - Human-readable, diff-friendly, version control friendly
2. **Excel** (.xlsx) — convenience/compatibility format
   - Cần `openpyxl`/`pandas`
   - Có thể bị DRM encrypt → cần lưu ý workflow

### Import rules:
- Auto-detect format (TSV vs Excel vs multilang sheets)
- Validate schema/headers trước khi import
- Report mismatches rõ ràng (missing columns, wrong format)
- Round-trip guarantee: export → import → data identical

### Export rules:
- Headers chuẩn: `Lang`, `TC No.`, `Word(resx)`, `Content`, `Priority`, `TopLeft (x)`, `TopLeft (y)`, `BottomRight (x)`, `BottomRight (y)`
- TSV export phải readable bằng Excel, Notepad, VS Code
- Excel export nên có auto-fit column width

### DRM awareness:
- Tránh workflow chỉ phụ thuộc vào .xlsx nếu có DRM
- Cung cấp TSV alternative cho mọi Excel feature

---

## 7. Token Efficiency

**Nguyên tắc**: Tiết kiệm context. Patch nhỏ. Không lặp.

### Rules:
- Patch nhỏ thay vì đọc/ghi toàn bộ file
- Đọc file có target (`offset`/`limit`) khi biết vị trí cần xem
- Reuse existing code/functions — không tạo mới khi đã có implementation tương đương
- Không generate large rewrites khi patch nhỏ đủ
- Không duplicate logic đã có

### Không được:
- Đọc file 300+ dòng rồi viết lại toàn bộ chỉ để sửa 5 dòng
- Tạo abstraction/wrapper mới cho logic chỉ dùng 1 lần
- Refactor large unrelated sections "tiện thể"
- Copy-paste logic từ nơi khác thay vì import/call

### Ưu tiên:
- Iterative implementation — từng bước nhỏ, verify, rồi tiếp
- Incremental patches — mỗi Edit call sửa đúng 1 thứ
- Targeted reads — đọc đúng phần cần, không đọc toàn bộ

---

## 8. Runtime Verification

**Nguyên tắc**: Code nói gì không quan trọng bằng app chạy thực tế.

### Với UI tasks, verify:
- Widget tồn tại tại runtime — `parent.winfo_children()`
- Widget visible — `.winfo_viewable()`, `.winfo_ismapped()`
- Layout đúng — `.winfo_x()`, `.winfo_y()`, `.winfo_width()`, `.winfo_height()`
- Event binding hoạt động — `.bind_all()`, `command=` callback

### Với logic tasks, verify:
- Function return value đúng type/structure
- Exception handling hoạt động (try/except paths)
- Edge cases: empty input, None, missing key

### Không chỉ dựa vào:
- Source code reading (code path có thể conditional)
- Static analysis (import có thể bị shadow)
- Grep results (string match không = runtime behavior)

---

## 9. AI Coding Workflow

**Nguyên tắc**: Tuân thủ workflow 6 bước. Không skip.

### Standard workflow cho mọi task:

```
Step 1: INVESTIGATE
  - Đọc code liên quan
  - Check git history/reflog
  - Thu thập evidence
  - Output: findings report

Step 2: REPORT
  - Báo cáo findings cho user
  - Nêu root cause (với evidence)
  - Nêu assumptions và uncertainty
  - Output: investigation summary

Step 3: PROPOSE
  - Đề xuất 1-3 solutions
  - Mỗi solution: scope, risk, effort
  - Recommend solution tối ưu
  - Output: solution options

Step 4: APPROVE
  - User chọn solution
  - Confirm scope, phase breakdown
  - Claude confirm understanding
  - Output: approved plan

Step 5: IMPLEMENT
  - Implement theo plan đã approved
  - Minimal patches, phase isolation
  - Report trước mỗi file change
  - Output: working code

Step 6: VERIFY
  - Run tests (unit + regression)
  - Verify UI nếu có thay đổi UI
  - Confirm existing features không bị ảnh hưởng
  - Output: verification report
```

### Khi nào có thể skip:
- Typo fix → skip Steps 1-4, trực tiếp fix + verify
- User đã cung cấp đầy đủ analysis → skip Step 1
- User chỉ định rõ solution → skip Step 3

### Khi nào KHÔNG ĐƯỢC skip:
- UI issues → luôn cần Step 1 (investigation) + Step 6 (runtime verify)
- Breaking changes → luôn cần Step 4 (approval)
- Multi-file changes → luôn cần Step 3 (propose) + Step 4 (approve)

---

## 10. Desktop Utility Stability

**Nguyên tắc**: Stability > architecture perfection. Simple > clever.

### Project characteristics:
- Internal desktop utility app — không phải SaaS, không phải library
- User base nhỏ, known — QA team Koh Young
- Tkinter GUI — simple, stable, no framework magic
- File-based data — JSON, CSV, không database

### Stability rules:
- Ưu tiên maintainability đơn giản
- Tránh unnecessary framework patterns (MVC, observer, factory...)
- Tránh aggressive refactoring — code đang chạy ổn = không cần refactor
- Preserve current UX/workflow — user đã quen cách dùng hiện tại
- Predictable behavior > elegant architecture

### Không được:
- Introduce design patterns chỉ vì "best practice"
- Migrate từ Tkinter sang framework khác
- Thêm dependency mới nếu stdlib đủ dùng
- Abstract hóa logic chỉ dùng 1 chỗ
- Tạo class hierarchy phức tạp cho simple functions

### Khi thêm feature mới:
- Follow existing code style/pattern trong project
- Đặt code gần code liên quan (cùng file, cùng section)
- Dùng cùng UI patterns đang có (tk.Button, messagebox, filedialog)
- Test trên Windows — đây là target platform duy nhất
