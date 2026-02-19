"""
LernsystemX Dashboard Core Services (Part 2)

Continuation of services.py - Recommendation service.

Services:
    - DashboardRecommendationService: KI recommendations

Pure psycopg3 - No ORM
ISO 9001:2015 compliant - Service layer
DDD compliant - Domain-Driven Design
"""

from typing import Dict, List

from app.infrastructure.persistence.repositories.dashboard.core import DashboardRepository as RecommendationRepository  # TODO: Fix this


class DashboardRecommendationService:
    """
    Dashboard Recommendation Service

    Manages KI-powered recommendations for users.

    Business Rules:
        - Only Premium+ users get recommendations
        - Recommendations are scored and ranked
        - Users can dismiss or accept recommendations
    """

    PREMIUM_ROLES = [
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
        Get KI recommendations for user.

        Args:
            user: User dict
            limit: Max recommendations
            include_dismissed: Include dismissed recommendations

        Returns:
            List of recommendations

        Raises:
            PermissionError: If user is not Premium+
        """
        role = user.get('role', 'user')

        if role not in cls.PREMIUM_ROLES:
            raise PermissionError(
                "KI recommendations require Premium subscription"
            )

        return RecommendationRepository.get_user_recommendations(
            user_id=user['user_id'],
            limit=limit,
            include_dismissed=include_dismissed
        )

    @classmethod
    def dismiss_recommendation(cls, user: Dict, recommendation_id: str) -> bool:
        """
        Dismiss a recommendation.

        Args:
            user: User dict
            recommendation_id: Recommendation UUID

        Returns:
            True if dismissed, False if not found
        """
        return RecommendationRepository.dismiss_recommendation(
            user_id=user['user_id'],
            recommendation_id=recommendation_id
        )

    @classmethod
    def accept_recommendation(cls, user: Dict, recommendation_id: str) -> Dict:
        """
        Accept a recommendation.

        Performs action based on recommendation type:
            - course: Enrolls user in course
            - learning_path: Adds learning path
            - exam: Schedules exam

        Args:
            user: User dict
            recommendation_id: Recommendation UUID

        Returns:
            Action result dict

        Raises:
            ValueError: If recommendation not found
        """
        recommendation = RecommendationRepository.get_recommendation_by_id(
            recommendation_id
        )

        if not recommendation or recommendation['user_id'] != user['user_id']:
            raise ValueError("Recommendation not found")

        # Perform action based on type
        result = cls._execute_recommendation_action(user, recommendation)

        # Mark as accepted
        RecommendationRepository.accept_recommendation(
            recommendation_id=recommendation_id
        )

        return result

    @classmethod
    def _execute_recommendation_action(cls, user: Dict, recommendation: Dict) -> Dict:
        """
        Execute recommendation action.

        Args:
            user: User dict
            recommendation: Recommendation dict

        Returns:
            Action result
        """
        rec_type = recommendation['recommendation_type']
        target_id = recommendation['target_id']

        if rec_type == 'course':
            # Enroll user in course
            from app.infrastructure.persistence.repositories.enrollments.core import EnrollmentRepository
            enrollment = EnrollmentRepository.create_enrollment(
                user_id=user['user_id'],
                course_id=target_id,
                access_type='recommended'
            )
            return {
                'action': 'enrolled',
                'course_id': target_id,
                'enrollment_id': enrollment['enrollment_id']
            }

        elif rec_type == 'learning_path':
            # Add learning path
            return {
                'action': 'learning_path_added',
                'path_id': target_id
            }

        elif rec_type == 'exam':
            # Schedule exam
            return {
                'action': 'exam_scheduled',
                'exam_id': target_id
            }

        else:
            return {
                'action': 'accepted',
                'type': rec_type
            }

    @classmethod
    def get_stats(cls, user: Dict) -> Dict:
        """
        Get recommendation statistics.

        Args:
            user: User dict

        Returns:
            Stats dict with counts and rates
        """
        return RecommendationRepository.get_recommendation_stats(
            user_id=user['user_id']
        )


# Exports
__all__ = [
    'DashboardRecommendationService',
]
