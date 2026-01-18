"""
AI Repository Package

AI-related repositories for pipeline management:
- jobs.py: AI job execution and tracking
- profiles.py: AI model profile management
- providers.py: AI provider configuration
- editor.py: AI Editor operations

Example usage:
    >>> from app.infrastructure.persistence.repositories.ai.jobs import AIJobRepository
    >>> job = AIJobRepository.find_by_id(job_id)
"""

from app.infrastructure.persistence.repositories.ai.jobs import AIJobRepository
from app.infrastructure.persistence.repositories.ai.profiles import AiModelProfilesRepository
from app.infrastructure.persistence.repositories.ai.providers import AIProviderRepository
from app.infrastructure.persistence.repositories.ai.editor import AIEditorRepository
from app.infrastructure.persistence.repositories.ai.usage import AIUsageRepository

__all__ = [
    'AIJobRepository',
    'AiModelProfilesRepository',
    'AIProviderRepository',
    'AIEditorRepository',
    'AIUsageRepository',
]
