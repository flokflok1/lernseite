"""
Chapters API Package

Feature-based structure (flattened from admin/core/user structure):

**Admin operations:**
- admin_generation.py: Chapter theory KI generation (229 LOC)
  - From admin/generation.py

- admin_management.py: Admin chapter CRUD (142 LOC)
  - From admin/management.py

- admin_media.py: Chapter theory TTS audio (242 LOC)
  - From admin/media.py

- admin_templates.py: Theory generation prompts (239 LOC)
  - From admin/templates.py

**User operations:**
- user_read.py: User read-only chapter operations (231 LOC)
  - From user/read.py

**Core domain logic:**
- factory.py: Chapter factory (DDD pattern) (159 LOC)
  - From core/factory.py

- repository.py: Chapter repository (database access) (279 LOC)
  - From core/repository.py

**Note:** Old generation/, management/, media/ subdirectories were leftovers from
DDD refactoring 2026-01-08 and have been removed during flattening.

Total: 1521 LOC across 7 feature files (down from 2582 LOC with duplicates removed)

All routes: /api/v1/chapters/* and /api/v1/chapter-theory/*
"""

# Admin operations
from app.api.v1.chapters.admin_generation import (
    chapter_theory_gen_bp,
    generate_theory_content,
    parse_json_response,
    get_theory_prompts
)

from app.api.v1.chapters.admin_management import chapter_theory_admin_management_bp

from app.api.v1.chapters.admin_media import (
    chapter_theory_audio_bp,
    generate_theory_audio
)

# User operations
from app.api.v1.chapters.user_read import chapter_theory_user_read_bp

# Core domain logic
from app.api.v1.chapters.repository import (
    get_chapter_theory,
    get_chapter_theory_by_id,
    list_chapter_theories,
    save_chapter_theory,
    update_chapter_theory_title,
    delete_chapter_theory_by_id,
    delete_chapter_theory_by_style,
    get_chapter_info,
    get_chapter_lessons,
    get_fallback_theory
)

from app.api.v1.chapters.factory import TheoryFactory

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
__all__ = [
    # Blueprints
    'chapter_theory_gen_bp',
    'chapter_theory_admin_management_bp',
    'chapter_theory_audio_bp',
    'chapter_theory_user_read_bp',
    'ALL_BLUEPRINTS',
    # Repository functions
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
