"""
ExamTypeRegistry Repository

CRUD for exam type configurations (FI_AP1, AWS_SAA_C03, etc.).
All queries use parameterized SQL (%s) via psycopg3.
"""

import json
from typing import Optional, List, Dict, Any

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)


class ExamTypeRegistryRepository:
    """Repository for assessments.exam_type_registry table."""

    @staticmethod
    def find_all() -> List[Dict[str, Any]]:
        """List all registered exam types."""
        return fetch_all("""
            SELECT exam_type, display_name, passing_score, parts, settings,
                   program_id, applies_to, sort_order, archive_folder_id, created_at
            FROM assessments.exam_type_registry
            ORDER BY sort_order, exam_type
        """)

    @staticmethod
    def find_by_type(exam_type: str) -> Optional[Dict[str, Any]]:
        """Find a single exam type by key."""
        return fetch_one("""
            SELECT exam_type, display_name, passing_score, parts, settings,
                   program_id, applies_to, sort_order, archive_folder_id, created_at
            FROM assessments.exam_type_registry
            WHERE exam_type = %s
        """, (exam_type,))

    @staticmethod
    def find_by_program(program_id: int) -> List[Dict[str, Any]]:
        """Find all exam types for a program, with published exam/question counts."""
        return fetch_all("""
            SELECT etr.exam_type, etr.display_name, etr.passing_score,
                   etr.parts, etr.settings, etr.program_id, etr.applies_to,
                   etr.sort_order, etr.archive_folder_id, etr.created_at,
                   COUNT(DISTINCT e.exam_id)       AS exam_count,
                   COUNT(DISTINCT eq.question_id)  AS question_count
            FROM assessments.exam_type_registry etr
            LEFT JOIN assessments.exams e
                ON e.exam_type_key = etr.exam_type AND e.published = true
            LEFT JOIN assessments.exam_questions eq
                ON eq.exam_id = e.exam_id
            WHERE etr.program_id = %s
            GROUP BY etr.exam_type, etr.display_name, etr.passing_score,
                     etr.parts, etr.settings, etr.program_id, etr.applies_to,
                     etr.sort_order, etr.archive_folder_id, etr.created_at
            ORDER BY etr.sort_order, etr.exam_type
        """, (program_id,))

    @staticmethod
    def create(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new exam type."""
        return fetch_one("""
            INSERT INTO assessments.exam_type_registry
                (exam_type, display_name, passing_score, parts, settings,
                 program_id, applies_to, sort_order, archive_folder_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
        """, (
            data['exam_type'],
            json.dumps(data.get('display_name', {})),
            data.get('passing_score', 50),
            json.dumps(data.get('parts')) if data.get('parts') else None,
            json.dumps(data.get('settings')) if data.get('settings') else None,
            data.get('program_id'),
            data.get('applies_to', []),
            data.get('sort_order', 0),
            data.get('archive_folder_id'),
        ))

    @staticmethod
    def update(exam_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing exam type."""
        sets, params = [], []
        if 'display_name' in data:
            sets.append('display_name = %s')
            params.append(json.dumps(data['display_name']))
        if 'passing_score' in data:
            sets.append('passing_score = %s')
            params.append(data['passing_score'])
        if 'parts' in data:
            sets.append('parts = %s')
            params.append(json.dumps(data['parts']) if data['parts'] else None)
        if 'settings' in data:
            sets.append('settings = %s')
            params.append(json.dumps(data['settings']) if data['settings'] else None)
        if 'program_id' in data:
            sets.append('program_id = %s')
            params.append(data['program_id'])
        if 'applies_to' in data:
            sets.append('applies_to = %s')
            params.append(data['applies_to'])
        if 'sort_order' in data:
            sets.append('sort_order = %s')
            params.append(data['sort_order'])
        if 'archive_folder_id' in data:
            sets.append('archive_folder_id = %s')
            params.append(data['archive_folder_id'])
        if not sets:
            return ExamTypeRegistryRepository.find_by_type(exam_type)
        params.append(exam_type)
        return fetch_one(f"""
            UPDATE assessments.exam_type_registry
            SET {', '.join(sets)}
            WHERE exam_type = %s
            RETURNING *
        """, tuple(params))

    @staticmethod
    def has_dependent_exams(exam_type: str) -> bool:
        """Return True if any exams or sessions reference this exam type."""
        if fetch_one(
            "SELECT 1 FROM assessments.exams WHERE exam_type_key = %s LIMIT 1",
            (exam_type,),
        ):
            return True
        return fetch_one(
            "SELECT 1 FROM assessments.exam_sessions WHERE exam_type_key = %s LIMIT 1",
            (exam_type,),
        ) is not None

    @staticmethod
    def delete(exam_type: str) -> bool:
        """Hard-delete an exam type (only call after has_dependent_exams() check)."""
        execute_query(
            "DELETE FROM assessments.exam_type_registry WHERE exam_type = %s",
            (exam_type,),
        )
        return True
