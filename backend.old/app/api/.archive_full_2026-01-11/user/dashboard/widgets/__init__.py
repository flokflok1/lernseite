"""
LernsystemX Dashboard Widgets Package

Widget management endpoints refactored from monolithic widgets.py (440 lines).

Modules:
    - models: Pydantic request models (AddWidget, UpdatePosition, UpdateSettings)
    - registry: Get available widgets for user's role
    - instances: CRUD operations for user widget instances

Structure:
    models.py      ~35 lines   - Pydantic models
    registry.py    ~70 lines   - GET /widgets (available widgets)
    instances.py   ~360 lines  - CRUD: /user, /add, /{id}, /{id}/position, /{id}/settings, /{id}/toggle

Endpoints:
- GET    /api/v1/dashboard/widgets       - Get available widgets for role
- GET    /api/v1/dashboard/widgets/user  - Get user's widget instances
- POST   /api/v1/dashboard/widgets/add   - Add widget to dashboard
- DELETE /api/v1/dashboard/widgets/{id}  - Remove widget
- PATCH  /api/v1/dashboard/widgets/{id}/position - Update position (Drag & Drop)
- PATCH  /api/v1/dashboard/widgets/{id}/settings - Update settings
- PATCH  /api/v1/dashboard/widgets/{id}/toggle   - Toggle visibility

ISO 27001:2013 compliant - Widget management system
Refactored: 2026-01-08 per Developer-Guide-KI Section 10
"""

from .registry import widgets_registry_bp
from .instances import widgets_instances_bp
from .models import AddWidgetRequest, UpdatePositionRequest, UpdateSettingsRequest

# All blueprints in this package
ALL_BLUEPRINTS = [
    widgets_registry_bp,
    widgets_instances_bp,
]

# Export all blueprints and models for direct import
__all__ = [
    # Blueprints
    'widgets_registry_bp',
    'widgets_instances_bp',
    'ALL_BLUEPRINTS',
    # Models
    'AddWidgetRequest',
    'UpdatePositionRequest',
    'UpdateSettingsRequest',
]
