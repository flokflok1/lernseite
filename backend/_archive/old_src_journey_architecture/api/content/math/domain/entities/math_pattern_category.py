"""
Math Pattern Category Entity (DDD Domain Entity)

Represents a category of math patterns (e.g., Percent, Calculation, Interest).
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MathPatternCategory:
    """
    Math Pattern Category domain entity.

    Represents a category grouping related math patterns
    (e.g., Prozentrechnung, Handelskalkulation, Zinsrechnung).

    Attributes:
        category_id: UUID
        category_code: Unique code (e.g., 'percent', 'calculation')
        name: Category name
        description: Category description
        icon: Icon identifier (emoji or icon name)
        color: Color code for UI
        sort_order: Display order
        is_active: Active status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    category_id: str
    category_code: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate math pattern category entity."""
        if not self.category_id or not self.category_id.strip():
            raise ValueError("Category ID cannot be empty")
        if not self.category_code or not self.category_code.strip():
            raise ValueError("Category code cannot be empty")
        if not self.name or not self.name.strip():
            raise ValueError("Name cannot be empty")

    def activate(self) -> None:
        """Activate this category."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate this category."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def update_metadata(self, **kwargs) -> None:
        """
        Update category metadata.

        Args:
            **kwargs: Fields to update
        """
        allowed_fields = {
            'name', 'description', 'icon', 'color', 'sort_order'
        }

        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)

        self.updated_at = datetime.utcnow()
