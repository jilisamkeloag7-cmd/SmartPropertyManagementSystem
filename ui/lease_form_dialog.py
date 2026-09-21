print(">>> lease_form_dialog.py V3 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDateEdit, QDialogButtonBox, QLabel, QMessageBox
)
from PySide6.QtCore import QDate, Qt
from Repositories.property_repository import PropertyRepository
from Repositories.user_repository import UserRepository
from Models.user import UserRole
from ui import theme


class LeaseFormDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Lease")
        self.setFixedSize(520, 580)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._property_lookup = {}   # property_id → property object (for price lookup)
        self._build()
        # Trigger the initial auto-fill for the first selection
        self._on_property_changed()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(16)

        title = QLabel("Create Lease")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        subtitle = QLabel("Link a tenant to a property with a rent and term")
        subtitle.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(subtitle)

        layout.addSpacing(4)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # ---- Property combo (with embedded listing price display)
        self.property_combo = QComboBox()
        self.property_combo.setFixedHeight(40)
        prop_repo = PropertyRepository()
        for p in prop_repo.list_all():
            if p.status == "Archived":
                continue
            price_suffix = ""
            if p.listing_price is not None:
                price_suffix = f"  •  R{p.listing_price:,.0f}/mo"
            self.property_combo.addItem(
                f"#{p.property_id} — {p.address}{price_suffix}",
                p.property_id,
            )
            self._property_lookup[p.property_id] = p
        self.property_combo.setStyleSheet(theme.input_qss())
        self.property_combo.currentIndexChanged.connect(self._on_property_changed)
        form.addRow(self._label("Property"), self.property_combo)

        self.tenant_combo = QComboBox()
        self.tenant_combo.setFixedHeight(40)
        user_repo = UserRepository()
        for u in user_repo.list_all():
            if u.role != UserRole.TENANT:
                continue
            if u.status != "Active":
                continue
            self.tenant_combo.addItem(f"{u.name} ({u.email})", u.user_id)
        self.tenant_combo.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Tenant"), self.tenant_combo)

        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate())
        self.start_date.setDisplayFormat("yyyy-MM-dd")
        self.start_date.setFixedHeight(40)
        self.start_date.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Start Date"), self.start_date)

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate().addYears(1))
        self.end_date.setDisplayFormat("yyyy-MM-dd")
        self.end_date.setFixedHeight(40)
        self.end_date.setStyleSheet(theme.input_qss())
        form.addRow(self._label("End Date"), self.end_date)

        # ---- Rent field with auto-fill hint
        self.rent = QLineEdit()
        self.rent.setPlaceholderText("e.g. 6500.00")
        self.rent.setFixedHeight(40)
        self.rent.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Monthly Rent (R)"), self.rent)

        # Hint label under rent
        self.hint_label = QLabel("")
        self.hint_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px; "
            f"font-style: italic;"
        )
        form.addRow("", self.hint_label)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        save_btn = buttons.button(QDialogButtonBox.Save)
        save_btn.setText("Create")
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

    # ------------------------------------------------------------------ auto-fill
    def _on_property_changed(self):
        pid = self.property_combo.currentData()
        if pid is None:
            return
        prop = self._property_lookup.get(pid)
        if prop and prop.listing_price is not None and prop.listing_price > 0:
            # Auto-fill rent with the property's asking price
            self.rent.setText(f"{prop.listing_price:.2f}")
            self.hint_label.setText(
                f"Auto-filled from property's asking price. You may adjust."
            )
        else:
            # No listing price → clear and hint
            if not self.rent.text().strip() or self.rent.text().strip() == "":
                self.rent.clear()
            self.hint_label.setText(
                "This property has no listing price set — enter a rent manually."
            )

    # ------------------------------------------------------------------ validate
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