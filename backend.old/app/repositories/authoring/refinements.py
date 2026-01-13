"""
Repository for authoring_refinements table (Collaborative Refinement Dialog)
"""
from typing import Dict, List, Optional
import logging

from app.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AuthoringRefinementsRepository(BaseRepository):
    """Repository for tracking user refinement requests and AI suggestions"""

    @staticmethod
    def create_refinement(
        session_id: str,
        target_type: str,
        target_id: str,
        refinement_type: str,
        user_request: str,
        generation_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new refinement request.

        Args:
            session_id: UUID of authoring session
            target_type: Type of target entity
            target_id: UUID of target entity
            refinement_type: Type of refinement
            user_request: User's refinement request
            generation_id: Optional generation ID

        Returns:
            refinement_id if successful
        """
        query = """
            INSERT INTO ai_pipeline.authoring_refinements (
                session_id, generation_id, target_type, target_id,
                refinement_type, user_request
            ) VALUES (
                %s, %s, %s, %s, %s, %s
            ) RETURNING refinement_id
        """
        try:
            result = AuthoringRefinementsRepository.fetch_one(query, (
                session_id, generation_id, target_type, target_id,
                refinement_type, user_request
            ))
            return result['refinement_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating refinement: {e}")
            return None

    @staticmethod
    def get_refinement_by_id(refinement_id: str) -> Optional[Dict]:
        """Get refinement record by ID"""
        query = """
            SELECT
                refinement_id, session_id, generation_id,
                target_type, target_id, refinement_type,
                user_request, ai_suggestion, ai_actions,
                discussion_thread, ai_learning_note,
                user_approved, user_feedback,
                applied, applied_at,
                ai_provider, ai_model, tokens_used,
                requested_at, responded_at, created_at
            FROM ai_pipeline.authoring_refinements
            WHERE refinement_id = %s
        """
        try:
            return AuthoringRefinementsRepository.fetch_one(query, (refinement_id,))
        except Exception as e:
            logger.error(f"Error fetching refinement: {e}")
            return None

    @staticmethod
    def get_refinements_by_session(
        session_id: str,
        include_applied: bool = True
    ) -> List[Dict]:
        """Get refinements for session"""
        query = """
            SELECT
                refinement_id, target_type, target_id,
                refinement_type, user_request, ai_suggestion,
                user_approved, applied, requested_at
            FROM ai_pipeline.authoring_refinements
            WHERE session_id = %s
        """
        if not include_applied:
            query += " AND applied = FALSE"

        query += " ORDER BY requested_at DESC"

        try:
            return AuthoringRefinementsRepository.fetch_all(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching session refinements: {e}")
            return []

    @staticmethod
    def set_ai_response(
        refinement_id: str,
        ai_suggestion: str,
        ai_actions: List[Dict],
        ai_provider: str,
        ai_model: str,
        tokens_used: int
    ) -> bool:
        """
        Store AI's response to refinement request.

        Args:
            refinement_id: UUID of refinement
            ai_suggestion: AI's suggestion text
            ai_actions: Structured actions AI will perform
            ai_provider: AI provider used
            ai_model: AI model used
            tokens_used: Tokens consumed

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_refinements
            SET ai_suggestion = %s,
                ai_actions = %s,
                ai_provider = %s,
                ai_model = %s,
                tokens_used = %s,
                responded_at = NOW()
            WHERE refinement_id = %s
        """
        try:
            AuthoringRefinementsRepository.execute_update(query, (
                ai_suggestion, ai_actions, ai_provider,
                ai_model, tokens_used, refinement_id
            ))
            return True
        except Exception as e:
            logger.error(f"Error setting AI response: {e}")
            return False

    @staticmethod
    def add_discussion_message(
        refinement_id: str,
        role: str,
        message: str
    ) -> bool:
        """
        Add message to discussion thread.

        Args:
            refinement_id: UUID of refinement
            role: Message role (user/assistant)
            message: Message text

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_refinements
            SET discussion_thread = COALESCE(discussion_thread, '[]'::jsonb) ||
                jsonb_build_array(jsonb_build_object('role', %s, 'message', %s, 'timestamp', NOW()))
            WHERE refinement_id = %s
        """
        try:
            AuthoringRefinementsRepository.execute_update(
                query,
                (role, message, refinement_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error adding discussion message: {e}")
            return False

    @staticmethod
    def set_user_decision(
        refinement_id: str,
        approved: bool,
        feedback: Optional[str] = None
    ) -> bool:
        """Record user's decision on refinement"""
        query = """
            UPDATE ai_pipeline.authoring_refinements
            SET user_approved = %s,
                user_feedback = %s
            WHERE refinement_id = %s
        """
        try:
            AuthoringRefinementsRepository.execute_update(
                query,
                (approved, feedback, refinement_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting user decision: {e}")
            return False

    @staticmethod
    def mark_applied(
        refinement_id: str,
        ai_learning_note: Optional[str] = None
    ) -> bool:
        """
        Mark refinement as applied.

        Args:
            refinement_id: UUID of refinement
            ai_learning_note: What AI learned from this

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_refinements
            SET applied = TRUE,
                applied_at = NOW(),
                ai_learning_note = %s
            WHERE refinement_id = %s
        """
        try:
            AuthoringRefinementsRepository.execute_update(
                query,
                (ai_learning_note, refinement_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error marking applied: {e}")
            return False

    @staticmethod
    def get_pending_refinements(session_id: str) -> List[Dict]:
        """Get refinements pending user approval"""
        query = """
            SELECT
                refinement_id, target_type, target_id,
                refinement_type, user_request, ai_suggestion,
                ai_actions, discussion_thread,
                requested_at, responded_at
            FROM ai_pipeline.authoring_refinements
            WHERE session_id = %s
            AND user_approved IS NULL
            ORDER BY requested_at ASC
        """
        try:
            return AuthoringRefinementsRepository.fetch_all(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching pending refinements: {e}")
            return []
