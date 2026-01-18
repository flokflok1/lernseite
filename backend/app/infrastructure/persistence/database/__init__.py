"""
LernsystemX Database Package

Provides database connection management and utilities for psycopg.
Implements connection pooling and context managers for safe database access.

ISO 9001:2015 compliant - Database access management
"""

from app.infrastructure.persistence.database.connection import (
    get_connection,
    get_db_connection,  # Backward compatibility alias
    get_cursor,
    execute_query,
    execute_many,
    fetch_one,
    fetch_all,
    DatabaseConnection
)

__all__ = [
    'get_connection',
    'get_db_connection',  # Backward compatibility alias
    'get_cursor',
    'execute_query',
    'execute_many',
    'fetch_one',
    'fetch_all',
    'DatabaseConnection'
]
