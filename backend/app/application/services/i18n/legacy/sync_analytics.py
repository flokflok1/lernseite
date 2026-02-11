"""
i18n Sync Service - Analytics and Statistics

Handles retrieving sync details, statistics, and comparison operations.

No ORM - uses psycopg3 with repositories.
"""

from typing import Dict, Any, List, Tuple, Optional
from difflib import SequenceMatcher
import logging

from app.infrastructure.persistence.repositories.i18n.sync import (
    SyncRepository, SyncOperation, SyncChange
)
from app.infrastructure.persistence.repositories.i18n.translations import I18nTranslationsRepository as TranslationRepository
from app.infrastructure.utils.exceptions import NotFoundError
from app.infrastructure.persistence.database import get_connection

logger = logging.getLogger(__name__)


class TranslationComparisonService:
    """
    Service for comparing translations and detecting changes.

    Analyzes differences between frontend and database versions.
    """

    @staticmethod
    def calculate_similarity(value1: Optional[str], value2: Optional[str]) -> float:
        """
        Calculate similarity score between two values.

        Args:
            value1: First value
            value2: Second value

        Returns:
            Similarity score from 0.0 to 1.0
        """
        if value1 is None or value2 is None:
            return 0.0

        matcher = SequenceMatcher(None, str(value1), str(value2))
        return matcher.ratio()

    @staticmethod
    def detect_change_type(
        frontend_value: Optional[str],
        database_value: Optional[str],
        previous_value: Optional[str] = None
    ) -> Tuple[Optional[str], float]:
        """
        Detect type of change between versions.

        Args:
            frontend_value: Frontend version
            database_value: Database version
            previous_value: Previous known value (for conflict detection)

        Returns:
            Tuple of (change_type, similarity_score)
            change_type: NEW, CHANGED, DELETED, CONFLICT, or None (no change)
        """
        # No frontend value = deleted
        if frontend_value is None:
            if database_value is not None:
                return ('DELETED', 1.0)
            return (None, 1.0)

        # Frontend value exists, database doesn't = new
        if database_value is None:
            return ('NEW', 1.0)

        # Both exist, compare values
        if frontend_value == database_value:
            return (None, 1.0)  # No change

        # Values differ - detect if it's a simple change or conflict
        if previous_value is None:
            return ('CHANGED', 0.0)  # Only frontend changed

        # Previous value exists - check if both changed
        if previous_value != database_value and previous_value != frontend_value:
            # Both changed from previous = conflict
            similarity = TranslationComparisonService.calculate_similarity(
                frontend_value,
                database_value
            )
            return ('CONFLICT', similarity)

        # Only database changed, frontend unchanged = conflict
        if previous_value == frontend_value and previous_value != database_value:
            similarity = TranslationComparisonService.calculate_similarity(
                frontend_value,
                database_value
            )
            return ('CONFLICT', similarity)

        # Default to changed
        return ('CHANGED', 0.0)


