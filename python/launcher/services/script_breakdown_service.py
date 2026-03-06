from __future__ import annotations

import os
from typing import TYPE_CHECKING

from launcher.domain.script_breakdown import ScriptBreakdown

if TYPE_CHECKING:
    from launcher.ui.app_context import AppContext


class ScriptBreakdownService:

    def __init__(self, ctx: AppContext):
        self._ctx = ctx

    def parse(self, pdf_path: str) -> ScriptBreakdown:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        with open(pdf_path, "rb") as f:
            files = {
                "file": (os.path.basename(pdf_path), f, "application/pdf")
            }
            response = self._ctx.api_client.request(
                "POST",
                "/script/parse",
                files=files,
            )

        response.raise_for_status()
        data = response.json()
        return ScriptBreakdown(**data)