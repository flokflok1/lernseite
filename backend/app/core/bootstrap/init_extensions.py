"""
Extension Initialization - Register Flask extensions, shell context, Celery.

Extracted from app/__init__.py (Section 1) for DDD layer compliance.
"""

from flask import Flask

from app.core.bootstrap.extensions import (
    db_pool,
    init_db_pool,
    jwt,
    socketio,
    celery,
    redis_client,
    limiter,
    mail,
)


def register_extensions(app: Flask) -> None:
    """
    Register Flask extensions.

    Args:
        app: Flask application instance
    """
    # Database Connection Pool (psycopg)
    init_db_pool(
        database_url=app.config['SQLALCHEMY_DATABASE_URI'],
        min_size=app.config.get('DB_POOL_MIN_SIZE', 2),
        max_size=app.config.get('DB_POOL_MAX_SIZE', 10)
    )

    # Authentication
    jwt.init_app(app)

    # WebSocket
    socketio.init_app(
        app,
        message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'],
        cors_allowed_origins=app.config['SOCKETIO_CORS_ALLOWED_ORIGINS']
    )

    # Rate Limiting
    limiter.init_app(app)

    # Email (Legacy Flask-Mail)
    mail.init_app(app)

    # Email Service (New Template-based Email Utility)
    from app.infrastructure.notifications.email import init_email_service
    init_email_service(app)


def register_shell_context(app: Flask) -> None:
    """
    Register shell context for Flask shell.

    Args:
        app: Flask application instance
    """
    @app.shell_context_processor
    def make_shell_context():
        """Add database pool and utilities to shell context"""
        from app.infrastructure.persistence.repositories.user import UserRepository
        from app.infrastructure.persistence.repositories.courses import CourseRepository
        from app.infrastructure.persistence.repositories.courses.chapters import ChapterRepository
        from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository
        from app.infrastructure.persistence.repositories.enrollments.core import EnrollmentRepository
        from app.infrastructure.persistence.repositories.category import CategoryRepository
        from app.infrastructure.persistence.repositories.learning_method import LearningMethodRepository
        from app.infrastructure.persistence.repositories.token import TokenRepository
        from app.infrastructure.persistence.repositories.subscription import SubscriptionRepository
        from app.infrastructure.persistence.repositories.organisations.core import OrganisationRepository
        from app.infrastructure.persistence.repositories.dashboard.core import DashboardRepository
        from app.infrastructure.persistence.repositories.analytics import AnalyticsRepository
        from app.application.services.ai_adapter import AIAdapter
        from app.application.services.system.billing.service import BillingService

        return {
            'db_pool': db_pool,
            'redis': redis_client,
            'UserRepository': UserRepository,
            'CourseRepository': CourseRepository,
            'ChapterRepository': ChapterRepository,
            'LessonRepository': LessonRepository,
            'EnrollmentRepository': EnrollmentRepository,
            'CategoryRepository': CategoryRepository,
            'LearningMethodRepository': LearningMethodRepository,
            'TokenRepository': TokenRepository,
            'SubscriptionRepository': SubscriptionRepository,
            'OrganisationRepository': OrganisationRepository,
            'DashboardRepository': DashboardRepository,
            'AnalyticsRepository': AnalyticsRepository,
            'AIAdapter': AIAdapter,
            'BillingService': BillingService
        }


def init_celery(app: Flask) -> None:
    """
    Initialize Celery with Flask app context.

    Args:
        app: Flask application instance
    """
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
