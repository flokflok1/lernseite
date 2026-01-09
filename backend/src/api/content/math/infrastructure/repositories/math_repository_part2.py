"""
Math Repository Part 2 (Infrastructure Layer - Continuation)

Continuation of math repository for remaining tables:
- math_formulas
- math_toolkit_sessions
- math_calculation_steps
- math_calculator_history
- math_user_progress
- math_pattern_recognition_tasks
- math_scaffolding_hints
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
import json
from datetime import datetime
from src.core.database import get_db_connection
from src.api.content.math.domain.entities.math_formula import MathFormula
from src.api.content.math.domain.entities.math_toolkit_session import MathToolkitSession
from src.api.content.math.domain.entities.math_calculation_step import MathCalculationStep
from src.api.content.math.domain.entities.math_calculator_history import MathCalculatorHistory
from src.api.content.math.domain.entities.math_user_progress import MathUserProgress
from src.api.content.math.domain.entities.math_pattern_recognition_task import MathPatternRecognitionTask
from src.api.content.math.domain.entities.math_scaffolding_hint import MathScaffoldingHint


class MathRepositoryPart2:
    """
    Math Repository Part 2 - Formulas, Sessions, Progress, Tasks, Hints.
    """

    # ============================================================================
    # MATH FORMULAS
    # ============================================================================

    @staticmethod
    def find_formula_by_id(formula_id: str) -> Optional[MathFormula]:
        """Find math formula by ID."""
        query = """
            SELECT formula_id, category_id, pattern_id, name, description,
                   formula_text, formula_latex, formula_display, variables,
                   example_input, example_output, tags, is_favorite, usage_count,
                   sort_order, is_active, created_at
            FROM learning_methods.math_formulas
            WHERE formula_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (formula_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return MathFormula(
                    formula_id=row[0],
                    category_id=row[1],
                    pattern_id=row[2],
                    name=row[3],
                    description=row[4],
                    formula_text=row[5],
                    formula_latex=row[6],
                    formula_display=row[7],
                    variables=row[8],
                    example_input=row[9],
                    example_output=row[10],
                    tags=row[11],
                    is_favorite=row[12],
                    usage_count=row[13],
                    sort_order=row[14],
                    is_active=row[15],
                    created_at=row[16]
                )

    @staticmethod
    def find_all_formulas(
        category_id: Optional[str] = None,
        pattern_id: Optional[str] = None,
        favorites_only: bool = False,
        active_only: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[MathFormula]:
        """Find all math formulas with filters."""
        query = """
            SELECT formula_id, category_id, pattern_id, name, description,
                   formula_text, formula_latex, formula_display, variables,
                   example_input, example_output, tags, is_favorite, usage_count,
                   sort_order, is_active, created_at
            FROM learning_methods.math_formulas
            WHERE 1=1
        """
        params = []

        if category_id:
            query += " AND category_id = %s"
            params.append(category_id)

        if pattern_id:
            query += " AND pattern_id = %s"
            params.append(pattern_id)

        if favorites_only:
            query += " AND is_favorite = TRUE"

        if active_only:
            query += " AND is_active = TRUE"

        query += " ORDER BY sort_order ASC, usage_count DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    MathFormula(
                        formula_id=row[0],
                        category_id=row[1],
                        pattern_id=row[2],
                        name=row[3],
                        description=row[4],
                        formula_text=row[5],
                        formula_latex=row[6],
                        formula_display=row[7],
                        variables=row[8],
                        example_input=row[9],
                        example_output=row[10],
                        tags=row[11],
                        is_favorite=row[12],
                        usage_count=row[13],
                        sort_order=row[14],
                        is_active=row[15],
                        created_at=row[16]
                    )
                    for row in rows
                ]

    # ============================================================================
    # MATH TOOLKIT SESSIONS
    # ============================================================================

    @staticmethod
    def find_session_by_id(session_id: str) -> Optional[MathToolkitSession]:
        """Find math toolkit session by ID."""
        query = """
            SELECT session_id, user_id, course_id, lesson_id, learning_method_id,
                   session_type, pattern_id, scaffolding_level, started_at, ended_at,
                   tasks_completed, tasks_correct, hints_used
            FROM learning_methods.math_toolkit_sessions
            WHERE session_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (session_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return MathToolkitSession(
                    session_id=row[0],
                    user_id=row[1],
                    course_id=row[2],
                    lesson_id=row[3],
                    learning_method_id=row[4],
                    session_type=row[5],
                    pattern_id=row[6],
                    scaffolding_level=row[7],
                    started_at=row[8],
                    ended_at=row[9],
                    tasks_completed=row[10],
                    tasks_correct=row[11],
                    hints_used=row[12]
                )

    @staticmethod
    def find_sessions_by_user(
        user_id: str,
        active_only: bool = False,
        limit: int = 50
    ) -> List[MathToolkitSession]:
        """Find math toolkit sessions by user."""
        query = """
            SELECT session_id, user_id, course_id, lesson_id, learning_method_id,
                   session_type, pattern_id, scaffolding_level, started_at, ended_at,
                   tasks_completed, tasks_correct, hints_used
            FROM learning_methods.math_toolkit_sessions
            WHERE user_id = %s
        """
        params = [user_id]

        if active_only:
            query += " AND ended_at IS NULL"

        query += " ORDER BY started_at DESC LIMIT %s"
        params.append(limit)

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    MathToolkitSession(
                        session_id=row[0],
                        user_id=row[1],
                        course_id=row[2],
                        lesson_id=row[3],
                        learning_method_id=row[4],
                        session_type=row[5],
                        pattern_id=row[6],
                        scaffolding_level=row[7],
                        started_at=row[8],
                        ended_at=row[9],
                        tasks_completed=row[10],
                        tasks_correct=row[11],
                        hints_used=row[12]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_session(session: MathToolkitSession) -> MathToolkitSession:
        """Create new math toolkit session."""
        query = """
            INSERT INTO learning_methods.math_toolkit_sessions
            (session_id, user_id, course_id, lesson_id, learning_method_id,
             session_type, pattern_id, scaffolding_level, started_at, ended_at,
             tasks_completed, tasks_correct, hints_used)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING session_id, user_id, course_id, lesson_id, learning_method_id,
                      session_type, pattern_id, scaffolding_level, started_at, ended_at,
                      tasks_completed, tasks_correct, hints_used
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    session.session_id,
                    session.user_id,
                    session.course_id,
                    session.lesson_id,
                    session.learning_method_id,
                    session.session_type,
                    session.pattern_id,
                    session.scaffolding_level,
                    session.started_at or datetime.utcnow(),
                    session.ended_at,
                    session.tasks_completed,
                    session.tasks_correct,
                    session.hints_used
                ))

                row = cur.fetchone()
                conn.commit()

                return MathToolkitSession(
                    session_id=row[0],
                    user_id=row[1],
                    course_id=row[2],
                    lesson_id=row[3],
                    learning_method_id=row[4],
                    session_type=row[5],
                    pattern_id=row[6],
                    scaffolding_level=row[7],
                    started_at=row[8],
                    ended_at=row[9],
                    tasks_completed=row[10],
                    tasks_correct=row[11],
                    hints_used=row[12]
                )

    @staticmethod
    def update_session(session: MathToolkitSession) -> MathToolkitSession:
        """Update math toolkit session."""
        query = """
            UPDATE learning_methods.math_toolkit_sessions
            SET scaffolding_level = %s,
                ended_at = %s,
                tasks_completed = %s,
                tasks_correct = %s,
                hints_used = %s
            WHERE session_id = %s
            RETURNING session_id, user_id, course_id, lesson_id, learning_method_id,
                      session_type, pattern_id, scaffolding_level, started_at, ended_at,
                      tasks_completed, tasks_correct, hints_used
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    session.scaffolding_level,
                    session.ended_at,
                    session.tasks_completed,
                    session.tasks_correct,
                    session.hints_used,
                    session.session_id
                ))

                row = cur.fetchone()
                conn.commit()

                return MathToolkitSession(
                    session_id=row[0],
                    user_id=row[1],
                    course_id=row[2],
                    lesson_id=row[3],
                    learning_method_id=row[4],
                    session_type=row[5],
                    pattern_id=row[6],
                    scaffolding_level=row[7],
                    started_at=row[8],
                    ended_at=row[9],
                    tasks_completed=row[10],
                    tasks_correct=row[11],
                    hints_used=row[12]
                )

    # ============================================================================
    # MATH USER PROGRESS
    # ============================================================================

    @staticmethod
    def find_progress_by_user_and_pattern(
        user_id: str,
        pattern_id: str
    ) -> Optional[MathUserProgress]:
        """Find math user progress by user and pattern."""
        query = """
            SELECT progress_id, user_id, pattern_id, current_level, total_attempts,
                   correct_attempts, mastery_score, current_streak, best_streak,
                   last_practiced_at, next_review_at, created_at, updated_at
            FROM learning_methods.math_user_progress
            WHERE user_id = %s AND pattern_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id, pattern_id))
                row = cur.fetchone()

                if not row:
                    return None

                return MathUserProgress(
                    progress_id=row[0],
                    user_id=row[1],
                    pattern_id=row[2],
                    current_level=row[3],
                    total_attempts=row[4],
                    correct_attempts=row[5],
                    mastery_score=row[6],
                    current_streak=row[7],
                    best_streak=row[8],
                    last_practiced_at=row[9],
                    next_review_at=row[10],
                    created_at=row[11],
                    updated_at=row[12]
                )

    @staticmethod
    def find_all_progress_by_user(user_id: str) -> List[MathUserProgress]:
        """Find all math user progress for a user."""
        query = """
            SELECT progress_id, user_id, pattern_id, current_level, total_attempts,
                   correct_attempts, mastery_score, current_streak, best_streak,
                   last_practiced_at, next_review_at, created_at, updated_at
            FROM learning_methods.math_user_progress
            WHERE user_id = %s
            ORDER BY last_practiced_at DESC NULLS LAST
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                rows = cur.fetchall()

                return [
                    MathUserProgress(
                        progress_id=row[0],
                        user_id=row[1],
                        pattern_id=row[2],
                        current_level=row[3],
                        total_attempts=row[4],
                        correct_attempts=row[5],
                        mastery_score=row[6],
                        current_streak=row[7],
                        best_streak=row[8],
                        last_practiced_at=row[9],
                        next_review_at=row[10],
                        created_at=row[11],
                        updated_at=row[12]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_progress(progress: MathUserProgress) -> MathUserProgress:
        """Create new math user progress."""
        query = """
            INSERT INTO learning_methods.math_user_progress
            (progress_id, user_id, pattern_id, current_level, total_attempts,
             correct_attempts, mastery_score, current_streak, best_streak,
             last_practiced_at, next_review_at, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING progress_id, user_id, pattern_id, current_level, total_attempts,
                      correct_attempts, mastery_score, current_streak, best_streak,
                      last_practiced_at, next_review_at, created_at, updated_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    progress.progress_id,
                    progress.user_id,
                    progress.pattern_id,
                    progress.current_level,
                    progress.total_attempts,
                    progress.correct_attempts,
                    progress.mastery_score,
                    progress.current_streak,
                    progress.best_streak,
                    progress.last_practiced_at,
                    progress.next_review_at,
                    progress.created_at or datetime.utcnow(),
                    progress.updated_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return MathUserProgress(
                    progress_id=row[0],
                    user_id=row[1],
                    pattern_id=row[2],
                    current_level=row[3],
                    total_attempts=row[4],
                    correct_attempts=row[5],
                    mastery_score=row[6],
                    current_streak=row[7],
                    best_streak=row[8],
                    last_practiced_at=row[9],
                    next_review_at=row[10],
                    created_at=row[11],
                    updated_at=row[12]
                )

    @staticmethod
    def update_progress(progress: MathUserProgress) -> MathUserProgress:
        """Update math user progress."""
        query = """
            UPDATE learning_methods.math_user_progress
            SET current_level = %s,
                total_attempts = %s,
                correct_attempts = %s,
                mastery_score = %s,
                current_streak = %s,
                best_streak = %s,
                last_practiced_at = %s,
                next_review_at = %s,
                updated_at = %s
            WHERE progress_id = %s
            RETURNING progress_id, user_id, pattern_id, current_level, total_attempts,
                      correct_attempts, mastery_score, current_streak, best_streak,
                      last_practiced_at, next_review_at, created_at, updated_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    progress.current_level,
                    progress.total_attempts,
                    progress.correct_attempts,
                    progress.mastery_score,
                    progress.current_streak,
                    progress.best_streak,
                    progress.last_practiced_at,
                    progress.next_review_at,
                    datetime.utcnow(),
                    progress.progress_id
                ))

                row = cur.fetchone()
                conn.commit()

                return MathUserProgress(
                    progress_id=row[0],
                    user_id=row[1],
                    pattern_id=row[2],
                    current_level=row[3],
                    total_attempts=row[4],
                    correct_attempts=row[5],
                    mastery_score=row[6],
                    current_streak=row[7],
                    best_streak=row[8],
                    last_practiced_at=row[9],
                    next_review_at=row[10],
                    created_at=row[11],
                    updated_at=row[12]
                )
