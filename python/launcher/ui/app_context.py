# ui/app_context.py
from launcher.services.auth_service import AuthService
from launcher.services.project_service import ProjectService

from launcher.services.theater_service import TheaterService
from launcher.services.http_client import HttpClient

from PyQt6.QtCore import QObject, pyqtSignal

class AppContext(QObject):

    session_expired = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        client = HttpClient()
        self.auth_service = AuthService()
        self.project_service = ProjectService(self.auth_service, client)
        self.theater_service = TheaterService(self.auth_service, client)
