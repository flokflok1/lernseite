"""
Prompts System API Package

Feature-based structure (flattened from admin/core structure):
- admin_crud.py: Prompt CRUD operations (101 LOC)
  - From admin/crud.py

- admin_actions.py: Prompt actions (106 LOC)
  - From admin/actions.py

- admin_categories.py: Prompt categories management (151 LOC)
  - From admin/categories.py

- value_objects.py: Prompt value objects (85 LOC)
  - From core/value_objects.py

Total: 443 LOC across 4 feature files

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

# Import endpoint modules
from app.api.v1.prompts_system import (
    admin_crud,
    admin_actions,
    admin_categories
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
    'admin_crud',
    'admin_actions',
    'admin_categories',
    'value_objects',
    'prompts_crud_bp',
    'prompts_actions_bp',
    'prompts_categories_bp',
    'ALL_BLUEPRINTS'
]
