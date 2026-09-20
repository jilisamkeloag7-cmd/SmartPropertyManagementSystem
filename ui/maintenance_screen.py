print(">>> maintenance_screen.py V2 <<<")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Qt
from Controllers.maintenance_controller import MaintenanceController
from ui.maintenance_form_dialog import MaintenanceFormDialog
from ui.maintenance_detail_dialog import MaintenanceDetailDialog
from ui import theme


PRIORITY_COLORS = {
    "Low":    theme.TEXT_FAINT,
    "Medium": theme.INFO,
    "High":   theme.WARNING_HOVER,
    "Urgent": theme.DANGER_HOVER,
}


class MaintenanceScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = MaintenanceController()
        self.user_data = None
        self.is_manager = False
        self._build()

    def set_user(self, user_data: dict):
        self.user_data = user_data
        role = (user_data or {}).get("role", "")
        self.is_manager = role in ("Administrator", "Property Manager")
        self._apply_role_ui()
        self.refresh()

    def refresh(self):
        filters = {
            "query": self.search_input.text().strip(),
            "status": self.status_filter.currentText(),
            "priority": self.priority_filter.currentText(),
        }
        rows = self.controller.list(filters, self.user_data)
        self._populate_table(rows)
        self.count_label.setText(f"{len(rows)} request(s)")

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(12)

        self.header_title = QLabel("🔧 Maintenance")
        self.header_title.setStyleSheet(
            f"font-size: {theme.FS_2XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        header.addWidget(self.header_title)

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

        self.btn_add = QPushButton("+ Submit Request")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setFixedHeight(36)
        self.btn_add.setStyleSheet(theme.button_qss("primary"))
        self.btn_add.clicked.connect(self._on_add)
        header.addWidget(self.btn_add)

        layout.addLayout(header)

        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by address, submitter or description…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(theme.input_qss())
        self.search_input.returnPressed.connect(self.refresh)
        filters_row.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Open", "In Progress", "Resolved", "Closed"])
        self.status_filter.setFixedHeight(38)
        self.status_filter.setStyleSheet(theme.input_qss())
        self.status_filter.currentTextChanged.connect(self.refresh)
        filters_row.addWidget(self.status_filter)

        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["All", "Low", "Medium", "High", "Urgent"])
        self.priority_filter.setFixedHeight(38)
        self.priority_filter.setStyleSheet(theme.input_qss())
        self.priority_filter.currentTextChanged.connect(self.refresh)
        filters_row.addWidget(self.priority_filter)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setCursor(Qt.PointingHandCursor)
        btn_refresh.setFixedHeight(38)
        btn_refresh.setStyleSheet(theme.button_qss("secondary"))
        btn_refresh.clicked.connect(self.refresh)
        filters_row.addWidget(btn_refresh)

        layout.addLayout(filters_row)

        self.count_label = QLabel("0 request(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Property", "Submitter", "Priority", "Status", "Created", "Completed", "Description"]
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
        for i in range(8):
            hv.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.Stretch)
        hv.setSectionResizeMode(7, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch()

        self.btn_open = QPushButton("Open Selected")
        self.btn_open.setCursor(Qt.PointingHandCursor)
        self.btn_open.setFixedHeight(38)
        self.btn_open.setStyleSheet(theme.button_qss("primary"))
        self.btn_open.clicked.connect(self._on_open_selected)
        actions.addWidget(self.btn_open)

        layout.addLayout(actions)

    def _apply_role_ui(self):
        role = (self.user_data or {}).get("role", "")

        if role == "Administrator":
            self.header_title.setText("🔧 All Maintenance Requests")
            self.readonly_badge.setVisible(False)
            self.btn_add.setVisible(True)
        elif role == "Property Manager":
            self.header_title.setText("🔧 Maintenance Requests")
            self.readonly_badge.setVisible(False)
            self.btn_add.setVisible(True)
        elif role == "Owner":
            self.header_title.setText("🔧 Maintenance on My Properties")
            self.readonly_badge.setVisible(True)
            self.btn_add.setVisible(False)
        elif role == "Tenant":
            self.header_title.setText("🔧 My Maintenance Requests")
            self.readonly_badge.setVisible(False)
            self.btn_add.setVisible(True)
        else:
            self.header_title.setText("🔧 Maintenance")
            self.readonly_badge.setVisible(False)

    def _populate_table(self, rows):
        self.table.setRowCount(0)
        for r, m in enumerate(rows):
            self.table.insertRow(r)
            self.table.setRowHeight(r, 42)
            cells = [
                str(m["request_id"]),
                m["property_address"] or "",
                m["submitter_name"] or "",
                m["priority"] or "",
                m["status"] or "",
                str(m["created_at"])[:16] if m["created_at"] else "",
                str(m["completed_at"])[:16] if m["completed_at"] else "—",
                (m["description"] or "")[:80],
            ]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if c == 3 and m["priority"] in PRIORITY_COLORS:
                    item.setForeground(QBrush(QColor(PRIORITY_COLORS[m["priority"]])))
                self.table.setItem(r, c, item)

    def _selected_request_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def _go_dashboard(self):
        self.parent_window._set_screen("dashboard")

    def _on_add(self):
        dlg = MaintenanceFormDialog(self, session_user=self.user_data)
        if dlg.exec():
            ok, msg = self.controller.submit(dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self.refresh()
                self.parent_window.properties_screen.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_open_selected(self):
        rid = self._selected_request_id()
        if rid is None:
            QMessageBox.information(self, "No selection", "Select a request first.")
            return
        data = self.controller.get(rid)
        if not data:
            QMessageBox.warning(self, "Error", "Request not found.")
            return
        dlg = MaintenanceDetailDialog(self, request_data=data, session_user=self.user_data)
        if dlg.exec():
            new_status = getattr(dlg, "new_status", None)
            if new_status:
                ok, msg = self.controller.update_status(rid, new_status, self.user_data)
                if ok:
                    QMessageBox.information(self, "Success", msg)
                    self.refresh()
                    self.parent_window.properties_screen.refresh()
                else:
                    QMessageBox.warning(self, "Error", msg)

    def _on_row_double_click(self, index):
        self._on_open_selected()