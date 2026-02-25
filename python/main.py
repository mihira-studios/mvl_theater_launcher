# main.py
import sys
from PyQt6.QtWidgets import QApplication

from launcher.ui.app_context import AppContext
from launcher.ui.login_window import LoginWindow
from launcher.ui.main_window import MainWindow
from launcher.ui.script_breakdown_page import ScriptBreakdownPage
from launcher.ui.theme import apply_global_theme


def main():
    app = QApplication(sys.argv)
    apply_global_theme(app)

    ctx = AppContext()

    holder = {"login": None, "main": None}

    def show_login(message: str = ""):
        # hide main if present
        if holder["main"] is not None:
            holder["main"].hide()
            holder["main"] = None

        # recreate login if closed
        if holder["login"] is None:
            holder["login"] = LoginWindow(ctx, on_login_success=open_main_window)

        if message:
            holder["login"].status_label.setText(message)  # optional
        holder["login"].show()
        holder["login"].raise_()
        holder["login"].activateWindow()

    def on_logout(reason: str, main_window: MainWindow):
        ctx.auth_service.logout()
        # don't close the app window chain; just return to login
        show_login(reason or "Logged out.")

    def open_main_window(user, login_win: LoginWindow):
        # Hide (don't close) login so we can show it again on logout
        login_win.hide()

        win = MainWindow(ctx, user, on_logout=on_logout)  # <-- pass callback
        win.show()
        holder["main"] = win
        holder["login"] = login_win  # keep ref

    holder["login"] = LoginWindow(ctx, on_login_success=open_main_window)
    holder["login"].show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
