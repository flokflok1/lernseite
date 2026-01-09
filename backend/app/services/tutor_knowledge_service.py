"""
TutorKnowledgeService - Bridge/Legacy Compatibility Module

DEPRECATED: Use `from app.services.tutor_knowledge import TutorKnowledgeService` instead.

This module provides backward compatibility for existing imports.
All functionality has been refactored into the tutor_knowledge package:
- app.services.tutor_knowledge.context_loader (course, chapter, lesson context)
- app.services.tutor_knowledge.method_loader (learning method data)
- app.services.tutor_knowledge.file_loader (course files)
- app.services.tutor_knowledge.progress_loader (user progress)
- app.services.tutor_knowledge.prompt_builder (tutor context prompt)

Existing code should update imports from:
    from app.services.tutor_knowledge_service import TutorKnowledgeService
To:
    from app.services.tutor_knowledge import TutorKnowledgeService
"""

# Re-export TutorKnowledgeService from the new package
from app.services.tutor_knowledge import TutorKnowledgeService

__all__ = ['TutorKnowledgeService']
