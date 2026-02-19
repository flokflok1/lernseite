"""
i18n Sync Service - Core business logic for translation synchronization.

Orchestrates the sync workflow:
1. Initiate sync (MANUAL or AUTO mode)
2. Scan translations (detect changes)
3. Resolve conflicts (manual or auto)

No ORM - uses psycopg3 with repositories.
"""

from typing import Optional, Dict, Any, List, Tuple, Callable
from datetime import datetime
import time
import logging

from app.infrastructure.persistence.repositories.i18n.sync_ops import (
    SyncMode, SyncStatus, SyncOperation, SyncOpsRepository
)
from app.infrastructure.persistence.repositories.i18n.sync_changes import (
    ChangeType, SyncChange, SyncChangesRepository
)
from app.infrastructure.persistence.repositories.i18n.sync_resolutions import (
    Resolution, SyncResolution, SyncResolutionsRepository
)
from app.infrastructure.persistence.repositories.i18n.sync_repository import (
    I18nSyncRepository
)
# OLD IMPORT BELOW (to be removed):
if False:
    from app.infrastructure.persistence.repositories.i18n.sync import (
    SyncRepository, SyncMode, SyncStatus, ChangeType, Resolution,
    SyncOperation, SyncChange, SyncResolution
)
from app.infrastructure.persistence.repositories.i18n.translations import I18nTranslationsRepository as TranslationRepository
from app.infrastructure.error_handling.exceptions import ValidationError, NotFoundError, BusinessLogicError
from app.infrastructure.persistence.database import get_connection

logger = logging.getLogger(__name__)


