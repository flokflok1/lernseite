"""
LernsystemX Category Repository - Hierarchy & Tree Operations

Data access layer for hierarchical category operations:
- Tree building with unlimited depth
- Path-based operations
- Category movement/restructuring
- Breadcrumb generation
- Descendant/ancestor queries
- Reordering

ISO 27001:2013 compliant - Secure category data management
"""

from typing import Optional, Dict, List, Any

from app.database.connection import fetch_one, fetch_all, execute_query
from app.repositories.base_repository import BaseRepository
from app.services.cache_service import CacheService
from flask import current_app

from .base_category_repository import BaseCategoryRepository


class HierarchyCategoryRepository(BaseCategoryRepository):
    """
    Repository for Category hierarchy operations

    Handles:
    - Tree building with unlimited depth
    - Category path operations
    - Movement/restructuring
    - Breadcrumb generation
    - Reordering
    """

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
                (SELECT COUNT(*) FROM courses.courses WHERE category_id = c.category_id) AS course_count
            FROM courses.course_categories c
            LEFT JOIN courses.course_categories p ON c.parent_id = p.category_id
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
            >>> tree = HierarchyCategoryRepository.get_tree()
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
                    (SELECT COUNT(*) FROM courses.courses WHERE category_id = c.category_id) AS course_count
                FROM courses.course_categories c
                WHERE c.parent_id IS NULL
            """
            params = {}
        else:
            query = """
                SELECT
                    c.*,
                    (SELECT COUNT(*) FROM courses.courses WHERE category_id = c.category_id) AS course_count
                FROM courses.course_categories c
                WHERE c.parent_id = %(parent_id)s
            """
            params = {'parent_id': parent_id}

        if active_only:
            query += " AND c.active = TRUE"

        query += " ORDER BY c.order_index ASC"

        return cls._normalize_list_response(fetch_all(query, params if params else None))

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
                   (SELECT COUNT(*) FROM courses.courses WHERE category_id = c.category_id) AS course_count,
                   (SELECT COUNT(*) FROM courses.course_categories WHERE parent_id = c.category_id) AS child_count
            FROM courses.course_categories c
            WHERE c.parent_id IS NULL
        """

        if active_only:
            query += " AND c.active = TRUE"

        query += " ORDER BY c.order_index, c.name"

        return cls._normalize_list_response(fetch_all(query))

    @classmethod
    def get_breadcrumb(cls, category_id: int) -> List[Dict[str, Any]]:
        """
        Get category breadcrumb path from root to category

        Args:
            category_id: Category ID

        Returns:
            List of categories from root to current category

        Example:
            >>> breadcrumb = HierarchyCategoryRepository.get_breadcrumb(15)
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
                FROM courses.course_categories
                WHERE category_id = %(category_id)s

                UNION ALL

                SELECT c.category_id, c.parent_id, c.name, c.slug, c.level, c.path, c.active
                FROM courses.course_categories c
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
            UPDATE courses.course_categories
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
    def reorder(cls, category_orders: List[Dict[str, int]]) -> bool:
        """
        Reorder categories

        Args:
            category_orders: List of dicts with 'category_id' and 'order_index'

        Returns:
            True if successful

        Example:
            >>> HierarchyCategoryRepository.reorder([
            ...     {'category_id': 5, 'order_index': 0},
            ...     {'category_id': 3, 'order_index': 1},
            ...     {'category_id': 8, 'order_index': 2}
            ... ])
        """
        # Update each category's order_index
        for item in category_orders:
            query = """
                UPDATE courses.course_categories
                SET order_index = %(order_index)s, updated_at = NOW()
                WHERE category_id = %(category_id)s
            """
            execute_query(query, {'order_index': item['order_index'], 'category_id': item['category_id']})

        # Invalidate category cache after reordering
        CacheService.invalidate_category_cache()

        return True

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
                   (SELECT COUNT(*) FROM courses.courses WHERE category_id = c.category_id) AS course_count
            FROM courses.course_categories c
            WHERE c.path = %(path)s
        """
        return cls._normalize_response(fetch_one(query, {'path': path}))

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
            SELECT path_ids FROM courses.course_categories WHERE category_id = %(category_id)s
        """
        result = fetch_one(query, {'category_id': category_id})
        return result['path_ids'] if result and result['path_ids'] else []
