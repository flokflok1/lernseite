"""
ExamTrainer Repository

Data access layer for user-facing exam trainer features:
- Topic listing with user statistics
- Topic stats tracking (upsert on answer submission)
- Exam attempt management (start, complete)
- Answer recording and grading support
- Adaptive attempt creation and pool stats

All queries use parameterized SQL (%s) via psycopg3.

Split into two files for G01 compliance:
  - trainer.py: Core attempt/answer/result CRUD, adaptive attempts, pool stats
  - trainer_part2.py: Rotation queries, review, history
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import uuid

from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    insert_returning,
    update_returning,
    execute_query
)
from app.infrastructure.persistence.repositories.exams.trainer_part2 import (
    ExamTrainerRotationMixin,
)


class ExamTrainerRepository(ExamTrainerRotationMixin):
    """
    Repository for exam trainer user-facing queries.

    Handles:
    - Topic aggregation across archive exams
    - Per-user topic statistics (exam_topic_stats)
    - Exam attempts lifecycle
    - Answer recording
    - Adaptive exam attempts
    - Question pool statistics
    """

    @classmethod
    def find_published_archive_exams(cls) -> List[Dict]:
        """
        Find all published archive exams ready for practice.

        Returns:
            List of exams with question_count
        """
        query = """
            SELECT e.exam_id, e.title, e.semester, e.part,
                   e.year, e.season, e.profession, e.region,
                   e.duration_minutes, e.passing_score,
                   e.total_points, e.analysis_status,
                   COUNT(eq.question_id) as question_count
            FROM assessments.exams e
            LEFT JOIN assessments.exam_questions eq
                ON e.exam_id = eq.exam_id
            WHERE e.exam_type = 'real'
              AND e.published = true
              AND e.analysis_status = 'ready'
            GROUP BY e.exam_id
            ORDER BY e.year DESC NULLS LAST, e.season
        """
        return fetch_all(query)

    @classmethod
    def find_topics_with_stats(cls, user_id: int) -> List[Dict]:
        """
        Get all distinct topics across archive questions
        joined with per-user statistics.

        Args:
            user_id: Current user's ID

        Returns:
            List of topic records with question_count and user stats
        """
        query = """
            SELECT t.topic,
                   COUNT(*) as question_count,
                   COALESCE(s.attempts, 0) as user_attempts,
                   CASE WHEN s.attempts > 0
                        THEN ROUND(
                            s.correct_count::numeric / s.attempts * 100, 1
                        )
                        ELSE 0
                   END as correct_pct
            FROM (
                SELECT DISTINCT unnest(eq.topics) as topic
                FROM assessments.exam_questions eq
                JOIN assessments.exams e ON e.exam_id = eq.exam_id
                WHERE e.exam_type = 'real'
            ) t
            LEFT JOIN assessments.exam_topic_stats s
                ON s.topic = t.topic AND s.user_id = %s
            GROUP BY t.topic, s.attempts, s.correct_count
            ORDER BY t.topic
        """
        return fetch_all(query, (user_id,))

    @classmethod
    def upsert_topic_stats(
        cls,
        user_id: int,
        topic: str,
        is_correct: bool,
        total_points: int,
        earned_points: int
    ) -> None:
        """
        Insert or update topic statistics for a user.

        Uses ON CONFLICT upsert to atomically track attempts.

        Args:
            user_id: User ID
            topic: Topic string
            is_correct: Whether the answer was correct
            total_points: Maximum points for the question
            earned_points: Points earned by the user
        """
        correct_val = 1 if is_correct else 0
        query = """
            INSERT INTO assessments.exam_topic_stats
                (user_id, topic, attempts, correct_count,
                 total_points, earned_points, last_attempt_at)
            VALUES (%s, %s, 1, %s, %s, %s, NOW())
            ON CONFLICT (user_id, topic) DO UPDATE SET
                attempts = assessments.exam_topic_stats.attempts + 1,
                correct_count = assessments.exam_topic_stats.correct_count
                    + EXCLUDED.correct_count,
                total_points = assessments.exam_topic_stats.total_points
                    + EXCLUDED.total_points,
                earned_points = assessments.exam_topic_stats.earned_points
                    + EXCLUDED.earned_points,
                last_attempt_at = NOW(),
                updated_at = NOW()
        """
        execute_query(query, (user_id, topic, correct_val,
                              total_points, earned_points))

    @classmethod
    def create_attempt(
        cls,
        user_id: int,
        exam_id: str,
        time_limit_minutes: int
    ) -> Optional[Dict]:
        """
        Create a new exam attempt with status 'in_progress'.

        Args:
            user_id: User ID
            exam_id: Exam UUID
            time_limit_minutes: Time limit in minutes

        Returns:
            Created attempt record
        """
        attempt_data = {
            'attempt_id': str(uuid.uuid4()),
            'user_id': user_id,
            'exam_id': exam_id,
            'status': 'in_progress',
            'started_at': datetime.utcnow(),
            'time_limit_minutes': time_limit_minutes
        }
        return insert_returning(
            'assessments.exam_attempts', attempt_data, '*',
        )

    @classmethod
    def find_attempt(cls, attempt_id: str) -> Optional[Dict]:
        """
        Find an exam attempt by ID.

        Args:
            attempt_id: Attempt UUID

        Returns:
            Attempt record or None
        """
        query = """
            SELECT * FROM assessments.exam_attempts
            WHERE attempt_id = %s
        """
        return fetch_one(query, (attempt_id,))

    @classmethod
    def complete_attempt(
        cls,
        attempt_id: str,
        score: float,
        total_points: int,
        passed: bool
    ) -> Optional[Dict]:
        """
        Mark an attempt as completed with final score.

        Args:
            attempt_id: Attempt UUID
            score: Earned score
            total_points: Maximum possible points
            passed: Whether the user passed

        Returns:
            Updated attempt record
        """
        update_data = {
            'status': 'completed',
            'score': score,
            'total_points': total_points,
            'passed': passed,
            'completed_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        where = "attempt_id = %s"
        return update_returning(
            'assessments.exam_attempts', update_data, where,
            (attempt_id,), '*'
        )

    @classmethod
    def record_answer(
        cls,
        attempt_id: str,
        question_id: str,
        user_answer: Any,
        is_correct: Optional[bool],
        points_earned: float,
        needs_review: bool = False
    ) -> Optional[Dict]:
        """
        Record a user's answer to an exam question.

        Args:
            attempt_id: Attempt UUID
            question_id: Question UUID
            user_answer: User's answer (JSONB)
            is_correct: Whether the answer is correct (None if needs_review)
            points_earned: Points earned
            needs_review: Whether manual review is needed

        Returns:
            Created answer record
        """
        answer_data = {
            'answer_id': str(uuid.uuid4()),
            'attempt_id': attempt_id,
            'question_id': question_id,
            'user_answer': json.dumps(user_answer)
                if isinstance(user_answer, (dict, list)) else user_answer,
            'is_correct': is_correct,
            'points_earned': points_earned,
            'flagged_for_review': needs_review,
            'answered_at': datetime.utcnow()
        }
        return insert_returning(
            'assessments.exam_answers', answer_data, '*',
        )

    @classmethod
    def get_attempt_answers(cls, attempt_id: str) -> List[Dict]:
        """
        Get all answers for an attempt.

        Args:
            attempt_id: Attempt UUID

        Returns:
            List of answer records with question details
        """
        query = """
            SELECT ea.*, eq.points as max_points,
                   eq.topics, eq.question_type
            FROM assessments.exam_answers ea
            JOIN assessments.exam_questions eq
                ON ea.question_id = eq.question_id
            WHERE ea.attempt_id = %s
            ORDER BY ea.answered_at
        """
        return fetch_all(query, (attempt_id,))

    @classmethod
    def create_exam_result(
        cls,
        attempt_id: str,
        user_id: int,
        exam_id: str,
        score: float,
        total_points: int,
        percentage: float,
        passed: bool,
        results_by_topic: Dict
    ) -> Optional[Dict]:
        """
        Create an exam result summary record.

        Args:
            attempt_id: Attempt UUID
            user_id: User ID
            exam_id: Exam UUID
            score: Earned score
            total_points: Maximum points
            percentage: Score percentage
            passed: Whether the user passed
            results_by_topic: Per-topic breakdown (JSONB)

        Returns:
            Created result record
        """
        result_data = {
            'result_id': str(uuid.uuid4()),
            'attempt_id': attempt_id,
            'user_id': user_id,
            'exam_id': exam_id,
            'score': score,
            'total_points': total_points,
            'percentage': percentage,
            'passed': passed,
            'details': json.dumps(results_by_topic),
            'graded_at': datetime.utcnow()
        }
        return insert_returning(
            'assessments.exam_results', result_data, '*',
        )

    @classmethod
    def create_adaptive_attempt(
        cls,
        user_id: int,
        duration_minutes: int,
        total_points: int,
    ) -> Optional[Dict]:
        """Create an exam attempt for an adaptive session (no fixed exam).

        Args:
            user_id: User ID
            duration_minutes: Time limit in minutes
            total_points: Maximum possible points

        Returns:
            Created attempt record or None
        """
        attempt_data = {
            'attempt_id': str(uuid.uuid4()),
            'user_id': user_id,
            'exam_id': None,
            'status': 'in_progress',
            'started_at': datetime.utcnow(),
            'time_limit_minutes': duration_minutes,
            'total_points': total_points,
        }
        return insert_returning(
            'assessments.exam_attempts', attempt_data, '*',
        )

    @classmethod
    def count_pool_stats(cls, user_id: int) -> Dict:
        """Get overall question pool statistics for the dashboard.

        Args:
            user_id: User ID

        Returns:
            Dict with total_questions, seen_questions, mastered_questions
        """
        query = """
            SELECT
                (SELECT count(*) FROM assessments.exam_questions eq
                 JOIN assessments.exams e ON e.exam_id = eq.exam_id
                 WHERE e.analysis_status = 'ready'
                   AND e.published = true) AS total_questions,
                (SELECT count(*) FROM assessments.user_question_stats
                 WHERE user_id = %s) AS seen_questions,
                (SELECT count(*) FROM assessments.user_question_stats
                 WHERE user_id = %s AND times_correct > 0
                 AND times_correct::float
                     / GREATEST(times_seen, 1) >= 0.5) AS mastered_questions
        """
        row = fetch_one(query, (user_id, user_id))
        if not row:
            return {
                'total_questions': 0,
                'seen_questions': 0,
                'mastered_questions': 0,
            }
        return {
            'total_questions': row.get('total_questions', 0) or 0,
            'seen_questions': row.get('seen_questions', 0) or 0,
            'mastered_questions': row.get('mastered_questions', 0) or 0,
        }

    @classmethod
    def find_programs(cls, user_id: int) -> List[Dict]:
        """Find exam training programs from exam data (not courses).

        Groups published exams by profession to build programs.
        Independent of course existence.
        """
        query = """
            SELECT
                COALESCE(e.profession, 'GENERAL') AS program_id,
                CASE e.profession
                    WHEN 'FISI' THEN 'Fachinformatiker Systemintegration — AP1'
                    WHEN 'FIAE' THEN 'Fachinformatiker Anwendungsentwicklung — AP1'
                    ELSE COALESCE(e.profession, 'Allgemein')
                END AS title,
                count(DISTINCT eq.question_id) AS total_questions,
                count(DISTINCT e.exam_id) AS exam_count,
                (SELECT count(*) FROM assessments.user_question_stats
                 WHERE user_id = %s) AS seen_questions,
                (SELECT count(*) FROM assessments.user_question_stats
                 WHERE user_id = %s AND times_correct > 0
                 AND times_correct::float / GREATEST(times_seen, 1) >= 0.5
                ) AS mastered_questions
            FROM assessments.exams e
            JOIN assessments.exam_questions eq ON eq.exam_id = e.exam_id
            WHERE e.analysis_status = 'ready' AND e.published = true
            GROUP BY e.profession
            ORDER BY count(DISTINCT eq.question_id) DESC
        """
        return fetch_all(query, (user_id, user_id))

    @classmethod
    def find_exam_topics(cls) -> List[Dict]:
        """Get distinct topics from exam questions as topic categories."""
        query = """
            SELECT DISTINCT unnest(eq.topics) AS title,
                   count(*) AS question_count
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON e.exam_id = eq.exam_id
            WHERE e.analysis_status = 'ready'
            GROUP BY unnest(eq.topics)
            ORDER BY count(*) DESC
            LIMIT 20
        """
        return fetch_all(query)
