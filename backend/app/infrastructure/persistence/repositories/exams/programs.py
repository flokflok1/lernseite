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
        """List all registered exam programs."""
        return fetch_all("""
            SELECT program_id, program_key, display_name, program_type,
                   provider, description, icon, sort_order, created_at
            FROM assessments.exam_programs
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
    def delete_by_id(program_id: int) -> bool:
        """Delete a program by ID."""
        result = fetch_one(
            "DELETE FROM assessments.exam_programs WHERE program_id = %s RETURNING program_id",
            (program_id,),
        )
        return result is not None
