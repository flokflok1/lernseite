"""
Tutor Core Domain

Domain-Driven Design (DDD) core components for the AI Tutor system.

Components:
- Value Objects: GenerationStyle, TutorContext, TTSVoice
- Factory: TutorSessionFactory, TutorGenerationFactory
- Services: TutorKnowledgeService, TutorResponseService, TutorStyleService
- Events: TutorSessionStartedEvent, TheoryGeneratedEvent, etc.
"""

from .value_objects import GenerationStyle, TutorContext, TTSVoice, AVAILABLE_VOICES
from .factory import TutorSessionFactory, TutorGenerationFactory
from .services import TutorKnowledgeService, TutorResponseService, TutorStyleService

__all__ = [
    # Value Objects
    'GenerationStyle',
    'TutorContext',
    'TTSVoice',
    'AVAILABLE_VOICES',
    # Factories
    'TutorSessionFactory',
    'TutorGenerationFactory',
    # Services
    'TutorKnowledgeService',
    'TutorResponseService',
    'TutorStyleService'
]
