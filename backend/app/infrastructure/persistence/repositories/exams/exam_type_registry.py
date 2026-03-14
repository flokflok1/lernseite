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
        query = """
            SELECT exam_type, display_name, passing_score, parts, settings,
                   program_id, applies_to, sort_order, created_at
            FROM assessments.exam_type_registry
            ORDER BY sort_order, exam_type
        """
        return fetch_all(query)

    @staticmethod
    def find_by_type(exam_type: str) -> Optional[Dict[str, Any]]:
        """Find a single exam type by key."""
        query = """
            SELECT exam_type, display_name, passing_score, parts, settings,
                   program_id, applies_to, sort_order, created_at
            FROM assessments.exam_type_registry
            WHERE exam_type = %s
        """
        return fetch_one(query, (exam_type,))

    @staticmethod
    def find_by_program(program_id: int) -> List[Dict[str, Any]]:
        """Find all exam types belonging to a program."""
        return fetch_all("""
            SELECT exam_type, display_name, passing_score, parts, settings,
                   program_id, applies_to, sort_order, created_at
            FROM assessments.exam_type_registry
            WHERE program_id = %s
            ORDER BY sort_order, exam_type
        """, (program_id,))

    @staticmethod
    def create(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new exam type."""
        query = """
            INSERT INTO assessments.exam_type_registry
                (exam_type, display_name, passing_score, parts, settings)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING *
        """
        return fetch_one(query, (
            data['exam_type'],
            json.dumps(data.get('display_name', {})),
            data.get('passing_score', 50),
            json.dumps(data.get('parts')) if data.get('parts') else None,
            json.dumps(data.get('settings')) if data.get('settings') else None,
        ))

    @staticmethod
    def update(exam_type: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing exam type."""
        sets = []
        params = []
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
        if not sets:
            return ExamTypeRegistryRepository.find_by_type(exam_type)
        params.append(exam_type)
        query = f"""
            UPDATE assessments.exam_type_registry
            SET {', '.join(sets)}
            WHERE exam_type = %s
            RETURNING *
        """
        return fetch_one(query, tuple(params))

    @staticmethod
    def delete(exam_type: str) -> bool:
        """Delete an exam type. Returns True if deleted."""
        query = "DELETE FROM assessments.exam_type_registry WHERE exam_type = %s"
        execute_query(query, (exam_type,))
        return True
