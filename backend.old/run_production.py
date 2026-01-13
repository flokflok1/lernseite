#!/usr/bin/env python3
"""
LernsystemX Backend - Production Server Launcher

This script launches the Flask application using Gunicorn in production mode.

Usage:
    python run_production.py

Or directly with Gunicorn:
    gunicorn -c gunicorn.conf.py "app:create_app()"

Environment:
    FLASK_ENV=production or LSX_ENV=production

ISO 27001:2013 compliant - Production deployment
"""

import os
import sys

# Ensure we're in production mode
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('LSX_ENV', 'production')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create application instance
application = create_app('production')
app = application  # Alias for WSGI servers

if __name__ == '__main__':
    # This should not be used in production - use Gunicorn instead
    print("=" * 60)
    print("WARNING: This script should not be used directly in production!")
    print("Use Gunicorn instead:")
    print("  gunicorn -c gunicorn.conf.py 'run_production:application'")
    print("=" * 60)
    sys.exit(1)
