"""
LernsystemX Category Repository - Utility Operations

Data access layer for utility category operations:
- Search and filtering
- Statistics
- Bulk operations

ISO 27001:2013 compliant - Secure category data management
"""

from typing import Optional, Dict, List, Any

from app.database.connection import fetch_one, fetch_all
from flask import current_app

from .base_category_repository import BaseCategoryRepository


class UtilsCategoryRepository(BaseCategoryRepository):
    """
    Repository for Category utility operations

    Handles:
    - Search and filtering
    - Statistics and analytics
    - Bulk operations
    - Path-based searches
    """

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
                (SELECT COUNT(*) FROM courses.courses WHERE category_id = c.category_id) AS course_count
            FROM courses.course_categories c
            LEFT JOIN courses.course_categories p ON c.parent_id = p.category_id
            WHERE (c.name ILIKE %(search_pattern)s OR c.description ILIKE %(search_pattern)s)
        """

        if active_only:
            query += " AND c.active = TRUE"

        query += " ORDER BY c.level ASC, c.order_index ASC"

        search_pattern = f'%{search_term}%'
        return cls._normalize_list_response(fetch_all(query, {'search_pattern': search_pattern}))

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
                   (SELECT COUNT(*) FROM courses.courses WHERE category_id = c.category_id) AS course_count
            FROM courses.course_categories c
            WHERE c.path LIKE %(path_pattern)s AND c.active = TRUE
            ORDER BY c.path
        """
        return cls._normalize_list_response(fetch_all(query, {'path_pattern': path_pattern}))

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
            FROM courses.course_categories
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
