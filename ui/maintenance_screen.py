print(">>> maintenance_screen.py V1 <<<")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtGui import QBrush, QColor
from Controllers.maintenance_controller import MaintenanceController
from ui.maintenance_form_dialog import MaintenanceFormDialog
from ui.maintenance_detail_dialog import MaintenanceDetailDialog


PRIORITY_COLORS = {
    "Low":      QColor("#95a5a6"),
    "Medium":   QColor("#2980b9"),
    "High":     QColor("#e67e22"),
    "Urgent":   QColor("#c0392b"),
}


class MaintenanceScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = MaintenanceController()
        self.user_data = None
        self.is_manager = False
        self._build()

    # ------------------------------------------------------------------ API
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

    # ------------------------------------------------------------------ UI
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # Header
        header = QHBoxLayout()

        self.header_title = QLabel("🔧 Maintenance")
        self.header_title.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #2c3e50;"
        )
        header.addWidget(self.header_title)

        self.readonly_badge = QLabel("Read-only")
        self.readonly_badge.setStyleSheet(
            "background: #fef3cd; color: #856404; "
            "padding: 3px 10px; border-radius: 6px; "
            "font-size: 11px; font-weight: bold;"
        )
        self.readonly_badge.setVisible(False)
        header.addWidget(self.readonly_badge)

        header.addStretch()

        btn_dashboard = QPushButton("← Dashboard")
        btn_dashboard.setStyleSheet(
            "background: transparent; color: #7f8c8d; border: none; "
            "font-size: 13px; padding: 6px 10px;"
        )
        btn_dashboard.clicked.connect(self._go_dashboard)
        header.addWidget(btn_dashboard)

        self.btn_add = QPushButton("+ Submit Request")
        self.btn_add.setFixedHeight(38)
        self.btn_add.setStyleSheet(
            "background-color: #3498db; color: white; border: none; "
            "border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 18px;"
        )
        self.btn_add.clicked.connect(self._on_add)
        header.addWidget(self.btn_add)

        layout.addLayout(header)

        # Filters
        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by address, submitter or description…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(
            "padding: 0 12px; border: 2px solid #ecf0f1; border-radius: 10px; "
            "font-size: 13px; background: white;"
        )
        self.search_input.returnPressed.connect(self.refresh)
        filters_row.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Open", "In Progress", "Resolved", "Closed"])
        self.status_filter.setFixedHeight(38)
        self.status_filter.setStyleSheet(
            "padding: 0 12px; border: 2px solid #ecf0f1; border-radius: 10px; "
            "font-size: 13px; background: white;"
        )
        self.status_filter.currentTextChanged.connect(self.refresh)
        filters_row.addWidget(self.status_filter)

        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["All", "Low", "Medium", "High", "Urgent"])
        self.priority_filter.setFixedHeight(38)
        self.priority_filter.setStyleSheet(
            "padding: 0 12px; border: 2px solid #ecf0f1; border-radius: 10px; "
            "font-size: 13px; background: white;"
        )
        self.priority_filter.currentTextChanged.connect(self.refresh)
        filters_row.addWidget(self.priority_filter)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setFixedHeight(38)
        btn_refresh.setStyleSheet(
            "background: #ecf0f1; color: #2c3e50; border: none; "
            "border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 18px;"
        )
        btn_refresh.clicked.connect(self.refresh)
        filters_row.addWidget(btn_refresh)

        layout.addLayout(filters_row)

        self.count_label = QLabel("0 request(s)")
        self.count_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.count_label)

        # Table
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
        self.table.setStyleSheet("""
            QTableWidget {
                background: white; border: 1px solid #ecf0f1;
                border-radius: 12px; font-size: 13px;
                gridline-color: #ecf0f1;
            }
            QHeaderView::section {
                background: #f8fbfe; color: #2c3e50;
                padding: 10px; border: none;
                font-weight: bold; font-size: 12px;
            }
            QTableWidget::item { padding: 8px; }
            QTableWidget::item:selected {
                background: #eaf3fb; color: #2c3e50;
            }
        """)
        hv = self.table.horizontalHeader()
        for i in range(8):
            hv.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.Stretch)
        hv.setSectionResizeMode(7, QHeaderView.Stretch)
        layout.addWidget(self.table, stretch=1)

        # Actions
        actions = QHBoxLayout()
        actions.addStretch()

        self.btn_open = QPushButton("Open Selected")
        self.btn_open.setFixedHeight(38)
        self.btn_open.setStyleSheet(
            "background: #3498db; color: white; border: none; "
            "border-radius: 10px; font-size: 13px; font-weight: bold; padding: 0 18px;"
        )
        self.btn_open.clicked.connect(self._on_open_selected)
        actions.addWidget(self.btn_open)

        layout.addLayout(actions)

    # ------------------------------------------------------------------ role UI
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

    # ------------------------------------------------------------------ helpers
    def _populate_table(self, rows):
        self.table.setRowCount(0)
        for r, m in enumerate(rows):
            self.table.insertRow(r)
            cells = [
                str(m["request_id"]),
                m["property_address"] or "",
                m["submitter_name"] or "",
                m["priority"] or "",
                m["status"] or "",
                str(m["created_at"]) if m["created_at"] else "",
                str(m["completed_at"]) if m["completed_at"] else "—",
                (m["description"] or "")[:80],
            ]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if c == 3 and m["priority"] in PRIORITY_COLORS:
                    item.setForeground(QBrush(PRIORITY_COLORS[m["priority"]]))
                self.table.setItem(r, c, item)

    def _selected_request_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    # ------------------------------------------------------------------ handlers
    def _go_dashboard(self):
        self.parent_window.stacked_widget.setCurrentIndex(3)

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