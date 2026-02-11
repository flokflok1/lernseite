"""
Learning Methods API Package

Learning method type management, catalog, and content-specific implementations.

Structure:
- public/ - Public-facing learning method endpoints (core, catalog, chapters, explanations, videos)
- admin/ - Admin learning method endpoints (schema endpoint for dynamic forms)

Consolidated from: learning_methods/ root + learning-methods/admin/ (Batch 5, Phase 7)

Endpoints (Public - No Auth):
- GET /learning-methods - List all methods
- GET /learning-methods/:id - Get method details
- GET /learning-methods/catalog - Browse catalog
- GET /chapter-theory - Chapter theory content
- GET /lesson-explanations - Lesson explanations
- GET /lesson-videos - Lesson videos

Endpoints (Admin - Auth Required):
- POST/PUT/DELETE /learning-methods - CRUD operations
- GET /admin-panel/learning-methods/:code/schema - UI schema for forms

ISO 27001:2013 compliant - AI execution security
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from app.api.v1.learning_methods.public.core import learning_methods_bp
from app.api.v1.learning_methods.public.chapters import chapter_theory_bp
from app.api.v1.learning_methods.public.explanations import lesson_explanations_bp
from app.api.v1.learning_methods.public.videos import lesson_videos_bp
from app.api.v1.learning_methods.public.catalog import catalog_bp as learning_methods_catalog_bp

__all__ = [
    'learning_methods_bp',
    'chapter_theory_bp',
    'lesson_explanations_bp',
    'lesson_videos_bp',
    'learning_methods_catalog_bp'
]
