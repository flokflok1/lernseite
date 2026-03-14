"""
ExamQuestionRepository — CRUD + queries for exam_questions table.

Split from core.py per G01 (500 LOC limit).
"""

import logging
from typing import Optional, List, Dict, Any
import json

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    insert_returning,
    update_returning,
    delete_returning,
)

logger = logging.getLogger(__name__)


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
        """Find all questions for an exam, ordered by order_index."""
        query = """
            SELECT *
            FROM assessments.exam_questions
            WHERE exam_id = %s
            ORDER BY order_index ASC
        """
        return fetch_all(query, (exam_id,))

    @classmethod
    def create_question(cls, question_data: Dict[str, Any]) -> Optional[Dict]:
        """Create new exam question with auto-calculated order_index."""
        if 'order_index' not in question_data:
            max_order_query = """
                SELECT COALESCE(MAX(order_index), 0) as max_order
                FROM assessments.exam_questions
                WHERE exam_id = %s
            """
            result = fetch_one(max_order_query, (question_data['exam_id'],))
            question_data['order_index'] = result['max_order'] + 1 if result else 1

        if 'data' in question_data and isinstance(question_data['data'], dict):
            question_data['data'] = json.dumps(question_data['data'])

        if 'solution' in question_data and isinstance(question_data['solution'], dict):
            question_data['solution'] = json.dumps(question_data['solution'])

        return insert_returning('exam_questions', question_data, '*')

    @classmethod
    def bulk_create_questions(cls, questions: List[Dict[str, Any]]) -> bool:
        """Bulk create exam questions (for AI-generated exams)."""
        try:
            for question_data in questions:
                cls.create_question(question_data)
            return True
        except Exception:
            logger.exception("Error bulk creating questions")
            raise

    @classmethod
    def update_question(cls, question_id: str, update_data: Dict[str, Any]) -> Optional[Dict]:
        """Update exam question."""
        if 'data' in update_data and isinstance(update_data['data'], dict):
            update_data['data'] = json.dumps(update_data['data'])

        if 'solution' in update_data and isinstance(update_data['solution'], dict):
            update_data['solution'] = json.dumps(update_data['solution'])

        where = "question_id = %s"
        return update_returning('exam_questions', update_data, where, (question_id,), '*')

    @classmethod
    def delete_question(cls, question_id: str) -> bool:
        """Delete exam question."""
        where = "question_id = %s"
        result = delete_returning('exam_questions', where, (question_id,), 'question_id')
        return result is not None

    @classmethod
    def find_by_topics(cls, topics: List[str]) -> List[Dict]:
        """Find questions whose topics overlap with the given list (PostgreSQL &&)."""
        query = """
            SELECT eq.*, e.title as exam_title,
                   e.semester, e.year, e.season, e.part
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON eq.exam_id = e.exam_id
            WHERE eq.topics && %s
            ORDER BY e.year DESC NULLS LAST, eq.order_index
        """
        return fetch_all(query, (topics,))

    @classmethod
    def find_for_course_generation(
        cls, exam_type_key: str, region: str,
    ) -> List[Dict]:
        """
        Fetch all ready exam questions for a given type + region.
        Used by ExamCourseGeneratorService.preview().
        """
        base = """
            SELECT eq.question_id, eq.question_text, eq.question_type,
                   eq.points, eq.topics, eq.data, eq.solution_text,
                   eq.scenario_title, eq.scenario_text, eq.question_number,
                   e.year, e.season, e.part
            FROM assessments.exam_questions eq
            JOIN assessments.exams e ON eq.exam_id = e.exam_id
            LEFT JOIN assessments.exam_sessions s ON e.session_id = s.session_id
            WHERE e.analysis_status = 'ready'
              AND (s.exam_type_key = %s OR e.exam_type_key = %s)
        """
        order = " ORDER BY eq.topics, e.year DESC, eq.order_index"

        if region == 'alle':
            # "Alle Bundesländer" → return all questions regardless of region
            return fetch_all(
                base + order,
                (exam_type_key, exam_type_key),
            )

        # Specific region → match region or untagged ('alle')
        return fetch_all(
            base + """
              AND (
                  COALESCE(s.region, 'alle') = %s
                  OR COALESCE(s.region, 'alle') = 'alle'
              )
            """ + order,
            (exam_type_key, exam_type_key, region),
        )

    @classmethod
    def find_by_ids(cls, question_ids: List[str]) -> List[Dict]:
        """Load multiple questions by their IDs."""
        if not question_ids:
            return []
        placeholders = ', '.join(['%s'] * len(question_ids))
        return fetch_all(
            f"""SELECT q.question_id, q.question_text, q.question_type,
                       q.points, q.data, q.solution_text, q.question_number,
                       q.scenario_title, q.scenario_text,
                       COALESCE(q.topics, ARRAY[]::text[]) AS topics
                FROM assessments.exam_questions q
                WHERE q.question_id IN ({placeholders})""",
            question_ids,
        )

    @classmethod
    def find_by_difficulty(
        cls,
        exam_type_key: str,
        difficulty: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Find questions filtered by difficulty level.

        Args:
            exam_type_key: Exam type key (e.g. 'FI_AP1').
            difficulty: 'leicht', 'mittel', 'schwer', or None for mixed.
            limit: Optional max number of questions.

        Returns:
            List of question dicts.
        """
        difficulty_filter = ""
        params: List[Any] = [exam_type_key]

        if difficulty == 'leicht':
            difficulty_filter = "AND (q.difficulty IN ('easy', 'leicht') OR q.difficulty IS NULL)"
        elif difficulty == 'mittel':
            difficulty_filter = "AND q.difficulty IN ('medium', 'mittel')"
        elif difficulty == 'schwer':
            difficulty_filter = "AND q.difficulty IN ('hard', 'schwer')"

        limit_clause = ""
        if limit:
            limit_clause = "LIMIT %s"
            params.append(limit)

        return fetch_all(
            f"""SELECT q.question_id, q.question_number,
                       q.question_text, q.points, q.difficulty,
                       q.exam_id, e.part AS exam_part
                FROM assessments.exam_questions q
                JOIN assessments.exams e ON e.exam_id = q.exam_id
                WHERE e.exam_type_key = %s
                {difficulty_filter}
                ORDER BY RANDOM()
                {limit_clause}""",
            params,
        )

    @classmethod
    def reorder_questions(cls, exam_id: str, question_orders: List[Dict[str, Any]]) -> bool:
        """Reorder questions in an exam."""
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
        except Exception:
            logger.exception("Error reordering questions")
            raise
