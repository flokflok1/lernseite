"""
Exam Domain Service.

Core business logic for exam domain following DDD principles.
Coordinates between repositories, factories, and value objects.
"""

import json
from typing import Dict, Any, Optional, List
from uuid import UUID
import logging

from app.database.connection import fetch_one, fetch_all, execute_query

from .factory import ExamFactory, QuestionFactory
from .value_objects import (
    ExamStatus, AttemptStatus, ExamConfig, ExamContext,
    QuestionType, Difficulty
)

logger = logging.getLogger(__name__)


class ExamService:
    """
    Core service for exam domain logic.

    Handles:
    - Exam simulation creation and management
    - Attempt lifecycle
    - Answer evaluation
    - Score calculation
    """

    @staticmethod
    def create_simulation(
        course_id: str,
        user_id: str,
        config_data: Dict[str, Any],
        context_data: Dict[str, Any],
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new exam simulation.

        Args:
            course_id: Course UUID
            user_id: User UUID
            config_data: Configuration dictionary
            context_data: Context dictionary
            title: Optional custom title

        Returns:
            Created simulation data
        """
        # Build value objects
        config = ExamConfig.from_dict(config_data)
        context = ExamContext.from_dict(context_data)

        # Use factory to create simulation
        simulation_data = ExamFactory.create_exam_simulation(
            course_id=course_id,
            user_id=user_id,
            config=config,
            context=context,
            title=title
        )

        # Insert into database
        query = """
            INSERT INTO exam_simulations (
                simulation_id, course_id, user_id, title,
                context_json, config_json, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING simulation_id, course_id, user_id, title,
                      context_json, config_json, status, created_at
        """

        result = fetch_one(query, (
            simulation_data['simulation_id'],
            simulation_data['course_id'],
            simulation_data['user_id'],
            simulation_data['title'],
            simulation_data['context_json'],
            simulation_data['config_json'],
            simulation_data['status'],
            simulation_data['created_at']
        ))

        return dict(result) if result else None

    @staticmethod
    def start_attempt(
        simulation_id: str,
        user_id: str
    ) -> tuple[Optional[Dict[str, Any]], Optional[List[Dict[str, Any]]]]:
        """
        Start a new exam attempt.

        Args:
            simulation_id: Simulation UUID
            user_id: User UUID

        Returns:
            Tuple of (attempt_data, questions) or (None, None) if failed

        Raises:
            ValueError: If simulation not ready or not found
        """
        # Get simulation
        sim = fetch_one(
            """
            SELECT simulation_id, user_id, status, result_json, config_json
            FROM exam_simulations
            WHERE simulation_id = %s
            """,
            (simulation_id,)
        )

        if not sim:
            raise ValueError("Simulation not found")

        if str(sim['user_id']) != user_id:
            raise ValueError("Access denied")

        # Check status using value object
        status = ExamStatus.from_string(sim['status'])
        if not status.can_start_attempt():
            raise ValueError(f"Simulation not ready (status: {status.value})")

        if not sim['result_json']:
            raise ValueError("Simulation has no questions")

        # Get max score
        result_data = sim['result_json']
        max_score = result_data.get('total_points', 100)

        # Create attempt using factory
        attempt_data = ExamFactory.create_exam_attempt(
            simulation_id=simulation_id,
            user_id=user_id,
            max_score=max_score
        )

        # Insert attempt
        query = """
            INSERT INTO exam_simulation_attempts (
                attempt_id, simulation_id, user_id, max_score, status, started_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING attempt_id, started_at, status, max_score
        """

        attempt = fetch_one(query, (
            attempt_data['attempt_id'],
            attempt_data['simulation_id'],
            attempt_data['user_id'],
            attempt_data['max_score'],
            attempt_data['status'],
            attempt_data['started_at']
        ))

        # Update simulation attempt count
        execute_query(
            """
            UPDATE exam_simulations
            SET attempt_count = attempt_count + 1
            WHERE simulation_id = %s
            """,
            (simulation_id,)
        )

        # Prepare questions (without answers)
        questions = ExamService._sanitize_questions_for_attempt(
            result_data.get('questions', [])
        )

        return dict(attempt) if attempt else None, questions

    @staticmethod
    def submit_attempt(
        attempt_id: str,
        user_id: str,
        answers: List[Dict[str, Any]],
        time_spent_seconds: int
    ) -> Dict[str, Any]:
        """
        Submit and evaluate exam attempt.

        Args:
            attempt_id: Attempt UUID
            user_id: User UUID
            answers: List of answer dictionaries
            time_spent_seconds: Time spent on exam

        Returns:
            Evaluation results with score and feedback

        Raises:
            ValueError: If attempt not found, access denied, or already completed
        """
        # Get attempt with simulation data
        attempt = fetch_one(
            """
            SELECT a.*, s.result_json, s.simulation_id
            FROM exam_simulation_attempts a
            JOIN exam_simulations s ON s.simulation_id = a.simulation_id
            WHERE a.attempt_id = %s
            """,
            (attempt_id,)
        )

        if not attempt:
            raise ValueError("Attempt not found")

        if str(attempt['user_id']) != user_id:
            raise ValueError("Access denied")

        # Check status
        status = AttemptStatus.from_string(attempt['status'])
        if status != AttemptStatus.IN_PROGRESS:
            raise ValueError(f"Attempt already {status.value}")

        # Evaluate answers
        result_json = attempt['result_json'] or {}
        evaluation = ExamService._evaluate_answers(
            answers=answers,
            questions=result_json.get('questions', [])
        )

        # Calculate pass status (50% threshold)
        passed = evaluation['percentage'] >= 50

        # Update attempt
        execute_query(
            """
            UPDATE exam_simulation_attempts
            SET
                completed_at = NOW(),
                time_spent_seconds = %s,
                answers_json = %s,
                score = %s,
                percentage = %s,
                passed = %s,
                results_by_topic = %s,
                status = %s
            WHERE attempt_id = %s
            """,
            (
                time_spent_seconds,
                json.dumps(evaluation['evaluated_answers']),
                evaluation['total_score'],
                evaluation['percentage'],
                passed,
                json.dumps(evaluation['results_by_topic']),
                AttemptStatus.COMPLETED.value,
                attempt_id
            )
        )

        # Update simulation statistics
        execute_query(
            """
            UPDATE exam_simulations
            SET
                best_score = GREATEST(COALESCE(best_score, 0), %s),
                avg_score = (
                    SELECT AVG(percentage)
                    FROM exam_simulation_attempts
                    WHERE simulation_id = %s AND status = %s
                )
            WHERE simulation_id = %s
            """,
            (
                evaluation['percentage'],
                attempt['simulation_id'],
                AttemptStatus.COMPLETED.value,
                attempt['simulation_id']
            )
        )

        return {
            'attempt_id': attempt_id,
            'score': evaluation['total_score'],
            'max_score': evaluation['max_score'],
            'percentage': round(evaluation['percentage'], 1),
            'passed': passed,
            'time_spent_seconds': time_spent_seconds,
            'results_by_topic': evaluation['results_by_topic'],
            'answers': evaluation['evaluated_answers']
        }

    @staticmethod
    def _sanitize_questions_for_attempt(questions: List[Dict]) -> List[Dict]:
        """
        Remove correct answers and explanations from questions.

        Args:
            questions: List of question dictionaries

        Returns:
            Sanitized questions without solutions
        """
        sanitized = []
        for q in questions:
            sanitized.append({
                'question_id': q.get('question_id'),
                'type': q.get('type'),
                'topic': q.get('topic'),
                'difficulty': q.get('difficulty'),
                'points': q.get('points'),
                'question': q.get('question'),
                'options': q.get('options'),
            })
        return sanitized

    @staticmethod
    def _evaluate_answers(
        answers: List[Dict[str, Any]],
        questions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Evaluate submitted answers against correct solutions.

        Args:
            answers: User's submitted answers
            questions: Questions with correct solutions

        Returns:
            Evaluation results dictionary
        """
        questions_dict = {q['question_id']: q for q in questions}

        total_score = 0
        max_score = sum(q.get('points', 0) for q in questions)
        results_by_topic = {}
        evaluated_answers = []

        for ans in answers:
            q_id = ans.get('question_id')
            user_answer = ans.get('answer')

            question = questions_dict.get(q_id)
            if not question:
                continue

            points = question.get('points', 0)
            correct_answer = question.get('correct_answer')
            topic = question.get('topic', 'Allgemein')

            # Evaluate based on question type
            is_correct = ExamService._check_answer_correctness(
                user_answer=user_answer,
                correct_answer=correct_answer,
                question_type=question.get('type', 'multiple_choice')
            )

            earned_points = points if is_correct else 0
            total_score += earned_points

            # Track by topic
            if topic not in results_by_topic:
                results_by_topic[topic] = {
                    'correct': 0,
                    'total': 0,
                    'points': 0,
                    'max_points': 0
                }

            results_by_topic[topic]['total'] += 1
            results_by_topic[topic]['max_points'] += points
            if is_correct:
                results_by_topic[topic]['correct'] += 1
                results_by_topic[topic]['points'] += points

            evaluated_answers.append({
                'question_id': q_id,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
                'points_earned': earned_points,
                'points_possible': points,
                'explanation': question.get('explanation')
            })

        percentage = (total_score / max_score * 100) if max_score > 0 else 0

        return {
            'total_score': total_score,
            'max_score': max_score,
            'percentage': percentage,
            'results_by_topic': results_by_topic,
            'evaluated_answers': evaluated_answers
        }

    @staticmethod
    def _check_answer_correctness(
        user_answer: Any,
        correct_answer: Any,
        question_type: str
    ) -> bool:
        """
        Check if user answer is correct based on question type.

        Args:
            user_answer: User's submitted answer
            correct_answer: Correct answer
            question_type: Type of question

        Returns:
            True if answer is correct
        """
        if question_type == 'calculation':
            # Numerical comparison with tolerance
            try:
                user_num = float(user_answer)
                correct_num = float(correct_answer)
                tolerance = 0.01
                return abs(user_num - correct_num) <= tolerance
            except (ValueError, TypeError):
                return False

        elif question_type == 'true_false':
            # Boolean comparison
            return bool(user_answer) == bool(correct_answer)

        else:
            # String comparison (case-insensitive)
            return str(user_answer).strip().lower() == str(correct_answer).strip().lower()


class ExamGenerationService:
    """
    Service for exam generation tasks.

    Handles:
    - Triggering AI generation
    - Managing generation status
    """

    @staticmethod
    def start_generation(simulation_id: str) -> bool:
        """
        Start exam generation process.

        Args:
            simulation_id: Simulation UUID

        Returns:
            True if generation started successfully

        Raises:
            ValueError: If simulation not found or invalid status
        """
        # Get current status
        result = fetch_one(
            "SELECT status FROM exam_simulations WHERE simulation_id = %s",
            (simulation_id,)
        )

        if not result:
            raise ValueError("Simulation not found")

        status = ExamStatus.from_string(result['status'])

        if not status.can_regenerate():
            raise ValueError(f"Cannot generate: status is {status.value}")

        # Update status
        execute_query(
            """
            UPDATE exam_simulations
            SET status = %s, generation_started_at = NOW()
            WHERE simulation_id = %s
            """,
            (ExamStatus.GENERATING.value, simulation_id)
        )

        # Queue Celery task (if available)
        try:
            from app.tasks.exam_tasks import generate_exam_task
            generate_exam_task.delay(simulation_id)
            logger.info(f"Queued exam generation task for {simulation_id}")
        except ImportError:
            logger.warning("Celery not configured - exam generation will run synchronously")

        return True

    @staticmethod
    def mark_generation_complete(
        simulation_id: str,
        result_data: Dict[str, Any],
        tokens_used: int,
        model_used: str
    ) -> None:
        """
        Mark exam generation as complete.

        Args:
            simulation_id: Simulation UUID
            result_data: Generated exam data
            tokens_used: Number of AI tokens used
            model_used: AI model identifier
        """
        execute_query(
            """
            UPDATE exam_simulations
            SET
                status = %s,
                result_json = %s,
                generation_completed_at = NOW(),
                tokens_used = %s,
                model_used = %s
            WHERE simulation_id = %s
            """,
            (
                ExamStatus.READY.value,
                json.dumps(result_data),
                tokens_used,
                model_used,
                simulation_id
            )
        )
        logger.info(f"Exam generation complete for {simulation_id}")

    @staticmethod
    def mark_generation_failed(
        simulation_id: str,
        error_message: str
    ) -> None:
        """
        Mark exam generation as failed.

        Args:
            simulation_id: Simulation UUID
            error_message: Error message
        """
        execute_query(
            """
            UPDATE exam_simulations
            SET
                status = %s,
                error_message = %s
            WHERE simulation_id = %s
            """,
            (ExamStatus.FAILED.value, error_message, simulation_id)
        )
        logger.error(f"Exam generation failed for {simulation_id}: {error_message}")
