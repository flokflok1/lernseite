"""
LernsystemX Category Repository - Base CRUD Operations

Data access layer for core category CRUD operations:
- Create categories with validation
- Find by ID/slug
- Update categories
- Activate/deactivate (soft delete)
- Delete categories with cascade option

ISO 27001:2013 compliant - Secure category data management
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query
from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.cache.service import CacheService
from flask import current_app


class BaseCategoryRepository(BaseRepository):
    """
    Base repository for Category CRUD operations

    Handles:
    - Category creation with hierarchy validation
    - Single category retrieval (by ID or slug)
    - Category updates (restricted fields)
    - Soft delete operations (activate/deactivate)
    - Hard delete with cascade option
    """

    table_name = 'courses.course_categories'
    MAX_DEPTH = 20  # Practical limit to prevent infinite recursion

    @staticmethod
    def _normalize_response(category: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Normalize category response - map DB field names to API field names

        Maps:
        - active -> is_active (frontend expects is_active)
        """
        if category is None:
            return None

        result = dict(category)
        # Map 'active' to 'is_active' for frontend consistency
        if 'active' in result:
            result['is_active'] = result.pop('active')
        return result

    @staticmethod
    def _normalize_list_response(categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize a list of category responses"""
        return [BaseCategoryRepository._normalize_response(cat) for cat in categories if cat]

    @classmethod
    def create(cls, category_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new category

        Args:
            category_data: Category data including:
                - name: str (required)
                - slug: str (auto-generated if not provided)
                - description: str
                - parent_id: int (None for root categories)
                - level: int (1-5)
                - icon: str
                - color: str
                - order_index: int (auto-assigned if not provided)
                - is_active: bool (default: True)

        Returns:
            Created category with category_id

        Raises:
            ValueError: If level > 5 or hierarchy constraints violated
        """
        # Auto-assign order_index if not provided
        if 'order_index' not in category_data:
            max_order_query = """
                SELECT COALESCE(MAX(order_index), -1) + 1 AS next_order
                FROM courses.course_categories
                WHERE parent_id IS NOT DISTINCT FROM %(parent_id)s
            """
            parent_id = category_data.get('parent_id')
            result = fetch_one(max_order_query, {'parent_id': parent_id})
            category_data['order_index'] = result['next_order'] if result else 0

        # Validate level constraints
        level = category_data.get('level', 1)
        parent_id = category_data.get('parent_id')

        if level > cls.MAX_DEPTH:
            raise ValueError(f'Category level cannot exceed {cls.MAX_DEPTH}')

        if level == 1 and parent_id is not None:
            raise ValueError('Level 1 categories cannot have a parent')

        if level > 1 and parent_id is None:
            raise ValueError(f'Level {level} categories must have a parent_id')

        # If parent_id is provided, verify it exists and level is correct
        if parent_id is not None:
            parent = cls.find_by_id(parent_id)
            if not parent:
                raise ValueError(f'Parent category {parent_id} not found')

            expected_level = parent['level'] + 1
            if level != expected_level:
                raise ValueError(f'Level must be {expected_level} (parent level + 1)')

        query = """
            INSERT INTO courses.course_categories (
                name, slug, description, parent_id, level,
                icon, color, order_index, active,
                created_at, updated_at
            ) VALUES (
                %(name)s, %(slug)s, %(description)s, %(parent_id)s, %(level)s,
                %(icon)s, %(color)s, %(order_index)s, %(active)s,
                NOW(), NOW()
            )
            RETURNING
                category_id, name, slug, description, parent_id, level,
                icon, color, order_index, active, path, root_id,
                created_at, updated_at
        """

        defaults = {
            'description': None,
            'parent_id': None,
            'icon': None,
            'color': None,
            'active': True
        }

        params = {**defaults, **category_data}

        result = fetch_one(query, params)

        # Invalidate category cache after creation
        if result:
            CacheService.invalidate_category_cache()

        return cls._normalize_response(result)

    @classmethod
    def find_by_id(cls, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Find category by ID with parent info and course count

        Args:
            category_id: Category ID

        Returns:
            Category dict or None
        """
        query = """
            SELECT
                c.*,
                p.name AS parent_name,
                (SELECT COUNT(*) FROM courses.courses WHERE category_id = c.category_id) AS course_count
            FROM courses.course_categories c
            LEFT JOIN courses.course_categories p ON c.parent_id = p.category_id
            WHERE c.category_id = %(category_id)s
        """

        return cls._normalize_response(fetch_one(query, {'category_id': category_id}))

    @classmethod
    def find_by_slug(cls, slug: str) -> Optional[Dict[str, Any]]:
        """
        Find category by slug

        Args:
            slug: Category slug

        Returns:
            Category dict or None
        """
        query = """
            SELECT
                c.*,
                (SELECT COUNT(*) FROM courses.courses WHERE category_id = c.category_id) AS course_count
            FROM courses.course_categories c
            WHERE c.slug = %(slug)s
        """

        return cls._normalize_response(fetch_one(query, {'slug': slug}))

    @classmethod
    def update(cls, category_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update category

        Note: Cannot update level or parent_id to prevent breaking hierarchy

        Args:
            category_id: Category ID
            update_data: Fields to update

        Returns:
            Updated category or None
        """
        # Map is_active to active (frontend uses is_active, DB uses active)
        if 'is_active' in update_data:
            update_data['active'] = update_data.pop('is_active')

        # Don't allow updating these fields directly
        restricted_fields = ['category_id', 'level', 'parent_id', 'created_at']
        update_data = {k: v for k, v in update_data.items() if k not in restricted_fields}

        if not update_data:
            return cls.find_by_id(category_id)

        # Always update updated_at
        update_data['updated_at'] = datetime.utcnow()

        # Build SET clause
        set_parts = [f"{key} = %({key})s" for key in update_data.keys()]
        set_clause = ", ".join(set_parts)

        query = f"""
            UPDATE courses.course_categories
            SET {set_clause}
            WHERE category_id = %(category_id)s
            RETURNING *
        """

        params = {**update_data, 'category_id': category_id}

        result = fetch_one(query, params)

        # Invalidate category cache after update
        if result:
            CacheService.invalidate_category_cache()

        return cls._normalize_response(result)

    @classmethod
    def deactivate(cls, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Soft delete - deactivate category

        Args:
            category_id: Category ID

        Returns:
            Updated category or None
        """
        return cls.update(category_id, {'active': False})

    @classmethod
    def activate(cls, category_id: int) -> Optional[Dict[str, Any]]:
        """
        Activate category

        Args:
            category_id: Category ID

        Returns:
            Updated category or None
        """
        return cls.update(category_id, {'active': True})

    @classmethod
    def delete(cls, category_id: int, cascade: bool = True) -> dict:
        """
        Delete a category

        Args:
            category_id: Category ID
            cascade: If True, delete all subcategories recursively (default: True)

        Returns:
            Dict with deletion stats: {'deleted_categories': int, 'affected_courses': int}

        Raises:
            ValueError: If category has courses (courses must be moved first)
        """
        # Get all descendants if cascade mode
        if cascade:
            # Get all category IDs to delete (self + all descendants)
            descendants_query = """
                WITH RECURSIVE cat_tree AS (
                    SELECT category_id FROM courses.course_categories WHERE category_id = %(category_id)s
                    UNION ALL
                    SELECT c.category_id FROM courses.course_categories c
                    JOIN cat_tree ct ON c.parent_id = ct.category_id
                )
                SELECT category_id FROM cat_tree
            """
            descendants = fetch_all(descendants_query, {'category_id': category_id})
            category_ids = [d['category_id'] for d in descendants] if descendants else [category_id]
        else:
            category_ids = [category_id]

        # Check if ANY of these categories have courses
        courses_query = """
            SELECT COUNT(*) as count FROM courses.courses
            WHERE category_id = ANY(%(category_ids)s)
        """
        courses_result = fetch_one(courses_query, {'category_ids': category_ids})

        if courses_result and courses_result['count'] > 0:
            raise ValueError(f'Kann nicht löschen: {courses_result["count"]} Kurs(e) sind diesen Kategorien zugeordnet. Bitte erst die Kurse verschieben oder löschen.')

        # Delete all categories (children first due to foreign key)
        delete_query = """
            DELETE FROM courses.course_categories
            WHERE category_id = ANY(%(category_ids)s)
        """
        execute_query(delete_query, {'category_ids': category_ids})

        # Invalidate category cache after deletion
        CacheService.invalidate_category_cache()

        return {
            'deleted_categories': len(category_ids),
            'affected_courses': 0
        }
