
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame, QScrollArea, QWidget, QMessageBox,
    QFileDialog, QDialogButtonBox
)
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QFrame, QScrollArea, QWidget, QMessageBox,
    QFileDialog, QDialogButtonBox, QInputDialog
)
from PySide6.QtCore import Qt
from Controllers.profile_controller import ProfileController
from ui.widgets.avatar import make_avatar_pixmap
from ui import theme


SECURITY_QUESTIONS = [
    "What city were you born in?",
    "What is your mother's maiden name?",
    "What was the name of your first pet?",
    "What was the model of your first car?",
    "What was the name of your first school?",
]


class ProfileDialog(QDialog):
    def __init__(self, parent=None, user_id: int | None = None,
                 session_user: dict | None = None,
                 on_profile_updated=None):
        super().__init__(parent)
        self.controller = ProfileController()
        self.user_id = user_id
        self.session_user = session_user or {}
        self.on_profile_updated = on_profile_updated
        self.profile = None
        self.pending_requests = []
        self.setWindowTitle("My Profile")
        self.setFixedSize(720, 780)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; }}
        """)
        self._load()
        self._build()

    # ------------------------------------------------------------------ load
    def _load(self):
        self.profile = self.controller.get(self.user_id)
        self.pending_requests = self.controller.list_my_requests(self.user_id)
        # Map field -> pending request
        self.pending_map = {
            r["field_name"]: r
            for r in self.pending_requests
            if r["status"] == "Pending"
        }

    # ------------------------------------------------------------------ UI
    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(f"QScrollArea {{ background: {theme.BG_APP}; }}")

        content = QWidget()
        content.setStyleSheet(f"background: {theme.BG_APP};")
        scroll.setWidget(content)

        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 22, 24, 22)
        layout.setSpacing(16)

        # ---- Header with avatar
        header = QHBoxLayout()
        header.setSpacing(20)

        self.avatar = QLabel()
        self.avatar.setFixedSize(96, 96)
        self.avatar.setPixmap(make_avatar_pixmap(
            self.profile.get("profile_image_path"),
            self.profile.get("name", ""),
            96,
        ))
        header.addWidget(self.avatar)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        name_lbl = QLabel(self.profile.get("name", ""))
        name_lbl.setStyleSheet(
            f"font-size: {theme.FS_2XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        info_col.addWidget(name_lbl)

        email_lbl = QLabel(self.profile.get("email", ""))
        email_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_BASE}px;"
        )
        info_col.addWidget(email_lbl)

        role_lbl = QLabel(self.profile.get("role", ""))
        role_lbl.setStyleSheet(f"""
            background: {theme.PRIMARY_SOFT};
            color: {theme.PRIMARY};
            padding: 3px 10px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_XS}px;
            font-weight: bold;
        """)
        role_lbl.setFixedWidth(120)
        info_col.addWidget(role_lbl)

        info_col.addStretch()
        header.addLayout(info_col)
        header.addStretch()

        # Image action buttons
        img_col = QVBoxLayout()
        img_col.setSpacing(6)
        btn_upload = QPushButton("Change Photo")
        btn_upload.setCursor(Qt.PointingHandCursor)
        btn_upload.setFixedHeight(32)
        btn_upload.setStyleSheet(theme.button_qss("secondary"))
        btn_upload.clicked.connect(self._on_upload_image)
        img_col.addWidget(btn_upload)

        btn_remove = QPushButton("Remove Photo")
        btn_remove.setCursor(Qt.PointingHandCursor)
        btn_remove.setFixedHeight(32)
        btn_remove.setStyleSheet(theme.button_qss("ghost"))
        btn_remove.clicked.connect(self._on_remove_image)
        img_col.addWidget(btn_remove)
        img_col.addStretch()

        header.addLayout(img_col)

        layout.addLayout(header)

        # ---- Section divider
        layout.addWidget(self._hairline())
        layout.addWidget(self._section_title("Contact Information"))

        # ---- Phone (direct edit)
        phone_row = self._field_row(
            "Phone",
            self.profile.get("phone") or "—",
            editable_direct=True,
            button_text="Edit",
            on_click=self._on_edit_phone,
        )
        layout.addWidget(phone_row)

        # ---- Name (approval)
        name_row = self._field_row(
            "Full Name",
            self.profile.get("name", ""),
            is_pending="name" in self.pending_map,
            button_text="Request Change",
            on_click=lambda: self._on_request_change("name"),
        )
        layout.addWidget(name_row)

        # ---- Email (approval)
        email_row = self._field_row(
            "Email",
            self.profile.get("email", ""),
            is_pending="email" in self.pending_map,
            button_text="Request Change",
            on_click=lambda: self._on_request_change("email"),
        )
        layout.addWidget(email_row)

        # ---- ID (read-only)
        id_row = self._field_row(
            "ID Number",
            self.profile.get("id_number", ""),
            is_locked=True,
        )
        layout.addWidget(id_row)

        # ---- Section divider
        layout.addWidget(self._hairline())
        layout.addWidget(self._section_title("Account Security"))

        # ---- Password
        pwd_row = self._field_row(
            "Password",
            "••••••••",
            button_text="Change",
            on_click=self._on_change_password,
        )
        layout.addWidget(pwd_row)

        # ---- Security question
        sec_row = self._field_row(
            "Security Question",
            self.profile.get("security_question") or "(not set)",
            button_text="Edit",
            on_click=self._on_edit_security_question,
        )
        layout.addWidget(sec_row)

        # ---- Section divider
        layout.addWidget(self._hairline())
        layout.addWidget(self._section_title("Pending Change Requests"))

        # List of this user's change requests
        self._render_change_requests(layout)

        layout.addStretch()

        # ---- Footer
        footer = QHBoxLayout()
        footer.addStretch()
        btn_close = QPushButton("Close")
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.setFixedHeight(40)
        btn_close.setStyleSheet(theme.button_qss("secondary"))
        btn_close.clicked.connect(self.accept)
        footer.addWidget(btn_close)
        layout.addLayout(footer)

        outer.addWidget(scroll)

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _hairline():
        line = QFrame()
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {theme.BORDER};")
        return line

    @staticmethod
    def _section_title(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"font-size: {theme.FS_LG}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN}; padding-top: 6px;"
        )
        return lbl

    def _field_row(self, label, value, editable_direct=False,
                    is_pending=False, is_locked=False,
                    button_text=None, on_click=None):
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-radius: {theme.RADIUS_MD}px;
            }}
        """)

        h = QHBoxLayout(row)
        h.setContentsMargins(18, 14, 18, 14)
        h.setSpacing(12)

        # Label + value column
        col = QVBoxLayout()
        col.setSpacing(2)

        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px; "
            f"font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;"
        )
        col.addWidget(lbl)

        val = QLabel(str(value))
        val.setStyleSheet(
            f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_MD}px; "
            f"font-weight: bold;"
        )
        val.setWordWrap(True)
        col.addWidget(val)

        h.addLayout(col, stretch=1)

        # Status badge / button
        if is_locked:
            locked = QLabel("🔒 Locked")
            locked.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_XS}px;"
            )
            h.addWidget(locked)
        elif is_pending:
            pending = QLabel("⏳ Pending")
            pending.setStyleSheet(f"""
                background: {theme.WARNING_SOFT};
                color: {theme.WARNING_HOVER};
                padding: 4px 10px;
                border-radius: {theme.RADIUS_SM}px;
                font-size: {theme.FS_XS}px;
                font-weight: bold;
            """)
            h.addWidget(pending)
            cancel = QPushButton("Cancel")
            cancel.setCursor(Qt.PointingHandCursor)
            cancel.setFixedHeight(30)
            cancel.setStyleSheet(theme.button_qss("ghost"))
            cancel.clicked.connect(
                lambda checked=False, f=label: self._on_cancel_pending(f)
            )
            h.addWidget(cancel)
        elif button_text and on_click:
            btn = QPushButton(button_text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.setStyleSheet(theme.button_qss("primary"))
            btn.clicked.connect(on_click)
            h.addWidget(btn)

        return row

    def _render_change_requests(self, layout):
        requests = [r for r in self.pending_requests if r["status"] != "Cancelled"]
        if not requests:
            empty = QLabel("No change requests submitted.")
            empty.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_SM}px; "
                f"padding: 12px; font-style: italic;"
            )
            layout.addWidget(empty)
            return

        for r in requests:
            layout.addWidget(self._make_request_card(r))

    def _make_request_card(self, r):
        card = QFrame()
        status = r["status"]
        accent = {"Pending": "#f59e0b", "Approved": "#10b981",
                  "Rejected": "#ef4444"}.get(status, theme.BORDER)
        card.setStyleSheet(f"""
            QFrame {{
                background: {theme.BG_CARD};
                border: 1px solid {theme.BORDER};
                border-left: 3px solid {accent};
                border-radius: {theme.RADIUS_MD}px;
            }}
        """)
        inner = QVBoxLayout(card)
        inner.setContentsMargins(14, 10, 14, 10)
        inner.setSpacing(4)

        header = QHBoxLayout()
        title = QLabel(f"{r['field_name'].title()} change")
        title.setStyleSheet(
            f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; "
            f"font-weight: bold;"
        )
        header.addWidget(title)
        header.addStretch()

        kind = {"Pending": "warning", "Approved": "success",
                "Rejected": "danger"}.get(status, "muted")
        bg, fg = {
            "warning": (theme.WARNING_SOFT, theme.WARNING_HOVER),
            "success": (theme.SUCCESS_SOFT, theme.SUCCESS_HOVER),
            "danger":  (theme.DANGER_SOFT, theme.DANGER_HOVER),
            "muted":   (theme.BG_SUBTLE, theme.TEXT_MUTED),
        }[kind]
        badge = QLabel(status)
        badge.setStyleSheet(f"""
            background: {bg};
            color: {fg};
            padding: 3px 10px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_XS}px;
            font-weight: bold;
        """)
        header.addWidget(badge)
        inner.addLayout(header)

        body = QLabel(
            f"From: {r['old_value'] or '(empty)'}\n"
            f"To:   {r['new_value']}"
        )
        body.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        body.setWordWrap(True)
        inner.addWidget(body)

        if r.get("decision_note"):
            note = QLabel(f"Note: {r['decision_note']}")
            note.setWordWrap(True)
            note.setStyleSheet(
                f"color: {theme.TEXT_FAINT}; font-size: {theme.FS_XS}px; "
                f"font-style: italic;"
            )
            inner.addWidget(note)

        return card

    # ------------------------------------------------------------------ handlers
    def _on_upload_image(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select profile picture", "",
            "Images (*.png *.jpg *.jpeg *.gif *.webp)"
        )
        if not path:
            return
        ok, msg = self.controller.upload_image(self.user_id, path)
        if ok:
            QMessageBox.information(self, "Success", msg)
            self._refresh_all()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_remove_image(self):
        confirm = QMessageBox.question(
            self, "Remove picture",
            "Remove your profile picture?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.remove_image(self.user_id)
        if ok:
            self._refresh_all()

    def _on_edit_phone(self):
        current = self.profile.get("phone", "")
        text, ok = QInputDialog.getText(
            self, "Edit phone", "New phone number:", text=current
        )
        if not ok:
            return
        ok, msg = self.controller.update_phone(self.user_id, text)
        if ok:
            QMessageBox.information(self, "Saved", msg)
            self._refresh_all()
        else:
            QMessageBox.warning(self, "Error", msg)

    def _on_request_change(self, field_name):
        current = self.profile.get(field_name, "")
        dlg = RequestChangeDialog(self, field_name=field_name, current_value=current)
        if dlg.exec():
            data = dlg.get_data()
            ok, msg = self.controller.request_change(
                self.user_id, field_name, data["new_value"], data["reason"]
            )
            if ok:
                QMessageBox.information(self, "Submitted", msg)
                self._refresh_all()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_cancel_pending(self, label):
        # Find the request_id matching this field
        field_key = label.lower().replace(" ", "_")
        req = self.pending_map.get(field_key)
        if not req:
            return
        confirm = QMessageBox.question(
            self, "Cancel request",
            "Cancel this pending change request?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        ok, msg = self.controller.cancel_request(req["request_id"], self.session_user)
        if ok:
            self._refresh_all()

    def _on_change_password(self):
        dlg = ChangePasswordDialog(self)
        if dlg.exec():
            data = dlg.get_data()
            ok, msg = self.controller.change_password(
                self.user_id, data["old"], data["new"], data["confirm"]
            )
            if ok:
                QMessageBox.information(self, "Changed", msg)
            else:
                QMessageBox.warning(self, "Error", msg)

    def _on_edit_security_question(self):
        dlg = SecurityQuestionDialog(self,
                                     current_question=self.profile.get("security_question", ""))
        if dlg.exec():
            data = dlg.get_data()
            ok, msg = self.controller.update_security_qa(
                self.user_id, data["question"], data["answer"]
            )
            if ok:
                QMessageBox.information(self, "Saved", msg)
                self._refresh_all()
            else:
                QMessageBox.warning(self, "Error", msg)

    def _refresh_all(self):
        # Reload from DB
        self._load()

        # Rebuild UI
        # (simplest: rebuild the whole dialog content)
        old_geometry = self.geometry()
        QDialog.close(self)
        # We'll just close and reopen via the callback
        if self.on_profile_updated:
            self.on_profile_updated()


# =====================================================================
# Sub-dialogs
# =====================================================================

class RequestChangeDialog(QDialog):
    def __init__(self, parent=None, field_name="", current_value=""):
        super().__init__(parent)
        self.field_name = field_name
        self.current_value = current_value
        self.setWindowTitle(f"Request {field_name.title()} Change")
        self.setFixedSize(480, 380)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        title = QLabel(f"Request {self.field_name.title()} Change")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        info = QLabel(
            "Change requests for identity fields require approval by a "
            "manager or administrator."
        )
        info.setWordWrap(True)
        info.setStyleSheet(f"""
            color: {theme.INFO};
            background: {theme.INFO_SOFT};
            padding: 10px;
            border-radius: {theme.RADIUS_SM}px;
            font-size: {theme.FS_SM}px;
        """)
        layout.addWidget(info)

        layout.addSpacing(6)

        cur_lbl = QLabel("Current value")
        cur_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px; "
            f"font-weight: bold;"
        )
        layout.addWidget(cur_lbl)

        cur_val = QLabel(self.current_value or "(empty)")
        cur_val.setStyleSheet(
            f"color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; "
            f"background: {theme.BG_SUBTLE}; padding: 8px 12px; "
            f"border-radius: {theme.RADIUS_SM}px;"
        )
        layout.addWidget(cur_val)

        new_lbl = QLabel("New value *")
        new_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px; "
            f"font-weight: bold; padding-top: 6px;"
        )
        layout.addWidget(new_lbl)

        self.new_input = QLineEdit()
        self.new_input.setFixedHeight(42)
        self.new_input.setStyleSheet(theme.input_qss())
        layout.addWidget(self.new_input)

        reason_lbl = QLabel("Reason for change (optional)")
        reason_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px; "
            f"font-weight: bold; padding-top: 6px;"
        )
        layout.addWidget(reason_lbl)

        self.reason_input = QLineEdit()
        self.reason_input.setPlaceholderText("e.g. legal name change after marriage")
        self.reason_input.setFixedHeight(42)
        self.reason_input.setStyleSheet(theme.input_qss())
        layout.addWidget(self.reason_input)

        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText("Submit Request")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFixedHeight(42)
        ok_btn.setStyleSheet(theme.button_qss("primary"))

        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setText("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(42)
        cancel_btn.setStyleSheet(theme.button_qss("secondary"))

        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        if not self.new_input.text().strip():
            QMessageBox.warning(self, "Missing", "Please enter the new value.")
            return
        self.accept()

    def get_data(self):
        return {
            "new_value": self.new_input.text().strip(),
            "reason": self.reason_input.text().strip(),
        }


class ChangePasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Password")
        self.setFixedSize(460, 400)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        title = QLabel("Change Password")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.old = QLineEdit()
        self.old.setEchoMode(QLineEdit.Password)
        self.old.setFixedHeight(42)
        self.old.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Current Password *"), self.old)

        self.new = QLineEdit()
        self.new.setEchoMode(QLineEdit.Password)
        self.new.setFixedHeight(42)
        self.new.setStyleSheet(theme.input_qss())
        form.addRow(self._label("New Password *"), self.new)

        self.confirm = QLineEdit()
        self.confirm.setEchoMode(QLineEdit.Password)
        self.confirm.setFixedHeight(42)
        self.confirm.setStyleSheet(theme.input_qss())
        form.addRow(self._label("Confirm New *"), self.confirm)

        layout.addLayout(form)
        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText("Change Password")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFixedHeight(42)
        ok_btn.setStyleSheet(theme.button_qss("primary"))
        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(42)
        cancel_btn.setStyleSheet(theme.button_qss("secondary"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _label(text):
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px; font-weight: bold;"
        )
        return lbl

    def get_data(self):
        return {
            "old": self.old.text(),
            "new": self.new.text(),
            "confirm": self.confirm.text(),
        }


class SecurityQuestionDialog(QDialog):
    def __init__(self, parent=None, current_question=""):
        super().__init__(parent)
        self.current_question = current_question
        self.setWindowTitle("Security Question")
        self.setFixedSize(500, 380)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(12)

        title = QLabel("Security Question")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        info = QLabel(
            "Used for password recovery. Choose a question only you can answer."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(info)

        layout.addSpacing(6)

        q_lbl = QLabel("Question *")
        q_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px; font-weight: bold;"
        )
        layout.addWidget(q_lbl)

        self.question_combo = QComboBox()
        self.question_combo.addItems(SECURITY_QUESTIONS)
        if self.current_question in SECURITY_QUESTIONS:
            self.question_combo.setCurrentText(self.current_question)
        self.question_combo.setFixedHeight(42)
        self.question_combo.setStyleSheet(theme.input_qss())
        layout.addWidget(self.question_combo)

        a_lbl = QLabel("Answer *")
        a_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_XS}px; "
            f"font-weight: bold; padding-top: 6px;"
        )
        layout.addWidget(a_lbl)

        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Your answer (case-insensitive)")
        self.answer_input.setFixedHeight(42)
        self.answer_input.setStyleSheet(theme.input_qss())
        layout.addWidget(self.answer_input)

        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText("Save")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFixedHeight(42)
        ok_btn.setStyleSheet(theme.button_qss("primary"))
        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(42)
        cancel_btn.setStyleSheet(theme.button_qss("secondary"))
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return {
            "question": self.question_combo.currentText(),
            "answer": self.answer_input.text().strip(),
        }
