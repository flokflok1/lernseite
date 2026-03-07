"""
LernsystemX AI Model Sync Service

Provides sync status queries. Actual model synchronization is performed
by the admin API endpoint (api/v1/panel/admin/ai/models/sync.py) which
calls provider APIs directly.

Model data (including pricing) lives exclusively in the database.
Pricing is managed in the Admin Panel — never overwritten by sync.

Phase KI-Architektur - Model Management
"""

import logging
from typing import Dict, Any

from app.infrastructure.persistence.repositories.ai_models import AIModelsRepository
from app.application.services.ai.models.sync_part2 import AIModelSyncHelpers

logger = logging.getLogger(__name__)


class AIModelSyncService(AIModelSyncHelpers):
    """
    Service for AI model sync status and helper utilities.

    Model data lives exclusively in the database (Single Source of Truth).
    The actual sync is triggered via the admin API endpoint which fetches
    from provider APIs and uses AISyncService for business rules.
    """

    @classmethod
    def get_sync_status(cls) -> Dict[str, Any]:
        """Get current sync status and stats."""
        stats = AIModelsRepository.get_stats()
        categories = AIModelsRepository.get_categories()

        return {
            'stats': stats,
            'categories': categories,
        }
