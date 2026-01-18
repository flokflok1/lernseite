"""
LernsystemX Database Connection Management

Provides connection pool wrapper and utility functions for psycopg.
Implements context managers for safe database access.

ISO 9001:2015 compliant - Resource management
"""

from typing import Optional, List, Dict, Any, Tuple
from contextlib import contextmanager
from psycopg.rows import dict_row

import app.extensions  # Import module, not the variable directly


class DatabaseConnection:
    """
    Context manager for database connections

    Example:
        >>> with DatabaseConnection() as conn:
        ...     with conn.cursor() as cur:
        ...         cur.execute("SELECT * FROM users")
        ...         users = cur.fetchall()
    """

    def __enter__(self):
        """Get connection from pool"""
        if app.extensions.db_pool is None:
            raise RuntimeError("Database pool not initialized")
        self.conn = app.extensions.db_pool.getconn()
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Return connection to pool"""
        if exc_type is not None:
            # Rollback on error
            self.conn.rollback()
        else:
            # Commit on success
            self.conn.commit()

        app.extensions.db_pool.putconn(self.conn)


@contextmanager
def get_connection():
    """
    Get database connection from pool (context manager)

    Yields:
        psycopg.Connection: Database connection

    Example:
        >>> with get_connection() as conn:
        ...     with conn.cursor() as cur:
        ...         cur.execute("SELECT 1")
    """
    if app.extensions.db_pool is None:
        raise RuntimeError("Database pool not initialized")

    conn = app.extensions.db_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        app.extensions.db_pool.putconn(conn)


@contextmanager
def get_cursor(row_factory=dict_row):
    """
    Get database cursor with automatic connection management

    Args:
        row_factory: Row factory (default: dict_row for dictionary results)

    Yields:
        psycopg.Cursor: Database cursor

    Example:
        >>> with get_cursor() as cur:
        ...     cur.execute("SELECT * FROM users WHERE user_id = %s", (1,))
        ...     user = cur.fetchone()
        ...     print(user['email'])
    """
    with get_connection() as conn:
        with conn.cursor(row_factory=row_factory) as cur:
            yield cur


def execute_query(
    query: str,
    params: Optional[Tuple] = None,
    fetch: bool = False,
    fetch_one: bool = False,
    row_factory=dict_row
) -> Optional[Any]:
    """
    Execute a SQL query with automatic connection management

    Args:
        query: SQL query string
        params: Query parameters (tuple)
        fetch: Whether to fetch all results
        fetch_one: Whether to fetch only one result
        row_factory: Row factory for results

    Returns:
        Query results or None

    Example:
        >>> # Insert
        >>> execute_query(
        ...     "INSERT INTO users (email, name) VALUES (%s, %s)",
        ...     ("user@example.com", "User")
        ... )

        >>> # Select one
        >>> user = execute_query(
        ...     "SELECT * FROM users WHERE email = %s",
        ...     ("user@example.com",),
        ...     fetch_one=True
        ... )

        >>> # Select all
        >>> users = execute_query(
        ...     "SELECT * FROM users WHERE is_active = %s",
        ...     (True,),
        ...     fetch=True
        ... )
    """
    with get_cursor(row_factory=row_factory) as cur:
        cur.execute(query, params or ())

        if fetch_one:
            return cur.fetchone()
        elif fetch:
            return cur.fetchall()

        return None


def execute_many(query: str, params_list: List[Tuple]) -> None:
    """
    Execute a SQL query multiple times with different parameters

    Args:
        query: SQL query string
        params_list: List of parameter tuples

    Example:
        >>> execute_many(
        ...     "INSERT INTO users (email, name) VALUES (%s, %s)",
        ...     [
        ...         ("user1@example.com", "User 1"),
        ...         ("user2@example.com", "User 2"),
        ...         ("user3@example.com", "User 3")
        ...     ]
        ... )
    """
    with get_cursor() as cur:
        cur.executemany(query, params_list)


def fetch_one(query: str, params: Optional[Tuple] = None, row_factory=dict_row) -> Optional[Dict]:
    """
    Fetch single row from database

    Args:
        query: SQL query string
        params: Query parameters
        row_factory: Row factory for result

    Returns:
        Single row as dictionary or None

    Example:
        >>> user = fetch_one(
        ...     "SELECT * FROM users WHERE user_id = %s",
        ...     (1,)
        ... )
        >>> print(user['email'])
    """
    return execute_query(query, params, fetch_one=True, row_factory=row_factory)


def fetch_all(query: str, params: Optional[Tuple] = None, row_factory=dict_row) -> List[Dict]:
    """
    Fetch all rows from database

    Args:
        query: SQL query string
        params: Query parameters
        row_factory: Row factory for results

    Returns:
        List of rows as dictionaries

    Example:
        >>> users = fetch_all(
        ...     "SELECT * FROM users WHERE role = %s",
        ...     ('admin',)
        ... )
        >>> for user in users:
        ...     print(user['email'])
    """
    result = execute_query(query, params, fetch=True, row_factory=row_factory)
    return result if result is not None else []


def insert_returning(
    table: str,
    data: Dict[str, Any],
    returning: str = "*"
) -> Optional[Dict]:
    """
    Insert row and return inserted data

    Args:
        table: Table name
        data: Dictionary of column: value pairs
        returning: Columns to return (default: *)

    Returns:
        Inserted row as dictionary

    Example:
        >>> user = insert_returning(
        ...     'users',
        ...     {
        ...         'email': 'user@example.com',
        ...         'password_hash': 'hashed_password',
        ...         'role': 'user'
        ...     },
        ...     returning='user_id, email'
        ... )
        >>> print(f"Created user {user['user_id']}")
    """
    columns = list(data.keys())
    placeholders = ', '.join(['%s'] * len(columns))
    column_str = ', '.join(columns)

    query = f"""
        INSERT INTO {table} ({column_str})
        VALUES ({placeholders})
        RETURNING {returning}
    """

    params = tuple(data.values())
    return fetch_one(query, params)


def update_returning(
    table: str,
    data: Dict[str, Any],
    where: str,
    where_params: Tuple,
    returning: str = "*"
) -> Optional[Dict]:
    """
    Update row and return updated data

    Args:
        table: Table name
        data: Dictionary of column: value pairs to update
        where: WHERE clause (without WHERE keyword)
        where_params: Parameters for WHERE clause
        returning: Columns to return (default: *)

    Returns:
        Updated row as dictionary

    Example:
        >>> user = update_returning(
        ...     'users',
        ...     {'last_login': datetime.utcnow()},
        ...     'user_id = %s',
        ...     (123,),
        ...     returning='user_id, last_login'
        ... )
    """
    set_clause = ', '.join([f"{col} = %s" for col in data.keys()])

    query = f"""
        UPDATE {table}
        SET {set_clause}
        WHERE {where}
        RETURNING {returning}
    """

    params = tuple(data.values()) + where_params
    return fetch_one(query, params)


def delete_returning(
    table: str,
    where: str,
    where_params: Tuple,
    returning: str = "*"
) -> Optional[Dict]:
    """
    Delete row and return deleted data

    Args:
        table: Table name
        where: WHERE clause (without WHERE keyword)
        where_params: Parameters for WHERE clause
        returning: Columns to return (default: *)

    Returns:
        Deleted row as dictionary

    Example:
        >>> deleted_user = delete_returning(
        ...     'users',
        ...     'user_id = %s',
        ...     (123,)
        ... )
    """
    query = f"""
        DELETE FROM {table}
        WHERE {where}
        RETURNING {returning}
    """

    return fetch_one(query, where_params)


def table_exists(table_name: str) -> bool:
    """
    Check if table exists in database

    Args:
        table_name: Name of table to check

    Returns:
        bool: True if table exists, False otherwise

    Example:
        >>> if table_exists('users'):
        ...     print("Users table exists")
    """
    result = fetch_one("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name = %s
        )
    """, (table_name,))

    return result['exists'] if result else False


# Backward compatibility alias (for legacy code using get_db_connection)
get_db_connection = get_connection
