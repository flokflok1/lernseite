"""
Base Repository Pattern

Abstract base class for all repositories following DDD principles.
NO ORM - all queries are direct SQL with psycopg3.
"""

from typing import Any, Dict, List, Optional, Tuple
from abc import ABC
from src.infrastructure.database.connection import DatabaseConnection


class BaseRepository(ABC):
    """
    Base repository for database access.

    All repositories must inherit from this class and use parameterized queries.
    SQL injection prevention is enforced through parameterized queries only.

    Example:
        class UserRepository(BaseRepository):
            @staticmethod
            def find_by_id(user_id: str) -> Optional[Dict[str, Any]]:
                query = "SELECT * FROM users WHERE user_id = %s"
                return BaseRepository.fetch_one(query, (user_id,))
    """

    @staticmethod
    def fetch_one(query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Fetch single row.

        Args:
            query: SQL query with %s placeholders
            params: Query parameters tuple

        Returns:
            Dictionary with row data or None
        """
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()

    @staticmethod
    def fetch_all(query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """
        Fetch multiple rows.

        Args:
            query: SQL query with %s placeholders
            params: Query parameters tuple

        Returns:
            List of dictionaries with row data
        """
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchall()

    @staticmethod
    def execute(query: str, params: Tuple = ()) -> int:
        """
        Execute INSERT/UPDATE/DELETE query.

        Args:
            query: SQL query with %s placeholders
            params: Query parameters tuple

        Returns:
            Number of affected rows
        """
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return cur.rowcount

    @staticmethod
    def execute_returning(query: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        """
        Execute INSERT/UPDATE query with RETURNING clause.

        Args:
            query: SQL query with %s placeholders and RETURNING clause
            params: Query parameters tuple

        Returns:
            Dictionary with returned row data
        """
        with DatabaseConnection.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                conn.commit()
                return cur.fetchone()
