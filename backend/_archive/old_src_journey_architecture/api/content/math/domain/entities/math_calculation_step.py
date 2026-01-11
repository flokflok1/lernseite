"""
Math Calculation Step Entity (DDD Domain Entity)

Represents a single calculation step in a session.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal


@dataclass
class MathCalculationStep:
    """
    Math Calculation Step domain entity.

    Represents a single calculation step with input, result, and evaluation.

    Attributes:
        step_id: UUID
        session_id: Parent session UUID
        step_number: Step number in sequence
        input_expression: Input expression string
        input_values: JSONB dict with input values
        result_value: Calculated result (Decimal for precision)
        result_display: Result display string
        calculator_keystrokes: JSONB list of keystrokes for replay
        is_correct: Whether the step was correct
        expected_value: Expected result value
        error_type: Error type if incorrect
        hint_shown: Hint text if shown
        created_at: Creation timestamp
    """

    step_id: str
    session_id: str
    step_number: int
    input_expression: str
    input_values: Optional[Dict[str, Any]] = None
    result_value: Optional[Decimal] = None
    result_display: Optional[str] = None
    calculator_keystrokes: Optional[List[str]] = None
    is_correct: Optional[bool] = None
    expected_value: Optional[Decimal] = None
    error_type: Optional[str] = None
    hint_shown: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate math calculation step entity."""
        if not self.step_id or not self.step_id.strip():
            raise ValueError("Step ID cannot be empty")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("Session ID cannot be empty")
        if self.step_number < 1:
            raise ValueError("Step number must be positive")
        if not self.input_expression or not self.input_expression.strip():
            raise ValueError("Input expression cannot be empty")

    def mark_as_correct(self) -> None:
        """Mark this step as correct."""
        self.is_correct = True

    def mark_as_incorrect(self, expected: Decimal, error_type: str) -> None:
        """
        Mark this step as incorrect.

        Args:
            expected: Expected correct value
            error_type: Type of error made
        """
        self.is_correct = False
        self.expected_value = expected
        self.error_type = error_type

    def show_hint(self, hint: str) -> None:
        """
        Show a hint for this step.

        Args:
            hint: Hint text to show
        """
        self.hint_shown = hint
