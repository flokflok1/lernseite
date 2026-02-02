"""
Mathematical expression solver module.

Provides safe evaluation of mathematical expressions using limited namespace.
"""

import math
import logging
from typing import Dict, Any, List, Optional

from .parser import ExpressionParser

logger = logging.getLogger(__name__)


class MathSolver:
    """Evaluates mathematical expressions safely."""

    # Safe namespace for eval
    SAFE_NAMESPACE = {
        '__builtins__': {},
        'sqrt': math.sqrt,
        'pow': pow,
        'abs': abs,
        'round': round
    }

    @staticmethod
    def evaluate_expression(expression: str) -> Dict[str, Any]:
        """
        Evaluate a mathematical expression safely.

        Args:
            expression: User input expression

        Returns:
            Dict with keys:
            - success (bool)
            - result (float, optional)
            - display (str, optional)
            - error (str, optional)
            - expression (str)
        """
        try:
            # Normalize
            normalized = ExpressionParser.normalize_expression(expression)

            # Validate characters
            is_valid, error_msg = ExpressionParser.validate_expression(normalized)
            if not is_valid:
                return {'success': False, 'error': error_msg}

            # Check parentheses
            balanced, error_msg = ExpressionParser.check_balanced_parentheses(
                normalized
            )
            if not balanced:
                return {'success': False, 'error': error_msg}

            # Evaluate safely
            result = eval(normalized, MathSolver.SAFE_NAMESPACE)

            # Format result
            if isinstance(result, float):
                result = round(result, 6)
                result_display = f"{result:g}"
            else:
                result_display = str(result)

            return {
                'success': True,
                'result': result,
                'display': result_display,
                'expression': expression
            }

        except ZeroDivisionError:
            return {'success': False, 'error': 'Division durch Null'}
        except Exception as e:
            logger.warning(f"Fehler bei Auswertung: {expression} - {e}")
            return {'success': False, 'error': 'Ungültiger Ausdruck'}

    @staticmethod
    def format_result(value: float, precision: int = 6) -> str:
        """
        Format numeric result for display.

        Args:
            value: Numeric value to format
            precision: Decimal places to round to

        Returns:
            Formatted string with trailing zeros removed
        """
        rounded = round(value, precision)
        return f"{rounded:g}"
