"""
AI Models Admin Package (DDD)

Endpoints for AI model management using DDD patterns:
- Uses AIModelFactory for creation
- Uses AIModelSelectionService for queries
- Publishes Domain Events on state changes
- Uses Repository Pattern for persistence

Blueprints:
    - models_crud_bp: CRUD operations
    - models_defaults_bp: Default model management
    - models_sync_bp: Provider synchronization
    - models_usage_bp: Usage statistics
"""

from .crud import models_crud_bp
from .defaults import models_defaults_bp
from .sync import models_sync_bp
from .usage import models_usage_bp

__all__ = [
    'models_crud_bp',
    'models_defaults_bp',
    'models_sync_bp',
    'models_usage_bp'
]
