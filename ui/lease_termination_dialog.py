
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QDialogButtonBox,
    QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from ui import theme


class LeaseTerminationDialog(QDialog):
    """Tenant fills in a reason for requesting lease termination."""

    def __init__(self, parent=None, lease_data: dict | None = None):
        super().__init__(parent)
        self.lease_data = lease_data or {}
        self.setWindowTitle("Request Lease Termination")
        self.setFixedSize(520, 420)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        title = QLabel("Request Lease Termination")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        # Lease summary
        prop = self.lease_data.get("property_address", "")
        rent = self.lease_data.get("rent_amount")
        rent_str = f"R{rent:,.2f}/month" if rent else "—"
        summary = QLabel(f"<b>{prop}</b><br>{rent_str}")
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

        # Warning
        warning = QLabel(
            "⚠  Your request will be sent to management for approval. "
            "The lease remains active until approved."
        )
        warning.setWordWrap(True)
        warning.setStyleSheet(f"""
            color: {theme.WARNING_HOVER};
            background: {theme.WARNING_SOFT};
            padding: 10px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_SM}px;
        """)
        layout.addWidget(warning)

        # Reason
        reason_lbl = QLabel("Reason for termination *")
        reason_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-weight: bold; "
            f"font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(reason_lbl)

        self.reason = QTextEdit()
        self.reason.setFixedHeight(120)
        self.reason.setPlaceholderText(
            "e.g. Relocating to another city for work, financial "
            "hardship, property condition issues…"
        )
        self.reason.setStyleSheet(theme.input_qss())
        layout.addWidget(self.reason)

        # Buttons
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

    def _on_accept(self):
        if len(self.reason.toPlainText().strip()) < 10:
            QMessageBox.warning(
                self, "Reason too short",
                "Please provide a reason with at least 10 characters."
            )
            return
        self.accept()

    def get_reason(self) -> str:
        return self.reason.toPlainText().strip()
