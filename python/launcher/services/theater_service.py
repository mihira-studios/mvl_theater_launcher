from PyQt6.QtCore import QObject, QProcess, pyqtSignal
from .http_client import HttpClient
from .auth_service import AuthService

from PyQt6.QtCore import QProcess, QProcessEnvironment

import os
import subprocess

class TheaterService(QObject):
    started = pyqtSignal()
    finished = pyqtSignal(int)
    output = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, auth: AuthService, client: HttpClient | None = None, parent = None):
        super().__init__(parent)
        self.proc = QProcess(self)
        self.proc.started.connect(self.started)
        self.proc.finished.connect(lambda code, status: self.finished.emit(code))
        self.proc.errorOccurred.connect(self._on_err)
        self.proc.started.connect(lambda: print("[QProcess] started"))
        self.proc.finished.connect(lambda code, status: print(f"[QProcess] finished code={code} status={status}"))
        self.proc.readyReadStandardError.connect(self._on_err)
        self.proc.readyReadStandardOutput.connect(self._on_out)

    def launch(self, editor_exe: str, uproject: str, args=None, env: dict[str, str] | None = None):
        args = args or []

        # Hard validation (do this first!)
        if not os.path.exists(editor_exe):
            raise FileNotFoundError(f"UnrealEditor not found: {editor_exe}")
        if not os.path.exists(uproject):
            raise FileNotFoundError(f".uproject not found: {uproject}")

        # Working directory helps on Windows
        self.proc.setWorkingDirectory(os.path.dirname(uproject))

        # Env
        if env:
            pe = QProcessEnvironment.systemEnvironment()
            for k, v in env.items():
                pe.insert(k, str(v))
            self.proc.setProcessEnvironment(pe)

        # Ensure we see logs if -log is used
        self.proc.setProcessChannelMode(QProcess.ProcessChannelMode.SeparateChannels)

        # Start
        self.proc.start(editor_exe, [uproject, *args])

        # If it fails to start, show why
        if not self.proc.waitForStarted(5000):
            raise RuntimeError(f"Failed to start process: {self.proc.errorString()}")

    def launch_detached(self, editor_exe: str, uproject: str, args=None, env=None):
        args = args or []

        if env:
            pe = QProcessEnvironment.systemEnvironment()
            for k, v in env.items():
                pe.insert(k, str(v))
            self.proc.setProcessEnvironment(pe)

        ok = QProcess.startDetached(editor_exe, [uproject, *args], os.path.dirname(uproject))
        if not ok:
            raise RuntimeError("startDetached failed (check paths/permissions).")



    def launch_with_subprocess(self, editor_exe: str, uproject: str, args=None, env=None):
        args = args or []

        # Hard validation (do this first!)
        if not os.path.exists(editor_exe):
            raise FileNotFoundError(f"UnrealEditor not found: {editor_exe}")
        if not os.path.exists(uproject):
            raise FileNotFoundError(f".uproject not found: {uproject}")

        subprocess.run([editor_exe,uproject, "-MVLEditor"], env=env, shell=True, check=True)

    def _on_out(self):
        self.output.emit(bytes(self.proc.readAllStandardOutput()).decode(errors="replace"))

    def _on_err(self):
        self.error.emit(bytes(self.proc.readAllStandardError()).decode(errors="replace"))

