"""
Prompts Admin Package (DDD)

Admin endpoints for prompt template management.

Endpoints:
- CRUD (list, get, create, update, delete)
- Categories & Styles
- Actions (duplicate, set-default, preview, usage-stats)
"""

from flask import Blueprint

# Define blueprints
prompts_crud_bp = Blueprint(
    'prompts_crud',
    __name__,
    url_prefix='/api/v1/admin/prompts'
)

prompts_categories_bp = Blueprint(
    'prompts_categories',
    __name__,
    url_prefix='/api/v1/admin/prompts'
)

prompts_actions_bp = Blueprint(
    'prompts_actions',
    __name__,
    url_prefix='/api/v1/admin/prompts'
)

# Import routes (registers endpoints with blueprints)
from . import crud, categories, actions

__all__ = [
    'prompts_crud_bp',
    'prompts_categories_bp',
    'prompts_actions_bp'
]
