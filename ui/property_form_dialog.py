print(">>> property_form_dialog.py V4 <<<")

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QDialogButtonBox, QLabel, QMessageBox, QPushButton
)
from PySide6.QtCore import Qt
from ui import theme


PROPERTY_TYPES = ["House", "Apartment", "Commercial", "Other"]
STATUSES = ["Available", "Occupied", "Under Maintenance", "Archived"]


class PropertyFormDialog(QDialog):
    def __init__(self, parent=None, property_data: dict | None = None,
                 session_user: dict | None = None):
        super().__init__(parent)
        self.property_data = property_data or {}
        self.session_user = session_user or {}
        self.is_edit = bool(property_data and property_data.get("property_id"))
        self.setWindowTitle("Edit Property" if self.is_edit else "Add Property")
        self.setFixedSize(500, 620)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        title = QLabel("Edit Property" if self.is_edit else "Add Property")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        subtitle = QLabel(
            "Update the fields below" if self.is_edit
            else "Fill in the property details. Save first, then add images."
        )
        subtitle.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.address = QLineEdit()
        self.address.setPlaceholderText("e.g. 12 Main Rd, Durban")
        self.address.setFixedHeight(40)
        self.address.setText(self.property_data.get("address", ""))
        self.address.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Address"), self.address)

        self.ptype = QComboBox()
        self.ptype.setFixedHeight(40)
        self.ptype.addItems(PROPERTY_TYPES)
        if self.property_data.get("property_type"):
            self.ptype.setCurrentText(self.property_data["property_type"])
        self.ptype.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Property Type"), self.ptype)

        self.status = QComboBox()
        self.status.setFixedHeight(40)
        self.status.addItems(STATUSES)
        if self.property_data.get("status"):
            self.status.setCurrentText(self.property_data["status"])
        self.status.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Status"), self.status)

        self.listing_price = QLineEdit()
        self.listing_price.setPlaceholderText("e.g. 6500.00 (monthly rent in R)")
        self.listing_price.setFixedHeight(40)
        self.listing_price.setStyleSheet(theme.input_qss())
        if self.property_data.get("listing_price") is not None:
            self.listing_price.setText(f"{self.property_data['listing_price']:.2f}")
        form.addRow(self._label("Listing Price (R)"), self.listing_price)

        self.build_details = QTextEdit()
        self.build_details.setPlaceholderText(
            "e.g. 3 bed, 2 bath, built 2010, 250m² yard"
        )
        self.build_details.setFixedHeight(80)
        self.build_details.setText(self.property_data.get("build_details", "") or "")
        self.build_details.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Build Details"), self.build_details)

        layout.addLayout(form)

        # ---- Manage Images button
        img_row = QHBoxLayout()
        img_row.addStretch()
        self.btn_images = QPushButton("🖼  Manage Images")
        self.btn_images.setCursor(Qt.PointingHandCursor)
        self.btn_images.setFixedHeight(38)
        self.btn_images.setStyleSheet(theme.button_qss("secondary"))
        self.btn_images.clicked.connect(self._on_manage_images)
        self.btn_images.setEnabled(self.is_edit)
        if not self.is_edit:
            self.btn_images.setToolTip("Save the property first, then add images.")
        img_row.addWidget(self.btn_images)
        layout.addLayout(img_row)

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

    def _on_manage_images(self):
        from ui.property_images_dialog import PropertyImagesDialog
        dlg = PropertyImagesDialog(
            self,
            property_id=self.property_data.get("property_id"),
            property_address=self.property_data.get("address", ""),
            session_user=self.session_user,
        )
        dlg.exec()

    def _on_accept(self):
        if not self.address.text().strip():
            QMessageBox.warning(self, "Missing field", "Address is required.")
            return

        price_text = self.listing_price.text().strip()
        if price_text:
            try:
                val = float(price_text)
                if val < 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Invalid price",
                                    "Listing price must be a positive number.")
                return

        self.accept()

    def get_data(self) -> dict:
        price_text = self.listing_price.text().strip()
        try:
            price = float(price_text) if price_text else None
        except ValueError:
            price = None
        return {
            "address": self.address.text().strip(),
            "property_type": self.ptype.currentText(),
            "status": self.status.currentText(),
            "listing_price": price,
            "build_details": self.build_details.toPlainText().strip(),
        }