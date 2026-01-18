"""
LernsystemX Exam Repository

Data access layer for exam management:
- CRUD operations for exams
- CRUD operations for exam questions
- Exam listing with filters
- AI-generated exam tracking

Phase C1.3 - KI-Prüfungs-Generator
Based on tables: exams, exam_questions
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from app.infrastructure.persistence.repositories.base_repository import BaseRepository
from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    insert_returning,
    update_returning,
    delete_returning,
    execute_query
)


class ExamRepository(BaseRepository):
    """
    Exam repository for CRUD operations on exams table

    Table: exams
    Primary Key: exam_id (UUID)
    """

    table_name = 'assessments.exams'
    pk_column = 'exam_id'

    @classmethod
    def find_by_id(cls, exam_id: str) -> Optional[Dict]:
        """
        Find exam by UUID with question count

        Args:
            exam_id: Exam UUID

        Returns:
            Exam record with question_count or None
        """
        query = """
            SELECT
                e.*,
                COUNT(eq.question_id) as question_count
            FROM assessments.exams e
            LEFT JOIN assessments.exam_questions eq ON e.exam_id = eq.exam_id
            WHERE e.exam_id = %s
            GROUP BY e.exam_id
        """
        return fetch_one(query, (exam_id,))

    @classmethod
    def find_by_course(cls, course_id: str, include_unpublished: bool = True) -> List[Dict]:
        """
        Find all exams for a course

        Args:
            course_id: Course UUID
            include_unpublished: Include unpublished exams (default: True for admins)

        Returns:
            List of exams with question counts
        """
        if include_unpublished:
            query = """
                SELECT
                    e.*,
                    COUNT(eq.question_id) as question_count
                FROM assessments.exams e
                LEFT JOIN assessments.exam_questions eq ON e.exam_id = eq.exam_id
                WHERE e.course_id = %s
                GROUP BY e.exam_id
                ORDER BY e.created_at DESC
            """
            return fetch_all(query, (course_id,))
        else:
            query = """
                SELECT
                    e.*,
                    COUNT(eq.question_id) as question_count
                FROM assessments.exams e
                LEFT JOIN assessments.exam_questions eq ON e.exam_id = eq.exam_id
                WHERE e.course_id = %s AND e.published = true
                GROUP BY e.exam_id
                ORDER BY e.created_at DESC
            """
            return fetch_all(query, (course_id,))

    @classmethod
    def create_exam(cls, exam_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create new exam

        Args:
            exam_data: Dictionary with exam fields
                - course_id (UUID)
                - exam_type (str)
                - title (str)
                - description (str, optional)
                - duration_minutes (int)
                - passing_score (int)
                - total_points (int, default: 100)
                - settings (dict/JSONB, optional)
                - published (bool, default: False)
                - generated_by_ai (bool, default: False)
                - ai_model (str, optional)
                - ai_job_id (UUID, optional)

        Returns:
            Created exam record
        """
        # Ensure JSONB fields are properly formatted
        if 'settings' in exam_data and isinstance(exam_data['settings'], dict):
            exam_data['settings'] = json.dumps(exam_data['settings'])

        return insert_returning('exams', exam_data, '*')

    @classmethod
    def update_exam(cls, exam_id: str, update_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Update exam metadata

        Args:
            exam_id: Exam UUID
            update_data: Dictionary with fields to update

        Returns:
            Updated exam record
        """
        # Ensure JSONB fields are properly formatted
        if 'settings' in update_data and isinstance(update_data['settings'], dict):
            update_data['settings'] = json.dumps(update_data['settings'])

        update_data['updated_at'] = datetime.utcnow()

        where = "exam_id = %s"
        return update_returning('exams', update_data, where, (exam_id,), '*')

    @classmethod
    def delete_exam(cls, exam_id: str) -> bool:
        """
        Delete exam and cascade to questions

        Args:
            exam_id: Exam UUID

        Returns:
            bool: True if deleted successfully
        """
        # Delete questions first (manual cascade)
        execute_query("DELETE FROM assessments.exam_questions WHERE exam_id = %s", (exam_id,))

        # Delete exam
        where = "exam_id = %s"
        result = delete_returning('exams', where, (exam_id,), 'exam_id')
        return result is not None

    @classmethod
    def publish_exam(cls, exam_id: str) -> Optional[Dict]:
        """
        Publish exam (make visible to students)

        Args:
            exam_id: Exam UUID

        Returns:
            Updated exam record
        """
        return cls.update_exam(exam_id, {'published': True})

    @classmethod
    def unpublish_exam(cls, exam_id: str) -> Optional[Dict]:
        """
        Unpublish exam (hide from students)

        Args:
            exam_id: Exam UUID

        Returns:
            Updated exam record
        """
        return cls.update_exam(exam_id, {'published': False})


class ExamQuestionRepository(BaseRepository):
    """
    Exam Question repository for CRUD operations on exam_questions table

    Table: exam_questions
    Primary Key: question_id (UUID)
    """

    table_name = 'assessments.exam_questions'
    pk_column = 'question_id'

    @classmethod
    def find_by_exam(cls, exam_id: str) -> List[Dict]:
        """
        Find all questions for an exam

        Args:
            exam_id: Exam UUID

        Returns:
            List of questions ordered by order_index
        """
        query = """
            SELECT *
            FROM assessments.exam_questions
            WHERE exam_id = %s
            ORDER BY order_index ASC
        """
        return fetch_all(query, (exam_id,))

    @classmethod
    def create_question(cls, question_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create new exam question

        Args:
            question_data: Dictionary with question fields
                - exam_id (UUID)
                - question_type (str)
                - question_text (str)
                - data (dict/JSONB) - question-specific data
                - solution (dict/JSONB) - solution data
                - points (int, default: 1)
                - order_index (int, optional)

        Returns:
            Created question record
        """
        # Auto-calculate order_index if not provided
        if 'order_index' not in question_data:
            max_order_query = """
                SELECT COALESCE(MAX(order_index), 0) as max_order
                FROM assessments.exam_questions
                WHERE exam_id = %s
            """
            result = fetch_one(max_order_query, (question_data['exam_id'],))
            question_data['order_index'] = result['max_order'] + 1 if result else 1

        # Ensure JSONB fields are properly formatted
        if 'data' in question_data and isinstance(question_data['data'], dict):
            question_data['data'] = json.dumps(question_data['data'])

        if 'solution' in question_data and isinstance(question_data['solution'], dict):
            question_data['solution'] = json.dumps(question_data['solution'])

        return insert_returning('exam_questions', question_data, '*')

    @classmethod
    def bulk_create_questions(cls, questions: List[Dict[str, Any]]) -> bool:
        """
        Bulk create exam questions (for AI-generated exams)

        Args:
            questions: List of question data dictionaries

        Returns:
            bool: True if all created successfully
        """
        try:
            for question_data in questions:
                cls.create_question(question_data)
            return True
        except Exception as e:
            print(f"Error bulk creating questions: {e}")
            return False

    @classmethod
    def update_question(cls, question_id: str, update_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Update exam question

        Args:
            question_id: Question UUID
            update_data: Dictionary with fields to update

        Returns:
            Updated question record
        """
        # Ensure JSONB fields are properly formatted
        if 'data' in update_data and isinstance(update_data['data'], dict):
            update_data['data'] = json.dumps(update_data['data'])

        if 'solution' in update_data and isinstance(update_data['solution'], dict):
            update_data['solution'] = json.dumps(update_data['solution'])

        where = "question_id = %s"
        return update_returning('exam_questions', update_data, where, (question_id,), '*')

    @classmethod
    def delete_question(cls, question_id: str) -> bool:
        """
        Delete exam question

        Args:
            question_id: Question UUID

        Returns:
            bool: True if deleted successfully
        """
        where = "question_id = %s"
        result = delete_returning('exam_questions', where, (question_id,), 'question_id')
        return result is not None

    @classmethod
    def reorder_questions(cls, exam_id: str, question_orders: List[Dict[str, Any]]) -> bool:
        """
        Reorder questions in an exam

        Args:
            exam_id: Exam UUID
            question_orders: List of {'question_id': UUID, 'order_index': int}

        Returns:
            bool: True if reordered successfully
        """
        try:
            for item in question_orders:
                where = "question_id = %s AND exam_id = %s"
                update_returning(
                    'exam_questions',
                    {'order_index': item['order_index']},
                    where,
                    (item['question_id'], exam_id),
                    'question_id'
                )
            return True
        except Exception as e:
            print(f"Error reordering questions: {e}")
            return False
