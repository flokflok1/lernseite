"""
Pattern recognition tasks module.

Handles pattern recognition exercises and answer validation.
"""

from typing import Dict, Any, List, Optional
import logging

from app.infrastructure.persistence.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class TaskManager:
    """Manages pattern recognition tasks."""

    @staticmethod
    def get_pattern_tasks(
        pattern_id: str = None,
        task_type: str = None,
        difficulty: int = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Retrieve pattern recognition tasks.

        Args:
            pattern_id: Optional pattern filter
            task_type: Optional task type filter
            difficulty: Optional difficulty filter
            limit: Maximum tasks to return

        Returns:
            List of task dictionaries
        """
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
        return BaseRepository.fetch_all(
            query, (pattern_id, task_type, difficulty, limit)
        ) or []

    @staticmethod
    def check_pattern_task_answer(task_id: str, user_answer: Any) -> Dict:
        """
        Check answer for pattern recognition task.

        Args:
            task_id: Task identifier
            user_answer: User's answer

        Returns:
            Dict with validation result and feedback
        """
        query = """
            SELECT task_type, solution
            FROM math_pattern_recognition_tasks
            WHERE task_id = %s
        """
        task = BaseRepository.fetch_one(query, (task_id,))

        if not task:
            return {'success': False, 'error': 'Aufgabe nicht gefunden'}

        solution = task['solution']
        is_correct = TaskManager._validate_answer(
            user_answer, solution, task['task_type']
        )

        return {
            'success': True,
            'is_correct': is_correct,
            'solution': solution if not is_correct else None,
            'feedback': solution.get(
                'feedback',
                'Richtig!' if is_correct else 'Leider falsch.'
            )
        }

    @staticmethod
    def _validate_answer(
        user_answer: Any,
        solution: Dict,
        task_type: str
    ) -> bool:
        """
        Validate user answer based on task type.

        Args:
            user_answer: User's submitted answer
            solution: Expected solution dictionary
            task_type: Type of task

        Returns:
            Whether answer is correct
        """
        try:
            if task_type == 'identify_pattern':
                return (str(user_answer).lower() ==
                        str(solution.get('pattern_code', '')).lower())

            elif task_type == 'order_steps':
                return user_answer == solution.get('correct_order', [])

            elif task_type == 'fill_formula':
                return (str(user_answer).strip() ==
                        str(solution.get('answer', '')).strip())

            elif task_type == 'match_values':
                return user_answer == solution.get('matches', {})

            elif task_type == 'spot_error':
                return user_answer == solution.get('error_position')

            elif task_type == 'complete_calculation':
                return abs(float(user_answer) - float(
                    solution.get('result', 0)
                )) < 0.01

            return False

        except (ValueError, TypeError):
            return False
