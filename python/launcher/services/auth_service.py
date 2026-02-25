from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import requests


from launcher import config
from launcher.domain.user import User
class AuthError(Exception):
    pass


class SessionExpired(AuthError):
    pass


@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str | None
    expires_at: datetime  # when access token should be considered expired


class AuthService:
    def __init__(self):
        self._tokens: AuthTokens | None = None
       
    def auth_headers(self) -> dict[str, str]:
        token = self.get_access_token()
        return {"Authorization": f"Bearer {token}"}

    def login(self, email: str, password: str) -> User:
        token_url = f"{config.KC_BASE}/realms/{config.KC_REALM}/protocol/openid-connect/token"

        payload = {
            "grant_type": "password",
            "client_id": config.KC_CLIENT_ID,
            "username": email,
            "password": password,
        }

        # If client is confidential
        if getattr(config, "KC_CLIENT_SECRET", None):
            payload["client_secret"] = config.KC_CLIENT_SECRET

        token_resp = requests.post(token_url, data=payload, timeout=10)
        self._raise_auth_error(token_resp)

        token_data = token_resp.json()
        access_token = token_data["access_token"]
        refresh_token = token_data.get("refresh_token")
        expires_in = int(token_data.get("expires_in", 3600))

        # refresh 60s early to avoid race conditions
        self._tokens = AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in - 60),
        )

        me = self._api_get("/auth/me").json()

        self._current_user = User(
            id=me["kc_user_id"],
            email=email,
            display_name=me.get("username"),
        )
        return self._current_user

    def get_access_token(self) -> str:
        if not self._tokens:
            raise SessionExpired("Not logged in.")

        if datetime.utcnow() < self._tokens.expires_at:
            return self._tokens.access_token

        # refresh
        if not self._tokens.refresh_token:
            self.logout()
            raise SessionExpired("Session expired. Please log in again.")

        url = f"{config.KC_BASE}/realms/{config.KC_REALM}/protocol/openid-connect/token"
        payload = {
            "grant_type": "refresh_token",
            "client_id": config.KC_CLIENT_ID,
            "refresh_token": self._tokens.refresh_token,
        }
        if getattr(config, "KC_CLIENT_SECRET", None):
            payload["client_secret"] = config.KC_CLIENT_SECRET

        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code != 200:
            self.logout()
            raise SessionExpired("Session expired. Please log in again.")

        data = resp.json()
        expires_in = int(data.get("expires_in", 3600))

        refresh_early = min(60, max(0, expires_in//10))  # refresh at least 30s before expiry, but no more than 60s early
        self._tokens = AuthTokens(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token", self._tokens.refresh_token),
            expires_at=datetime.utcnow() + timedelta(seconds=expires_in - refresh_early),
        )
        return self._tokens.access_token

    def _api_get(self, path: str) -> requests.Response:
        url = f"{config.FASTAPI_BASE_URL}{config.FASTAPI_AUTH_PREFIX}{path}"
        token = self.get_access_token()
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)

        if resp.status_code == 401 and self._tokens and self._tokens.refresh_token:
            self._tokens.expires_at = datetime.utcnow() - timedelta(seconds=1)
            token = self.get_access_token()
            resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=10)

        resp.raise_for_status()
        return resp

    def _raise_auth_error(self, resp: requests.Response) -> None:
        if resp.status_code < 400:
            return
        # Keycloak returns JSON like {"error":"invalid_grant","error_description":"..."}
        try:
            data = resp.json()
            msg = data.get("error_description") or data.get("error") or resp.text
        except Exception:
            msg = resp.text
        raise AuthError(msg)

    def logout(self) -> None:
        try:
            if self._tokens and self._tokens.refresh_token:
                url = f"{config.KC_BASE}/realms/{config.KC_REALM}/protocol/openid-connect/logout"
                payload = {
                    "client_id": config.KC_CLIENT_ID,
                    "refresh_token": self._tokens.refresh_token,
                }
                if getattr(config, "KC_CLIENT_SECRET", None):
                    payload["client_secret"] = config.KC_CLIENT_SECRET
                requests.post(url, data=payload, timeout=10)
        finally:
            self._tokens = None
    
    def access_token_minutes_left(self) -> float:
        if not self._tokens:
            return 0.0
        delta = self._tokens.expires_at - datetime.utcnow()
        return max(0.0, delta.total_seconds() / 60.0)