"""
Learning Method Repository - Base CRUD Operations

Core data access layer for learning method CRUD operations:
- get_all: List all/active methods with caching
- find_by_id: Get method by UUID
- find_by_name: Get method by title
- create: Create new method
- update: Update method data
- delete: Remove method
- activate/deactivate: Publish state management

Uses BaseRepository for connection pooling and psycopg for SQL.
"""

from typing import Dict, Any, Optional, List
import psycopg
from psycopg.rows import dict_row

from app.extensions import db_pool
from app.services.cache_service import CacheService
from flask import current_app


class LearningMethodBaseRepository:
    """
    Base CRUD operations for learning methods.

    All methods use psycopg connection pool and return dictionaries.
    """

    @classmethod
    def get_all(cls, active_only: bool = False, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get all learning methods with optional caching.

        Args:
            active_only: Only return active methods
            use_cache: Use cache (default: True)

        Returns:
            List of learning method dictionaries
        """
        if use_cache:
            cache_suffix = 'active' if active_only else 'all'
            cache_key = CacheService.make_key('METHODS', 'list', cache_suffix)
            ttl = current_app.config.get('CACHE_LEARNING_METHOD_TTL', 3600)

            def load_methods():
                with db_pool.connection() as conn:
                    with conn.cursor(row_factory=dict_row) as cur:
                        query = """
                            SELECT
                                lm.method_id,
                                lm.method_type,
                                lm.title as name,
                                lm.instructions as description,
                                lm.tier,
                                lm.data as config,
                                lm.published as active,
                                lm.created_at,
                                lm.updated_at,
                                0 as usage_count
                            FROM learning_methods lm
                        """
                        if active_only:
                            query += " WHERE lm.published = TRUE"
                        query += " ORDER BY lm.tier, lm.title"

                        cur.execute(query)
                        return cur.fetchall()

            return CacheService.cache_get_or_set(cache_key, ttl, load_methods)

        # Bypass cache
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                query = """
                    SELECT
                        lm.method_id,
                        lm.method_type,
                        lm.title as name,
                        lm.instructions as description,
                        lm.tier,
                        lm.data as config,
                        lm.published as active,
                        lm.created_at,
                        lm.updated_at,
                        0 as usage_count
                    FROM learning_methods lm
                """
                if active_only:
                    query += " WHERE lm.published = TRUE"
                query += " ORDER BY lm.tier, lm.title"

                cur.execute(query)
                return cur.fetchall()

    @classmethod
    def find_by_id(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """
        Find learning method by ID.

        Args:
            method_id: Learning method UUID

        Returns:
            Learning method dictionary or None
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        lm.method_id,
                        lm.method_type,
                        lm.title as name,
                        lm.instructions as description,
                        lm.tier,
                        lm.data as config,
                        lm.published as active,
                        lm.created_at,
                        lm.updated_at,
                        0 as usage_count
                    FROM learning_methods lm
                    WHERE lm.method_id = %s
                """, (method_id,))

                return cur.fetchone()

    @classmethod
    def find_by_name(cls, name: str) -> Optional[Dict[str, Any]]:
        """
        Find learning method by name (title).

        Args:
            name: Learning method title

        Returns:
            Learning method dictionary or None
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    SELECT
                        method_id,
                        method_type,
                        title as name,
                        instructions as description,
                        tier,
                        data as config,
                        published as active,
                        created_at,
                        updated_at
                    FROM learning_methods
                    WHERE title = %s
                """, (name,))

                return cur.fetchone()

    @classmethod
    def create(cls, method_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new learning method.

        Args:
            method_data: Learning method data with keys: name, description, tier, config, active

        Returns:
            Created learning method dictionary
        """
        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                cur.execute("""
                    INSERT INTO learning_methods (
                        name, description, tier, config, active
                    ) VALUES (%s, %s, %s, %s, %s)
                    RETURNING *
                """, (
                    method_data['name'],
                    method_data.get('description'),
                    method_data['tier'],
                    psycopg.types.json.Jsonb(method_data.get('config', {})),
                    method_data.get('active', True)
                ))

                conn.commit()
                result = cur.fetchone()

                if result:
                    CacheService.invalidate_learning_methods_cache()

                return result

    @classmethod
    def update(cls, method_id: str, method_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update learning method.

        Args:
            method_id: Learning method ID
            method_data: Updated data (dynamic fields)

        Returns:
            Updated learning method or None
        """
        update_fields = []
        params = []

        for key, value in method_data.items():
            if key == 'config':
                update_fields.append(f"{key} = %s")
                params.append(psycopg.types.json.Jsonb(value))
            else:
                update_fields.append(f"{key} = %s")
                params.append(value)

        if not update_fields:
            return cls.find_by_id(method_id)

        params.append(method_id)

        with db_pool.connection() as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                query = f"""
                    UPDATE learning_methods
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE method_id = %s
                    RETURNING *
                """

                cur.execute(query, params)
                conn.commit()
                result = cur.fetchone()

                if result:
                    CacheService.invalidate_learning_methods_cache()

                return result

    @classmethod
    def delete(cls, method_id: str) -> bool:
        """
        Delete learning method (hard delete).

        Args:
            method_id: Learning method ID

        Returns:
            True if deleted, False if not found
        """
        with db_pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    DELETE FROM learning_methods
                    WHERE method_id = %s
                """, (method_id,))

                conn.commit()
                deleted = cur.rowcount > 0

                if deleted:
                    CacheService.invalidate_learning_methods_cache()

                return deleted

    @classmethod
    def activate(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """Activate learning method (set published=TRUE)."""
        return cls.update(method_id, {'active': True})

    @classmethod
    def deactivate(cls, method_id: str) -> Optional[Dict[str, Any]]:
        """Deactivate learning method (set published=FALSE)."""
        return cls.update(method_id, {'active': False})
