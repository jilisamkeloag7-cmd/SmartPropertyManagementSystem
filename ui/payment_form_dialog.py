print(">>> payment_form_dialog.py V2 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDateEdit, QDialogButtonBox, QLabel, QComboBox, QMessageBox
)
from PySide6.QtCore import QDate, Qt
from Repositories.lease_repository import LeaseRepository
from ui import theme


class PaymentFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Payment")
        self.setFixedSize(480, 400)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        title = QLabel("Add Payment")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        subtitle = QLabel("Attach a manual payment to an active lease")
        subtitle.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.lease_combo = QComboBox()
        self.lease_combo.setFixedHeight(40)
        lease_repo = LeaseRepository()
        for lease in lease_repo.list_all():
            if lease.status != "Active":
                continue
            self.lease_combo.addItem(
                f"Lease #{lease.lease_id} (Property #{lease.property_id})",
                lease.lease_id,
            )
        self.lease_combo.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Lease"), self.lease_combo)

        self.amount = QLineEdit()
        self.amount.setPlaceholderText("e.g. 6500.00")
        self.amount.setFixedHeight(40)
        self.amount.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Amount (R)"), self.amount)

        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDate(QDate.currentDate())
        self.due_date.setDisplayFormat("yyyy-MM-dd")
        self.due_date.setFixedHeight(40)
        self.due_date.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Due Date"), self.due_date)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        save_btn = buttons.button(QDialogButtonBox.Save)
        save_btn.setText("Save")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setFixedHeight(40)
        save_btn.setStyleSheet(theme.button_qss("primary"))

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
        if self.lease_combo.count() == 0:
            QMessageBox.warning(self, "Missing data", "No active leases available.")
            return
        if not self.amount.text().strip():
            QMessageBox.warning(self, "Missing field", "Amount is required.")
            return
        try:
            if float(self.amount.text()) <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid amount", "Enter a positive number.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "lease_id": self.lease_combo.currentData(),
            "amount": float(self.amount.text()),
            "due_date": self.due_date.date().toPython(),
        }