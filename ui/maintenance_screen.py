
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView, QScrollArea,
    QFrame
)
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Qt
from Controllers.maintenance_controller import MaintenanceController
from ui.maintenance_form_dialog import MaintenanceFormDialog
from ui.maintenance_detail_dialog import MaintenanceDetailDialog
from ui.widgets.entity_cards import MaintenanceKanbanCard, KanbanColumn
from ui import theme


PRIORITY_COLORS = {
    "Low":    theme.TEXT_FAINT,
    "Medium": theme.INFO,
    "High":   theme.WARNING_HOVER,
    "Urgent": theme.DANGER_HOVER,
}

COLUMNS = [
    ("Open",         "#0ea5e9"),
    ("In Progress",  "#f59e0b"),
    ("Resolved",     "#10b981"),
    ("Closed",       "#94a3b8"),
]


class MaintenanceScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = MaintenanceController()
        self.user_data = None
        self.role = ""
        self.is_tenant = False
        self.is_owner = False
        self.is_manager = False
        self.column_widgets = {}
        self._build()

    def set_user(self, user_data: dict):
        self.user_data = user_data or {}
        self.role = self.user_data.get("role", "")
        self.is_tenant = self.role == "Tenant"
        self.is_owner = self.role == "Owner"
        self.is_manager = self.role in ("Administrator", "Property Manager")
        self._apply_role_ui()
        self.refresh()

    def refresh(self):
        filters = {
            "query": self.search_input.text().strip(),
            "status": self.status_filter.currentText(),
            "priority": self.priority_filter.currentText(),
        }
        rows = self.controller.list(filters, self.user_data)
        self.count_label.setText(f"{len(rows)} request(s)")

        if self.is_owner:
            self._populate_table(rows)
        else:
            self._populate_kanban(rows)

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

        self.header_title = QLabel("🔧 Maintenance")
        self.header_title.setStyleSheet(
            f"font-size: {theme.FS_2XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
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

        # Filters
        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by address, submitter or description…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(theme.input_qss())
        self.search_input.returnPressed.connect(self.refresh)
        filters_row.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(
            ["All", "Open", "In Progress", "Resolved", "Closed"]
        )
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

        # ---- Table (owner only)
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

        # ---- Kanban board (everyone else)
        self.kanban = QWidget()
        self.kanban.setStyleSheet("background: transparent;")
        kanban_layout = QHBoxLayout(self.kanban)
        kanban_layout.setContentsMargins(0, 0, 0, 0)
        kanban_layout.setSpacing(14)
        kanban_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        for title, colour in COLUMNS:
            col = KanbanColumn(title, colour)
            kanban_layout.addWidget(col, stretch=1)
            self.column_widgets[title] = col

        layout.addWidget(self.kanban, stretch=1)

        # Actions (owner only)
        self.actions_row = QHBoxLayout()
        self.actions_row.setSpacing(10)
        self.actions_row.addStretch()

        self.btn_open = QPushButton("Open Selected")
        self.btn_open.setCursor(Qt.PointingHandCursor)
        self.btn_open.setFixedHeight(38)
        self.btn_open.setStyleSheet(theme.button_qss("primary"))
        self.btn_open.clicked.connect(self._on_open_selected)
        self.actions_row.addWidget(self.btn_open)

        layout.addLayout(self.actions_row)

    def _apply_role_ui(self):
        if self.role == "Administrator":
            self.header_title.setText("🔧 All Maintenance Requests")
            self.readonly_badge.setVisible(False)
            self.btn_add.setVisible(True)
        elif self.role == "Property Manager":
            self.header_title.setText("🔧 Maintenance Requests")
            self.readonly_badge.setVisible(False)
            self.btn_add.setVisible(True)
        elif self.role == "Owner":
            self.header_title.setText("🔧 Maintenance on My Properties")
            self.readonly_badge.setVisible(True)
            self.btn_add.setVisible(True)
        elif self.role == "Tenant":
            self.header_title.setText("🔧 My Requests")
            self.readonly_badge.setVisible(False)
            self.btn_add.setVisible(True)
        else:
            self.header_title.setText("🔧 Maintenance")
            self.readonly_badge.setVisible(False)

        self.table.setVisible(self.is_owner)
        self.kanban.setVisible(not self.is_owner)
        self.btn_open.setVisible(self.is_owner)

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

    def _populate_kanban(self, rows):
        # Clear all columns
        for col in self.column_widgets.values():
            col.clear()

        counts = {name: 0 for name, _ in COLUMNS}

        for r in rows:
            status = r.get("status", "")
            if status not in self.column_widgets:
                continue
            card = MaintenanceKanbanCard(r, on_click=self._on_card_click)
            self.column_widgets[status].add_card(card)
            counts[status] += 1

        for name, col in self.column_widgets.items():
            col.set_count(counts[name])

    # ------------------------------------------------------------------ helpers
    def _selected_request_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def _go_dashboard(self):
        self.parent_window._set_screen("dashboard")

    # ------------------------------------------------------------------ handlers
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
        self._open_request(rid)

    def _on_row_double_click(self, index):
        self._on_open_selected()

    def _on_card_click(self, request: dict):
        self._open_request(request.get("request_id"))

    def _open_request(self, rid):
        if not rid:
            return
        data = self.controller.get(rid)
        if not data:
            QMessageBox.warning(self, "Error", "Request not found.")
            return
        dlg = MaintenanceDetailDialog(self, request_data=data,
                                      session_user=self.user_data)
        if dlg.exec():
            new_status = getattr(dlg, "new_status", None)
            if new_status:
                ok, msg = self.controller.update_status(rid, new_status,
                                                        self.user_data)
                if ok:
                    QMessageBox.information(self, "Success", msg)
                    self.refresh()
                    self.parent_window.properties_screen.refresh()
                else:
                    QMessageBox.warning(self, "Error", msg)
