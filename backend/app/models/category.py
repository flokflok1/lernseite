"""
LernsystemX Category Models

Pydantic models for flexible hierarchical course categorization (unlimited depth):
- CategoryBase, CategoryCreate, CategoryUpdate - Category CRUD
- CategoryResponse - Single category with metadata
- CategoryTreeResponse - Hierarchical tree structure
- CategoryListResponse - Paginated category list
- CategoryMoveRequest - Move category to new parent

Supports unlimited depth hierarchy (practical limit: 20 levels):
Level 1: Main Category (e.g., "IT & Software")
Level 2: Subcategory (e.g., "Netzwerk")
Level 3+: Nested sub-categories (e.g., "Cisco/CCNA/Routing/OSPF/...")

Features:
- Automatic path calculation (e.g., "IT/Netzwerk/Cisco/CCNA")
- Path-based lookups for fast tree traversal
- Course count caching for performance
- Multi-language support (name_en, name_es, name_fr)

ISO 9001:2015 compliant - Course categorization standards
ISO/IEC/IEEE 26515:2018 compliant - API data validation
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, computed_field
import re


class CategoryBase(BaseModel):
    """
    Base category model with common fields

    Attributes:
        name: Category name (required, 3-255 characters)
        slug: URL-friendly slug (auto-generated from name if not provided)
        description: Category description
        parent_id: Parent category ID (None for root categories)
        level: Hierarchy level (1-20, unlimited depth)
        icon: Icon identifier (e.g., "fa-code", "mdi-laptop")
        color: Color code (e.g., "#3498db")
        order_index: Display order within parent (0-based)
        is_active: Category active status

    Example:
        >>> category = CategoryBase(
        ...     name="Programming",
        ...     level=2,
        ...     parent_id=1,
        ...     icon="fa-code"
        ... )
    """

    name: str = Field(..., min_length=3, max_length=255, description="Category name")
    slug: Optional[str] = Field(None, max_length=255, description="URL-friendly slug")
    description: Optional[str] = Field(None, max_length=2000, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID (None for root)")
    level: int = Field(..., ge=1, le=20, description="Hierarchy level (1-20)")
    icon: Optional[str] = Field(None, max_length=100, description="Icon identifier")
    color: Optional[str] = Field(None, max_length=20, description="Color code")
    order_index: int = Field(default=0, ge=0, description="Display order")
    is_active: bool = Field(default=True, description="Category active status")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str], info) -> Optional[str]:
        """
        Validate and auto-generate slug from name if not provided

        Converts name to kebab-case (lowercase, hyphen-separated)
        """
        if v is None:
            # Auto-generate slug from name
            name = info.data.get('name', '')
            if name:
                # Convert to lowercase, replace spaces and special chars with hyphens
                slug = re.sub(r'[^\w\s-]', '', name.lower())
                slug = re.sub(r'[-\s]+', '-', slug).strip('-')
                return slug
            return None

        # Validate provided slug
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')

        return v

    @field_validator('level')
    @classmethod
    def validate_level(cls, v: int, info) -> int:
        """
        Validate category level

        - Level 1: Root categories (no parent)
        - Level 2-5: Sub-categories (must have parent)
        """
        parent_id = info.data.get('parent_id')

        if v == 1 and parent_id is not None:
            raise ValueError('Level 1 categories cannot have a parent')

        if v > 1 and parent_id is None:
            raise ValueError(f'Level {v} categories must have a parent_id')

        return v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color code"""
        if v is not None:
            if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
                raise ValueError('Color must be a valid hex code (e.g., #3498db)')
        return v

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "name": "Web Development",
                "slug": "web-development",
                "description": "Learn web development with modern frameworks",
                "parent_id": 5,
                "level": 4,
                "icon": "fa-globe",
                "color": "#3498db",
                "order_index": 0,
                "is_active": True
            }
        }
    }


class CategoryCreate(CategoryBase):
    """
    Schema for creating a new category

    Note: Slug is auto-generated from name if not provided

    Example:
        >>> category_data = CategoryCreate(
        ...     name="Python Programming",
        ...     parent_id=2,
        ...     level=3,
        ...     description="Learn Python from scratch",
        ...     icon="fa-python",
        ...     color="#3776ab"
        ... )
    """

    pass


