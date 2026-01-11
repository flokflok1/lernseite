"""
Math Pattern Entity (DDD Domain Entity)

Represents a math calculation pattern with formula templates and step definitions.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List


@dataclass
class MathPattern:
    """
    Math Pattern domain entity.

    Represents a reusable math calculation pattern (e.g., Bezugskalkulation,
    Prozentrechnung, Dreisatz) with dynamic formula templates and step definitions.

    All configuration stored in JSONB fields - completely flexible.

    Attributes:
        pattern_id: UUID
        category_id: Parent category UUID
        pattern_code: Unique code (e.g., 'bezugskalkulation')
        name: Pattern name
        description: Pattern description
        formula_template: Formula template string
        formula_latex: LaTeX format formula
        variables: JSONB list of variables (e.g., [{"var": "G", "name": "Grundwert", "unit": "€"}])
        steps_template: JSONB list of calculation steps
        example_values: JSONB dict with example values
        difficulty: Difficulty level (1-5)
        ihk_relevant: IHK exam relevance flag
        tags: JSONB list of tags
        sort_order: Display order
        is_active: Active status
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    pattern_id: str
    pattern_code: str
    name: str
    formula_template: str
    variables: List[Dict[str, Any]]
    steps_template: List[Dict[str, Any]]
    category_id: Optional[str] = None
    description: Optional[str] = None
    formula_latex: Optional[str] = None
    example_values: Optional[Dict[str, Any]] = None
    difficulty: int = 1
    ihk_relevant: bool = False
    tags: Optional[List[str]] = None
    sort_order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate math pattern entity."""
        if not self.pattern_id or not self.pattern_id.strip():
            raise ValueError("Pattern ID cannot be empty")
        if not self.pattern_code or not self.pattern_code.strip():
            raise ValueError("Pattern code cannot be empty")
        if not self.name or not self.name.strip():
            raise ValueError("Name cannot be empty")
        if not self.formula_template or not self.formula_template.strip():
            raise ValueError("Formula template cannot be empty")
        if not self.variables:
            raise ValueError("Variables list cannot be empty")
        if not self.steps_template:
            raise ValueError("Steps template list cannot be empty")
        if self.difficulty < 1 or self.difficulty > 5:
            raise ValueError("Difficulty must be between 1 and 5")

    def activate(self) -> None:
        """Activate this pattern."""
        self.is_active = True
        self.updated_at = datetime.utcnow()

    def deactivate(self) -> None:
        """Deactivate this pattern."""
        self.is_active = False
        self.updated_at = datetime.utcnow()

    def update_metadata(self, **kwargs) -> None:
        """
        Update pattern metadata.

        Args:
            **kwargs: Fields to update
        """
        allowed_fields = {
            'name', 'description', 'formula_template', 'formula_latex',
            'difficulty', 'ihk_relevant', 'sort_order'
        }

        for field, value in kwargs.items():
            if field in allowed_fields and hasattr(self, field):
                setattr(self, field, value)

        self.updated_at = datetime.utcnow()

    def update_variables(self, variables: List[Dict[str, Any]]) -> None:
        """
        Update pattern variables (JSONB).

        Args:
            variables: List of variable definitions
        """
        if not variables:
            raise ValueError("Variables list cannot be empty")
        self.variables = variables
        self.updated_at = datetime.utcnow()

    def update_steps(self, steps: List[Dict[str, Any]]) -> None:
        """
        Update pattern calculation steps (JSONB).

        Args:
            steps: List of step definitions
        """
        if not steps:
            raise ValueError("Steps template list cannot be empty")
        self.steps_template = steps
        self.updated_at = datetime.utcnow()

    def update_example_values(self, example_values: Dict[str, Any]) -> None:
        """
        Update example values for tutorial (JSONB).

        Args:
            example_values: Dictionary of example values
        """
        self.example_values = example_values
        self.updated_at = datetime.utcnow()

    def add_tag(self, tag: str) -> None:
        """Add a tag to this pattern."""
        if self.tags is None:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.utcnow()

    def remove_tag(self, tag: str) -> None:
        """Remove a tag from this pattern."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.utcnow()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of math pattern.

        Returns:
            Summary dict with key information
        """
        return {
            'pattern_id': self.pattern_id,
            'pattern_code': self.pattern_code,
            'name': self.name,
            'category_id': self.category_id,
            'difficulty': self.difficulty,
            'ihk_relevant': self.ihk_relevant,
            'is_active': self.is_active,
            'tags': self.tags
        }
