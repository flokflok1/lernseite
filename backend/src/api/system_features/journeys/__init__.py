"""System Features Domain - All Journeys"""

from .admin import feature_types_bp, course_features_bp

ALL_JOURNEY_BLUEPRINTS = [
    # Admin Journey (5 endpoints)
    feature_types_bp,  # 1 endpoint
    course_features_bp,  # 4 endpoints
]

__all__ = [
    'ALL_JOURNEY_BLUEPRINTS',
    'feature_types_bp',
    'course_features_bp',
]
