"""
Generation Log Repository

Data access for AI generation history in the Unified AI Editor.
All queries target ai_pipeline.ai_generation_log.
"""

from typing import Optional, Dict, Any, List
import json

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, insert_returning, update_returning
)


class GenerationLogRepository:
    """Repository for AI Generation Log (ai_pipeline.ai_generation_log)."""

    table_name = 'ai_pipeline.ai_generation_log'

    @classmethod
    def create(cls, log_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new generation log entry."""
        if 'output_content' in log_data and isinstance(log_data['output_content'], (dict, list)):
            log_data['output_content'] = json.dumps(log_data['output_content'])
        return insert_returning(cls.table_name, log_data, returning='*')

    @classmethod
    def find_by_id(cls, generation_id: str) -> Optional[Dict[str, Any]]:
        """Find a generation log entry by ID."""
        query = """
            SELECT * FROM ai_pipeline.ai_generation_log
            WHERE generation_id = %s
        """
        return fetch_one(query, (generation_id,))

    @classmethod
    def find_by_plan(cls, plan_id: str) -> List[Dict[str, Any]]:
        """Find all generations for a specific plan."""
        query = """
            SELECT * FROM ai_pipeline.ai_generation_log
            WHERE plan_id = %s
            ORDER BY created_at ASC
        """
        return fetch_all(query, (plan_id,))

    @classmethod
    def find_by_course(
        cls, course_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Find generation history for a course, paginated."""
        query = """
            SELECT * FROM ai_pipeline.ai_generation_log
            WHERE course_id = %s
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """
        return fetch_all(query, (course_id, limit, offset))

    @classmethod
    def find_by_skill(
        cls, skill_code: str, course_id: str
    ) -> List[Dict[str, Any]]:
        """Find generations filtered by skill code and course."""
        query = """
            SELECT * FROM ai_pipeline.ai_generation_log
            WHERE skill_code = %s AND course_id = %s
            ORDER BY created_at DESC
        """
        return fetch_all(query, (skill_code, course_id))

    @classmethod
    def update_status(
        cls, generation_id: str, status: str
    ) -> Optional[Dict[str, Any]]:
        """Update generation status."""
        return update_returning(
            cls.table_name,
            {'status': status},
            'generation_id = %s',
            (generation_id,),
        )
