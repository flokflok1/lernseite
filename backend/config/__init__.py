"""
LernsystemX Backend Configuration Module

Centralized configuration management for:
- Gunicorn server configuration (production)
- Logging configuration
- Environment variables
"""

import os
from pathlib import Path

# Get root directory
ROOT_DIR = Path(__file__).parent.parent

# Environment variables
def load_env_vars():
    """Load environment variables from .env file."""
    env_file = ROOT_DIR / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)

# Load environment on import
load_env_vars()
