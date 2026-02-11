"""
LernsystemX Base Repository

Provides generic CRUD operations for all repositories.
Implements DRY principle and standard database operations.

ISO 9001:2015 compliant - Standardized data access
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    insert_returning,
    update_returning,
    delete_returning,
    execute_query
)


class BaseRepository:
    """
    Base repository with generic CRUD operations

    Subclasses should define:
    - table_name: Name of the database table
    - pk_column: Name of the primary key column (default: 'id')

    Example:
        >>> class CourseRepository(BaseRepository):
        ...     table_name = 'courses'
        ...     pk_column = 'course_id'
    """

    table_name: str = None
    pk_column: str = 'id'

    @classmethod
    def find_by_id(cls, id_value: int) -> Optional[Dict]:
        """
        Find record by primary key

        Args:
            id_value: Primary key value

        Returns:
            Record as dictionary or None

        Example:
            >>> user = UserRepository.find_by_id(123)
            >>> print(user['email'])
        """
        if not cls.table_name:
            raise NotImplementedError("table_name must be defined")

        query = f"SELECT * FROM {cls.table_name} WHERE {cls.pk_column} = %s"
        return fetch_one(query, (id_value,))

    @classmethod
    def find_all(
        cls,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: Optional[str] = None
    ) -> List[Dict]:
        """
        Find all records

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            order_by: Column to order by (e.g., 'created_at DESC')

        Returns:
            List of records as dictionaries

        Example:
            >>> users = UserRepository.find_all(limit=10, order_by='created_at DESC')
        """
        if not cls.table_name:
            raise NotImplementedError("table_name must be defined")

        query = f"SELECT * FROM {cls.table_name}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        if offset:
            query += f" OFFSET {offset}"

        return fetch_all(query)

    @classmethod
    def find_by(cls, **conditions) -> Optional[Dict]:
        """
        Find single record by conditions

        Args:
            **conditions: Column-value pairs for WHERE clause

        Returns:
            Record as dictionary or None

        Example:
            >>> user = UserRepository.find_by(email='user@example.com')
            >>> user = UserRepository.find_by(role='admin', is_active=True)
        """
        if not cls.table_name:
            raise NotImplementedError("table_name must be defined")

        if not conditions:
            raise ValueError("At least one condition must be provided")

        where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
        params = tuple(conditions.values())

        query = f"SELECT * FROM {cls.table_name} WHERE {where_clause}"
        return fetch_one(query, params)

    @classmethod
    def find_all_by(
        cls,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: Optional[str] = None,
        **conditions
    ) -> List[Dict]:
        """
        Find all records matching conditions

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            order_by: Column to order by
            **conditions: Column-value pairs for WHERE clause

        Returns:
            List of records as dictionaries

        Example:
            >>> active_users = UserRepository.find_all_by(
            ...     is_active=True,
            ...     limit=10,
            ...     order_by='created_at DESC'
            ... )
        """
        if not cls.table_name:
            raise NotImplementedError("table_name must be defined")

        if not conditions:
            return cls.find_all(limit=limit, offset=offset, order_by=order_by)

        where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
        params = tuple(conditions.values())

        query = f"SELECT * FROM {cls.table_name} WHERE {where_clause}"

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit:
            query += f" LIMIT {limit}"

        if offset:
            query += f" OFFSET {offset}"

        return fetch_all(query, params)

    @classmethod
    def create(cls, data: Dict[str, Any], returning: str = "*") -> Optional[Dict]:
        """
        Create new record

        Args:
            data: Dictionary of column-value pairs
            returning: Columns to return (default: *)

        Returns:
            Created record as dictionary

        Example:
            >>> user = UserRepository.create({
            ...     'email': 'user@example.com',
            ...     'password_hash': 'hashed_password',
            ...     'role': 'user'
            ... })
            >>> print(f"Created user with ID: {user['user_id']}")
        """
        if not cls.table_name:
            raise NotImplementedError("table_name must be defined")

        return insert_returning(cls.table_name, data, returning)

    @classmethod
    def update(
        cls,
        id_value: int,
        data: Dict[str, Any],
        returning: str = "*"
    ) -> Optional[Dict]:
        """
        Update record by primary key

        Args:
            id_value: Primary key value
            data: Dictionary of column-value pairs to update
            returning: Columns to return (default: *)

        Returns:
            Updated record as dictionary

        Example:
            >>> user = UserRepository.update(
            ...     123,
            ...     {'last_login': datetime.utcnow()}
            ... )
        """
        if not cls.table_name:
            raise NotImplementedError("table_name must be defined")

        # Add updated_at timestamp if column exists
        if 'updated_at' not in data:
            data['updated_at'] = datetime.utcnow()

        where = f"{cls.pk_column} = %s"
        return update_returning(cls.table_name, data, where, (id_value,), returning)

    @classmethod
    def update_by(
        cls,
        data: Dict[str, Any],
        returning: str = "*",
        **conditions
    ) -> Optional[Dict]:
        """
        Update record by conditions

        Args:
            data: Dictionary of column-value pairs to update
            returning: Columns to return (default: *)
            **conditions: Column-value pairs for WHERE clause

        Returns:
            Updated record as dictionary

        Example:
            >>> user = UserRepository.update_by(
            ...     {'is_verified': True},
            ...     email='user@example.com'
            ... )
        """
        if not cls.table_name:
            raise NotImplementedError("table_name must be defined")

        if not conditions:
            raise ValueError("At least one condition must be provided")

        # Add updated_at timestamp
        if 'updated_at' not in data:
            data['updated_at'] = datetime.utcnow()

        where = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
        where_params = tuple(conditions.values())

        return update_returning(cls.table_name, data, where, where_params, returning)

    @classmethod
    def delete(cls, id_value: int, returning: str = "*") -> Optional[Dict]:
        """
        Delete record by primary key

        Args:
            id_value: Primary key value
            returning: Columns to return (default: *)

        Returns:
            Deleted record as dictionary

        Example:
            >>> deleted_user = UserRepository.delete(123)
        """
        if not cls.table_name:
            raise NotImplementedError("table_name must be defined")

        where = f"{cls.pk_column} = %s"
        return delete_returning(cls.table_name, where, (id_value,), returning)

    @classmethod
    def delete_by(cls, returning: str = "*", **conditions) -> Optional[Dict]:
        """
        Delete record by conditions

        Args:
            returning: Columns to return (default: *)
            **conditions: Column-value pairs for WHERE clause

        Returns:
            Deleted record as dictionary

        Example:
            >>> deleted = UserRepository.delete_by(email='old@example.com')
        """
        if not cls.table_name:
            raise NotImplementedError("table_name must be defined")

        if not conditions:
            raise ValueError("At least one condition must be provided")

        where = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
        where_params = tuple(conditions.values())

        return delete_returning(cls.table_name, where, where_params, returning)

    @classmethod
    def exists(cls, **conditions) -> bool:
        """
        Check if record exists

        Args:
            **conditions: Column-value pairs for WHERE clause

        Returns:
            bool: True if record exists, False otherwise

        Example:
            >>> if UserRepository.exists(email='user@example.com'):
            ...     print("User already exists")
        """
        if not cls.table_name:
            raise NotImplementedError("table_name must be defined")

        if not conditions:
            raise ValueError("At least one condition must be provided")

        where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
        params = tuple(conditions.values())

        query = f"""
            SELECT EXISTS(
                SELECT 1 FROM {cls.table_name} WHERE {where_clause}
            )
        """

        result = fetch_one(query, params)
        return result['exists'] if result else False

    @classmethod
    def count(cls, **conditions) -> int:
        """
        Count records matching conditions

        Args:
            **conditions: Column-value pairs for WHERE clause (optional)

        Returns:
            int: Number of records

        Example:
            >>> total_users = UserRepository.count()
            >>> active_users = UserRepository.count(is_active=True)
        """
        if not cls.table_name:
            raise NotImplementedError("table_name must be defined")

        if conditions:
            where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
            params = tuple(conditions.values())
            query = f"SELECT COUNT(*) FROM {cls.table_name} WHERE {where_clause}"
            result = fetch_one(query, params)
        else:
            query = f"SELECT COUNT(*) FROM {cls.table_name}"
            result = fetch_one(query)

        return result['count'] if result else 0

    @classmethod
    def paginate(
        cls,
        page: int = 1,
        per_page: int = 20,
        order_by: Optional[str] = None,
        **conditions
    ) -> Dict[str, Any]:
        """
        Paginate records

        Args:
            page: Page number (1-indexed)
            per_page: Records per page
            order_by: Column to order by
            **conditions: Column-value pairs for WHERE clause

        Returns:
            Dictionary with:
            - items: List of records
            - total: Total number of records
            - page: Current page
            - per_page: Records per page
            - total_pages: Total number of pages

        Example:
            >>> result = UserRepository.paginate(
            ...     page=2,
            ...     per_page=10,
            ...     order_by='created_at DESC',
            ...     is_active=True
            ... )
            >>> print(f"Page {result['page']} of {result['total_pages']}")
            >>> for user in result['items']:
            ...     print(user['email'])
        """
        total = cls.count(**conditions)
        offset = (page - 1) * per_page

        items = cls.find_all_by(
            limit=per_page,
            offset=offset,
            order_by=order_by,
            **conditions
        )

        total_pages = (total + per_page - 1) // per_page  # Ceiling division

        return {
            'items': items,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages
        }
