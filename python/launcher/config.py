# config.py
import os
import sys
import configparser
from pathlib import Path


def _get_config_path() -> Path:
    if getattr(sys, 'frozen', False):
        # First check next to the exe (testers can edit this)
        exe_dir = Path(sys.executable).parent
        config_next_to_exe = exe_dir / "config.ini"
        if config_next_to_exe.exists():
            return config_next_to_exe
        # Fallback to bundled copy inside exe
        return Path(sys._MEIPASS) / "config.ini"
    else:
        # Running as .py — config.ini is in python/ next to main.py
        # __file__ is python/launcher/config.py
        # parents[0] = python/launcher/
        # parents[1] = python/
        return Path(__file__).resolve().parents[1] / "config.ini"


# Load ini
_cfg = configparser.ConfigParser()
_cfg.read(_get_config_path())

AI_API_KEY = _cfg.get("AI", "openrouter_api_key", fallback="")

# MVL_DOMAIN: env var takes priority (set by .bat for devs)
# falls back to config.ini (used by exe for testers)
DOMAIN = os.getenv("MVL_DOMAIN") or _cfg.get("Network", "mvl_domain", fallback="localhost")

print(f"Domain: {DOMAIN}")

KC_BASE      = os.getenv("KC_BASE",     f"http://{DOMAIN}:8080")
KC_ISSUER    = os.getenv("KC_BASE",     f"http://{DOMAIN}:8080")
KC_REALM     = os.getenv("KC_REALM",    "MIHIRA-REALM")
KC_CLIENT_ID = os.getenv("KC_CLIENT_ID","mihira-cli")

FASTAPI_BASE_URL    = f"http://{DOMAIN}:4007/api/v1"
FASTAPI_AUTH_PREFIX = ""