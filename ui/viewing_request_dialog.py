
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QTextEdit, QComboBox,
    QDateEdit, QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import QDate, Qt
from ui import theme


TIME_SLOTS = ["Morning", "Afternoon", "Evening"]


class ViewingRequestDialog(QDialog):
    def __init__(self, parent=None, property_data: dict | None = None):
        super().__init__(parent)
        self.property_data = property_data or {}
        self.setWindowTitle("Request a Viewing")
        self.setFixedSize(520, 520)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        title = QLabel("Request a Viewing")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        # Property summary
        prop = self.property_data.get("address", "")
        price = self.property_data.get("listing_price")
        price_str = f"  •  R{price:,.0f}/month" if price else ""
        summary = QLabel(f"<b>{prop}</b>{price_str}")
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

        # Info banner
        info = QLabel(
            "ℹ  Pick a preferred date and time. Management will confirm or "
            "suggest an alternative."
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

        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setMinimumDate(QDate.currentDate().addDays(1))
        self.date_edit.setMaximumDate(QDate.currentDate().addDays(60))
        self.date_edit.setDate(QDate.currentDate().addDays(2))
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setFixedHeight(40)
        self.date_edit.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Preferred Date *"), self.date_edit)

        self.time_combo = QComboBox()
        self.time_combo.addItems(TIME_SLOTS)
        self.time_combo.setFixedHeight(40)
        self.time_combo.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Preferred Time *"), self.time_combo)

        self.message = QTextEdit()
        self.message.setFixedHeight(100)
        self.message.setPlaceholderText(
            "Optional: any specific questions or notes for the agent"
        )
        self.message.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Message"), self.message)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText("Submit Request")
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
        if len(self.message.toPlainText()) > 500:
            QMessageBox.warning(self, "Message too long",
                                "Please keep your message under 500 characters.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "preferred_date": self.date_edit.date().toPython(),
            "preferred_time": self.time_combo.currentText(),
            "message": self.message.toPlainText().strip(),
        }
