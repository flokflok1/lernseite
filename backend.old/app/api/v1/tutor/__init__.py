"""
Tutor API Package

Feature-based structure (flattened from admin/core/user structure):
- admin_chapter_theory_generation.py: Chapter theory generation (233 LOC)
  - From admin/chapter_theory/generation.py

- admin_lesson_explanation_generation.py: Lesson explanation generation (153 LOC)
  - From admin/lesson_explanation/generation.py

- events.py: Tutor events (69 LOC)
  - From core/events.py

- value_objects.py: Value object definitions (172 LOC)
  - From core/value_objects.py

- factory.py: Tutor factory (242 LOC)
  - From core/factory.py

- services.py: Tutor services (292 LOC)
  - From core/services.py

- user_chat.py: User tutor chat (182 LOC)
  - From user/chat.py

- user_tts.py: User text-to-speech (140 LOC)
  - From user/tts.py

Total: 1483 LOC across 8 feature files

All routes: /api/v1/tutor/*
"""

# Import blueprints first to avoid circular imports
from app.api.v1.tutor.blueprints import (
    tutor_chapter_theory_bp,
    tutor_lesson_explanation_bp,
    tutor_user_chat_bp,
    tutor_user_tts_bp
)

# Import domain logic (factory, services, value_objects, events)
from app.api.v1.tutor import factory, services, value_objects, events

# Import endpoint modules
from app.api.v1.tutor import (
    admin_chapter_theory_generation,
    admin_lesson_explanation_generation,
    user_chat,
    user_tts
)

# All blueprints to register
ALL_BLUEPRINTS = [
    tutor_chapter_theory_bp,
    tutor_lesson_explanation_bp,
    tutor_user_chat_bp,
    tutor_user_tts_bp
]

# Register all blueprints to api_v1
from app.api import api_v1

for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)

__all__ = [
    # Blueprints
    'tutor_chapter_theory_bp',
    'tutor_lesson_explanation_bp',
    'tutor_user_chat_bp',
    'tutor_user_tts_bp',
    'ALL_BLUEPRINTS',
    # Modules
    'admin_chapter_theory_generation',
    'admin_lesson_explanation_generation',
    'events',
    'value_objects',
    'factory',
    'services',
    'user_chat',
    'user_tts'
]
