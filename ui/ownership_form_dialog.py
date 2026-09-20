print(">>> ownership_form_dialog.py V2 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QDialogButtonBox, QLabel, QMessageBox, QCheckBox
)
from PySide6.QtCore import QDate, Qt
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Models.user import UserRole
from ui import theme


class OwnershipFormDialog(QDialog):
    def __init__(self, parent=None, preselected_property_id: int | None = None):
        super().__init__(parent)
        self.preselected_property_id = preselected_property_id
        self.setWindowTitle("Add Ownership")
        self.setFixedSize(520, 520)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        title = QLabel("Add Ownership")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        subtitle = QLabel("Link an owner to a property with their share")
        subtitle.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.property_combo = QComboBox()
        self.property_combo.setFixedHeight(40)
        prop_repo = PropertyRepository()
        for p in prop_repo.list_all():
            if p.status == "Archived":
                continue
            self.property_combo.addItem(
                f"#{p.property_id} — {p.address}", p.property_id
            )
        if self.preselected_property_id is not None:
            for i in range(self.property_combo.count()):
                if self.property_combo.itemData(i) == self.preselected_property_id:
                    self.property_combo.setCurrentIndex(i)
                    break
        self.property_combo.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Property"), self.property_combo)

        self.owner_combo = QComboBox()
        self.owner_combo.setFixedHeight(40)
        user_repo = UserRepository()
        for u in user_repo.list_all():
            if u.role != UserRole.OWNER:
                continue
            if u.status != "Active":
                continue
            self.owner_combo.addItem(f"{u.name} ({u.email})", u.user_id)
        self.owner_combo.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Owner"), self.owner_combo)

        self.share = QLineEdit()
        self.share.setPlaceholderText("0.5 = 50%")
        self.share.setFixedHeight(40)
        self.share.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Ownership Share"), self.share)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setFixedHeight(40)
        self.start_date.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Start Date"), self.start_date)

        self.has_end = QCheckBox("Has an end date (closed ownership)")
        self.has_end.setStyleSheet(
            f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px;"
        )
        form.addRow("", self.has_end)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addYears(1))
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setFixedHeight(40)
        self.end_date.setEnabled(False)
        self.end_date.setStyleSheet(theme.input_qss())
        form.addRow(self._label("End Date"), self.end_date)

        self.has_end.toggled.connect(self.end_date.setEnabled)

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