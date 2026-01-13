"""
LernsystemX System Features API Package

System-level features that provide infrastructure capabilities.

Package Structure:
├── ai/               # AI Operations (models, jobs, pricing, profiles)
├── agents/           # AI Agents System
├── analytics/        # Analytics Features
├── learning_methods/ # Learning Methods Core
├── math/             # Math Toolkit
├── prompts/          # Prompt Management
└── tutor/            # AI Tutor Features

Uses:
- Flask Blueprints for modular routing
- Repository Pattern (no ORM)
- Domain-Driven Design (DDD)
"""

from flask import Blueprint

# Create system_features blueprint
system_features_bp = Blueprint(
    'system_features',
    __name__,
    url_prefix='/api/v1'
)

# Import AI features (models, jobs, pricing, profiles)
try:
    from app.api.system_features import ai
except ImportError as e:
    print(f"Warning: AI features import failed: {e}")
    ai = None

# Import other system features
try:
    from app.api.system_features import agents
except ImportError as e:
    print(f"Warning: Agents features import failed: {e}")
    agents = None

try:
    from app.api.system_features import analytics
except ImportError as e:
    print(f"Warning: Analytics features import failed: {e}")
    analytics = None

try:
    from app.api.system_features import learning_methods
except ImportError as e:
    print(f"Warning: Learning Methods features import failed: {e}")
    learning_methods = None

try:
    from app.api.system_features import math
except ImportError as e:
    print(f"Warning: Math features import failed: {e}")
    math = None

try:
    from app.api.system_features import prompts
except ImportError as e:
    print(f"Warning: Prompts features import failed: {e}")
    prompts = None

try:
    from app.api.system_features import tutor
except ImportError as e:
    print(f"Warning: Tutor features import failed: {e}")
    tutor = None

__all__ = [
    'system_features_bp',
    'ai',
    'agents',
    'analytics',
    'learning_methods',
    'math',
    'prompts',
    'tutor'
]
