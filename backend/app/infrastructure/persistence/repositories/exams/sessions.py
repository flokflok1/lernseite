"""
ExamSessionRepository — Grouped session queries for exam archive.

Handles hierarchical exam structure:
  exam_type_registry -> exam_regions -> exam_sessions -> exams

Uses static methods with fetch_one/fetch_all helpers (project convention).
"""

from typing import Dict, Any, Optional, List

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, insert_returning
)


class ExamSessionRepository:
    """Repository for assessments.exam_sessions."""

    @staticmethod
    def find_sessions_grouped(
        program_key: str = None,
    ) -> List[Dict[str, Any]]:
        """Grouped query: program -> region -> exam_type -> sessions.

        Returns rows with program info, region, exam type, session info,
        and per-session aggregates. The API layer groups these into:
          program -> region -> exam_type -> (year + season) sessions
        """
        query = """
            SELECT p.program_key, p.display_name AS program_name,
                   p.provider, p.icon, p.sort_order AS program_sort,
                   s.region, reg.display_name AS region_name,
                   r.exam_type, r.display_name AS type_display_name,
                   r.sort_order AS type_sort,
                   s.session_id, s.year, s.season,
                   COUNT(e.exam_id) AS exam_count,
                   COUNT(e.exam_id) FILTER (
                       WHERE e.analysis_status = 'ready'
                   ) AS ready_count,
                   SUM(COALESCE(eq.q_count, 0)) AS total_questions
            FROM assessments.exam_sessions s
            JOIN assessments.exam_type_registry r
                ON r.exam_type = s.exam_type_key
            LEFT JOIN assessments.exam_programs p
                ON p.program_id = r.program_id
            LEFT JOIN assessments.exam_regions reg
                ON reg.region_code = s.region
            LEFT JOIN assessments.exams e
                ON e.session_id = s.session_id
            LEFT JOIN LATERAL (
                SELECT COUNT(*) AS q_count
                FROM assessments.exam_questions q
                WHERE q.exam_id = e.exam_id
            ) eq ON TRUE
        """
        params: List = []
        if program_key:
            query += " WHERE p.program_key = %s"
            params.append(program_key)

        query += """
            GROUP BY p.program_key, p.display_name, p.provider, p.icon,
                     p.sort_order, s.region, reg.display_name,
                     r.exam_type, r.display_name,
                     r.sort_order, s.session_id, s.year, s.season
            ORDER BY p.sort_order, s.region, r.sort_order,
                     s.year DESC, s.season DESC
        """
        return fetch_all(query, params)

    @staticmethod
    def find_or_create(
        exam_type_key: str,
        region: str,
        year: int,
        season: str,
    ) -> Dict[str, Any]:
        """Find existing session or create a new one (upsert)."""
        region = (region or 'alle').lower()
        season = season.lower()

        existing = fetch_one(
            """SELECT * FROM assessments.exam_sessions
               WHERE exam_type_key = %s AND region = %s
                 AND year = %s AND season = %s""",
            [exam_type_key, region, year, season],
        )
        if existing:
            return existing

        return insert_returning(
            'assessments.exam_sessions',
            {
                'exam_type_key': exam_type_key,
                'region': region,
                'year': year,
                'season': season,
            },
            'session_id, exam_type_key, region, year, season',
        )

    @staticmethod
    def find_by_id(session_id: str) -> Optional[Dict[str, Any]]:
        return fetch_one(
            "SELECT * FROM assessments.exam_sessions WHERE session_id = %s",
            [session_id],
        )

    @staticmethod
    def update_tags(
        session_id: str, tags: List[str],
    ) -> Optional[Dict[str, Any]]:
        return fetch_one(
            """UPDATE assessments.exam_sessions
               SET tags = %s, updated_at = NOW()
               WHERE session_id = %s RETURNING *""",
            [tags, session_id],
        )

    @staticmethod
    def find_exams_by_session(
        session_id: str,
    ) -> List[Dict[str, Any]]:
        """All exams in a session with question counts."""
        return fetch_all(
            """SELECT e.exam_id, e.title, e.part,
                      e.analysis_status, e.upload_source,
                      e.uploaded_by,
                      COUNT(q.question_id) AS question_count
               FROM assessments.exams e
               LEFT JOIN assessments.exam_questions q
                   ON q.exam_id = e.exam_id
               WHERE e.session_id = %s
               GROUP BY e.exam_id
               ORDER BY e.part NULLS LAST""",
            [session_id],
        )

    @staticmethod
    def find_all_regions() -> List[Dict[str, Any]]:
        return fetch_all(
            "SELECT * FROM assessments.exam_regions ORDER BY region_code",
            [],
        )

    @staticmethod
    def find_type_display_name(
        exam_type_key: str,
    ) -> Optional[Dict[str, Any]]:
        """Look up display_name for an exam type from registry."""
        return fetch_one(
            """SELECT display_name FROM assessments.exam_type_registry
               WHERE exam_type = %s""",
            [exam_type_key],
        )

    @staticmethod
    def find_region_display_name(
        region_code: str,
    ) -> Optional[Dict[str, Any]]:
        """Look up display_name for a region."""
        return fetch_one(
            """SELECT display_name FROM assessments.exam_regions
               WHERE region_code = %s""",
            [region_code],
        )

    @staticmethod
    def delete_session(session_id: str) -> bool:
        """Delete an empty session. Returns False if exams exist."""
        count = fetch_one(
            "SELECT COUNT(*) AS cnt FROM assessments.exams WHERE session_id = %s",
            [session_id],
        )
        if count and count['cnt'] > 0:
            return False
        from app.infrastructure.persistence.database.connection import (
            execute_query,
        )
        execute_query(
            "DELETE FROM assessments.exam_sessions WHERE session_id = %s",
            [session_id],
        )
        return True

    @staticmethod
    def move_exam(
        exam_id: str, target_session_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Move an exam to a different session."""
        return fetch_one(
            """UPDATE assessments.exams
               SET session_id = %s, updated_at = NOW()
               WHERE exam_id = %s RETURNING exam_id, session_id""",
            [target_session_id, exam_id],
        )

    @staticmethod
    def delete_exam(exam_id: str) -> bool:
        """Delete an exam and its questions."""
        from app.infrastructure.persistence.database.connection import (
            execute_query,
        )
        execute_query(
            "DELETE FROM assessments.exam_questions WHERE exam_id = %s",
            [exam_id],
        )
        execute_query(
            "DELETE FROM assessments.exams WHERE exam_id = %s",
            [exam_id],
        )
        return True
