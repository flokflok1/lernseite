"""
i18n Sync Repository - Part 2: Details, Snapshots & Statistics

Continuation of sync_repository.py (split for Quality Gate G01: max 500 lines).

Contains:
- Sync detail operations (per-key resolution tracking)
- Snapshot operations (JSONB rollback storage)
- Statistics queries (dashboard + per-sync stats)

Implements Repository Pattern with direct SQL + psycopg3 (no ORM)
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
import psycopg
from psycopg.rows import dict_row


class I18nSyncDetailsMixin:
    """
    Mixin providing sync detail, snapshot, and statistics operations.

    Mixed into I18nSyncRepository to keep file sizes under 500 lines.
    Requires self.conn (psycopg.Connection) from the host class.
    """

    conn: psycopg.Connection

    # =========================================================================
    # SYNC DETAILS OPERATIONS
    # =========================================================================

    def create_sync_detail(
        self,
        sync_id: UUID,
        namespace_code: str,
        key_path: str,
        language: str,
        action: str,
        resolution_status: str,
        frontend_value: Optional[str] = None,
        database_value: Optional[str] = None,
        similarity_score: float = 0.0,
        conflict_reason: Optional[str] = None,
        is_new: bool = False,
        is_changed: bool = False,
        is_deleted: bool = False,
        change_magnitude: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create sync detail record"""
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO translations.i18n_sync_details (
                    sync_id, namespace_code, key_path, language,
                    action, resolution_status,
                    frontend_value, database_value, similarity_score,
                    conflict_reason,
                    is_new, is_changed, is_deleted, change_magnitude
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    sync_id, namespace_code, key_path, language,
                    action, resolution_status,
                    frontend_value, database_value, similarity_score,
                    conflict_reason,
                    is_new, is_changed, is_deleted, change_magnitude
                )
            )
            result = cursor.fetchone()
            self.conn.commit()
            return result

    def get_sync_detail(self, detail_id: UUID) -> Optional[Dict[str, Any]]:
        """Get sync detail by ID"""
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT * FROM translations.i18n_sync_details
                WHERE detail_id = %s
                """,
                (detail_id,)
            )
            return cursor.fetchone()

    def list_sync_details(
        self,
        sync_id: UUID,
        limit: int = 100,
        offset: int = 0,
        action: Optional[str] = None,
        status: Optional[str] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        List sync details for a sync operation

        Args:
            sync_id: Sync ID
            limit: Max results
            offset: Skip N results
            action: Filter by action (ADD, UPDATE, DELETE, SKIP, CONFLICT)
            status: Filter by resolution status

        Returns:
            Tuple of (list of details, total count)
        """
        if limit > 500:
            limit = 500

        with self.conn.cursor(row_factory=dict_row) as cursor:
            # Build WHERE clause
            where_parts = ["sync_id = %s"]
            params = [sync_id]

            if action:
                where_parts.append("action = %s")
                params.append(action)

            if status:
                where_parts.append("resolution_status = %s")
                params.append(status)

            where_sql = " AND ".join(where_parts)

            # Get count
            cursor.execute(
                f"SELECT COUNT(*) as count FROM translations.i18n_sync_details WHERE {where_sql}",
                params
            )
            total = cursor.fetchone()['count']

            # Get paginated results
            count_params = params.copy()
            params.extend([limit, offset])
            cursor.execute(
                f"""
                SELECT * FROM translations.i18n_sync_details
                WHERE {where_sql}
                ORDER BY namespace_code, language, key_path
                LIMIT %s OFFSET %s
                """,
                params
            )
            details = cursor.fetchall()

        return details, total

    def update_sync_detail(
        self,
        detail_id: UUID,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update sync detail record"""
        if not updates:
            return self.get_sync_detail(detail_id)

        set_clauses = []
        params = []

        for field, value in updates.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)

        set_sql = ", ".join(set_clauses)
        params.append(detail_id)

        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""
                UPDATE translations.i18n_sync_details
                SET {set_sql}
                WHERE detail_id = %s
                RETURNING *
                """,
                params
            )
            result = cursor.fetchone()
            self.conn.commit()

        return result

    def resolve_sync_detail(
        self,
        detail_id: UUID,
        action: str,
        manual_value: Optional[str] = None,
        resolved_by: Optional[UUID] = None
    ) -> Optional[Dict[str, Any]]:
        """Resolve a sync detail (mark as RESOLVED or MANUAL_OVERRIDE)"""
        resolution_status = 'MANUAL_OVERRIDE' if manual_value else 'RESOLVED'

        updates = {
            'action': action,
            'resolution_status': resolution_status,
            'resolved_by': resolved_by
        }

        if manual_value:
            updates['manual_resolution_value'] = manual_value

        return self.update_sync_detail(detail_id, updates)

    def count_pending_resolutions(self, sync_id: UUID) -> int:
        """Count pending resolutions for a sync"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM translations.i18n_sync_details
                WHERE sync_id = %s AND resolution_status = 'PENDING'
                """,
                (sync_id,)
            )
            return cursor.fetchone()[0]

    def count_conflicts(self, sync_id: UUID) -> int:
        """Count conflicts for a sync"""
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT COUNT(*) FROM translations.i18n_sync_details
                WHERE sync_id = %s AND action = 'CONFLICT'
                """,
                (sync_id,)
            )
            return cursor.fetchone()[0]

    # =========================================================================
    # SNAPSHOT OPERATIONS
    # =========================================================================

    def create_snapshot(
        self,
        sync_id: UUID,
        snapshot_type: str,
        db_state: Dict[str, Any],
        total_keys: int,
        affected_keys: int,
        languages_covered: List[str],
        reason: str,
        created_by: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Create JSONB snapshot of database state

        Args:
            sync_id: Sync ID
            snapshot_type: 'PRE_SYNC', 'POST_SYNC', or 'ROLLBACK'
            db_state: JSONB dict of translations state
            total_keys: Total number of keys in snapshot
            affected_keys: Number of keys affected by sync
            languages_covered: List of languages in snapshot
            reason: Human-readable reason
            created_by: User UUID who created snapshot

        Returns:
            Snapshot record as dict
        """
        import json

        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO translations.i18n_sync_snapshots (
                    sync_id, snapshot_type, db_state,
                    total_keys, affected_keys, languages_covered,
                    snapshot_reason, created_by
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    sync_id, snapshot_type, json.dumps(db_state),
                    total_keys, affected_keys, languages_covered,
                    reason, created_by
                )
            )
            result = cursor.fetchone()
            self.conn.commit()
            return result

    def get_snapshot(self, snapshot_id: UUID) -> Optional[Dict[str, Any]]:
        """Get snapshot by ID"""
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT * FROM translations.i18n_sync_snapshots
                WHERE snapshot_id = %s
                """,
                (snapshot_id,)
            )
            return cursor.fetchone()

    def get_snapshot_by_type(
        self,
        sync_id: UUID,
        snapshot_type: str
    ) -> Optional[Dict[str, Any]]:
        """Get snapshot of specific type for sync"""
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT * FROM translations.i18n_sync_snapshots
                WHERE sync_id = %s AND snapshot_type = %s
                """,
                (sync_id, snapshot_type)
            )
            return cursor.fetchone()

    def list_snapshots(
        self,
        sync_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List snapshots for a sync operation"""
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT * FROM translations.i18n_sync_snapshots
                WHERE sync_id = %s
                ORDER BY created_at DESC
                LIMIT %s
                """,
                (sync_id, limit)
            )
            return cursor.fetchall()

    # =========================================================================
    # STATISTICS QUERIES
    # =========================================================================

    def get_sync_stats(self, sync_id: UUID) -> Optional[Dict[str, Any]]:
        """Get complete statistics for a sync"""
        history = self.get_sync_history(sync_id)
        if not history:
            return None

        # Count details by action
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                SELECT
                    action,
                    COUNT(*) as count
                FROM translations.i18n_sync_details
                WHERE sync_id = %s
                GROUP BY action
                """,
                (sync_id,)
            )
            action_counts = {row['action']: row['count'] for row in cursor.fetchall()}

        return {
            **history,
            'action_breakdown': action_counts
        }

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics across all syncs"""
        with self.conn.cursor(row_factory=dict_row) as cursor:
            # Total syncs
            cursor.execute("SELECT COUNT(*) as count FROM translations.i18n_sync_history")
            total_syncs = cursor.fetchone()['count']

            # Syncs today
            cursor.execute(
                "SELECT COUNT(*) as count FROM translations.i18n_sync_history WHERE DATE(created_at) = CURRENT_DATE"
            )
            syncs_today = cursor.fetchone()['count']

            # Successful syncs
            cursor.execute(
                "SELECT COUNT(*) as count FROM translations.i18n_sync_history WHERE sync_status = 'COMPLETED'"
            )
            successful = cursor.fetchone()['count']

            # Failed syncs
            cursor.execute(
                "SELECT COUNT(*) as count FROM translations.i18n_sync_history WHERE sync_status = 'FAILED'"
            )
            failed = cursor.fetchone()['count']

            # Last sync
            cursor.execute(
                "SELECT * FROM translations.i18n_sync_history ORDER BY created_at DESC LIMIT 1"
            )
            last_sync = cursor.fetchone()

            # Pending resolutions across all syncs
            cursor.execute(
                "SELECT COUNT(*) as count FROM translations.i18n_sync_details WHERE resolution_status = 'PENDING'"
            )
            pending_resolutions = cursor.fetchone()['count']

        return {
            'total_syncs': total_syncs,
            'syncs_today': syncs_today,
            'successful_syncs': successful,
            'failed_syncs': failed,
            'last_sync': last_sync,
            'pending_resolutions': pending_resolutions
        }
