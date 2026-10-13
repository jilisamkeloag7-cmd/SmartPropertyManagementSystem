
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import Qt
from Controllers.ownership_controller import OwnershipController
from ui.ownership_form_dialog import OwnershipFormDialog
from ui import theme


class OwnershipsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = OwnershipController()
        self.user_data = None
        self.is_writer = False
        self._build()

    def set_user(self, user_data: dict):
        self.user_data = user_data
        role = (user_data or {}).get("role", "")
        self.is_writer = role in ("Administrator", "Property Manager")
        self._apply_role_ui()
        self.refresh()

    def refresh(self):
        filters = {
            "query": self.search_input.text().strip(),
            "status": self.status_filter.currentText(),
        }
        rows = self.controller.list(filters, self.user_data)
        self._populate_table(rows)
        self.count_label.setText(f"{len(rows)} ownership record(s)")

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(12)

        self.header_title = QLabel("🔑 Ownership")
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

        self.btn_add = QPushButton("+ Add Ownership")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setFixedHeight(36)
        self.btn_add.setStyleSheet(theme.button_qss("primary"))
        self.btn_add.clicked.connect(self._on_add)
        header.addWidget(self.btn_add)

        layout.addLayout(header)

        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by property address or owner…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(theme.input_qss())
        self.search_input.returnPressed.connect(self.refresh)
        filters_row.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", "Active", "Ended"])
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

        self.count_label = QLabel("0 ownership record(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Property", "Owner", "Email", "Share", "Start", "End", "Status"]
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

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch()

        self.btn_end = QPushButton("End Selected Ownership")
        self.btn_end.setCursor(Qt.PointingHandCursor)
        self.btn_end.setFixedHeight(38)
        self.btn_end.setStyleSheet(theme.button_qss("danger"))
        self.btn_end.clicked.connect(self._on_end_selected)
        actions.addWidget(self.btn_end)

        layout.addLayout(actions)

    def _apply_role_ui(self):
        role = (self.user_data or {}).get("role", "")
        if role == "Administrator":
            self.header_title.setText("🔑 All Ownership Records")
            self.readonly_badge.setVisible(False)
        elif role == "Property Manager":
            self.header_title.setText("🔑 Ownership Records")
            self.readonly_badge.setVisible(False)
        elif role == "Owner":
            self.header_title.setText("🔑 My Properties")
            self.readonly_badge.setVisible(True)
        else:
            self.header_title.setText("🔑 Ownership")
            self.readonly_badge.setVisible(False)

        self.btn_add.setVisible(self.is_writer)
        self.btn_end.setVisible(self.is_writer)

    def _populate_table(self, rows):
        self.table.setRowCount(0)
        ended_bg = QBrush(QColor(theme.BG_SUBTLE))
        ended_fg = QBrush(QColor(theme.TEXT_FAINT))

        for r, o in enumerate(rows):
            self.table.insertRow(r)
            self.table.setRowHeight(r, 42)
            share_str = f"{o['ownership_share'] * 100:.0f}%" if o["ownership_share"] is not None else ""
            cells = [
                str(o["ownership_id"]),
                o["property_address"] or "",
                o["owner_name"] or "",
                o["owner_email"] or "",
                share_str,
                str(o["start_date"]) if o["start_date"] else "",
                str(o["end_date"]) if o["end_date"] else "—",
                "Active" if o["is_active"] else "Ended",
            ]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if not o["is_active"]:
                    item.setBackground(ended_bg)
                    item.setForeground(ended_fg)
                self.table.setItem(r, c, item)

    def _selected_ownership_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def _go_dashboard(self):
        self.parent_window._set_screen("dashboard")

    def _on_add(self):
        if not self.is_writer:
            return
        dlg = OwnershipFormDialog(self)
        if dlg.exec():
            ok, msg = self.controller.add(dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_end_selected(self):
        if not self.is_writer:
            return
        oid = self._selected_ownership_id()
        if oid is None:
            QMessageBox.information(self, "No selection", "Select an ownership record first.")
            return
        confirm = QMessageBox.question(
            self, "End ownership",
            f"End ownership #{oid} today? The record will be preserved as history.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.end(oid, self.user_data)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)
