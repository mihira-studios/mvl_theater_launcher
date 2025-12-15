from __future__ import annotations

from typing import Optional


from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QSizePolicy,
)

from launcher.util.helper import icon_path


class ProjectCard(QFrame):
    """
    A single project row styled like your Mihira launcher mock.

    Signals:
        browse_clicked(project_id)
        assemble_clicked(project_id)
        delete_clicked(project_id)
        menu_clicked(project_id)
    """

    browse_clicked = pyqtSignal(str)
    assemble_clicked = pyqtSignal(str)
    delete_clicked = pyqtSignal(str)
    menu_clicked = pyqtSignal(str)

    def __init__(self, project_id: str, title: str, scenes_sets_text: str,
                 id_text: str, accent_color: str = "#4AC0FF",
                 icon: str | None = None,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._project_id = project_id
        self._accent_color = accent_color
        self._icon = icon

        self.setObjectName("ProjectCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(96)

        # Enable hover events on this widget
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self._build_ui(title, scenes_sets_text, id_text)
        self._apply_style()

    # ------------------------------------------------------------------ UI
    def enterEvent(self, event: QEvent) -> None:
        """Mouse moved over the card."""
        # mark the background frame as hovered
        self._card.setProperty("hover", True)
        self._refresh_styles(self._card)
        super().enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        """Mouse left the card."""
        self._card.setProperty("hover", False)
        self._refresh_styles(self._card)
        super().leaveEvent(event)

    def _refresh_styles(self, widget: QWidget) -> None:
        """Force QSS to re-evaluate after property changes."""
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()
    
    def _build_ui(self, title: str, scenes_sets_text: str, id_text: str) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Card background
        self._card = QFrame(self)
        self._card.setObjectName("CardBackground")
        card_layout = QHBoxLayout(self._card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(16)

        # Left color stripe
        stripe = QFrame(self._card)
        stripe.setObjectName("AccentStripe")
        stripe.setFixedWidth(6)
        card_layout.addWidget(stripe)

        # Logo
        logo_wrapper = QFrame(self._card)
        logo_layout = QVBoxLayout(logo_wrapper)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.icon_label = QLabel(logo_wrapper)
        self.icon_label.setObjectName("ProjectLogo")
        self.icon_label.setFixedSize(48, 48)

        if self._icon:
            pm = QPixmap(icon_path(self._icon))
            if not pm.isNull():
                self.icon_label.setPixmap(
                    pm.scaled(
                        self.icon_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )

        logo_layout.addWidget(self.icon_label)
        card_layout.addWidget(logo_wrapper)

        # Text info (title + meta)
        info_wrapper = QFrame(self._card)
        info_layout = QVBoxLayout(info_wrapper)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        self.title_label = QLabel(title, info_wrapper)
        self.title_label.setObjectName("ProjectTitle")

        self.meta_label = QLabel(scenes_sets_text, info_wrapper)
        self.meta_label.setObjectName("ProjectMeta")

        self.id_label = QLabel(id_text, info_wrapper)
        self.id_label.setObjectName("ProjectId")

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.meta_label)
        info_layout.addWidget(self.id_label)

        card_layout.addWidget(info_wrapper, stretch=1)

        # Right side container (darker background for buttons)
        right_container = QFrame(self._card)
        right_container.setObjectName("RightContainer")
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(24, 8, 8, 8)
        right_layout.setSpacing(12)

        # Browse / Assemble buttons
        self.browse_btn = QPushButton("Browse", right_container)
        self.browse_btn.setObjectName("BrowseButton")
        self.browse_btn.clicked.connect(
            lambda: self.browse_clicked.emit(self._project_id)
        )

        self.assemble_btn = QPushButton("Assemble", right_container)
        self.assemble_btn.setObjectName("AssembleButton")
        self.assemble_btn.clicked.connect(
            lambda: self.assemble_clicked.emit(self._project_id)
        )

        right_layout.addWidget(self.browse_btn)
        right_layout.addWidget(self.assemble_btn)

        # Trash + menu buttons (round icon buttons)
        self.trash_btn = QPushButton(right_container)
        self.trash_btn.setObjectName("TrashButton")
        self.trash_btn.setFixedSize(40, 40)
        self.trash_btn.clicked.connect(
            lambda: self.delete_clicked.emit(self._project_id)
        )

        self.menu_btn = QPushButton(right_container)
        self.menu_btn.setObjectName("MenuButton")
        self.menu_btn.setFixedSize(40, 40)
        self.menu_btn.clicked.connect(
            lambda: self.menu_clicked.emit(self._project_id)
        )

        # Optional: set icons if you have them
        # self.trash_btn.setIcon(QIcon("launcher/resources/icons/trash.png"))
        # self.menu_btn.setIcon(QIcon("launcher/resources/icons/more_dots.png"))

        right_layout.addWidget(self.trash_btn)
        right_layout.addWidget(self.menu_btn)

        card_layout.addWidget(right_container)

        outer.addWidget(self._card)

    # ------------------------------------------------------------------ Style

    def _apply_style(self) -> None:
        self.setStyleSheet(
            f"""
            #ProjectCard {{
                background-color: transparent;
            }}

            #CardBackground {{
                background-color: #2A2D34;
                border-radius: 18px;
            }}

            /* Hovered card background */
            #CardBackground[hover="true"] {{
                background-color: #343844;
            }}

            #AccentStripe {{
                background-color: {self._accent_color};
                border-radius: 3px;
            }}

            #ProjectLogo {{
                background-color: transparent;
            }}

            #ProjectTitle {{
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 600;
            }}

            #ProjectMeta {{
                color: #B0B3C0;
                font-size: 13px;
            }}

            #ProjectId {{
                color: #6E7280;
                font-size: 12px;
            }}

            #RightContainer {{
                background-color: #33363F;
                border-radius: 16px;
            }}

            QPushButton#BrowseButton,
            QPushButton#AssembleButton {{
                background-color: transparent;
                color: #C9B8FF;
                border: 2px solid #7B61FF;
                border-radius: 18px;
                padding: 4px 18px;
                font-size: 13px;
            }}

            QPushButton#BrowseButton:hover,
            QPushButton#AssembleButton:hover {{
                background-color: rgba(123, 97, 255, 0.15);
            }}

            QPushButton#TrashButton {{
                background-color: #FF4E6A;
                border-radius: 20px;
                border: none;
                color: #FFFFFF;
                font-size: 18px;
            }}

            QPushButton#TrashButton::before {{
                content: "🗑";
            }}

            QPushButton#MenuButton {{
                background-color: transparent;
                border-radius: 20px;
                border: none;
                color: #9DA0AE;
                font-size: 20px;
            }}

            QPushButton#MenuButton::before {{
                content: "⋯";
            }}

            QPushButton#TrashButton:hover {{
                background-color: #FF3355;
            }}

            QPushButton#MenuButton:hover {{
                background-color: rgba(255, 255, 255, 0.06);
            }}
            """
        )

    # ------------------------------------------------------------------ Helpers

    def set_logo(self, path: str) -> None:
        """Change the logo at runtime."""
        pm = QPixmap(path)
        if not pm.isNull():
            self.icon_label.setPixmap(
                pm.scaled(
                    self.icon_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    def set_accent_color(self, color: str) -> None:
        """Change the left stripe color dynamically."""
        self._accent_color = color
        self._apply_style()
