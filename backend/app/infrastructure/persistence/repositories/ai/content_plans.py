"""
Content Plan Repository

Data access for AI content plans in the Unified AI Editor.
All queries target ai_pipeline.ai_content_plans.
"""

from typing import Optional, Dict, Any, List
import json

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query, insert_returning, update_returning
)


class ContentPlanRepository:
    """Repository for AI Content Plans (ai_pipeline.ai_content_plans)."""

    table_name = 'ai_pipeline.ai_content_plans'

    @classmethod
    def create(cls, plan_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new content plan."""
        if 'plan_data' in plan_data and isinstance(plan_data['plan_data'], (dict, list)):
            plan_data['plan_data'] = json.dumps(plan_data['plan_data'])
        return insert_returning(cls.table_name, plan_data, returning='*')

    @classmethod
    def find_by_id(cls, plan_id: str) -> Optional[Dict[str, Any]]:
        """Find a content plan by ID with generation count."""
        query = """
            SELECT p.*,
                   COALESCE(g.gen_count, 0) AS generation_count
            FROM ai_pipeline.ai_content_plans p
            LEFT JOIN (
                SELECT plan_id, COUNT(*) AS gen_count
                FROM ai_pipeline.ai_generation_log
                GROUP BY plan_id
            ) g ON g.plan_id = p.plan_id
            WHERE p.plan_id = %s
        """
        return fetch_one(query, (plan_id,))

    @classmethod
    def find_by_course(
        cls, course_id: str, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Find plans for a course, paginated."""
        query = """
            SELECT p.*,
                   COALESCE(g.gen_count, 0) AS generation_count
            FROM ai_pipeline.ai_content_plans p
            LEFT JOIN (
                SELECT plan_id, COUNT(*) AS gen_count
                FROM ai_pipeline.ai_generation_log
                GROUP BY plan_id
            ) g ON g.plan_id = p.plan_id
            WHERE p.course_id = %s
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """
        return fetch_all(query, (course_id, limit, offset))

    @classmethod
    def update_status(cls, plan_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update plan status."""
        return update_returning(
            cls.table_name,
            {'status': status, 'updated_at': 'NOW()'},
            'plan_id = %s',
            (plan_id,),
        )

    @classmethod
    def update_plan_data(
        cls, plan_id: str, plan_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update plan data (steps reorder, parameter changes)."""
        return update_returning(
            cls.table_name,
            {'plan_data': json.dumps(plan_data), 'updated_at': 'NOW()'},
            'plan_id = %s',
            (plan_id,),
        )

    @classmethod
    def update_token_count(
        cls, plan_id: str, actual_tokens: int
    ) -> Optional[Dict[str, Any]]:
        """Update actual token count after execution."""
        return update_returning(
            cls.table_name,
            {'actual_tokens': actual_tokens, 'updated_at': 'NOW()'},
            'plan_id = %s',
            (plan_id,),
        )

    @classmethod
    def delete(cls, plan_id: str) -> None:
        """Delete a draft plan."""
        execute_query(
            "DELETE FROM ai_pipeline.ai_content_plans WHERE plan_id = %s AND status = 'draft'",
            (plan_id,),
        )