class I18nSyncService:
    """
    Service for managing i18n translation synchronization.

    Handles the complete workflow:
    - MANUAL mode: Requires explicit user resolution of conflicts
    - AUTO mode: Automatically resolves conflicts using similarity scoring

    Coordinates SyncRepository and TranslationRepository.
    """

    def __init__(self, conn=None):
        """
        Initialize sync service.

        Args:
            conn: Database connection (optional, created if not provided)
        """
        self.conn = conn or get_connection()
        self.sync_repo = SyncRepository(self.conn)
        self.translation_repo = TranslationRepository(self.conn)

    def initiate_sync(
        self,
        user_id: str,
        mode: str,
        languages: List[str],
        frontend_translations_loader: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SyncOperation:
        """
        Initiate new translation sync.

        Args:
            user_id: User initiating sync
            mode: MANUAL or AUTO (from SyncMode enum)
            languages: List of language codes to sync (e.g., ['de', 'en', 'pl'])
            frontend_translations_loader: Callback to load frontend translations
            metadata: Optional metadata dict

        Returns:
            Created SyncOperation

        Raises:
            ValidationError: If mode or languages invalid
        """
        # Validate mode
        valid_modes = ['MANUAL', 'AUTO']
        if mode not in valid_modes:
            raise ValidationError(
                f"Invalid sync mode: {mode}. Must be one of {valid_modes}"
            )

        # Validate languages
        if not languages or not isinstance(languages, list):
            raise ValidationError("Languages must be non-empty list")

        # Get supported languages
        supported_langs = self.translation_repo.get_supported_languages()
        unsupported = [lang for lang in languages if lang not in supported_langs]
        if unsupported:
            raise ValidationError(
                f"Unsupported languages: {unsupported}. "
                f"Supported: {supported_langs}"
            )

        # Create sync operation
        sync = self.sync_repo.create_sync(
            mode=mode,
            user_id=user_id,
            languages=languages,
            metadata=metadata or {}
        )

        logger.info(
            f"Initiated sync {sync.sync_id}",
            extra={'user_id': user_id, 'mode': mode, 'languages': languages}
        )

        return sync

    def scan_translations(
        self,
        sync_id: str,
        frontend_translations: Dict[str, Dict[str, str]],  # {lang: {key: value}}
    ) -> Tuple[SyncOperation, int, int, int, int]:
        """
        Scan frontend translations against database.

        Detects:
        - NEW: Keys in frontend but not in database
        - CHANGED: Keys with different values (only frontend changed)
        - DELETED: Keys in database but not in frontend
        - CONFLICT: Keys with different values (both changed)

        Args:
            sync_id: Sync operation ID
            frontend_translations: Frontend translations by language
                                  Format: {'de': {'key': 'value'}, ...}

        Returns:
            Tuple of (sync_operation, new_count, changed_count, deleted_count, conflict_count)

        Raises:
            NotFoundError: If sync not found
            BusinessLogicError: If sync not in PENDING state
        """
        # Get sync operation
        sync = self.sync_repo.get_sync(sync_id)
        if not sync:
            raise NotFoundError(f"Sync {sync_id} not found")

        if sync.status != SyncStatus.PENDING:
            raise BusinessLogicError(
                f"Cannot scan sync in {sync.status} state. Must be PENDING."
            )

        # Mark as scanning
        self.sync_repo.update_sync_status(sync_id, SyncStatus.SCANNING)

        # Scan each language
        start_time = time.time()
        stats = {'new': 0, 'changed': 0, 'deleted': 0, 'conflicts': 0}

        for language_code in sync.languages_synced:
            # Get frontend translations for language
            frontend_by_lang = frontend_translations.get(language_code, {})

            # Get database translations for language
            db_translations, _ = self.translation_repo.get_translations_for_language(
                language_code,
                limit=10000
            )
            database_by_lang = {t.translation_key: t.value for t in db_translations}

            # Get previous values from metadata (for conflict detection)
            previous_values = {}  # TODO: Load from sync history if available

            # Detect changes
            changes = self.translation_repo.detect_changes(
                frontend_by_lang,
                database_by_lang,
                previous_values
            )

            # Record changes in database
            for change_type, change_list in changes.items():
                if not change_list:
                    continue

                for change_data in change_list:
                    self.sync_repo.create_change(
                        sync_id=sync_id,
                        translation_key=change_data['key'],
                        language_code=language_code,
                        change_type=change_type.upper(),
                        frontend_value=change_data.get('frontend_value'),
                        database_value=change_data.get('database_value'),
                        previous_value=change_data.get('previous_value'),
                        similarity_score=change_data.get('similarity', 0.0)
                    )

                    stats[change_type] += 1

        # Calculate scan duration
        scan_duration_ms = int((time.time() - start_time) * 1000)

        # Update sync with results
        completed_sync = self.sync_repo.complete_sync(
            sync_id,
            scan_duration_ms,
            {
                'new_keys': stats['new'],
                'changed_keys': stats['changed'],
                'deleted_keys': stats['deleted'],
                'conflicted_keys': stats['conflicts']
            }
        )

        logger.info(
            f"Completed scan for sync {sync_id}",
            extra={
                'duration_ms': scan_duration_ms,
                'new': stats['new'],
                'changed': stats['changed'],
                'deleted': stats['deleted'],
                'conflicts': stats['conflicts']
            }
        )

        return completed_sync, stats['new'], stats['changed'], stats['deleted'], stats['conflicts']

    def get_scan_results(
        self,
        sync_id: str,
        limit: int = 20,
        offset: int = 0,
        change_type: Optional[str] = None,
        language_code: Optional[str] = None
    ) -> Tuple[List[SyncChange], int]:
        """
        Get detailed scan results for a sync.

        Args:
            sync_id: Sync operation ID
            limit: Max results to return
            offset: Number of results to skip
            change_type: Optional filter by change type (NEW, CHANGED, DELETED, CONFLICT)
            language_code: Optional filter by language

        Returns:
            Tuple of (changes_list, total_count)
        """
        changes, total = self.sync_repo.list_changes(
            sync_id,
            limit=limit,
            offset=offset,
            change_type=change_type,
            language_code=language_code
        )

        return changes, total

    def resolve_conflict(
        self,
        sync_id: str,
        change_id: int,
        chosen_action: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> SyncResolution:
        """
        Record user resolution for a conflict.

        Args:
            sync_id: Sync operation ID
            change_id: Change ID (must be CONFLICT type)
            chosen_action: Resolution action (ADD, UPDATE, DELETE, SKIP)
            user_id: User making resolution
            notes: Optional resolution notes

        Returns:
            Created SyncResolution

        Raises:
            NotFoundError: If change not found
            BusinessLogicError: If change is not a CONFLICT
        """
        # Get change
        change = self.sync_repo.get_change(change_id)
        if not change:
            raise NotFoundError(f"Change {change_id} not found")

        if change.change_type != ChangeType.CONFLICT:
            raise BusinessLogicError(
                f"Cannot resolve non-CONFLICT change (type: {change.change_type})"
            )

        # Record resolution
        resolution = self.sync_repo.create_resolution(
            sync_id=sync_id,
            change_id=change_id,
            translation_key=change.translation_key,
            language_code=change.language_code,
            chosen_action=chosen_action,
            user_id=user_id,
            notes=notes
        )

        # Update change with resolution
        self.sync_repo.update_change_resolution(
            change_id,
            chosen_action,
            notes
        )

        logger.info(
            f"Resolved conflict {change_id}: {chosen_action}",
            extra={'sync_id': sync_id, 'user_id': user_id}
        )

        return resolution
