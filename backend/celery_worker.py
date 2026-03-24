"""
Celery worker entry point — NO eventlet monkey-patching.

Usage:
    celery -A celery_worker:celery worker --pool=prefork --loglevel=info

This file exists because wsgi.py conditionally calls eventlet.monkey_patch()
which breaks psycopg_pool's native threads in Celery prefork workers.
"""

from app import create_app
from app.core.bootstrap.extensions import celery

# Create Flask app so extensions (db_pool, redis, etc.) are initialized.
# The worker_process_init signal in extensions.py will refresh the pool
# in each forked worker process.
app = create_app()
app.app_context().push()
