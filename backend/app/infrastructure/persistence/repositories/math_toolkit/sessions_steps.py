"""
Math Toolkit Repository - Sessions, Steps, Calculator, Hints.

Database queries for session management, calculation steps,
calculator history, and scaffolding hints.
"""

from typing import Dict, List, Optional
import json

from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    execute_query
)


class MathSessionsStepsRepository:
    """Repository for math toolkit sessions, steps, calculator history, and hints."""

    # ─── Sessions ──────────────────────────────────────────────

    @staticmethod
    def insert_session(
        user_id: str,
        session_type: str,
        pattern_id: Optional[str],
        scaffolding_level: int,
        course_id: Optional[str],
        lesson_id: Optional[str]
    ) -> Optional[Dict]:
        """Insert a new toolkit session."""
        query = """
            INSERT INTO math_toolkit_sessions
                (user_id, session_type, pattern_id, scaffolding_level,
                 course_id, lesson_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING session_id
        """
        return fetch_one(query, (
            user_id, session_type, pattern_id, scaffolding_level,
            course_id, lesson_id
        ))

    @staticmethod
    def end_session(session_id: str) -> bool:
        """Set ended_at on an active session."""
        query = """
            UPDATE math_toolkit_sessions
            SET ended_at = NOW()
            WHERE session_id = %s AND ended_at IS NULL
        """
        return execute_query(query, (session_id,))

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        """Get session details with pattern info."""
        query = """
            SELECT
                s.session_id, s.user_id, s.session_type,
                s.scaffolding_level, s.started_at, s.ended_at,
                s.tasks_completed, s.tasks_correct, s.hints_used,
                p.pattern_code, p.name as pattern_name
            FROM math_toolkit_sessions s
            LEFT JOIN math_patterns p ON s.pattern_id = p.pattern_id
            WHERE s.session_id = %s
        """
        return fetch_one(query, (session_id,))

    @staticmethod
    def update_session_stats(
        session_id: str,
        updates: List[str],
        params: list
    ) -> bool:
        """Update session statistics with dynamic SET clause."""
        query = f"""
            UPDATE math_toolkit_sessions
            SET {', '.join(updates)}
            WHERE session_id = %s
        """
        params.append(session_id)
        return execute_query(query, tuple(params))

    # ─── Calculation Steps ─────────────────────────────────────

    @staticmethod
    def insert_calculation_step(
        session_id: str,
        step_number: int,
        input_expression: str,
        input_values_json: str,
        result_value: Optional[float],
        result_display: Optional[str],
        keystrokes_json: str,
        is_correct: Optional[bool],
        expected_value: Optional[float],
        error_type: Optional[str],
        hint_shown: Optional[str]
    ) -> Optional[Dict]:
        """Insert a calculation step record."""
        query = """
            INSERT INTO math_calculation_steps
                (session_id, step_number, input_expression, input_values,
                 result_value, result_display, calculator_keystrokes,
                 is_correct, expected_value, error_type, hint_shown)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING step_id
        """
        return fetch_one(query, (
            session_id, step_number, input_expression,
            input_values_json, result_value, result_display,
            keystrokes_json, is_correct, expected_value,
            error_type, hint_shown
        ))

    @staticmethod
    def get_session_steps(session_id: str) -> List[Dict]:
        """Get all steps in a session ordered by sequence."""
        query = """
            SELECT
                step_id, step_number, input_expression, input_values,
                result_value, result_display, calculator_keystrokes,
                is_correct, expected_value, error_type, hint_shown,
                created_at
            FROM math_calculation_steps
            WHERE session_id = %s
            ORDER BY step_number
        """
        return fetch_all(query, (session_id,)) or []

    # ─── Calculator History ────────────────────────────────────

    @staticmethod
    def insert_calculator_entry(
        user_id: str,
        session_id: Optional[str],
        expression: str,
        result: float,
        result_display: str,
        keystrokes_json: str,
        memory_used: bool,
        memory_value: Optional[float]
    ) -> Optional[Dict]:
        """Insert a calculator history entry."""
        query = """
            INSERT INTO math_calculator_history
                (user_id, session_id, expression, result, result_display,
                 keystrokes, memory_used, memory_value)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING history_id
        """
        return fetch_one(query, (
            user_id, session_id, expression, result, result_display,
            keystrokes_json, memory_used, memory_value
        ))

    @staticmethod
    def get_calculator_history(user_id: str, limit: int = 50) -> List[Dict]:
        """Get calculator history for a user."""
        query = """
            SELECT history_id, expression, result, result_display, keystrokes,
                   memory_used, memory_value, created_at
            FROM math_calculator_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        return fetch_all(query, (user_id, limit)) or []

    # ─── Scaffolding Hints ─────────────────────────────────────

    @staticmethod
    def get_hint(
        pattern_id: str,
        hint_type: str,
        step_number: Optional[int],
        error_type: Optional[str]
    ) -> Optional[Dict]:
        """Get scaffolding hint matching context."""
        query = """
            SELECT hint_level_1, hint_level_2, hint_level_3
            FROM math_scaffolding_hints
            WHERE pattern_id = %s
              AND hint_type = %s
              AND ($3::int IS NULL OR step_number = $3 OR step_number IS NULL)
              AND ($4::text IS NULL OR error_type = $4 OR error_type IS NULL)
              AND is_active = TRUE
            ORDER BY
                CASE WHEN step_number = $3 THEN 0 ELSE 1 END,
                CASE WHEN error_type = $4 THEN 0 ELSE 1 END
            LIMIT 1
        """
        return fetch_one(
            query, (pattern_id, hint_type, step_number, error_type)
        )
