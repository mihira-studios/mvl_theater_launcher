import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSplitter, QSizePolicy
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

from launcher.services.script_breakdown_service import ScriptBreakdownService


class BreakdownWorker(QThread):
    success = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, pdf_path: str, parent=None):
        super().__init__(parent)
        self._pdf_path = pdf_path
        self._service = ScriptBreakdownService()

    def run(self):
        try:
            result = self._service.parse(self._pdf_path)
            self.success.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ScriptBreakdownPage(QWidget):
    # Signal to notify main_window to go back
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        # --- Upload button ---
        self.btn_upload = QPushButton("⬆  Upload & Breakdown")
        self.btn_upload.setObjectName("PrimaryButton")
        self.btn_upload.setFixedWidth(200)
        self.btn_upload.clicked.connect(self._browse_and_parse)

        self.lbl_file = QLabel("No file selected")
        self.lbl_file.setObjectName("StatusLabelProjects")

        upload_row = QHBoxLayout()
        upload_row.addWidget(self.btn_upload)
        upload_row.addWidget(self.lbl_file)
        upload_row.addStretch()
        root.addLayout(upload_row)

        # --- Status ---
        self.lbl_status = QLabel("")
        self.lbl_status.setObjectName("StatusLabelProjects")
        root.addWidget(self.lbl_status)

        # --- Metrics row ---
        metrics_row = QHBoxLayout()
        self.lbl_pages = self._metric_card("Pages", "-")
        self.lbl_scenes = self._metric_card("Scenes", "-")
        self.lbl_chars = self._metric_card("Characters", "-")
        for card, _ in [self.lbl_pages, self.lbl_scenes, self.lbl_chars]:
            metrics_row.addWidget(card)
        root.addLayout(metrics_row)

        # --- Splitter: characters | scenes ---
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Characters table
        char_frame = QFrame()
        char_layout = QVBoxLayout(char_frame)
        char_layout.setContentsMargins(0, 0, 0, 0)
        char_layout.addWidget(self._section_label("👥 Characters"))
        self.char_table = self._make_table(["Character", "Scenes"])
        self.char_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        char_layout.addWidget(self.char_table)
        splitter.addWidget(char_frame)

        # Scenes table
        scene_frame = QFrame()
        scene_layout = QVBoxLayout(scene_frame)
        scene_layout.setContentsMargins(0, 0, 0, 0)
        scene_layout.addWidget(self._section_label("📽️ Scenes"))
        self.scene_table = self._make_table(["#", "Scene Heading"])
        self.scene_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        scene_layout.addWidget(self.scene_table)
        splitter.addWidget(scene_frame)

        splitter.setSizes([300, 500])
        root.addWidget(splitter)

    # --- Helpers ---

    def _make_table(self, headers: list) -> QTableWidget:
        t = QTableWidget()
        t.setColumnCount(len(headers))
        t.setHorizontalHeaderLabels(headers)
        t.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        t.setAlternatingRowColors(True)
        t.verticalHeader().setVisible(False)
        return t

    def _metric_card(self, label: str, value: str):
        frame = QFrame()
        frame.setObjectName("ProjectsContainer")
        inner = QVBoxLayout(frame)
        inner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val = QLabel(value)
        val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        txt = QLabel(label)
        txt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        inner.addWidget(val)
        inner.addWidget(txt)
        return frame, val

    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        return lbl

    # --- Logic ---

    def _browse_and_parse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Script PDF", "", "PDF Files (*.pdf)")
        if not path:
            return

        self.lbl_file.setText(f"📄 {os.path.basename(path)}")
        self.lbl_status.setText("Sending to backend...")
        self.btn_upload.setEnabled(False)
        self.btn_upload.setText("⏳ Processing...")
        self._clear_results()

        self._worker = BreakdownWorker(path, self)
        self._worker.success.connect(self._on_success)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_success(self, result):
        self.lbl_pages[1].setText(str(result.total_pages))
        self.lbl_scenes[1].setText(str(result.total_scenes))
        self.lbl_chars[1].setText(str(result.total_characters))

        self.char_table.setRowCount(len(result.character_appearances))
        for row, (name, count) in enumerate(result.character_appearances.items()):
            self.char_table.setItem(row, 0, QTableWidgetItem(name))
            item = QTableWidgetItem(str(count))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.char_table.setItem(row, 1, item)

        self.scene_table.setRowCount(len(result.scenes))
        for row, scene in enumerate(result.scenes):
            num = QTableWidgetItem(str(row + 1))
            num.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scene_table.setItem(row, 0, num)
            self.scene_table.setItem(row, 1, QTableWidgetItem(scene))

        self.lbl_status.setText(f"✅ Done — {result.total_scenes} scenes, {result.total_characters} characters.")
        self._reset_button()

    def _on_error(self, msg: str):
        self.lbl_status.setText(f"❌ {msg}")
        self._reset_button()

    def _reset_button(self):
        self.btn_upload.setEnabled(True)
        self.btn_upload.setText("⬆  Upload & Breakdown")

    def _clear_results(self):
        self.lbl_pages[1].setText("-")
        self.lbl_scenes[1].setText("-")
        self.lbl_chars[1].setText("-")
        self.char_table.setRowCount(0)
        self.scene_table.setRowCount(0)