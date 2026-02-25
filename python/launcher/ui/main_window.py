# launcher/ui/main_window.py

from __future__ import annotations

import os, sys
from typing import TYPE_CHECKING, List, Dict

from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QMenu,
    QWidgetAction,
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
    QStackedWidget,
    QToolButton,
)

from PyQt6.QtGui import QIcon

from launcher.ui.card_list_page import CardListPage
from launcher.ui.widgets.project_card import ProjectCard
from launcher.ui.widgets.entity_card import CardButtonSpec, EntityCard
from launcher.domain.project import Project
from python.launcher.ui.script_breakdown_page import ScriptBreakdownPage

if TYPE_CHECKING:
    from launcher.ui.app_context import AppContext
    from launcher.domain.project import Project
    from launcher.domain.user import User

class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        if not self.isEnabled():
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class LoadSequencesWorker(QThread):
    success = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, ctx, project_id: str, parent=None):
        super().__init__(parent)
        self._ctx = ctx
        self._project_id = project_id

    def run(self):
        try:
            seqs = self._ctx.project_service.list_sequences(self._project_id)
            self.success.emit(seqs)
        except Exception as e:
            self.error.emit(str(e))
        
class LoadProjectsWorker(QThread):
    """
    Background worker to load projects from the ProjectService.
    """
    success = pyqtSignal(object)
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

