"""Resolve AI model for a specific task category.

Used by all services to get their task-specific model instead of
using the global default. Falls back to global default if no
task-specific configuration exists.
"""
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

# Cache to avoid DB lookups on every request
_cache: dict = {}


def resolve_model_for_task(category: str) -> Tuple[str, str]:
    """Resolve (provider, model) for a task category.

    Args:
        category: Task category (grading, vision, content, etc.)

    Returns:
        Tuple of (provider_name, model_name)
    """
    if category in _cache:
        return _cache[category]

    from app.infrastructure.persistence.repositories.ai.task_defaults import (
        AITaskDefaultsRepository,
    )

    row = AITaskDefaultsRepository.get_for_task(category)
    if row:
        result = (row['provider_name'], row['model_name'])
        _cache[category] = result
        return result

    # Ultimate fallback — resolve from global default model in DB
    logger.warning("No task default for '%s', using global default", category)
    try:
        from app.infrastructure.persistence.repositories.ai_models import (
            AIModelsRepository,
        )
        default_model = AIModelsRepository.get_default_model()
        if default_model:
            result = (
                default_model.get('provider_name', 'google'),
                default_model.get('model_name', 'gemini-3.1-pro-preview'),
            )
            _cache[category] = result
            return result
    except Exception:
        logger.exception("Failed to resolve global default model")

    # Absolute last resort
    return ('google', 'gemini-3.1-pro-preview')


def clear_cache() -> None:
    """Clear the resolution cache (call after settings change)."""
    _cache.clear()
