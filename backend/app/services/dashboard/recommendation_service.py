"""
LernsystemX Recommendation Service

Business logic for KI-Empfehlungen:
- Generate recommendations (via GPT-4)
- Get user recommendations
- Track user interactions
- Analytics

ISO 9001:2015 compliant - Service layer
"""

from typing import List, Dict, Optional
from datetime import datetime

from app.repositories.widgets.recommendation_repository import RecommendationRepository


class RecommendationService:
    """
    KI Recommendation Service

    Manages AI-generated recommendations for Premium+ users
    """

    # Roles with KI recommendations
    KI_ROLES = [
        'premium', 'creator', 'teacher',
        'school_admin', 'company_admin',
        'admin', 'superadmin'
    ]

    @classmethod
    def get_recommendations(
        cls,
        user: Dict,
        limit: int = 10,
        include_dismissed: bool = False
    ) -> List[Dict]:
        """
        Get recommendations for user

        Args:
            user: User dict
            limit: Max recommendations
            include_dismissed: Include dismissed

        Returns:
            List of recommendation dicts

        Raises:
            PermissionError: If user not Premium+
        """
        user_id = user['user_id']
        role = user.get('role', 'free')

        # Permission check
        if role not in cls.KI_ROLES:
            raise PermissionError(
                f"Role '{role}' does not have access to KI recommendations. "
                "Upgrade to Premium."
            )

        # Get recommendations
        recommendations = RecommendationRepository.get_recommendations(
            user_id,
            limit,
            include_dismissed
        )

        # Mark as shown
        for reco in recommendations:
            if not reco.get('is_shown'):
                RecommendationRepository.mark_as_shown(reco['recommendation_id'])

        return recommendations

    @classmethod
    def dismiss_recommendation(cls, user: Dict, recommendation_id: str) -> bool:
        """
        Dismiss recommendation

        Args:
            user: User dict
            recommendation_id: Recommendation UUID

        Returns:
            bool: Success

        Raises:
            ValueError: If recommendation not found
        """
        # Mark as dismissed
        success = RecommendationRepository.mark_as_dismissed(recommendation_id)

        if not success:
            raise ValueError("Recommendation not found or already dismissed")

        return success

    @classmethod
    def accept_recommendation(cls, user: Dict, recommendation_id: str) -> bool:
        """
        Accept recommendation

        Args:
            user: User dict
            recommendation_id: Recommendation UUID

        Returns:
            bool: Success

        Raises:
            ValueError: If recommendation not found
        """
        # Mark as accepted
        success = RecommendationRepository.mark_as_accepted(recommendation_id)

        if not success:
            raise ValueError("Recommendation not found")

        return success

    @classmethod
    def get_recommendation_stats(cls, user: Dict) -> Dict:
        """
        Get recommendation statistics

        Args:
            user: User dict

        Returns:
            Dict with stats
        """
        user_id = user['user_id']

        stats = RecommendationRepository.get_recommendation_stats(user_id)

        return {
            'total': stats.get('total', 0),
            'shown': stats.get('shown', 0),
            'dismissed': stats.get('dismissed', 0),
            'accepted': stats.get('accepted', 0),
            'acceptance_rate': (
                stats.get('accepted', 0) / stats.get('total', 1) * 100
                if stats.get('total', 0) > 0 else 0
            ),
            'avg_score': float(stats.get('avg_score', 0.0) or 0.0),
            'avg_confidence': float(stats.get('avg_confidence', 0.0) or 0.0)
        }

    @classmethod
    def has_ki_access(cls, role: str) -> bool:
        """
        Check if role has KI recommendations access

        Args:
            role: User role

        Returns:
            bool: True if has access
        """
        return role in cls.KI_ROLES

    @classmethod
    def create_recommendation(
        cls,
        user_id: str,
        recommendation_type: str,
        target_type: str,
        target_id: str,
        score: float,
        reason: str,
        confidence: float = 0.85,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Create new recommendation (called by KI pipeline)

        Args:
            user_id: User UUID
            recommendation_type: Type
            target_type: Target type
            target_id: Target UUID
            score: Score (0.0-1.0)
            reason: KI-generated reason
            confidence: Confidence
            context: Optional context

        Returns:
            Created recommendation dict
        """
        return RecommendationRepository.create_recommendation(
            user_id=user_id,
            recommendation_type=recommendation_type,
            target_type=target_type,
            target_id=target_id,
            score=score,
            reason=reason,
            confidence=confidence,
            context=context
        )
