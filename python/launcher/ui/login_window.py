from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QSpacerItem,
    QSizePolicy,
)

from launcher.util.helper import icon_path

if TYPE_CHECKING:
    from launcher.ui.app_context import AppContext
    from launcher.domain.user import User


class LoginWorker(QThread):
    success = pyqtSignal(object)  # User
    error = pyqtSignal(str)

    def __init__(self, app_context: AppContext, email: str, password: str, parent=None):
        super().__init__(parent)
        self._ctx = app_context
        self._email = email
        self._password = password

    def run(self):
        try:
            user = self._ctx.auth_service.login(self._email, self._password)
            self.success.emit(user)
        except Exception as exc:
            self.error.emit(str(exc))


class LoginWindow(QWidget):
    def __init__(self, app_context: AppContext, on_login_success, parent=None):
        super().__init__(parent)
        self._ctx = app_context
        self._on_login_success = on_login_success
        self._worker: LoginWorker | None = None

        self.setObjectName("LoginWindow")
        self.setWindowTitle("Mihira Theatre – Login")
        self.resize(1365, 768)

        self._build_ui()

    def _build_ui(self):
        main = QVBoxLayout(self)
        main.setContentsMargins(32, 24, 32, 24)
        main.setSpacing(0)

        # top spacer
        main.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum,
                                       QSizePolicy.Policy.Expanding))

        # center content
        center = QVBoxLayout()
        center.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        center.setSpacing(40)

        # logo
        logo_label = QLabel(self)
        logo_label.setObjectName("LogoLabel")
        logo_label.setFixedSize(260, 180)

        logo_pix = QPixmap(icon_path("mihira_logo.png"))
        if not logo_pix.isNull():
            logo_label.setPixmap(
                logo_pix.scaled(
                    logo_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

        center.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # form container
        form_wrapper = QWidget(self)
        form_wrapper.setObjectName("FormWrapper")
        form_layout = QVBoxLayout(form_wrapper)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        self.username_input = QLineEdit(form_wrapper)
        self.username_input.setObjectName("LoginLineEdit")
        self.username_input.setPlaceholderText("USERNAME")

        self.password_input = QLineEdit(form_wrapper)
        self.password_input.setObjectName("LoginLineEdit")
        self.password_input.setPlaceholderText("PASSWORD")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.password_input)

        center.addWidget(form_wrapper)

        # connect button
        self.connect_button = QPushButton("Connect", self)
        self.connect_button.setObjectName("ConnectButton")
        self.connect_button.setFixedSize(220, 52)
        self.connect_button.clicked.connect(self._on_connect_clicked)

        center.addWidget(self.connect_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        # status label (for inline errors/info)
        self.status_label = QLabel("", self)
        self.status_label.setObjectName("StatusLabel")
        center.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        main.addLayout(center)

        # bottom bar: version text bottom-right
        bottom_bar = QHBoxLayout()
        bottom_bar.setContentsMargins(0, 0, 0, 0)

        bottom_bar.addStretch(1)
        version_label = QLabel("THEATRE V 0.1", self)
        version_label.setObjectName("VersionLabel")
        bottom_bar.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignRight)

        main.addSpacerItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum,
                                       QSizePolicy.Policy.Expanding))
        main.addLayout(bottom_bar)

    # ---------------- Logic ----------------

    def _set_ui_enabled(self, enabled: bool):
        self.username_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)
        self.connect_button.setEnabled(enabled)

    def _on_connect_clicked(self):
        email = self.username_input.text().strip()
        password = self.password_input.text()

        if not email or not password:
            QMessageBox.warning(self, "Missing info", "Username and password are required.")
            return

        self._set_ui_enabled(False)
        self.status_label.setText("Connecting...")

        self._worker = LoginWorker(self._ctx, email, password, self)
        self._worker.success.connect(self._handle_login_success)
        self._worker.error.connect(self._handle_login_error)
        self._worker.finished.connect(self._cleanup_worker)
        self._worker.start()

    def _handle_login_success(self, user: User):
        self.status_label.setText("")
        # callback: open main window + close this one (handled in main.py)
        self._on_login_success(user, self)

    def _handle_login_error(self, message: str):
        self._set_ui_enabled(True)
        self.status_label.setText("")
        QMessageBox.critical(self, "Login failed", message)

    def _cleanup_worker(self):
        self._worker = None
