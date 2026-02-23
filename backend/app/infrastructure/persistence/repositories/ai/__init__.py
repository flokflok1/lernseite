"""
AI Repository Package

AI-related repositories for pipeline management:
- jobs.py: AI job execution and tracking
- profiles.py: AI model profile management
- providers.py: AI provider configuration
- editor.py: AI Editor operations
- content_plans.py: AI Content Plan management
- generation_log.py: AI Generation history

Example usage:
    >>> from app.infrastructure.persistence.repositories.ai.jobs import AIJobRepository
    >>> job = AIJobRepository.find_by_id(job_id)
"""

from app.infrastructure.persistence.repositories.ai.jobs import AIJobRepository
from app.infrastructure.persistence.repositories.ai.profiles import AiModelProfilesRepository
from app.infrastructure.persistence.repositories.ai.providers import AIProviderRepository
from app.infrastructure.persistence.repositories.ai.editor import AIEditorRepository
from app.infrastructure.persistence.repositories.ai.usage import AIUsageRepository
from app.infrastructure.persistence.repositories.ai.exam_context import ExamContextRepository
from app.infrastructure.persistence.repositories.ai.content_plans import ContentPlanRepository
from app.infrastructure.persistence.repositories.ai.generation_log import GenerationLogRepository

__all__ = [
    'AIJobRepository',
    'AiModelProfilesRepository',
    'AIProviderRepository',
    'AIEditorRepository',
    'AIUsageRepository',
    'ExamContextRepository',
    'ContentPlanRepository',
    'GenerationLogRepository',
]
