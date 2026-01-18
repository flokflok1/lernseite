"""
LernsystemX Core Bootstrap Package

Provides core application initialization and configuration:
- config: Environment-specific configuration classes
- extensions: Flask extensions and global instances
"""

from app.core.bootstrap.config import config, Config
from app.core.bootstrap.extensions import (
    db_pool,
    init_db_pool,
    jwt,
    socketio,
    limiter,
    mail,
    celery,
    redis_client,
    refresh_db_pool,
)

__all__ = [
    'config',
    'Config',
    'db_pool',
    'init_db_pool',
    'jwt',
    'socketio',
    'limiter',
    'mail',
    'celery',
    'redis_client',
    'refresh_db_pool',
]
