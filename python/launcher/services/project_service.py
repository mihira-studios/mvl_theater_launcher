# services/project_service.py
from .http_client import HttpClient
from .auth_service import AuthService
from launcher.domain.project import Project


class ProjectService:
    def __init__(self, auth: AuthService, client: HttpClient | None = None):
        self.auth = auth
        self.client = client or HttpClient()

    def list_my_projects(self) -> list[Project]:
        headers = self.auth.auth_headers()
        resp = self.client.get("auth/me/projects", headers=headers)
        resp.raise_for_status()
        items = resp.json()

        print(f"projects {items}")

        return [
            Project(
                id=p["id"],
                name=p["name"],
                code=p["code"],
            )
            for p in items
        ]
