"""
Prompts System API Package

AI prompt template management with categories and actions.

Structure:
- admin/ - Admin prompt management (CRUD, actions, categories)
- blueprints.py - Blueprint definitions
- value_objects.py - Domain value objects

Consolidated from: prompts_system/ root admin_* files (Batch 5, Phase 7)
Previously flattened from: admin/prompts/

Endpoints (Admin - @permission_required):
- GET/POST/PUT/DELETE /prompts - Prompt CRUD operations
- POST /prompts/:id/activate - Activate prompt
- POST /prompts/:id/test - Test prompt
- GET/POST /prompts/categories - Category management

All routes: /api/v1/prompts/*
"""

# Import blueprints first to avoid circular imports
from app.api.v1.prompts_system.blueprints import (
    prompts_crud_bp,
    prompts_actions_bp,
    prompts_categories_bp
)

# Import domain logic
from app.api.v1.prompts_system import value_objects

# Import endpoint modules from admin subdirectory
from app.api.v1.prompts_system.admin import (
    crud,
    actions,
    categories
)

# All blueprints to register
ALL_BLUEPRINTS = [
    prompts_crud_bp,
    prompts_actions_bp,
    prompts_categories_bp
]

# Register all blueprints to api_v1
from app.api.v1 import api_v1
for bp in ALL_BLUEPRINTS:
    api_v1.register_blueprint(bp)

__all__ = [
    'crud',
    'actions',
    'categories',
    'value_objects',
    'prompts_crud_bp',
    'prompts_actions_bp',
    'prompts_categories_bp',
    'ALL_BLUEPRINTS'
]