class MainWindow(QMainWindow):
    """
    Projects window styled via global theme.qss.

    Uses:
        - Welcome label with user's name/email
        - Projects list rendered as ProjectCard widgets inside a QListWidget
        - New Project / Refresh buttons
    """

    def __init__(self, app_context: AppContext, user: User, on_logout, parent=None):
        super().__init__(parent)

        self._ctx = app_context
        self._ctx.session_expired.connect(self._on_session_expired)
        
        self._user = user

        self._on_logout = on_logout

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

        initial = (self._user.display_name or self._user.email or "?").strip()[:1].upper()

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

        self.user_button = QToolButton(central)
        self.user_button.setObjectName("UserInitialButton")
        self.user_button.setText(initial)
        self.user_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.user_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextOnly)
        self.user_button.setFixedSize(36, 36)  # round size

        self.user_menu = self._build_user_menu()
        self.user_button.setMenu(self.user_menu)

        header.addWidget(self.user_button)

        outer.addLayout(header)

        # ----- Section title -----
        crumb_row = QHBoxLayout()
        crumb_row.setSpacing(8)

        self.crumb_projects = ClickableLabel("Projects", central)
        self.crumb_projects.setObjectName("SectionCrumb")

        self.crumb_sep = QLabel("›", central)
        self.crumb_sep.setObjectName("SectionCrumbSep")

        self.crumb_current = QLabel("", central)   # current page (not clickable)
        self.crumb_current.setObjectName("SectionCrumbCurrent")

        self.crumb_projects.clicked.connect(self._back_to_projects)

        crumb_row.addWidget(self.crumb_projects)
        crumb_row.addWidget(self.crumb_sep)
        crumb_row.addWidget(self.crumb_current)
        crumb_row.addStretch(1)

        outer.addLayout(crumb_row)

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

        
        self.stack = QStackedWidget(self.projects_container)
        self.stack.setAutoFillBackground(False)
        self.stack.setObjectName("MainStack")
        self.stack.currentChanged.connect(lambda _: self._update_breadcrumb())
        container_layout.addWidget(self.stack)

        outer.addWidget(self.projects_container)

        # ----- Bottom bar -----
        bottom = QHBoxLayout()
        bottom.addStretch(1)

        self.new_project_button = QPushButton("New Project", central)
        self.new_project_button.setObjectName("NewProjectButton")
        self.new_project_button.clicked.connect(self._show_script_breakdown)
        # TODO: connect to "create project" flow when ready
        bottom.addWidget(self.new_project_button)

        outer.addLayout(bottom)

        self.setCentralWidget(central)

        self._build_pages()
    
    def _show_script_breakdown(self):
        self.crumb_current.setText("Script Breakdown")
        self.stack.setCurrentWidget(self.script_breakdown_page)

    def _logout_clicked(self):
        self._on_logout("Logged out.", self)

    def _build_user_menu(self) -> QMenu:
        menu = QMenu(self)
        menu.setObjectName("UserMenu")

        # Header widget inside menu
        card = QWidget(menu)
        card.setObjectName("UserMenuCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(4)

        name = self._user.display_name or self._user.email
        name_lbl = QLabel(name, card)
        name_lbl.setObjectName("UserMenuName")

        email_lbl = QLabel(self._user.email, card)
        email_lbl.setObjectName("UserMenuEmail")

        layout.addWidget(name_lbl)
        layout.addWidget(email_lbl)

        wa = QWidgetAction(menu)
        wa.setDefaultWidget(card)
        menu.addAction(wa)

        menu.addSeparator()

        signout = menu.addAction("Sign out")
        signout.triggered.connect(self._logout_clicked)  # your existing logout handler
        return menu

    def _update_breadcrumb(self):
        on_projects = (self.stack.currentWidget() == self.projects_page)
        on_script_breakdown = (self.stack.currentWidget() == self.script_breakdown_page)

        if on_projects:
            self.crumb_projects.setText("Projects")
            self.crumb_sep.setVisible(False)
            self.crumb_current.setVisible(False)
            # optional: disable clicking when already on projects
            self.crumb_projects.setEnabled(False)
        else:
            # sequences page
            proj = None
            if getattr(self, "_current_project_id", None):
                proj = self._projects_by_id.get(self._current_project_id)

            self.crumb_projects.setEnabled(True)
            self.crumb_sep.setVisible(True)
            self.crumb_current.setVisible(True)

            self.crumb_projects.setText("Projects")
            self.crumb_current.setText(proj.name if proj else "Sequences")

    def _on_section_clicked(self):
        # example: if you're on sequences, go back to projects
        if self.stack.currentWidget() == self.sequences_page:
            self._back_to_projects()

    def _set_loading(self, loading: bool, message: str = ""):
        enabled = not loading
        self.refresh_button.setEnabled(enabled)
        self.new_project_button.setEnabled(enabled)
        self.stack.setEnabled(enabled)
        self.status_label.setText(message)

    def _load_sequences(self, project_id: str):
        # Avoid overlapping loads
        if getattr(self, "_seq_worker", None) is not None and self._seq_worker.isRunning():
            return

        self._current_project_id = project_id
        self._set_loading(True, "Loading sequences...")

        self._seq_worker = LoadSequencesWorker(self._ctx, project_id, self)
        self._seq_worker.success.connect(self._handle_sequences_loaded)
        self._seq_worker.error.connect(self._handle_sequences_error)
        self._seq_worker.finished.connect(self._cleanup_seq_worker)
        self._seq_worker.start()

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

    def _make_project_card(self, project: Project) -> EntityCard:
        card = EntityCard(
            entity_id=project.id,
            title=project.name,
            meta_text=f"sequences {project.sequence_count} • shots {project.shot_count}",
            id_text=f"ID: {project.code}",
            icon="project.png",
            buttons=[
                CardButtonSpec("browse", "Browse", qss_object="PrimaryButton"),
                CardButtonSpec("assemble", "Assemble", qss_object="PrimaryButton"),
                CardButtonSpec("delete", text="🗑", qss_object="DangerIconButton", fixed_size=(40, 40)),
                CardButtonSpec("menu", text="⋯", qss_object="IconButton", fixed_size=(40, 40)),
            ],
        )
        return card

    def _make_sequence_card(self, seq) -> EntityCard:
        card = EntityCard(
            entity_id=seq.id,
            title=f"{seq.code} {seq.name or ''}".strip(),
            meta_text=f"status {seq.status}",
            id_text=f"ID: {seq.id}",
            icon="sequence.png",
            buttons=[
                CardButtonSpec("open", "Open", qss_object="PrimaryButton"),
                CardButtonSpec("delete", text="🗑", qss_object="DangerIconButton", fixed_size=(40, 40)),
            ],
        )
        return card

    def _handle_sequences_loaded(self, sequences):
        self._set_loading(False, "")

        sequences = list(sequences or [])
        if not sequences:
            self.status_label.setText("No sequences available.")
            self.sequences_page.set_items([])
        else:
            self.status_label.setText(f"Loaded {len(sequences)} sequence(s).")
            self.sequences_page.set_items(sequences)

        self.stack.setCurrentWidget(self.sequences_page)

    def _handle_sequences_error(self, msg: str):
        self._set_loading(False, msg)

    def _cleanup_seq_worker(self):
        self._seq_worker = None

    def _handle_projects_loaded(self, projects: List[Project]):
        self._set_loading(False, "")
        self._projects = list(projects or [])
        self._projects_by_id = {p.id: p for p in self._projects}

        if not self._projects:
            self.status_label.setText("No projects available.")
            self.projects_page.set_items([])
            return

        self.status_label.setText(f"Loaded {len(self._projects)} project(s).")
        self.projects_page.set_items(self._projects)
    
    def _on_projects_action(self, project_id: str, action: str, project_obj):
        if action == "browse":
            self._load_sequences(project_id)  
        elif action == "assemble":
            self._on_card_assemble(project_id)
        elif action == "delete":
            self._on_card_delete(project_id)
        elif action == "menu":
            self._on_card_menu(project_id)

        self._projects_obj = project_obj

    def _handle_projects_error(self, message: str):
       
        self._set_loading(False, "")
        QMessageBox.critical(self, "Error loading projects", message)

        self._set_loading(False, "")
        QMessageBox.critical(self, "Error loading projects", message)

    def _cleanup_load_worker(self):
        self._load_worker = None

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

    def _build_pages(self):
        self.projects_page = CardListPage(make_card=self._make_project_card, show_back=False)
        self.sequences_page = CardListPage(make_card=self._make_sequence_card, show_back=True)
        self.script_breakdown_page = ScriptBreakdownPage()

        self.stack.addWidget(self.projects_page)
        self.stack.addWidget(self.sequences_page)

        self.projects_page.action.connect(self._on_projects_action)
        self.sequences_page.action.connect(self._on_sequences_action)
        self.sequences_page.back_requested.connect(self._back_to_projects)
        self.script_breakdown_page.back_requested.connect(self._back_to_projects) 

    def _show_projects(self):
        self.stack.setCurrentWidget(self.projects_page)

    def _show_sequences(self, project_id: str):
        self._current_project_id = project_id
        self.stack.setCurrentWidget(self.sequences_page)

    def _on_sequences_action(self, sequence_id: str, action: str, sequence_obj):
        env = os.environ.copy()
        env["PROJECTS_ROOT_DIR"] = r"J:"

        # Pick the right fields for your domain objects:
        env["MVL_PROJECT"] = "tg63" #getattr(self._projects_obj, "code", None) or str(getattr(self._projects_obj, "id", ""))
        env["MVL_TYPE"] = "sequences"
        env["MVL_SCOPE"] = "sq01"#getattr(sequence_obj, "code", None) or str(getattr(sequence_obj, "id", ""))
        env["MVL_CONTAINER"] = "master"
        env["MVL_TASK"] = "layout"
        env["MVL_STEP"] = "lay"

        if action == "open":
            if os.environ.get("THEATER_EXECUTABLE") and os.environ.get("THEATER_UPROJECT_TEMPLATE"):
                ue_editor = os.path.join(os.environ.get("THEATER_HOME")) #, r"Engine\Binaries\Win64\UnrealEditor.exe") 
                uproject = os.environ.get("THEATER_UPROJECT_TMEPLATE") 
                service = self._ctx.theater_service.launch(ue_editoclr,uproject,["-MVLEditor"], env=env)
            else:
                print(f"THEATER_EXECUTABLE or THEATER_UPROJECT_TMEPLATE env not set")
        elif action == "delete":
            print("Delete sequence", sequence_id)

    def _refresh_current_page(self):
        current = self.stack.currentWidget()
        if hasattr(current, "refresh"):
            current.refresh()

    def _back_to_projects(self):
        self._show_projects()

    def _on_session_expired(self, msg: str):
        QMessageBox.information(self, "Session expired", mg)
        self._ctx.auth_service.logout()
        self._on_logout(msg, self)
