"""
Scaffolding hints module.

Provides contextual hints based on pattern, error type, and scaffolding level.
"""

from typing import Optional
import logging

from app.infrastructure.persistence.repositories.math_toolkit import (
    MathSessionsStepsRepository
)

logger = logging.getLogger(__name__)


class HintProvider:
    """Manages scaffolding hints for different levels."""

    @staticmethod
    def get_hint(
        pattern_id: str,
        hint_type: str,
        scaffolding_level: int,
        step_number: int = None,
        error_type: str = None
    ) -> Optional[str]:
        """
        Get appropriate hint based on context and level.

        Selects hints with priority to specific step and error type,
        falling back to general hints.

        Args:
            pattern_id: Pattern identifier
            hint_type: Type of hint needed
            scaffolding_level: User scaffolding level (1-3)
            step_number: Optional specific step number
            error_type: Optional error type context

        Returns:
            Hint string appropriate for level, or None
        """
        result = MathSessionsStepsRepository.get_hint(
            pattern_id, hint_type, step_number, error_type
        )

        if not result:
            return None

        # Select hint based on scaffolding level
        if scaffolding_level == 1:
            return result['hint_level_1']
        elif scaffolding_level == 2:
            return result['hint_level_2'] or result['hint_level_1']
        else:
            # Level 3: most detailed hint
            return result['hint_level_3'] or "Versuche es nochmal!"
