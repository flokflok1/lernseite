"""
LernsystemX Category Repositories

Modular repository package for category-related database operations.

Combines:
- BaseCategoryRepository: Core CRUD operations
- HierarchyCategoryRepository: Tree, path, and movement operations
- UtilsCategoryRepository: Search, statistics, and bulk operations

All functionality available through unified CategoryRepository interface.
"""

from .base_category_repository import BaseCategoryRepository
from .hierarchy_category_repository import HierarchyCategoryRepository
from .utils_category_repository import UtilsCategoryRepository


class CategoryRepository(UtilsCategoryRepository, HierarchyCategoryRepository, BaseCategoryRepository):
    """
    Unified Category Repository

    Combines all category operations:
    - CRUD operations (create, find, update, delete, activate, deactivate)
    - Hierarchy operations (tree, paths, movement, reordering, breadcrumbs)
    - Utilities (search, statistics, bulk operations)

    All methods available on single CategoryRepository interface.

    Example:
        >>> # Create category
        >>> category = CategoryRepository.create({
        ...     'name': 'Python Programming',
        ...     'level': 2,
        ...     'parent_id': 1
        ... })
        >>>
        >>> # Get tree structure
        >>> tree = CategoryRepository.get_tree()
        >>>
        >>> # Search categories
        >>> results = CategoryRepository.search('Python')
        >>>
        >>> # Move category
        >>> moved = CategoryRepository.move_category(5, new_parent_id=2)
    """
    pass


__all__ = [
    'CategoryRepository',
    'BaseCategoryRepository',
    'HierarchyCategoryRepository',
    'UtilsCategoryRepository'
]
