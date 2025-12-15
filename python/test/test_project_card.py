import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from launcher.ui.widgets.project_card import ProjectCard  

app = QApplication(sys.argv)

root = QWidget()
layout = QVBoxLayout(root)

card1 = ProjectCard(
    project_id="12345",
    title="Blade Runner",
    scenes_sets_text="Scenes 137, Sets 90",
    id_text="ID 12345",
    accent_color="#4AC0FF",
    icon="app_icon.png",  
)

card2 = ProjectCard(
    project_id="23456",
    title="Eternal Wars ep1",
    scenes_sets_text="Scenes 21, Sets 08",
    id_text="ID 23456",
    accent_color="#FF6A7A",
    icon="app_icon.png",
)

card3 = ProjectCard(
    project_id="34567",
    title="Eternal Wars ep2",
    scenes_sets_text="Scene 12, Sets 22",
    id_text="ID 34567",
    accent_color="#4AC0FF",
    icon="app_icon.png",
)

layout.addWidget(card1)
layout.addWidget(card2)
layout.addWidget(card3)
layout.addStretch()

root.resize(1100, 400)
root.show()

sys.exit(app.exec())