class CategoryUpdate(BaseModel):
    """
    Schema for updating a category

    All fields are optional for partial updates.
    Cannot change level or parent_id to avoid breaking hierarchy.

    Example:
        >>> update = CategoryUpdate(
        ...     name="Advanced Python",
        ...     description="Updated description",
        ...     is_active=True
        ... )
    """

    name: Optional[str] = Field(None, min_length=3, max_length=255)
    slug: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    icon: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=20)
    order_index: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Validate slug format"""
        if v is not None:
            if not re.match(r'^[a-z0-9-]+$', v):
                raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v

    @field_validator('color')
    @classmethod
    def validate_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate hex color code"""
        if v is not None:
            if not re.match(r'^#[0-9A-Fa-f]{6}$', v):
                raise ValueError('Color must be a valid hex code (e.g., #3498db)')
        return v

    model_config = {
        "from_attributes": True
    }


class CategoryResponse(BaseModel):
    """
    Schema for category response

    Complete category data returned by API with flexible depth support

    Example:
        >>> category = CategoryResponse(
        ...     category_id=5,
        ...     name="Python",
        ...     slug="python",
        ...     parent_id=2,
        ...     level=3,
        ...     path="IT/Programming/Python",
        ...     course_count=42,
        ...     created_at=datetime.now()
        ... )
    """

    category_id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly slug")
    description: Optional[str] = Field(None, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    level: int = Field(..., ge=1, le=20, description="Hierarchy level (1-20)")
    icon: Optional[str] = Field(None, description="Icon identifier")
    color: Optional[str] = Field(None, description="Color code")
    order_index: int = Field(..., description="Display order")
    is_active: bool = Field(default=True, description="Active status")
    course_count: Optional[int] = Field(0, description="Number of courses in this category")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    # New fields for flexible hierarchy
    path: Optional[str] = Field(None, description="Full path from root (e.g., 'IT/Netzwerk/Cisco')")
    root_id: Optional[int] = Field(None, description="Root category ID for this branch")
    path_ids: Optional[List[int]] = Field(None, description="Array of category IDs from root to this category")
    total_course_count: Optional[int] = Field(0, description="Total courses including all descendants")

    # Multi-language support
    name_en: Optional[str] = Field(None, description="English name")
    name_es: Optional[str] = Field(None, description="Spanish name")
    name_fr: Optional[str] = Field(None, description="French name")

    # Optional fields for tree representation
    parent_name: Optional[str] = Field(None, description="Parent category name")
    children: Optional[List['CategoryResponse']] = Field(None, description="Child categories")
    has_children: Optional[bool] = Field(None, description="Whether category has children")

    model_config = {
        "from_attributes": True
    }


class CategoryTreeNode(BaseModel):
    """
    Schema for a single node in the category tree

    Used for hierarchical tree representation with unlimited depth

    Example:
        >>> node = CategoryTreeNode(
        ...     category_id=1,
        ...     name="IT & Software",
        ...     level=1,
        ...     path="IT & Software",
        ...     children=[child1, child2, child3]
        ... )
    """

    category_id: int = Field(..., description="Category ID")
    name: str = Field(..., description="Category name")
    slug: str = Field(..., description="URL-friendly slug")
    description: Optional[str] = Field(None, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    level: int = Field(..., ge=1, le=20, description="Hierarchy level (1-20)")
    icon: Optional[str] = Field(None, description="Icon identifier")
    color: Optional[str] = Field(None, description="Color code")
    order_index: int = Field(default=0, description="Display order")
    is_active: bool = Field(default=True, description="Active status")
    course_count: int = Field(0, description="Number of courses")
    children: List['CategoryTreeNode'] = Field(default_factory=list, description="Child categories")

    # New fields for flexible hierarchy
    path: Optional[str] = Field(None, description="Full path from root")
    root_id: Optional[int] = Field(None, description="Root category ID")
    path_ids: Optional[List[int]] = Field(None, description="Array of category IDs from root")
    total_course_count: Optional[int] = Field(0, description="Total courses including descendants")

    @computed_field
    @property
    def has_children(self) -> bool:
        """Check if category has child categories"""
        return len(self.children) > 0

    @computed_field
    @property
    def total_courses(self) -> int:
        """Calculate total courses including all descendants"""
        total = self.course_count
        for child in self.children:
            total += child.total_courses
        return total

    model_config = {
        "from_attributes": True
    }


class CategoryTreeResponse(BaseModel):
    """
    Schema for complete category tree response

    Returns hierarchical tree structure with unlimited depth (practical limit: 20)

    Example:
        >>> tree = CategoryTreeResponse(
        ...     categories=[root1, root2, root3],
        ...     total_categories=150,
        ...     max_level=8
        ... )
    """

    categories: List[CategoryTreeNode] = Field(..., description="Root categories with children")
    total_categories: int = Field(..., description="Total number of categories")
    max_level: int = Field(..., description="Maximum level depth found in tree")
    active_categories: int = Field(..., description="Number of active categories")

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "categories": [
                    {
                        "category_id": 1,
                        "name": "IT & Software",
                        "slug": "it-software",
                        "level": 1,
                        "path": "IT & Software",
                        "children": [
                            {
                                "category_id": 2,
                                "name": "Programming",
                                "slug": "programming",
                                "level": 2,
                                "path": "IT & Software/Programming",
                                "parent_id": 1,
                                "children": []
                            }
                        ]
                    }
                ],
                "total_categories": 150,
                "max_level": 8,
                "active_categories": 142
            }
        }
    }


