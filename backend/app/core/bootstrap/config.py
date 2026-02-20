"""
LernsystemX Backend - Configuration Classes

Environment-specific configuration for development, production, and testing.
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from app/.env (the canonical config location)
_env_file = Path(__file__).parents[2] / '.env'
load_dotenv(dotenv_path=_env_file)


class Config:
    """
    Base configuration class with common settings
    """
    # Flask Core
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-this')
    DEBUG = False
    TESTING = False

    # Database Configuration (psycopg)
    # NOTE: No default value - must be configured via Setup Wizard or .env
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', None)

    # Database Connection Pool Configuration
    DB_POOL_MIN_SIZE = int(os.getenv('DB_POOL_MIN_SIZE', 2))
    DB_POOL_MAX_SIZE = int(os.getenv('DB_POOL_MAX_SIZE', 10))
    DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', 30))
    DB_POOL_MAX_IDLE = int(os.getenv('DB_POOL_MAX_IDLE', 300))

    # Redis Configuration
    # NOTE: No default values - must be configured via Setup Wizard or .env
    REDIS_URL = os.getenv('REDIS_URL', None)
    REDIS_HOST = os.getenv('REDIS_HOST', None)
    REDIS_PORT = int(os.getenv('REDIS_PORT', 0)) if os.getenv('REDIS_PORT') else 0
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    # Cache TTL Configuration (in seconds)
    # Based on 27_Caching-Strategy.md
    CACHE_DEFAULT_TTL = int(os.getenv('CACHE_DEFAULT_TTL', 600))  # 10 minutes default
    CACHE_USER_PROFILE_TTL = int(os.getenv('CACHE_USER_PROFILE_TTL', 600))  # 10 min
    CACHE_COURSE_TTL = int(os.getenv('CACHE_COURSE_TTL', 3600))  # 1 hour
    CACHE_MODULE_TTL = int(os.getenv('CACHE_MODULE_TTL', 3600))  # 1 hour
    CACHE_LESSON_TTL = int(os.getenv('CACHE_LESSON_TTL', 3600))  # 1 hour
    CACHE_CATEGORY_TTL = int(os.getenv('CACHE_CATEGORY_TTL', 3600))  # 1 hour
    CACHE_LEARNING_METHOD_TTL = int(os.getenv('CACHE_LEARNING_METHOD_TTL', 3600))  # 1 hour
    CACHE_ORGANISATION_TTL = int(os.getenv('CACHE_ORGANISATION_TTL', 300))  # 5 min
    CACHE_TOKEN_STATUS_TTL = int(os.getenv('CACHE_TOKEN_STATUS_TTL', 30))  # 30 sec
    CACHE_WIDGET_TTL = int(os.getenv('CACHE_WIDGET_TTL', 60))  # 1 min
    CACHE_ANALYTICS_TTL = int(os.getenv('CACHE_ANALYTICS_TTL', 60))  # 1 min
    CACHE_EXAM_TTL = int(os.getenv('CACHE_EXAM_TTL', 300))  # 5 min
    CACHE_API_RESPONSE_TTL = int(os.getenv('CACHE_API_RESPONSE_TTL', 60))  # 1 min
    CACHE_TRANSLATION_TTL = None  # Permanent (no expiry)
    CACHE_AI_RESULT_TTL = None  # Permanent (no expiry)

    # Celery Configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TIMEZONE = 'Europe/Berlin'
    CELERY_ENABLE_UTC = True
    CELERY_TASK_TRACK_STARTED = True
    CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
    CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-change-this')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))
    )
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # AI Integration - Anthropic
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')

    # AI Integration - OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4-turbo-preview')

    # Translation - DeepL
    DEEPL_API_KEY = os.getenv('DEEPL_API_KEY')

    # Payment Processing - Stripe
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

    # Premium Model Configuration
    PREMIUM_PRICE_MONTHLY = float(os.getenv('PREMIUM_PRICE_MONTHLY', 14.99))
    PREMIUM_PRICE_YEARLY = float(os.getenv('PREMIUM_PRICE_YEARLY', 129.99))
    PREMIUM_TOKENS_MONTHLY = int(os.getenv('PREMIUM_TOKENS_MONTHLY', 10000))

    # Token Pricing (EUR per package)
    TOKEN_PACKAGES = {
        5000: float(os.getenv('TOKEN_PRICE_5K', 1.99)),
        20000: float(os.getenv('TOKEN_PRICE_20K', 6.99)),
        50000: float(os.getenv('TOKEN_PRICE_50K', 14.99)),
        100000: float(os.getenv('TOKEN_PRICE_100K', 24.99))
    }

    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'False').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@lernsystemx.com')

    # Email Service Configuration (New Email Utility)
    SMTP_SERVER = os.getenv('SMTP_SERVER', MAIL_SERVER)
    SMTP_PORT = int(os.getenv('SMTP_PORT', MAIL_PORT))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', MAIL_USERNAME)
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', MAIL_PASSWORD)
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', str(MAIL_USE_TLS)).lower() == 'true'
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', MAIL_DEFAULT_SENDER)
    SENDER_NAME = os.getenv('SENDER_NAME', 'LernSystemX')
    EMAIL_PROVIDER = os.getenv('EMAIL_PROVIDER', 'smtp')  # smtp, sendgrid, ses
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@lernsystemx.com')  # B2B contact notifications

    # CORS Configuration (Development: Allow all origins for easier testing)
    cors_env = os.getenv('CORS_ORIGINS', '*')
    CORS_ORIGINS = cors_env if cors_env == '*' else cors_env.split(',')

    # SocketIO Configuration
    SOCKETIO_MESSAGE_QUEUE = os.getenv('SOCKETIO_MESSAGE_QUEUE', 'redis://localhost:6379/3')
    socketio_cors_env = os.getenv('SOCKETIO_CORS_ALLOWED_ORIGINS', '*')
    SOCKETIO_CORS_ALLOWED_ORIGINS = socketio_cors_env if socketio_cors_env == '*' else socketio_cors_env.split(',')

    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/4')
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '300 per minute')  # Increased from 200/hour for better polling support
    RATELIMIT_HEADERS_ENABLED = True

    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = set(
        os.getenv('ALLOWED_EXTENSIONS', 'pdf,docx,pptx,jpg,jpeg,png,gif').split(',')
    )

    # Frontend URL
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

    # LiveRoom Configuration (WebRTC)
    TURN_SERVER_URL = os.getenv('TURN_SERVER_URL')
    TURN_USERNAME = os.getenv('TURN_USERNAME')
    TURN_PASSWORD = os.getenv('TURN_PASSWORD')

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/lernsystemx.log')

    # Session Configuration
    SESSION_TYPE = os.getenv('SESSION_TYPE', 'redis')
    SESSION_PERMANENT = os.getenv('SESSION_PERMANENT', 'False').lower() == 'true'
    SESSION_USE_SIGNER = os.getenv('SESSION_USE_SIGNER', 'True').lower() == 'true'
    SESSION_REDIS_URL = os.getenv('SESSION_REDIS_URL', 'redis://localhost:6379/5')

    # Supported Languages (20 languages)
    SUPPORTED_LANGUAGES = [
        'de', 'en', 'es', 'fr', 'it', 'pt', 'nl', 'pl', 'ru', 'tr',
        'ja', 'ko', 'zh', 'ar', 'hi', 'sv', 'no', 'da', 'fi', 'el'
    ]
    DEFAULT_LANGUAGE = 'de'

    # Learning Methods Configuration
    LEARNING_METHODS = {
        'free': [
            'flashcards', 'mcq', 'fill_blanks', 'matching', 'drag_drop',
            'math', 'true_false', 'sorting', 'image_quiz', 'audio_quiz', 'video_quiz'
        ],
        'premium': [
            'spaced_repetition', 'mind_maps', 'timeline',
            'storytelling', 'mnemonics', 'peer_learning'
        ],
        'pro': [
            'case_studies', 'role_play', 'ai_exam_simulation', 'whiteboard_ai'
        ]
    }

    # AI Token Costs (average per operation)
    AI_TOKEN_COSTS = {
        'flashcard_generation': 500,
        'mcq_generation': 800,
        'quiz_generation': 1500,
        'exam_generation': 6000,
        'mindmap_generation': 2000,
        'translation': 1000,
        'content_validation': 500,
        'whiteboard_ai': 3000,
        'math_ai': 2500
    }

    # API Gateway Configuration (Phase 21)
    API_GATEWAY_ENABLED = os.getenv('API_GATEWAY_ENABLED', 'True').lower() == 'true'
    API_BASE_PATH = os.getenv('API_BASE_PATH', '/api/v1')
    API_VERSION = os.getenv('API_VERSION', '1')

    # API Gateway Prefixes
    API_PUBLIC_PREFIX = os.getenv('API_PUBLIC_PREFIX', '/api/v1/public')
    API_APP_PREFIX = os.getenv('API_APP_PREFIX', '/api/v1')
    API_ADMIN_PREFIX = os.getenv('API_ADMIN_PREFIX', '/api/v1/admin')
    API_ORG_PREFIX = os.getenv('API_ORG_PREFIX', '/api/v1/organisations')

    # Gateway Logging & Analytics
    API_GATEWAY_LOG_REQUESTS = os.getenv('API_GATEWAY_LOG_REQUESTS', 'True').lower() == 'true'
    API_GATEWAY_TRACK_ANALYTICS = os.getenv('API_GATEWAY_TRACK_ANALYTICS', 'True').lower() == 'true'
    API_GATEWAY_REQUEST_ID_HEADER = os.getenv('API_GATEWAY_REQUEST_ID_HEADER', 'X-LSX-Request-ID')

    # Gateway Rate Limiting (extends Phase 20)
    API_GATEWAY_RATE_LIMIT_DEFAULT = os.getenv('API_GATEWAY_RATE_LIMIT_DEFAULT', '100 per minute')
    API_GATEWAY_RATE_LIMIT_ADMIN = os.getenv('API_GATEWAY_RATE_LIMIT_ADMIN', '500 per minute')  # Increased for AI job polling
    API_GATEWAY_RATE_LIMIT_PUBLIC = os.getenv('API_GATEWAY_RATE_LIMIT_PUBLIC', '10 per minute')
    API_GATEWAY_RATE_LIMIT_KI = os.getenv('API_GATEWAY_RATE_LIMIT_KI', '60 per minute')  # Increased for AI operations
    API_GATEWAY_RATE_LIMIT_ANALYTICS = os.getenv('API_GATEWAY_RATE_LIMIT_ANALYTICS', '60 per minute')
    API_GATEWAY_RATE_LIMIT_LIVEROOM = os.getenv('API_GATEWAY_RATE_LIMIT_LIVEROOM', '100 per minute')

    # Gateway Request Validation
    API_GATEWAY_MAX_BODY_SIZE = int(os.getenv('API_GATEWAY_MAX_BODY_SIZE', 10485760))  # 10MB default
    API_GATEWAY_VALIDATE_CONTENT_TYPE = os.getenv('API_GATEWAY_VALIDATE_CONTENT_TYPE', 'True').lower() == 'true'

    # Multi-Tenant Domain Routing
    API_GATEWAY_MULTI_TENANT_ENABLED = os.getenv('API_GATEWAY_MULTI_TENANT_ENABLED', 'True').lower() == 'true'
    API_GATEWAY_DEFAULT_ORG_HEADER = os.getenv('API_GATEWAY_DEFAULT_ORG_HEADER', 'X-LSX-Org-ID')
    API_GATEWAY_CLIENT_HEADER = os.getenv('API_GATEWAY_CLIENT_HEADER', 'X-LSX-Client')

    # API Versioning & Change Management (Phase 22)
    LSX_VERSION = os.getenv('LSX_VERSION', '1.0.0')
    LSX_ENV = os.getenv('LSX_ENV', 'development')

    # API Version Configuration
    API_VERSION_CURRENT = int(os.getenv('API_VERSION_CURRENT', '1'))
    API_VERSION_SUPPORTED = os.getenv('API_VERSION_SUPPORTED', '1').split(',')
    API_VERSION_DEFAULT = int(os.getenv('API_VERSION_DEFAULT', '1'))

    # API Version Headers
    API_VERSION_HEADER = os.getenv('API_VERSION_HEADER', 'X-LSX-API-Version')
    API_SYSTEM_VERSION_HEADER = os.getenv('API_SYSTEM_VERSION_HEADER', 'X-LSX-System-Version')

    # Deprecation Configuration
    API_DEPRECATION_ENABLED = os.getenv('API_DEPRECATION_ENABLED', 'True').lower() == 'true'
    API_DEPRECATION_HEADER = os.getenv('API_DEPRECATION_HEADER', 'X-LSX-Deprecated')
    API_DEPRECATION_DATE_HEADER = os.getenv('API_DEPRECATION_DATE_HEADER', 'X-LSX-Deprecation-Date')
    API_SUNSET_DATE_HEADER = os.getenv('API_SUNSET_DATE_HEADER', 'X-LSX-Sunset-Date')
    API_MIGRATION_GUIDE_HEADER = os.getenv('API_MIGRATION_GUIDE_HEADER', 'X-LSX-Migration-Guide')
    API_REPLACEMENT_HEADER = os.getenv('API_REPLACEMENT_HEADER', 'X-LSX-Replacement')

    # Deprecation Notice URL
    API_DEPRECATION_NOTICE_URL = os.getenv(
        'API_DEPRECATION_NOTICE_URL',
        'https://docs.lernsystemx.de/api/deprecation-notices'
    )

    # Version Support Window (in months)
    API_VERSION_SUPPORT_WINDOW = int(os.getenv('API_VERSION_SUPPORT_WINDOW', '12'))
    API_VERSION_DEPRECATION_WARNING = int(os.getenv('API_VERSION_DEPRECATION_WARNING', '6'))

    # Version Detection Strategy
    API_VERSION_DETECTION = os.getenv('API_VERSION_DETECTION', 'url')
    API_VERSION_ALLOW_HEADER_OVERRIDE = os.getenv('API_VERSION_ALLOW_HEADER_OVERRIDE', 'False').lower() == 'true'

    # Breaking Change Protection
    API_ENFORCE_VERSION_CHECK = os.getenv('API_ENFORCE_VERSION_CHECK', 'True').lower() == 'true'
    API_REJECT_UNSUPPORTED_VERSIONS = os.getenv('API_REJECT_UNSUPPORTED_VERSIONS', 'True').lower() == 'true'


class DevelopmentConfig(Config):
    """
    Development environment configuration
    """
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

    # Development-specific settings
    CELERY_TASK_ALWAYS_EAGER = False  # Run tasks asynchronously
    CELERY_TASK_EAGER_PROPAGATES = True


class ProductionConfig(Config):
    """
    Production environment configuration

    Optimized for high-availability, security, and performance in production.
    """
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # INFO for production logging

    # Stricter security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Security Headers (enforced by Nginx, but also set in Flask)
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year for static files

    # CORS - Restrictive in production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')  # Must be set explicitly

    # Production Celery settings
    CELERY_TASK_ALWAYS_EAGER = False
    CELERY_SEND_TASK_ERROR_EMAILS = True

    # Production database pool - larger size for higher traffic
    DB_POOL_MIN_SIZE = int(os.getenv('DB_POOL_MIN_SIZE', 5))
    DB_POOL_MAX_SIZE = int(os.getenv('DB_POOL_MAX_SIZE', 20))
    DB_POOL_TIMEOUT = int(os.getenv('DB_POOL_TIMEOUT', 60))  # Longer timeout in production

    # Gunicorn Configuration
    GUNICORN_WORKERS = int(os.getenv('GUNICORN_WORKERS', 4))  # Will be overridden by gunicorn.conf.py
    GUNICORN_THREADS = int(os.getenv('GUNICORN_THREADS', 2))
    GUNICORN_TIMEOUT = int(os.getenv('GUNICORN_TIMEOUT', 120))
    GUNICORN_KEEPALIVE = int(os.getenv('GUNICORN_KEEPALIVE', 5))

    # Rate Limiting - Stricter in production
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'redis://localhost:6379/4')
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per hour')  # More restrictive
    RATELIMIT_HEADERS_ENABLED = True

    # File Upload - Production limits
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB

    # Logging Configuration
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/lsx/backend.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

    # Performance Optimizations
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml',
        'application/json', 'application/javascript'
    ]
    COMPRESS_LEVEL = 6
    COMPRESS_MIN_SIZE = 500

    # Backup & Recovery Configuration
    BACKUP_DIR = os.getenv('BACKUP_DIR', '/var/backups/lsx')
    BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', 30))
    BACKUP_DB_NAME = os.getenv('BACKUP_DB_NAME', 'lernsystemx_prod')
    BACKUP_DB_HOST = os.getenv('BACKUP_DB_HOST', 'localhost')
    BACKUP_DB_PORT = int(os.getenv('BACKUP_DB_PORT', 5432))
    BACKUP_DB_USER = os.getenv('BACKUP_DB_USER', 'lsx_user')
    BACKUP_ENABLE_COMPRESSION = os.getenv('BACKUP_ENABLE_COMPRESSION', 'True').lower() == 'true'
    BACKUP_ENABLE_ENCRYPTION = os.getenv('BACKUP_ENABLE_ENCRYPTION', 'False').lower() == 'true'
    BACKUP_ENCRYPTION_KEY = os.getenv('BACKUP_ENCRYPTION_KEY')

    # Optional: Remote Backup (S3/MinIO)
    BACKUP_REMOTE_ENABLED = os.getenv('BACKUP_REMOTE_ENABLED', 'False').lower() == 'true'
    BACKUP_S3_BUCKET = os.getenv('BACKUP_S3_BUCKET')
    BACKUP_S3_ENDPOINT = os.getenv('BACKUP_S3_ENDPOINT')
    BACKUP_S3_ACCESS_KEY = os.getenv('BACKUP_S3_ACCESS_KEY')
    BACKUP_S3_SECRET_KEY = os.getenv('BACKUP_S3_SECRET_KEY')

    # Monitoring & Alerting Configuration
    MONITORING_ENABLED = os.getenv('MONITORING_ENABLED', 'False').lower() == 'true'
    MONITORING_EXPORTER = os.getenv('MONITORING_EXPORTER', 'prometheus')
    MONITORING_METRICS_PATH = os.getenv('MONITORING_METRICS_PATH', '/metrics')
    MONITORING_SAMPLE_RATE = float(os.getenv('MONITORING_SAMPLE_RATE', '1.0'))

    # Error Tracking (Sentry - optional)
    ERROR_TRACKING_ENABLED = os.getenv('ERROR_TRACKING_ENABLED', 'False').lower() == 'true'
    ERROR_TRACKING_DSN = os.getenv('ERROR_TRACKING_DSN')
    ERROR_TRACKING_SAMPLE_RATE = float(os.getenv('ERROR_TRACKING_SAMPLE_RATE', '1.0'))
    ERROR_TRACKING_ENVIRONMENT = os.getenv('ERROR_TRACKING_ENVIRONMENT', 'production')

    # Security Configuration (Phase 20)
    # Password Policy
    PASSWORD_MIN_LENGTH = int(os.getenv('PASSWORD_MIN_LENGTH', 12))
    PASSWORD_REQUIRE_UPPERCASE = os.getenv('PASSWORD_REQUIRE_UPPERCASE', 'True').lower() == 'true'
    PASSWORD_REQUIRE_LOWERCASE = os.getenv('PASSWORD_REQUIRE_LOWERCASE', 'True').lower() == 'true'
    PASSWORD_REQUIRE_DIGITS = os.getenv('PASSWORD_REQUIRE_DIGITS', 'True').lower() == 'true'
    PASSWORD_REQUIRE_SPECIAL = os.getenv('PASSWORD_REQUIRE_SPECIAL', 'True').lower() == 'true'

    # Login Security & Account Lockout
    MAX_LOGIN_ATTEMPTS = int(os.getenv('MAX_LOGIN_ATTEMPTS', 5))
    LOGIN_LOCKOUT_MINUTES = int(os.getenv('LOGIN_LOCKOUT_MINUTES', 15))
    ACCOUNT_LOCKOUT_THRESHOLD = int(os.getenv('ACCOUNT_LOCKOUT_THRESHOLD', 10))

    # Rate Limiting (Security-specific)
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_LOGIN = os.getenv('RATE_LIMIT_LOGIN', '5 per minute')
    RATE_LIMIT_API = os.getenv('RATE_LIMIT_API', '100 per minute')
    RATE_LIMIT_SENSITIVE = os.getenv('RATE_LIMIT_SENSITIVE', '10 per minute')

    # Security Headers
    SECURITY_HEADERS_ENABLED = os.getenv('SECURITY_HEADERS_ENABLED', 'True').lower() == 'true'
    HSTS_MAX_AGE = int(os.getenv('HSTS_MAX_AGE', 31536000))  # 1 year

    # Audit Logging
    AUDIT_LOG_ENABLED = os.getenv('AUDIT_LOG_ENABLED', 'True').lower() == 'true'
    AUDIT_LOG_RETENTION_DAYS = int(os.getenv('AUDIT_LOG_RETENTION_DAYS', 365))

    # Note: API Gateway and API Versioning configuration is now in base Config class
    # to ensure availability in all environments (lines 197-267)


class TestingConfig(Config):
    """
    Testing environment configuration
    """
    TESTING = True
    DEBUG = True

    # Use separate test database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'TEST_DATABASE_URL',
        'postgresql://username:password@localhost:5432/lernsystemx_test'
    )

    # Use separate Redis DB for testing
    REDIS_DB = 15
    CELERY_BROKER_URL = 'redis://localhost:6379/14'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/13'

    # Run Celery tasks synchronously in tests
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True

    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False

    # Testing-specific settings
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = 'DEBUG'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
