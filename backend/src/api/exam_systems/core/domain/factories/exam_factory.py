"""
Exam Systems Domain - Factories

DDD Factory Pattern for creating exam aggregates with business rules validation.

Factories:
- ExamFactory: Create exam templates with validation
- ExamAttemptFactory: Create exam attempts with time limits
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import uuid


class ExamFactory:
    """
    Factory for creating Exam aggregates.
    Enforces business rules for different exam types.
    """

    VALID_EXAM_TYPES = ['ihk', 'practical', 'chapter_completion']

    @staticmethod
    def create_ihk_exam(
        title: str,
        course_id: str,
        chapter_id: Optional[str] = None,
        description: Optional[str] = None,
        time_limit_minutes: int = 60,
        passing_percentage: Decimal = Decimal("50.0")
    ) -> Dict[str, Any]:
        """
        Create an IHK exam template.

        Args:
            title: Exam title
            course_id: UUID of the course
            chapter_id: Optional UUID of the chapter
            description: Optional description
            time_limit_minutes: Time limit in minutes (default: 60)
            passing_percentage: Passing percentage (default: 50)

        Returns:
            Exam data dict ready for repository

        Raises:
            ValueError: If validation fails
        """
        if not title or not course_id:
            raise ValueError("title and course_id are required")

        if time_limit_minutes <= 0:
            raise ValueError("time_limit_minutes must be positive")

        if not 0 <= passing_percentage <= 100:
            raise ValueError("passing_percentage must be between 0 and 100")

        return {
            'exam_type': 'ihk',
            'title': title,
            'description': description or f"IHK-Prüfung: {title}",
            'course_id': course_id,
            'chapter_id': chapter_id,
            'time_limit_minutes': time_limit_minutes,
            'passing_percentage': float(passing_percentage),
            'config': {
                'question_types': ['multiple_choice', 'scenario', 'calculation'],
                'certification_mode': True,
                'allow_partial_credit': False,
                'penalty_for_wrong': False
            },
            'is_active': True
        }

    @staticmethod
    def create_practical_exam(
        title: str,
        course_id: str,
        chapter_id: Optional[str] = None,
        description: Optional[str] = None,
        min_steps: int = 3,
        time_limit_minutes: int = 90,
        passing_percentage: Decimal = Decimal("60.0")
    ) -> Dict[str, Any]:
        """
        Create a Practical exam template.

        Args:
            title: Exam title
            course_id: UUID of the course
            chapter_id: Optional UUID of the chapter
            description: Optional description
            min_steps: Minimum number of practical steps (default: 3)
            time_limit_minutes: Time limit in minutes (default: 90)
            passing_percentage: Passing percentage (default: 60)

        Returns:
            Exam data dict ready for repository

        Raises:
            ValueError: If validation fails
        """
        if not title or not course_id:
            raise ValueError("title and course_id are required")

        if min_steps < 1:
            raise ValueError("min_steps must be at least 1")

        if time_limit_minutes <= 0:
            raise ValueError("time_limit_minutes must be positive")

        if not 0 <= passing_percentage <= 100:
            raise ValueError("passing_percentage must be between 0 and 100")

        return {
            'exam_type': 'practical',
            'title': title,
            'description': description or f"Praxisprüfung: {title}",
            'course_id': course_id,
            'chapter_id': chapter_id,
            'time_limit_minutes': time_limit_minutes,
            'passing_percentage': float(passing_percentage),
            'config': {
                'min_steps': min_steps,
                'partial_grading': True,
                'real_world_simulation': True,
                'allow_step_retry': False
            },
            'is_active': True
        }

    @staticmethod
    def create_chapter_completion_exam(
        title: str,
        course_id: str,
        chapter_id: str,
        description: Optional[str] = None,
        time_limit_minutes: int = 90,
        passing_percentage: Decimal = Decimal("70.0"),
        unlock_next_chapter: bool = True
    ) -> Dict[str, Any]:
        """
        Create a Chapter Completion exam template.

        Args:
            title: Exam title
            course_id: UUID of the course
            chapter_id: UUID of the chapter (REQUIRED)
            description: Optional description
            time_limit_minutes: Time limit in minutes (default: 90)
            passing_percentage: Passing percentage (default: 70)
            unlock_next_chapter: Whether to unlock next chapter on pass

        Returns:
            Exam data dict ready for repository

        Raises:
            ValueError: If validation fails
        """
        if not title or not course_id or not chapter_id:
            raise ValueError("title, course_id, and chapter_id are required for chapter completion exams")

        if time_limit_minutes <= 0:
            raise ValueError("time_limit_minutes must be positive")

        if not 0 <= passing_percentage <= 100:
            raise ValueError("passing_percentage must be between 0 and 100")

        return {
            'exam_type': 'chapter_completion',
            'title': title,
            'description': description or f"Kapitelabschluss: {title}",
            'course_id': course_id,
            'chapter_id': chapter_id,
            'time_limit_minutes': time_limit_minutes,
            'passing_percentage': float(passing_percentage),
            'config': {
                'comprehensive': True,
                'certificate_on_pass': True,
                'unlock_next_chapter': unlock_next_chapter,
                'allow_retry': True,
                'retry_cooldown_hours': 24
            },
            'is_active': True
        }


class ExamAttemptFactory:
    """
    Factory for creating Exam Attempt aggregates.
    Handles time limits and expiration logic.
    """

    @staticmethod
    def create_attempt(
        user_id: str,
        exam_id: str,
        time_limit_minutes: int
    ) -> Dict[str, Any]:
        """
        Create an exam attempt with time limits.

        Args:
            user_id: UUID of the user
            exam_id: UUID of the exam
            time_limit_minutes: Time limit in minutes

        Returns:
            Attempt data dict ready for repository

        Raises:
            ValueError: If validation fails
        """
        if not user_id or not exam_id:
            raise ValueError("user_id and exam_id are required")

        if time_limit_minutes <= 0:
            raise ValueError("time_limit_minutes must be positive")

        started_at = datetime.utcnow()
        expires_at = started_at + timedelta(minutes=time_limit_minutes)

        return {
            'user_id': user_id,
            'exam_id': exam_id,
            'started_at': started_at,
            'expires_at': expires_at
        }


class ExamQuestionFactory:
    """
    Factory for creating Exam Question aggregates.
    Validates question types and structure.
    """

    VALID_QUESTION_TYPES = [
        'multiple_choice',
        'single_choice',
        'scenario',
        'calculation',
        'practical_step',
        'free_text'
    ]

    @staticmethod
    def create_multiple_choice_question(
        exam_id: str,
        question_text: str,
        options: list,
        correct_answers: list,
        points: int = 1,
        explanation: Optional[str] = None,
        order_index: int = 0
    ) -> Dict[str, Any]:
        """
        Create a multiple choice question.

        Args:
            exam_id: UUID of the exam
            question_text: Question text
            options: List of answer options
            correct_answers: List of correct answer indices
            points: Points for this question
            explanation: Optional explanation
            order_index: Order index in exam

        Returns:
            Question data dict ready for repository

        Raises:
            ValueError: If validation fails
        """
        if not exam_id or not question_text:
            raise ValueError("exam_id and question_text are required")

        if not options or len(options) < 2:
            raise ValueError("At least 2 options are required")

        if not correct_answers:
            raise ValueError("At least one correct answer is required")

        # Validate correct_answers indices
        for idx in correct_answers:
            if idx < 0 or idx >= len(options):
                raise ValueError(f"Invalid correct answer index: {idx}")

        return {
            'exam_id': exam_id,
            'question_type': 'multiple_choice',
            'question_text': question_text,
            'points': points,
            'options': options,
            'correct_answer': correct_answers,
            'explanation': explanation,
            'order_index': order_index
        }

    @staticmethod
    def create_scenario_question(
        exam_id: str,
        scenario_text: str,
        question_text: str,
        options: list,
        correct_answer: int,
        points: int = 2,
        explanation: Optional[str] = None,
        order_index: int = 0
    ) -> Dict[str, Any]:
        """
        Create a scenario-based question.

        Args:
            exam_id: UUID of the exam
            scenario_text: Scenario description
            question_text: Question based on scenario
            options: List of answer options
            correct_answer: Index of correct answer
            points: Points for this question
            explanation: Optional explanation
            order_index: Order index in exam

        Returns:
            Question data dict ready for repository
        """
        if not exam_id or not scenario_text or not question_text:
            raise ValueError("exam_id, scenario_text, and question_text are required")

        if not options or len(options) < 2:
            raise ValueError("At least 2 options are required")

        if correct_answer < 0 or correct_answer >= len(options):
            raise ValueError(f"Invalid correct answer index: {correct_answer}")

        full_question = f"**Szenario:**\n{scenario_text}\n\n**Frage:**\n{question_text}"

        return {
            'exam_id': exam_id,
            'question_type': 'scenario',
            'question_text': full_question,
            'points': points,
            'options': options,
            'correct_answer': [correct_answer],
            'explanation': explanation,
            'order_index': order_index
        }
