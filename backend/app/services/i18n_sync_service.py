"""
i18n Sync Service - Translation Synchronization Engine

Implements:
- Frontend JSON ↔ Database synchronization
- Scanning and change detection with similarity scoring
- Conflict resolution (MANUAL vs AUTO modes)
- Snapshot management and rollback
- Per-key decision tracking and audit trail

Supports both MANUAL mode (admin chooses) and AUTO mode (system decides)
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from uuid import UUID, uuid4
import logging
import json
from difflib import SequenceMatcher

from app.repositories.i18n_sync_repository import I18nSyncRepository
from app.repositories.i18n_repository import I18nRepository
from app.database import get_db_connection
from app.models.i18n_sync import (
    SyncMode, SyncStatus, ResolutionAction, ResolutionStatus,
    ChangeMagnitude, ComparisonCategory, ComparisonItem
)

logger = logging.getLogger(__name__)


class I18nSyncService:
    """
    i18n Synchronization Service.

    Orchestrates scanning, comparison, resolution, and application of translation syncs.
    Supports MANUAL (admin decides) and AUTO (system decides) modes.
    """

    # Configuration
    SIMILARITY_THRESHOLD_MINOR = 0.95      # <5% difference
    SIMILARITY_THRESHOLD_MODERATE = 0.90   # 5-10% difference
    # >10% difference = MAJOR

    def __init__(self):
        self.sync_repo: Optional[I18nSyncRepository] = None
        self.i18n_repo: Optional[I18nRepository] = None
        self.conn = None

    def _init_repos(self):
        """Initialize repositories with database connection."""
        if self.conn is None:
            self.conn = get_db_connection()
        if self.sync_repo is None:
            self.sync_repo = I18nSyncRepository(self.conn)
        if self.i18n_repo is None:
            self.i18n_repo = I18nRepository(self.conn)

    def start_sync_scan(
        self,
        sync_mode: str,
        languages_affected: List[str],
        initiated_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Initiate a new sync scan operation.

        Creates sync history record, scans frontend JSON vs database,
        detects changes (new/changed/deleted keys), calculates similarity scores,
        and generates per-key decision records.

        Args:
            sync_mode: 'MANUAL' (admin selects actions) or 'AUTO' (system decides)
            languages_affected: List of language codes (e.g., ['de', 'en', 'pl'])
            initiated_by: UUID of user initiating sync (admin user ID)

        Returns:
            Dictionary with:
            - sync_id: UUID of created sync
            - sync_status: 'SCANNING' → 'PENDING'
            - scan_results: Summary of changes detected
            - total_keys: Total keys processed
            - keys_added, keys_updated, keys_deleted, keys_skipped, keys_conflicted: counts
        """
        self._init_repos()

        try:
            # Create sync history record (status: SCANNING)
            sync_id = uuid4()
            sync_history = self.sync_repo.create_sync_history(
                sync_mode=sync_mode,
                languages_affected=languages_affected,
                initiated_by=initiated_by
            )
            sync_id = UUID(sync_history['sync_id'])

            # Mark scan start time
            self.sync_repo.update_sync_history(
                sync_id,
                {'scan_started_at': datetime.utcnow()}
            )

            # Get frontend JSON and database translations
            frontend_data = self._load_frontend_json(languages_affected)
            database_data = self._load_database_translations(languages_affected)

            # Scan and detect changes
            comparison_data = self._scan_and_detect_changes(
                sync_id,
                frontend_data,
                database_data,
                sync_mode,
                languages_affected
            )

            # Mark scan complete
            self.sync_repo.complete_sync_scan(sync_id)

            # Update statistics
            self.sync_repo.update_sync_statistics(
                sync_id,
                added=comparison_data['keys_added'],
                updated=comparison_data['keys_updated'],
                deleted=comparison_data['keys_deleted'],
                skipped=comparison_data['keys_skipped'],
                conflicted=comparison_data['keys_conflicted']
            )

            # Create PRE_SYNC snapshot (backup before applying)
            self._create_snapshot(
                sync_id,
                'PRE_SYNC',
                database_data,
                f"Backup before {sync_mode} sync operation"
            )

            logger.info(
                f"Sync scan {sync_id} completed ({sync_mode} mode)",
                extra={
                    'sync_id': str(sync_id),
                    'sync_mode': sync_mode,
                    'languages': languages_affected,
                    **comparison_data
                }
            )

            return {
                'sync_id': str(sync_id),
                'sync_status': 'PENDING',
                'sync_mode': sync_mode,
                'languages_affected': languages_affected,
                'scan_results': comparison_data
            }

        except Exception as e:
            logger.error(f"Error during sync scan: {e}", exc_info=True)
            raise

    def get_comparison_panel(
        self,
        sync_id: UUID,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get comparison panel data for admin UI.

        Returns side-by-side comparison of frontend vs database values,
        grouped by category (NEW_KEYS, CHANGED_KEYS, DELETED_KEYS, CONFLICTS).

        Args:
            sync_id: Sync operation ID
            category: Optional filter by category
            limit: Max items per page (max 100)
            offset: Pagination offset

        Returns:
            Dictionary with:
            - categories: List of ComparisonCategory objects
            - total_items: Total items across all categories
            - pending_count: Items awaiting resolution
            - conflicts_count: Items with conflicts
            - can_apply: Whether sync can be applied (all pending resolved in MANUAL mode)
        """
        self._init_repos()

        try:
            # Get all sync details with pagination
            details, total = self.sync_repo.list_sync_details(
                sync_id,
                limit=min(limit, 100),
                offset=offset
            )

            # Group by category
            categories = {}
            for detail in details:
                action = detail['action']

                if action == 'ADD':
                    cat_name = 'NEW_KEYS'
                elif action == 'UPDATE':
                    cat_name = 'CHANGED_KEYS'
                elif action == 'DELETE':
                    cat_name = 'DELETED_KEYS'
                elif action == 'CONFLICT':
                    cat_name = 'CONFLICTS'
                else:  # SKIP
                    continue

                if cat_name not in categories:
                    categories[cat_name] = []

                # Format as ComparisonItem
                item = ComparisonItem(
                    namespace_code=detail['namespace_code'],
                    key_path=detail['key_path'],
                    language=detail['language'],
                    action=detail['action'],
                    resolution_status=detail['resolution_status'],
                    frontend_value=detail['frontend_value'],
                    database_value=detail['database_value'],
                    similarity=detail['similarity_score'],
                    conflict_reason=detail['conflict_reason'],
                    proposed_action=detail.get('proposed_action')
                )
                categories[cat_name].append(item)

            # Build response categories
            response_categories = [
                ComparisonCategory(
                    category=cat_name,
                    items=items,
                    count=len(items)
                )
                for cat_name, items in categories.items()
            ]

            # Get sync info
            sync_info = self.sync_repo.get_sync_history(sync_id)

            return {
                'success': True,
                'sync_id': str(sync_id),
                'categories': response_categories,
                'total_items': total,
                'sync_mode': sync_info['sync_mode'],
                'pending_count': self.sync_repo.count_pending_resolutions(sync_id),
                'conflicts_count': self.sync_repo.count_conflicts(sync_id),
                'can_apply': sync_info['sync_status'] == 'PENDING'
            }

        except Exception as e:
            logger.error(f"Error getting comparison panel: {e}", exc_info=True)
            raise

    def apply_sync(
        self,
        sync_id: UUID,
        resolutions: Optional[Dict[str, Any]] = None,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Apply sync changes to database.

        In MANUAL mode: Applies only keys with resolutions provided
        In AUTO mode: Applies all keys with auto-generated actions
        Prevents applying with unresolved conflicts unless force=True

        Args:
            sync_id: Sync operation ID
            resolutions: Dict of detail_id → {action, manual_value} (for MANUAL mode)
            force: Force apply even with conflicts

        Returns:
            Dictionary with:
            - success: True if applied
            - applied_count: Number of keys applied
            - failed_count: Number of failures
            - errors: List of error messages
        """
        self._init_repos()

        try:
            # Get sync info
            sync_info = self.sync_repo.get_sync_history(sync_id)
            sync_mode = sync_info['sync_mode']

            # Check if all conflicts are resolved (unless force=True)
            conflicts = self.sync_repo.count_conflicts(sync_id)
            if conflicts > 0 and not force:
                raise ValueError(
                    f"Cannot apply: {conflicts} unresolved conflicts. "
                    "Use force=True to override."
                )

            # Mark as APPLYING
            self.sync_repo.start_sync_apply(sync_id)

            applied_count = 0
            failed_count = 0
            errors = []

            # Get all pending sync details
            details, _ = self.sync_repo.list_sync_details(
                sync_id,
                limit=10000,  # Get all
                status='PENDING' if sync_mode == 'MANUAL' else None
            )

            for detail in details:
                try:
                    action = detail['action']

                    # Apply based on action
                    if action == 'ADD':
                        # Insert new translation
                        self.i18n_repo.create_translation(
                            namespace_code=detail['namespace_code'],
                            key_path=detail['key_path'],
                            language_code=detail['language'],
                            translation_text=detail['frontend_value'],
                            translated_by=None  # Sync system
                        )
                        applied_count += 1

                    elif action == 'UPDATE':
                        # Update existing translation
                        self.i18n_repo.update_translation(
                            key_id=detail['key_path'],  # Assuming this structure
                            language_code=detail['language'],
                            translation_text=detail['frontend_value'],
                            translated_by=None
                        )
                        applied_count += 1

                    elif action == 'DELETE':
                        # Delete translation
                        self.i18n_repo.delete_translation(
                            namespace_code=detail['namespace_code'],
                            key_path=detail['key_path'],
                            language_code=detail['language']
                        )
                        applied_count += 1

                    elif action in ['SKIP', 'CONFLICT']:
                        # Don't apply
                        pass

                    # Mark detail as RESOLVED
                    self.sync_repo.resolve_sync_detail(
                        detail_id=UUID(detail['detail_id']),
                        action=action,
                        resolved_by=None
                    )

                except Exception as e:
                    error_msg = f"Failed to apply {detail['key_path']}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    failed_count += 1

            # Create POST_SYNC snapshot
            database_data_after = self._load_database_translations(
                sync_info['languages_affected']
            )
            self._create_snapshot(
                sync_id,
                'POST_SYNC',
                database_data_after,
                f"Snapshot after applying {applied_count} changes"
            )

            # Mark as COMPLETED or FAILED
            if failed_count == 0:
                self.sync_repo.update_sync_history(
                    sync_id,
                    {
                        'sync_status': 'COMPLETED',
                        'apply_completed_at': datetime.utcnow()
                    }
                )
                status = 'COMPLETED'
            else:
                self.sync_repo.mark_sync_failed(
                    sync_id,
                    f"{failed_count} keys failed to apply"
                )
                status = 'FAILED'

            logger.info(
                f"Sync {sync_id} applied ({status}): {applied_count} applied, {failed_count} failed",
                extra={
                    'sync_id': str(sync_id),
                    'applied_count': applied_count,
                    'failed_count': failed_count
                }
            )

            return {
                'success': failed_count == 0,
                'status': status,
                'applied_count': applied_count,
                'failed_count': failed_count,
                'errors': errors
            }

        except Exception as e:
            logger.error(f"Error applying sync: {e}", exc_info=True)
            self.sync_repo.mark_sync_failed(sync_id, str(e))
            raise

    def rollback_sync(
        self,
        sync_id: UUID,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Rollback sync to PRE_SYNC snapshot state.

        Restores all translations to state before the sync was applied.

        Args:
            sync_id: Sync operation ID
            reason: Reason for rollback

        Returns:
            Dictionary with:
            - success: True if rolled back
            - keys_restored: Number of keys restored
            - rollback_duration_ms: Time taken in milliseconds
        """
        self._init_repos()

        try:
            import time
            start_time = time.time()

            # Get PRE_SYNC snapshot
            snapshot = self.sync_repo.get_snapshot_by_type(sync_id, 'PRE_SYNC')
            if not snapshot:
                raise ValueError(f"No PRE_SYNC snapshot found for sync {sync_id}")

            # Restore from snapshot
            db_state = json.loads(snapshot['db_state']) if isinstance(snapshot['db_state'], str) else snapshot['db_state']

            keys_restored = 0
            for namespace_code, languages in db_state.items():
                for language_code, translations in languages.items():
                    for key_path, value in translations.items():
                        # Restore each translation
                        self.i18n_repo.update_translation(
                            key_id=key_path,
                            language_code=language_code,
                            translation_text=value
                        )
                        keys_restored += 1

            # Create ROLLBACK snapshot
            self._create_snapshot(
                sync_id,
                'ROLLBACK',
                db_state,
                f"Rollback snapshot: {reason}"
            )

            # Mark sync as ROLLED_BACK
            duration_ms = int((time.time() - start_time) * 1000)
            self.sync_repo.update_sync_history(
                sync_id,
                {
                    'sync_status': 'ROLLED_BACK',
                    'error_message': f"Rolled back: {reason}"
                }
            )

            logger.info(
                f"Sync {sync_id} rolled back: {keys_restored} keys restored in {duration_ms}ms",
                extra={
                    'sync_id': str(sync_id),
                    'keys_restored': keys_restored,
                    'duration_ms': duration_ms,
                    'reason': reason
                }
            )

            return {
                'success': True,
                'keys_restored': keys_restored,
                'rollback_duration_ms': duration_ms
            }

        except Exception as e:
            logger.error(f"Error rolling back sync: {e}", exc_info=True)
            raise

    # =========================================================================
    # PRIVATE HELPER METHODS
    # =========================================================================

    def _load_frontend_json(self, languages: List[str]) -> Dict[str, Any]:
        """
        Load frontend JSON translations.

        Returns structure:
        {
            'namespace': {
                'de': {'key.path': 'German value', ...},
                'en': {'key.path': 'English value', ...}
            }
        }
        """
        # TODO: Implement loading from frontend JSON files
        # For now, return empty dict for implementation
        return {}

    def _load_database_translations(self, languages: List[str]) -> Dict[str, Any]:
        """
        Load all translations from database.

        Returns same structure as _load_frontend_json for comparison.
        """
        # TODO: Implement database query to get all translations
        # Builds nested dict structure from database
        return {}

    def _scan_and_detect_changes(
        self,
        sync_id: UUID,
        frontend_data: Dict[str, Any],
        database_data: Dict[str, Any],
        sync_mode: str,
        languages: List[str]
    ) -> Dict[str, int]:
        """
        Scan frontend vs database and detect changes.

        Creates i18n_sync_details records for each detected change.
        Calculates similarity scores and change magnitude.

        Returns: Statistics dict with counts
        """
        keys_added = 0
        keys_updated = 0
        keys_deleted = 0
        keys_skipped = 0
        keys_conflicted = 0

        # TODO: Implement full scanning logic
        # For each language:
        #   1. Get all keys from frontend
        #   2. Get all keys from database
        #   3. Find intersections (changed), frontend-only (added), database-only (deleted)
        #   4. Calculate similarity_score for each changed key
        #   5. Determine change_magnitude based on similarity
        #   6. Create i18n_sync_details record
        #   7. Auto-generate proposed_action if AUTO mode

        return {
            'keys_added': keys_added,
            'keys_updated': keys_updated,
            'keys_deleted': keys_deleted,
            'keys_skipped': keys_skipped,
            'keys_conflicted': keys_conflicted,
            'total_keys': keys_added + keys_updated + keys_deleted
        }

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate text similarity score (0.0 to 1.0).

        Uses Python's SequenceMatcher for difflib-based comparison.
        """
        matcher = SequenceMatcher(None, str1, str2)
        return matcher.ratio()

    def _determine_magnitude(self, similarity_score: float) -> str:
        """
        Determine change magnitude based on similarity score.

        - MINOR: similarity >= 0.95 (<5% difference)
        - MODERATE: 0.90 <= similarity < 0.95 (5-10% difference)
        - MAJOR: similarity < 0.90 (>10% difference)
        """
        if similarity_score >= self.SIMILARITY_THRESHOLD_MINOR:
            return 'MINOR'
        elif similarity_score >= self.SIMILARITY_THRESHOLD_MODERATE:
            return 'MODERATE'
        else:
            return 'MAJOR'

    def _auto_suggest_action(
        self,
        similarity_score: float,
        change_magnitude: str
    ) -> str:
        """
        Auto-generate suggested action for AUTO mode.

        Rules:
        - MINOR changes: SKIP (likely typo fix, don't overwrite)
        - MODERATE changes: CONFLICT (needs review)
        - MAJOR changes: UPDATE (significant change, apply frontend version)
        """
        if change_magnitude == 'MINOR':
            return 'SKIP'
        elif change_magnitude == 'MODERATE':
            return 'CONFLICT'
        else:  # MAJOR
            return 'UPDATE'

    def _create_snapshot(
        self,
        sync_id: UUID,
        snapshot_type: str,
        db_state: Dict[str, Any],
        reason: str
    ) -> None:
        """
        Create JSONB snapshot of database state.

        Args:
            sync_id: Sync operation ID
            snapshot_type: 'PRE_SYNC', 'POST_SYNC', or 'ROLLBACK'
            db_state: Nested dict of all translations
            reason: Human-readable reason
        """
        self._init_repos()

        # Convert dict to JSON for storage
        db_state_json = json.dumps(db_state)

        self.sync_repo.create_snapshot(
            sync_id=sync_id,
            snapshot_type=snapshot_type,
            db_state=db_state_json,
            total_keys=self._count_keys_in_state(db_state),
            affected_keys=0,  # TODO: Calculate
            languages_covered=list(db_state.keys()),
            reason=reason,
            created_by=None
        )

    def _count_keys_in_state(self, db_state: Dict[str, Any]) -> int:
        """Count total keys in database state dict."""
        count = 0
        for namespace, languages in db_state.items():
            for language, keys in languages.items():
                count += len(keys)
        return count


# Singleton instance
_sync_service: Optional[I18nSyncService] = None


def get_sync_service() -> I18nSyncService:
    """Get or create singleton i18n sync service."""
    global _sync_service
    if _sync_service is None:
        _sync_service = I18nSyncService()
    return _sync_service
