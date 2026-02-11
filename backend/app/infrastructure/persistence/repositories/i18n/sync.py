"""
i18n Sync Repository Aggregator

Re-exports i18n sync-related repository classes and models for convenient importing.
Maintains backward compatibility with existing import paths.

This module acts as a facade over the individual i18n_sync modules:
- i18n_sync_repository.py - Main sync repository (I18nSyncRepository)
- i18n_sync_ops.py - Sync operations (SyncOpsRepository, SyncOperation, etc.)
- i18n_sync_changes.py - Change detection (SyncChangesRepository, SyncChange, etc.)
- i18n_sync_resolutions.py - Resolution management (SyncResolutionsRepository, etc.)

Implements Repository Pattern with direct SQL + psycopg3 (NO ORM).
"""

# Import main repository
from .sync_repository import I18nSyncRepository

# Alias for backward compatibility with code expecting SyncRepository
SyncRepository = I18nSyncRepository

# Import operation classes and repositories
from .sync_ops import (
    SyncMode,
    SyncStatus,
    SyncOperation,
    SyncOpsRepository,
)

# Import change detection classes and repositories
from .sync_changes import (
    ChangeType,
    SyncChange,
    SyncChangesRepository,
)

# Import resolution classes and repositories
from .sync_resolutions import (
    Resolution,
    SyncResolution,
    SyncResolutionsRepository,
)

__all__ = [
    # Main repository (aliased for backward compatibility)
    'SyncRepository',
    'I18nSyncRepository',

    # Operation classes
    'SyncMode',
    'SyncStatus',
    'SyncOperation',
    'SyncOpsRepository',

    # Change detection classes
    'ChangeType',
    'SyncChange',
    'SyncChangesRepository',

    # Resolution classes
    'Resolution',
    'SyncResolution',
    'SyncResolutionsRepository',
]
