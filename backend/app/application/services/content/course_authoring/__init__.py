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

from app.application.services.content.course_authoring.session import (
    CourseAuthoringSession,
    CourseAuthoringService,
)
from app.application.services.content.course_authoring.exceptions import CourseAuthoringError

__all__ = [
    "CourseAuthoringService",
    "CourseAuthoringSession",
    "CourseAuthoringError",
]


def get_course_authoring_service(
    provider: str = None,
    model: str = None
) -> CourseAuthoringService:
    """Get course authoring service instance. Resolves default model from DB if not specified."""
    return CourseAuthoringService(provider=provider, model=model)
