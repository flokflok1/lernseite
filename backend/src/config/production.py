"""
Production Configuration

Configuration settings for production environment.
"""

from src.config.base import BaseConfig


class ProductionConfig(BaseConfig):
    """Production configuration."""

    DEBUG = False
    TESTING = False

    # Enforce all security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
