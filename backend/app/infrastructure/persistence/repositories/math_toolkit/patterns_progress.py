"""
Math Toolkit Repository - Patterns, Formulas, Progress, Tasks.

Database queries for pattern/formula management, user progress tracking,
and pattern recognition tasks.
"""

from typing import Any, Dict, List, Optional

from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    execute_query
)


class MathPatternsProgressRepository:
    """Repository for math patterns, formulas, progress, and tasks."""

    # ─── Categories ────────────────────────────────────────────

    @staticmethod
    def get_categories(active_only: bool = True) -> List[Dict]:
        """Get all pattern categories."""
        query = """
            SELECT category_id, category_code, name, description, icon, color, sort_order
            FROM math_pattern_categories
            WHERE ($1 = FALSE OR is_active = TRUE)
            ORDER BY sort_order, name
        """
        return fetch_all(query, (active_only,)) or []

    @staticmethod
    def get_category_by_code(code: str) -> Optional[Dict]:
        """Get category by code."""
        query = """
            SELECT category_id, category_code, name, description, icon, color
            FROM math_pattern_categories
            WHERE category_code = %s AND is_active = TRUE
        """
        return fetch_one(query, (code,))

    # ─── Patterns ──────────────────────────────────────────────

    @staticmethod
    def get_patterns(
        active_only: bool,
        category_code: Optional[str],
        ihk_only: bool,
        difficulty: Optional[int]
    ) -> List[Dict]:
        """Get patterns with optional filters."""
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
        return fetch_all(
            query, (active_only, category_code, ihk_only, difficulty)
        ) or []

    @staticmethod
    def get_pattern_by_id(pattern_id: str) -> Optional[Dict]:
        """Get pattern by ID with category info."""
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
        return fetch_one(query, (pattern_id,))

    @staticmethod
    def get_pattern_by_code(pattern_code: str) -> Optional[Dict]:
        """Get active pattern by code."""
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
        return fetch_one(query, (pattern_code,))

    @staticmethod
    def insert_pattern(
        pattern_code: str,
        name: str,
        category_id: str,
        description: Optional[str],
        formula_template: str,
        formula_latex: Optional[str],
        variables_json: str,
        steps_template_json: str,
        example_values_json: str,
        difficulty: int,
        ihk_relevant: bool,
        tags_json: str
    ) -> Optional[Dict]:
        """Insert a new pattern."""
        query = """
            INSERT INTO math_patterns
                (pattern_code, name, category_id, description,
                 formula_template, formula_latex, variables, steps_template,
                 example_values, difficulty, ihk_relevant, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING pattern_id
        """
        return fetch_one(query, (
            pattern_code, name, category_id, description,
            formula_template, formula_latex, variables_json,
            steps_template_json, example_values_json,
            difficulty, ihk_relevant, tags_json
        ))

    # ─── Formulas ──────────────────────────────────────────────

    @staticmethod
    def get_formulas(
        category_code: Optional[str],
        favorites_only: bool
    ) -> List[Dict]:
        """Get formulas with optional filters."""
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
        return fetch_all(query, (category_code, favorites_only)) or []

    @staticmethod
    def increment_formula_usage(formula_id: str) -> bool:
        """Increment usage counter for a formula."""
        query = """
            UPDATE math_formulas
            SET usage_count = usage_count + 1
            WHERE formula_id = %s
        """
        return execute_query(query, (formula_id,))

    @staticmethod
    def toggle_formula_favorite(formula_id: str) -> Optional[Dict]:
        """Toggle favorite status, returning new value."""
        query = """
            UPDATE math_formulas
            SET is_favorite = NOT is_favorite
            WHERE formula_id = %s
            RETURNING is_favorite
        """
        return fetch_one(query, (formula_id,))

    @staticmethod
    def insert_formula(
        name: str,
        formula_text: str,
        category_id: Optional[str],
        description: Optional[str],
        formula_latex: Optional[str],
        formula_display: Optional[str],
        variables_json: str,
        example_input_json: str,
        example_output: Optional[str],
        tags_json: str
    ) -> Optional[Dict]:
        """Insert a new formula."""
        query = """
            INSERT INTO math_formulas
                (name, formula_text, category_id, description,
                 formula_latex, formula_display, variables,
                 example_input, example_output, tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING formula_id
        """
        return fetch_one(query, (
            name, formula_text, category_id, description,
            formula_latex, formula_display, variables_json,
            example_input_json, example_output, tags_json
        ))

    # ─── User Progress ─────────────────────────────────────────

    @staticmethod
    def get_user_progress(
        user_id: str,
        pattern_id: Optional[str]
    ) -> List[Dict]:
        """Get user progress, optionally filtered by pattern."""
        query = """
            SELECT
                up.progress_id, up.current_level, up.total_attempts,
                up.correct_attempts, up.mastery_score,
                up.current_streak, up.best_streak,
                up.last_practiced_at, up.next_review_at,
                p.pattern_code, p.name as pattern_name,
                c.category_code, c.name as category_name
            FROM math_user_progress up
            JOIN math_patterns p ON up.pattern_id = p.pattern_id
            LEFT JOIN math_pattern_categories c ON p.category_id = c.category_id
            WHERE up.user_id = %s
              AND ($2::uuid IS NULL OR up.pattern_id = $2)
            ORDER BY up.mastery_score DESC, up.last_practiced_at DESC
        """
        return fetch_all(query, (user_id, pattern_id)) or []

    @staticmethod
    def get_progress_record(user_id: str, pattern_id: str) -> Optional[Dict]:
        """Get a single progress record for user+pattern."""
        query = """
            SELECT progress_id, current_level, total_attempts, correct_attempts,
                   mastery_score, current_streak, best_streak
            FROM math_user_progress
            WHERE user_id = %s AND pattern_id = %s
        """
        return fetch_one(query, (user_id, pattern_id))

    @staticmethod
    def insert_progress_record(
        user_id: str, pattern_id: str
    ) -> Optional[Dict]:
        """Create a new progress record with defaults."""
        query = """
            INSERT INTO math_user_progress (user_id, pattern_id)
            VALUES (%s, %s)
            RETURNING progress_id, current_level, total_attempts,
                      correct_attempts, mastery_score, current_streak,
                      best_streak
        """
        return fetch_one(query, (user_id, pattern_id))

    @staticmethod
    def update_progress(
        user_id: str,
        pattern_id: str,
        new_level: int,
        total: int,
        correct: int,
        mastery: float,
        streak: int,
        best_streak: int,
        review_days: int
    ) -> bool:
        """Update progress metrics after an attempt."""
        query = """
            UPDATE math_user_progress
            SET current_level = %s,
                total_attempts = %s,
                correct_attempts = %s,
                mastery_score = %s,
                current_streak = %s,
                best_streak = %s,
                last_practiced_at = NOW(),
                next_review_at = NOW() + INTERVAL '1 day' * %s
            WHERE user_id = %s AND pattern_id = %s
        """
        return execute_query(query, (
            new_level, total, correct, mastery, streak, best_streak,
            review_days, user_id, pattern_id
        ))

    # ─── Pattern Recognition Tasks ─────────────────────────────

    @staticmethod
    def get_pattern_tasks(
        pattern_id: Optional[str],
        task_type: Optional[str],
        difficulty: Optional[int],
        limit: int
    ) -> List[Dict]:
        """Get pattern recognition tasks with filters."""
        query = """
            SELECT
                t.task_id, t.task_type, t.task_text, t.task_data,
                t.solution, t.difficulty,
                p.pattern_code, p.name as pattern_name
            FROM math_pattern_recognition_tasks t
            JOIN math_patterns p ON t.pattern_id = p.pattern_id
            WHERE t.is_active = TRUE
              AND ($1::uuid IS NULL OR t.pattern_id = $1)
              AND ($2::text IS NULL OR t.task_type = $2)
              AND ($3::int IS NULL OR t.difficulty = $3)
            ORDER BY RANDOM()
            LIMIT %s
        """
        return fetch_all(
            query, (pattern_id, task_type, difficulty, limit)
        ) or []

    @staticmethod
    def get_task_solution(task_id: str) -> Optional[Dict]:
        """Get task type and solution for answer validation."""
        query = """
            SELECT task_type, solution
            FROM math_pattern_recognition_tasks
            WHERE task_id = %s
        """
        return fetch_one(query, (task_id,))
