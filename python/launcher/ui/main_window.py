# launcher/ui/main_window.py

from __future__ import annotations

from typing import TYPE_CHECKING, List, Dict

from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QFrame,
    QSizePolicy,
)

from launcher.ui.widgets.project_card import ProjectCard
from launcher.domain.project import Project

if TYPE_CHECKING:
    from launcher.ui.app_context import AppContext
    from launcher.domain.project import Project
    from launcher.domain.user import User


# ---------------- Worker ----------------


class LoadProjectsWorker(QThread):
    """
    Background worker to load projects from the ProjectService.
    """
    success = pyqtSignal(object)  # List[Project]
    error = pyqtSignal(str)

    def __init__(self, app_context: AppContext, parent=None):
        super().__init__(parent)
        self._ctx = app_context

    def run(self):
        try:
            projects = self._ctx.project_service.list_my_projects()
            self.success.emit(projects)
        except Exception as exc:
            self.error.emit(str(exc))


# ---------------- Main Window ----------------


class MainWindow(QMainWindow):
    """
    Projects window styled via global theme.qss.

    Uses:
    - Welcome label with user's name/email
    - Projects list rendered as ProjectCard widgets inside a QListWidget
    - New Project / Refresh buttons
    """

    def __init__(self, app_context: AppContext, user: User, parent=None):
        super().__init__(parent)

        self._ctx = app_context
        self._user = user

        self._projects: List[Project] = []
        self._projects_by_id: Dict[str, Project] = {}
        self._load_worker: LoadProjectsWorker | None = None

        self.setWindowTitle("Mihira Theatre – Projects")
        self.resize(1365, 768)

        self._build_ui()
        self._load_projects()

    def _make_dummy_projects(self) -> list[Project]:
        return [
            Project(
                id="P-1001",
                name="Blade Runner",
                description="Scenes 137, Sets 90",
                uproject_path=r"C:\Unreal\Projects\BladeRunner\BladeRunner.uproject",
            ),
            Project(
                id="P-1002",
                name="Eternal Wars EP1",
                description="Scenes 21, Sets 8",
                uproject_path=r"C:\Unreal\Projects\EternalWars\EW_EP1.uproject",
            ),
            Project(
                id="P-1003",
                name="Eternal Wars EP2",
                description="Scenes 12, Sets 22",
                uproject_path=r"C:\Unreal\Projects\EternalWars\EW_EP2.uproject",
            ),
        ]

    def _build_ui(self):
        central = QWidget(self)
        central.setObjectName("ProjectCentral")  # used by global QSS
        outer = QVBoxLayout(central)
        outer.setContentsMargins(32, 24, 32, 24)
        outer.setSpacing(16)

        # ----- Header row: welcome + refresh button -----
        header = QHBoxLayout()
        header.setSpacing(8)

        welcome_name = self._user.display_name or self._user.email
        self.welcome_label = QLabel(f"Welcome Back, {welcome_name}!", central)
        self.welcome_label.setObjectName("WelcomeLabel")
        header.addWidget(self.welcome_label)

        header.addStretch(1)

        self.refresh_button = QPushButton("Refresh", central)
        self.refresh_button.setObjectName("RefreshButton")
        self.refresh_button.clicked.connect(self._load_projects)
        header.addWidget(self.refresh_button)

        outer.addLayout(header)

        # ----- Section title -----
        self.section_label = QLabel("Projects", central)
        self.section_label.setObjectName("SectionLabel")
        outer.addWidget(self.section_label)

        # ----- Status label -----
        self.status_label = QLabel("", central)
        self.status_label.setObjectName("StatusLabelProjects")
        outer.addWidget(self.status_label)

        # ----- Projects container (dark card from QSS) -----
        self.projects_container = QFrame(central)
        self.projects_container.setObjectName("ProjectsContainer")
        self.projects_container.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )

        container_layout = QVBoxLayout(self.projects_container)
        container_layout.setContentsMargins(24, 24, 24, 24)
        container_layout.setSpacing(12)

        # Projects list
        self.project_list = QListWidget(self.projects_container)
        self.project_list.setObjectName("ProjectList")
        self.project_list.setSpacing(8)  # space between cards

        container_layout.addWidget(self.project_list)
        outer.addWidget(self.projects_container)

        # ----- Bottom bar -----
        bottom = QHBoxLayout()
        bottom.addStretch(1)

        self.new_project_button = QPushButton("New Project", central)
        self.new_project_button.setObjectName("NewProjectButton")
        # TODO: connect to "create project" flow when ready
        bottom.addWidget(self.new_project_button)

        outer.addLayout(bottom)

        self.setCentralWidget(central)

    # ---------------- Project loading ----------------

    def _set_loading(self, loading: bool, message: str = ""):
        enabled = not loading
        self.refresh_button.setEnabled(enabled)
        self.new_project_button.setEnabled(enabled)
        self.project_list.setEnabled(enabled)
        self.status_label.setText(message)

    def _load_projects(self):
        #Avoid overlapping loads
        if self._load_worker is not None and self._load_worker.isRunning():
            return

        self._set_loading(True, "Loading projects...")

        self._load_worker = LoadProjectsWorker(self._ctx, self)
        self._load_worker.success.connect(self._handle_projects_loaded)
        self._load_worker.error.connect(self._handle_projects_error)
        self._load_worker.finished.connect(self._cleanup_load_worker)
        self._load_worker.start()
        self._set_loading(False, "")
        
        # dummy = self._make_dummy_projects()
        # self._handle_projects_loaded(dummy)


    def _handle_projects_loaded(self, projects: List[Project]):
        print("DEBUG: _handle_projects_loaded called with", len(projects), "projects")

        self._projects = list(projects or [])
        self._projects_by_id = {p.id: p for p in self._projects}

        self.project_list.clear()

        if not self._projects:
            self.status_label.setText("No projects available.")
            print("DEBUG: project_list.count() =", self.project_list.count())
            return

        self.status_label.setText(f"Loaded {len(self._projects)} project(s).")

        for project in self._projects:
            item = QListWidgetItem(self.project_list)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

            card = ProjectCard(
                project_id=project.id,
                title=project.name,
                scenes_sets_text=project.description or "",
                id_text=f"ID {project.id}",
                accent_color="#4AC0FF",
                icon="app_icon.png",
            )

            card.browse_clicked.connect(self._on_card_browse)
            card.assemble_clicked.connect(self._on_card_assemble)
            card.delete_clicked.connect(self._on_card_delete)
            card.menu_clicked.connect(self._on_card_menu)

            item.setSizeHint(card.sizeHint())
            self.project_list.addItem(item)
            self.project_list.setItemWidget(item, card)

        print("DEBUG: project_list.count() =", self.project_list.count())


    def _handle_projects_error(self, message: str):
        # This slot can be called even as window is closing, so be defensive
        try:
            self._projects = []
            self._projects_by_id = {}
            if self.project_list:
                self.project_list.clear()
        except RuntimeError:
            # Underlying C++ widget may already be deleted if app is exiting
            return

        self._set_loading(False, "")
        QMessageBox.critical(self, "Error loading projects", message)

    def _cleanup_load_worker(self):
        self._load_worker = None

    # ---------------- Card signal handlers ----------------

    def _get_project(self, project_id: str) -> Project | None:
        return self._projects_by_id.get(project_id)

    def _on_card_browse(self, project_id: str):
        project = self._get_project(project_id)
        if not project:
            return

        # TODO: later: open Sequences/Scenes page for this project
        QMessageBox.information(self, "Browse", f"Browse project: {project.name}")

    def _on_card_assemble(self, project_id: str):
        project = self._get_project(project_id)
        if not project:
            return

        try:
            self._ctx.launch_service.launch_project(project)
            QMessageBox.information(self, "Launching", f"Assembling / launching: {project.name}")
        except Exception as exc:
            QMessageBox.critical(self, "Launch failed", str(exc))

    def _on_card_delete(self, project_id: str):
        project = self._get_project(project_id)
        if not project:
            return

        reply = QMessageBox.question(
            self,
            "Delete project",
            f"Are you sure you want to delete '{project.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            # TODO: implement deletion via backend
            QMessageBox.information(self, "Delete", f"(Not implemented) Would delete: {project.name}")

    def _on_card_menu(self, project_id: str):
        project = self._get_project(project_id)
        if not project:
            return
        # TODO: show context menu / options dialog
        QMessageBox.information(self, "Menu", f"(Not implemented) Menu for: {project.name}")

    # ---------------- Cleanup ----------------

    def closeEvent(self, event):
        # Safely stop worker to avoid signals firing after widgets are gone
        if self._load_worker and self._load_worker.isRunning():
            self._load_worker.finished.disconnect()
            self._load_worker.error.disconnect()
            self._load_worker.success.disconnect()
            self._load_worker.requestInterruption()
            self._load_worker.quit()
            self._load_worker.wait(200)
        self._load_worker = None
        super().closeEvent(event)
