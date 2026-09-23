print(">>> viewings_screen.py V2 <<<")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QInputDialog
)
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Qt
from Controllers.viewing_controller import ViewingController
from ui import theme


class ViewingsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = ViewingController()
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
        self._populate_table(rows)
        self.count_label.setText(f"{len(rows)} viewing request(s)")

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(12)

        self.title_label = QLabel("📅 Viewings")
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

        self.count_label = QLabel("0 viewing request(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Property", "Tenant", "Date", "Time", "Status", "Note"]
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

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch()

        self.btn_cancel = QPushButton("Cancel My Request")
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.setFixedHeight(38)
        self.btn_cancel.setStyleSheet(theme.button_qss("secondary"))
        self.btn_cancel.clicked.connect(self._on_cancel)
        actions.addWidget(self.btn_cancel)

        self.btn_approve = QPushButton("Approve")
        self.btn_approve.setCursor(Qt.PointingHandCursor)
        self.btn_approve.setFixedHeight(38)
        self.btn_approve.setStyleSheet(theme.button_qss("success"))
        self.btn_approve.clicked.connect(self._on_approve)
        actions.addWidget(self.btn_approve)

        self.btn_decline = QPushButton("Decline")
        self.btn_decline.setCursor(Qt.PointingHandCursor)
        self.btn_decline.setFixedHeight(38)
        self.btn_decline.setStyleSheet(theme.button_qss("danger"))
        self.btn_decline.clicked.connect(self._on_decline)
        actions.addWidget(self.btn_decline)

        layout.addLayout(actions)

    def _apply_role_ui(self):
        if self.role == "Administrator":
            self.title_label.setText("📅 All Viewing Requests")
            self.readonly_badge.setVisible(False)
        elif self.role == "Property Manager":
            self.title_label.setText("📅 Viewing Requests")
            self.readonly_badge.setVisible(False)
        elif self.role == "Owner":
            self.title_label.setText("📅 Viewings on My Properties")
            self.readonly_badge.setVisible(True)
        elif self.role == "Tenant":
            self.title_label.setText("📅 My Viewing Requests")
            self.readonly_badge.setVisible(False)
        else:
            self.title_label.setText("📅 Viewings")
            self.readonly_badge.setVisible(False)

        self.btn_cancel.setVisible(self.is_tenant)
        self.btn_approve.setVisible(self.is_manager)
        self.btn_decline.setVisible(self.is_manager)

    def _populate_table(self, rows):
        self.table.setRowCount(0)
        pending_bg = QBrush(QColor(theme.WARNING_SOFT))
        pending_fg = QBrush(QColor(theme.WARNING_HOVER))
        approved_bg = QBrush(QColor(theme.SUCCESS_SOFT))
        approved_fg = QBrush(QColor(theme.SUCCESS_HOVER))
        declined_bg = QBrush(QColor(theme.DANGER_SOFT))
        declined_fg = QBrush(QColor(theme.DANGER_HOVER))

        for r, v in enumerate(rows):
            self.table.insertRow(r)
            self.table.setRowHeight(r, 42)

            if v.get("manager_note"):
                note_text = f"[manager] {v['manager_note']}"
            elif v.get("message"):
                note_text = v["message"]
            else:
                note_text = "—"

            cells = [
                str(v["request_id"]),
                v["property_address"] or "",
                v["tenant_name"] or "",
                str(v["preferred_date"]) if v["preferred_date"] else "",
                v["preferred_time"] or "",
                v["status"] or "",
                note_text[:80],
            ]
            status = v["status"]
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

    def _selected_viewing(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if not item:
            return None
        return self.controller.get(int(item.text()))

    def _go_dashboard(self):
        self.parent_window._set_screen("dashboard")

    def _on_approve(self):
        if not self.is_manager:
            return
        v = self._selected_viewing()
        if not v:
            QMessageBox.information(self, "No selection", "Select a request first.")
            return
        if v["status"] != "Pending":
            QMessageBox.information(self, "Not pending", "Only pending requests can be approved.")
            return

        note, ok = QInputDialog.getText(
            self, "Approve viewing",
            f"Approve the viewing request from {v['tenant_name']} "
            f"for {v['preferred_date']} ({v['preferred_time']})?\n\n"
            f"Optional note for the tenant:"
        )
        if not ok:
            return

        ok, msg = self.controller.approve(v["request_id"], note, self.user_data)
        if ok:
            QMessageBox.information(self, "Approved", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_decline(self):
        if not self.is_manager:
            return
        v = self._selected_viewing()
        if not v:
            QMessageBox.information(self, "No selection", "Select a request first.")
            return
        if v["status"] != "Pending":
            QMessageBox.information(self, "Not pending", "Only pending requests can be declined.")
            return

        reason, ok = QInputDialog.getText(
            self, "Decline viewing",
            f"Decline the viewing request from {v['tenant_name']}?\n\n"
            f"Reason (will be sent to the tenant):"
        )
        if not ok or len(reason.strip()) < 3:
            return

        ok, msg = self.controller.decline(v["request_id"], reason, self.user_data)
        if ok:
            QMessageBox.information(self, "Declined", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_cancel(self):
        if not self.is_tenant:
            return
        v = self._selected_viewing()
        if not v:
            QMessageBox.information(self, "No selection", "Select a request first.")
            return
        if v["status"] != "Pending":
            QMessageBox.information(
                self, "Cannot cancel",
                "Only pending requests can be cancelled."
            )
            return

        confirm = QMessageBox.question(
            self, "Cancel request",
            f"Cancel your viewing request for {v['property_address']}?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return

        ok, msg = self.controller.cancel(v["request_id"], self.user_data)
        if ok:
            QMessageBox.information(self, "Cancelled", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)