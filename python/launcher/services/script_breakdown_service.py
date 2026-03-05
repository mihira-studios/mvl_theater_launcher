"""
launcher/services/breakdown_service.py
"""

import os
from launcher.domain.script_breakdown import ScriptBreakdown
from launcher.services.auth_service import AuthService
from launcher.services.http_client import HttpClient


class ScriptBreakdownService:
    def __init__(self, auth: AuthService, client: HttpClient):
        self._auth = auth
        self._client = client

    def parse(self, pdf_path: str) -> ScriptBreakdown:
        with open(pdf_path, "rb") as f:
            files = {
                "file": (os.path.basename(pdf_path), f, "application/pdf")
            }
            # Use auth headers just like your other services
            response = self._client.post(
                "/api/v1/script/parse",
                files=files,
                headers=self._auth.auth_headers(),
                timeout=60.0
            )

        response.raise_for_status()
        data = response.json()
        return ScriptBreakdown(**data)