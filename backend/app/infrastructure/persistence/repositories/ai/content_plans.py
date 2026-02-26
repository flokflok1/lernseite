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

    JSONB_FIELDS = ('plan_data', 'course_meta', 'chapters', 'chat_history')

    @classmethod
    def _serialize_jsonb(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize dict/list values in JSONB columns to JSON strings."""
        result = dict(data)
        for field in cls.JSONB_FIELDS:
            if field in result and isinstance(result[field], (dict, list)):
                result[field] = json.dumps(result[field])
        return result

    @classmethod
    def create(cls, plan_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new content plan with optional wizard columns."""
        serialized = cls._serialize_jsonb(plan_data)
        return insert_returning(cls.table_name, serialized, returning='*')

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
    def update_phase(
        cls,
        plan_id: str,
        phase: int,
        phase_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Update current phase and associated JSONB fields.

        Only provided fields in phase_data are updated (course_meta,
        chapters, plan_data). Missing keys are left unchanged via COALESCE.
        """
        query = """
            UPDATE ai_pipeline.ai_content_plans
            SET current_phase = %s,
                course_meta = COALESCE(%s::jsonb, course_meta),
                chapters    = COALESCE(%s::jsonb, chapters),
                plan_data   = COALESCE(%s::jsonb, plan_data),
                updated_at  = NOW()
            WHERE plan_id = %s
            RETURNING *
        """
        data = phase_data or {}
        course_meta = json.dumps(data['course_meta']) if 'course_meta' in data else None
        chapters = json.dumps(data['chapters']) if 'chapters' in data else None
        plan_data = json.dumps(data['plan_data']) if 'plan_data' in data else None

        return fetch_one(query, (phase, course_meta, chapters, plan_data, plan_id))

    @classmethod
    def append_chat_message(
        cls, plan_id: str, message: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Append a chat message to the chat_history JSONB array."""
        query = """
            UPDATE ai_pipeline.ai_content_plans
            SET chat_history = chat_history || %s::jsonb,
                updated_at = NOW()
            WHERE plan_id = %s
            RETURNING *
        """
        return fetch_one(query, (json.dumps([message]), plan_id))

    @classmethod
    def delete(cls, plan_id: str) -> None:
        """Delete a draft plan."""
        execute_query(
            "DELETE FROM ai_pipeline.ai_content_plans WHERE plan_id = %s AND status = 'draft'",
            (plan_id,),
        )
