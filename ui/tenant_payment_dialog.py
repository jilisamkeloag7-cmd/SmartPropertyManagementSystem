print(">>> tenant_payment_dialog.py V1 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from ui import theme


class TenantPaymentDialog(QDialog):
    """Tenant marks a payment as made, entering a reference."""

    def __init__(self, parent=None, payment_data: dict | None = None):
        super().__init__(parent)
        self.payment_data = payment_data or {}
        self.setWindowTitle("Mark Payment as Paid")
        self.setFixedSize(540, 520)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        title = QLabel("Mark Payment as Paid")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Enter your payment reference so management can confirm receipt."
        )
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(subtitle)

        # ---- Payment summary card
        d = self.payment_data
        amount = d.get("amount")
        due = d.get("due_date")
        prop = d.get("property_address", "")
        summary_html = (
            f"<b>{prop}</b><br>"
            f"Amount: <b>R{amount:,.2f}</b><br>"
            f"Due: {due}"
        ) if amount else "<b>(payment details unavailable)</b>"

        summary = QLabel(summary_html)
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

        # ---- Info banner
        info = QLabel(
            "ℹ  Provide any reference that helps management verify your payment "
            "(bank reference, transaction ID, or a short note)."
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

        # ---- Form
        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.reference = QLineEdit()
        self.reference.setFixedHeight(42)
        self.reference.setPlaceholderText(
            "e.g. EFT-2026-09-22-A17X  (bank reference or transaction ID)"
        )
        self.reference.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Reference *"), self.reference)

        self.note = QTextEdit()
        self.note.setFixedHeight(90)
        self.note.setPlaceholderText(
            "Optional: any additional note for management"
        )
        self.note.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Note"), self.note)

        layout.addLayout(form)
        layout.addStretch()

        # ---- Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText("Submit")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFixedHeight(42)
        ok_btn.setStyleSheet(theme.button_qss("success"))

        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setText("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(42)
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
        if len(self.reference.text().strip()) < 3:
            QMessageBox.warning(
                self, "Reference required",
                "Please enter a reference with at least 3 characters."
            )
            return
        self.accept()

    def get_data(self) -> dict:
        note = self.note.toPlainText().strip()
        reference = self.reference.text().strip()
        if note:
            reference = f"{reference} — {note}"
        return {"reference": reference}