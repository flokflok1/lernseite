"""
Exam Systems Repository

Handles database operations for all exam systems (IHK, Practical, Chapter Completion).

DDD Repository Pattern - Single source of truth for exam data access.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from app.repositories.base_repository import BaseRepository


class ExamRepository:
    """
    Repository for Exam operations.

    Handles:
    - Exam CRUD (all types: IHK, Practical, Chapter Completion)
    - Exam questions management
    - Exam attempts tracking
    - Exam results storage
    """

    # ========================================================================
    # Exam Templates (Admin)
    # ========================================================================

    @staticmethod
    def create_exam(exam_data: Dict[str, Any]) -> Dict:
        """
        Create a new exam template.

        Args:
            exam_data: Exam data (type, title, config, etc.)

        Returns:
            Created exam record

        Example:
            {
                'exam_id': 'uuid',
                'exam_type': 'ihk',
                'title': 'IHK FISI Abschlussprüfung 2024',
                'course_id': 'course-uuid',
                'chapter_id': 'chapter-uuid',
                'config': {...},
                'is_active': True
            }
        """
        query = """
            INSERT INTO exams (
                exam_type, title, description, course_id, chapter_id,
                time_limit_minutes, passing_percentage, config, is_active
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING exam_id, exam_type, title, description, course_id, chapter_id,
                      time_limit_minutes, passing_percentage, config, is_active, created_at
        """
        import json
        return BaseRepository.fetch_one(query, (
            exam_data.get('exam_type'),
            exam_data.get('title'),
            exam_data.get('description'),
            exam_data.get('course_id'),
            exam_data.get('chapter_id'),
            exam_data.get('time_limit_minutes', 60),
            exam_data.get('passing_percentage', 50),
            json.dumps(exam_data.get('config', {})),
            exam_data.get('is_active', True)
        ))

    @staticmethod
    def get_exam_by_id(exam_id: str) -> Optional[Dict]:
        """
        Get exam by ID.

        Args:
            exam_id: UUID of the exam

        Returns:
            Exam record or None
        """
        query = """
            SELECT
                exam_id, exam_type, title, description, course_id, chapter_id,
                time_limit_minutes, passing_percentage, config, is_active,
                created_at, updated_at
            FROM exams
            WHERE exam_id = %s
        """
        return BaseRepository.fetch_one(query, (exam_id,))

    @staticmethod
    def get_exams_by_course(course_id: str, exam_type: Optional[str] = None) -> List[Dict]:
        """
        Get all exams for a course.

        Args:
            course_id: UUID of the course
            exam_type: Optional filter by exam type

        Returns:
            List of exam records
        """
        if exam_type:
            query = """
                SELECT
                    exam_id, exam_type, title, description, chapter_id,
                    time_limit_minutes, passing_percentage, is_active
                FROM exams
                WHERE course_id = %s AND exam_type = %s
                ORDER BY created_at DESC
            """
            return BaseRepository.fetch_all(query, (course_id, exam_type)) or []
        else:
            query = """
                SELECT
                    exam_id, exam_type, title, description, chapter_id,
                    time_limit_minutes, passing_percentage, is_active
                FROM exams
                WHERE course_id = %s
                ORDER BY exam_type, created_at DESC
            """
            return BaseRepository.fetch_all(query, (course_id,)) or []

    @staticmethod
    def get_exams_by_chapter(chapter_id: str) -> List[Dict]:
        """
        Get all exams for a chapter.

        Args:
            chapter_id: UUID of the chapter

        Returns:
            List of exam records
        """
        query = """
            SELECT
                exam_id, exam_type, title, description,
                time_limit_minutes, passing_percentage, is_active
            FROM exams
            WHERE chapter_id = %s AND is_active = TRUE
            ORDER BY exam_type, created_at DESC
        """
        return BaseRepository.fetch_all(query, (chapter_id,)) or []

    @staticmethod
    def update_exam(exam_id: str, exam_data: Dict[str, Any]) -> Dict:
        """
        Update an exam.

        Args:
            exam_id: UUID of the exam
            exam_data: Updated exam data

        Returns:
            Updated exam record
        """
        query = """
            UPDATE exams
            SET
                title = COALESCE(%s, title),
                description = COALESCE(%s, description),
                time_limit_minutes = COALESCE(%s, time_limit_minutes),
                passing_percentage = COALESCE(%s, passing_percentage),
                config = COALESCE(%s, config),
                is_active = COALESCE(%s, is_active),
                updated_at = NOW()
            WHERE exam_id = %s
            RETURNING exam_id, exam_type, title, description, time_limit_minutes,
                      passing_percentage, config, is_active, updated_at
        """
        import json
        config_json = json.dumps(exam_data.get('config')) if 'config' in exam_data else None

        return BaseRepository.fetch_one(query, (
            exam_data.get('title'),
            exam_data.get('description'),
            exam_data.get('time_limit_minutes'),
            exam_data.get('passing_percentage'),
            config_json,
            exam_data.get('is_active'),
            exam_id
        ))

    @staticmethod
    def delete_exam(exam_id: str) -> bool:
        """
        Soft-delete an exam (set is_active = False).

        Args:
            exam_id: UUID of the exam

        Returns:
            True if deleted successfully
        """
        query = "UPDATE exams SET is_active = FALSE, updated_at = NOW() WHERE exam_id = %s"
        BaseRepository.execute(query, (exam_id,))
        return True

    # ========================================================================
    # Exam Questions (Admin)
    # ========================================================================

    @staticmethod
    def add_question(question_data: Dict[str, Any]) -> Dict:
        """
        Add a question to an exam.

        Args:
            question_data: Question data

        Returns:
            Created question record
        """
        query = """
            INSERT INTO exam_questions (
                exam_id, question_type, question_text, points,
                options, correct_answer, explanation, order_index
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING question_id, exam_id, question_type, question_text,
                      points, options, correct_answer, order_index
        """
        import json
        return BaseRepository.fetch_one(query, (
            question_data.get('exam_id'),
            question_data.get('question_type'),
            question_data.get('question_text'),
            question_data.get('points', 1),
            json.dumps(question_data.get('options', [])),
            json.dumps(question_data.get('correct_answer')),
            question_data.get('explanation'),
            question_data.get('order_index', 0)
        ))

    @staticmethod
    def get_exam_questions(exam_id: str) -> List[Dict]:
        """
        Get all questions for an exam.

        Args:
            exam_id: UUID of the exam

        Returns:
            List of question records
        """
        query = """
            SELECT
                question_id, exam_id, question_type, question_text,
                points, options, correct_answer, explanation, order_index
            FROM exam_questions
            WHERE exam_id = %s
            ORDER BY order_index ASC, created_at ASC
        """
        return BaseRepository.fetch_all(query, (exam_id,)) or []

    # ========================================================================
    # Exam Attempts (User)
    # ========================================================================

    @staticmethod
    def start_exam_attempt(attempt_data: Dict[str, Any]) -> Dict:
        """
        Start a new exam attempt.

        Args:
            attempt_data: Attempt data (user_id, exam_id, etc.)

        Returns:
            Created attempt record
        """
        query = """
            INSERT INTO exam_attempts (
                user_id, exam_id, status, started_at, expires_at
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING attempt_id, user_id, exam_id, status, started_at, expires_at
        """
        return BaseRepository.fetch_one(query, (
            attempt_data.get('user_id'),
            attempt_data.get('exam_id'),
            'in_progress',
            attempt_data.get('started_at'),
            attempt_data.get('expires_at')
        ))

    @staticmethod
    def get_attempt_by_id(attempt_id: str) -> Optional[Dict]:
        """
        Get exam attempt by ID.

        Args:
            attempt_id: UUID of the attempt

        Returns:
            Attempt record or None
        """
        query = """
            SELECT
                attempt_id, user_id, exam_id, status,
                started_at, completed_at, expires_at,
                score_percentage, score_points, passed
            FROM exam_attempts
            WHERE attempt_id = %s
        """
        return BaseRepository.fetch_one(query, (attempt_id,))

    @staticmethod
    def get_user_attempts(user_id: str, exam_id: Optional[str] = None) -> List[Dict]:
        """
        Get all exam attempts for a user.

        Args:
            user_id: UUID of the user
            exam_id: Optional filter by exam ID

        Returns:
            List of attempt records
        """
        if exam_id:
            query = """
                SELECT
                    attempt_id, exam_id, status, started_at, completed_at,
                    score_percentage, passed
                FROM exam_attempts
                WHERE user_id = %s AND exam_id = %s
                ORDER BY started_at DESC
            """
            return BaseRepository.fetch_all(query, (user_id, exam_id)) or []
        else:
            query = """
                SELECT
                    attempt_id, exam_id, status, started_at, completed_at,
                    score_percentage, passed
                FROM exam_attempts
                WHERE user_id = %s
                ORDER BY started_at DESC
            """
            return BaseRepository.fetch_all(query, (user_id,)) or []

    @staticmethod
    def submit_answer(answer_data: Dict[str, Any]) -> Dict:
        """
        Submit an answer for a question.

        Args:
            answer_data: Answer data (attempt_id, question_id, answer, etc.)

        Returns:
            Created answer record
        """
        query = """
            INSERT INTO exam_answers (
                attempt_id, question_id, answer, points_earned, is_correct
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (attempt_id, question_id)
            DO UPDATE SET
                answer = EXCLUDED.answer,
                points_earned = EXCLUDED.points_earned,
                is_correct = EXCLUDED.is_correct,
                updated_at = NOW()
            RETURNING answer_id, attempt_id, question_id, answer, points_earned, is_correct
        """
        import json
        return BaseRepository.fetch_one(query, (
            answer_data.get('attempt_id'),
            answer_data.get('question_id'),
            json.dumps(answer_data.get('answer')),
            answer_data.get('points_earned', 0),
            answer_data.get('is_correct', False)
        ))

    @staticmethod
    def complete_exam_attempt(attempt_id: str, score_data: Dict[str, Any]) -> Dict:
        """
        Complete an exam attempt and store results.

        Args:
            attempt_id: UUID of the attempt
            score_data: Score data (points, percentage, passed)

        Returns:
            Updated attempt record
        """
        query = """
            UPDATE exam_attempts
            SET
                status = 'completed',
                completed_at = NOW(),
                score_points = %s,
                score_percentage = %s,
                passed = %s
            WHERE attempt_id = %s
            RETURNING attempt_id, status, completed_at, score_points, score_percentage, passed
        """
        return BaseRepository.fetch_one(query, (
            score_data.get('points_earned'),
            score_data.get('percentage'),
            score_data.get('passed'),
            attempt_id
        ))

    @staticmethod
    def get_attempt_answers(attempt_id: str) -> List[Dict]:
        """
        Get all answers for an exam attempt.

        Args:
            attempt_id: UUID of the attempt

        Returns:
            List of answer records
        """
        query = """
            SELECT
                answer_id, question_id, answer, points_earned, is_correct
            FROM exam_answers
            WHERE attempt_id = %s
        """
        return BaseRepository.fetch_all(query, (attempt_id,)) or []
