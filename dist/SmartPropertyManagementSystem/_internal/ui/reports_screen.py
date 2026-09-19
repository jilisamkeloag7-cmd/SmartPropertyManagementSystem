print(">>> reports_screen.py V1 <<<")

import os
import subprocess
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt
from Controllers.report_controller import ReportController


REPORTS = [
    ("📊", "Executive Summary",   "High-level counts across all entities",   "summary"),
    ("🏠", "Property Report",     "Full list of properties with status",     "property"),
    ("📄", "Lease Report",        "All leases with dates, rent and status",  "lease"),
    ("💰", "Payment Report",      "All payments with due/paid and status",   "payment"),
    ("🔧", "Maintenance Report",  "All maintenance requests with priority",  "maintenance"),
]


class ReportsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = ReportController()
        self.user_data = None
        self._build()

    # ------------------------------------------------------------------ API
    def set_user(self, user_data: dict):
        self.user_data = user_data
        self._apply_role_ui()
        self._load_recent()

    # ------------------------------------------------------------------ UI
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # ---- Header
        header = QHBoxLayout()
        title = QLabel("📊 Reports")
        title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2c3e50;"
        )
        header.addWidget(title)
        header.addStretch()

        btn_dashboard = QPushButton("← Dashboard")
        btn_dashboard.setStyleSheet(
            "background: transparent; color: #7f8c8d; border: none; "
            "font-size: 13px; padding: 6px 10px;"
        )
        btn_dashboard.clicked.connect(self._go_dashboard)
        header.addWidget(btn_dashboard)

        layout.addLayout(header)

        subtitle = QLabel(
            "Generate PDF reports. Files are saved to "
            "Documentation/reports/ in your project folder."
        )
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(subtitle)

        layout.addSpacing(6)

        # ---- Report cards (2-column grid)
        grid = QHBoxLayout()
        grid.setSpacing(14)

        left_col = QVBoxLayout()
        left_col.setSpacing(12)
        right_col = QVBoxLayout()
        right_col.setSpacing(12)

        for idx, (icon, name, desc, key) in enumerate(REPORTS):
            card = self._build_card(icon, name, desc, key)
            if idx % 2 == 0:
                left_col.addWidget(card)
            else:
                right_col.addWidget(card)

        left_col.addStretch()
        right_col.addStretch()
        grid.addLayout(left_col, stretch=1)
        grid.addLayout(right_col, stretch=1)
        layout.addLayout(grid)

        # ---- Recent files
        layout.addSpacing(14)
        recent_lbl = QLabel("Recently Generated")
        recent_lbl.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2c3e50;"
        )
        layout.addWidget(recent_lbl)

        self.recent_frame = QFrame()
        self.recent_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #ecf0f1;
            }
        """)
        self.recent_layout = QVBoxLayout(self.recent_frame)
        self.recent_layout.setContentsMargins(18, 14, 18, 14)
        self.recent_layout.setSpacing(6)
        layout.addWidget(self.recent_frame, stretch=1)

    def _build_card(self, icon, name, desc, key):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #ecf0f1;
            }
            QFrame:hover {
                border-color: #3498db;
            }
        """)
        card.setMinimumHeight(90)

        inner = QHBoxLayout(card)
        inner.setContentsMargins(16, 14, 16, 14)
        inner.setSpacing(14)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 24px;")
        inner.addWidget(icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #2c3e50;"
        )
        text_col.addWidget(name_lbl)
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("font-size: 11px; color: #7f8c8d;")
        desc_lbl.setWordWrap(True)
        text_col.addWidget(desc_lbl)
        inner.addLayout(text_col, stretch=1)

        btn = QPushButton("Generate")
        btn.setFixedSize(100, 36)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white;
                border: none; border-radius: 8px;
                font-size: 12px; font-weight: bold;
            }
            QPushButton:hover   { background-color: #2980b9; }
            QPushButton:pressed { background-color: #2471a3; }
        """)
        btn.clicked.connect(lambda checked, k=key: self._on_generate(k))
        inner.addWidget(btn)

        return card

    # ------------------------------------------------------------------ role UI
    def _apply_role_ui(self):
        # All roles may generate. In polish pass, restrict to admin/manager if needed.
        pass

    # ------------------------------------------------------------------ recent list
    def _load_recent(self):
        # Clear everything
        while self.recent_layout.count():
            item = self.recent_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        try:
            from Services.report_service import REPORTS_DIR
            if not os.path.isdir(REPORTS_DIR):
                raise FileNotFoundError
            files = sorted(
                [f for f in os.listdir(REPORTS_DIR) if f.endswith(".pdf")],
                key=lambda f: os.path.getmtime(os.path.join(REPORTS_DIR, f)),
                reverse=True,
            )[:8]
        except Exception:
            files = []

        if not files:
            lbl = QLabel("No reports generated yet. Use the buttons above.")
            lbl.setStyleSheet("color: #95a5a6; font-size: 12px;")
            self.recent_layout.addWidget(lbl)
            return

        for f in files:
            row = QHBoxLayout()
            name = QLabel(f)
            name.setStyleSheet("font-size: 12px; color: #2c3e50;")
            row.addWidget(name, stretch=1)

            btn_open = QPushButton("Open")
            btn_open.setFixedSize(60, 26)
            btn_open.setStyleSheet(
                "background: #ecf0f1; color: #2c3e50; border: none; "
                "border-radius: 6px; font-size: 11px; font-weight: bold;"
            )
            btn_open.clicked.connect(lambda checked, fn=f: self._on_open(fn))
            row.addWidget(btn_open)

            wrapper = QWidget()
            wrapper.setLayout(row)
            self.recent_layout.addWidget(wrapper)

        self.recent_layout.addStretch()

    # ------------------------------------------------------------------ handlers
    def _go_dashboard(self):
        self.parent_window.stacked_widget.setCurrentIndex(3)

    def _on_generate(self, key: str):
        generators = {
            "summary":     self.controller.generate_summary,
            "property":    self.controller.generate_property,
            "lease":       self.controller.generate_lease,
            "payment":     self.controller.generate_payment,
            "maintenance": self.controller.generate_maintenance,
        }
        gen = generators.get(key)
        if not gen:
            return

        ok, result = gen()
        if not ok:
            QMessageBox.warning(self, "Error", result)
            return

        QMessageBox.information(
            self, "Report generated",
            f"Saved to:\n{result}"
        )
        self._load_recent()

    def _on_open(self, filename: str):
        try:
            from Services.report_service import REPORTS_DIR
            path = os.path.join(REPORTS_DIR, filename)
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            QMessageBox.warning(self, "Cannot open", f"Failed to open file:\n{e}")