import httpx
import os
from launcher.domain.script_breakdown import ScriptBreakdown

BACKEND_URL = os.environ.get("BREAKDOWN_BACKEND_URL", "http://localhost:8000")

class ScriptBreakdownService:
    def parse(self, pdf_path: str) -> ScriptBreakdown:
        with open(pdf_path, "rb") as f:
            files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}
            response = httpx.post(
                f"{BACKEND_URL}/parse",
                files=files,
                timeout=60.0
            )
        response.raise_for_status()
        data = response.json()
        return ScriptBreakdown(**data)