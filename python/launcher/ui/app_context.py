# ui/app_context.py
from launcher.services.auth_service import AuthService
from launcher.services.project_service import ProjectService
from launcher.services.launch_service import LaunchService
from launcher.services.http_client import HttpClient


class AppContext:
    def __init__(self):
        client = HttpClient()
        self.auth_service = AuthService()
        self.project_service = ProjectService(self.auth_service, client)
        self.sequence_service = ProjectService(self.auth_service, client)
        self.launch_service = LaunchService(self.auth_service)
