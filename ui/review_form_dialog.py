
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QDialogButtonBox,
    QLabel, QPushButton, QMessageBox, QButtonGroup
)
from PySide6.QtCore import Qt
from ui import theme


class ReviewFormDialog(QDialog):
    """Tenant writes a review for a property."""

    def __init__(self, parent=None, property_address: str = ""):
        super().__init__(parent)
        self.property_address = property_address
        self.selected_rating = 0
        self.setWindowTitle("Write Review")
        self.setFixedSize(520, 480)
        self.setStyleSheet(f"""
            QDialog {{ background: {theme.BG_APP}; }}
            QLabel {{ color: {theme.TEXT_MAIN}; font-size: {theme.FS_BASE}px; }}
        """)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        title = QLabel("Write a Review")
        title.setStyleSheet(
            f"font-size: {theme.FS_XL}px; font-weight: bold; "
            f"color: {theme.TEXT_MAIN};"
        )
        layout.addWidget(title)

        subtitle = QLabel(self.property_address)
        subtitle.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-size: {theme.FS_BASE}px;"
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        layout.addSpacing(6)

        # Rating
        rating_lbl = QLabel("Rating *")
        rating_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-weight: bold; "
            f"font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(rating_lbl)

        stars_row = QHBoxLayout()
        stars_row.setSpacing(6)
        self.star_buttons = []
        for i in range(1, 6):
            b = QPushButton("★")
            b.setCursor(Qt.PointingHandCursor)
            b.setFixedSize(52, 52)
            b.setStyleSheet(self._star_qss(False))
            b.clicked.connect(lambda checked=False, n=i: self._on_star_click(n))
            stars_row.addWidget(b)
            self.star_buttons.append(b)
        stars_row.addStretch()
        layout.addLayout(stars_row)

        # Comment
        comment_lbl = QLabel("Comment (optional)")
        comment_lbl.setStyleSheet(
            f"color: {theme.TEXT_MUTED}; font-weight: bold; "
            f"font-size: {theme.FS_SM}px;"
        )
        layout.addWidget(comment_lbl)

        self.comment = QTextEdit()
        self.comment.setFixedHeight(140)
        self.comment.setPlaceholderText(
            "Share your experience living at this property…"
        )
        self.comment.setStyleSheet(theme.input_qss())
        layout.addWidget(self.comment)

        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        ok_btn = buttons.button(QDialogButtonBox.Ok)
        ok_btn.setText("Submit Review")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFixedHeight(40)
        ok_btn.setStyleSheet(theme.button_qss("primary"))

        cancel_btn = buttons.button(QDialogButtonBox.Cancel)
        cancel_btn.setText("Cancel")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet(theme.button_qss("secondary"))

        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def _star_qss(filled: bool) -> str:
        color = theme.WARNING if filled else theme.BORDER
        return f"""
            QPushButton {{
                background: {theme.BG_CARD};
                color: {color};
                border: 2px solid {theme.BORDER};
                border-radius: {theme.RADIUS_MD}px;
                font-size: 26px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border-color: {theme.WARNING};
            }}
        """

    def _on_star_click(self, n: int):
        self.selected_rating = n
        for i, b in enumerate(self.star_buttons, start=1):
            b.setStyleSheet(self._star_qss(filled=(i <= n)))

    def _on_accept(self):
        if self.selected_rating < 1:
            QMessageBox.warning(self, "Rating required",
                                "Please click a star to choose a rating.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "rating": self.selected_rating,
            "comment": self.comment.toPlainText().strip(),
        }
