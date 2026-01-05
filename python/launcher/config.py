# config.py
import os

DOMAIN = os.getenv("MVL_DOMAIN") if os.getenv("MVL_DOMAIN") else "http://localhost"


print (f"Domain {DOMAIN}")
KC_BASE = os.getenv("KC_BASE", f"http://{DOMAIN}:8080")
KC_ISSUER = os.getenv("KC_BASE", f"http://{DOMAIN}:8080")

KC_REALM = os.getenv("KC_REALM","MIHIRA-REALM")
KC_CLIENT_ID = os.getenv("KC_CLIENT_ID","mihira-cli")

FASTAPI_BASE_URL = f"http://{DOMAIN}:4007/api/v1"   
FASTAPI_AUTH_PREFIX = ""     

