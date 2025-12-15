# main.py

import sys
from PyQt6.QtWidgets import QApplication

from launcher.ui.app_context import AppContext
from launcher.ui.login_window import LoginWindow
from launcher.ui.main_window import MainWindow
from launcher.ui.theme import apply_global_theme

def main():
    app = QApplication(sys.argv)
    apply_global_theme(app)

    ctx = AppContext()

    main_window_holder = {"window": None}  # small trick to keep a ref

    def open_main_window(user, login_win):
        # Create & show MainWindow, close LoginWindow from inside
        win = MainWindow(ctx, user)
        win.show()
        main_window_holder["window"] = win  # keep reference to avoid GC

        login_win.close()

    login = LoginWindow(ctx, on_login_success=open_main_window)
    login.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
