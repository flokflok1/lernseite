"""
Prompts System Feature (DDD)

Prompt template management for AI content generation.

Package Structure:
- core/ - Core domain (Value Objects)
- admin/ - Admin endpoints (CRUD, Categories, Actions)

Blueprints:
- prompts_crud_bp: /api/v1/admin/prompts (list, get, create, update, delete)
- prompts_categories_bp: /api/v1/admin/prompts/categories, /styles
- prompts_actions_bp: /api/v1/admin/prompts/<id>/duplicate, /set-default

DDD Components:
- Value Objects: PromptCategory, PromptStyle, PromptMetadata

Old Location (to be deleted after migration):
- admin/prompts/ (5 files, ~650 LOC)
"""

# Admin blueprints
from .admin import (
    prompts_crud_bp,
    prompts_categories_bp,
    prompts_actions_bp
)

# Core domain exports (for internal use)
from .core import (
    PromptCategory,
    PromptStyle,
    PromptMetadata
)

__all__ = [
    # Admin Blueprints
    'prompts_crud_bp',
    'prompts_categories_bp',
    'prompts_actions_bp',
    # Core Domain
    'PromptCategory',
    'PromptStyle',
    'PromptMetadata'
]
