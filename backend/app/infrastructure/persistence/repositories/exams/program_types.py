"""ProgramTypeRepository — CRUD for assessments.program_types."""
import json
from typing import List, Dict, Any, Optional

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)


class ProgramTypeRepository:
    """Repository for dynamic program type categories."""

    @staticmethod
    def find_all() -> List[Dict[str, Any]]:
        return fetch_all("""
            SELECT type_key, display_name, icon, sort_order, created_at
            FROM assessments.program_types
            ORDER BY sort_order, type_key
        """)

    @staticmethod
    def create(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return fetch_one("""
            INSERT INTO assessments.program_types
                (type_key, display_name, icon, sort_order)
            VALUES (%s, %s, %s, %s)
            RETURNING *
        """, (
            data['type_key'],
            json.dumps(data.get('display_name', {})),
            data.get('icon'),
            data.get('sort_order', 0),
        ))

    @staticmethod
    def update(type_key: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        sets, params = [], []
        if 'display_name' in data:
            sets.append("display_name = %s")
            params.append(json.dumps(data['display_name']))
        if 'icon' in data:
            sets.append("icon = %s")
            params.append(data['icon'])
        if 'sort_order' in data:
            sets.append("sort_order = %s")
            params.append(data['sort_order'])
        if not sets:
            return None
        params.append(type_key)
        return fetch_one(
            f"UPDATE assessments.program_types SET {', '.join(sets)} "
            f"WHERE type_key = %s RETURNING *",
            tuple(params),
        )

    @staticmethod
    def delete(type_key: str) -> bool:
        execute_query(
            "DELETE FROM assessments.program_types WHERE type_key = %s",
            (type_key,),
        )
        return True
