"""
LernsystemX Exam Simulations - Core API

Exam simulation service layer and data models.

Contains:
- ExamSimulationCreate (Pydantic model)
- ExamService (service class with create, start, submit methods)
- Blueprint definitions (core_bp, course_bp)

Route endpoints are in core_part2.py.

ISO 9001:2015 compliant - Assessment & Evaluation Layer
Split from: exam_simulations.py (Part 1/3 - Core Simulation Management)
"""

import json
from flask import Blueprint
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List
from uuid import uuid4
from datetime import datetime

from app.infrastructure.persistence.repositories.exams.simulations import ExamSimulationRepository

core_bp = Blueprint('exam_simulations_core', __name__, url_prefix='')
course_bp = Blueprint('exam_simulations_course', __name__, url_prefix='/courses')


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class ExamSimulationCreate(BaseModel):
    """Request model for creating an exam simulation."""
    mode: str = Field(default='smart', pattern='^(smart|manual)$')
    difficulty: str = Field(default='realistic', pattern='^(easy|realistic|hard)$')
    time_limit_minutes: int = Field(default=90, ge=15, le=180)
    focus_distribution: Optional[Dict[str, int]] = None
    extra_instructions: Optional[str] = None
    selected_files: Optional[List[str]] = None
    title: Optional[str] = None

    @validator('focus_distribution')
    def validate_focus_distribution(cls, v):
        if v is not None:
            total = sum(v.values())
            if total != 100:
                raise ValueError(f"Focus distribution must sum to 100%, got {total}%")
        return v


# =============================================================================
# EXAM SERVICE - CORE METHODS
# =============================================================================

class ExamService:
    """Exam service methods for simulation and attempt management."""

    @staticmethod
    def create_simulation(
        course_id: str,
        user_id: str,
        config_data: Dict,
        context_data: Dict,
        title: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create exam simulation record.

        Args:
            course_id: Course ID
            user_id: User ID
            config_data: Simulation config (mode, difficulty, time_limit, etc)
            context_data: Exam context (topics, focus areas, etc)
            title: Optional custom title

        Returns:
            Created simulation record or None
        """
        simulation_id = str(uuid4())

        # Auto-generate title if not provided
        if not title:
            difficulty = config_data.get('difficulty', 'realistic')
            title = f"Prüfungssimulation ({difficulty})"

        return ExamSimulationRepository.create_simulation(
            simulation_id=simulation_id,
            course_id=course_id,
            user_id=user_id,
            title=title,
            context_json=json.dumps(context_data),
            config_json=json.dumps(config_data)
        )

    @staticmethod
    def start_attempt(simulation_id: str, user_id: str) -> tuple[Optional[Dict], List[Dict]]:
        """
        Start new exam attempt.

        Args:
            simulation_id: Simulation ID
            user_id: User ID

        Returns:
            Tuple of (attempt record, questions without correct answers)

        Raises:
            ValueError: If simulation not found, not ready, or access denied
        """
        # Verify simulation is ready
        sim = ExamSimulationRepository.get_simulation_full(simulation_id)

        if not sim:
            raise ValueError("Simulation not found")

        if sim['status'] != 'ready':
            raise ValueError(f"Simulation not ready (status: {sim['status']})")

        if str(sim['user_id']) != user_id:
            raise ValueError("Access denied")

        # Create attempt
        attempt_id = str(uuid4())
        result_json = sim['result_json'] if sim.get('result_json') else {}
        questions = result_json.get('questions', []) if isinstance(result_json, dict) else []

        max_score = sum(q.get('points', 1) for q in questions)

        attempt = ExamSimulationRepository.create_attempt(
            attempt_id=attempt_id,
            simulation_id=simulation_id,
            user_id=user_id,
            max_score=max_score
        )

        # Strip correct answers from questions (for security)
        safe_questions = []
        for q in questions:
            safe_q = {k: v for k, v in q.items() if k != 'correct_answer'}
            safe_questions.append(safe_q)

        return attempt, safe_questions

    @staticmethod
    def submit_attempt(
        attempt_id: str,
        user_id: str,
        answers: List[Dict],
        time_spent_seconds: int
    ) -> Dict:
        """
        Submit and evaluate exam attempt.

        Args:
            attempt_id: Attempt ID
            user_id: User ID
            answers: List of {'question_id': 'q1', 'answer': 'A'} dicts
            time_spent_seconds: Time spent on exam

        Returns:
            Result dict with score, percentage, passed status, feedback
        """
        # Get attempt
        attempt = ExamSimulationRepository.get_attempt(attempt_id)

        if not attempt:
            raise ValueError("Attempt not found")

        if str(attempt['user_id']) != user_id:
            raise ValueError("Access denied")

        # Get simulation with questions and correct answers
        sim = ExamSimulationRepository.get_simulation_result(attempt['simulation_id'])

        result_json = sim['result_json'] if sim and sim.get('result_json') else {}
        questions = result_json.get('questions', []) if isinstance(result_json, dict) else []

        # Create answer map
        answer_map = {a['question_id']: a['answer'] for a in answers}

        # Evaluate answers
        score = 0
        max_score = attempt['max_score']
        results_by_topic = {}
        evaluated_answers = []

        for q in questions:
            q_id = q['id']
            correct = q.get('correct_answer')
            user_answer = answer_map.get(q_id)
            is_correct = user_answer == correct
            points = q.get('points', 1)

            if is_correct:
                score += points

            # Track by topic
            topic = q.get('topic', 'General')
            if topic not in results_by_topic:
                results_by_topic[topic] = {'correct': 0, 'total': 0}
            results_by_topic[topic]['total'] += 1
            if is_correct:
                results_by_topic[topic]['correct'] += 1

            evaluated_answers.append({
                'question_id': q_id,
                'user_answer': user_answer,
                'correct_answer': correct,
                'is_correct': is_correct,
                'points': points if is_correct else 0
            })

        # Calculate percentage and pass status
        percentage = (score / max_score * 100) if max_score > 0 else 0
        passed = percentage >= 60  # 60% pass threshold

        # Update attempt
        ExamSimulationRepository.complete_attempt(
            attempt_id=attempt_id,
            time_spent_seconds=time_spent_seconds,
            score=score,
            percentage=percentage,
            passed=passed,
            results_by_topic=results_by_topic
        )

        # Update simulation stats
        ExamSimulationRepository.update_simulation_stats(
            str(attempt['simulation_id']), score
        )

        return {
            'attempt_id': str(attempt_id),
            'score': score,
            'max_score': max_score,
            'percentage': percentage,
            'passed': passed,
            'time_spent_seconds': time_spent_seconds,
            'results_by_topic': results_by_topic,
            'evaluated_answers': evaluated_answers
        }


__all__ = ['core_bp', 'course_bp', 'ExamService', 'ExamSimulationCreate']
