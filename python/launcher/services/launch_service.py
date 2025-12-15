# services/launch_service.py
import subprocess
from launcher import config
from launcher.domain.project import Project
from .auth_service import AuthService


class LaunchService:
    def __init__(self, auth: AuthService):
        self.auth = auth

    def launch_project(self, project: Project):
        tokens = self.auth.tokens
        if not tokens:
            raise RuntimeError("Not authenticated")

        args = [
            config.UNREAL_EDITOR_PATH,
            project.uproject_path,
            f"-projectId={project.id}",
            f"-authToken={tokens.access_token}",
        ]

        # Start Unreal as separate process
        subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
