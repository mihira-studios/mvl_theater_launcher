
from pathlib import Path


def icon_path(name: str) -> str:
    """
    Resolve an icon path relative to the launcher package.

    Expects icons in: launcher/resources/icons/<name>
    """
    # __file__ = .../launcher/utils/helper.py
    helper_file = Path(__file__).resolve()
    launcher_root = helper_file.parents[1]  # .../launcher

    icon_file = launcher_root / "ui" / "resources" / "icons" / name
    return str(icon_file)