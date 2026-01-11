"""System Features Domain - Admin Journey API Routes"""
from .feature_types import feature_types_bp
from .course_features import course_features_bp

__all__ = [
    'feature_types_bp',
    'course_features_bp',
]
