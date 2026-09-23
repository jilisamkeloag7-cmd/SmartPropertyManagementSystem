print(">>> applications_screen.py V3 <<<")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QInputDialog,
    QScrollArea, QGridLayout, QFrame
)
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Qt
from Controllers.lease_application_controller import LeaseApplicationController
from ui.widgets.entity_cards import TenantApplicationCard
from ui import theme


CARD_COLS = 2
CARD_GAP = 16


class ApplicationsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = LeaseApplicationController()
        self.user_data = None
        self.role = ""
        self.is_manager = False
        self.is_tenant = False
        self.is_owner = False
        self._build()

    def set_user(self, user_data: dict):
        self.user_data = user_data or {}
        self.role = self.user_data.get("role", "")
        self.is_manager = self.role in ("Administrator", "Property Manager")
        self.is_tenant = self.role == "Tenant"
        self.is_owner = self.role == "Owner"
        self._apply_role_ui()
        self.refresh()

    def refresh(self):
        filters = {
            "query": self.search_input.text().strip(),
            "status": self.status_filter.currentText(),
        }
        rows = self.controller.list(filters, self.user_data)
        self.count_label.setText(f"{len(rows)} application(s)")

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

        self.title_label = QLabel("📝 Applications")
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
        self.status_filter.addItems(
            ["All", "Pending", "Approved", "Declined", "Cancelled"]
        )
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

        self.count_label = QLabel("0 application(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Property", "Tenant", "Start", "Duration", "Status", "Note"]
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
        for i in range(7):
            hv.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.Stretch)
        hv.setSectionResizeMode(6, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        # Card container (tenant)
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setSpacing(CARD_GAP)
        self.cards_grid.setContentsMargins(0, 0, 0, 0)
        self.cards_grid.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.cards_container, stretch=1)

        # Actions
        self.actions = QHBoxLayout()
        self.actions.setSpacing(10)
        self.actions.addStretch()

        self.btn_approve = QPushButton("Approve")
        self.btn_approve.setCursor(Qt.PointingHandCursor)
        self.btn_approve.setFixedHeight(38)
        self.btn_approve.setStyleSheet(theme.button_qss("success"))
        self.btn_approve.clicked.connect(self._on_approve)
        self.actions.addWidget(self.btn_approve)

        self.btn_decline = QPushButton("Decline")
        self.btn_decline.setCursor(Qt.PointingHandCursor)
        self.btn_decline.setFixedHeight(38)
        self.btn_decline.setStyleSheet(theme.button_qss("danger"))
        self.btn_decline.clicked.connect(self._on_decline)
        self.actions.addWidget(self.btn_decline)

        layout.addLayout(self.actions)

    def _apply_role_ui(self):
        if self.role == "Administrator":
            self.title_label.setText("📝 All Lease Applications")
            self.readonly_badge.setVisible(False)
        elif self.role == "Property Manager":
            self.title_label.setText("📝 Lease Applications")
            self.readonly_badge.setVisible(False)
        elif self.role == "Owner":
            self.title_label.setText("📝 Applications on My Properties")
            self.readonly_badge.setVisible(True)
        elif self.role == "Tenant":
            self.title_label.setText("📝 My Applications")
            self.readonly_badge.setVisible(False)
        else:
            self.title_label.setText("📝 Applications")
            self.readonly_badge.setVisible(False)

        self.btn_approve.setVisible(self.is_manager)
        self.btn_decline.setVisible(self.is_manager)

        self.table.setVisible(not self.is_tenant)
        self.cards_container.setVisible(self.is_tenant)

    def _populate_table(self, rows):
        self.table.setRowCount(0)
        pending_bg = QBrush(QColor(theme.WARNING_SOFT))
        pending_fg = QBrush(QColor(theme.WARNING_HOVER))
        approved_bg = QBrush(QColor(theme.SUCCESS_SOFT))
        approved_fg = QBrush(QColor(theme.SUCCESS_HOVER))
        declined_bg = QBrush(QColor(theme.DANGER_SOFT))
        declined_fg = QBrush(QColor(theme.DANGER_HOVER))

        for r, a in enumerate(rows):
            self.table.insertRow(r)
            self.table.setRowHeight(r, 42)

            if a.get("decision_note"):
                note = f"[manager] {a['decision_note']}"
            elif a.get("message"):
                note = a["message"]
            else:
                note = "—"

            cells = [
                str(a["application_id"]),
                a["property_address"] or "",
                a["tenant_name"] or "",
                str(a["preferred_start"]) if a["preferred_start"] else "",
                f"{a['duration_months']} mo",
                a["status"] or "",
                note[:80],
            ]
            status = a["status"]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if status == "Pending":
                    item.setBackground(pending_bg)
                    item.setForeground(pending_fg)
                elif status == "Approved":
                    item.setBackground(approved_bg)
                    item.setForeground(approved_fg)
                elif status == "Declined":
                    item.setBackground(declined_bg)
                    item.setForeground(declined_fg)
                self.table.setItem(r, c, item)

    def _populate_cards(self, rows):
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

        if not rows:
            empty = QLabel(
                "No applications yet.\n\n"
                "Browse properties and click 'Apply for Lease' to get started."
            )
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_MD}px; "
                f"padding: 60px;"
            )
            self.cards_grid.addWidget(empty, 0, 0, 1, CARD_COLS)
            return

        for i, a in enumerate(rows):
            card = TenantApplicationCard(a, on_withdraw=self._card_withdraw)
            row = i // CARD_COLS
            col = i % CARD_COLS
            self.cards_grid.addWidget(card, row, col)

    # ------------------------------------------------------------------ helpers
    def _selected_application(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if not item:
            return None
        return self.controller.get(int(item.text()))

    def _go_dashboard(self):
        self.parent_window._set_screen("dashboard")

    # ------------------------------------------------------------------ handlers
    def _on_approve(self):
        if not self.is_manager:
            return
        a = self._selected_application()
        if not a:
            QMessageBox.information(self, "No selection", "Select an application first.")
            return
        if a["status"] != "Pending":
            QMessageBox.information(self, "Not pending",
                                    "Only pending applications can be approved.")
            return

        confirm = QMessageBox.question(
            self, "Approve application",
            f"Approve {a['tenant_name']}'s application for {a['property_address']}?\n\n"
            f"Start: {a['preferred_start']}\n"
            f"Duration: {a['duration_months']} months\n"
            f"Rent: R{a['property_listing_price'] or 0:,.0f}/month\n\n"
            f"A lease will be created automatically. All other pending "
            f"applications for this property will be declined.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        note, ok = QInputDialog.getText(
            self, "Approval note",
            "Optional note for the tenant:"
        )
        if not ok:
            return

        ok, msg = self.controller.approve(a["application_id"], note, self.user_data)
        if ok:
            QMessageBox.information(self, "Approved", msg)
            self.refresh()
            self.parent_window.properties_screen.refresh()
            self.parent_window.leases_screen.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_decline(self):
        if not self.is_manager:
            return
        a = self._selected_application()
        if not a:
            QMessageBox.information(self, "No selection", "Select an application first.")
            return
        if a["status"] != "Pending":
            QMessageBox.information(self, "Not pending",
                                    "Only pending applications can be declined.")
            return

        reason, ok = QInputDialog.getText(
            self, "Decline application",
            f"Decline {a['tenant_name']}'s application?\n\n"
            f"Reason (sent to the tenant):"
        )
        if not ok or len(reason.strip()) < 3:
            return

        ok, msg = self.controller.decline(a["application_id"], reason, self.user_data)
        if ok:
            QMessageBox.information(self, "Declined", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    # ---- tenant card action
    def _card_withdraw(self, application: dict):
        confirm = QMessageBox.question(
            self, "Withdraw application",
            f"Withdraw your application for {application['property_address']}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.withdraw(application["application_id"],
                                            self.user_data)
        if ok:
            QMessageBox.information(self, "Withdrawn", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)