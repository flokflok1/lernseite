"""AI Jobs Management

Job creation, management, and finalization for AI operations.

Blueprints:
- jobs_creation_bp: Job creation
- jobs_management_bp: Job management
- jobs_finalization_bp: Job finalization

Part of: Phase 2 AI Consolidation
"""

from app.api.v1.panel.admin.ai.jobs import creation, management, finalization

__all__ = ['creation', 'management', 'finalization']
