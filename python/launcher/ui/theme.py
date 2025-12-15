from pathlib import Path

def apply_global_theme(app):
    """
    Load and apply the global QSS theme to the QApplication.
    """
    # this file: launcher/ui/theme.py
    theme_file = Path(__file__).resolve().parents[1] / "ui" / "resources" / "qss" / "theme.qss"
    try:
        with open(theme_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("⚠️ theme.qss not found at", theme_file)
