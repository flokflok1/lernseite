"""
ExamRegion Repository

CRUD for exam regions (bayern, nrw, etc.).
All queries use parameterized SQL (%s) via psycopg3.
"""

import json
from typing import Optional, List, Dict, Any

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)


class ExamRegionRepository:
    """Repository for assessments.exam_regions table."""

    @staticmethod
    def find_all() -> List[Dict[str, Any]]:
        """List all exam regions."""
        return fetch_all(
            "SELECT region_code, display_name "
            "FROM assessments.exam_regions ORDER BY region_code",
        )

    @staticmethod
    def find_by_code(region_code: str) -> Optional[Dict[str, Any]]:
        """Find a single region by code."""
        return fetch_one(
            "SELECT region_code, display_name "
            "FROM assessments.exam_regions WHERE region_code = %s",
            (region_code,),
        )

    @staticmethod
    def create(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new exam region."""
        return fetch_one(
            "INSERT INTO assessments.exam_regions (region_code, display_name) "
            "VALUES (%s, %s) RETURNING *",
            (data['region_code'], json.dumps(data.get('display_name', {}))),
        )

    @staticmethod
    def update(region_code: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a region's display_name."""
        if 'display_name' not in data:
            return ExamRegionRepository.find_by_code(region_code)
        return fetch_one(
            "UPDATE assessments.exam_regions SET display_name = %s "
            "WHERE region_code = %s RETURNING *",
            (json.dumps(data['display_name']), region_code),
        )

    @staticmethod
    def delete(region_code: str) -> bool:
        """Delete a region. Returns True if deleted."""
        execute_query(
            "DELETE FROM assessments.exam_regions WHERE region_code = %s",
            (region_code,),
        )
        return True
