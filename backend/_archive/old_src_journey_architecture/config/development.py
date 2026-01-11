"""
Development Configuration

Configuration settings for development environment.
"""

from src.config.base import BaseConfig


class DevelopmentConfig(BaseConfig):
    """Development configuration."""

    DEBUG = True
    TESTING = False

    # Disable security features in development
    SESSION_COOKIE_SECURE = False

    # Enable detailed error pages
    PROPAGATE_EXCEPTIONS = True
