
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QScrollArea,
    QGridLayout, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from Controllers.lease_controller import LeaseController
from ui.lease_form_dialog import LeaseFormDialog
from ui.lease_termination_dialog import LeaseTerminationDialog
from ui.widgets.entity_cards import TenantLeaseCard
from ui import theme

from Repositories.ownership_repository import OwnershipRepository


TENANT_CARD_COLS = 2
CARD_GAP = 16


class LeasesScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = LeaseController()
        self.user_data = None
        self.role = ""
        self.is_writer = False
        self.is_admin = False
        self.is_tenant = False
        self._build()

    def set_user(self, user_data: dict):
        self.user_data = user_data or {}
        self.role = self.user_data.get("role", "")
        self.is_writer = self.role in ("Administrator", "Property Manager")
        self.is_admin = self.role == "Administrator"
        self.is_tenant = self.role == "Tenant"
        self._apply_role_ui()
        self.refresh()

    def refresh(self):
        filters = {
            "query": self.search_input.text().strip(),
            "status": self.status_filter.currentText(),
        }
        rows = self.controller.list(filters)

        if self.role == "Owner":
            uid = self.user_data.get("user_id")
            owned_pids = set(OwnershipRepository().property_ids_for_owner(uid))
            rows = [r for r in rows if r["property_id"] in owned_pids]
        elif self.role == "Tenant":
            uid = self.user_data.get("user_id")
            rows = [r for r in rows if r["tenant_id"] == uid]

        self.count_label.setText(f"{len(rows)} lease record(s)")

        if self.is_tenant:
            self._populate_cards(rows)
        else:
            self._populate_table(rows)

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

        # Header
        header = QHBoxLayout()
        header.setSpacing(12)

        self.title_label = QLabel("📄 Leases")
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

        self.btn_add = QPushButton("+ Create Lease")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setFixedHeight(36)
        self.btn_add.setStyleSheet(theme.button_qss("primary"))
        self.btn_add.clicked.connect(self._on_add)
        header.addWidget(self.btn_add)

        layout.addLayout(header)

        # Filters
        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by property address or tenant…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(theme.input_qss())
        self.search_input.returnPressed.connect(self.refresh)
        filters_row.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Expired", "Terminated"])
        self.status_filter.setFixedHeight(38)
        self.status_filter.setStyleSheet(theme.input_qss())
        self.status_filter.currentTextChanged.connect(self.refresh)
        filters_row.addWidget(self.status_filter)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setFixedHeight(38)
        btn_refresh.setStyleSheet(theme.button_qss("secondary"))
        btn_refresh.clicked.connect(self.refresh)
        filters_row.addWidget(btn_refresh)

        layout.addLayout(filters_row)

        self.count_label = QLabel("0 lease record(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        # Table (non-tenant)
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Property", "Tenant", "Start", "End", "Rent", "Status", "Request"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
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
        for i in range(8):
            hv.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        # Cards container (tenant)
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setSpacing(CARD_GAP)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.cards_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.cards_container, stretch=1)

        # Actions (non-tenant)
        self.actions_row = QHBoxLayout()
        self.actions_row.setSpacing(10)
        self.actions_row.addStretch()

        self.btn_reject = QPushButton("Reject Request")
        self.btn_reject.setCursor(Qt.PointingHandCursor)
        self.btn_reject.setFixedHeight(38)
        self.btn_reject.setStyleSheet(theme.button_qss("secondary"))
        self.btn_reject.clicked.connect(self._on_reject_termination)
        self.actions_row.addWidget(self.btn_reject)

        self.btn_approve = QPushButton("Approve Termination")
        self.btn_approve.setCursor(Qt.PointingHandCursor)
        self.btn_approve.setFixedHeight(38)
        self.btn_approve.setStyleSheet(theme.button_qss("danger"))
        self.btn_approve.clicked.connect(self._on_approve_termination)
        self.actions_row.addWidget(self.btn_approve)

        self.btn_terminate = QPushButton("Terminate Selected")
        self.btn_terminate.setCursor(Qt.PointingHandCursor)
        self.btn_terminate.setFixedHeight(38)
        self.btn_terminate.setStyleSheet(theme.button_qss("danger"))
        self.btn_terminate.setToolTip(
            "Direct termination — bypasses the tenant request workflow. Admin only."
        )
        self.btn_terminate.clicked.connect(self._on_terminate_selected)
        self.actions_row.addWidget(self.btn_terminate)

        layout.addLayout(self.actions_row)

    def _apply_role_ui(self):
        if self.role == "Administrator":
            self.title_label.setText("📄 All Leases")
            self.readonly_badge.setVisible(False)
        elif self.role == "Property Manager":
            self.title_label.setText("📄 Leases")
            self.readonly_badge.setVisible(False)
        elif self.role == "Owner":
            self.title_label.setText("📄 Leases on My Properties")
            self.readonly_badge.setVisible(True)
        elif self.role == "Tenant":
            self.title_label.setText("📄 My Leases")
            self.readonly_badge.setVisible(False)
        else:
            self.title_label.setText("📄 Leases")
            self.readonly_badge.setVisible(False)

        self.btn_add.setVisible(self.is_writer)
        self.btn_terminate.setVisible(self.is_admin)
        self.btn_reject.setVisible(self.is_writer)
        self.btn_approve.setVisible(self.is_writer)

        self.table.setVisible(not self.is_tenant)
        self.cards_container.setVisible(self.is_tenant)
        self.actions_row_visible = not self.is_tenant
        for w in [self.btn_reject, self.btn_approve, self.btn_terminate]:
            w.setVisible(w.isVisible() and not self.is_tenant)

    def _populate_table(self, rows):
        self.table.setRowCount(0)
        warning_bg = QBrush(QColor(theme.WARNING_SOFT))
        warning_fg = QBrush(QColor(theme.WARNING_HOVER))

        for r, l in enumerate(rows):
            self.table.insertRow(r)
            self.table.setRowHeight(r, 42)
            request_pending = l.get("termination_requested", False)
            request_label = "⚠ Pending" if request_pending else "—"

            cells = [
                str(l["lease_id"]),
                l["property_address"] or "",
                l["tenant_name"] or "",
                str(l["start_date"]) if l["start_date"] else "",
                str(l["end_date"]) if l["end_date"] else "",
                f"R{l['rent_amount']:.2f}" if l["rent_amount"] else "",
                l["status"] or "",
                request_label,
            ]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if c == 7 and request_pending:
                    item.setBackground(warning_bg)
                    item.setForeground(warning_fg)
                    reason = l.get("termination_reason") or "(no reason)"
                    item.setToolTip(f"Reason: {reason}")
                self.table.setItem(r, c, item)

    def _populate_cards(self, rows):
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not rows:
            empty = QLabel(
                "You have no active leases yet.\n\n"
                "Browse properties and apply for one to get started."
            )
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_MD}px; "
                f"padding: 60px;"
            )
            self.cards_grid.addWidget(empty, 0, 0, 1, TENANT_CARD_COLS)
            return

        for i, l in enumerate(rows):
            card = TenantLeaseCard(l, on_request_termination=self._card_request_termination)
            row = i // TENANT_CARD_COLS
            col = i % TENANT_CARD_COLS
            self.cards_grid.addWidget(card, row, col)

    # ------------------------------------------------------------------ actions
    def _go_dashboard(self):
        self.parent_window._set_screen("dashboard")

    def _selected_lease_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def _selected_lease(self):
        lid = self._selected_lease_id()
        if lid is None:
            return None
        return self.controller.get(lid)

    def _on_add(self):
        dlg = LeaseFormDialog(self)
        if dlg.exec():
            ok, msg = self.controller.create(dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self.refresh()
                self.parent_window.properties_screen.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_terminate_selected(self):
        if not self.is_admin:
            return
        lid = self._selected_lease_id()
        if lid is None:
            QMessageBox.information(self, "No selection", "Select a lease to terminate.")
            return
        confirm = QMessageBox.question(
            self, "Terminate lease directly",
            f"Terminate lease #{lid} directly?\n\n"
            f"This bypasses the tenant request workflow.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.terminate(lid, self.user_data)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self.refresh()
            self.parent_window.properties_screen.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_approve_termination(self):
        if not self.is_writer:
            return
        lease = self._selected_lease()
        if not lease:
            QMessageBox.information(self, "No selection", "Select a lease.")
            return
        if not lease["termination_requested"]:
            QMessageBox.information(self, "Nothing to approve",
                                    "This lease has no pending termination request.")
            return

        reason = lease.get("termination_reason") or "(no reason given)"
        confirm = QMessageBox.question(
            self, "Approve termination",
            f"Approve termination of lease #{lease['lease_id']}?\n\n"
            f"Tenant's reason:\n{reason}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.approve_termination(
            lease["lease_id"], self.user_data
        )
        if ok:
            QMessageBox.information(self, "Approved", msg)
            self.refresh()
            self.parent_window.properties_screen.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_reject_termination(self):
        if not self.is_writer:
            return
        lease = self._selected_lease()
        if not lease:
            QMessageBox.information(self, "No selection", "Select a lease.")
            return
        if not lease["termination_requested"]:
            QMessageBox.information(self, "Nothing to reject",
                                    "This lease has no pending termination request.")
            return

        reason = lease.get("termination_reason") or "(no reason given)"
        confirm = QMessageBox.question(
            self, "Reject termination",
            f"Reject the termination request for lease #{lease['lease_id']}?\n\n"
            f"Tenant's reason:\n{reason}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.reject_termination(
            lease["lease_id"], self.user_data
        )
        if ok:
            QMessageBox.information(self, "Rejected", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    # ---- tenant card action
    def _card_request_termination(self, lease: dict):
        dlg = LeaseTerminationDialog(self, lease_data=lease)
        if dlg.exec():
            ok, msg = self.controller.request_termination(
                lease["lease_id"], dlg.get_reason(), self.user_data
            )
            if ok:
                QMessageBox.information(self, "Submitted", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)
