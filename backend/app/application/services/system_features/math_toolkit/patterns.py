"""
Pattern and formula database management module.

Handles retrieval and management of mathematical patterns and formulas from DB.
"""

from typing import Dict, List, Optional
import json
import logging

from app.infrastructure.persistence.repositories.math_toolkit import (
    MathPatternsProgressRepository
)

logger = logging.getLogger(__name__)


class PatternManager:
    """Manages patterns and formulas from database."""

    @staticmethod
    def get_categories(active_only: bool = True) -> List[Dict]:
        """
        Retrieve all pattern categories.

        Args:
            active_only: Only return active categories

        Returns:
            List of category dictionaries
        """
        return MathPatternsProgressRepository.get_categories(active_only)

    @staticmethod
    def get_category_by_code(code: str) -> Optional[Dict]:
        """
        Retrieve category by code.

        Args:
            code: Category code

        Returns:
            Category dictionary or None
        """
        return MathPatternsProgressRepository.get_category_by_code(code)

    @staticmethod
    def get_patterns(
        category_code: str = None,
        ihk_only: bool = False,
        difficulty: int = None,
        active_only: bool = True
    ) -> List[Dict]:
        """
        Retrieve patterns with optional filters.

        Args:
            category_code: Filter by category
            ihk_only: Only IHK-relevant patterns
            difficulty: Filter by difficulty level
            active_only: Only active patterns

        Returns:
            List of pattern dictionaries
        """
        return MathPatternsProgressRepository.get_patterns(
            active_only, category_code, ihk_only, difficulty
        )

    @staticmethod
    def get_pattern_by_id(pattern_id: str) -> Optional[Dict]:
        """
        Retrieve pattern by ID.

        Args:
            pattern_id: Pattern identifier

        Returns:
            Pattern dictionary or None
        """
        return MathPatternsProgressRepository.get_pattern_by_id(pattern_id)

    @staticmethod
    def get_pattern_by_code(pattern_code: str) -> Optional[Dict]:
        """
        Retrieve pattern by code.

        Args:
            pattern_code: Pattern code

        Returns:
            Pattern dictionary or None
        """
        return MathPatternsProgressRepository.get_pattern_by_code(pattern_code)

    @staticmethod
    def get_formulas(
        category_code: str = None,
        favorites_only: bool = False
    ) -> List[Dict]:
        """
        Retrieve formulas from library.

        Args:
            category_code: Filter by category
            favorites_only: Only favorite formulas

        Returns:
            List of formula dictionaries
        """
        return MathPatternsProgressRepository.get_formulas(
            category_code, favorites_only
        )

    @staticmethod
    def increment_formula_usage(formula_id: str) -> bool:
        """
        Increment usage counter for formula.

        Args:
            formula_id: Formula identifier

        Returns:
            Success status
        """
        return MathPatternsProgressRepository.increment_formula_usage(formula_id)

    @staticmethod
    def toggle_formula_favorite(formula_id: str) -> Optional[bool]:
        """
        Toggle favorite status for formula.

        Args:
            formula_id: Formula identifier

        Returns:
            New favorite status or None if failed
        """
        result = MathPatternsProgressRepository.toggle_formula_favorite(formula_id)
        return result.get('is_favorite') if result else None

    @staticmethod
    def create_pattern(
        pattern_code: str,
        name: str,
        category_code: str,
        formula_template: str,
        variables: List[Dict],
        steps_template: List[Dict],
        **kwargs
    ) -> Optional[str]:
        """
        Create new pattern.

        Args:
            pattern_code: Unique pattern code
            name: Pattern name
            category_code: Category code
            formula_template: Formula template string
            variables: List of variable definitions
            steps_template: List of step definitions
            **kwargs: Additional fields (description, difficulty, etc.)

        Returns:
            New pattern_id or None if failed
        """
        cat = MathPatternsProgressRepository.get_category_by_code(category_code)
        if not cat:
            return None

        result = MathPatternsProgressRepository.insert_pattern(
            pattern_code, name, cat['category_id'],
            kwargs.get('description'),
            formula_template,
            kwargs.get('formula_latex'),
            json.dumps(variables),
            json.dumps(steps_template),
            json.dumps(kwargs.get('example_values', {})),
            kwargs.get('difficulty', 1),
            kwargs.get('ihk_relevant', False),
            json.dumps(kwargs.get('tags', []))
        )
        return str(result['pattern_id']) if result else None

    @staticmethod
    def create_formula(
        name: str,
        formula_text: str,
        category_code: str = None,
        **kwargs
    ) -> Optional[str]:
        """
        Create new formula.

        Args:
            name: Formula name
            formula_text: Formula expression
            category_code: Optional category code
            **kwargs: Additional fields (description, latex, etc.)

        Returns:
            New formula_id or None if failed
        """
        category_id = None
        if category_code:
            cat = MathPatternsProgressRepository.get_category_by_code(category_code)
            category_id = cat['category_id'] if cat else None

        result = MathPatternsProgressRepository.insert_formula(
            name, formula_text, category_id,
            kwargs.get('description'),
            kwargs.get('formula_latex'),
            kwargs.get('formula_display'),
            json.dumps(kwargs.get('variables', [])),
            json.dumps(kwargs.get('example_input', {})),
            kwargs.get('example_output'),
            json.dumps(kwargs.get('tags', []))
        )
        return str(result['formula_id']) if result else None
