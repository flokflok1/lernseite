"""
UserExamGoals Repository

CRUD for user exam preparation goals.
Users can have multiple active goals simultaneously.
All queries use parameterized SQL (%s) via psycopg3.
"""

from typing import Optional, List, Dict, Any

from app.infrastructure.persistence.database.connection import (
    fetch_one, fetch_all, execute_query,
)


class UserExamGoalsRepository:
    """Repository for core.user_exam_goals table."""

    @staticmethod
    def find_by_user(user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all goals for a user, optionally filtered by status."""
        if status:
            query = """
                SELECT g.*, r.display_name, r.passing_score, r.parts
                FROM core.user_exam_goals g
                JOIN assessments.exam_type_registry r ON r.exam_type = g.exam_type
                WHERE g.user_id = %s AND g.status = %s
                ORDER BY g.created_at DESC
            """
            return fetch_all(query, (user_id, status))
        query = """
            SELECT g.*, r.display_name, r.passing_score, r.parts
            FROM core.user_exam_goals g
            JOIN assessments.exam_type_registry r ON r.exam_type = g.exam_type
            WHERE g.user_id = %s
            ORDER BY g.created_at DESC
        """
        return fetch_all(query, (user_id,))

    @staticmethod
    def find_active_exam_types(user_id: str) -> List[str]:
        """Get just the active exam_type keys for a user."""
        query = """
            SELECT exam_type
            FROM core.user_exam_goals
            WHERE user_id = %s AND status = 'active'
        """
        rows = fetch_all(query, (user_id,))
        return [r['exam_type'] for r in rows]

    @staticmethod
    def create(user_id: str, exam_type: str, target_date: Optional[str] = None,
               status: str = 'active') -> Optional[Dict[str, Any]]:
        """Create or upsert an exam goal for a user."""
        query = """
            INSERT INTO core.user_exam_goals (user_id, exam_type, status, target_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, exam_type) DO UPDATE
                SET status = EXCLUDED.status,
                    target_date = EXCLUDED.target_date,
                    updated_at = NOW()
            RETURNING *
        """
        return fetch_one(query, (user_id, exam_type, status, target_date))

    @staticmethod
    def update_status(goal_id: str, status: str) -> Optional[Dict[str, Any]]:
        """Update the status of a goal."""
        query = """
            UPDATE core.user_exam_goals
            SET status = %s, updated_at = NOW()
            WHERE goal_id = %s
            RETURNING *
        """
        return fetch_one(query, (status, goal_id))

    @staticmethod
    def delete(goal_id: str) -> bool:
        """Delete a goal."""
        query = "DELETE FROM core.user_exam_goals WHERE goal_id = %s"
        execute_query(query, (goal_id,))
        return True
