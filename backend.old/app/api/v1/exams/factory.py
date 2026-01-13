"""
Exam Domain Factory.

Factory pattern for creating exam domain objects following DDD principles.
Implements Domain-Driven Design (DDD) Factory Pattern.
"""

import json
from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime

from .value_objects import (
    ExamType, QuestionType, ExamStatus, AttemptStatus,
    Difficulty, ExamMode, ExamConfig, ExamContext
)


class ExamFactory:
    """
    Factory for creating Exam domain objects.

    Implements Domain-Driven Design (DDD) Factory Pattern.
    Encapsulates complex creation logic and ensures valid domain objects.
    """

    @staticmethod
    def create_exam_simulation(
        course_id: str,
        user_id: str,
        config: ExamConfig,
        context: ExamContext,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new exam simulation.

        Args:
            course_id: Course UUID
            user_id: User UUID
            config: ExamConfig value object
            context: ExamContext value object
            title: Optional custom title

        Returns:
            Dictionary ready for database insertion
        """
        # Generate title if not provided
        if not title:
            title = ExamFactory._generate_title(context, config)

        return {
            'simulation_id': str(uuid4()),
            'course_id': course_id,
            'user_id': user_id,
            'title': title,
            'context_json': json.dumps(context.to_dict()),
            'config_json': json.dumps(config.to_dict()),
            'status': ExamStatus.PENDING.value,
            'created_at': datetime.utcnow()
        }

    @staticmethod
    def create_exam_attempt(
        simulation_id: str,
        user_id: str,
        max_score: int
    ) -> Dict[str, Any]:
        """
        Create a new exam attempt.

        Args:
            simulation_id: Exam simulation UUID
            user_id: User UUID
            max_score: Maximum possible score

        Returns:
            Dictionary ready for database insertion
        """
        return {
            'attempt_id': str(uuid4()),
            'simulation_id': simulation_id,
            'user_id': user_id,
            'max_score': max_score,
            'status': AttemptStatus.IN_PROGRESS.value,
            'started_at': datetime.utcnow()
        }

    @staticmethod
    def create_exam_question(
        exam_id: str,
        question_type: QuestionType,
        question_text: str,
        points: int,
        data: Dict[str, Any],
        solution: Dict[str, Any],
        order_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create an exam question.

        Args:
            exam_id: Exam UUID
            question_type: Type of question
            question_text: Question text
            points: Points for this question
            data: Question-specific data (options, etc.)
            solution: Solution data
            order_index: Optional order index

        Returns:
            Dictionary ready for database insertion
        """
        return {
            'question_id': str(uuid4()),
            'exam_id': exam_id,
            'question_type': question_type.value,
            'question_text': question_text,
            'points': points,
            'data': json.dumps(data) if isinstance(data, dict) else data,
            'solution': json.dumps(solution) if isinstance(solution, dict) else solution,
            'order_index': order_index,
            'created_at': datetime.utcnow()
        }

    @staticmethod
    def create_user_exam_profile(
        user_id: str,
        profession: Optional[str] = None,
        target_exam: Optional[str] = None,
        region: Optional[str] = None,
        preferred_difficulty: Optional[Difficulty] = None
    ) -> Dict[str, Any]:
        """
        Create or update user exam profile.

        Args:
            user_id: User UUID
            profession: User's profession
            target_exam: Target exam (AP1, AP2, etc.)
            region: Geographic region
            preferred_difficulty: Preferred difficulty level

        Returns:
            Dictionary ready for database insertion/update
        """
        profile = {
            'user_id': user_id,
            'updated_at': datetime.utcnow()
        }

        if profession:
            profile['profession'] = profession

        if target_exam:
            profile['target_exam'] = target_exam

        if region:
            profile['region'] = region

        if preferred_difficulty:
            profile['preferred_difficulty'] = preferred_difficulty.value

        return profile

    @staticmethod
    def _generate_title(context: ExamContext, config: ExamConfig) -> str:
        """
        Generate exam title from context and config.

        Args:
            context: ExamContext value object
            config: ExamConfig value object

        Returns:
            Generated title string
        """
        difficulty_labels = {
            Difficulty.EASY: 'Leicht',
            Difficulty.REALISTIC: 'Realistisch',
            Difficulty.HARD: 'Schwer'
        }

        parts = []

        # Add profession if available
        if context.profession:
            parts.append(context.profession)

        # Add exam level if available
        if context.exam_level:
            parts.append(context.exam_level)

        # Add "Simulation"
        parts.append('Simulation')

        # Add difficulty
        difficulty_label = difficulty_labels.get(config.difficulty, 'Realistisch')
        parts.append(f"- {difficulty_label}")

        return ' '.join(parts)


class QuestionFactory:
    """
    Specialized factory for creating different types of exam questions.
    """

    @staticmethod
    def create_multiple_choice(
        exam_id: str,
        question_text: str,
        options: list[str],
        correct_answer: str,
        points: int = 1,
        explanation: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a multiple choice question.

        Args:
            exam_id: Exam UUID
            question_text: Question text
            options: List of option strings (e.g., ['A: Option 1', 'B: Option 2'])
            correct_answer: Correct answer (e.g., 'A')
            points: Points for this question
            explanation: Optional explanation
            topic: Optional topic category
            difficulty: Optional difficulty level

        Returns:
            Dictionary ready for database insertion
        """
        data = {
            'options': options,
            'topic': topic,
            'difficulty': difficulty
        }

        solution = {
            'correct_answer': correct_answer,
            'explanation': explanation
        }

        return ExamFactory.create_exam_question(
            exam_id=exam_id,
            question_type=QuestionType.MULTIPLE_CHOICE,
            question_text=question_text,
            points=points,
            data=data,
            solution=solution
        )

    @staticmethod
    def create_true_false(
        exam_id: str,
        question_text: str,
        correct_answer: bool,
        points: int = 1,
        explanation: Optional[str] = None,
        topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a true/false question.

        Args:
            exam_id: Exam UUID
            question_text: Question text
            correct_answer: True or False
            points: Points for this question
            explanation: Optional explanation
            topic: Optional topic category

        Returns:
            Dictionary ready for database insertion
        """
        data = {
            'topic': topic
        }

        solution = {
            'correct_answer': correct_answer,
            'explanation': explanation
        }

        return ExamFactory.create_exam_question(
            exam_id=exam_id,
            question_type=QuestionType.TRUE_FALSE,
            question_text=question_text,
            points=points,
            data=data,
            solution=solution
        )

    @staticmethod
    def create_calculation(
        exam_id: str,
        question_text: str,
        correct_answer: float,
        points: int = 2,
        explanation: Optional[str] = None,
        topic: Optional[str] = None,
        unit: Optional[str] = None,
        tolerance: float = 0.01
    ) -> Dict[str, Any]:
        """
        Create a calculation question.

        Args:
            exam_id: Exam UUID
            question_text: Question text
            correct_answer: Correct numerical answer
            points: Points for this question
            explanation: Optional explanation
            topic: Optional topic category
            unit: Optional unit (e.g., 'EUR', 'kg')
            tolerance: Tolerance for answer validation

        Returns:
            Dictionary ready for database insertion
        """
        data = {
            'topic': topic,
            'unit': unit,
            'tolerance': tolerance
        }

        solution = {
            'correct_answer': correct_answer,
            'explanation': explanation
        }

        return ExamFactory.create_exam_question(
            exam_id=exam_id,
            question_type=QuestionType.CALCULATION,
            question_text=question_text,
            points=points,
            data=data,
            solution=solution
        )

    @staticmethod
    def create_short_answer(
        exam_id: str,
        question_text: str,
        correct_answers: list[str],
        points: int = 2,
        explanation: Optional[str] = None,
        topic: Optional[str] = None,
        case_sensitive: bool = False
    ) -> Dict[str, Any]:
        """
        Create a short answer question.

        Args:
            exam_id: Exam UUID
            question_text: Question text
            correct_answers: List of acceptable correct answers
            points: Points for this question
            explanation: Optional explanation
            topic: Optional topic category
            case_sensitive: Whether answer matching is case-sensitive

        Returns:
            Dictionary ready for database insertion
        """
        data = {
            'topic': topic,
            'case_sensitive': case_sensitive
        }

        solution = {
            'correct_answers': correct_answers,
            'explanation': explanation
        }

        return ExamFactory.create_exam_question(
            exam_id=exam_id,
            question_type=QuestionType.SHORT_ANSWER,
            question_text=question_text,
            points=points,
            data=data,
            solution=solution
        )
