"""
LernsystemX Runner Sessions Repository

Data access layer for runner session management.
Handles CRUD operations for runner_sessions table.

Note: Live session state is stored in Redis.
This repository handles persistent session metadata.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from app.infrastructure.persistence.repositories.core.base import BaseRepository
from app.infrastructure.persistence.database.connection import (
    fetch_one,
    fetch_all,
    insert_returning,
    update_returning
)


class RunnerSessionsRepository(BaseRepository):
    """
    Repository for learning_methods.runner_sessions table.

    Stores persistent metadata for runner sessions.
    Live state is managed via Redis (see RunnerStateManager).
    """

    table_name = "learning_methods.runner_sessions"
    pk_column = "session_id"

    @classmethod
    def find_by_id_str(cls, session_id: str) -> Optional[Dict]:
        """
        Find session by UUID string.

        Args:
            session_id: Session UUID as string

        Returns:
            Session dict or None
        """
        query = f"""
            SELECT * FROM {cls.table_name}
            WHERE session_id = %s::uuid
        """
        return fetch_one(query, (session_id,))

    @classmethod
    def find_by_id(cls, session_id: str) -> Optional[Dict]:
        """
        Alias for find_by_id_str.

        Compatibility wrapper for service layer consistency.
        """
        return cls.find_by_id_str(session_id)

    @classmethod
    def find_active_by_user(cls, user_id: str) -> List[Dict]:
        """
        Find all active sessions for a user.

        Args:
            user_id: User UUID

        Returns:
            List of active session dicts
        """
        query = f"""
            SELECT rs.*, rm.mode_code, rm.name as mode_name
            FROM {cls.table_name} rs
            JOIN learning_methods.runner_modes rm ON rs.mode_id = rm.mode_id
            WHERE rs.user_id = %s::uuid AND rs.status = 'active'
            ORDER BY rs.started_at DESC
        """
        return fetch_all(query, (user_id,))

    @classmethod
    def find_active_for_method(cls, user_id: str, method_id: str) -> Optional[Dict]:
        """
        Find active session for user and method (for resume).

        Args:
            user_id: User UUID
            method_id: Learning method instance UUID

        Returns:
            Active session dict or None
        """
        query = f"""
            SELECT rs.*, rm.mode_code, rm.name as mode_name
            FROM {cls.table_name} rs
            JOIN learning_methods.runner_modes rm ON rs.mode_id = rm.mode_id
            WHERE rs.user_id = %s::uuid
              AND rs.method_id = %s::uuid
              AND rs.status = 'active'
            ORDER BY rs.started_at DESC
            LIMIT 1
        """
        return fetch_one(query, (user_id, method_id))

    @classmethod
    def find_active_session(cls, user_id: str, method_id: str) -> Optional[Dict]:
        """
        Alias for find_active_for_method.

        Compatibility wrapper for service layer consistency.
        """
        return cls.find_active_for_method(user_id, method_id)

    @classmethod
    def create_session(cls, data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create new runner session.

        Args:
            data: Session data with:
                - method_id: Learning method instance UUID
                - user_id: User UUID
                - mode_id: Runner mode ID
                - course_id: Optional course UUID (for context)
                - chapter_id: Optional chapter UUID
                - features_active: Array of active feature codes
                - config: JSONB session configuration

        Returns:
            Created session dict with generated session_id
        """
        # Ensure required defaults
        session_data = {
            'status': 'active',
            'started_at': datetime.utcnow(),
            **data
        }

        return insert_returning(cls.table_name, session_data)

    @classmethod
    def update_heartbeat(cls, session_id: str) -> bool:
        """
        Update session heartbeat timestamp.

        Args:
            session_id: Session UUID

        Returns:
            True if updated
        """
        query = f"""
            UPDATE {cls.table_name}
            SET heartbeat_at = NOW()
            WHERE session_id = %s::uuid AND status = 'active'
            RETURNING session_id
        """
        result = fetch_one(query, (session_id,))
        return result is not None

    @classmethod
    def complete_session(
        cls,
        session_id: str,
        final_state: Dict[str, Any],
        score: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Mark session as completed with final results.

        Args:
            session_id: Session UUID
            final_state: Final state snapshot from Redis
            score: Optional computed score (0-100)

        Returns:
            Updated session dict
        """
        update_data = {
            'status': 'completed',
            'ended_at': datetime.utcnow(),
            'final_state': final_state,
            'score': score
        }

        query = f"""
            UPDATE {cls.table_name}
            SET status = %s,
                ended_at = %s,
                final_state = %s,
                score = %s,
                updated_at = NOW()
            WHERE session_id = %s::uuid
            RETURNING *
        """
        return fetch_one(query, (
            update_data['status'],
            update_data['ended_at'],
            update_data['final_state'],
            update_data['score'],
            session_id
        ))

    @classmethod
    def timeout_session(cls, session_id: str, final_state: Dict[str, Any]) -> Optional[Dict]:
        """
        Mark session as timed out.

        Args:
            session_id: Session UUID
            final_state: State at timeout

        Returns:
            Updated session dict
        """
        query = f"""
            UPDATE {cls.table_name}
            SET status = 'timed_out',
                ended_at = NOW(),
                final_state = %s,
                updated_at = NOW()
            WHERE session_id = %s::uuid
            RETURNING *
        """
        return fetch_one(query, (final_state, session_id))

    @classmethod
    def abandon_session(cls, session_id: str) -> Optional[Dict]:
        """
        Mark session as abandoned (user left without completing).

        Args:
            session_id: Session UUID

        Returns:
            Updated session dict
        """
        query = f"""
            UPDATE {cls.table_name}
            SET status = 'abandoned',
                ended_at = NOW(),
                updated_at = NOW()
            WHERE session_id = %s::uuid
            RETURNING *
        """
        return fetch_one(query, (session_id,))

    @classmethod
    def get_user_history(
        cls,
        user_id: str,
        method_id: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Get user's session history.

        Args:
            user_id: User UUID
            method_id: Optional filter by method
            limit: Max results

        Returns:
            List of session history dicts
        """
        if method_id:
            query = f"""
                SELECT rs.*, rm.mode_code, rm.name as mode_name
                FROM {cls.table_name} rs
                JOIN learning_methods.runner_modes rm ON rs.mode_id = rm.mode_id
                WHERE rs.user_id = %s::uuid AND rs.method_id = %s::uuid
                ORDER BY rs.started_at DESC
                LIMIT %s
            """
            return fetch_all(query, (user_id, method_id, limit))
        else:
            query = f"""
                SELECT rs.*, rm.mode_code, rm.name as mode_name
                FROM {cls.table_name} rs
                JOIN learning_methods.runner_modes rm ON rs.mode_id = rm.mode_id
                WHERE rs.user_id = %s::uuid
                ORDER BY rs.started_at DESC
                LIMIT %s
            """
            return fetch_all(query, (user_id, limit))

    @classmethod
    def get_method_stats(cls, method_id: str) -> Dict[str, Any]:
        """
        Get aggregated statistics for a method.

        Args:
            method_id: Learning method instance UUID

        Returns:
            Stats dict with completion rate, avg score, etc.
        """
        query = """
            SELECT
                COUNT(*) as total_sessions,
                COUNT(*) FILTER (WHERE status = 'completed') as completed_count,
                COUNT(*) FILTER (WHERE status = 'timed_out') as timed_out_count,
                COUNT(*) FILTER (WHERE status = 'abandoned') as abandoned_count,
                AVG(score) FILTER (WHERE score IS NOT NULL) as avg_score,
                MIN(score) FILTER (WHERE score IS NOT NULL) as min_score,
                MAX(score) FILTER (WHERE score IS NOT NULL) as max_score,
                AVG(EXTRACT(EPOCH FROM (ended_at - started_at)))
                    FILTER (WHERE ended_at IS NOT NULL) as avg_duration_seconds
            FROM learning_methods.runner_sessions
            WHERE method_id = %s::uuid
        """
        return fetch_one(query, (method_id,)) or {}

    @classmethod
    def cleanup_stale_sessions(cls, max_age_hours: int = 48) -> int:
        """
        Mark stale active sessions as abandoned.

        Args:
            max_age_hours: Hours after which active session is considered stale

        Returns:
            Number of sessions cleaned up
        """
        query = f"""
            UPDATE {cls.table_name}
            SET status = 'abandoned',
                ended_at = NOW(),
                updated_at = NOW()
            WHERE status = 'active'
              AND heartbeat_at < NOW() - INTERVAL '%s hours'
            RETURNING session_id
        """
        results = fetch_all(query, (max_age_hours,))
        return len(results) if results else 0
