"""
Calculator history and operations module.

Manages calculator history entries and keystroke recording.
"""

from typing import Dict, List, Optional
import json
import logging

from app.infrastructure.persistence.repositories.math_toolkit import (
    MathSessionsStepsRepository
)

logger = logging.getLogger(__name__)


class CalculatorHistory:
    """Manages calculator history and entries."""

    @staticmethod
    def save_calculator_entry(
        user_id: str,
        expression: str,
        result: float,
        result_display: str,
        session_id: str = None,
        keystrokes: List[str] = None,
        memory_used: bool = False,
        memory_value: float = None
    ) -> Optional[str]:
        """
        Save calculator entry to history.

        Args:
            user_id: User identifier
            expression: Mathematical expression
            result: Numeric result
            result_display: Formatted result for display
            session_id: Optional session context
            keystrokes: List of keystrokes used
            memory_used: Whether memory was used
            memory_value: Memory value if used

        Returns:
            New history_id or None if failed
        """
        result_row = MathSessionsStepsRepository.insert_calculator_entry(
            user_id, session_id, expression, result, result_display,
            json.dumps(keystrokes or []), memory_used, memory_value
        )
        return str(result_row['history_id']) if result_row else None

    @staticmethod
    def get_calculator_history(user_id: str, limit: int = 50) -> List[Dict]:
        """
        Retrieve calculator history for user.

        Args:
            user_id: User identifier
            limit: Maximum entries to return

        Returns:
            List of history entries
        """
        return MathSessionsStepsRepository.get_calculator_history(user_id, limit)
