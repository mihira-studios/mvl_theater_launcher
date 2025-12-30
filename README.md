MVL Theater Launcher

enviroment variables need to be set

MVL_DOMAIN  "ip addres"
KC_REALM    "keycloak releam"
KC_CLIENT_ID "keycloak client id"

THEATER_EXECUTABLE "unreal executable for theater"
THEATER_UPROJECT_TEMPLATE "unreal uproject template path"

A desktop launcher application for Unreal Engine–based productions, inspired by the Epic Games Launcher.
Built with Python + PyQt, secured with Keycloak, and backed by FastAPI.

This application provides a unified interface for:

Authentication

Project discovery

Sequence / scene navigation

Launching Unreal Engine projects

🚀 Key Features
✅ Implemented

Keycloak authentication

Secure login screen

Token handling via domain models

Single-window UI architecture

One QMainWindow

Projects dashboard

Custom ProjectCard widgets

Themed to match Epic-style launcher UX

Sequences page

Per-project drill-down

Back navigation without window recreation

Global theming

Centralized QSS (theme.qss)

Service-driven architecture

UI is decoupled from backend logic

Enables UI development without backend dependency

🧠 Architecture Overview
main.py
 └── LoginWindow
      └── MainWindow (single QMainWindow)
           ├── Projects Page
           │    └── ProjectCard widgets
           └── Sequences Page

Design Principles

✅ One window only

✅ Central widget swapping for navigation

✅ Clear separation: UI / Services / Domain

❌ No popup navigation windows

❌ No inline styling

📁 Project Structure
C:.
│   README.md
│
└── python
    │   main.py                  # Launcher entry point
    │
    ├── backend                  # FastAPI backend (local / dev)
    │   │   main.py
    │
    ├── launcher
    │   │   config.py
    │   │   logging_config.py
    │   │
    │   ├── domain               # Core domain models
    │   │   ├── auth_tokens.py   # Keycloak token models
    │   │   ├── project.py       # Project entity
    │   │   └── user.py          # User entity
    │   │
    │   ├── services             # Business & integration logic
    │   │   ├── auth_service.py
    │   │   ├── http_client.py
    │   │   ├── project_service.py
    │   │   ├── launch_service.py
    │   │   └── settings_service.py
    │   │
    │   ├── ui                   # All PyQt UI code
    │   │   ├── app_context.py   # Dependency container
    │   │   ├── login_window.py  # Login screen
    │   │   ├── main_window.py   # Main app window (projects)
    │   │   ├── sequences_page.py# Sequences per project
    │   │   ├── theme.py         # Global theme loader
    │   │
    │   │   ├── resources
    │   │   │   ├── icons        # App & UI icons
    │   │   │   └── qss          # Global QSS theme
    │   │
    │   │   └── widgets
    │   │       ├── project_card.py
    │   │       ├── project_list_widget.py
    │   │       └── loading_overlay.py
    │   │
    │   ├── util                 # Shared utilities
    │   │   ├── helper.py
    │   │   ├── threading.py
    │   │   └── errors.py
    │
    └── test
        ├── login.py
        └── test_project_card.py

🎨 Global Theme

Defined in:

launcher/ui/resources/qss/theme.qss


Applied once at startup:

from launcher.ui.theme import apply_global_theme

app = QApplication(sys.argv)
apply_global_theme(app)


All UI styling relies on objectName-based selectors.

🔐 Authentication

Keycloak used for authentication

Tokens stored in domain/auth_tokens.py

UI communicates via AuthService

Backend verification handled via FastAPI