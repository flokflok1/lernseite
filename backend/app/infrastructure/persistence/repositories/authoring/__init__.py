"""
Authoring Repository Package (Kurs Studio)

Modular authoring repositories for AI-powered course creation:
- analysis.py: Multi-file AI analysis and exam pattern recognition
- changes.py: Change tracking for edit mode (Undo/Redo)
- decision_explanations.py: AI transparency and alternatives
- dialog_messages.py: Structured chat history
- files.py: Multi-file upload system
- finalization.py: Merge strategies and conflict resolution
- generations.py: Long-running AI content generation jobs
- milestones.py: Gamification and achievements
- plan_versions.py: Plan versioning with approval workflow
- refinements.py: Collaborative refinement dialog
- user_journey.py: Progressive disclosure UX tracking

All repositories follow BaseRepository pattern with type hints and docstrings.

Example usage:
    >>> from app.infrastructure.persistence.repositories.authoring.changes import AuthoringChangesRepository
    >>> change_id = AuthoringChangesRepository.create_change(...)

For backward compatibility, legacy imports still work via bridge modules.
"""

from app.infrastructure.persistence.repositories.authoring.content.analysis import AuthoringAnalysisRepository
from app.infrastructure.persistence.repositories.authoring.content.changes import AuthoringChangesRepository
from app.infrastructure.persistence.repositories.authoring.decision_explanations import AIDecisionExplanationsRepository
from app.infrastructure.persistence.repositories.authoring.dialog_messages import AuthoringDialogMessagesRepository
from app.infrastructure.persistence.repositories.authoring.files import AuthoringFilesRepository
from app.infrastructure.persistence.repositories.authoring.sessions.finalization import AuthoringFinalizationRepository
from app.infrastructure.persistence.repositories.authoring.content.generations import AuthoringGenerationsRepository
from app.infrastructure.persistence.repositories.authoring.sessions.milestones import AuthoringMilestonesRepository
from app.infrastructure.persistence.repositories.authoring.sessions.plan_versions import AuthoringPlanVersionsRepository
from app.infrastructure.persistence.repositories.authoring.content.refinements import AuthoringRefinementsRepository
from app.infrastructure.persistence.repositories.authoring.sessions.user_journey import AuthoringUserJourneyRepository
from app.infrastructure.persistence.repositories.authoring.sessions.sessions import CourseAuthoringSessionRepository

__all__ = [
    'AuthoringAnalysisRepository',
    'AuthoringChangesRepository',
    'AIDecisionExplanationsRepository',
    'AuthoringDialogMessagesRepository',
    'AuthoringFilesRepository',
    'AuthoringFinalizationRepository',
    'AuthoringGenerationsRepository',
    'AuthoringMilestonesRepository',
    'AuthoringPlanVersionsRepository',
    'AuthoringRefinementsRepository',
    'AuthoringUserJourneyRepository',
    'CourseAuthoringSessionRepository',
]
