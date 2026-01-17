"""
i18n Sync Resolutions Repository - User decisions and rollback management.

Handles all database operations for managing user resolutions on conflicted
translations, including:
- Recording user resolution decisions
- Listing resolutions for a sync
- Marking resolutions as applied
- Rolling back entire sync operations

Uses psycopg3 with direct SQL and parameterized queries (NO ORM).
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import psycopg
from psycopg.rows import dict_row


class Resolution(str, Enum):
    """User resolution action on conflicted translations."""
    ADD = "ADD"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SKIP = "SKIP"


@dataclass
class SyncResolution:
    """Represents a user decision on a conflicted translation."""

    resolution_id: int
    sync_id: str
    change_id: int
    translation_key: str
    language_code: str
    chosen_action: str
    decided_by_user_id: str
    decided_at: Optional[datetime] = None
    decision_notes: Optional[str] = None
    applied: bool = False
    applied_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'resolution_id': self.resolution_id,
            'sync_id': self.sync_id,
            'change_id': self.change_id,
            'translation_key': self.translation_key,
            'language_code': self.language_code,
            'chosen_action': self.chosen_action,
            'decided_by_user_id': self.decided_by_user_id,
            'decided_at': self.decided_at.isoformat() if self.decided_at else None,
            'decision_notes': self.decision_notes,
            'applied': self.applied,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None
        }


class SyncResolutionsRepository:
    """
    Repository for managing user resolutions on sync changes.

    Handles operations for recording and tracking user decisions on
    conflicted translations, including application and rollback.
    """

    def __init__(self, connection: psycopg.Connection):
        """Initialize repository with database connection."""
        self.conn = connection

    def create_resolution(
        self,
        sync_id: str,
        change_id: int,
        translation_key: str,
        language_code: str,
        chosen_action: str,
        user_id: str,
        notes: Optional[str] = None
    ) -> SyncResolution:
        """
        Record user resolution for conflicted change.

        Args:
            sync_id: Associated sync operation ID
            change_id: Associated change record ID
            translation_key: Translation key (e.g., 'admin.users.title')
            language_code: Language code (de, en, pl)
            chosen_action: User's chosen action (ADD, UPDATE, DELETE, SKIP)
            user_id: User ID making the resolution
            notes: Optional decision notes explaining the choice

        Returns:
            Created SyncResolution instance
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO i18n.sync_resolutions
                (sync_id, change_id, translation_key, language_code,
                 chosen_action, decided_by_user_id, decision_notes)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    sync_id, change_id, translation_key, language_code,
                    chosen_action, user_id, notes
                )
            )
            row = cursor.fetchone()
            self.conn.commit()

            return self._map_resolution_row(row)

    def list_resolutions(
        self,
        sync_id: str,
        applied: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[SyncResolution], int]:
        """
        List resolutions for a sync operation.

        Args:
            sync_id: Sync operation ID
            applied: Filter by applied status (True/False/None for all)
            limit: Max results (default 100, max 100)
            offset: Results to skip (default 0)

        Returns:
            Tuple of (resolutions list, total count)
        """
        limit = min(limit, 100)

        where_clauses = ["sync_id = %s"]
        params = [sync_id]

        if applied is not None:
            where_clauses.append("applied = %s")
            params.append(applied)

        where_sql = " AND ".join(where_clauses)

        with self.conn.cursor(row_factory=dict_row) as cursor:
            # Get count
            cursor.execute(
                f"SELECT COUNT(*) as total FROM i18n.sync_resolutions WHERE {where_sql}",
                params
            )
            total = cursor.fetchone()['total']

            # Get resolutions
            params.extend([limit, offset])
            cursor.execute(
                f"""
                SELECT * FROM i18n.sync_resolutions
                WHERE {where_sql}
                ORDER BY decided_at DESC
                LIMIT %s OFFSET %s
                """,
                params
            )
            rows = cursor.fetchall()

            resolutions = [self._map_resolution_row(row) for row in rows]
            return resolutions, total

    def mark_resolution_applied(
        self,
        resolution_id: int
    ) -> Optional[SyncResolution]:
        """
        Mark resolution as applied.

        Args:
            resolution_id: Resolution record ID

        Returns:
            Updated SyncResolution or None if not found
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                UPDATE i18n.sync_resolutions
                SET applied = TRUE, applied_at = NOW()
                WHERE resolution_id = %s
                RETURNING *
                """,
                (resolution_id,)
            )
            row = cursor.fetchone()
            self.conn.commit()

            return self._map_resolution_row(row) if row else None

    def rollback_sync(
        self,
        sync_id: str,
        user_id: str,
        reason: Optional[str] = None
    ) -> None:
        """
        Mark sync as rolled back.

        Updates the associated sync operation to ROLLED_BACK status,
        recording the user who performed the rollback and optional reason.

        Args:
            sync_id: Sync operation ID to rollback
            user_id: User ID performing the rollback
            reason: Optional rollback reason

        Returns:
            None (updates sync operation in place)
        """
        from app.repositories.i18n_sync_ops import SyncStatus

        updates = {
            'status': SyncStatus.ROLLED_BACK.value,
            'rolled_back_by_user_id': user_id,
            'rolled_back_at': datetime.utcnow(),
            'rollback_reason': reason
        }

        with self.conn.cursor(row_factory=dict_row) as cursor:
            set_clauses = []
            params = []

            for key, value in updates.items():
                set_clauses.append(f"{key} = %s")
                params.append(value)

            set_sql = ", ".join(set_clauses)
            params.append(sync_id)

            cursor.execute(
                f"""
                UPDATE i18n.i18n_syncs
                SET {set_sql}, updated_at = NOW()
                WHERE sync_id = %s
                """,
                params
            )
            self.conn.commit()

    @staticmethod
    def _map_resolution_row(row: Dict[str, Any]) -> SyncResolution:
        """Map database row to SyncResolution dataclass."""
        return SyncResolution(
            resolution_id=row['resolution_id'],
            sync_id=str(row['sync_id']),
            change_id=row['change_id'],
            translation_key=row['translation_key'],
            language_code=row['language_code'],
            chosen_action=row['chosen_action'],
            decided_by_user_id=str(row['decided_by_user_id']),
            decided_at=row['decided_at'],
            decision_notes=row['decision_notes'],
            applied=row['applied'],
            applied_at=row['applied_at']
        )
