from __future__ import annotations
from typing import Any, Callable, Iterable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QScrollArea, QFrame

class CardListPage(QWidget):
    back_requested = pyqtSignal()
    action = pyqtSignal(str, str, object)  # (entity_id, action, item)

    def __init__(
        self,
        *,
        make_card: Callable[[Any], QWidget],   # <-- key: project vs sequence renderer
        show_back: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._make_card = make_card

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)

        # self.back_btn = QPushButton("← Back")
        # self.back_btn.setVisible(show_back)
        # self.back_btn.clicked.connect(self.back_requested.emit)
        # root.addWidget(self.back_btn)

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.host = QWidget()
        self.list_layout = QVBoxLayout(self.host)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(12)

        self.scroll.setWidget(self.host)
        root.addWidget(self.scroll, stretch=1)

        self.scroll.setObjectName("CardScroll")
        self.host.setObjectName("CardScrollHost")

        self.scroll.setAutoFillBackground(False)
        self.host.setAutoFillBackground(False)

    def set_items(self, items: Iterable[Any]) -> None:
        # clear
        while self.list_layout.count():
            it = self.list_layout.takeAt(0)
            w = it.widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        # render
        for obj in items:
            card = self._make_card(obj)

            # assumes card is EntityCard (has action_clicked)
            if hasattr(card, "action_clicked"):
                card.action_clicked.connect(lambda eid, act, o=obj: self.action.emit(eid, act, o))

            self.list_layout.addWidget(card)

        self.list_layout.addStretch(1)
