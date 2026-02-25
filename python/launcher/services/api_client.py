from __future__ import annotations
import requests

class ApiClient:
    def __init__(self, ctx):
        self._ctx = ctx

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = f"{config.FASTAPI_BASE_URL}{config.FASTAPI_AUTH_PREFIX}{path}"

        try:
            token = self._ctx.auth_service.get_access_token()
        except Exception as e:
            # already expired
            self._ctx.auth_service.logout()
            self._ctx.session_expired.emit(str(e))
            raise

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {token}"
        resp = requests.request(method, url, headers=headers, timeout=50, **kwargs)

        # If token invalid, try one refresh and retry once
        if resp.status_code == 401:
            try:
                # force refresh by expiring locally (optional) or just call get_access_token() again
                token = self._ctx.auth_service.get_access_token()
                headers["Authorization"] = f"Bearer {token}"
                resp = requests.request(method, url, headers=headers, timeout=10, **kwargs)
            except Exception as e:
                self._ctx.auth_service.logout()
                self._ctx.session_expired.emit("Session expired. Please log in again.")
                raise

        # If still 401, consider it expired
        if resp.status_code == 401:
            self._ctx.auth_service.logout()
            self._ctx.session_expired.emit("Session expired. Please log in again.")

        resp.raise_for_status()
        return resp
