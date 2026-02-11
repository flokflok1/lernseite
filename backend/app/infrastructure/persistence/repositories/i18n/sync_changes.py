"""
i18n Sync Changes Repository - Change detection and tracking.

Handles all database operations for detected translation changes, including:
- Recording detected changes (NEW, CHANGED, DELETED, CONFLICT)
- Retrieving individual changes
- Listing and filtering changes
- Updating change resolution status

Uses psycopg3 with direct SQL and parameterized queries (NO ORM).
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import psycopg
from psycopg.rows import dict_row


class ChangeType(str, Enum):
    """Type of translation change detected."""
    NEW = "NEW"
    CHANGED = "CHANGED"
    DELETED = "DELETED"
    CONFLICT = "CONFLICT"


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


class SyncChangesRepository:
    """
    Repository for managing translation sync changes.

    Handles operations for change detection and tracking, including:
    - Creating change records for detected differences
    - Retrieving individual changes
    - Listing and filtering changes by sync, type, or language
    - Updating change resolution status
    """

    def __init__(self, connection: psycopg.Connection):
        """Initialize repository with database connection."""
        self.conn = connection

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
