"""
WSGI Entry Point for Production Deployment

Used by Gunicorn:
    gunicorn -c config/gunicorn.conf.py wsgi:app

Or with eventlet worker for WebSocket support:
    gunicorn -c config/gunicorn.conf.py -k eventlet wsgi:app
"""

from app import create_app

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    app.run()
