"""
Repository for ai_decision_explanations table (AI Transparency)
"""
from typing import Dict, List, Optional
import logging

from app.infrastructure.persistence.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AIDecisionExplanationsRepository(BaseRepository):
    """Repository for AI decision explanations and alternatives"""

    @staticmethod
    def create_explanation(
        session_id: str,
        decision_type: str,
        ai_reasoning: str,
        user_friendly_explanation: str,
        confidence_score: float,
        alternative_options: List[Dict],
        analysis_id: Optional[str] = None,
        generation_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new decision explanation.

        Args:
            session_id: UUID of authoring session
            decision_type: Type of decision
            ai_reasoning: Technical AI reasoning
            user_friendly_explanation: User-friendly explanation
            confidence_score: Confidence (0.0-1.0)
            alternative_options: List of alternative options
            analysis_id: Optional analysis ID
            generation_id: Optional generation ID

        Returns:
            explanation_id if successful
        """
        query = """
            INSERT INTO ai_pipeline.ai_decision_explanations (
                session_id, analysis_id, generation_id,
                decision_type, ai_reasoning, user_friendly_explanation,
                confidence_score, alternative_options
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING explanation_id
        """
        try:
            result = AIDecisionExplanationsRepository.fetch_one(query, (
                session_id, analysis_id, generation_id,
                decision_type, ai_reasoning, user_friendly_explanation,
                confidence_score, alternative_options
            ))
            return result['explanation_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating explanation: {e}")
            return None

    @staticmethod
    def get_explanation_by_id(explanation_id: str) -> Optional[Dict]:
        """Get explanation by ID"""
        query = """
            SELECT
                explanation_id, session_id, analysis_id, generation_id,
                decision_type, ai_reasoning, user_friendly_explanation,
                confidence_score, alternative_options,
                user_accepted, user_selected_alternative, user_feedback,
                created_at
            FROM ai_pipeline.ai_decision_explanations
            WHERE explanation_id = %s
        """
        try:
            return AIDecisionExplanationsRepository.fetch_one(query, (explanation_id,))
        except Exception as e:
            logger.error(f"Error fetching explanation: {e}")
            return None

    @staticmethod
    def get_explanations_by_session(
        session_id: str,
        decision_type: Optional[str] = None
    ) -> List[Dict]:
        """Get explanations for session"""
        query = """
            SELECT
                explanation_id, decision_type,
                user_friendly_explanation, confidence_score,
                alternative_options, user_accepted,
                created_at
            FROM ai_pipeline.ai_decision_explanations
            WHERE session_id = %s
        """
        params = [session_id]

        if decision_type:
            query += " AND decision_type = %s"
            params.append(decision_type)

        query += " ORDER BY created_at DESC"

        try:
            return AIDecisionExplanationsRepository.fetch_all(query, tuple(params))
        except Exception as e:
            logger.error(f"Error fetching session explanations: {e}")
            return []

    @staticmethod
    def record_user_feedback(
        explanation_id: str,
        accepted: bool,
        selected_alternative: Optional[int] = None,
        feedback: Optional[str] = None
    ) -> bool:
        """
        Record user's response to explanation.

        Args:
            explanation_id: UUID of explanation
            accepted: Whether user accepted AI's decision
            selected_alternative: Index of selected alternative
            feedback: Optional user feedback

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.ai_decision_explanations
            SET user_accepted = %s,
                user_selected_alternative = %s,
                user_feedback = %s
            WHERE explanation_id = %s
        """
        try:
            AIDecisionExplanationsRepository.execute_update(query, (
                accepted, selected_alternative, feedback, explanation_id
            ))
            return True
        except Exception as e:
            logger.error(f"Error recording user feedback: {e}")
            return False

    @staticmethod
    def get_acceptance_rate(
        session_id: Optional[str] = None,
        decision_type: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get acceptance rate statistics.

        Args:
            session_id: Optional filter by session
            decision_type: Optional filter by type

        Returns:
            Statistics dict
        """
        where_clauses = []
        params = []

        if session_id:
            where_clauses.append("session_id = %s")
            params.append(session_id)

        if decision_type:
            where_clauses.append("decision_type = %s")
            params.append(decision_type)

        where_sql = ""
        if where_clauses:
            where_sql = "WHERE " + " AND ".join(where_clauses)

        query = f"""
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN user_accepted = TRUE THEN 1 END) as accepted,
                COUNT(CASE WHEN user_accepted = FALSE THEN 1 END) as rejected,
                COUNT(CASE WHEN user_selected_alternative IS NOT NULL THEN 1 END) as alternative_selected,
                AVG(confidence_score) as avg_confidence
            FROM ai_pipeline.ai_decision_explanations
            {where_sql}
        """
        try:
            return AIDecisionExplanationsRepository.fetch_one(query, tuple(params))
        except Exception as e:
            logger.error(f"Error fetching acceptance rate: {e}")
            return None
