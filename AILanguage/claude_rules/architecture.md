# Architecture

> Chi tiết đầy đủ: [`docs/architecture.md`](../docs/architecture.md)

## Quick Reference

```
UI Layer              →  Logic Layer           →  Data Layer
────────────────────     ───────────────────      ──────────────
main.py                  script_manager.py        scripts.json
ui_script_list.py        check_item_manager.py    check_items.json
ui_editor.py             setting_manager.py       settings.csv
ui_runner.py             utils.py                 Log/
ui_check_list.py
ui_check_editor.py
import_dialog.py
```

Entry point: `main.py` → `ScriptRunnerApp` (Tkinter sidebar navigation, tabs)

## Rules

- **11 core files** — không đổi tên, không tách/gộp (xem [stability.md](stability.md))
- **Import chain** — xem dependency map trong `docs/architecture.md`
- **Data flow** — xem read/write paths trong `docs/architecture.md`
