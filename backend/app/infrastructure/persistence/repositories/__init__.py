"""
LernsystemX Repository Package

Implements Repository Pattern for data access layer.
Each repository handles database operations for a specific entity.

ISO 9001:2015 compliant - Data access standardization
"""

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.repositories.user import UserRepository
from app.infrastructure.persistence.repositories.i18n_sync_ops import SyncOpsRepository, SyncMode, SyncStatus, SyncOperation
from app.infrastructure.persistence.repositories.i18n_sync_changes import SyncChangesRepository, ChangeType, SyncChange
from app.infrastructure.persistence.repositories.i18n_sync_resolutions import SyncResolutionsRepository, Resolution, SyncResolution

__all__ = [
    'BaseRepository',
    'UserRepository',
    'SyncOpsRepository',
    'SyncChangesRepository',
    'SyncResolutionsRepository',
    'SyncMode',
    'SyncStatus',
    'SyncOperation',
    'ChangeType',
    'SyncChange',
    'Resolution',
    'SyncResolution'
]
