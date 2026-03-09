import sys
from pathlib import Path

def _resource_path(relative_path: str) -> Path:
    """Resolve resource paths for both .py and PyInstaller .exe"""
    if getattr(sys, 'frozen', False):
        # Running as exe — PyInstaller unpacks here
        base = Path(sys._MEIPASS)
    else:
        # Running as .py — go up from theme.py to python/ folder
        base = Path(__file__).resolve().parents[2]

    return base / relative_path

def apply_global_theme(app):
    """
    Load and apply the global QSS theme to the QApplication.
    """
    theme_file = _resource_path("launcher/ui/resources/qss/theme.qss")
    try:
        with open(theme_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("⚠️ theme.qss not found at", theme_file)