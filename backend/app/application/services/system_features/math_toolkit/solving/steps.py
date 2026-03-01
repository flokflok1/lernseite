"""
Calculation steps tracking module.

Records individual steps in multi-step calculations with validation.
"""

from typing import Dict, List, Optional
import json
import logging

from app.infrastructure.persistence.repositories.math_toolkit import (
    MathSessionsStepsRepository
)

logger = logging.getLogger(__name__)


class StepRecorder:
    """Records calculation steps in sessions."""

    @staticmethod
    def save_calculation_step(
        session_id: str,
        step_number: int,
        input_expression: str,
        input_values: Dict = None,
        result_value: float = None,
        result_display: str = None,
        calculator_keystrokes: List[str] = None,
        is_correct: bool = None,
        expected_value: float = None,
        error_type: str = None,
        hint_shown: str = None
    ) -> Optional[str]:
        """
        Save a calculation step.

        Args:
            session_id: Session identifier
            step_number: Step sequence number
            input_expression: The expression evaluated
            input_values: Input variable values
            result_value: Numeric result
            result_display: Formatted result
            calculator_keystrokes: Keystrokes used
            is_correct: Whether result was correct
            expected_value: Expected result for validation
            error_type: Type of error if incorrect
            hint_shown: Hint provided to user

        Returns:
            New step_id or None if failed
        """
        result = MathSessionsStepsRepository.insert_calculation_step(
            session_id, step_number, input_expression,
            json.dumps(input_values or {}),
            result_value, result_display,
            json.dumps(calculator_keystrokes or []),
            is_correct, expected_value, error_type, hint_shown
        )
        return str(result['step_id']) if result else None

    @staticmethod
    def get_session_steps(session_id: str) -> List[Dict]:
        """
        Retrieve all steps in a session.

        Args:
            session_id: Session identifier

        Returns:
            List of step dictionaries ordered by sequence
        """
        return MathSessionsStepsRepository.get_session_steps(session_id)
