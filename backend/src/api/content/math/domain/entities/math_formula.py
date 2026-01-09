"""
Math Formula Entity (DDD Domain Entity)

Represents a formula in the formula library.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class MathFormula:
    """
    Math Formula domain entity.

    Represents a formula in the quick-access formula library.
    Linked to patterns and categories.

    Attributes:
        formula_id: UUID
        category_id: Parent category UUID (optional)
        pattern_id: Related pattern UUID (optional)
        name: Formula name
        description: Formula description
        formula_text: Formula in text format
        formula_latex: Formula in LaTeX format
        formula_display: Formula display format
        variables: JSONB list of variable explanations
        example_input: JSONB dict with example input
        example_output: Example output string
        tags: JSONB list of tags
        is_favorite: Favorite flag
        usage_count: How many times used
        sort_order: Display order
        is_active: Active status
        created_at: Creation timestamp
    """

    formula_id: str
    name: str
    formula_text: str
    category_id: Optional[str] = None
    pattern_id: Optional[str] = None
    description: Optional[str] = None
    formula_latex: Optional[str] = None
    formula_display: Optional[str] = None
    variables: Optional[List[Dict[str, Any]]] = None
    example_input: Optional[Dict[str, Any]] = None
    example_output: Optional[str] = None
    tags: Optional[List[str]] = None
    is_favorite: bool = False
    usage_count: int = 0
    sort_order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate math formula entity."""
        if not self.formula_id or not self.formula_id.strip():
            raise ValueError("Formula ID cannot be empty")
        if not self.name or not self.name.strip():
            raise ValueError("Name cannot be empty")
        if not self.formula_text or not self.formula_text.strip():
            raise ValueError("Formula text cannot be empty")

    def mark_as_favorite(self) -> None:
        """Mark this formula as favorite."""
        self.is_favorite = True

    def unmark_as_favorite(self) -> None:
        """Unmark this formula as favorite."""
        self.is_favorite = False

    def increment_usage(self) -> None:
        """Increment usage counter."""
        self.usage_count += 1

    def add_tag(self, tag: str) -> None:
        """Add a tag to this formula."""
        if self.tags is None:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this formula."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
