"""
Math Repository Part 3 (Infrastructure Layer - Final Part)

Remaining tables:
- math_calculation_steps
- math_calculator_history
- math_pattern_recognition_tasks
- math_scaffolding_hints
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
import json
from datetime import datetime
from src.core.database import get_db_connection
from src.api.content.math.domain.entities.math_calculation_step import MathCalculationStep
from src.api.content.math.domain.entities.math_calculator_history import MathCalculatorHistory
from src.api.content.math.domain.entities.math_pattern_recognition_task import MathPatternRecognitionTask
from src.api.content.math.domain.entities.math_scaffolding_hint import MathScaffoldingHint


class MathRepositoryPart3:
    """
    Math Repository Part 3 - Calculation Steps, Calculator History, Recognition Tasks, Scaffolding Hints.
    """

    # ============================================================================
    # MATH CALCULATION STEPS
    # ============================================================================

    @staticmethod
    def find_step_by_id(step_id: str) -> Optional[MathCalculationStep]:
        """Find math calculation step by ID."""
        query = """
            SELECT step_id, session_id, step_number, input_expression, input_values,
                   result_value, result_display, calculator_keystrokes, is_correct,
                   expected_value, error_type, hint_shown, created_at
            FROM learning_methods.math_calculation_steps
            WHERE step_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (step_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return MathCalculationStep(
                    step_id=row[0],
                    session_id=row[1],
                    step_number=row[2],
                    input_expression=row[3],
                    input_values=row[4],
                    result_value=row[5],
                    result_display=row[6],
                    calculator_keystrokes=row[7],
                    is_correct=row[8],
                    expected_value=row[9],
                    error_type=row[10],
                    hint_shown=row[11],
                    created_at=row[12]
                )

    @staticmethod
    def find_steps_by_session(session_id: str) -> List[MathCalculationStep]:
        """Find all math calculation steps for a session."""
        query = """
            SELECT step_id, session_id, step_number, input_expression, input_values,
                   result_value, result_display, calculator_keystrokes, is_correct,
                   expected_value, error_type, hint_shown, created_at
            FROM learning_methods.math_calculation_steps
            WHERE session_id = %s
            ORDER BY step_number ASC
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (session_id,))
                rows = cur.fetchall()

                return [
                    MathCalculationStep(
                        step_id=row[0],
                        session_id=row[1],
                        step_number=row[2],
                        input_expression=row[3],
                        input_values=row[4],
                        result_value=row[5],
                        result_display=row[6],
                        calculator_keystrokes=row[7],
                        is_correct=row[8],
                        expected_value=row[9],
                        error_type=row[10],
                        hint_shown=row[11],
                        created_at=row[12]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_step(step: MathCalculationStep) -> MathCalculationStep:
        """Create new math calculation step."""
        query = """
            INSERT INTO learning_methods.math_calculation_steps
            (step_id, session_id, step_number, input_expression, input_values,
             result_value, result_display, calculator_keystrokes, is_correct,
             expected_value, error_type, hint_shown, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING step_id, session_id, step_number, input_expression, input_values,
                      result_value, result_display, calculator_keystrokes, is_correct,
                      expected_value, error_type, hint_shown, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    step.step_id,
                    step.session_id,
                    step.step_number,
                    step.input_expression,
                    json.dumps(step.input_values) if step.input_values else None,
                    step.result_value,
                    step.result_display,
                    json.dumps(step.calculator_keystrokes) if step.calculator_keystrokes else None,
                    step.is_correct,
                    step.expected_value,
                    step.error_type,
                    step.hint_shown,
                    step.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return MathCalculationStep(
                    step_id=row[0],
                    session_id=row[1],
                    step_number=row[2],
                    input_expression=row[3],
                    input_values=row[4],
                    result_value=row[5],
                    result_display=row[6],
                    calculator_keystrokes=row[7],
                    is_correct=row[8],
                    expected_value=row[9],
                    error_type=row[10],
                    hint_shown=row[11],
                    created_at=row[12]
                )

    # ============================================================================
    # MATH CALCULATOR HISTORY
    # ============================================================================

    @staticmethod
    def find_history_by_id(history_id: str) -> Optional[MathCalculatorHistory]:
        """Find math calculator history by ID."""
        query = """
            SELECT history_id, session_id, user_id, expression, result,
                   result_display, keystrokes, memory_used, memory_value, created_at
            FROM learning_methods.math_calculator_history
            WHERE history_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (history_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return MathCalculatorHistory(
                    history_id=row[0],
                    session_id=row[1],
                    user_id=row[2],
                    expression=row[3],
                    result=row[4],
                    result_display=row[5],
                    keystrokes=row[6],
                    memory_used=row[7],
                    memory_value=row[8],
                    created_at=row[9]
                )

    @staticmethod
    def find_history_by_user(
        user_id: str,
        limit: int = 50
    ) -> List[MathCalculatorHistory]:
        """Find math calculator history for a user."""
        query = """
            SELECT history_id, session_id, user_id, expression, result,
                   result_display, keystrokes, memory_used, memory_value, created_at
            FROM learning_methods.math_calculator_history
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id, limit))
                rows = cur.fetchall()

                return [
                    MathCalculatorHistory(
                        history_id=row[0],
                        session_id=row[1],
                        user_id=row[2],
                        expression=row[3],
                        result=row[4],
                        result_display=row[5],
                        keystrokes=row[6],
                        memory_used=row[7],
                        memory_value=row[8],
                        created_at=row[9]
                    )
                    for row in rows
                ]

    @staticmethod
    def find_history_by_session(session_id: str) -> List[MathCalculatorHistory]:
        """Find math calculator history for a session."""
        query = """
            SELECT history_id, session_id, user_id, expression, result,
                   result_display, keystrokes, memory_used, memory_value, created_at
            FROM learning_methods.math_calculator_history
            WHERE session_id = %s
            ORDER BY created_at ASC
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (session_id,))
                rows = cur.fetchall()

                return [
                    MathCalculatorHistory(
                        history_id=row[0],
                        session_id=row[1],
                        user_id=row[2],
                        expression=row[3],
                        result=row[4],
                        result_display=row[5],
                        keystrokes=row[6],
                        memory_used=row[7],
                        memory_value=row[8],
                        created_at=row[9]
                    )
                    for row in rows
                ]

    @staticmethod
    def create_history(history: MathCalculatorHistory) -> MathCalculatorHistory:
        """Create new math calculator history entry."""
        query = """
            INSERT INTO learning_methods.math_calculator_history
            (history_id, session_id, user_id, expression, result,
             result_display, keystrokes, memory_used, memory_value, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING history_id, session_id, user_id, expression, result,
                      result_display, keystrokes, memory_used, memory_value, created_at
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (
                    history.history_id,
                    history.session_id,
                    history.user_id,
                    history.expression,
                    history.result,
                    history.result_display,
                    json.dumps(history.keystrokes) if history.keystrokes else None,
                    history.memory_used,
                    history.memory_value,
                    history.created_at or datetime.utcnow()
                ))

                row = cur.fetchone()
                conn.commit()

                return MathCalculatorHistory(
                    history_id=row[0],
                    session_id=row[1],
                    user_id=row[2],
                    expression=row[3],
                    result=row[4],
                    result_display=row[5],
                    keystrokes=row[6],
                    memory_used=row[7],
                    memory_value=row[8],
                    created_at=row[9]
                )

    # ============================================================================
    # MATH PATTERN RECOGNITION TASKS
    # ============================================================================

    @staticmethod
    def find_task_by_id(task_id: str) -> Optional[MathPatternRecognitionTask]:
        """Find math pattern recognition task by ID."""
        query = """
            SELECT task_id, pattern_id, task_type, task_text, task_data,
                   solution, difficulty, is_active, created_at
            FROM learning_methods.math_pattern_recognition_tasks
            WHERE task_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (task_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return MathPatternRecognitionTask(
                    task_id=row[0],
                    pattern_id=row[1],
                    task_type=row[2],
                    task_text=row[3],
                    task_data=row[4],
                    solution=row[5],
                    difficulty=row[6],
                    is_active=row[7],
                    created_at=row[8]
                )

    @staticmethod
    def find_tasks_by_pattern(
        pattern_id: str,
        task_type: Optional[str] = None,
        difficulty: Optional[int] = None,
        active_only: bool = True
    ) -> List[MathPatternRecognitionTask]:
        """Find math pattern recognition tasks for a pattern."""
        query = """
            SELECT task_id, pattern_id, task_type, task_text, task_data,
                   solution, difficulty, is_active, created_at
            FROM learning_methods.math_pattern_recognition_tasks
            WHERE pattern_id = %s
        """
        params = [pattern_id]

        if task_type:
            query += " AND task_type = %s"
            params.append(task_type)

        if difficulty is not None:
            query += " AND difficulty = %s"
            params.append(difficulty)

        if active_only:
            query += " AND is_active = TRUE"

        query += " ORDER BY difficulty ASC, created_at ASC"

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    MathPatternRecognitionTask(
                        task_id=row[0],
                        pattern_id=row[1],
                        task_type=row[2],
                        task_text=row[3],
                        task_data=row[4],
                        solution=row[5],
                        difficulty=row[6],
                        is_active=row[7],
                        created_at=row[8]
                    )
                    for row in rows
                ]

    # ============================================================================
    # MATH SCAFFOLDING HINTS
    # ============================================================================

    @staticmethod
    def find_hint_by_id(hint_id: str) -> Optional[MathScaffoldingHint]:
        """Find math scaffolding hint by ID."""
        query = """
            SELECT hint_id, pattern_id, hint_type, step_number, error_type,
                   hint_level_1, hint_level_2, hint_level_3, trigger_condition,
                   sort_order, is_active, created_at
            FROM learning_methods.math_scaffolding_hints
            WHERE hint_id = %s
        """

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (hint_id,))
                row = cur.fetchone()

                if not row:
                    return None

                return MathScaffoldingHint(
                    hint_id=row[0],
                    pattern_id=row[1],
                    hint_type=row[2],
                    step_number=row[3],
                    error_type=row[4],
                    hint_level_1=row[5],
                    hint_level_2=row[6],
                    hint_level_3=row[7],
                    trigger_condition=row[8],
                    sort_order=row[9],
                    is_active=row[10],
                    created_at=row[11]
                )

    @staticmethod
    def find_hints_by_pattern(
        pattern_id: str,
        hint_type: Optional[str] = None,
        step_number: Optional[int] = None,
        active_only: bool = True
    ) -> List[MathScaffoldingHint]:
        """Find math scaffolding hints for a pattern."""
        query = """
            SELECT hint_id, pattern_id, hint_type, step_number, error_type,
                   hint_level_1, hint_level_2, hint_level_3, trigger_condition,
                   sort_order, is_active, created_at
            FROM learning_methods.math_scaffolding_hints
            WHERE pattern_id = %s
        """
        params = [pattern_id]

        if hint_type:
            query += " AND hint_type = %s"
            params.append(hint_type)

        if step_number is not None:
            query += " AND step_number = %s"
            params.append(step_number)

        if active_only:
            query += " AND is_active = TRUE"

        query += " ORDER BY sort_order ASC, hint_type ASC"

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    MathScaffoldingHint(
                        hint_id=row[0],
                        pattern_id=row[1],
                        hint_type=row[2],
                        step_number=row[3],
                        error_type=row[4],
                        hint_level_1=row[5],
                        hint_level_2=row[6],
                        hint_level_3=row[7],
                        trigger_condition=row[8],
                        sort_order=row[9],
                        is_active=row[10],
                        created_at=row[11]
                    )
                    for row in rows
                ]

    @staticmethod
    def find_hints_by_error_type(
        pattern_id: str,
        error_type: str,
        active_only: bool = True
    ) -> List[MathScaffoldingHint]:
        """Find math scaffolding hints for a specific error type."""
        query = """
            SELECT hint_id, pattern_id, hint_type, step_number, error_type,
                   hint_level_1, hint_level_2, hint_level_3, trigger_condition,
                   sort_order, is_active, created_at
            FROM learning_methods.math_scaffolding_hints
            WHERE pattern_id = %s AND error_type = %s
        """
        params = [pattern_id, error_type]

        if active_only:
            query += " AND is_active = TRUE"

        query += " ORDER BY sort_order ASC"

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()

                return [
                    MathScaffoldingHint(
                        hint_id=row[0],
                        pattern_id=row[1],
                        hint_type=row[2],
                        step_number=row[3],
                        error_type=row[4],
                        hint_level_1=row[5],
                        hint_level_2=row[6],
                        hint_level_3=row[7],
                        trigger_condition=row[8],
                        sort_order=row[9],
                        is_active=row[10],
                        created_at=row[11]
                    )
                    for row in rows
                ]
