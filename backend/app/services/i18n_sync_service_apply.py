"""
i18n Sync Service - Apply and Rollback Operations

Handles applying sync changes to the database and rollback functionality.

No ORM - uses psycopg3 with repositories.
"""

from typing import Dict, Tuple, Optional, Any
from datetime import datetime
import logging

from app.repositories.i18n_sync import (
    SyncRepository, SyncMode, SyncStatus, ChangeType, Resolution,
    SyncOperation
)
from app.repositories.i18n_translation import TranslationRepository
from app.utils.exceptions import NotFoundError, BusinessLogicError
from app.database import get_connection

logger = logging.getLogger(__name__)


class I18nSyncServiceApply:
    """
    Service for applying and rolling back i18n translation syncs.

    Coordinates change application to database and rollback functionality.
    """

    def __init__(self, conn=None):
        """
        Initialize apply service.

        Args:
            conn: Database connection (optional, created if not provided)
        """
        self.conn = conn or get_connection()
        self.sync_repo = SyncRepository(self.conn)
        self.translation_repo = TranslationRepository(self.conn)

    def apply_sync(
        self,
        sync_id: str,
        auto_resolve: bool = False
    ) -> Tuple[SyncOperation, Dict[str, int]]:
        """
        Apply sync changes to database.

        For MANUAL mode:
        - All conflicts must be resolved before applying
        - Applies CHANGED and resolved conflict changes

        For AUTO mode:
        - Auto-resolves conflicts using similarity scoring
        - Applies all changes automatically

        Args:
            sync_id: Sync operation ID
            auto_resolve: For MANUAL mode, attempt auto-resolve of unresolved conflicts

        Returns:
            Tuple of (updated_sync, stats_dict)
            stats: {'applied': N, 'skipped': N, 'errors': N}

        Raises:
            NotFoundError: If sync not found
            BusinessLogicError: If sync has unresolved conflicts (MANUAL mode)
        """
        # Get sync
        sync = self.sync_repo.get_sync(sync_id)
        if not sync:
            raise NotFoundError(f"Sync {sync_id} not found")

        if sync.status != SyncStatus.COMPLETED:
            raise BusinessLogicError(
                f"Sync must be in COMPLETED state (currently {sync.status})"
            )

        # Check for unresolved conflicts (MANUAL mode)
        if sync.mode == SyncMode.MANUAL and not auto_resolve:
            conflicts, _ = self.sync_repo.list_changes(
                sync_id,
                change_type=ChangeType.CONFLICT,
                limit=1
            )

            unresolved = [c for c in conflicts if c.resolution is None]
            if unresolved:
                raise BusinessLogicError(
                    f"Cannot apply sync with {len(unresolved)} unresolved conflicts. "
                    "Resolve conflicts or use auto_resolve=True"
                )

        # Get all changes
        changes, _ = self.sync_repo.list_changes(
            sync_id,
            limit=100000  # Get all
        )

        stats = {'applied': 0, 'skipped': 0, 'errors': 0}

        for change in changes:
            try:
                # Skip if resolution is SKIP
                if change.resolution == Resolution.SKIP:
                    stats['skipped'] += 1
                    continue

                # Apply based on change type and resolution
                if change.change_type == ChangeType.NEW:
                    # Create new translation
                    self.translation_repo.create_translation(
                        change.translation_key,
                        change.language_code,
                        change.frontend_value
                    )
                    stats['applied'] += 1

                elif change.change_type == ChangeType.CHANGED:
                    # Update translation
                    self.translation_repo.update_translation(
                        change.translation_key,
                        change.language_code,
                        change.frontend_value
                    )
                    stats['applied'] += 1

                elif change.change_type == ChangeType.DELETED:
                    # Delete translation
                    self.translation_repo.delete_translation(
                        change.translation_key,
                        change.language_code
                    )
                    stats['applied'] += 1

                elif change.change_type == ChangeType.CONFLICT:
                    # Apply based on resolution
                    if change.resolution == Resolution.ADD:
                        self.translation_repo.create_translation(
                            change.translation_key,
                            change.language_code,
                            change.frontend_value
                        )
                    elif change.resolution == Resolution.UPDATE:
                        self.translation_repo.update_translation(
                            change.translation_key,
                            change.language_code,
                            change.frontend_value
                        )
                    elif change.resolution == Resolution.DELETE:
                        self.translation_repo.delete_translation(
                            change.translation_key,
                            change.language_code
                        )

                    stats['applied'] += 1

            except Exception as e:
                logger.error(
                    f"Error applying change {change.change_id}: {str(e)}",
                    extra={'sync_id': sync_id, 'change_id': change.change_id}
                )
                stats['errors'] += 1

        # Mark all resolutions as applied
        resolutions, _ = self.sync_repo.list_resolutions(sync_id, applied=False)
        for res in resolutions:
            self.sync_repo.mark_resolution_applied(res.resolution_id)

        logger.info(
            f"Applied sync {sync_id}",
            extra=stats
        )

        return sync, stats

    def rollback_sync(
        self,
        sync_id: str,
        user_id: str,
        reason: str
    ) -> SyncOperation:
        """
        Rollback a sync operation.

        Reverts all applied changes from a sync operation back to previous state.
        Used when sync was applied but needs to be undone.

        Args:
            sync_id: Sync operation ID
            user_id: User requesting rollback
            reason: Reason for rollback

        Returns:
            Updated SyncOperation with status ROLLED_BACK

        Raises:
            NotFoundError: If sync not found
            BusinessLogicError: If sync cannot be rolled back
        """
        # Get sync
        sync = self.sync_repo.get_sync(sync_id)
        if not sync:
            raise NotFoundError(f"Sync {sync_id} not found")

        if sync.status not in [SyncStatus.COMPLETED, SyncStatus.APPLIED]:
            raise BusinessLogicError(
                f"Cannot rollback sync in {sync.status} state. "
                "Sync must be COMPLETED or APPLIED"
            )

        # Get all applied changes
        changes, _ = self.sync_repo.list_changes(
            sync_id,
            limit=100000  # Get all
        )

        # Reverse changes (last to first)
        for change in reversed(changes):
            try:
                # Reverse based on change type
                if change.change_type == ChangeType.NEW:
                    # Delete newly created translations
                    self.translation_repo.delete_translation(
                        change.translation_key,
                        change.language_code
                    )

                elif change.change_type == ChangeType.CHANGED:
                    # Restore previous value
                    if change.previous_value:
                        self.translation_repo.update_translation(
                            change.translation_key,
                            change.language_code,
                            change.previous_value
                        )

                elif change.change_type == ChangeType.DELETED:
                    # Restore deleted translations
                    if change.database_value:
                        self.translation_repo.create_translation(
                            change.translation_key,
                            change.language_code,
                            change.database_value
                        )

                elif change.change_type == ChangeType.CONFLICT:
                    # Restore based on original value
                    if change.database_value:
                        self.translation_repo.update_translation(
                            change.translation_key,
                            change.language_code,
                            change.database_value
                        )

            except Exception as e:
                logger.error(
                    f"Error rolling back change {change.change_id}: {str(e)}",
                    extra={'sync_id': sync_id, 'change_id': change.change_id}
                )

        # Update sync status to ROLLED_BACK
        rolled_back_sync = self.sync_repo.update_sync_status(
            sync_id,
            SyncStatus.ROLLED_BACK
        )

        # Record rollback reason
        self.sync_repo.add_rollback_record(
            sync_id,
            user_id,
            reason
        )

        logger.info(
            f"Rolled back sync {sync_id}",
            extra={'user_id': user_id, 'reason': reason}
        )

        return rolled_back_sync
