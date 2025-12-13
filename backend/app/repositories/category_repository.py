"""
LernsystemX Category Repository

Data access layer for flexible hierarchical course categories:
- CRUD operations for categories
- Hierarchical tree building (unlimited depth)
- Category search and filtering
- Ordering and reordering
- Course count calculation
- Path-based operations
- Category moving/restructuring

ISO 27001:2013 compliant - Secure category data management
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

from app.database.connection import fetch_one, fetch_all, execute_query, insert_returning
from app.repositories.base_repository import BaseRepository
from app.services.cache_service import CacheService
from flask import current_app


class CategoryRepository(BaseRepository):
    """
    Repository for Category entity

    Handles all database operations for categories including:
    - Category CRUD with hierarchy validation
    - Tree building with unlimited depth (practical limit: 20 levels)
    - Category ordering and reordering
    - Search and filtering
    - Path-based navigation
    - Category restructuring (move)
    """

    table_name = 'course_categories'
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
        return [CategoryRepository._normalize_response(cat) for cat in categories if cat]

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

        Example:
            >>> category = CategoryRepository.create({
            ...     'name': 'Python Programming',
            ...     'slug': 'python-programming',
            ...     'parent_id': 2,
            ...     'level': 3
            ... })
        """
        # Auto-assign order_index if not provided
        if 'order_index' not in category_data:
            max_order_query = """
                SELECT COALESCE(MAX(order_index), -1) + 1 AS next_order
                FROM course_categories
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
            INSERT INTO course_categories (
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
                (SELECT COUNT(*) FROM courses WHERE category_id = c.category_id) AS course_count
            FROM course_categories c
            LEFT JOIN course_categories p ON c.parent_id = p.category_id
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
                (SELECT COUNT(*) FROM courses WHERE category_id = c.category_id) AS course_count
            FROM course_categories c
            WHERE c.slug = %(slug)s
        """

        return cls._normalize_response(fetch_one(query, {'slug': slug}))

    @classmethod
    def get_all(cls, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get all categories (flat list)

        Args:
            active_only: Only return active categories

        Returns:
            List of all categories ordered by level and order_index
        """
        query = """
            SELECT
                c.*,
                p.name AS parent_name,
                (SELECT COUNT(*) FROM courses WHERE category_id = c.category_id) AS course_count
            FROM course_categories c
            LEFT JOIN course_categories p ON c.parent_id = p.category_id
        """

        if active_only:
            query += " WHERE c.active = TRUE"

        query += " ORDER BY c.level ASC, c.order_index ASC"

        return cls._normalize_list_response(fetch_all(query))

    @classmethod
    def get_tree(cls, active_only: bool = False, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Get category tree with hierarchical structure (up to 5 levels)

        Builds a tree structure from flat category list.

        Args:
            active_only: Only include active categories
            use_cache: Use cache (default: True)

        Returns:
            List of root categories with nested children (up to 5 levels deep)

        Example:
            >>> tree = CategoryRepository.get_tree()
            >>> # Returns:
            >>> # [
            >>> #   {
            >>> #     'category_id': 1,
            >>> #     'name': 'IT & Software',
            >>> #     'level': 1,
            >>> #     'children': [
            >>> #       {
            >>> #         'category_id': 2,
            >>> #         'name': 'Programming',
            >>> #         'level': 2,
            >>> #         'parent_id': 1,
            >>> #         'children': [...]
            >>> #       }
            >>> #     ]
            >>> #   }
            >>> # ]
        """
        # Try cache first
        if use_cache:
            cache_suffix = 'active' if active_only else 'all'
            cache_key = CacheService.make_key('CATEGORY', 'tree', cache_suffix)
            ttl = current_app.config.get('CACHE_CATEGORY_TTL', 3600)

            def load_tree():
                # Get all categories
                all_categories = cls.get_all(active_only)

                # Build lookup dictionary
                categories_dict = {cat['category_id']: {**cat, 'children': []} for cat in all_categories}

                # Build tree
                root_categories = []

                for category in all_categories:
                    cat_id = category['category_id']
                    parent_id = category['parent_id']

                    if parent_id is None:
                        # Root category (level 1)
                        root_categories.append(categories_dict[cat_id])
                    else:
                        # Child category - add to parent's children
                        if parent_id in categories_dict:
                            categories_dict[parent_id]['children'].append(categories_dict[cat_id])

                return root_categories

            return CacheService.cache_get_or_set(cache_key, ttl, load_tree)

        # Bypass cache
        # Get all categories
        all_categories = cls.get_all(active_only)

        # Build lookup dictionary
        categories_dict = {cat['category_id']: {**cat, 'children': []} for cat in all_categories}

        # Build tree
        root_categories = []

        for category in all_categories:
            cat_id = category['category_id']
            parent_id = category['parent_id']

            if parent_id is None:
                # Root category (level 1)
                root_categories.append(categories_dict[cat_id])
            else:
                # Child category - add to parent's children
                if parent_id in categories_dict:
                    categories_dict[parent_id]['children'].append(categories_dict[cat_id])

        return root_categories

    @classmethod
    def get_subcategories(cls, parent_id: Optional[int] = None, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Get direct subcategories of a parent

        Args:
            parent_id: Parent category ID (None for root categories)
            active_only: Only return active categories

        Returns:
            List of direct child categories
        """
        if parent_id is None:
            # Get root categories (level 1)
            query = """
                SELECT
                    c.*,
                    (SELECT COUNT(*) FROM courses WHERE category_id = c.category_id) AS course_count
                FROM course_categories c
                WHERE c.parent_id IS NULL
            """
            params = {}
        else:
            query = """
                SELECT
                    c.*,
                    (SELECT COUNT(*) FROM courses WHERE category_id = c.category_id) AS course_count
                FROM course_categories c
                WHERE c.parent_id = %(parent_id)s
            """
            params = {'parent_id': parent_id}

        if active_only:
            query += " AND c.active = TRUE"

        query += " ORDER BY c.order_index ASC"

        return cls._normalize_list_response(fetch_all(query, params if params else None))

    @classmethod
    def search(cls, search_term: str, active_only: bool = False) -> List[Dict[str, Any]]:
        """
        Search categories by name or description

        Args:
            search_term: Search query
            active_only: Only search active categories

        Returns:
            List of matching categories
        """
        query = """
            SELECT
                c.*,
                p.name AS parent_name,
                (SELECT COUNT(*) FROM courses WHERE category_id = c.category_id) AS course_count
            FROM course_categories c
            LEFT JOIN categories p ON c.parent_id = p.category_id
            WHERE (c.name ILIKE %(search_pattern)s OR c.description ILIKE %(search_pattern)s)
        """

        if active_only:
            query += " AND c.active = TRUE"

        query += " ORDER BY c.level ASC, c.order_index ASC"

        search_pattern = f'%{search_term}%'
        return cls._normalize_list_response(fetch_all(query, {'search_pattern': search_pattern}))

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
            UPDATE course_categories
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
                    SELECT category_id FROM course_categories WHERE category_id = %(category_id)s
                    UNION ALL
                    SELECT c.category_id FROM course_categories c
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
            SELECT COUNT(*) as count FROM courses
            WHERE category_id = ANY(%(category_ids)s)
        """
        courses_result = fetch_one(courses_query, {'category_ids': category_ids})

        if courses_result and courses_result['count'] > 0:
            raise ValueError(f'Kann nicht löschen: {courses_result["count"]} Kurs(e) sind diesen Kategorien zugeordnet. Bitte erst die Kurse verschieben oder löschen.')

        # Delete all categories (children first due to foreign key)
        # Delete in reverse order of level (deepest first)
        delete_query = """
            DELETE FROM course_categories
            WHERE category_id = ANY(%(category_ids)s)
        """
        execute_query(delete_query, {'category_ids': category_ids})

        # Invalidate category cache after deletion
        CacheService.invalidate_category_cache()

        return {
            'deleted_categories': len(category_ids),
            'affected_courses': 0
        }

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
    def reorder(cls, category_orders: List[Dict[str, int]]) -> bool:
        """
        Reorder categories

        Args:
            category_orders: List of dicts with 'category_id' and 'order_index'

        Returns:
            True if successful

        Example:
            >>> CategoryRepository.reorder([
            ...     {'category_id': 5, 'order_index': 0},
            ...     {'category_id': 3, 'order_index': 1},
            ...     {'category_id': 8, 'order_index': 2}
            ... ])
        """
        # Update each category's order_index
        for item in category_orders:
            query = """
                UPDATE course_categories
                SET order_index = %(order_index)s, updated_at = NOW()
                WHERE category_id = %(category_id)s
            """
            execute_query(query, {'order_index': item['order_index'], 'category_id': item['category_id']})

        # Invalidate category cache after reordering
        CacheService.invalidate_category_cache()

        return True

    @classmethod
    def get_breadcrumb(cls, category_id: int) -> List[Dict[str, Any]]:
        """
        Get category breadcrumb path from root to category

        Args:
            category_id: Category ID

        Returns:
            List of categories from root to current category

        Example:
            >>> breadcrumb = CategoryRepository.get_breadcrumb(15)
            >>> # Returns: [
            >>> #   {'category_id': 1, 'name': 'IT & Software', 'level': 1},
            >>> #   {'category_id': 2, 'name': 'Programming', 'level': 2},
            >>> #   {'category_id': 5, 'name': 'Python', 'level': 3},
            >>> #   {'category_id': 15, 'name': 'Flask', 'level': 4}
            >>> # ]
        """
        breadcrumb = []
        current_id = category_id

        # Traverse up to root (max 5 levels)
        for _ in range(5):
            category = cls.find_by_id(current_id)
            if not category:
                break

            breadcrumb.insert(0, category)

            if category['parent_id'] is None:
                break

            current_id = category['parent_id']

        return breadcrumb

    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """
        Get category statistics

        Returns:
            Statistics dict with counts by level
        """
        query = """
            SELECT
                COUNT(*) as total_categories,
                COUNT(CASE WHEN active = TRUE THEN 1 END) as active_categories,
                COUNT(CASE WHEN level = 1 THEN 1 END) as level_1_count,
                COUNT(CASE WHEN level = 2 THEN 1 END) as level_2_count,
                COUNT(CASE WHEN level = 3 THEN 1 END) as level_3_count,
                COUNT(CASE WHEN level = 4 THEN 1 END) as level_4_count,
                COUNT(CASE WHEN level = 5 THEN 1 END) as level_5_count,
                MAX(level) as max_level
            FROM course_categories
        """

        result = fetch_one(query)

        if not result:
            return {}

        return {
            'total_categories': result['total_categories'] or 0,
            'active_categories': result['active_categories'] or 0,
            'level_1_count': result['level_1_count'] or 0,
            'level_2_count': result['level_2_count'] or 0,
            'level_3_count': result['level_3_count'] or 0,
            'level_4_count': result['level_4_count'] or 0,
            'level_5_count': result['level_5_count'] or 0,
            'max_level': result['max_level'] or 0
        }

    # =========================================================================
    # NEW METHODS FOR FLEXIBLE CATEGORY SYSTEM
    # =========================================================================

    @classmethod
    def get_by_path(cls, path: str) -> Optional[Dict[str, Any]]:
        """
        Find category by its full path

        Args:
            path: Full path like "IT/Netzwerk/Cisco/CCNA"

        Returns:
            Category dict or None
        """
        query = """
            SELECT c.*,
                   (SELECT COUNT(*) FROM courses WHERE category_id = c.category_id) AS course_count
            FROM course_categories c
            WHERE c.path = %(path)s
        """
        return cls._normalize_response(fetch_one(query, {'path': path}))

    @classmethod
    def get_descendants(cls, category_id: int, include_self: bool = False) -> List[Dict[str, Any]]:
        """
        Get all descendants of a category (recursive)

        Args:
            category_id: Parent category ID
            include_self: Include the category itself

        Returns:
            List of all descendant categories
        """
        query = """
            WITH RECURSIVE descendants AS (
                SELECT category_id, parent_id, name, slug, level, path, active
                FROM course_categories
                WHERE category_id = %(category_id)s

                UNION ALL

                SELECT c.category_id, c.parent_id, c.name, c.slug, c.level, c.path, c.active
                FROM course_categories c
                JOIN descendants d ON c.parent_id = d.category_id
            )
            SELECT * FROM descendants
        """

        if not include_self:
            query += " WHERE category_id != %(category_id)s"

        query += " ORDER BY level, name"

        return cls._normalize_list_response(fetch_all(query, {'category_id': category_id}))

    @classmethod
    def move_category(cls, category_id: int, new_parent_id: Optional[int]) -> Optional[Dict[str, Any]]:
        """
        Move a category to a new parent

        This will update the category's parent_id, level, path, and root_id.
        The database trigger will automatically update path information.

        Args:
            category_id: Category to move
            new_parent_id: New parent ID (None for root)

        Returns:
            Updated category or None

        Raises:
            ValueError: If move would create circular reference or exceed max depth
        """
        # Check if category exists
        category = cls.find_by_id(category_id)
        if not category:
            raise ValueError(f'Category {category_id} not found')

        # Cannot move to itself
        if new_parent_id == category_id:
            raise ValueError('Cannot move category to itself')

        # Check if new_parent_id is a descendant (would create circular reference)
        if new_parent_id:
            descendants = cls.get_descendants(category_id)
            descendant_ids = [d['category_id'] for d in descendants]
            if new_parent_id in descendant_ids:
                raise ValueError('Cannot move category to its own descendant')

            # Check new parent exists and calculate new level
            new_parent = cls.find_by_id(new_parent_id)
            if not new_parent:
                raise ValueError(f'New parent {new_parent_id} not found')

            new_level = new_parent['level'] + 1

            # Check max depth including descendants
            max_descendant_depth = max([d['level'] for d in descendants], default=category['level'])
            depth_increase = max_descendant_depth - category['level']

            if new_level + depth_increase > cls.MAX_DEPTH:
                raise ValueError(f'Move would exceed maximum depth of {cls.MAX_DEPTH}')
        else:
            new_level = 1

        # Perform the move - trigger will update path, root_id, etc.
        query = """
            UPDATE course_categories
            SET parent_id = %(new_parent_id)s,
                level = %(new_level)s,
                updated_at = NOW()
            WHERE category_id = %(category_id)s
            RETURNING *
        """

        result = fetch_one(query, {
            'category_id': category_id,
            'new_parent_id': new_parent_id,
            'new_level': new_level
        })

        # Invalidate cache
        if result:
            CacheService.invalidate_category_cache()

        return cls._normalize_response(result)

    @classmethod
    def get_root_categories(cls, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get all root categories (level 1)

        Args:
            active_only: Only return active categories

        Returns:
            List of root categories
        """
        query = """
            SELECT c.*,
                   (SELECT COUNT(*) FROM courses WHERE category_id = c.category_id) AS course_count,
                   (SELECT COUNT(*) FROM course_categories WHERE parent_id = c.category_id) AS child_count
            FROM course_categories c
            WHERE c.parent_id IS NULL
        """

        if active_only:
            query += " AND c.active = TRUE"

        query += " ORDER BY c.order_index, c.name"

        return cls._normalize_list_response(fetch_all(query))

    @classmethod
    def get_category_path_ids(cls, category_id: int) -> List[int]:
        """
        Get list of category IDs from root to this category

        Args:
            category_id: Category ID

        Returns:
            List of category IDs [root_id, ..., category_id]
        """
        query = """
            SELECT path_ids FROM course_categories WHERE category_id = %(category_id)s
        """
        result = fetch_one(query, {'category_id': category_id})
        return result['path_ids'] if result and result['path_ids'] else []

    @classmethod
    def bulk_create(cls, categories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create multiple categories at once

        Args:
            categories: List of category data dicts

        Returns:
            List of created categories
        """
        created = []
        for cat_data in categories:
            try:
                result = cls.create(cat_data)
                if result:
                    created.append(result)
            except ValueError as e:
                current_app.logger.warning(f"Failed to create category: {e}")

        return created

    @classmethod
    def search_by_path(cls, path_pattern: str) -> List[Dict[str, Any]]:
        """
        Search categories by path pattern

        Args:
            path_pattern: Path pattern (e.g., "IT/%" for all under IT)

        Returns:
            List of matching categories
        """
        query = """
            SELECT c.*,
                   (SELECT COUNT(*) FROM courses WHERE category_id = c.category_id) AS course_count
            FROM course_categories c
            WHERE c.path LIKE %(path_pattern)s AND c.active = TRUE
            ORDER BY c.path
        """
        return cls._normalize_list_response(fetch_all(query, {'path_pattern': path_pattern}))
