print(">>> payment_form_dialog.py V1 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDateEdit, QDialogButtonBox, QLabel, QComboBox, QMessageBox
)
from PySide6.QtCore import QDate
from Repositories.lease_repository import LeaseRepository


class PaymentFormDialog(QDialog):
    """Modal for creating a manual payment tied to a lease."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Payment")
        self.setFixedSize(460, 340)
        self.setStyleSheet("""
            QDialog { background: #f0f4f8; }
            QLabel { color: #2c3e50; font-size: 13px; }
            QLineEdit, QComboBox, QDateEdit {
                padding: 8px 10px; border: 2px solid #ecf0f1;
                border-radius: 8px; font-size: 13px; background: white;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #3498db;
            }
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("Add Payment")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        # Lease dropdown
        self.lease_combo = QComboBox()
        lease_repo = LeaseRepository()
        for lease in lease_repo.list_all():
            if lease.status != "Active":
                continue
            self.lease_combo.addItem(
                f"Lease #{lease.lease_id} (Property #{lease.property_id})",
                lease.lease_id,
            )
        form.addRow("Lease *", self.lease_combo)

        # Amount
        self.amount = QLineEdit()
        self.amount.setPlaceholderText("e.g. 6500.00")
        form.addRow("Amount (R) *", self.amount)

        # Due date
        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDate(QDate.currentDate())
        self.due_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Due Date *", self.due_date)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Save).setStyleSheet(
            "background-color: #3498db; color: white; border: none; "
            "border-radius: 8px; padding: 8px 18px; font-weight: bold;"
        )
        buttons.button(QDialogButtonBox.Cancel).setStyleSheet(
            "background-color: #ecf0f1; color: #2c3e50; border: none; "
            "border-radius: 8px; padding: 8px 18px; font-weight: bold;"
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

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