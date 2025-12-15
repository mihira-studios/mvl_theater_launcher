from __future__ import annotations
from typing import TYPE_CHECKING, List

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem
)

if TYPE_CHECKING:
    from launcher.ui.app_context import AppContext
    from launcher.domain.project import Project

class SequencesPage(QWidget):
    """
    Shows sequences/scenes for a given project.
    Styled by global theme via objectNames.
    """

    def __init__(self, ctx: AppContext, project: Project, on_back, parent=None):
        super().__init__(parent)
        self._ctx = ctx
        self._project = project
        self._on_back = on_back  # callback to go back to projects

        self.setObjectName("ProjectCentral")  # reuse same background style
        self._build_ui()
        self._load_sequences()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(16)

        # header: back + title
        header = QHBoxLayout()
        self.back_button = QPushButton("← Projects", self)
        self.back_button.setObjectName("RefreshButton")  # will get pill style
        self.back_button.clicked.connect(self._on_back)
        header.addWidget(self.back_button)

        header.addStretch(1)

        self.title_label = QLabel(f"{self._project.name} – Sequences", self)
        self.title_label.setObjectName("SectionLabel")
        header.addWidget(self.title_label, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(header)

        # status
        self.status_label = QLabel("", self)
        self.status_label.setObjectName("StatusLabelProjects")
        layout.addWidget(self.status_label)

        # list container
        from PyQt6.QtWidgets import QFrame, QVBoxLayout as QV

        self.container = QFrame(self)
        self.container.setObjectName("ProjectsContainer")

        c_layout = QV(self.container)
        c_layout.setContentsMargins(24, 24, 24, 24)
        c_layout.setSpacing(12)

        self.sequence_list = QListWidget(self.container)
        self.sequence_list.setObjectName("ProjectList")
        c_layout.addWidget(self.sequence_list)

        layout.addWidget(self.container)

    def _load_sequences(self):
        # TODO: replace with real API call:
        # sequences = self._ctx.sequence_service.list_by_project(self._project.id)
        # For now fake:
        fake = ["Opening", "Battle on the bridge", "Finale"]

        self.sequence_list.clear()
        if not fake:
            self.status_label.setText("No sequences.")
        else:
            self.status_label.setText(f"{len(fake)} sequence(s).")
            for name in fake:
                item = QListWidgetItem(name)
                self.sequence_list.addItem(item)
