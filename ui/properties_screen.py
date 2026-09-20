print(">>> properties_screen.py V2 <<<")

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QFrame, QAbstractItemView
)
from PySide6.QtCore import Qt
from Controllers.property_controller import PropertyController
from ui.property_form_dialog import PropertyFormDialog
from ui import theme


class PropertiesScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = PropertyController()
        self.user_data = None
        self._build()

    # ------------------------------------------------------------------ API
    def set_user(self, user_data: dict):
        self.user_data = user_data
        self.refresh()

    def refresh(self):
        filters = {
            "query": self.search_input.text().strip(),
            "status": self.status_filter.currentText(),
        }
        rows = self.controller.list(filters)
        self._populate_table(rows)
        self.count_label.setText(f"{len(rows)} property record(s)")

    # ------------------------------------------------------------------ UI
    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(18)

        # ============================================================
        # HEADER
        # ============================================================
        header = QHBoxLayout()
        header.setSpacing(12)

        title = QLabel("🏠 Properties")
        title.setStyleSheet(
            f"font-size: {theme.FS_2XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        header.addWidget(title)
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
        # FILTERS
        # ============================================================
        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by address or type…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(theme.input_qss())
        self.search_input.returnPressed.connect(self.refresh)
        filters_row.addWidget(self.search_input, stretch=1)

        self.status_filter = QComboBox()
        self.status_filter.addItems(
            ["All", "Available", "Occupied", "Under Maintenance", "Archived"]
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

        # ============================================================
        # COUNT
        # ============================================================
        self.count_label = QLabel("0 property record(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        # ============================================================
        # TABLE
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
            QTableWidget::item {{
                padding: 10px;
                border: none;
            }}
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
        # ACTIONS
        # ============================================================
        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch()

        self.btn_edit = QPushButton("Edit Selected")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.setFixedHeight(38)
        self.btn_edit.setStyleSheet(theme.button_qss("primary"))
        self.btn_edit.clicked.connect(self._on_edit_selected)
        actions.addWidget(self.btn_edit)

        self.btn_archive = QPushButton("Archive Selected")
        self.btn_archive.setCursor(Qt.PointingHandCursor)
        self.btn_archive.setFixedHeight(38)
        self.btn_archive.setStyleSheet(theme.button_qss("danger"))
        self.btn_archive.clicked.connect(self._on_archive_selected)
        actions.addWidget(self.btn_archive)

        layout.addLayout(actions)

    # ------------------------------------------------------------------ helpers
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
                self.refresh()
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
                self.refresh()
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
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_row_double_click(self, index):
        self._on_edit_selected()