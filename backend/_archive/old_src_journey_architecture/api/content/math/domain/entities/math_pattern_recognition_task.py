"""
Math Pattern Recognition Task Entity (DDD Domain Entity)

Represents a pattern recognition task for learning.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any


@dataclass
class MathPatternRecognitionTask:
    """
    Math Pattern Recognition Task domain entity.

    Represents a task for recognizing and working with math patterns.
    Task data and solution stored in JSONB - completely flexible.

    Task types (from DB):
    - identify_pattern: "Which pattern is this?"
    - order_steps: "Put steps in correct order"
    - fill_formula: "Complete the formula"
    - match_values: "Match values to variables"
    - spot_error: "Find the error"
    - complete_calculation: "Complete the calculation"

    Attributes:
        task_id: UUID
        pattern_id: Related pattern UUID
        task_type: Type of task (from DB enum)
        task_text: Task description text
        task_data: JSONB dict with task-specific data
        solution: JSONB dict with solution data
        difficulty: Difficulty level (1-5)
        is_active: Active status
        created_at: Creation timestamp
    """

    task_id: str
    pattern_id: str
    task_type: str
    task_text: str
    task_data: Dict[str, Any]
    solution: Dict[str, Any]
    difficulty: int = 1
    is_active: bool = True
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate math pattern recognition task entity."""
        if not self.task_id or not self.task_id.strip():
            raise ValueError("Task ID cannot be empty")
        if not self.pattern_id or not self.pattern_id.strip():
            raise ValueError("Pattern ID cannot be empty")
        if not self.task_type or not self.task_type.strip():
            raise ValueError("Task type cannot be empty")
        if not self.task_text or not self.task_text.strip():
            raise ValueError("Task text cannot be empty")
        if not self.task_data:
            raise ValueError("Task data cannot be empty")
        if not self.solution:
            raise ValueError("Solution cannot be empty")
        if self.difficulty < 1 or self.difficulty > 5:
            raise ValueError("Difficulty must be between 1 and 5")

        # Validate task_type is one of the allowed types
        valid_types = {
            'identify_pattern', 'order_steps', 'fill_formula',
            'match_values', 'spot_error', 'complete_calculation'
        }
        if self.task_type not in valid_types:
            raise ValueError(f"Invalid task type. Must be one of: {valid_types}")

    def activate(self) -> None:
        """Activate this task."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate this task."""
        self.is_active = False

    def check_solution(self, user_answer: Dict[str, Any]) -> bool:
        """
        Check if user's answer matches the solution.

        Args:
            user_answer: User's answer data

        Returns:
            True if answer is correct

        Note: This is a simple equality check. More complex
        validation logic should be in the service layer.
        """
        return user_answer == self.solution
