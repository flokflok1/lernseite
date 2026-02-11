"""
LernsystemX Audit Log Repository

Provides data access for audit logging across the system.
Stores audit trails for compliance, debugging, and analytics.

ISO 27001:2013 compliant - Audit trail and logging
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from psycopg.rows import dict_row

from app.infrastructure.persistence.repositories.core.base import BaseRepository


class AuditLogRepository(BaseRepository):
    """
    Repository for audit log records.

    Handles storage and retrieval of audit trail entries
    for all system changes, feature modifications, and user actions.
    """

    def __init__(self, connection):
        super().__init__(connection)
        self.table_name = "audit_logs"
        self.model_class = dict

    def find_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """Find audit log by ID."""
        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"SELECT * FROM {self.table_name} WHERE id = %s",
                (log_id,)
            )
            return cursor.fetchone()

    def find_all(
        self,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at DESC"
    ) -> List[Dict[str, Any]]:
        """Find all audit logs with pagination."""
        if limit > 1000:
            limit = 1000

        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""
                SELECT * FROM {self.table_name}
                ORDER BY {order_by}
                LIMIT %s OFFSET %s
                """,
                (limit, offset)
            )
            return cursor.fetchall()

    def find_by(
        self,
        filters: Dict[str, Any],
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Find audit logs by filters."""
        if not filters:
            return self.find_all(limit=limit, offset=offset)

        # Build WHERE clause
        where_clauses = []
        params = []

        for field, value in filters.items():
            if field.endswith('_gte'):
                # Greater than or equal
                field_name = field[:-4]
                where_clauses.append(f"{field_name} >= %s")
            elif field.endswith('_lte'):
                # Less than or equal
                field_name = field[:-4]
                where_clauses.append(f"{field_name} <= %s")
            else:
                where_clauses.append(f"{field} = %s")
            params.append(value)

        where_sql = " AND ".join(where_clauses)
        params.extend([limit, offset])

        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""
                SELECT * FROM {self.table_name}
                WHERE {where_sql}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                params
            )
            return cursor.fetchall()

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new audit log entry."""
        fields = list(data.keys())
        values = list(data.values())
        placeholders = ["%s"] * len(fields)

        fields_sql = ", ".join(fields)
        placeholders_sql = ", ".join(placeholders)

        with self.conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                f"""
                INSERT INTO {self.table_name} ({fields_sql})
                VALUES ({placeholders_sql})
                RETURNING *
                """,
                values
            )
            row = cursor.fetchone()
            self.conn.commit()

            return row

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count audit log records."""
        with self.conn.cursor() as cursor:
            if filters:
                where_clauses = []
                params = []

                for field, value in filters.items():
                    if field.endswith('_gte'):
                        field_name = field[:-4]
                        where_clauses.append(f"{field_name} >= %s")
                    elif field.endswith('_lte'):
                        field_name = field[:-4]
                        where_clauses.append(f"{field_name} <= %s")
                    else:
                        where_clauses.append(f"{field} = %s")
                    params.append(value)

                where_sql = " AND ".join(where_clauses)

                cursor.execute(
                    f"SELECT COUNT(*) FROM {self.table_name} WHERE {where_sql}",
                    params
                )
            else:
                cursor.execute(f"SELECT COUNT(*) FROM {self.table_name}")

            return cursor.fetchone()[0]
