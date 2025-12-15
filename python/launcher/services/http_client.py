# services/http_client.py
import requests
from launcher import config


class HttpClient:
    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or config.FASTAPI_BASE_URL
        self.session = requests.Session()
        self.session.timeout = 10  # default

    def _url(self, path: str) -> str:
        return self.base_url.rstrip("/") + "/" + path.lstrip("/")

    def get(self, path: str, **kwargs):
        return self.session.get(self._url(path), **kwargs)

    def post(self, path: str, **kwargs):
        return self.session.post(self._url(path), **kwargs)
