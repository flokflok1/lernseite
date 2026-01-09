"""
LernsystemX Admin API Module

Refactored: 2026-01-08 - ISO/IEC 26515 + DDD compliant
Struktur parallel zu Frontend (components/admin/)

Admin-Bereiche:
├── ai-operations/          # AI-Funktionen (Proxy zu system_features/ai/)
├── content-management/     # Content-Verwaltung (Kurse, Lektionen, Kapitel)
├── assessment/             # Prüfungsverwaltung
├── user-management/        # Benutzerverwaltung (Proxy zu users/admin/)
└── system-operations/      # System-Einstellungen

Total: ~150 endpoints
"""

# AI Operations (Proxies zu system_features/ai/)
try:
    from app.api.admin.ai_operations import (
        authoring_bp,
        generation_bp,
        jobs_bp,
        models_bp,
        pricing_bp,
        profiles_bp,
        studio_bp,
        tutor_bp
    )
except ImportError as e:
    print(f"Warning: AI Operations import failed: {e}")
    authoring_bp = generation_bp = jobs_bp = models_bp = None
    pricing_bp = profiles_bp = studio_bp = tutor_bp = None

# Content Management
try:
    from app.api.admin.content_management import (
        courses_crud,
        chapters,
        lessons,
        exams,
        prompts,
        files
    )
except ImportError as e:
    print(f"Warning: Content Management import failed: {e}")
    courses_crud = chapters = lessons = exams = prompts = files = None

# User Management (Proxies zu users/admin/)
try:
    from app.api.admin.user_management import (
        admin_users_crud_bp,
        admin_users_roles_bp,
        admin_users_actions_bp
    )
except ImportError as e:
    print(f"Warning: User Management import failed: {e}")
    admin_users_crud_bp = admin_users_roles_bp = admin_users_actions_bp = None

# System Operations
try:
    from app.api.admin.system_operations import (
        system_settings_module
    )
except ImportError as e:
    print(f"Warning: System Operations import failed: {e}")
    system_settings_module = None

__all__ = [
    # AI Operations
    'authoring_bp',
    'generation_bp',
    'jobs_bp',
    'models_bp',
    'pricing_bp',
    'profiles_bp',
    'studio_bp',
    'tutor_bp',
    # Content Management
    'courses_crud',
    'chapters',
    'lessons',
    'exams',
    'prompts',
    'files',
    # User Management
    'admin_users_crud_bp',
    'admin_users_roles_bp',
    'admin_users_actions_bp',
    # System Operations
    'system_settings_module',
]
