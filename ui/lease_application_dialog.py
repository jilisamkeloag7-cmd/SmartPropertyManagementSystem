
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QTextEdit, QSpinBox,
    QDateEdit, QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import QDate, Qt
from ui import theme


class LeaseApplicationDialog(QDialog):
    def __init__(self, parent=None, property_data: dict | None = None):
        super().__init__(parent)
        self.property_data = property_data or {}
        self.setWindowTitle("Apply for Lease")
        self.setFixedSize(540, 560)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        title = QLabel("Apply for Lease")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        # Property summary
        d = self.property_data
        addr = d.get("address", "")
        price = d.get("listing_price")
        price_str = f"  •  R{price:,.0f}/month" if price else ""
        summary = QLabel(f"<b>{addr}</b>{price_str}")
        summary.setTextFormat(Qt.RichText)
        summary.setStyleSheet(f"""
            background: {theme.BG_CARD};
            border: 1px solid {theme.BORDER};
            border-radius: {theme.RADIUS_MD}px;
            padding: 12px;
            color: {theme.TEXT_MAIN};
            font-size: {theme.FS_BASE}px;
        """)
        layout.addWidget(summary)

        info = QLabel(
            "ℹ  Management will review your application. If approved, a lease "
            "agreement is created automatically."
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"""
            color: {theme.INFO};
            background: {theme.INFO_SOFT};
            padding: 10px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_SM}px;
        """)
        layout.addWidget(info)

        # Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setMinimumDate(QDate.currentDate())
        self.start_date.setMaximumDate(QDate.currentDate().addDays(90))
        self.start_date.setDate(QDate.currentDate().addDays(7))
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setFixedHeight(40)
        self.start_date.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Preferred Start *"), self.start_date)

        self.duration = QSpinBox()
        self.duration.setMinimum(1)
        self.duration.setMaximum(36)
        self.duration.setValue(12)
        self.duration.setSuffix(" months")
        self.duration.setFixedHeight(40)
        self.duration.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Duration *"), self.duration)

        self.message = QTextEdit()
        self.message.setFixedHeight(120)
        self.message.setPlaceholderText(
            "Optional: introduce yourself, mention any questions, or special "
            "requirements (e.g. parking, pets)."
        )
        self.message.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Message"), self.message)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText("Submit Application")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFixedHeight(40)
        ok_btn.setStyleSheet(theme.button_qss("primary"))

        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setText("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet(theme.button_qss("secondary"))

        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; "
            f"font-size: {theme.FS_SM}px; font-weight: bold;"
        )
        return lbl

    def _on_accept(self):
        if len(self.message.toPlainText()) > 1000:
            QMessageBox.warning(self, "Message too long",
                                "Please keep your message under 1000 characters.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "preferred_start": self.start_date.date().toPython(),
            "duration_months": self.duration.value(),
            "message": self.message.toPlainText().strip(),
        }