class CategoryListResponse(BaseModel):
    """
    Schema for paginated category list response

    Returns flat list of categories with pagination

    Example:
        >>> response = CategoryListResponse(
        ...     items=[cat1, cat2, cat3],
        ...     total=50,
        ...     page=1,
        ...     per_page=20
        ... )
    """

    items: List[CategoryResponse] = Field(..., description="List of categories")
    total: int = Field(..., description="Total number of categories")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    total_pages: int = Field(..., description="Total number of pages")

    model_config = {
        "from_attributes": True
    }


class CategoryReorderRequest(BaseModel):
    """
    Schema for reordering categories

    Example:
        >>> reorder = CategoryReorderRequest(
        ...     category_orders=[
        ...         {"category_id": 5, "order_index": 0},
        ...         {"category_id": 3, "order_index": 1},
        ...         {"category_id": 8, "order_index": 2}
        ...     ]
        ... )
    """

    category_orders: List[dict] = Field(
        ...,
        description="List of category IDs with new order indices",
        min_length=1
    )

    @field_validator('category_orders')
    @classmethod
    def validate_category_orders(cls, v: List[dict]) -> List[dict]:
        """Validate category order structure"""
        for item in v:
            if 'category_id' not in item or 'order_index' not in item:
                raise ValueError('Each item must have category_id and order_index')
            if not isinstance(item['category_id'], int) or not isinstance(item['order_index'], int):
                raise ValueError('category_id and order_index must be integers')
            if item['order_index'] < 0:
                raise ValueError('order_index must be >= 0')
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "category_orders": [
                    {"category_id": 5, "order_index": 0},
                    {"category_id": 3, "order_index": 1},
                    {"category_id": 8, "order_index": 2}
                ]
            }
        }
    }


class CategoryMoveRequest(BaseModel):
    """
    Schema for moving a category to a new parent

    Example:
        >>> move_request = CategoryMoveRequest(
        ...     new_parent_id=5
        ... )
        >>> # Or to make it a root category:
        >>> move_request = CategoryMoveRequest(
        ...     new_parent_id=None
        ... )
    """

    new_parent_id: Optional[int] = Field(
        None,
        description="New parent category ID (None to make it a root category)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "new_parent_id": 5
            }
        }
    }


# Update forward references for recursive models
CategoryResponse.model_rebuild()
CategoryTreeNode.model_rebuild()
