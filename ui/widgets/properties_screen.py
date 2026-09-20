print(">>> properties_screen.py V3 <<<")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QScrollArea,
    QGridLayout, QFrame
)
from PySide6.QtCore import Qt
from Controllers.property_controller import PropertyController
from ui.property_form_dialog import PropertyFormDialog
from ui.widgets.property_card import PropertyCard
from ui import theme

from Repositories.lease_repository import LeaseRepository
from Repositories.ownership_repository import OwnershipRepository


CARD_COLS = 3
CARD_GAP = 16


class PropertiesScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = PropertyController()
        self.user_data = None
        self.role = ""
        self._build()

    # ------------------------------------------------------------------ API
    def set_user(self, user_data: dict):
        self.user_data = user_data or {}
        self.role = self.user_data.get("role", "")
        self._refresh_all()

    def refresh(self):
        self._refresh_all()

    # ------------------------------------------------------------------ UI
    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; }")
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet(f"background: {theme.BG_APP};")
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(18)

        # ============================================================
        # HEADER (title changes per role)
        # ============================================================
        header = QHBoxLayout()
        header.setSpacing(12)

        self.title_label = QLabel("🏠 Properties")
        self.title_label.setStyleSheet(
            f"font-size: {theme.FS_2XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        header.addWidget(self.title_label)

        self.readonly_badge = QLabel("Read-only")
        self.readonly_badge.setStyleSheet(f"""
            background: {theme.WARNING_SOFT};
            color: {theme.WARNING_HOVER};
            padding: 4px 12px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_XS}px;
            font-weight: bold;
        """)
        self.readonly_badge.setVisible(False)
        header.addWidget(self.readonly_badge)

        header.addStretch()

        btn_dashboard = QPushButton("← Dashboard")
        btn_dashboard.setCursor(Qt.PointingHandCursor)
        btn_dashboard.setFixedHeight(36)
        btn_dashboard.setStyleSheet(theme.button_qss("ghost"))
        btn_dashboard.clicked.connect(self._go_dashboard)
        header.addWidget(btn_dashboard)

        self.btn_add = QPushButton("+ Add Property")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setFixedHeight(36)
        self.btn_add.setStyleSheet(theme.button_qss("primary"))
        self.btn_add.clicked.connect(self._on_add)
        header.addWidget(self.btn_add)

        layout.addLayout(header)

        # ============================================================
        # FILTERS (shared across roles)
        # ============================================================
        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by address or type…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(theme.input_qss())
        self.search_input.returnPressed.connect(self._refresh_all)
        filters_row.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(
            ["All", "Available", "Occupied", "Under Maintenance", "Archived"]
        )
        self.status_filter.setFixedHeight(38)
        self.status_filter.setStyleSheet(theme.input_qss())
        self.status_filter.currentTextChanged.connect(self._refresh_all)
        filters_row.addWidget(self.status_filter)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setFixedHeight(38)
        btn_refresh.setStyleSheet(theme.button_qss("secondary"))
        btn_refresh.clicked.connect(self._refresh_all)
        filters_row.addWidget(btn_refresh)

        layout.addLayout(filters_row)

        # ============================================================
        # COUNT LABEL
        # ============================================================
        self.count_label = QLabel("0 property record(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        # ============================================================
        # ADMIN TABLE (hidden unless Admin/Manager)
        # ============================================================
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Address", "Type", "Status", "Build Details"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._on_row_double_click)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_LG}px;
                font-size: {theme.FS_BASE}px;
                gridline-color: transparent;
                alternate-background-color: {theme.BG_SUBTLE};
                outline: none;
            }}
            QHeaderView::section {{
                background: {theme.BG_SUBTLE};
                color: {theme.TEXT_MUTED};
                padding: 12px 10px;
                border: none;
                border-bottom: 1px solid {theme.BORDER};
                font-weight: bold;
                font-size: {theme.FS_XS}px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }}
            QTableWidget::item {{ padding: 10px; border: none; }}
            QTableWidget::item:selected {{
                background: {theme.PRIMARY_SOFT};
                color: {theme.TEXT_MAIN};
            }}
        """)
        hv = self.table.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.Stretch)
        hv.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        # ============================================================
        # CARD GRID (shown for Owner/Tenant)
        # ============================================================
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setSpacing(CARD_GAP)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.cards_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.cards_container, stretch=1)

        # ============================================================
        # ACTIONS ROW (admin/manager only)
        # ============================================================
        self.actions_row = QHBoxLayout()
        self.actions_row.setSpacing(10)
        self.actions_row.addStretch()

        self.btn_edit = QPushButton("Edit Selected")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.setFixedHeight(38)
        self.btn_edit.setStyleSheet(theme.button_qss("primary"))
        self.btn_edit.clicked.connect(self._on_edit_selected)
        self.actions_row.addWidget(self.btn_edit)

        self.btn_archive = QPushButton("Archive Selected")
        self.btn_archive.setCursor(Qt.PointingHandCursor)
        self.btn_archive.setFixedHeight(38)
        self.btn_archive.setStyleSheet(theme.button_qss("danger"))
        self.btn_archive.clicked.connect(self._on_archive_selected)
        self.actions_row.addWidget(self.btn_archive)

        layout.addLayout(self.actions_row)

    # ------------------------------------------------------------------ refresh
    def _refresh_all(self):
        # ---- Role-based UI
        is_admin_like = self.role in ("Administrator", "Property Manager")
        is_owner = self.role == "Owner"
        is_tenant = self.role == "Tenant"

        # Title
        if is_admin_like:
            self.title_label.setText("🏠 All Properties")
            self.readonly_badge.setVisible(False)
        elif is_owner:
            self.title_label.setText("🏠 My Properties")
            self.readonly_badge.setVisible(True)
        elif is_tenant:
            self.title_label.setText("🏠 Browse Properties")
            self.readonly_badge.setVisible(True)
        else:
            self.title_label.setText("🏠 Properties")
            self.readonly_badge.setVisible(False)

        # Add button only for writers
        self.btn_add.setVisible(is_admin_like)

        # Table only for admin/manager; cards for owner/tenant
        self.table.setVisible(is_admin_like)
        self.cards_container.setVisible(is_owner or is_tenant)
        self.btn_edit.setVisible(is_admin_like)
        self.btn_archive.setVisible(is_admin_like)

        # ---- Data fetch
        filters = {
            "query": self.search_input.text().strip(),
            "status": self.status_filter.currentText(),
        }
        rows = self.controller.list(filters)

        # ---- Role scoping
        if is_owner:
            uid = self.user_data.get("user_id")
            owned_pids = set(
                OwnershipRepository().property_ids_for_owner(uid)
            )
            rows = [r for r in rows if r["property_id"] in owned_pids]
        elif is_tenant:
            uid = self.user_data.get("user_id")
            leases = LeaseRepository().list_for_tenant(uid)
            leased_pids = {l.property_id for l in leases if l.status == "Active"}
            # Tenant sees: properties they lease (any status) + available ones
            rows = [
                r for r in rows
                if r["property_id"] in leased_pids or r["status"] == "Available"
            ]
            # Sort: own leased first, then available
            rows.sort(key=lambda r: (
                0 if r["property_id"] in leased_pids else 1,
                r["property_id"],
            ))

        self.count_label.setText(f"{len(rows)} propert(y/ies)")

        # ---- Populate
        if is_admin_like:
            self._populate_table(rows)
        else:
            self._populate_cards(rows, is_tenant=is_tenant)

    # ------------------------------------------------------------------ table
    def _populate_table(self, rows):
        self.table.setRowCount(0)
        for r, p in enumerate(rows):
            self.table.insertRow(r)
            self.table.setRowHeight(r, 42)
            self.table.setItem(r, 0, QTableWidgetItem(str(p["property_id"])))
            self.table.setItem(r, 1, QTableWidgetItem(p["address"] or ""))
            self.table.setItem(r, 2, QTableWidgetItem(p["property_type"] or ""))
            self.table.setItem(r, 3, QTableWidgetItem(p["status"] or ""))
            self.table.setItem(r, 4, QTableWidgetItem(p["build_details"] or ""))

    # ------------------------------------------------------------------ cards
    def _populate_cards(self, rows, is_tenant: bool):
        # Clear
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not rows:
            empty = QLabel("No properties to show.")
            empty.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_MD}px; "
                f"padding: 40px;"
            )
            self.cards_grid.addWidget(empty, 0, 0)
            return

        for i, p in enumerate(rows):
            card = PropertyCard(
                p,
                on_click=self._on_card_click,
            )
            row = i // CARD_COLS
            col = i % CARD_COLS
            self.cards_grid.addWidget(card, row, col)

    def _on_card_click(self, property_data):
        # For now, show a simple details popup.
        # In Phase 5 this becomes a rich detail view with image gallery.
        d = property_data
        msg = (
            f"<b>{d.get('address', '')}</b><br><br>"
            f"<b>Type:</b> {d.get('property_type') or '—'}<br>"
            f"<b>Status:</b> {d.get('status') or '—'}<br>"
            f"<b>Details:</b> {d.get('build_details') or '—'}"
        )
        box = QMessageBox(self)
        box.setWindowTitle("Property Details")
        box.setTextFormat(Qt.RichText)
        box.setText(msg)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec()

    # ------------------------------------------------------------------ helpers
    def _selected_property_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    # ------------------------------------------------------------------ handlers
    def _go_dashboard(self):
        self.parent_window.stacked_widget.setCurrentIndex(3)

    def _on_add(self):
        dlg = PropertyFormDialog(self, property_data=None)
        if dlg.exec():
            ok, msg = self.controller.create(dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self._refresh_all()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_edit_selected(self):
        pid = self._selected_property_id()
        if pid is None:
            QMessageBox.information(self, "No selection", "Select a property to edit.")
            return
        data = self.controller.get(pid)
        if not data:
            QMessageBox.warning(self, "Error", "Property not found.")
            return
        dlg = PropertyFormDialog(self, property_data=data)
        if dlg.exec():
            ok, msg = self.controller.update(pid, dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self._refresh_all()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_archive_selected(self):
        pid = self._selected_property_id()
        if pid is None:
            QMessageBox.information(self, "No selection", "Select a property to archive.")
            return
        confirm = QMessageBox.question(
            self, "Archive property",
            f"Archive property #{pid}? It will no longer appear as active.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.archive(pid, self.user_data)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self._refresh_all()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_row_double_click(self, index):
        self._on_edit_selected()