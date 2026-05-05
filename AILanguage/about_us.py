import tkinter as tk


def show_about_us(parent):
    frame = tk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

    tk.Label(frame, text="DPI Automation Tool", font=("Arial", 20, "bold")).pack(pady=(10, 5))

    info_frame = tk.Frame(frame)
    info_frame.pack(anchor="w", padx=20, pady=(10, 0))

    fields = [
        ("Version:", "1.0.0"),
        ("Build Date:", "2026-04-19"),
        ("Developed by:", "Lynn Nguyen"),
        ("Role:", "SQA Engineer (vnsqa team)"),
    ]
    for label_text, value_text in fields:
        row = tk.Frame(info_frame)
        row.pack(anchor="w", pady=2)
        tk.Label(row, text=label_text, font=("Arial", 11, "bold"), width=14, anchor="w").pack(side=tk.LEFT)
        tk.Label(row, text=value_text, font=("Arial", 11)).pack(side=tk.LEFT)

    tk.Label(frame, text="Description", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(20, 5))
    tk.Label(
        frame,
        text="DPI Automation Tool is a desktop-based QA automation solution designed to test\n"
             "multilingual user interfaces in Display Product Inspection (DPI) systems.\n\n"
             "The tool enables recording and replaying user interactions, combined with\n"
             "OCR-based validation to ensure accurate rendering of multilingual content\n"
             "(Chinese, Japanese, English) within the application UI.",
        font=("Arial", 11), justify=tk.LEFT, wraplength=600
    ).pack(anchor="w", padx=20)

    tk.Label(frame, text="Key Features", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
    features = [
        "Record and replay UI interaction sequences",
        "Image-based and coordinate-based automation",
        "OCR validation for multilingual text",
        "Batch execution via Excel test data",
        "Automated pass/fail reporting",
    ]
    for feat in features:
        tk.Label(frame, text=f"•  {feat}", font=("Arial", 11), justify=tk.LEFT).pack(anchor="w", padx=30)

    tk.Label(frame, text="Use Case", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
    tk.Label(
        frame,
        text="Designed for QA engineers to validate UI consistency and localization accuracy\n"
             "in DPI software environments where traditional web automation tools are not applicable.",
        font=("Arial", 11), justify=tk.LEFT, wraplength=600
    ).pack(anchor="w", padx=20)

    tk.Label(frame, text="Contact", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
    tk.Label(frame, text="Email: lynn.nguyen@kohyoung.com", font=("Arial", 11)).pack(anchor="w", padx=20)

    tk.Label(
        frame,
        text="\u00a9 2026 Lynn Nguyen. All rights reserved.",
        font=("Arial", 10), fg="gray"
    ).pack(side=tk.BOTTOM, pady=10)
