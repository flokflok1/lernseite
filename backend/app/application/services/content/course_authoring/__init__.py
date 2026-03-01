"""
LernsystemX Course Authoring Service Package

Chat-basiertes Kurs-Authoring mit persistenten Sessions.
Ermöglicht:
- Kursstruktur über Chat erstellen/bearbeiten
- Kapitel, Lektionen, Lernmethoden generieren
- Draft-Structure mit Patch-Operationen
- Finalize um echte DB-Entities zu erstellen

Integration:
- Nutzt AIAdapter für KI-Calls
- Nutzt bestehenden AuthoringService für Content-Generation
- Speichert Sessions in course_authoring_sessions Tabelle
"""

from app.application.services.content.course_authoring.session.session import (
    CourseAuthoringSession,
    CourseAuthoringService,
)
from app.application.services.content.course_authoring.exceptions import CourseAuthoringError
from app.application.services.content.course_authoring.generation.tool_processor import ToolCallProcessor
from app.application.services.content.course_authoring.validation.scope_guard import ScopeGuard
from app.application.services.content.course_authoring.quality_profile import (
    QualityProfile,
    get_quality_profile,
    list_quality_levels,
)
from app.application.services.content.course_authoring.session.token_budget import TokenBudget
from app.application.services.content.course_authoring.validation.content_validator import ContentValidator
from app.application.services.content.course_authoring.generation.pipeline import GenerationPipeline

__all__ = [
    "CourseAuthoringService",
    "CourseAuthoringSession",
    "CourseAuthoringError",
    "ToolCallProcessor",
    "ScopeGuard",
    "QualityProfile",
    "get_quality_profile",
    "list_quality_levels",
    "TokenBudget",
    "ContentValidator",
    "GenerationPipeline",
]


def get_course_authoring_service(
    provider: str = None,
    model: str = None
) -> CourseAuthoringService:
    """Get course authoring service instance. Resolves default model from DB if not specified."""
    return CourseAuthoringService(provider=provider, model=model)
