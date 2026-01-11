"""Category Service"""
from typing import Optional, List
from src.api.categories.core.domain.entities.category import Category
from src.api.categories.core.infrastructure.repositories.category_repository import CategoryRepository

class CategoryService:
    @staticmethod
    def get_category(category_id: int) -> Optional[Category]:
        return CategoryRepository.find_by_id(category_id)
    
    @staticmethod
    def get_root_categories() -> List[Category]:
        return CategoryRepository.list_root_categories()
    
    @staticmethod
    def get_children(parent_id: int) -> List[Category]:
        return CategoryRepository.list_children(parent_id)
