
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from Controllers.user_controller import UserController
from ui.user_form_dialog import UserFormDialog
from ui import theme


class UsersScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.controller = UserController()
        self.user_data = None
        self._build()

    def set_user(self, user_data: dict):
        self.user_data = user_data
        self.refresh()

    def refresh(self):
        filters = {
            "query": self.search_input.text().strip(),
            "role": self.role_filter.currentText(),
            "status": self.status_filter.currentText(),
        }
        rows = self.controller.list(filters)
        self._populate_table(rows)
        self.count_label.setText(f"{len(rows)} user record(s)")
        self._update_approval_visibility()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 26, 30, 26)
        layout.setSpacing(18)

        header = QHBoxLayout()
        header.setSpacing(12)

        title = QLabel("👥 Users")
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

        self.btn_add = QPushButton("+ Add User")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setFixedHeight(36)
        self.btn_add.setStyleSheet(theme.button_qss("primary"))
        self.btn_add.clicked.connect(self._on_add)
        header.addWidget(self.btn_add)

        layout.addLayout(header)

        filters_row = QHBoxLayout()
        filters_row.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, email or ID…")
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet(theme.input_qss())
        self.search_input.returnPressed.connect(self.refresh)
        filters_row.addWidget(self.search_input, stretch=1)

        self.role_filter = QComboBox()
        self.role_filter.addItems(
            ["All", "Administrator", "Property Manager", "Owner", "Tenant"]
        )
        self.role_filter.setFixedHeight(38)
        self.role_filter.setStyleSheet(theme.input_qss())
        self.role_filter.currentTextChanged.connect(self.refresh)
        filters_row.addWidget(self.role_filter)

        self.status_filter = QComboBox()
        self.status_filter.addItems(
            ["All", "Active", "Inactive", "Pending Approval"]
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

        self.count_label = QLabel("0 user record(s)")
        self.count_label.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(self.count_label)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Name", "ID Number", "Email", "Phone", "Role", "Status"]
        )
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.doubleClicked.connect(self._on_row_double_click)
        self.table.itemSelectionChanged.connect(self._update_approval_visibility)
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
        hv.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(1, QHeaderView.Stretch)
        hv.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(3, QHeaderView.Stretch)
        hv.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        hv.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        layout.addWidget(self.table, stretch=1)

        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addStretch()

        self.btn_edit = QPushButton("Edit Selected")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.setFixedHeight(38)
        self.btn_edit.setStyleSheet(theme.button_qss("primary"))
        self.btn_edit.clicked.connect(self._on_edit_selected)
        actions.addWidget(self.btn_edit)

        # Approve button — only for pending users
        self.btn_approve = QPushButton("✓ Approve")
        self.btn_approve.setCursor(Qt.PointingHandCursor)
        self.btn_approve.setFixedHeight(38)
        self.btn_approve.setStyleSheet(theme.button_qss("success"))
        self.btn_approve.clicked.connect(self._on_approve_selected)
        actions.addWidget(self.btn_approve)

        self.btn_toggle = QPushButton("Toggle Active")
        self.btn_toggle.setCursor(Qt.PointingHandCursor)
        self.btn_toggle.setFixedHeight(38)
        self.btn_toggle.setStyleSheet(theme.button_qss("warning"))
        self.btn_toggle.clicked.connect(self._on_toggle_active)
        actions.addWidget(self.btn_toggle)

        self.btn_delete = QPushButton("Delete Selected")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setFixedHeight(38)
        self.btn_delete.setStyleSheet(theme.button_qss("danger"))
        self.btn_delete.clicked.connect(self._on_delete_selected)
        actions.addWidget(self.btn_delete)

        layout.addLayout(actions)

    def _populate_table(self, rows):
        self.table.setRowCount(0)
        pending_bg = QBrush(QColor(theme.WARNING_SOFT))
        pending_fg = QBrush(QColor(theme.WARNING_HOVER))
        inactive_bg = QBrush(QColor(theme.BG_SUBTLE))
        inactive_fg = QBrush(QColor(theme.TEXT_FAINT))

        for r, u in enumerate(rows):
            self.table.insertRow(r)
            self.table.setRowHeight(r, 42)
            cells = [
                str(u["user_id"]),
                u["name"] or "",
                u["id_number"] or "",
                u["email"] or "",
                u["phone"] or "",
                u["role"] or "",
                u["status"] or "",
            ]
            status = u["status"]
            for c, text in enumerate(cells):
                item = QTableWidgetItem(text)
                if status == "Pending Approval":
                    item.setBackground(pending_bg)
                    item.setForeground(pending_fg)
                elif status == "Inactive":
                    item.setBackground(inactive_bg)
                    item.setForeground(inactive_fg)
                self.table.setItem(r, c, item)

    def _selected_user_id(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return int(item.text()) if item else None

    def _selected_status(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 6)
        return item.text() if item else None

    def _update_approval_visibility(self):
        show = self._selected_status() == "Pending Approval"
        self.btn_approve.setVisible(show)

    def _go_dashboard(self):
        self.parent_window._set_screen("dashboard")

    def _on_add(self):
        dlg = UserFormDialog(self, user_data=None)
        if dlg.exec():
            ok, msg = self.controller.create(dlg.get_data(), self.user_data)
            if ok:
                QMessageBox.information(self, "Success", msg)
                self.refresh()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_edit_selected(self):
        uid = self._selected_user_id()
        if uid is None:
            QMessageBox.information(self, "No selection", "Select a user to edit.")
            return
        data = self.controller.get(uid)
        if not data:
            QMessageBox.warning(self, "Error", "User not found.")
            return
        dlg = UserFormDialog(self, user_data=data)
        if dlg.exec():
            form_data = dlg.get_data()
            ok, msg = self.controller.update(uid, form_data, self.user_data)
            if not ok:
                QMessageBox.warning(self, "Error", msg)
                return
            if form_data.get("password"):
                from Services.security import hash_password
                from Repositories.user_repository import UserRepository
                UserRepository().update_password(uid, hash_password(form_data["password"]))
                msg += " Password updated."
            QMessageBox.information(self, "Success", msg)
            self.refresh()

    def _on_approve_selected(self):
        uid = self._selected_user_id()
        if uid is None:
            return
        ok, msg = self.controller.reactivate(uid, self.user_data)
        if ok:
            QMessageBox.information(
                self, "Approved",
                "User activated. They can now log in."
            )
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_toggle_active(self):
        uid = self._selected_user_id()
        if uid is None:
            QMessageBox.information(self, "No selection", "Select a user first.")
            return
        data = self.controller.get(uid)
        if not data:
            return
        if data["status"] == "Active":
            ok, msg = self.controller.deactivate(uid, self.user_data)
        else:
            ok, msg = self.controller.reactivate(uid, self.user_data)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_delete_selected(self):
        uid = self._selected_user_id()
        if uid is None:
            QMessageBox.information(self, "No selection", "Select a user to delete.")
            return
        confirm = QMessageBox.question(
            self, "Delete user",
            f"Permanently delete user #{uid}? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.delete(uid, self.user_data)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self.refresh()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_row_double_click(self, index):
        self._on_edit_selected()
