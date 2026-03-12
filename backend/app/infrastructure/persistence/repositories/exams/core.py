"""
LernsystemX Exam Repository

Data access layer for exam management:
- CRUD operations for exams
- Exam listing with filters
- AI-generated exam tracking

ExamQuestionRepository has been split to questions.py (G01).
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from app.infrastructure.persistence.repositories.core.base import BaseRepository
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
                Archive columns (optional):
                - semester (str) - e.g. "Sommer 2024"
                - year (int)
                - season (str) - "sommer" or "winter"
                - part (str) - e.g. "GA1", "GA2", "WK"
                - region (str) - e.g. "bw"
                - profession (str) - e.g. "FISI"
                - pdf_path (str) - filesystem path to PDF
                - solution_pdf_path (str) - path to solution PDF
                - analysis_status (str) - "pending", "processing", "done", "error"
                - raw_text (str) - extracted PDF text

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

    @classmethod
    def find_by_pdf_path(cls, pdf_path: str) -> Optional[Dict]:
        """
        Find exam by its PDF filesystem path (for duplicate detection)

        Args:
            pdf_path: Absolute path to the PDF file

        Returns:
            Exam record or None
        """
        query = """
            SELECT * FROM assessments.exams
            WHERE pdf_path = %s
            LIMIT 1
        """
        return fetch_one(query, (pdf_path,))

    @classmethod
    def find_archive_exams(
        cls, status: Optional[str] = None
    ) -> List[Dict]:
        """
        Find all real (archived) exams, optionally filtered by status

        Args:
            status: Optional analysis_status filter

        Returns:
            List of archive exam records with question counts
        """
        if status:
            query = """
                SELECT e.*,
                       COUNT(eq.question_id) as question_count
                FROM assessments.exams e
                LEFT JOIN assessments.exam_questions eq
                    ON e.exam_id = eq.exam_id
                WHERE e.exam_type = 'real'
                  AND e.analysis_status = %s
                GROUP BY e.exam_id
                ORDER BY e.year DESC NULLS LAST, e.season
            """
            return fetch_all(query, (status,))
        else:
            query = """
                SELECT e.*,
                       COUNT(eq.question_id) as question_count
                FROM assessments.exams e
                LEFT JOIN assessments.exam_questions eq
                    ON e.exam_id = eq.exam_id
                WHERE e.exam_type = 'real'
                GROUP BY e.exam_id
                ORDER BY e.year DESC NULLS LAST, e.season
            """
            return fetch_all(query)

    @classmethod
    def update_analysis_status(
        cls, exam_id: str, status: str
    ) -> Optional[Dict]:
        """
        Update the analysis status of an archived exam

        Args:
            exam_id: Exam UUID
            status: New status ("pending", "processing", "done", "error")

        Returns:
            Updated exam record
        """
        return cls.update_exam(exam_id, {
            'analysis_status': status
        })


    @classmethod
    def find_simulation_exam_ids(
        cls, exam_type_key: str, region: str, limit: int = 6,
    ) -> List[str]:
        """Find distinct ready exam IDs for simulation chapters.

        Returns the most recent exams first (by session year/season)
        so simulations reflect current exam style.
        """
        query = """
            SELECT DISTINCT ON (e.exam_id)
                   e.exam_id, s.year, s.season
            FROM assessments.exams e
            LEFT JOIN assessments.exam_sessions s
                ON e.session_id = s.session_id
            WHERE e.analysis_status = 'ready'
              AND (s.exam_type_key = %s OR e.exam_type_key = %s)
              AND (
                  COALESCE(s.region, 'alle') = %s
                  OR COALESCE(s.region, 'alle') = 'alle'
              )
            ORDER BY e.exam_id, s.year DESC NULLS LAST
        """
        # Wrap to re-sort by year descending after DISTINCT ON
        outer = f"""
            SELECT sub.exam_id
            FROM ({query}) sub
            ORDER BY sub.year DESC NULLS LAST, sub.exam_id
            LIMIT %s
        """
        rows = fetch_all(
            outer, (exam_type_key, exam_type_key, region, limit),
        )
        return [str(r['exam_id']) for r in rows]



# ExamQuestionRepository moved to questions.py (G01 split)
