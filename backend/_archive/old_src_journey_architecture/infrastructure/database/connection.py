"""
Database Connection Pool

Manages PostgreSQL connection pooling using psycopg3.
NO ORM - direct SQL with parameterized queries only.
"""

import os
from typing import Optional
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool


class DatabaseConnection:
    """
    Database connection pool manager.

    Uses psycopg3 with connection pooling for optimal performance.
    All queries must use parameterized format to prevent SQL injection.
    """

    _pool: Optional[ConnectionPool] = None

    @classmethod
    def initialize(cls, database_url: str, min_size: int = 5, max_size: int = 20) -> None:
        """
        Initialize connection pool.

        Args:
            database_url: PostgreSQL connection URL
            min_size: Minimum pool size
            max_size: Maximum pool size
        """
        if cls._pool is None:
            cls._pool = ConnectionPool(
                conninfo=database_url,
                min_size=min_size,
                max_size=max_size,
                kwargs={'row_factory': dict_row}
            )

    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        Get database connection from pool.

        Yields:
            Database connection with dict_row factory

        Example:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                    result = cur.fetchone()
        """
        if cls._pool is None:
            raise RuntimeError("Database pool not initialized. Call initialize() first.")

        with cls._pool.connection() as conn:
            yield conn

    @classmethod
    def close(cls) -> None:
        """Close connection pool."""
        if cls._pool:
            cls._pool.close()
            cls._pool = None
