"""
Math Calculator History Entity (DDD Domain Entity)

Represents calculator usage history for replay and analysis.
ALL data loaded from database - NO hardcoded values.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


@dataclass
class MathCalculatorHistory:
    """
    Math Calculator History domain entity.

    Represents a calculator calculation in the history for replay.

    Attributes:
        history_id: UUID
        session_id: Parent session UUID (optional)
        user_id: User UUID
        expression: Calculator expression string
        result: Calculated result (Decimal for precision)
        result_display: Result display string
        keystrokes: JSONB list of keystrokes for replay
        memory_used: Whether memory function was used
        memory_value: Memory value if used
        created_at: Creation timestamp
    """

    history_id: str
    user_id: str
    expression: str
    session_id: Optional[str] = None
    result: Optional[Decimal] = None
    result_display: Optional[str] = None
    keystrokes: Optional[List[str]] = None
    memory_used: bool = False
    memory_value: Optional[Decimal] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate math calculator history entity."""
        if not self.history_id or not self.history_id.strip():
            raise ValueError("History ID cannot be empty")
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        if not self.expression or not self.expression.strip():
            raise ValueError("Expression cannot be empty")

    def use_memory(self, value: Decimal) -> None:
        """
        Mark that memory function was used.

        Args:
            value: Memory value
        """
        self.memory_used = True
        self.memory_value = value
