import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSplitter, QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont


PROJECT_TYPES = ["Film", "Series", "Short", "Game", "Commercial", "Custom"]


class BreakdownWorker(QThread):
    success = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, pdf_path: str, ctx, parent=None):
        super().__init__(parent)
        self._pdf_path = pdf_path
        self._service = ctx.script_breakdown_service

    def run(self):
        try:
            result = self._service.parse(self._pdf_path)
            self.success.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class SaveProjectWorker(QThread):
    success = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, ctx, name: str, code: str, project_type: str, breakdown, parent=None):
        super().__init__(parent)
        self._ctx = ctx
        self._name = name
        self._code = code
        self._type = project_type
        self._breakdown = breakdown

    def run(self):
        try:
            result = self._ctx.script_breakdown_service.save_project(
                self._name, self._code, self._type, self._breakdown
            )
            self.success.emit(result)
        except Exception as e:
            self.error.emit(str(e))


class ScriptBreakdownPage(QWidget):
    back_requested = pyqtSignal()
    results_ready = pyqtSignal(bool)

    def __init__(self, ctx, parent=None):
        super().__init__(parent)
        self._ctx = ctx
        self._worker = None
        self._save_worker = None
        self._last_result = None
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(16)

        # --- Upload row ---
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

        # --- Project fields row ---
        fields_row = QHBoxLayout()
        fields_row.setSpacing(12)

        self.input_name = QLineEdit()
        self.input_name.setObjectName("BreakdownLineEdit")
        self.input_name.setPlaceholderText("Project Name")
        self.input_name.setFixedHeight(36)
        self.input_name.textChanged.connect(self._check_save_ready)

        self.input_code = QLineEdit()
        self.input_code.setObjectName("BreakdownLineEdit")
        self.input_code.setPlaceholderText("Project Code  (e.g. BLR)")
        self.input_code.setFixedHeight(36)
        self.input_code.setMaxLength(10)
        self.input_code.textChanged.connect(self._check_save_ready)

        self.combo_type = QComboBox()
        self.combo_type.setObjectName("BreakdownComboBox")
        self.combo_type.setFixedHeight(36)
        self.combo_type.addItems(PROJECT_TYPES)
        self.combo_type.currentTextChanged.connect(self._on_type_changed)

        self.input_custom_type = QLineEdit()
        self.input_custom_type.setObjectName("BreakdownLineEdit")
        self.input_custom_type.setPlaceholderText("Enter custom type...")
        self.input_custom_type.setFixedHeight(36)
        self.input_custom_type.setVisible(False)
        self.input_custom_type.textChanged.connect(self._check_save_ready)

        fields_row.addWidget(self.input_name, 2)
        fields_row.addWidget(self.input_code, 1)
        fields_row.addWidget(self.combo_type, 1)
        fields_row.addWidget(self.input_custom_type, 1)
        root.addLayout(fields_row)

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

        char_frame = QFrame()
        char_layout = QVBoxLayout(char_frame)
        char_layout.setContentsMargins(0, 0, 0, 0)
        char_layout.addWidget(self._section_label("👥 Characters"))
        self.char_table = self._make_table(["Character", "Scenes"])
        self.char_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        char_layout.addWidget(self.char_table)
        splitter.addWidget(char_frame)

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

    def _on_type_changed(self, text: str):
        self.input_custom_type.setVisible(text == "Custom")
        self._check_save_ready()

    def _check_save_ready(self):
        """Enable Save only when breakdown has results AND all fields are filled."""
        has_breakdown = (
            self._last_result is not None
            and self._last_result.total_pages > 0
            and self._last_result.total_scenes > 0
            and self._last_result.total_characters > 0
        )
        has_name = bool(self.input_name.text().strip())
        has_code = bool(self.input_code.text().strip())
        type_text = self.combo_type.currentText()
        has_type = (
            bool(self.input_custom_type.text().strip())
            if type_text == "Custom"
            else True
        )
        self.results_ready.emit(has_breakdown and has_name and has_code and has_type)

    def _browse_and_parse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select Script PDF", "", "PDF Files (*.pdf)")
        if not path:
            return

        self.lbl_file.setText(f"📄 {os.path.basename(path)}")
        self.btn_upload.setEnabled(False)
        self.btn_upload.setText("⏳ Processing...")
        self._last_result = None
        self._clear_results()

        self._worker = BreakdownWorker(path, self._ctx, self)
        self._worker.success.connect(self._on_success)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _on_success(self, result):
        self._last_result = result

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

        self._reset_button()
        self._check_save_ready()

    def _on_error(self, msg: str):
        print(f"❌ {msg}")
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
        self.results_ready.emit(False)

    def save(self):
        if not self._last_result:
            return

        name = self.input_name.text().strip()
        code = self.input_code.text().strip().upper()
        type_text = self.combo_type.currentText()
        project_type = (
            self.input_custom_type.text().strip()
            if type_text == "Custom"
            else type_text
        )

        if not name or not code or not project_type:
            self.lbl_status.setText("❌ Please fill in all project fields.")
            return

        self.lbl_status.setText("💾 Saving project...")
        self.btn_upload.setEnabled(False)
        self.results_ready.emit(False)

        self._save_worker = SaveProjectWorker(
            self._ctx, name, code, project_type, self._last_result, self
        )
        self._save_worker.success.connect(self._on_save_success)
        self._save_worker.error.connect(self._on_save_error)
        self._save_worker.start()

    def _on_save_success(self, project):
        self.lbl_status.setText(f"✅ Project '{project.get('name')}' created successfully.")
        self._reset_button()
        # Reset form for a fresh entry
        self.input_name.clear()
        self.input_code.clear()
        self.combo_type.setCurrentIndex(0)
        self.input_custom_type.clear()
        self._last_result = None
        self._clear_results()
        self.lbl_file.setText("No file selected")

    def _on_save_error(self, msg: str):
        self.lbl_status.setText(f"❌ Save failed: {msg}")
        self._reset_button()
        self._check_save_ready()