from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton,
    QHBoxLayout, QVBoxLayout, QSizePolicy
)

from launcher.util.helper import icon_path


@dataclass(frozen=True)
class CardButtonSpec:
    action: str                  # e.g. "browse", "assemble", "delete"
    text: str | None = None      # button label (None => icon-only)
    qss_object: str = "CardButton"  # used for styling, e.g. "PrimaryButton"
    fixed_size: tuple[int, int] | None = None
    tooltip: str | None = None
    enabled: bool = True


class EntityCard(QFrame):
    """
    Generic card for any entity (Project, Sequence, ...)

    Emits:
      action_clicked(entity_id: str, action: str)
    """
    action_clicked = pyqtSignal(str, str)

    def __init__(
        self,
        entity_id: str,
        title: str,
        meta_text: str = "",
        id_text: str = "",
        accent_color: str = "#4AC0FF",
        icon: str | None = None,
        buttons: Iterable[CardButtonSpec] = (),
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._entity_id = entity_id
        self._accent_color = accent_color
        self._icon = icon
        self._buttons = list(buttons)

        self.setObjectName("EntityCard")
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(96)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)

        self._build_ui(title, meta_text, id_text)
        self._apply_style()

    # ------------------------------------------------------------------ Hover
    def enterEvent(self, event) -> None:
        self._card.setProperty("hover", True)
        self._refresh_styles(self._card)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._card.setProperty("hover", False)
        self._refresh_styles(self._card)
        super().leaveEvent(event)

    def _refresh_styles(self, widget: QWidget) -> None:
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()

    # ------------------------------------------------------------------ UI
    def _build_ui(self, title: str, meta_text: str, id_text: str) -> None:
        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # Card background
        self._card = QFrame(self)
        self._card.setObjectName("CardBackground")
        card_layout = QHBoxLayout(self._card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(16)

        # Left stripe
        stripe = QFrame(self._card)
        stripe.setObjectName("AccentStripe")
        stripe.setFixedWidth(6)
        card_layout.addWidget(stripe)

        # Icon/logo
        logo_wrapper = QFrame(self._card)
        logo_layout = QVBoxLayout(logo_wrapper)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.icon_label = QLabel(logo_wrapper)
        self.icon_label.setObjectName("EntityLogo")
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

        # Texts
        info_wrapper = QFrame(self._card)
        info_layout = QVBoxLayout(info_wrapper)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        self.title_label = QLabel(title, info_wrapper)
        self.title_label.setObjectName("EntityTitle")

        self.meta_label = QLabel(meta_text, info_wrapper)
        self.meta_label.setObjectName("EntityMeta")

        self.id_label = QLabel(id_text, info_wrapper)
        self.id_label.setObjectName("EntityId")

        # Hide empty rows to keep spacing clean
        self.meta_label.setVisible(bool(meta_text))
        self.id_label.setVisible(bool(id_text))

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.meta_label)
        info_layout.addWidget(self.id_label)

        card_layout.addWidget(info_wrapper, stretch=1)

        # Right container with buttons
        right_container = QFrame(self._card)
        right_container.setObjectName("RightContainer")
        right_layout = QHBoxLayout(right_container)
        right_layout.setContentsMargins(24, 8, 8, 8)
        right_layout.setSpacing(12)

        self._btn_widgets: dict[str, QPushButton] = {}

        for spec in self._buttons:
            btn = QPushButton(right_container)
            btn.setObjectName(spec.qss_object)

            if spec.text is not None:
                btn.setText(spec.text)

            if spec.fixed_size:
                btn.setFixedSize(*spec.fixed_size)

            if spec.tooltip:
                btn.setToolTip(spec.tooltip)

            btn.setEnabled(spec.enabled)
            btn.clicked.connect(lambda _=False, a=spec.action: self.action_clicked.emit(self._entity_id, a))

            right_layout.addWidget(btn)
            self._btn_widgets[spec.action] = btn

        card_layout.addWidget(right_container)
        outer.addWidget(self._card)

    # ------------------------------------------------------------------ Style
    def _apply_style(self) -> None:
        self.setStyleSheet(
            f"""
            #EntityCard {{
                background-color: transparent;
            }}

            #CardBackground {{
                background-color: #2A2D34;
                border-radius: 18px;
            }}

            #CardBackground[hover="true"] {{
                background-color: #343844;
            }}

            #AccentStripe {{
                background-color: {self._accent_color};
                border-radius: 3px;
            }}

            #EntityLogo {{
                background-color: transparent;
            }}

            #EntityTitle {{
                color: #FFFFFF;
                font-size: 16px;
                font-weight: 600;
            }}

            #EntityMeta {{
                color: #B0B3C0;
                font-size: 13px;
            }}

            #EntityId {{
                color: #6E7280;
                font-size: 12px;
            }}

            #RightContainer {{
                background-color: #33363F;
                border-radius: 16px;
            }}

            /* Generic button baseline */
            QPushButton#CardButton {{
                background-color: transparent;
                border-radius: 18px;
                padding: 4px 18px;
                font-size: 13px;
            }}

            /* A “primary outlined” style */
            QPushButton#PrimaryButton {{
                background-color: transparent;
                color: #C9B8FF;
                border: 2px solid #7B61FF;
                border-radius: 18px;
                padding: 4px 18px;
                font-size: 13px;
            }}
            QPushButton#PrimaryButton:hover {{
                background-color: rgba(123, 97, 255, 0.15);
            }}

            /* Icon-only round button */
            QPushButton#IconButton {{
                background-color: transparent;
                border-radius: 20px;
                border: none;
                color: #9DA0AE;
                font-size: 20px;
                min-width: 40px;
                min-height: 40px;
            }}
            QPushButton#IconButton:hover {{
                background-color: rgba(255, 255, 255, 0.06);
            }}

            /* Destructive icon-only */
            QPushButton#DangerIconButton {{
                background-color: #FF4E6A;
                border-radius: 20px;
                border: none;
                color: #FFFFFF;
                font-size: 18px;
                min-width: 40px;
                min-height: 40px;
            }}
            QPushButton#DangerIconButton:hover {{
                background-color: #FF3355;
            }}
            """
        )

    # ------------------------------------------------------------------ Helpers
    def set_logo(self, path: str) -> None:
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
        self._accent_color = color
        self._apply_style()

    def button(self, action: str) -> QPushButton | None:
        """Access a button widget for further customization (setIcon, etc.)."""
        return self._btn_widgets.get(action)
