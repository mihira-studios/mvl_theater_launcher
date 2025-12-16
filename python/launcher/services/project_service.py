# services/project_service.py
from .http_client import HttpClient
from .auth_service import AuthService
from launcher.domain.project import Project
from launcher.domain.sequence import Sequence
from launcher.domain.shot import Shot

from uuid import UUID

class ProjectService:
    def __init__(self, auth: AuthService, client: HttpClient | None = None):
        self.auth = auth
        self.client = client or HttpClient()

    def list_my_projects(self) -> list[Project]:
        headers = self.auth.auth_headers()
        resp = self.client.get("auth/me/projects", headers=headers)
        resp.raise_for_status()
        items = resp.json()

        projects: list[Project] = []
        for p in items:
            count_resp = self.client.get(f"projects/{p['id']}/sequences/count", headers=headers)
            count_resp.raise_for_status()
            seq_count = count_resp.json().get("sequence_count", 0)

            # shots count (summed from Sequence.meta["shots"])
            shot_resp = self.client.get(f"projects/{p['id']}/shots/count", headers=headers)
            shot_resp.raise_for_status()
            shot_count = shot_resp.json().get("shot_count", 0)

            projects.append(
                Project(
                    id=p["id"],
                    name=p["name"],
                    code=p["code"],
                    sequence_count=int(seq_count),
                    shot_count=int(shot_count),
                )
            )

        return projects
    
    def list_sequences(self, project_id: str | UUID) -> list[Sequence]:
        headers = self.auth.auth_headers()

        # endpoint suggestion: /projects/{project_id}/sequences
        resp = self.client.get(f"projects/{project_id}/sequences", headers=headers)
        resp.raise_for_status()
        items = resp.json()

        return [
            Sequence(
                id=s["id"],
                project_id=s["project_id"],
                code=s["code"],
                name=s.get("name"),
                status=s.get("status", "new"),
                meta=s.get("meta", {}),
            )
            for s in items
        ]

    def list_shots(self, project_id: str | UUID, sequence_id: str | UUID) -> list[Shot]:
        headers = self.auth.auth_headers()

        # endpoint suggestion: /projects/{project_id}/sequences
        resp = self.client.get(f"/shots", headers=headers)
        resp.raise_for_status()
        items = resp.json()

        return [
            Sequence(
                id=s["id"],
                project_id=s["project_id"],
                sequence_id=s["sequence_id"],
                code=s["code"],
                name=s.get("name"),
                status=s.get("status", "new"),
                meta=s.get("meta", {}),
            )
            for s in items
        ]
    


