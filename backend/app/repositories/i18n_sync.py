"""
i18n Sync Repository - Data access layer for translation synchronization.

Implements the Repository Pattern for all database operations related to
i18n sync tracking, change management, and resolution handling.

No ORM - Uses psycopg3 with direct SQL and parameterized queries.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from uuid import UUID
import psycopg
from psycopg.rows import dict_row
from dataclasses import dataclass, field, asdict
from enum import Enum


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


class ChangeType(str, Enum):
    """Type of translation change detected."""
    NEW = "NEW"
    CHANGED = "CHANGED"
    DELETED = "DELETED"
    CONFLICT = "CONFLICT"


class Resolution(str, Enum):
    """User resolution action."""
    ADD = "ADD"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SKIP = "SKIP"


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


@dataclass
class SyncChange:
    """Represents a detected translation change."""

    change_id: int
    sync_id: str
    translation_key: str
    language_code: str
    change_type: str
    frontend_value: Optional[str] = None
    database_value: Optional[str] = None
    previous_value: Optional[str] = None
    similarity_score: float = 0.0
    resolution: Optional[str] = None
    resolution_notes: Optional[str] = None
    resolved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'change_id': self.change_id,
            'sync_id': self.sync_id,
            'translation_key': self.translation_key,
            'language_code': self.language_code,
            'change_type': self.change_type,
            'frontend_value': self.frontend_value,
            'database_value': self.database_value,
            'previous_value': self.previous_value,
            'similarity_score': self.similarity_score,
            'resolution': self.resolution,
            'resolution_notes': self.resolution_notes,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


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


class SyncRepository:
    """
    Repository for managing translation sync operations.

    Handles all database operations for sync tracking, including:
    - Creating and retrieving sync operations
    - Tracking changes (NEW, CHANGED, DELETED, CONFLICT)
    - Recording user resolutions
    - Querying sync history and statistics
    - Supporting rollback operations
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
            count_sql = f"SELECT COUNT(*) as total FROM i18n.i18n_syncs {where_sql.replace('LIMIT', '').replace('OFFSET', '')}"
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

    def create_change(
        self,
        sync_id: str,
        translation_key: str,
        language_code: str,
        change_type: str,
        frontend_value: Optional[str] = None,
        database_value: Optional[str] = None,
        previous_value: Optional[str] = None,
        similarity_score: float = 0.0
    ) -> SyncChange:
        """
        Create sync change record.

        Args:
            sync_id: Associated sync operation ID
            translation_key: Translation key (e.g., 'admin.users.title')
            language_code: Language code (de, en, pl)
            change_type: Type of change (NEW, CHANGED, DELETED, CONFLICT)
            frontend_value: Current frontend translation value
            database_value: Current database translation value
            previous_value: Previous database value
            similarity_score: Similarity score (0.0-1.0) for conflicts

        Returns:
            Created SyncChange instance
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO i18n.sync_changes
                (sync_id, translation_key, language_code, change_type,
                 frontend_value, database_value, previous_value, similarity_score)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *
                """,
                (
                    sync_id, translation_key, language_code, change_type,
                    frontend_value, database_value, previous_value, similarity_score
                )
            )
            row = cursor.fetchone()
            self.conn.commit()

            return self._map_change_row(row)

    def get_change(self, change_id: int) -> Optional[SyncChange]:
        """
        Get sync change by ID.

        Args:
            change_id: Change record ID

        Returns:
            SyncChange or None if not found
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT * FROM i18n.sync_changes WHERE change_id = %s",
                (change_id,)
            )
            row = cursor.fetchone()

            return self._map_change_row(row) if row else None

    def list_changes(
        self,
        sync_id: str,
        limit: int = 100,
        offset: int = 0,
        change_type: Optional[str] = None,
        language_code: Optional[str] = None
    ) -> Tuple[List[SyncChange], int]:
        """
        List changes for a sync operation.

        Args:
            sync_id: Sync operation ID
            limit: Max results
            offset: Results to skip
            change_type: Filter by change type
            language_code: Filter by language

        Returns:
            Tuple of (changes list, total count)
        """
        limit = min(limit, 100)

        where_clauses = ["sync_id = %s"]
        params = [sync_id]

        if change_type:
            where_clauses.append("change_type = %s")
            params.append(change_type)
        if language_code:
            where_clauses.append("language_code = %s")
            params.append(language_code)

        where_sql = " AND ".join(where_clauses)

        with self.conn.cursor(row_factory=dict_row) as cursor:
            # Get count
            cursor.execute(
                f"SELECT COUNT(*) as total FROM i18n.sync_changes WHERE {where_sql}",
                params
            )
            total = cursor.fetchone()['total']

            # Get changes
            params.extend([limit, offset])
            cursor.execute(
                f"""
                SELECT * FROM i18n.sync_changes
                WHERE {where_sql}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                params
            )
            rows = cursor.fetchall()

            changes = [self._map_change_row(row) for row in rows]
            return changes, total

    def update_change_resolution(
        self,
        change_id: int,
        resolution: str,
        notes: Optional[str] = None
    ) -> Optional[SyncChange]:
        """
        Update change resolution status.

        Args:
            change_id: Change record ID
            resolution: Resolution action (ADD, UPDATE, DELETE, SKIP)
            notes: Optional resolution notes

        Returns:
            Updated SyncChange or None if not found
        """
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                UPDATE i18n.sync_changes
                SET resolution = %s, resolution_notes = %s, resolved_at = NOW()
                WHERE change_id = %s
                RETURNING *
                """,
                (resolution, notes, change_id)
            )
            row = cursor.fetchone()
            self.conn.commit()

            return self._map_change_row(row) if row else None

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
            translation_key: Translation key
            language_code: Language code
            chosen_action: User's chosen action (ADD, UPDATE, DELETE, SKIP)
            user_id: User making the resolution
            notes: Optional decision notes

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
            applied: Filter by applied status
            limit: Max results
            offset: Results to skip

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
    ) -> Optional[SyncOperation]:
        """
        Mark sync as rolled back.

        Args:
            sync_id: Sync operation ID
            user_id: User performing rollback
            reason: Optional rollback reason

        Returns:
            Updated SyncOperation or None if not found
        """
        updates = {
            'status': SyncStatus.ROLLED_BACK.value,
            'rolled_back_by_user_id': user_id,
            'rolled_back_at': datetime.utcnow(),
            'rollback_reason': reason
        }

        return self.update_sync_status(sync_id, SyncStatus.ROLLED_BACK.value, updates)

    # Helper methods

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

    @staticmethod
    def _map_change_row(row: Dict[str, Any]) -> SyncChange:
        """Map database row to SyncChange dataclass."""
        return SyncChange(
            change_id=row['change_id'],
            sync_id=str(row['sync_id']),
            translation_key=row['translation_key'],
            language_code=row['language_code'],
            change_type=row['change_type'],
            frontend_value=row['frontend_value'],
            database_value=row['database_value'],
            previous_value=row['previous_value'],
            similarity_score=row['similarity_score'],
            resolution=row['resolution'],
            resolution_notes=row['resolution_notes'],
            resolved_at=row['resolved_at'],
            created_at=row['created_at']
        )

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
