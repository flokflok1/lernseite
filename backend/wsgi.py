"""
WSGI Entry Point for Production Deployment

Used by Gunicorn:
    gunicorn -c config/gunicorn.conf.py wsgi:app

With eventlet (Docker production):
    GUNICORN_WORKER_CLASS=eventlet gunicorn -c config/gunicorn.conf.py wsgi:app

CRITICAL: eventlet.monkey_patch() MUST be called before ANY other imports.
This ensures psycopg3 pool threads and Flask-SocketIO work correctly.
The GUNICORN_WORKER_CLASS env var is set in docker/.env.docker and the Dockerfile.
"""

import os

# Monkey-patch stdlib if using eventlet worker class.
# Must happen BEFORE any other imports (psycopg3, flask, etc.).
# In Docker: always set via Dockerfile ENV + .env.docker.
# In dev: not set, so no patching (flask dev server doesn't need it).
if os.environ.get('GUNICORN_WORKER_CLASS') == 'eventlet':
    import eventlet
    eventlet.monkey_patch()

from app import create_app, socketio
from app.core.bootstrap.extensions import db_pool, celery

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    app.run()
