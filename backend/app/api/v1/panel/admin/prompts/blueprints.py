"""
Prompts System Blueprints

Centralized blueprint definitions to avoid circular imports.
"""

from flask import Blueprint

# Prompt CRUD Blueprint
prompts_crud_bp = Blueprint(
    'prompts_crud',
    __name__,
    url_prefix='/panel/prompts'
)

# Prompt Actions Blueprint
prompts_actions_bp = Blueprint(
    'prompts_actions',
    __name__,
    url_prefix='/panel/prompts'
)

# Prompt Categories Blueprint
prompts_categories_bp = Blueprint(
    'prompts_categories',
    __name__,
    url_prefix='/panel/prompts'
)
