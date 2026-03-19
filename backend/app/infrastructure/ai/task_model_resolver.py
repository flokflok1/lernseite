"""Resolve AI model for a specific task category.

Used by all services to get their task-specific model.
All categories must be configured in ai_pipeline.ai_task_defaults.
No hardcoded fallbacks — if config is missing, it's a setup error.
"""
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

_cache: dict = {}


def resolve_model_for_task(category: str) -> Tuple[str, str]:
    """Resolve (provider, model) for a task category.

    Reads from ai_pipeline.ai_task_defaults. If the specific category
    is not found, uses the 'default' category. If neither exists,
    raises a clear error — the system must be configured.

    Args:
        category: Task category (grading, vision, content, etc.)

    Returns:
        Tuple of (provider_name, model_name)

    Raises:
        RuntimeError: If no configuration exists for this category
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

    logger.error(
        "No AI model configured for task '%s'. "
        "Configure it in System Settings → KI-Einstellungen.",
        category,
    )
    raise RuntimeError(
        f"No AI model configured for task '{category}'. "
        f"Go to System Settings → KI-Einstellungen to configure."
    )


def clear_cache() -> None:
    """Clear the resolution cache (call after settings change)."""
    _cache.clear()
