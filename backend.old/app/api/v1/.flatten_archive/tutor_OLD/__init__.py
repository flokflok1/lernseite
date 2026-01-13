"""
Tutor System Feature (DDD)

AI Tutor companion with context-aware chat, content generation, and TTS.

Package Structure:
- core/ - Core domain (Value Objects, Factories, Services, Events)
- admin/ - Admin endpoints (Chapter Theory, Lesson Explanation)
- user/ - User endpoints (Chat, TTS)

Blueprints:
- tutor_chapter_theory_bp: /api/v1/admin/ai/generate-chapter-theory
- tutor_lesson_explanation_bp: /api/v1/admin/ai/generate-lesson-steps, generate-lesson-detailed
- tutor_user_chat_bp: /api/v1/tutor/chat
- tutor_user_tts_bp: /api/v1/tutor/tts, /voices

DDD Components:
- Value Objects: GenerationStyle, TutorContext, TTSVoice
- Factories: TutorSessionFactory, TutorGenerationFactory
- Services: TutorKnowledgeService, TutorResponseService, TutorStyleService
- Events: TutorSessionStartedEvent, ChapterTheoryGeneratedEvent, LessonExplanationGeneratedEvent
"""

# Admin blueprints
from .admin import (
    tutor_chapter_theory_bp,
    tutor_lesson_explanation_bp
)

# User blueprints
from .user import (
    tutor_user_chat_bp,
    tutor_user_tts_bp
)

# Core domain exports (for internal use)
from .core import (
    GenerationStyle,
    TutorContext,
    TTSVoice,
    AVAILABLE_VOICES,
    TutorSessionFactory,
    TutorGenerationFactory,
    TutorKnowledgeService,
    TutorResponseService,
    TutorStyleService
)

__all__ = [
    # Admin Blueprints
    'tutor_chapter_theory_bp',
    'tutor_lesson_explanation_bp',
    # User Blueprints
    'tutor_user_chat_bp',
    'tutor_user_tts_bp',
    # Core Domain (exported for internal use)
    'GenerationStyle',
    'TutorContext',
    'TTSVoice',
    'AVAILABLE_VOICES',
    'TutorSessionFactory',
    'TutorGenerationFactory',
    'TutorKnowledgeService',
    'TutorResponseService',
    'TutorStyleService'
]
