print(">>> ownership_form_dialog.py V1 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QDialogButtonBox, QLabel, QMessageBox, QCheckBox
)
from PySide6.QtCore import QDate
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Models.user import UserRole


class OwnershipFormDialog(QDialog):
    """Modal for adding a new ownership record."""

    def __init__(self, parent=None, preselected_property_id: int | None = None):
        super().__init__(parent)
        self.setWindowTitle("Add Ownership")
        self.setFixedSize(500, 480)
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
        self.preselected_property_id = preselected_property_id
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        title = QLabel("Add Ownership")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        # Property dropdown (non-archived)
        self.property_combo = QComboBox()
        prop_repo = PropertyRepository()
        for p in prop_repo.list_all():
            if p.status == "Archived":
                continue
            self.property_combo.addItem(
                f"#{p.property_id} — {p.address}", p.property_id
            )
        # Preselect if requested
        if self.preselected_property_id is not None:
            for i in range(self.property_combo.count()):
                if self.property_combo.itemData(i) == self.preselected_property_id:
                    self.property_combo.setCurrentIndex(i)
                    break
        form.addRow("Property *", self.property_combo)

        # Owner dropdown (only Owner role, active users)
        self.owner_combo = QComboBox()
        user_repo = UserRepository()
        for u in user_repo.list_all():
            if u.role != UserRole.OWNER:
                continue
            if u.status != "Active":
                continue
            self.owner_combo.addItem(f"{u.name} ({u.email})", u.user_id)
        form.addRow("Owner *", self.owner_combo)

        # Share (0–1)
        self.share = QLineEdit()
        self.share.setPlaceholderText("0.5 = 50%")
        form.addRow("Ownership Share *", self.share)

        # Start date
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        form.addRow("Start Date *", self.start_date)

        # Has end date?
        self.has_end = QCheckBox("Has an end date (closed ownership)")
        form.addRow("", self.has_end)

        # End date (disabled until checkbox)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addYears(1))
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setEnabled(False)
        form.addRow("End Date", self.end_date)

        self.has_end.toggled.connect(self.end_date.setEnabled)

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
            QMessageBox.warning(self, "Missing data", "No eligible property available.")
            return
        if self.owner_combo.count() == 0:
            QMessageBox.warning(
                self, "Missing data",
                "No active Owner users found. Create an Owner first."
            )
            return
        try:
            val = float(self.share.text().strip())
            if val <= 0 or val > 1.0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(
                self, "Invalid share",
                "Share must be a number between 0 and 1.0 (e.g. 0.5)."
            )
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "property_id": self.property_combo.currentData(),
            "user_id": self.owner_combo.currentData(),
            "ownership_share": float(self.share.text().strip()),
            "start_date": self.start_date.date().toPython(),
            "end_date": self.end_date.date().toPython() if self.has_end.isChecked() else None,
        }