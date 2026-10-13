
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QInputDialog
)
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Qt
from Controllers.profile_controller import ProfileController
from ui import theme


class ProfileRequestsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = ProfileController()
        self.user_data = None
        self._build()
        print("[profile-requests] screen constructed")

    def set_user(self, user_data: dict):
        print(f"[profile-requests] set_user called — role={user_data.get('role') if user_data else None}")
        self.user_data = user_data
        self.refresh()

    def refresh(self):
        print("[profile-requests] refresh() starting")
        try:
            status = self.status_filter.currentText()
            print(f"[profile-requests] filter status='{status}'")

            if status == "Pending":
                rows = self.controller.list_pending_requests()
            else:
                rows = self.controller.list_all_requests()
                if status != "All":
                    rows = [r for r in rows if r["status"] == status]

            print(f"[profile-requests] query returned {len(rows)} row(s)")
            for r in rows[:5]:
                print(f"[profile-requests]   #{r['request_id']} {r['user_name']} "
                      f"{r['field_name']} -> {r['new_value']} [{r['status']}]")

            # Search filter
            q = self.search_input.text().strip().lower()
            if q:
                rows = [r for r in rows
                        if q in (r["user_name"] or "").lower()
                        or q in (r["field_name"] or "").lower()
                        or q in (r["user_email"] or "").lower()]
                print(f"[profile-requests] after search filter: {len(rows)} row(s)")

            self._populate_table(rows)
            self.count_label.setText(f"{len(rows)} request(s)")
            print("[profile-requests] refresh() done")

        except Exception as e:
            print(f"[profile-requests] ERROR during refresh: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(12)

        title = QLabel("🗂 Profile Change Requests")
        title.setStyleSheet(
            f"font-size: {theme.FS_2XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        header.addWidget(title)
        header.addStretch()

        btn_dashboard = QPushButton("← Dashboard")
        btn_dashboard.setCursor(Qt.PointingHandCursor)
        btn_dashboard.setFixedHeight(36)
        btn_dashboard.setStyleSheet(theme.button_qss("ghost"))
        btn_dashboard.clicked.connect(self._go_dashboard)
        header.addWidget(btn_dashboard)

        layout.addLayout(header)

        filters = QHBoxLayout()
        filters.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by user or field…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(theme.input_qss())
        self.search_input.returnPressed.connect(self.refresh)
        filters.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Pending", "All", "Approved", "Rejected"])
        self.status_filter.setFixedHeight(38)
        self.status_filter.setStyleSheet(theme.input_qss())
        self.status_filter.currentTextChanged.connect(self.refresh)
        filters.addWidget(self.status_filter)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setFixedHeight(38)
        btn_refresh.setStyleSheet(theme.button_qss("secondary"))
        btn_refresh.clicked.connect(self.refresh)
        filters.addWidget(btn_refresh)

        layout.addLayout(filters)

        self.count_label = QLabel("0 request(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "User", "Role", "Field", "Old → New", "Reason", "Status"]
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
        hv.setSectionResizeMode(4, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch()

        self.btn_approve = QPushButton("✓ Approve")
        self.btn_approve.setCursor(Qt.PointingHandCursor)
        self.btn_approve.setFixedHeight(38)
        self.btn_approve.setStyleSheet(theme.button_qss("success"))
        self.btn_approve.clicked.connect(self._on_approve)
        actions.addWidget(self.btn_approve)

        self.btn_reject = QPushButton("✕ Reject")
        self.btn_reject.setCursor(Qt.PointingHandCursor)
        self.btn_reject.setFixedHeight(38)
        self.btn_reject.setStyleSheet(theme.button_qss("danger"))
        self.btn_reject.clicked.connect(self._on_reject)
        actions.addWidget(self.btn_reject)

        layout.addLayout(actions)

    def _populate_table(self, rows):
        self.table.setRowCount(0)
        pending_bg = QBrush(QColor(theme.WARNING_SOFT))
        pending_fg = QBrush(QColor(theme.WARNING_HOVER))
        approved_bg = QBrush(QColor(theme.SUCCESS_SOFT))
        approved_fg = QBrush(QColor(theme.SUCCESS_HOVER))
        rejected_bg = QBrush(QColor(theme.DANGER_SOFT))
        rejected_fg = QBrush(QColor(theme.DANGER_HOVER))

        for i, r in enumerate(rows):
            self.table.insertRow(i)
            self.table.setRowHeight(i, 42)
            cells = [
                str(r["request_id"]),
                r["user_name"] or "",
                r["user_role"] or "",
                r["field_name"] or "",
                f"{r['old_value'] or '(empty)'} → {r['new_value']}",
                (r["reason"] or "")[:60],
                r["status"],
            ]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text if text is not None else "")
                if r["status"] == "Pending":
                    item.setBackground(pending_bg)
                    item.setForeground(pending_fg)
                elif r["status"] == "Approved":
                    item.setBackground(approved_bg)
                    item.setForeground(approved_fg)
                elif r["status"] == "Rejected":
                    item.setBackground(rejected_bg)
                    item.setForeground(rejected_fg)
                self.table.setItem(i, c, item)

    def _selected_request(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if not item:
            return None
        rid = int(item.text())
        for r in self.controller.list_all_requests():
            if r["request_id"] == rid:
                return r
        return None

    def _go_dashboard(self):
        self.parent_window._set_screen("dashboard")

    def _on_approve(self):
        req = self._selected_request()
        if not req:
            QMessageBox.information(self, "No selection", "Select a request first.")
            return
        if req["status"] != "Pending":
            QMessageBox.information(self, "Not pending",
                                    "Only pending requests can be approved.")
            return
        confirm = QMessageBox.question(
            self, "Approve change",
            f"Approve the {req['field_name']} change for {req['user_name']}?\n\n"
            f"From: {req['old_value'] or '(empty)'}\n"
            f"To:   {req['new_value']}",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.approve_change(req["request_id"], self.user_data)
        if ok:
            QMessageBox.information(self, "Approved", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_reject(self):
        req = self._selected_request()
        if not req:
            QMessageBox.information(self, "No selection", "Select a request first.")
            return
        if req["status"] != "Pending":
            QMessageBox.information(self, "Not pending",
                                    "Only pending requests can be rejected.")
            return
        reason, ok = QInputDialog.getText(
            self, "Reject change",
            f"Reject the {req['field_name']} change for {req['user_name']}?\n\n"
            f"Reason (sent to the user):"
        )
        if not ok or len(reason.strip()) < 3:
            return
        ok, msg = self.controller.reject_change(req["request_id"], reason,
                                                 self.user_data)
        if ok:
            QMessageBox.information(self, "Rejected", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)
