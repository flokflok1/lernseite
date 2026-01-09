"""Category Entity"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Category:
    """Course category entity (hierarchical)."""
    category_id: int
    name: str
    slug: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    level: int = 1
    order_index: int = 0
    active: bool = True
    path: Optional[str] = None
    root_id: Optional[int] = None
    path_ids: Optional[List[int]] = None
    name_en: Optional[str] = None
    name_es: Optional[str] = None
    name_fr: Optional[str] = None
    course_count: int = 0
    total_course_count: int = 0
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.level < 1 or self.level > 20:
            raise ValueError(f"Level must be between 1 and 20, got {self.level}")
    
    def is_root(self) -> bool:
        return self.parent_id is None
    
    def is_active(self) -> bool:
        return self.active
