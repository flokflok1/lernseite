"""
AI Repository Package

AI-related repositories for pipeline management:
- jobs.py: AI job execution and tracking
- profiles.py: AI model profile management
- providers.py: AI provider configuration
- studio.py: AI Studio operations

Example usage:
    >>> from app.repositories.ai.jobs import AIJobRepository
    >>> job = AIJobRepository.find_by_id(job_id)
"""

from app.repositories.ai.jobs import AIJobRepository
from app.repositories.ai.profiles import AiModelProfilesRepository
from app.repositories.ai.providers import AIProviderRepository
from app.repositories.ai.studio import AIStudioRepository

__all__ = [
    'AIJobRepository',
    'AiModelProfilesRepository',
    'AIProviderRepository',
    'AIStudioRepository',
]
