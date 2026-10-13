
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QScrollArea,
    QGridLayout, QFrame, QInputDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from Controllers.property_controller import PropertyController
from ui.property_form_dialog import PropertyFormDialog
from ui.property_detail_dialog import PropertyDetailDialog
from ui.widgets.property_card import PropertyCard
from ui.widgets.loading_overlay import LoadingOverlay
from ui.widgets.async_worker import AsyncRunner
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
        self._overlay = LoadingOverlay(self, "Loading properties…")
        self._async = AsyncRunner(self)

    def set_user(self, user_data: dict):
        self.user_data = user_data or {}
        self.role = self.user_data.get("role", "")
        self._refresh_all()

    def refresh(self):
        self._refresh_all()

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
            background: {theme.WARNING_SOFT}; color: {theme.WARNING_HOVER};
            padding: 4px 12px; border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_XS}px; font-weight: bold;
        """)
        self.readonly_badge.setVisible(False)
        header.addWidget(self.readonly_badge)
        header.addStretch()

        self.btn_dashboard = QPushButton("← Dashboard")
        self.btn_dashboard.setCursor(Qt.PointingHandCursor)
        self.btn_dashboard.setFixedHeight(36)
        self.btn_dashboard.setStyleSheet(theme.button_qss("ghost"))
        self.btn_dashboard.clicked.connect(self._go_dashboard)
        header.addWidget(self.btn_dashboard)

        self.btn_add = QPushButton("+ Add Property")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setFixedHeight(36)
        self.btn_add.setStyleSheet(theme.button_qss("primary"))
        self.btn_add.clicked.connect(self._on_add)
        header.addWidget(self.btn_add)

        self.btn_submit = QPushButton("+ Submit Property")
        self.btn_submit.setCursor(Qt.PointingHandCursor)
        self.btn_submit.setFixedHeight(36)
        self.btn_submit.setStyleSheet(theme.button_qss("primary"))
        self.btn_submit.clicked.connect(self._on_add)
        self.btn_submit.setVisible(False)
        header.addWidget(self.btn_submit)

        layout.addLayout(header)

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
            ["All", "Pending Approval", "Available", "Occupied",
             "Under Maintenance", "Rejected", "Archived"]
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

        self.count_label = QLabel("0 property record(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Address", "Type", "Status", "Price", "Build Details"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._on_row_double_click)
        self.table.itemSelectionChanged.connect(self._update_approval_buttons_visibility)
        self.table.setShowGrid(False)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background: {theme.BG_CARD}; border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_LG}px;
                font-size: {theme.FS_BASE}px; gridline-color: transparent;
                alternate-background-color: {theme.BG_SUBTLE}; outline: none;
            }}
            QHeaderView::section {{
                background: {theme.BG_SUBTLE}; color: {theme.TEXT_MUTED};
                padding: 10px 10px; border: none;
                border-bottom: 1px solid {theme.BORDER};
                font-weight: bold; font-size: {theme.FS_XS}px;
                text-transform: uppercase; letter-spacing: 0.5px;
            }}
            QTableWidget::item {{ padding: 10px; border: none; }}
            QTableWidget::item:selected {{
                background: {theme.PRIMARY_SOFT}; color: {theme.TEXT_MAIN};
            }}
        """)
        hv = self.table.horizontalHeader()
        hv.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.Stretch)
        hv.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(5, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setSpacing(CARD_GAP)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.cards_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.cards_container, stretch=1)

        self.actions_row = QHBoxLayout()
        self.actions_row.setSpacing(10)
        self.actions_row.addStretch()

        self.btn_edit = QPushButton("Edit Selected")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.setFixedHeight(38)
        self.btn_edit.setStyleSheet(theme.button_qss("primary"))
        self.btn_edit.clicked.connect(self._on_edit_selected)
        self.actions_row.addWidget(self.btn_edit)

        self.btn_approve = QPushButton("✓ Approve")
        self.btn_approve.setCursor(Qt.PointingHandCursor)
        self.btn_approve.setFixedHeight(38)
        self.btn_approve.setStyleSheet(theme.button_qss("success"))
        self.btn_approve.clicked.connect(self._on_approve_selected)
        self.actions_row.addWidget(self.btn_approve)

        self.btn_reject = QPushButton("✕ Reject")
        self.btn_reject.setCursor(Qt.PointingHandCursor)
        self.btn_reject.setFixedHeight(38)
        self.btn_reject.setStyleSheet(theme.button_qss("danger"))
        self.btn_reject.clicked.connect(self._on_reject_selected)
        self.actions_row.addWidget(self.btn_reject)

        self.btn_archive = QPushButton("Archive Selected")
        self.btn_archive.setCursor(Qt.PointingHandCursor)
        self.btn_archive.setFixedHeight(38)
        self.btn_archive.setStyleSheet(theme.button_qss("danger"))
        self.btn_archive.clicked.connect(self._on_archive_selected)
        self.actions_row.addWidget(self.btn_archive)

        self.btn_withdraw = QPushButton("Withdraw Submission")
        self.btn_withdraw.setCursor(Qt.PointingHandCursor)
        self.btn_withdraw.setFixedHeight(38)
        self.btn_withdraw.setStyleSheet(theme.button_qss("danger"))
        self.btn_withdraw.clicked.connect(self._on_withdraw_selected)
        self.actions_row.addWidget(self.btn_withdraw)

        layout.addLayout(self.actions_row)

    def _refresh_all(self):
        is_admin_like = self.role in ("Administrator", "Property Manager")
        is_owner = self.role == "Owner"
        is_tenant = self.role == "Tenant"
        is_guest = self.role == "Guest"

        if is_admin_like:
            self.title_label.setText("🏠 All Properties")
            self.readonly_badge.setVisible(False)
        elif is_owner:
            self.title_label.setText("🏠 My Properties")
            self.readonly_badge.setVisible(True)
        elif is_tenant:
            self.title_label.setText("🏠 Browse Properties")
            self.readonly_badge.setVisible(True)
        elif is_guest:
            self.title_label.setText("🏠 Browse Properties")
            self.readonly_badge.setVisible(False)
        else:
            self.title_label.setText("🏠 Properties")
            self.readonly_badge.setVisible(False)

        self.btn_dashboard.setVisible(not is_guest)
        self.btn_add.setVisible(is_admin_like)
        self.btn_submit.setVisible(is_owner)
        self.table.setVisible(is_admin_like or is_owner)
        self.cards_container.setVisible(is_tenant or is_guest)
        self.btn_edit.setVisible(is_admin_like or is_owner)
        self.btn_archive.setVisible(is_admin_like)
        self.btn_withdraw.setVisible(is_owner)

        # Synchronous load — direct call
        try:
            filters = {
                "query": self.search_input.text().strip(),
                "status": self.status_filter.currentText(),
            }
            rows = self.controller.list(filters)
            self._on_rows_loaded(rows)
        except Exception as e:
            self._on_load_error(f"{type(e).__name__}: {e}")

    def _on_rows_loaded(self, rows):
        is_owner = self.role == "Owner"
        is_tenant = self.role == "Tenant"
        is_guest = self.role == "Guest"
        is_admin_like = self.role in ("Administrator", "Property Manager")

        if is_owner:
            uid = self.user_data.get("user_id")
            owned_pids = set(OwnershipRepository().property_ids_for_owner(uid))
            rows = [r for r in rows if r["property_id"] in owned_pids]
        elif is_tenant:
            uid = self.user_data.get("user_id")
            leases = LeaseRepository().list_for_tenant(uid)
            leased_pids = {l.property_id for l in leases if l.status == "Active"}
            rows = [
                r for r in rows
                if r["status"] not in ("Pending Approval", "Rejected")
                and (r["property_id"] in leased_pids or r["status"] == "Available")
            ]
            rows.sort(key=lambda r: (
                0 if r["property_id"] in leased_pids else 1,
                r["property_id"],
            ))
        elif is_guest:
            rows = [r for r in rows if r["status"] == "Available"]

        self.count_label.setText(f"{len(rows)} propert(y/ies)")

        if is_admin_like or is_owner:
            self._populate_table(rows, is_owner=is_owner)
        else:
            self._populate_cards(rows, is_tenant=is_tenant)

        self._update_approval_buttons_visibility()
        self._overlay.hide_loading()

    def _on_load_error(self, err_msg):
        self._overlay.hide_loading()
        QMessageBox.warning(self, "Connection error",
                            f"Could not load properties:\n\n{err_msg}")

    def _populate_table(self, rows, is_owner=False):
        self.table.setRowCount(0)
        pending_bg = QBrush(QColor(theme.WARNING_SOFT))
        pending_fg = QBrush(QColor(theme.WARNING_HOVER))
        rejected_bg = QBrush(QColor(theme.DANGER_SOFT))
        rejected_fg = QBrush(QColor(theme.DANGER_HOVER))

        for r, p in enumerate(rows):
            self.table.insertRow(r)
            self.table.setRowHeight(r, 42)
            price = p.get("listing_price")
            price_str = f"R{price:,.2f}" if price is not None else "—"
            cells = [
                str(p["property_id"]),
                p["address"] or "",
                p["property_type"] or "",
                p["status"] or "",
                price_str,
                p["build_details"] or "",
            ]
            status = p["status"]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if c == 4 and price is not None:
                    item.setForeground(QBrush(QColor(theme.PRIMARY)))
                if status == "Pending Approval":
                    item.setBackground(pending_bg); item.setForeground(pending_fg)
                elif status == "Rejected":
                    item.setBackground(rejected_bg); item.setForeground(rejected_fg)
                self.table.setItem(r, c, item)

    def _populate_cards(self, rows, is_tenant=False):
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not rows:
            empty = QLabel(
                "No properties to show.\n\n"
                "Try adjusting your filters or search terms."
            )
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_MD}px; "
                f"padding: 60px;"
            )
            self.cards_grid.addWidget(empty, 0, 0, 1, CARD_COLS)
            return

        for i, p in enumerate(rows):
            card = PropertyCard(p, on_click=self._on_card_click)
            self.cards_grid.addWidget(card, i // CARD_COLS, i % CARD_COLS)

    def _on_card_click(self, property_data):
        dlg = PropertyDetailDialog(
            self, property_data=property_data, session_user=self.user_data,
        )
        dlg.exec()

    def _selected_property_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def _selected_status(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 3)
        return item.text() if item else None

    def _update_approval_buttons_visibility(self):
        is_admin_like = self.role in ("Administrator", "Property Manager")
        status = self._selected_status()
        show = is_admin_like and status == "Pending Approval"
        self.btn_approve.setVisible(show)
        self.btn_reject.setVisible(show)

    def _go_dashboard(self):
        self.parent_window._set_screen("dashboard")

    def _on_add(self):
        dlg = PropertyFormDialog(self, property_data=None,
                                 session_user=self.user_data)
        if dlg.exec():
            data = dlg.get_data()
            if self.role == "Owner":
                ok, msg = self.controller.owner_submit(data, self.user_data)
            else:
                ok, msg = self.controller.create(data, self.user_data)
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
        dlg = PropertyFormDialog(self, property_data=data,
                                 session_user=self.user_data)
        if dlg.exec():
            form_data = dlg.get_data()
            if self.role == "Owner":
                ok, msg = self.controller.owner_update(pid, form_data, self.user_data)
            else:
                ok, msg = self.controller.update(pid, form_data, self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self._refresh_all()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_approve_selected(self):
        pid = self._selected_property_id()
        if pid is None:
            return
        ok, msg = self.controller.approve(pid, self.user_data)
        if ok:
            QMessageBox.information(self, "Approved", msg)
            self._refresh_all()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_reject_selected(self):
        pid = self._selected_property_id()
        if pid is None:
            return
        reason, ok = QInputDialog.getText(
            self, "Reject property",
            f"Reject property submission #{pid}?\n\nReason (sent to the owner):"
        )
        if not ok or len(reason.strip()) < 3:
            return
        ok, msg = self.controller.reject(pid, reason, self.user_data)
        if ok:
            QMessageBox.information(self, "Rejected", msg)
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

    def _on_withdraw_selected(self):
        pid = self._selected_property_id()
        if pid is None:
            QMessageBox.information(self, "No selection", "Select one of your submissions.")
            return
        confirm = QMessageBox.question(
            self, "Withdraw submission",
            f"Withdraw your property submission #{pid}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.owner_withdraw(pid, self.user_data)
        if ok:
            QMessageBox.information(self, "Withdrawn", msg)
            self._refresh_all()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_row_double_click(self, index):
        self._on_edit_selected()
        self._update_approval_buttons_visibility()
