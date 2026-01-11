"""
Exam Repository (DB-First Architecture)

All exam data loaded dynamically from database.
NO hardcoded values or configurations.

Uses Repository Pattern with direct SQL (NO ORM).
"""

from typing import List, Optional, Dict, Any
from decimal import Decimal
import json
from src.infrastructure.database.base_repository import BaseRepository
from src.api.content.assessments.exams.domain.entities.exam import Exam


class ExamRepository(BaseRepository):
    """
    Exam repository for database access.

    ALL data loaded from database dynamically.
    NO hardcoded exam lists or configurations.
    """

    @staticmethod
    def find_by_id(exam_id: str) -> Optional[Exam]:
        """
        Find exam by ID.

        Args:
            exam_id: Exam UUID

        Returns:
            Exam entity or None
        """
        query = """
            SELECT
                exam_id, course_id, chapter_id, created_by, exam_type,
                title, description, instructions, duration_minutes,
                passing_score, total_points, randomize_questions,
                show_results_immediately, allow_review, max_attempts,
                settings, published, created_at, updated_at
            FROM assessments.exams
            WHERE exam_id = %s
        """
        row = ExamRepository.fetch_one(query, (exam_id,))

        if row:
            # Parse JSONB settings
            if row.get('settings'):
                row['settings'] = row['settings'] if isinstance(row['settings'], dict) else json.loads(row['settings'])
            return Exam(**row)
        return None

    @staticmethod
    def find_by_course_id(
        course_id: str,
        published_only: bool = False
    ) -> List[Exam]:
        """
        Find exams by course ID.

        Args:
            course_id: Course UUID
            published_only: Only return published exams

        Returns:
            List of exams
        """
        query = """
            SELECT
                exam_id, course_id, chapter_id, created_by, exam_type,
                title, description, instructions, duration_minutes,
                passing_score, total_points, randomize_questions,
                show_results_immediately, allow_review, max_attempts,
                settings, published, created_at, updated_at
            FROM assessments.exams
            WHERE course_id = %s
        """
        params = [course_id]

        if published_only:
            query += " AND published = TRUE"

        query += " ORDER BY created_at DESC"

        rows = ExamRepository.fetch_all(query, tuple(params))

        # Parse JSONB settings for each row
        for row in rows:
            if row.get('settings'):
                row['settings'] = row['settings'] if isinstance(row['settings'], dict) else json.loads(row['settings'])

        return [Exam(**row) for row in rows]

    @staticmethod
    def find_by_chapter_id(
        chapter_id: str,
        published_only: bool = False
    ) -> List[Exam]:
        """
        Find exams by chapter ID.

        Args:
            chapter_id: Chapter UUID
            published_only: Only return published exams

        Returns:
            List of exams
        """
        query = """
            SELECT
                exam_id, course_id, chapter_id, created_by, exam_type,
                title, description, instructions, duration_minutes,
                passing_score, total_points, randomize_questions,
                show_results_immediately, allow_review, max_attempts,
                settings, published, created_at, updated_at
            FROM assessments.exams
            WHERE chapter_id = %s
        """
        params = [chapter_id]

        if published_only:
            query += " AND published = TRUE"

        query += " ORDER BY created_at DESC"

        rows = ExamRepository.fetch_all(query, tuple(params))

        # Parse JSONB settings
        for row in rows:
            if row.get('settings'):
                row['settings'] = row['settings'] if isinstance(row['settings'], dict) else json.loads(row['settings'])

        return [Exam(**row) for row in rows]

    @staticmethod
    def find_all(
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        exam_type: Optional[str] = None,  # From DB, not hardcoded
        created_by: Optional[str] = None,
        published: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Exam]:
        """
        Find exams with dynamic filters.

        ALL filter values come from database or parameters.
        NO hardcoded filter lists.

        Args:
            course_id: Filter by course
            chapter_id: Filter by chapter
            exam_type: Filter by exam type (from DB)
            created_by: Filter by creator
            published: Filter by published status
            limit: Result limit
            offset: Result offset

        Returns:
            List of exam entities
        """
        query = """
            SELECT
                exam_id, course_id, chapter_id, created_by, exam_type,
                title, description, instructions, duration_minutes,
                passing_score, total_points, randomize_questions,
                show_results_immediately, allow_review, max_attempts,
                settings, published, created_at, updated_at
            FROM assessments.exams
            WHERE 1=1
        """
        params = []

        # Dynamic filters - NO hardcoded values
        if course_id:
            query += " AND course_id = %s"
            params.append(course_id)

        if chapter_id:
            query += " AND chapter_id = %s"
            params.append(chapter_id)

        if exam_type:
            query += " AND exam_type = %s"
            params.append(exam_type)

        if created_by:
            query += " AND created_by = %s"
            params.append(created_by)

        if published is not None:
            query += " AND published = %s"
            params.append(published)

        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        rows = ExamRepository.fetch_all(query, tuple(params))

        # Parse JSONB settings
        for row in rows:
            if row.get('settings'):
                row['settings'] = row['settings'] if isinstance(row['settings'], dict) else json.loads(row['settings'])

        return [Exam(**row) for row in rows]

    @staticmethod
    def create(exam: Exam) -> Exam:
        """
        Create new exam.

        Args:
            exam: Exam entity to create

        Returns:
            Created exam with DB-generated fields
        """
        query = """
            INSERT INTO assessments.exams (
                exam_id, course_id, chapter_id, created_by, exam_type,
                title, description, instructions, duration_minutes,
                passing_score, total_points, randomize_questions,
                show_results_immediately, allow_review, max_attempts,
                settings, published, created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
            )
            RETURNING
                exam_id, course_id, chapter_id, created_by, exam_type,
                title, description, instructions, duration_minutes,
                passing_score, total_points, randomize_questions,
                show_results_immediately, allow_review, max_attempts,
                settings, published, created_at, updated_at
        """

        # Convert settings dict to JSONB
        settings_json = json.dumps(exam.settings) if exam.settings else None

        params = (
            exam.exam_id,
            exam.course_id,
            exam.chapter_id,
            exam.created_by,
            exam.exam_type,
            exam.title,
            exam.description,
            exam.instructions,
            exam.duration_minutes,
            exam.passing_score,
            exam.total_points,
            exam.randomize_questions,
            exam.show_results_immediately,
            exam.allow_review,
            exam.max_attempts,
            settings_json,
            exam.published,
        )

        row = ExamRepository.execute_returning(query, params)

        if row:
            # Parse JSONB settings
            if row.get('settings'):
                row['settings'] = row['settings'] if isinstance(row['settings'], dict) else json.loads(row['settings'])
            return Exam(**row)
        return exam

    @staticmethod
    def update(exam: Exam) -> Exam:
        """
        Update existing exam.

        Args:
            exam: Exam entity with updates

        Returns:
            Updated exam
        """
        query = """
            UPDATE assessments.exams SET
                title = %s,
                description = %s,
                instructions = %s,
                duration_minutes = %s,
                passing_score = %s,
                total_points = %s,
                randomize_questions = %s,
                show_results_immediately = %s,
                allow_review = %s,
                max_attempts = %s,
                settings = %s,
                published = %s,
                updated_at = NOW()
            WHERE exam_id = %s
            RETURNING
                exam_id, course_id, chapter_id, created_by, exam_type,
                title, description, instructions, duration_minutes,
                passing_score, total_points, randomize_questions,
                show_results_immediately, allow_review, max_attempts,
                settings, published, created_at, updated_at
        """

        # Convert settings dict to JSONB
        settings_json = json.dumps(exam.settings) if exam.settings else None

        params = (
            exam.title,
            exam.description,
            exam.instructions,
            exam.duration_minutes,
            exam.passing_score,
            exam.total_points,
            exam.randomize_questions,
            exam.show_results_immediately,
            exam.allow_review,
            exam.max_attempts,
            settings_json,
            exam.published,
            exam.exam_id,
        )

        row = ExamRepository.execute_returning(query, params)

        if row:
            # Parse JSONB settings
            if row.get('settings'):
                row['settings'] = row['settings'] if isinstance(row['settings'], dict) else json.loads(row['settings'])
            return Exam(**row)
        return exam

    @staticmethod
    def delete(exam_id: str) -> bool:
        """
        Delete exam (hard delete - cascade to questions and attempts).

        Args:
            exam_id: Exam UUID

        Returns:
            True if deleted
        """
        query = """
            DELETE FROM assessments.exams
            WHERE exam_id = %s
        """
        affected = ExamRepository.execute(query, (exam_id,))
        return affected > 0

    @staticmethod
    def count(
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        exam_type: Optional[str] = None,
        published: Optional[bool] = None
    ) -> int:
        """
        Count exams with dynamic filters.

        Args:
            course_id: Filter by course
            chapter_id: Filter by chapter
            exam_type: Filter by exam type
            published: Filter by published status

        Returns:
            Exam count
        """
        query = "SELECT COUNT(*) as count FROM assessments.exams WHERE 1=1"
        params = []

        if course_id:
            query += " AND course_id = %s"
            params.append(course_id)

        if chapter_id:
            query += " AND chapter_id = %s"
            params.append(chapter_id)

        if exam_type:
            query += " AND exam_type = %s"
            params.append(exam_type)

        if published is not None:
            query += " AND published = %s"
            params.append(published)

        row = ExamRepository.fetch_one(query, tuple(params))
        return row['count'] if row else 0

    @staticmethod
    def get_available_exam_types() -> List[str]:
        """
        Get available exam types from database constraint.

        Returns:
            List of valid exam types from DB
        """
        # Query PostgreSQL constraint to get valid exam types
        query = """
            SELECT
                UNNEST(
                    STRING_TO_ARRAY(
                        SUBSTRING(
                            pg_get_constraintdef(c.oid)
                            FROM '\\(exam_type\\)::\\w+\\s*=\\s*ANY\\s*\\(ARRAY\\[(.*)\\]'
                        ),
                        ','
                    )
                ) AS exam_type
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            JOIN pg_namespace n ON t.relnamespace = n.oid
            WHERE c.conname = 'chk_exam_type'
            AND n.nspname = 'assessments'
            AND t.relname = 'exams'
        """

        rows = ExamRepository.fetch_all(query, ())

        if rows:
            # Clean up the values (remove quotes and whitespace)
            return [row['exam_type'].strip().strip("'\"") for row in rows]

        # Fallback: query actual distinct values in table
        fallback_query = """
            SELECT DISTINCT exam_type
            FROM assessments.exams
            ORDER BY exam_type
        """
        fallback_rows = ExamRepository.fetch_all(fallback_query, ())
        return [row['exam_type'] for row in fallback_rows]
