"""Prompts Domain - All Journeys"""

from .admin import (
    prompts_crud_bp,
    prompts_categories_bp,
    prompts_actions_bp,
)

ALL_JOURNEY_BLUEPRINTS = [
    prompts_crud_bp,
    prompts_categories_bp,
    prompts_actions_bp,
]

__all__ = ['ALL_JOURNEY_BLUEPRINTS', 'prompts_crud_bp', 'prompts_categories_bp', 'prompts_actions_bp']
