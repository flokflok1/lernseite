"""AI Models Management

CRUD operations, defaults, synchronization, and usage tracking for AI models.

Blueprints:
- models_crud_bp: Model CRUD operations
- models_defaults_bp: Default model configuration
- models_sync_bp: Model synchronization
- models_usage_bp: Model usage tracking

Part of: Phase 2 AI Consolidation
"""

from app.api.v1.panel.admin.ai.models import crud, defaults, sync, usage

__all__ = ['crud', 'defaults', 'sync', 'usage']
