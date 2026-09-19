print(">>> lease_form_dialog.py V1 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import QDate
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Models.user import UserRole


class LeaseFormDialog(QDialog):
    """Modal for creating a new lease."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Lease")
        self.setFixedSize(480, 480)
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

        title = QLabel("Create Lease")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        # ---- Property dropdown (non-archived only)
        self.property_combo = QComboBox()
        prop_repo = PropertyRepository()
        for p in prop_repo.list_all():
            if p.status == "Archived":
                continue
            self.property_combo.addItem(
                f"#{p.property_id} — {p.address}", p.property_id
            )
        form.addRow("Property *", self.property_combo)

        # ---- Tenant dropdown (Tenant role only, active users)
        self.tenant_combo = QComboBox()
        user_repo = UserRepository()
        for u in user_repo.list_all():
            if u.role != UserRole.TENANT:
                continue
            if u.status != "Active":
                continue
            self.tenant_combo.addItem(f"{u.name} ({u.email})", u.user_id)
        form.addRow("Tenant *", self.tenant_combo)

        # ---- Dates
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Start Date *", self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addYears(1))
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("End Date *", self.end_date)

        # ---- Rent
        self.rent = QLineEdit()
        self.rent.setPlaceholderText("e.g. 6500.00")
        form.addRow("Monthly Rent *", self.rent)

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
        if self.property_combo.count() == 0:
            QMessageBox.warning(self, "Missing data",
                                "No non-archived properties available.")
            return
        if self.tenant_combo.count() == 0:
            QMessageBox.warning(self, "Missing data",
                                "No active Tenants found. Create a Tenant user first.")
            return
        if not self.rent.text().strip():
            QMessageBox.warning(self, "Missing field", "Rent is required.")
            return
        try:
            if float(self.rent.text()) <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid rent",
                                "Rent must be a positive number.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "property_id": self.property_combo.currentData(),
            "tenant_id": self.tenant_combo.currentData(),
            "start_date": self.start_date.date().toPython(),
            "end_date": self.end_date.date().toPython(),
            "rent_amount": float(self.rent.text()),
        }