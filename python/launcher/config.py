# config.py
import os

KC_BASE = os.getenv("KC_BASE", "http://10.100.1.30:8080")
KC_ISSUER = os.getenv("KC_BASE", "http://10.100.1.30:8080")

KC_REALM = "MIHIRA-REALM"
KC_CLIENT_ID = "mihira-cli"

FASTAPI_BASE_URL = "http://localhost:4007/api/v1"   # default uvicorn port
FASTAPI_AUTH_PREFIX = ""     

API_BASE_URL = "http://10.100.1.30:8080"  # backend
UNREAL_EDITOR_PATH = r"C:\\UnrealEngine\\Engine\\Binaries\\Win64\\UnrealEditor.exe"  # or game exe
APP_NAME = "Theater Launcher"
