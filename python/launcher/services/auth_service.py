# launcher/services/auth_service.py

from datetime import datetime, timedelta
import requests

from launcher import config
from launcher.domain.auth_tokens import AuthTokens
from launcher.domain.user import User


class AuthService:
    def __init__(self):
        self._tokens: AuthTokens | None = None
        self._current_user: User | None = None

    @property
    def tokens(self) -> AuthTokens | None:
        return self._tokens

    @property
    def current_user(self) -> User | None:
        return self._current_user

    def login(self, email: str, password: str) -> User:
        """
        1) Ask Keycloak for access_token via password grant.
        2) Call FastAPI /me with that token to get user details.
        """
        # --- 1. Keycloak token ---
        token_url = (
            f"{config.KC_BASE}/realms/{config.KC_REALM}/protocol/openid-connect/token"
        )

        payload = {
            "grant_type": "password",
            "client_id": config.KC_CLIENT_ID,
            "username": email,
            "password": password,
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        token_resp = requests.post(token_url, data=payload, headers=headers, timeout=10)
        token_resp.raise_for_status()
        token_data = token_resp.json()

        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")
        expires_in = token_data.get("expires_in", 3600)

        self._tokens = AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in - 60),
        )

        # --- 2. FastAPI /me (your router) ---
        me_url = f"{config.FASTAPI_BASE_URL}{config.FASTAPI_AUTH_PREFIX}/auth/me"

        me_resp = requests.get(
            me_url,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        me_resp.raise_for_status()
        me = me_resp.json()
        # me returns:
        # {
        #   "kc_user_id": ...,
        #   "username": ...,
        #   "realm_roles": [...],
        #   "client_roles": [...],
        #   "groups": [...]
        # }

        self._current_user = User(
            id=me["kc_user_id"],
            email=email,  # Keycloak userinfo has email; here /me doesn’t, so we use login email
            display_name=me.get("username"),
        )

        return self._current_user

    def auth_headers(self) -> dict:
        if not self._tokens:
            return {}
        return {"Authorization": f"Bearer {self._tokens.access_token}"}
