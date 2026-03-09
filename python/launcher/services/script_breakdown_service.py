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

    def save_project(self, name: str, code: str, project_type: str, breakdown: ScriptBreakdown):
        payload = {
            "name": name,
            "code": code,
            "type": project_type,
            "description": (
                f"Pages: {breakdown.total_pages} | "
                f"Scenes: {breakdown.total_scenes} | "
                f"Characters: {breakdown.total_characters}"
            ),
            "status": "Active",
            "archived": False,
            "config": {
                "total_pages": breakdown.total_pages,
                "total_scenes": breakdown.total_scenes,
                "total_characters": breakdown.total_characters,
                "scenes": breakdown.scenes,
                "character_appearances": breakdown.character_appearances,
            },
        }

        response = self._ctx.api_client.request(
            "POST",
            "/projects/",
            json=payload,
        )
        response.raise_for_status()
        project = response.json()

        user_kc_id = self._ctx.auth_service._current_user.id
        access_response = self._ctx.api_client.request(
            "POST",
            "/projects/access",
            json={
                "project_id": project["id"],
                "user_kc_id": user_kc_id,
                "role": "admin",
            },
        )
        access_response.raise_for_status()

        return project