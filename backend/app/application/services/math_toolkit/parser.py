"""
Expression parsing and validation module.

Handles safe parsing of mathematical expressions without using eval().
"""

import re
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ExpressionParser:
    """Parses and validates mathematical expressions safely."""

    # Allowed characters in expressions
    ALLOWED_PATTERN = r'^[\d\s\+\-\*\/\.\(\)\%\^]+$'

    @staticmethod
    def normalize_expression(expression: str) -> str:
        """
        Normalize expression to standard format.

        Converts:
        - German decimal separators (,) to dots
        - × to *
        - ÷ to /
        - ^ to **
        - Percentage calculations to formulas

        Args:
            expression: Raw mathematical expression

        Returns:
            Normalized expression string
        """
        expr = expression.strip()
        expr = expr.replace(',', '.')  # Deutsche Dezimalzahlen
        expr = expr.replace('×', '*').replace('÷', '/')
        expr = expr.replace('^', '**')

        # Prozent-Berechnung: "20% of 100" -> "(20/100)*100"
        expr = re.sub(
            r'(\d+(?:\.\d+)?)\s*%\s*of\s*(\d+(?:\.\d+)?)',
            r'(\1/100)*\2',
            expr,
            flags=re.IGNORECASE
        )

        return expr

    @staticmethod
    def validate_expression(expression: str) -> tuple[bool, Optional[str]]:
        """
        Validate that expression contains only allowed characters.

        Args:
            expression: Normalized expression to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not re.match(ExpressionParser.ALLOWED_PATTERN, expression):
            return False, 'Ungültige Zeichen im Ausdruck'
        return True, None

    @staticmethod
    def check_balanced_parentheses(expression: str) -> tuple[bool, Optional[str]]:
        """
        Check that parentheses are balanced.

        Args:
            expression: Expression to check

        Returns:
            Tuple of (is_balanced, error_message)
        """
        count = 0
        for char in expression:
            if char == '(':
                count += 1
            elif char == ')':
                count -= 1
            if count < 0:
                return False, 'Unausgeglichene Klammern'

        if count != 0:
            return False, 'Unausgeglichene Klammern'

        return True, None
