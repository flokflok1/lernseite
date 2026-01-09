"""
Pattern and formula database management module.

Handles retrieval and management of mathematical patterns and formulas from DB.
"""

from typing import Dict, List, Optional
import json
import logging

from app.repositories.base_repository import BaseRepository

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
        query = """
            SELECT category_id, category_code, name, description, icon, color, sort_order
            FROM math_pattern_categories
            WHERE ($1 = FALSE OR is_active = TRUE)
            ORDER BY sort_order, name
        """
        return BaseRepository.fetch_all(query, (active_only,)) or []

    @staticmethod
    def get_category_by_code(code: str) -> Optional[Dict]:
        """
        Retrieve category by code.

        Args:
            code: Category code

        Returns:
            Category dictionary or None
        """
        query = """
            SELECT category_id, category_code, name, description, icon, color
            FROM math_pattern_categories
            WHERE category_code = %s AND is_active = TRUE
        """
        return BaseRepository.fetch_one(query, (code,))

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
        query = """
            SELECT
                p.pattern_id, p.pattern_code, p.name, p.description,
                p.formula_template, p.formula_latex,
                p.variables, p.steps_template, p.example_values,
                p.difficulty, p.ihk_relevant, p.tags,
                c.category_code, c.name as category_name, c.icon as category_icon
            FROM math_patterns p
            LEFT JOIN math_pattern_categories c ON p.category_id = c.category_id
            WHERE ($1 = FALSE OR p.is_active = TRUE)
              AND ($2::text IS NULL OR c.category_code = $2)
              AND ($3 = FALSE OR p.ihk_relevant = TRUE)
              AND ($4::int IS NULL OR p.difficulty = $4)
            ORDER BY c.sort_order, p.sort_order, p.name
        """
        return BaseRepository.fetch_all(
            query, (active_only, category_code, ihk_only, difficulty)
        ) or []

    @staticmethod
    def get_pattern_by_id(pattern_id: str) -> Optional[Dict]:
        """
        Retrieve pattern by ID.

        Args:
            pattern_id: Pattern identifier

        Returns:
            Pattern dictionary or None
        """
        query = """
            SELECT
                p.pattern_id, p.pattern_code, p.name, p.description,
                p.formula_template, p.formula_latex,
                p.variables, p.steps_template, p.example_values,
                p.difficulty, p.ihk_relevant, p.tags,
                c.category_code, c.name as category_name, c.icon as category_icon
            FROM math_patterns p
            LEFT JOIN math_pattern_categories c ON p.category_id = c.category_id
            WHERE p.pattern_id = %s
        """
        return BaseRepository.fetch_one(query, (pattern_id,))

    @staticmethod
    def get_pattern_by_code(pattern_code: str) -> Optional[Dict]:
        """
        Retrieve pattern by code.

        Args:
            pattern_code: Pattern code

        Returns:
            Pattern dictionary or None
        """
        query = """
            SELECT
                p.pattern_id, p.pattern_code, p.name, p.description,
                p.formula_template, p.formula_latex,
                p.variables, p.steps_template, p.example_values,
                p.difficulty, p.ihk_relevant, p.tags,
                c.category_code, c.name as category_name
            FROM math_patterns p
            LEFT JOIN math_pattern_categories c ON p.category_id = c.category_id
            WHERE p.pattern_code = %s AND p.is_active = TRUE
        """
        return BaseRepository.fetch_one(query, (pattern_code,))

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
        query = """
            SELECT
                f.formula_id, f.name, f.description,
                f.formula_text, f.formula_latex, f.formula_display,
                f.variables, f.example_input, f.example_output,
                f.is_favorite, f.usage_count,
                c.category_code, c.name as category_name, c.icon as category_icon
            FROM math_formulas f
            LEFT JOIN math_pattern_categories c ON f.category_id = c.category_id
            WHERE f.is_active = TRUE
              AND ($1::text IS NULL OR c.category_code = $1)
              AND ($2 = FALSE OR f.is_favorite = TRUE)
            ORDER BY f.is_favorite DESC, f.usage_count DESC, f.name
        """
        return BaseRepository.fetch_all(query, (category_code, favorites_only)) or []

    @staticmethod
    def increment_formula_usage(formula_id: str) -> bool:
        """
        Increment usage counter for formula.

        Args:
            formula_id: Formula identifier

        Returns:
            Success status
        """
        query = """
            UPDATE math_formulas
            SET usage_count = usage_count + 1
            WHERE formula_id = %s
        """
        return BaseRepository.execute(query, (formula_id,))

    @staticmethod
    def toggle_formula_favorite(formula_id: str) -> Optional[bool]:
        """
        Toggle favorite status for formula.

        Args:
            formula_id: Formula identifier

        Returns:
            New favorite status or None if failed
        """
        query = """
            UPDATE math_formulas
            SET is_favorite = NOT is_favorite
            WHERE formula_id = %s
            RETURNING is_favorite
        """
        result = BaseRepository.fetch_one(query, (formula_id,))
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
        cat = PatternManager.get_category_by_code(category_code)
        if not cat:
            return None

        query = """
            INSERT INTO math_patterns
                (pattern_code, name, category_id, description,
                 formula_template, formula_latex, variables, steps_template,
                 example_values, difficulty, ihk_relevant, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING pattern_id
        """
        result = BaseRepository.fetch_one(query, (
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
        ))
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
            cat = PatternManager.get_category_by_code(category_code)
            category_id = cat['category_id'] if cat else None

        query = """
            INSERT INTO math_formulas
                (name, formula_text, category_id, description,
                 formula_latex, formula_display, variables,
                 example_input, example_output, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING formula_id
        """
        result = BaseRepository.fetch_one(query, (
            name, formula_text, category_id,
            kwargs.get('description'),
            kwargs.get('formula_latex'),
            kwargs.get('formula_display'),
            json.dumps(kwargs.get('variables', [])),
            json.dumps(kwargs.get('example_input', {})),
            kwargs.get('example_output'),
            json.dumps(kwargs.get('tags', []))
        ))
        return str(result['formula_id']) if result else None
