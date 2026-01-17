"""
i18n Sync Operations Repository - Sync operation CRUD and status management.

Handles all database operations for sync tracking, including:
- Creating and retrieving sync operations
- Listing sync operations with filtering
- Updating sync status and metadata
- Recording sync completion

Uses psycopg3 with direct SQL and parameterized queries (NO ORM).
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import psycopg
from psycopg.rows import dict_row


class SyncMode(str, Enum):
    """Sync operation mode."""
    MANUAL = "MANUAL"
    AUTO = "AUTO"


class SyncStatus(str, Enum):
    """Sync operation status."""
    PENDING = "PENDING"
    SCANNING = "SCANNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


@dataclass
class SyncOperation:
    """Represents a translation synchronization operation."""

    sync_id: str
    mode: str
    status: str
    languages_synced: List[str]
    total_keys: int = 0
    new_keys: int = 0
    changed_keys: int = 0
    deleted_keys: int = 0
    conflicted_keys: int = 0
    scan_duration_ms: Optional[int] = None
    initiated_by_user_id: str = ""
    initiated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    rolled_back_by_user_id: Optional[str] = None
    rolled_back_at: Optional[datetime] = None
    rollback_reason: Optional[str] = None
    parent_sync_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'sync_id': self.sync_id,
            'mode': self.mode,
            'status': self.status,
            'languages_synced': self.languages_synced,
            'total_keys': self.total_keys,
            'new_keys': self.new_keys,
            'changed_keys': self.changed_keys,
            'deleted_keys': self.deleted_keys,
            'conflicted_keys': self.conflicted_keys,
            'scan_duration_ms': self.scan_duration_ms,
            'initiated_by_user_id': self.initiated_by_user_id,
            'initiated_at': self.initiated_at.isoformat() if self.initiated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'rolled_back_by_user_id': self.rolled_back_by_user_id,
            'rolled_back_at': self.rolled_back_at.isoformat() if self.rolled_back_at else None,
            'rollback_reason': self.rollback_reason,
            'parent_sync_id': self.parent_sync_id,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SyncOpsRepository:
    """
    Repository for managing translation sync operations.

    Handles CRUD operations for sync tracking, including:
    - Creating new sync operations
    - Retrieving sync operations by ID
    - Listing and filtering sync operations
    - Updating sync status and statistics
    """

    def __init__(self, connection: psycopg.Connection):
        """Initialize repository with database connection."""
        self.conn = connection

    def create_sync(
        self,
        mode: str,
        user_id: str,
        languages: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> SyncOperation:
        """
        Create new sync operation.

        Args:
            mode: 'MANUAL' or 'AUTO'
            user_id: User initiating the sync
            languages: List of language codes to sync (e.g., ['de', 'en', 'pl'])
            metadata: Optional metadata dictionary

        Returns:
            Created SyncOperation instance
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO i18n.i18n_syncs
                (mode, status, languages_synced, initiated_by_user_id, metadata)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING *
                """,
                (mode, SyncStatus.PENDING.value, languages, user_id, metadata or {})
            )
            row = cursor.fetchone()
            self.conn.commit()

            return self._map_sync_row(row)

    def get_sync(self, sync_id: str) -> Optional[SyncOperation]:
        """
        Get sync operation by ID.

        Args:
            sync_id: Sync operation ID (UUID)

        Returns:
            SyncOperation or None if not found
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * FROM i18n.i18n_syncs WHERE sync_id = %s",
                (sync_id,)
            )
            row = cursor.fetchone()

            return self._map_sync_row(row) if row else None

    def list_syncs(
        self,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
        mode: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Tuple[List[SyncOperation], int]:
        """
        List sync operations with optional filtering.

        Args:
            limit: Max results to return (default 20, max 100)
            offset: Results to skip (default 0)
            status: Filter by status (PENDING, SCANNING, COMPLETED, FAILED, ROLLED_BACK)
            mode: Filter by mode (MANUAL, AUTO)
            user_id: Filter by user who initiated sync

        Returns:
            Tuple of (syncs list, total count)
        """
        limit = min(limit, 100)

        # Build WHERE clause
        where_clauses = []
        params = []

        if status:
            where_clauses.append("status = %s")
            params.append(status)
        if mode:
            where_clauses.append("mode = %s")
            params.append(mode)
        if user_id:
            where_clauses.append("initiated_by_user_id = %s")
            params.append(user_id)

        where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
        params.extend([limit, offset])

        with self.conn.cursor(row_factory=dict_row) as cursor:
            # Get total count
            cursor.execute(
                f"SELECT COUNT(*) as total FROM i18n.i18n_syncs {where_sql.replace('LIMIT %s', '').replace('OFFSET %s', '')}",
                params[:-2] if where_sql else []
            )
            total = cursor.fetchone()['total']

            # Get syncs
            cursor.execute(
                f"""
                SELECT * FROM i18n.i18n_syncs
                {where_sql}
                ORDER BY initiated_at DESC
                LIMIT %s OFFSET %s
                """,
                params
            )
            rows = cursor.fetchall()

            syncs = [self._map_sync_row(row) for row in rows]
            return syncs, total

    def update_sync_status(
        self,
        sync_id: str,
        status: str,
        updates: Optional[Dict[str, Any]] = None
    ) -> Optional[SyncOperation]:
        """
        Update sync operation status and optional fields.

        Args:
            sync_id: Sync operation ID
            status: New status
            updates: Optional dictionary of additional fields to update

        Returns:
            Updated SyncOperation or None if not found
        """
        set_clauses = ["status = %s"]
        params = [status]

        if updates:
            for key, value in updates.items():
                set_clauses.append(f"{key} = %s")
                params.append(value)

        set_sql = ", ".join(set_clauses)
        params.append(sync_id)

        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""
                UPDATE i18n.i18n_syncs
                SET {set_sql}, updated_at = NOW()
                WHERE sync_id = %s
                RETURNING *
                """,
                params
            )
            row = cursor.fetchone()
            self.conn.commit()

            return self._map_sync_row(row) if row else None

    def complete_sync(
        self,
        sync_id: str,
        scan_duration_ms: int,
        statistics: Dict[str, int]
    ) -> Optional[SyncOperation]:
        """
        Mark sync as completed and update statistics.

        Args:
            sync_id: Sync operation ID
            scan_duration_ms: Scan duration in milliseconds
            statistics: Dict with keys: new_keys, changed_keys, deleted_keys, conflicted_keys

        Returns:
            Updated SyncOperation or None if not found
        """
        updates = {
            'status': SyncStatus.COMPLETED.value,
            'completed_at': datetime.utcnow(),
            'scan_duration_ms': scan_duration_ms,
            'total_keys': sum(statistics.values()),
            'new_keys': statistics.get('new_keys', 0),
            'changed_keys': statistics.get('changed_keys', 0),
            'deleted_keys': statistics.get('deleted_keys', 0),
            'conflicted_keys': statistics.get('conflicted_keys', 0)
        }

        return self.update_sync_status(sync_id, SyncStatus.COMPLETED.value, updates)

    @staticmethod
    def _map_sync_row(row: Dict[str, Any]) -> SyncOperation:
        """Map database row to SyncOperation dataclass."""
        return SyncOperation(
            sync_id=str(row['sync_id']),
            mode=row['mode'],
            status=row['status'],
            languages_synced=row['languages_synced'],
            total_keys=row['total_keys'],
            new_keys=row['new_keys'],
            changed_keys=row['changed_keys'],
            deleted_keys=row['deleted_keys'],
            conflicted_keys=row['conflicted_keys'],
            scan_duration_ms=row['scan_duration_ms'],
            initiated_by_user_id=str(row['initiated_by_user_id']),
            initiated_at=row['initiated_at'],
            completed_at=row['completed_at'],
            rolled_back_by_user_id=str(row['rolled_back_by_user_id']) if row['rolled_back_by_user_id'] else None,
            rolled_back_at=row['rolled_back_at'],
            rollback_reason=row['rollback_reason'],
            parent_sync_id=str(row['parent_sync_id']) if row['parent_sync_id'] else None,
            metadata=row['metadata'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
