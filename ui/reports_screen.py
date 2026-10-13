
import os
import subprocess
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from Controllers.report_controller import ReportController
from ui import theme


# (icon, name, description, key) for admin/manager
ADMIN_REPORTS = [
    ("📊", "Executive Summary",  "High-level counts across all entities",  "summary"),
    ("🏠", "Property Report",    "Full list of properties with status",    "property"),
    ("📄", "Lease Report",       "All leases with dates, rent and status", "lease"),
    ("💰", "Payment Report",     "All payments with due/paid and status",  "payment"),
    ("🔧", "Maintenance Report", "All maintenance requests with priority", "maintenance"),
]

# Owner reports
OWNER_REPORTS = [
    ("📊", "Portfolio Summary",
     "Occupancy, income and net position across your properties", "owner_summary"),
    ("💰", "Income Report",
     "Month-by-month rent collected, pending and overdue",         "owner_income"),
    ("👥", "My Tenants",
     "All tenants currently or previously leasing your properties", "owner_tenants"),
]


class ReportsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = ReportController()
        self.user_data = None
        self.role = ""
        self._build()

    # ------------------------------------------------------------------ API
    def set_user(self, user_data: dict):
        self.user_data = user_data or {}
        self.role = self.user_data.get("role", "")
        self._apply_role_ui()
        self._load_recent()

    # ------------------------------------------------------------------ UI
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(12)

        self.title_label = QLabel("📊 Reports")
        self.title_label.setStyleSheet(
            f"font-size: {theme.FS_2XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        header.addWidget(self.title_label)
        header.addStretch()

        btn_dashboard = QPushButton("← Dashboard")
        btn_dashboard.setCursor(Qt.PointingHandCursor)
        btn_dashboard.setFixedHeight(36)
        btn_dashboard.setStyleSheet(theme.button_qss("ghost"))
        btn_dashboard.clicked.connect(self._go_dashboard)
        header.addWidget(btn_dashboard)

        layout.addLayout(header)

        self.subtitle = QLabel("")
        self.subtitle.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        self.subtitle.setWordWrap(True)
        layout.addWidget(self.subtitle)

        layout.addSpacing(6)

        # Report cards grid (rebuilt per role)
        self.cards_layout = QHBoxLayout()
        self.cards_layout.setSpacing(16)
        layout.addLayout(self.cards_layout)

        layout.addSpacing(14)

        recent_lbl = QLabel("Recently Generated")
        recent_lbl.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(recent_lbl)

        self.recent_frame = QFrame()
        self.recent_frame.setStyleSheet(theme.card_qss())
        self.recent_layout = QVBoxLayout(self.recent_frame)
        self.recent_layout.setContentsMargins(18, 14, 18, 14)
        self.recent_layout.setSpacing(6)
        layout.addWidget(self.recent_frame, stretch=1)

    # ------------------------------------------------------------------ role UI
    def _apply_role_ui(self):
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
            layout = item.layout()
            if layout is not None:
                while layout.count():
                    sub = layout.takeAt(0)
                    sw = sub.widget()
                    if sw:
                        sw.deleteLater()

        if self.role == "Owner":
            self.title_label.setText("📊 Owner Reports")
            self.subtitle.setText(
                "Generate PDF reports for your portfolio. Files are saved to "
                "Documentation/reports/ in your project folder."
            )
            reports = OWNER_REPORTS
        else:
            self.title_label.setText("📊 Reports")
            self.subtitle.setText(
                "Generate system-wide PDF reports. Files are saved to "
                "Documentation/reports/ in your project folder."
            )
            reports = ADMIN_REPORTS

        left_col = QVBoxLayout()
        left_col.setSpacing(12)
        right_col = QVBoxLayout()
        right_col.setSpacing(12)

        for idx, (icon, name, desc, key) in enumerate(reports):
            card = self._build_card(icon, name, desc, key)
            if idx % 2 == 0:
                left_col.addWidget(card)
            else:
                right_col.addWidget(card)

        left_col.addStretch()
        right_col.addStretch()
        self.cards_layout.addLayout(left_col, stretch=1)
        self.cards_layout.addLayout(right_col, stretch=1)

    def _build_card(self, icon, name, desc, key):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border-radius: {theme.RADIUS_LG}px;
                border: 1px solid {theme.BORDER};
            }}
            QFrame:hover {{ border-color: {theme.PRIMARY}; }}
        """)
        card.setMinimumHeight(96)

        inner = QHBoxLayout(card)
        inner.setContentsMargins(18, 16, 18, 16)
        inner.setSpacing(16)

        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(44, 44)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            background: {theme.PRIMARY_SOFT};
            border-radius: {theme.RADIUS_MD}px;
            font-size: 22px;
        """)
        inner.addWidget(icon_lbl)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(
            f"font-size: {theme.FS_MD}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        text_col.addWidget(name_lbl)
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet(
            f"font-size: {theme.FS_XS}px; color: {theme.TEXT_MUTED};"
        )
        desc_lbl.setWordWrap(True)
        text_col.addWidget(desc_lbl)
        inner.addLayout(text_col, stretch=1)

        btn = QPushButton("Generate")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFixedSize(110, 36)
        btn.setStyleSheet(theme.button_qss("primary"))
        btn.clicked.connect(lambda checked, k=key: self._on_generate(k))
        inner.addWidget(btn)

        return card

    # ------------------------------------------------------------------ recent
    def _load_recent(self):
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
            lbl.setStyleSheet(f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_SM}px;")
            self.recent_layout.addWidget(lbl)
            return

        for f in files:
            row = QHBoxLayout()
            name = QLabel(f)
            name.setStyleSheet(
                f"font-size: {theme.FS_SM}px; color: {theme.TEXT_MAIN};"
            )
            row.addWidget(name, stretch=1)

            btn_open = QPushButton("Open")
            btn_open.setCursor(Qt.PointingHandCursor)
            btn_open.setFixedSize(72, 30)
            btn_open.setStyleSheet(theme.button_qss("secondary"))
            btn_open.clicked.connect(lambda checked, fn=f: self._on_open(fn))
            row.addWidget(btn_open)

            wrapper = QWidget()
            wrapper.setLayout(row)
            self.recent_layout.addWidget(wrapper)

        self.recent_layout.addStretch()

    # ------------------------------------------------------------------ handlers
    def _go_dashboard(self):
        self.parent_window._set_screen("dashboard")

    def _on_generate(self, key: str):
        user = self.user_data or {}

        if key == "summary":
            ok, result = self.controller.generate_summary()
        elif key == "property":
            ok, result = self.controller.generate_property()
        elif key == "lease":
            ok, result = self.controller.generate_lease()
        elif key == "payment":
            ok, result = self.controller.generate_payment()
        elif key == "maintenance":
            ok, result = self.controller.generate_maintenance()
        elif key == "owner_summary":
            ok, result = self.controller.generate_owner_summary(user)
        elif key == "owner_income":
            ok, result = self.controller.generate_owner_income(user)
        elif key == "owner_tenants":
            ok, result = self.controller.generate_owner_tenants(user)
        else:
            return

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
