# config.py
import os

DOMAIN = os.environ.get("MVL_DOMAIN") if os.environ.get("MVL_DOMAIN") else "http://localhost"

KC_BASE = os.getenv("KC_BASE", f"{DOMAIN}:8080")
KC_ISSUER = os.getenv("KC_BASE", f"{DOMAIN}:8080")

KC_REALM = os.getenv("KC_REALM","MIHIRA-REALM")
KC_CLIENT_ID = os.getenv("KC_CLIENT_ID","mihira-cli")

FASTAPI_BASE_URL = f"{DOMAIN}:4007/api/v1"   
FASTAPI_AUTH_PREFIX = ""     

