"""
Repository for authoring_analysis table (Multi-File AI Analysis)
"""
from typing import Dict, List, Optional
import logging

from app.infrastructure.persistence.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AuthoringAnalysisRepository(BaseRepository):
    """Repository for multi-file AI analysis with exam pattern recognition"""

    @staticmethod
    def create_analysis(
        session_id: str,
        file_ids: List[str],
        analysis_type: str,
        ai_provider: str,
        ai_model: str
    ) -> Optional[str]:
        """
        Create a new analysis record.

        Args:
            session_id: UUID of authoring session
            file_ids: List of file UUIDs to analyze
            analysis_type: Type of analysis
            ai_provider: AI provider (anthropic, openai)
            ai_model: AI model used

        Returns:
            analysis_id if successful
        """
        query = """
            INSERT INTO ai_pipeline.authoring_analysis (
                session_id, file_ids, analysis_type,
                ai_provider, ai_model, status
            ) VALUES (
                %s, %s, %s, %s, %s, 'queued'
            ) RETURNING analysis_id
        """
        try:
            result = AuthoringAnalysisRepository.fetch_one(query, (
                session_id, file_ids, analysis_type, ai_provider, ai_model
            ))
            return result['analysis_id'] if result else None
        except Exception as e:
            logger.error(f"Error creating analysis: {e}")
            return None

    @staticmethod
    def get_analysis_by_id(analysis_id: str) -> Optional[Dict]:
        """Get analysis record by ID"""
        query = """
            SELECT
                analysis_id, session_id, file_ids, analysis_type,
                topics_found, difficulty_analysis, exam_patterns,
                content_structure, quality_metrics,
                exam_insights, user_feedback_on_insights, insights_applied,
                ai_provider, ai_model, tokens_used, prompt_used,
                status, error_message,
                started_at, completed_at, processing_duration_ms,
                created_at
            FROM ai_pipeline.authoring_analysis
            WHERE analysis_id = %s
        """
        try:
            return AuthoringAnalysisRepository.fetch_one(query, (analysis_id,))
        except Exception as e:
            logger.error(f"Error fetching analysis: {e}")
            return None

    @staticmethod
    def get_analyses_by_session(session_id: str) -> List[Dict]:
        """Get all analyses for session"""
        query = """
            SELECT
                analysis_id, file_ids, analysis_type,
                topics_found, exam_patterns, exam_insights,
                status, started_at, completed_at
            FROM ai_pipeline.authoring_analysis
            WHERE session_id = %s
            ORDER BY created_at DESC
        """
        try:
            return AuthoringAnalysisRepository.fetch_all(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching session analyses: {e}")
            return []

    @staticmethod
    def update_status(
        analysis_id: str,
        status: str,
        error_message: Optional[str] = None
    ) -> bool:
        """Update analysis status"""
        query = """
            UPDATE ai_pipeline.authoring_analysis
            SET status = %s,
                error_message = %s,
                completed_at = CASE
                    WHEN %s IN ('completed', 'failed') THEN NOW()
                    ELSE completed_at
                END
            WHERE analysis_id = %s
        """
        try:
            AuthoringAnalysisRepository.execute_update(
                query,
                (status, error_message, status, analysis_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error updating analysis status: {e}")
            return False

    @staticmethod
    def update_results(
        analysis_id: str,
        topics_found: List[Dict],
        difficulty_analysis: Dict,
        exam_patterns: Dict,
        content_structure: Dict,
        quality_metrics: Dict,
        tokens_used: int,
        processing_duration_ms: int
    ) -> bool:
        """
        Update analysis results.

        Args:
            analysis_id: UUID of analysis
            topics_found: List of discovered topics
            difficulty_analysis: Difficulty breakdown
            exam_patterns: Recognized exam patterns (CRITICAL!)
            content_structure: Content structure analysis
            quality_metrics: Quality assessment
            tokens_used: AI tokens consumed
            processing_duration_ms: Processing time

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_analysis
            SET topics_found = %s,
                difficulty_analysis = %s,
                exam_patterns = %s,
                content_structure = %s,
                quality_metrics = %s,
                tokens_used = %s,
                processing_duration_ms = %s,
                status = 'completed',
                completed_at = NOW()
            WHERE analysis_id = %s
        """
        try:
            AuthoringAnalysisRepository.execute_update(query, (
                topics_found, difficulty_analysis, exam_patterns,
                content_structure, quality_metrics,
                tokens_used, processing_duration_ms, analysis_id
            ))
            return True
        except Exception as e:
            logger.error(f"Error updating analysis results: {e}")
            return False

    @staticmethod
    def set_exam_insights(
        analysis_id: str,
        exam_insights: Dict
    ) -> bool:
        """
        Set user-friendly exam insights.

        Args:
            analysis_id: UUID of analysis
            exam_insights: Formatted insights for UI

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_analysis
            SET exam_insights = %s
            WHERE analysis_id = %s
        """
        try:
            AuthoringAnalysisRepository.execute_update(
                query,
                (exam_insights, analysis_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error setting exam insights: {e}")
            return False

    @staticmethod
    def add_user_feedback(
        analysis_id: str,
        feedback: str,
        insights_applied: bool
    ) -> bool:
        """
        Record user feedback on insights.

        Args:
            analysis_id: UUID of analysis
            feedback: User feedback text
            insights_applied: Whether user applied insights

        Returns:
            True if successful
        """
        query = """
            UPDATE ai_pipeline.authoring_analysis
            SET user_feedback_on_insights = %s,
                insights_applied = %s
            WHERE analysis_id = %s
        """
        try:
            AuthoringAnalysisRepository.execute_update(
                query,
                (feedback, insights_applied, analysis_id)
            )
            return True
        except Exception as e:
            logger.error(f"Error adding user feedback: {e}")
            return False

    @staticmethod
    def get_latest_by_session(session_id: str) -> Optional[Dict]:
        """Get most recent completed analysis for session"""
        query = """
            SELECT
                analysis_id, file_ids, analysis_type,
                topics_found, difficulty_analysis, exam_patterns,
                content_structure, quality_metrics, exam_insights,
                tokens_used, completed_at
            FROM ai_pipeline.authoring_analysis
            WHERE session_id = %s AND status = 'completed'
            ORDER BY completed_at DESC
            LIMIT 1
        """
        try:
            return AuthoringAnalysisRepository.fetch_one(query, (session_id,))
        except Exception as e:
            logger.error(f"Error fetching latest analysis: {e}")
            return None
