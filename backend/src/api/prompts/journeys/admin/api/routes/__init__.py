"""Prompts Domain - Admin Journey Routes"""

from .crud import prompts_crud_bp
from .categories import prompts_categories_bp
from .actions import prompts_actions_bp

__all__ = [
    'prompts_crud_bp',
    'prompts_categories_bp',
    'prompts_actions_bp',
]
