"""
Math Scaffolding Hint Entity (DDD Domain Entity)

Represents dynamic scaffolding hints for different skill levels.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class MathScaffoldingHint:
    """
    Math Scaffolding Hint domain entity.

    Represents adaptive hints that adjust to user's scaffolding level.
    Level 1 = full explanation, Level 2 = brief hint, Level 3 = minimal nudge.

    Hint types (from DB):
    - step_intro: Introduction for a step
    - step_help: Help during step execution
    - error_feedback: Feedback on error
    - success_praise: Praise on success
    - pattern_tip: General tip about pattern
    - calculator_tip: Calculator usage tip

    Attributes:
        hint_id: UUID
        pattern_id: Related pattern UUID (optional)
        hint_type: Type of hint (from DB enum)
        step_number: Step number if step-specific (optional)
        error_type: Error type if error-specific (optional)
        hint_level_1: Full explanation text
        hint_level_2: Brief hint text (optional)
        hint_level_3: Minimal nudge text (optional)
        trigger_condition: JSONB dict with trigger conditions
        sort_order: Display order
        is_active: Active status
        created_at: Creation timestamp
    """

    hint_id: str
    hint_type: str
    hint_level_1: str
    pattern_id: Optional[str] = None
    step_number: Optional[int] = None
    error_type: Optional[str] = None
    hint_level_2: Optional[str] = None
    hint_level_3: Optional[str] = None
    trigger_condition: Optional[Dict[str, Any]] = None
    sort_order: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate math scaffolding hint entity."""
        if not self.hint_id or not self.hint_id.strip():
            raise ValueError("Hint ID cannot be empty")
        if not self.hint_type or not self.hint_type.strip():
            raise ValueError("Hint type cannot be empty")
        if not self.hint_level_1 or not self.hint_level_1.strip():
            raise ValueError("Hint level 1 (full explanation) cannot be empty")

        # Validate hint_type is one of the allowed types
        valid_types = {
            'step_intro', 'step_help', 'error_feedback',
            'success_praise', 'pattern_tip', 'calculator_tip'
        }
        if self.hint_type not in valid_types:
            raise ValueError(f"Invalid hint type. Must be one of: {valid_types}")

        # Validate step_number if provided
        if self.step_number is not None and self.step_number < 1:
            raise ValueError("Step number must be positive")

    def get_hint_for_level(self, scaffolding_level: int) -> str:
        """
        Get appropriate hint text for scaffolding level.

        Args:
            scaffolding_level: User's current scaffolding level (1-3)

        Returns:
            Hint text for the level

        Raises:
            ValueError: If level is invalid
        """
        if scaffolding_level < 1 or scaffolding_level > 3:
            raise ValueError("Scaffolding level must be between 1 and 3")

        if scaffolding_level == 1:
            return self.hint_level_1
        elif scaffolding_level == 2:
            return self.hint_level_2 or self.hint_level_1  # Fallback to level 1
        elif scaffolding_level == 3:
            return self.hint_level_3 or self.hint_level_2 or self.hint_level_1  # Fallback cascade

    def activate(self) -> None:
        """Activate this hint."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate this hint."""
        self.is_active = False

    def matches_trigger(self, context: Dict[str, Any]) -> bool:
        """
        Check if this hint should be triggered based on context.

        Args:
            context: Context data to check against trigger_condition

        Returns:
            True if hint should be shown

        Note: Simple implementation. More complex trigger logic
        should be in the service layer.
        """
        if not self.trigger_condition:
            return True  # No condition means always show

        # Check each condition key
        for key, expected_value in self.trigger_condition.items():
            if key not in context or context[key] != expected_value:
                return False

        return True
