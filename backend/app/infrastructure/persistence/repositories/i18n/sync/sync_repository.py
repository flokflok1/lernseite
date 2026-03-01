"""
i18n Sync Repository - Part 1: History Operations

Data access layer for i18n synchronization operations:
- Sync history tracking (audit trail)

Part 2 (sync_repository_part2.py) contains:
- Per-key resolution tracking (sync details)
- JSONB snapshot storage for rollback
- Statistics queries

Implements Repository Pattern with direct SQL + psycopg3 (no ORM)
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
import psycopg
from psycopg.rows import dict_row

from .sync_repository_part2 import I18nSyncDetailsMixin


class I18nSyncRepository(I18nSyncDetailsMixin):
    """
    Repository for i18n sync operations

    Manages:
    - translations.i18n_sync_history (audit trail)
    - translations.i18n_sync_details (per-key decisions) [via mixin]
    - translations.i18n_sync_snapshots (JSONB backups) [via mixin]
    """

    def __init__(self, connection: psycopg.Connection):
        """Initialize repository with database connection"""
        self.conn = connection

    # =========================================================================
    # SYNC HISTORY OPERATIONS
    # =========================================================================

    def create_sync_history(
        self,
        sync_mode: str,
        languages_affected: List[str],
        initiated_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Create new sync operation record

        Args:
            sync_mode: 'MANUAL' or 'AUTO'
            languages_affected: List of language codes (de, en, pl)
            initiated_by: User UUID who initiated the sync

        Returns:
            Sync history record as dict with sync_id
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO translations.i18n_sync_history (
                    sync_mode, sync_status, languages_affected,
                    scan_started_at, initiated_by
                )
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)
                RETURNING *
                """,
                (sync_mode, 'SCANNING', languages_affected, initiated_by)
            )
            result = cursor.fetchone()
            self.conn.commit()
            return result

    def get_sync_history(self, sync_id: UUID) -> Optional[Dict[str, Any]]:
        """Get sync history by ID"""
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT * FROM translations.i18n_sync_history
                WHERE sync_id = %s
                """,
                (sync_id,)
            )
            return cursor.fetchone()

    def list_sync_history(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        List sync operations with pagination

        Args:
            limit: Max results
            offset: Skip N results
            status: Filter by status (COMPLETED, FAILED, etc.)

        Returns:
            Tuple of (list of syncs, total count)
        """
        # Validate limit
        if limit > 100:
            limit = 100

        with self.conn.cursor(row_factory=dict_row) as cursor:
            # Get total count
            if status:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM translations.i18n_sync_history WHERE sync_status = %s",
                    (status,)
                )
            else:
                cursor.execute("SELECT COUNT(*) as count FROM translations.i18n_sync_history")
            total = cursor.fetchone()['count']

            # Get paginated results
            if status:
                cursor.execute(
                    """
                    SELECT * FROM translations.i18n_sync_history
                    WHERE sync_status = %s
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (status, limit, offset)
                )
            else:
                cursor.execute(
                    """
                    SELECT * FROM translations.i18n_sync_history
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                    """,
                    (limit, offset)
                )
            syncs = cursor.fetchall()

        return syncs, total

    def update_sync_history(
        self,
        sync_id: UUID,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update sync history record

        Args:
            sync_id: Sync ID
            updates: Dictionary of field updates

        Returns:
            Updated record or None if not found
        """
        if not updates:
            return self.get_sync_history(sync_id)

        # Build SET clause
        set_clauses = []
        params = []

        for field, value in updates.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)

        set_sql = ", ".join(set_clauses)
        params.append(sync_id)

        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""
                UPDATE translations.i18n_sync_history
                SET {set_sql}
                WHERE sync_id = %s
                RETURNING *
                """,
                params
            )
            result = cursor.fetchone()
            self.conn.commit()

        return result

    def complete_sync_scan(self, sync_id: UUID) -> Optional[Dict[str, Any]]:
        """Mark scan as completed"""
        return self.update_sync_history(sync_id, {
            'sync_status': 'PENDING',
            'scan_completed_at': datetime.utcnow()
        })

    def start_sync_apply(self, sync_id: UUID) -> Optional[Dict[str, Any]]:
        """Mark sync as applying"""
        return self.update_sync_history(sync_id, {
            'sync_status': 'APPLYING',
            'apply_started_at': datetime.utcnow()
        })

    def complete_sync_apply(
        self,
        sync_id: UUID,
        completed_by: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Mark sync as completed"""
        return self.update_sync_history(sync_id, {
            'sync_status': 'COMPLETED',
            'apply_completed_at': datetime.utcnow(),
            'completed_by': completed_by
        })

    def mark_sync_failed(
        self,
        sync_id: UUID,
        error_message: str
    ) -> Optional[Dict[str, Any]]:
        """Mark sync as failed"""
        return self.update_sync_history(sync_id, {
            'sync_status': 'FAILED',
            'error_message': error_message
        })

    def update_sync_statistics(
        self,
        sync_id: UUID,
        added: int = 0,
        updated: int = 0,
        deleted: int = 0,
        skipped: int = 0,
        conflicted: int = 0
    ) -> Optional[Dict[str, Any]]:
        """Update sync statistics"""
        return self.update_sync_history(sync_id, {
            'total_keys': added + updated + deleted + skipped + conflicted,
            'keys_added': added,
            'keys_updated': updated,
            'keys_deleted': deleted,
            'keys_skipped': skipped,
            'keys_conflicted': conflicted
        })
