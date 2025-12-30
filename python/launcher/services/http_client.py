import requests

from launcher.services.auth_service import SessionExpired
from launcher import config

class HttpClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = (base_url or config.FASTAPI_BASE_URL).rstrip("/")

    def get(self, path: str, headers=None, timeout=10, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        return requests.get(url, headers=headers, timeout=timeout, **kwargs)

    def request(self, method: str, path: str, headers=None, timeout=10, **kwargs):
        url = f"{self.base_url}/{path.lstrip('/')}"
        return requests.request(method, url, headers=headers, timeout=timeout, **kwargs)

    def get_with_auth_retry(self, auth, path: str, **kwargs):
        # First try
        resp = self.get(path, headers=auth.auth_headers(), **kwargs)
        if resp.status_code != 401:
            return resp

        # Refresh + retry once
        try:
            auth.get_access_token()  # refresh if needed
        except SessionExpired:
            raise

        resp2 = self.get(path, headers=auth.auth_headers(), **kwargs)
        if resp2.status_code == 401:
            auth.logout()
            raise SessionExpired("Session expired. Please log in again.")
        return resp2
