"""
ExamProgramRepository — CRUD for assessments.exam_programs.

Manages the parent-level exam programs (Beruf/Zertifizierung) that group
exam type registry entries (Prüfungsteile) hierarchically.
"""
import json
from typing import Optional, List, Dict, Any

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)


class ExamProgramRepository:
    """Repository for the assessments.exam_programs table."""

    @staticmethod
    def find_all() -> List[Dict[str, Any]]:
        """List all active (non-trashed) exam programs."""
        return fetch_all("""
            SELECT program_id, program_key, display_name, program_type,
                   provider, description, icon, sort_order, created_at
            FROM assessments.exam_programs
            WHERE trashed_at IS NULL
            ORDER BY sort_order, program_key
        """)

    @staticmethod
    def find_by_key(program_key: str) -> Optional[Dict[str, Any]]:
        """Find a single program by key."""
        return fetch_one("""
            SELECT program_id, program_key, display_name, program_type,
                   provider, description, icon, sort_order, created_at
            FROM assessments.exam_programs
            WHERE program_key = %s
        """, (program_key,))

    @staticmethod
    def find_with_parts() -> List[Dict[str, Any]]:
        """Return all programs with their exam parts nested."""
        programs = fetch_all("""
            SELECT program_id, program_key, display_name, program_type,
                   provider, icon, sort_order
            FROM assessments.exam_programs
            ORDER BY sort_order, program_key
        """)
        if not programs:
            return []

        parts = fetch_all("""
            SELECT exam_type, display_name, passing_score, program_id,
                   applies_to, sort_order, parts, settings
            FROM assessments.exam_type_registry
            WHERE program_id IS NOT NULL
            ORDER BY sort_order, exam_type
        """)

        parts_by_program: Dict[int, list] = {}
        for p in parts:
            pid = p['program_id']
            parts_by_program.setdefault(pid, []).append(p)

        for prog in programs:
            prog['parts'] = parts_by_program.get(prog['program_id'], [])

        return programs

    @staticmethod
    def create(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new exam program."""
        return fetch_one("""
            INSERT INTO assessments.exam_programs
                (program_key, display_name, program_type, provider,
                 description, icon, sort_order)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            data['program_key'],
            json.dumps(data.get('display_name', {})),
            data.get('program_type', 'custom'),
            data.get('provider'),
            json.dumps(data.get('description')) if data.get('description') else None,
            data.get('icon'),
            data.get('sort_order', 0),
        ))

    @staticmethod
    def update(program_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a program's display fields."""
        sets = []
        params = []
        if 'display_name' in data:
            sets.append("display_name = %s")
            params.append(json.dumps(data['display_name']))
        if 'icon' in data:
            sets.append("icon = %s")
            params.append(data['icon'])
        if 'program_type' in data:
            sets.append("program_type = %s")
            params.append(data['program_type'])
        if 'provider' in data:
            sets.append("provider = %s")
            params.append(data['provider'])
        if 'sort_order' in data:
            sets.append("sort_order = %s")
            params.append(data['sort_order'])
        if not sets:
            return None
        params.append(program_id)
        return fetch_one(f"""
            UPDATE assessments.exam_programs
            SET {', '.join(sets)}
            WHERE program_id = %s
            RETURNING *
        """, tuple(params))

    @staticmethod
    def delete(program_key: str) -> bool:
        """Delete a program by key."""
        execute_query(
            "DELETE FROM assessments.exam_programs WHERE program_key = %s",
            (program_key,),
        )
        return True

    @staticmethod
    def trash_by_id(program_id: int) -> bool:
        """Soft-delete a program (move to trash)."""
        result = fetch_one("""
            UPDATE assessments.exam_programs
            SET trashed_at = NOW()
            WHERE program_id = %s AND trashed_at IS NULL
            RETURNING program_id
        """, (program_id,))
        return result is not None

    @staticmethod
    def restore_by_id(program_id: int) -> bool:
        """Restore a program from trash."""
        result = fetch_one("""
            UPDATE assessments.exam_programs
            SET trashed_at = NULL
            WHERE program_id = %s AND trashed_at IS NOT NULL
            RETURNING program_id
        """, (program_id,))
        return result is not None

    @staticmethod
    def purge_by_id(program_id: int) -> bool:
        """Permanently delete a trashed program."""
        result = fetch_one(
            "DELETE FROM assessments.exam_programs WHERE program_id = %s AND trashed_at IS NOT NULL RETURNING program_id",
            (program_id,),
        )
        return result is not None

    @staticmethod
    def find_trashed() -> List[Dict[str, Any]]:
        """Get all trashed programs."""
        return fetch_all("""
            SELECT program_id, program_key, display_name, icon, trashed_at
            FROM assessments.exam_programs
            WHERE trashed_at IS NOT NULL
            ORDER BY trashed_at DESC
        """)

    @staticmethod
    def find_enrolled_programs(user_id: str) -> List[Dict[str, Any]]:
        """Get programs a user is enrolled in, with per-program stats."""
        return fetch_all("""
            SELECT
                ep.program_id, ep.program_key, ep.display_name,
                ep.program_type, ep.provider, ep.icon, ep.sort_order,
                pt.display_name AS type_display_name,
                (SELECT count(DISTINCT eq.question_id)
                 FROM assessments.exam_questions eq
                 JOIN assessments.exams e ON e.exam_id = eq.exam_id
                 JOIN assessments.exam_type_registry etr ON etr.exam_type = e.exam_type_key
                 WHERE etr.program_id = ep.program_id
                   AND e.analysis_status = 'ready' AND e.published = true
                ) AS total_questions,
                (SELECT count(DISTINCT uqs.question_id)
                 FROM assessments.user_question_stats uqs
                 JOIN assessments.exam_questions eq2 ON eq2.question_id = uqs.question_id
                 JOIN assessments.exams e3 ON e3.exam_id = eq2.exam_id
                 JOIN assessments.exam_type_registry etr3 ON etr3.exam_type = e3.exam_type_key
                 WHERE uqs.user_id = %s AND etr3.program_id = ep.program_id
                ) AS seen_questions,
                (SELECT count(DISTINCT uqs2.question_id)
                 FROM assessments.user_question_stats uqs2
                 JOIN assessments.exam_questions eq3 ON eq3.question_id = uqs2.question_id
                 JOIN assessments.exams e4 ON e4.exam_id = eq3.exam_id
                 JOIN assessments.exam_type_registry etr4 ON etr4.exam_type = e4.exam_type_key
                 WHERE uqs2.user_id = %s AND etr4.program_id = ep.program_id
                   AND uqs2.times_correct > 0
                   AND uqs2.times_correct::float / GREATEST(uqs2.times_seen, 1) >= 0.5
                ) AS mastered_questions,
                (SELECT count(DISTINCT e2.exam_id)
                 FROM assessments.exams e2
                 JOIN assessments.exam_type_registry etr2 ON etr2.exam_type = e2.exam_type_key
                 WHERE etr2.program_id = ep.program_id
                   AND e2.analysis_status = 'ready' AND e2.published = true
                ) AS exam_count,
                etr_main.course_id
            FROM assessments.user_program_enrollments upe
            JOIN assessments.exam_programs ep ON ep.program_id = upe.program_id
            LEFT JOIN assessments.program_types pt ON pt.type_key = ep.program_type
            LEFT JOIN LATERAL (
                SELECT course_id FROM assessments.exam_type_registry
                WHERE program_id = ep.program_id AND course_id IS NOT NULL
                ORDER BY sort_order LIMIT 1
            ) etr_main ON true
            WHERE upe.user_id = %s AND ep.trashed_at IS NULL
            ORDER BY ep.sort_order, ep.program_key
        """, (user_id, user_id, user_id))

    @staticmethod
    def enroll_user(user_id: str, program_id: int) -> bool:
        """Enroll a user in a program."""
        result = fetch_one("""
            INSERT INTO assessments.user_program_enrollments (user_id, program_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            RETURNING user_id
        """, (user_id, program_id))
        return result is not None

    @staticmethod
    def unenroll_user(user_id: str, program_id: int) -> bool:
        """Remove a user's enrollment."""
        execute_query(
            "DELETE FROM assessments.user_program_enrollments WHERE user_id = %s AND program_id = %s",
            (user_id, program_id),
        )
        return True

    @staticmethod
    def find_available_programs() -> List[Dict[str, Any]]:
        """List all active programs for the catalog."""
        return fetch_all("""
            SELECT ep.program_id, ep.program_key, ep.display_name,
                   ep.program_type, ep.provider, ep.icon, ep.sort_order,
                   pt.display_name AS type_display_name
            FROM assessments.exam_programs ep
            LEFT JOIN assessments.program_types pt ON pt.type_key = ep.program_type
            WHERE ep.trashed_at IS NULL
            ORDER BY ep.sort_order, ep.program_key
        """)
