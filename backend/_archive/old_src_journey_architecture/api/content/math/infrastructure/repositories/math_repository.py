"""
Math Repository (Infrastructure Layer)

Database access for math toolkit system.
ALL data loaded dynamically from database - NO hardcoded values.

Handles 9 tables:
1. math_pattern_categories
2. math_patterns
3. math_formulas
4. math_toolkit_sessions
5. math_calculation_steps
6. math_calculator_history
7. math_user_progress
8. math_pattern_recognition_tasks
9. math_scaffolding_hints
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
import json
from datetime import datetime
from src.core.database import get_db_connection
from src.api.content.math.domain.entities.math_pattern_category import MathPatternCategory
from src.api.content.math.domain.entities.math_pattern import MathPattern
from src.api.content.math.domain.entities.math_formula import MathFormula
from src.api.content.math.domain.entities.math_toolkit_session import MathToolkitSession
from src.api.content.math.domain.entities.math_calculation_step import MathCalculationStep
from src.api.content.math.domain.entities.math_calculator_history import MathCalculatorHistory
from src.api.content.math.domain.entities.math_user_progress import MathUserProgress
from src.api.content.math.domain.entities.math_pattern_recognition_task import MathPatternRecognitionTask
from src.api.content.math.domain.entities.math_scaffolding_hint import MathScaffoldingHint


class MathRepository:
    """
    Repository for math toolkit database operations.

    ALL configurations loaded from database dynamically.
    NO hardcoded patterns, categories, or formulas.
    """

    # ============================================================================
    # MATH PATTERN CATEGORIES
    # ============================================================================

    @staticmethod
    def find_category_by_id(category_id: str) -> Optional[MathPatternCategory]:
        """Find math pattern category by ID."""
        query = """
            SELECT category_id, category_code, name, description, icon, color,
                   sort_order, is_active, created_at, updated_at
            FROM learning_methods.math_pattern_categories
            WHERE category_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (category_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return MathPatternCategory(
                    category_id=row[0],
                    category_code=row[1],
                    name=row[2],
                    description=row[3],
                    icon=row[4],
                    color=row[5],
                    sort_order=row[6],
                    is_active=row[7],
                    created_at=row[8],
                    updated_at=row[9]
                )

    @staticmethod
    def find_category_by_code(category_code: str) -> Optional[MathPatternCategory]:
        """Find math pattern category by code."""
        query = """
            SELECT category_id, category_code, name, description, icon, color,
                   sort_order, is_active, created_at, updated_at
            FROM learning_methods.math_pattern_categories
            WHERE category_code = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (category_code,))
                row = cur.fetchone()

                if not row:
                    return None

                return MathPatternCategory(
                    category_id=row[0],
                    category_code=row[1],
                    name=row[2],
                    description=row[3],
                    icon=row[4],
                    color=row[5],
                    sort_order=row[6],
                    is_active=row[7],
                    created_at=row[8],
                    updated_at=row[9]
                )

    @staticmethod
    def find_all_categories(active_only: bool = True) -> List[MathPatternCategory]:
        """Find all math pattern categories."""
        query = """
            SELECT category_id, category_code, name, description, icon, color,
                   sort_order, is_active, created_at, updated_at
            FROM learning_methods.math_pattern_categories
            WHERE 1=1
        """
        params = []

        if active_only:
            query += " AND is_active = TRUE"

        query += " ORDER BY sort_order ASC, name ASC"

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    MathPatternCategory(
                        category_id=row[0],
                        category_code=row[1],
                        name=row[2],
                        description=row[3],
                        icon=row[4],
                        color=row[5],
                        sort_order=row[6],
                        is_active=row[7],
                        created_at=row[8],
                        updated_at=row[9]
                    )
                    for row in rows
                ]

    # ============================================================================
    # MATH PATTERNS
    # ============================================================================

    @staticmethod
    def find_pattern_by_id(pattern_id: str) -> Optional[MathPattern]:
        """Find math pattern by ID."""
        query = """
            SELECT pattern_id, category_id, pattern_code, name, description,
                   formula_template, formula_latex, variables, steps_template,
                   example_values, difficulty, ihk_relevant, tags, sort_order,
                   is_active, created_at, updated_at
            FROM learning_methods.math_patterns
            WHERE pattern_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (pattern_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return MathPattern(
                    pattern_id=row[0],
                    category_id=row[1],
                    pattern_code=row[2],
                    name=row[3],
                    description=row[4],
                    formula_template=row[5],
                    formula_latex=row[6],
                    variables=row[7] or [],
                    steps_template=row[8] or [],
                    example_values=row[9],
                    difficulty=row[10],
                    ihk_relevant=row[11],
                    tags=row[12],
                    sort_order=row[13],
                    is_active=row[14],
                    created_at=row[15],
                    updated_at=row[16]
                )

    @staticmethod
    def find_pattern_by_code(pattern_code: str) -> Optional[MathPattern]:
        """Find math pattern by code."""
        query = """
            SELECT pattern_id, category_id, pattern_code, name, description,
                   formula_template, formula_latex, variables, steps_template,
                   example_values, difficulty, ihk_relevant, tags, sort_order,
                   is_active, created_at, updated_at
            FROM learning_methods.math_patterns
            WHERE pattern_code = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (pattern_code,))
                row = cur.fetchone()

                if not row:
                    return None

                return MathPattern(
                    pattern_id=row[0],
                    category_id=row[1],
                    pattern_code=row[2],
                    name=row[3],
                    description=row[4],
                    formula_template=row[5],
                    formula_latex=row[6],
                    variables=row[7] or [],
                    steps_template=row[8] or [],
                    example_values=row[9],
                    difficulty=row[10],
                    ihk_relevant=row[11],
                    tags=row[12],
                    sort_order=row[13],
                    is_active=row[14],
                    created_at=row[15],
                    updated_at=row[16]
                )

    @staticmethod
    def find_all_patterns(
        category_id: Optional[str] = None,
        difficulty: Optional[int] = None,
        ihk_relevant: Optional[bool] = None,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[MathPattern]:
        """Find all math patterns with filters."""
        query = """
            SELECT pattern_id, category_id, pattern_code, name, description,
                   formula_template, formula_latex, variables, steps_template,
                   example_values, difficulty, ihk_relevant, tags, sort_order,
                   is_active, created_at, updated_at
            FROM learning_methods.math_patterns
            WHERE 1=1
        """
        params = []

        if category_id:
            query += " AND category_id = %s"
            params.append(category_id)

        if difficulty is not None:
            query += " AND difficulty = %s"
            params.append(difficulty)

        if ihk_relevant is not None:
            query += " AND ihk_relevant = %s"
            params.append(ihk_relevant)

        if active_only:
            query += " AND is_active = TRUE"

        query += " ORDER BY sort_order ASC, name ASC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    MathPattern(
                        pattern_id=row[0],
                        category_id=row[1],
                        pattern_code=row[2],
                        name=row[3],
                        description=row[4],
                        formula_template=row[5],
                        formula_latex=row[6],
                        variables=row[7] or [],
                        steps_template=row[8] or [],
                        example_values=row[9],
                        difficulty=row[10],
                        ihk_relevant=row[11],
                        tags=row[12],
                        sort_order=row[13],
                        is_active=row[14],
                        created_at=row[15],
                        updated_at=row[16]
                    )
                    for row in rows
                ]

    # Note: This file will continue in part 2 due to size constraints.
    # Part 2 will include: Formulas, Sessions, Steps, History, Progress, Tasks, Hints
