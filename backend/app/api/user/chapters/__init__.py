"""
LernsystemX Chapter Theory API Package

DDD-organized chapter theory operations.

Packages:
    - admin: Admin-only operations (generation, management, media)
    - user: User-facing read-only operations
    - core: Domain logic (repository, factory)

Structure:
    admin/
        ├── generation.py       ~226 LOC  - KI theory generation
        ├── templates.py        ~237 LOC  - Style-specific prompts
        ├── management.py       ~137 LOC  - Admin CRUD operations
        └── media.py            ~240 LOC  - TTS audio generation
    user/
        └── read.py             ~226 LOC  - User read operations
    core/
        ├── repository.py       ~277 LOC  - Database access
        └── factory.py          ~140 LOC  - DDD Factory Pattern

Route Registration:
    All routes are registered on api_v1 blueprint.
    Final URLs: /api/v1/chapters/..., /api/v1/chapter-theory/...

DDD Refactored: 2026-01-08
Per Developer-Guide-KI DDD Pattern and ISO/IEC 26515
Original: generation/ (447 LOC), management/ (339 LOC), media/ (240 LOC)
Total: 1026 LOC → 1483 LOC (with factory and improved organization)
"""

# Admin operations
from .admin import (
    chapter_theory_gen_bp,
    generate_theory_content,
    parse_json_response,
    get_theory_prompts,
    chapter_theory_admin_management_bp,
    chapter_theory_audio_bp,
    generate_theory_audio,
)

# User operations
from .user import chapter_theory_user_read_bp

# Core domain logic
from .core import (
    get_chapter_theory,
    get_chapter_theory_by_id,
    list_chapter_theories,
    save_chapter_theory,
    update_chapter_theory_title,
    delete_chapter_theory_by_id,
    delete_chapter_theory_by_style,
    get_chapter_info,
    get_chapter_lessons,
    get_fallback_theory,
    TheoryFactory,
)

# All blueprints in this package
ALL_BLUEPRINTS = [
    chapter_theory_gen_bp,              # Admin: Generation
    chapter_theory_admin_management_bp, # Admin: Management
    chapter_theory_audio_bp,            # Admin: Audio
    chapter_theory_user_read_bp,        # User: Read operations
]

# Register all sub-blueprints on api_v1 (nested blueprint pattern)
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)

# Backward compatibility exports
# Legacy imports from old structure remain functional
__all__ = [
    # Blueprints
    'chapter_theory_gen_bp',
    'chapter_theory_admin_management_bp',
    'chapter_theory_audio_bp',
    'chapter_theory_user_read_bp',
    'ALL_BLUEPRINTS',
    # Repository functions (backward compatibility)
    'get_chapter_theory',
    'get_chapter_theory_by_id',
    'list_chapter_theories',
    'save_chapter_theory',
    'update_chapter_theory_title',
    'delete_chapter_theory_by_id',
    'delete_chapter_theory_by_style',
    'get_chapter_info',
    'get_chapter_lessons',
    'get_fallback_theory',
    # Generation functions
    'generate_theory_content',
    'get_theory_prompts',
    'parse_json_response',
    # Audio functions
    'generate_theory_audio',
    # Factory
    'TheoryFactory',
]