class I18nSyncAnalyticsService:
    """
    Service for analytics and statistics of i18n translation syncs.

    Provides detailed information about sync operations and system state.
    """

    def __init__(self, conn=None):
        """
        Initialize analytics service.

        Args:
            conn: Database connection (optional, created if not provided)
        """
        self.conn = conn or get_connection()
        self.sync_repo = SyncRepository(self.conn)
        self.translation_repo = TranslationRepository(self.conn)

    def get_sync_details(
        self,
        sync_id: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive details about a sync operation.

        Args:
            sync_id: Sync operation ID

        Returns:
            Dictionary with sync details, changes, and resolutions

        Raises:
            NotFoundError: If sync not found
        """
        # Get sync
        sync = self.sync_repo.get_sync(sync_id)
        if not sync:
            raise NotFoundError(f"Sync {sync_id} not found")

        # Get changes by type
        changes_by_type = {}
        for change_type in ['NEW', 'CHANGED', 'DELETED', 'CONFLICT']:
            changes, count = self.sync_repo.list_changes(
                sync_id,
                change_type=change_type,
                limit=100
            )
            changes_by_type[change_type.lower()] = [c.to_dict() for c in changes]

        # Get resolutions
        resolutions, resolution_count = self.sync_repo.list_resolutions(
            sync_id,
            limit=100
        )

        return {
            'sync': sync.to_dict(),
            'changes': {
                'by_type': changes_by_type,
                'total': self.sync_repo.count_changes(sync_id)
            },
            'resolutions': {
                'items': [r.to_dict() for r in resolutions],
                'total': resolution_count
            }
        }

    def get_sync_statistics(
        self,
        sync_id: str
    ) -> Dict[str, Any]:
        """
        Get statistics about sync operation results.

        Args:
            sync_id: Sync operation ID

        Returns:
            Dictionary with statistical data

        Raises:
            NotFoundError: If sync not found
        """
        # Get sync
        sync = self.sync_repo.get_sync(sync_id)
        if not sync:
            raise NotFoundError(f"Sync {sync_id} not found")

        # Count changes by type
        new_count = self.sync_repo.count_changes(sync_id, change_type='NEW')
        changed_count = self.sync_repo.count_changes(sync_id, change_type='CHANGED')
        deleted_count = self.sync_repo.count_changes(sync_id, change_type='DELETED')
        conflict_count = self.sync_repo.count_changes(sync_id, change_type='CONFLICT')

        total_changes = new_count + changed_count + deleted_count + conflict_count

        # Calculate resolution stats
        resolutions, _ = self.sync_repo.list_resolutions(sync_id, limit=100000)
        resolved_conflicts = len([r for r in resolutions if r.action is not None])

        return {
            'sync_id': sync_id,
            'mode': sync.mode,
            'status': sync.status,
            'changes': {
                'new': new_count,
                'changed': changed_count,
                'deleted': deleted_count,
                'conflicts': conflict_count,
                'total': total_changes
            },
            'resolutions': {
                'resolved': resolved_conflicts,
                'unresolved': conflict_count - resolved_conflicts
            },
            'performance': {
                'scan_duration_ms': sync.scan_duration_ms or 0,
                'completed_at': sync.completed_at.isoformat() if sync.completed_at else None
            }
        }

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get system-wide dashboard statistics for i18n syncs.

        Returns:
            Dictionary with system-wide statistics
        """
        # Count syncs by status
        total_syncs = self.sync_repo.count_syncs()
        completed_syncs = self.sync_repo.count_syncs_by_status('COMPLETED')
        failed_syncs = self.sync_repo.count_syncs_by_status('FAILED')
        rolled_back_syncs = self.sync_repo.count_syncs_by_status('ROLLED_BACK')

        # Count syncs by mode
        manual_syncs = self.sync_repo.count_syncs_by_mode('MANUAL')
        auto_syncs = self.sync_repo.count_syncs_by_mode('AUTO')

        # Get recent syncs
        recent_syncs, _ = self.sync_repo.list_syncs(limit=10)

        # Translation statistics
        total_translations = self.translation_repo.count_all_translations()
        translations_by_language = self.translation_repo.count_by_language()

        # Calculate success rate
        success_rate = 0.0
        if total_syncs > 0:
            success_rate = (completed_syncs / total_syncs) * 100

        # Calculate average scan duration
        avg_scan_duration = 0
        completed_list, _ = self.sync_repo.list_syncs_by_status('COMPLETED', limit=100)
        if completed_list:
            durations = [s.scan_duration_ms for s in completed_list if s.scan_duration_ms]
            if durations:
                avg_scan_duration = sum(durations) / len(durations)

        return {
            'total_syncs': total_syncs,
            'syncs': {
                'completed': completed_syncs,
                'failed': failed_syncs,
                'rolled_back': rolled_back_syncs,
                'manual_mode': manual_syncs,
                'auto_mode': auto_syncs
            },
            'performance': {
                'avg_scan_duration_ms': int(avg_scan_duration),
                'recent_syncs': [s.to_dict() for s in recent_syncs]
            },
            'translations': {
                'total_keys': total_translations,
                'by_language': translations_by_language
            },
            'success_rate': f"{success_rate:.1f}%"
        }
