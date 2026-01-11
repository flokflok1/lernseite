"""
Learning Method Repository (Infrastructure Layer)

Database access for learning methods (12 Content-LMs).
ALL data loaded dynamically from database - NO hardcoded values.

Handles:
- Learning Method Types (the 12 Content-LMs: LM00-LM11)
- Learning Method Instances (concrete instances in chapters)
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
import json
from datetime import datetime
from src.core.database import get_db_connection
from src.api.content.learning_methods.domain.entities.learning_method_type import LearningMethodType
from src.api.content.learning_methods.domain.entities.learning_method_instance import LearningMethodInstance


class LearningMethodRepository:
    """
    Repository for learning method database operations.

    ALL configurations loaded from database dynamically.
    NO hardcoded method types or configurations.
    """

    # ============================================================================
    # LEARNING METHOD TYPES (The 12 Content-LMs)
    # ============================================================================

    @staticmethod
    def find_type_by_id(type_id: int) -> Optional[LearningMethodType]:
        """
        Find learning method type by ID.

        Args:
            type_id: Type ID

        Returns:
            LearningMethodType or None
        """
        query = """
            SELECT type_id, method_type, name, description, group_code, tier, ki_usage,
                   active, config, icon, created_at, updated_at
            FROM learning_methods.learning_method_types
            WHERE type_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (type_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return LearningMethodType(
                    type_id=row[0],
                    method_type=row[1],
                    name=row[2],
                    description=row[3],
                    group_code=row[4],
                    tier=row[5],
                    ki_usage=row[6],
                    active=row[7],
                    config=row[8],
                    icon=row[9],
                    created_at=row[10],
                    updated_at=row[11]
                )

    @staticmethod
    def find_type_by_method_type(method_type: int) -> Optional[LearningMethodType]:
        """
        Find learning method type by method_type (0-11).

        Args:
            method_type: Method type ID (0-11 for 12 Content-LMs)

        Returns:
            LearningMethodType or None
        """
        query = """
            SELECT type_id, method_type, name, description, group_code, tier, ki_usage,
                   active, config, icon, created_at, updated_at
            FROM learning_methods.learning_method_types
            WHERE method_type = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (method_type,))
                row = cur.fetchone()

                if not row:
                    return None

                return LearningMethodType(
                    type_id=row[0],
                    method_type=row[1],
                    name=row[2],
                    description=row[3],
                    group_code=row[4],
                    tier=row[5],
                    ki_usage=row[6],
                    active=row[7],
                    config=row[8],
                    icon=row[9],
                    created_at=row[10],
                    updated_at=row[11]
                )

    @staticmethod
    def find_all_types(
        group_code: Optional[str] = None,
        tier: Optional[str] = None,
        active_only: bool = True
    ) -> List[LearningMethodType]:
        """
        Find all learning method types with optional filters.

        Args:
            group_code: Optional group filter (A, B, C)
            tier: Optional tier filter (basic, premium)
            active_only: Only active types

        Returns:
            List of LearningMethodType
        """
        query = """
            SELECT type_id, method_type, name, description, group_code, tier, ki_usage,
                   active, config, icon, created_at, updated_at
            FROM learning_methods.learning_method_types
            WHERE 1=1
        """
        params = []

        if group_code:
            query += " AND group_code = %s"
            params.append(group_code)

        if tier:
            query += " AND tier = %s"
            params.append(tier)

        if active_only:
            query += " AND active = TRUE"

        query += " ORDER BY method_type ASC"

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    LearningMethodType(
                        type_id=row[0],
                        method_type=row[1],
                        name=row[2],
                        description=row[3],
                        group_code=row[4],
                        tier=row[5],
                        ki_usage=row[6],
                        active=row[7],
                        config=row[8],
                        icon=row[9],
                        created_at=row[10],
                        updated_at=row[11]
                    )
                    for row in rows
                ]

    @staticmethod
    def get_available_method_types() -> List[int]:
        """
        Get available learning method types from database constraint.

        Returns valid method_type values (0-11 for 12 Content-LMs) by querying
        the database CHECK constraint. NO hardcoded lists.

        Returns:
            List of valid method type IDs (e.g., [0, 1, 2, ..., 11])
        """
        query = """
            SELECT
                UNNEST(
                    ARRAY(
                        SELECT generate_series(
                            0::int,
                            (
                                SELECT CAST(
                                    SUBSTRING(
                                        pg_get_constraintdef(c.oid)
                                        FROM 'method_type <= (\\d+)'
                                    ) AS INTEGER
                                )
                                FROM pg_constraint c
                                JOIN pg_class t ON c.conrelid = t.oid
                                JOIN pg_namespace n ON t.relnamespace = n.oid
                                WHERE n.nspname = 'learning_methods'
                                  AND t.relname = 'learning_method_types'
                                  AND c.conname = 'chk_method_type'
                            )
                        )
                    )
                ) AS method_type
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
                return [row[0] for row in rows]

    # ============================================================================
    # LEARNING METHOD INSTANCES (Concrete instances in chapters)
    # ============================================================================

    @staticmethod
    def find_by_id(method_id: str) -> Optional[LearningMethodInstance]:
        """
        Find learning method instance by ID.

        Args:
            method_id: Method instance UUID

        Returns:
            LearningMethodInstance or None
        """
        query = """
            SELECT method_id, chapter_id, method_type, title, instructions,
                   data, solution, tier, duration_minutes, difficulty,
                   order_index, published, created_at, updated_at
            FROM learning_methods.learning_method_instances
            WHERE method_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (method_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return LearningMethodInstance(
                    method_id=row[0],
                    chapter_id=row[1],
                    method_type=row[2],
                    title=row[3],
                    instructions=row[4],
                    data=row[5],
                    solution=row[6],
                    tier=row[7],
                    duration_minutes=row[8],
                    difficulty=row[9],
                    order_index=row[10],
                    published=row[11],
                    created_at=row[12],
                    updated_at=row[13]
                )

    @staticmethod
    def find_by_chapter_id(
        chapter_id: str,
        published_only: bool = False,
        order_by_index: bool = True
    ) -> List[LearningMethodInstance]:
        """
        Find learning method instances by chapter ID.

        Args:
            chapter_id: Chapter UUID
            published_only: Only published instances
            order_by_index: Order by order_index

        Returns:
            List of LearningMethodInstance
        """
        query = """
            SELECT method_id, chapter_id, method_type, title, instructions,
                   data, solution, tier, duration_minutes, difficulty,
                   order_index, published, created_at, updated_at
            FROM learning_methods.learning_method_instances
            WHERE chapter_id = %s
        """
        params = [chapter_id]

        if published_only:
            query += " AND published = TRUE"

        if order_by_index:
            query += " ORDER BY order_index ASC"
        else:
            query += " ORDER BY created_at ASC"

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    LearningMethodInstance(
                        method_id=row[0],
                        chapter_id=row[1],
                        method_type=row[2],
                        title=row[3],
                        instructions=row[4],
                        data=row[5],
                        solution=row[6],
                        tier=row[7],
                        duration_minutes=row[8],
                        difficulty=row[9],
                        order_index=row[10],
                        published=row[11],
                        created_at=row[12],
                        updated_at=row[13]
                    )
                    for row in rows
                ]

    @staticmethod
    def find_all(
        chapter_id: Optional[str] = None,
        method_type: Optional[int] = None,
        tier: Optional[str] = None,
        published: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LearningMethodInstance]:
        """
        Find learning method instances with filters.

        Args:
            chapter_id: Optional chapter filter
            method_type: Optional method type filter (0-11)
            tier: Optional tier filter (basic, premium)
            published: Optional published filter
            limit: Result limit
            offset: Result offset

        Returns:
            List of LearningMethodInstance
        """
        query = """
            SELECT method_id, chapter_id, method_type, title, instructions,
                   data, solution, tier, duration_minutes, difficulty,
                   order_index, published, created_at, updated_at
            FROM learning_methods.learning_method_instances
            WHERE 1=1
        """
        params = []

        if chapter_id:
            query += " AND chapter_id = %s"
            params.append(chapter_id)

        if method_type is not None:
            query += " AND method_type = %s"
            params.append(method_type)

        if tier:
            query += " AND tier = %s"
            params.append(tier)

        if published is not None:
            query += " AND published = %s"
            params.append(published)

        query += " ORDER BY chapter_id, order_index ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    LearningMethodInstance(
                        method_id=row[0],
                        chapter_id=row[1],
                        method_type=row[2],
                        title=row[3],
                        instructions=row[4],
                        data=row[5],
                        solution=row[6],
                        tier=row[7],
                        duration_minutes=row[8],
                        difficulty=row[9],
                        order_index=row[10],
                        published=row[11],
                        created_at=row[12],
                        updated_at=row[13]
                    )
                    for row in rows
                ]

    @staticmethod
    def create(instance: LearningMethodInstance) -> LearningMethodInstance:
        """
        Create new learning method instance.

        Args:
            instance: LearningMethodInstance to create

        Returns:
            Created LearningMethodInstance with timestamps
        """
        query = """
            INSERT INTO learning_methods.learning_method_instances
            (method_id, chapter_id, method_type, title, instructions, data, solution,
             tier, duration_minutes, difficulty, order_index, published, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING method_id, chapter_id, method_type, title, instructions,
                      data, solution, tier, duration_minutes, difficulty,
                      order_index, published, created_at, updated_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    instance.method_id,
                    instance.chapter_id,
                    instance.method_type,
                    instance.title,
                    instance.instructions,
                    json.dumps(instance.data) if instance.data else None,
                    json.dumps(instance.solution) if instance.solution else None,
                    instance.tier,
                    instance.duration_minutes,
                    instance.difficulty,
                    instance.order_index,
                    instance.published,
                    instance.created_at or datetime.utcnow(),
                    instance.updated_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return LearningMethodInstance(
                    method_id=row[0],
                    chapter_id=row[1],
                    method_type=row[2],
                    title=row[3],
                    instructions=row[4],
                    data=row[5],
                    solution=row[6],
                    tier=row[7],
                    duration_minutes=row[8],
                    difficulty=row[9],
                    order_index=row[10],
                    published=row[11],
                    created_at=row[12],
                    updated_at=row[13]
                )

    @staticmethod
    def update(instance: LearningMethodInstance) -> LearningMethodInstance:
        """
        Update learning method instance.

        Args:
            instance: LearningMethodInstance with updates

        Returns:
            Updated LearningMethodInstance
        """
        query = """
            UPDATE learning_methods.learning_method_instances
            SET title = %s,
                instructions = %s,
                data = %s,
                solution = %s,
                tier = %s,
                duration_minutes = %s,
                difficulty = %s,
                order_index = %s,
                published = %s,
                updated_at = %s
            WHERE method_id = %s
            RETURNING method_id, chapter_id, method_type, title, instructions,
                      data, solution, tier, duration_minutes, difficulty,
                      order_index, published, created_at, updated_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    instance.title,
                    instance.instructions,
                    json.dumps(instance.data) if instance.data else None,
                    json.dumps(instance.solution) if instance.solution else None,
                    instance.tier,
                    instance.duration_minutes,
                    instance.difficulty,
                    instance.order_index,
                    instance.published,
                    datetime.utcnow(),
                    instance.method_id
                ))

                row = cur.fetchone()
                conn.commit()

                return LearningMethodInstance(
                    method_id=row[0],
                    chapter_id=row[1],
                    method_type=row[2],
                    title=row[3],
                    instructions=row[4],
                    data=row[5],
                    solution=row[6],
                    tier=row[7],
                    duration_minutes=row[8],
                    difficulty=row[9],
                    order_index=row[10],
                    published=row[11],
                    created_at=row[12],
                    updated_at=row[13]
                )

    @staticmethod
    def delete(method_id: str) -> bool:
        """
        Delete learning method instance.

        Args:
            method_id: Method instance UUID

        Returns:
            True if deleted, False if not found
        """
        query = """
            DELETE FROM learning_methods.learning_method_instances
            WHERE method_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (method_id,))
                deleted = cur.rowcount > 0
                conn.commit()
                return deleted

    @staticmethod
    def count(
        chapter_id: Optional[str] = None,
        method_type: Optional[int] = None,
        tier: Optional[str] = None,
        published: Optional[bool] = None
    ) -> int:
        """
        Count learning method instances with filters.

        Args:
            chapter_id: Optional chapter filter
            method_type: Optional method type filter
            tier: Optional tier filter
            published: Optional published filter

        Returns:
            Instance count
        """
        query = "SELECT COUNT(*) FROM learning_methods.learning_method_instances WHERE 1=1"
        params = []

        if chapter_id:
            query += " AND chapter_id = %s"
            params.append(chapter_id)

        if method_type is not None:
            query += " AND method_type = %s"
            params.append(method_type)

        if tier:
            query += " AND tier = %s"
            params.append(tier)

        if published is not None:
            query += " AND published = %s"
            params.append(published)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.fetchone()[0]
