"""
LernsystemX API v1 Package

Complete flat structure with all packages consolidated under /api/v1/

Refactored: 2026-01-11 - All packages from core/, shared/, user/, system_features/
now unified under v1/ for flat, documentation-aligned structure.

Package Structure:
├── v1/
│   ├── /auth/              # Authentication
│   ├── /users/             # User management
│   ├── /profile/           # User profiles
│   ├── /courses/           # Course operations
│   ├── /chapters/          # Chapters
│   ├── /lessons/           # Lessons
│   ├── /exams/             # Exams
│   ├── /categories/        # Categories
│   ├── /learning_methods/  # Learning methods
│   ├── /subscriptions/     # Subscriptions
│   ├── /tokens_wallet/     # Token wallet
│   ├── /organisations/     # Organisation management
│   ├── /feedback/          # User feedback
│   ├── /tts/               # Text-to-Speech
│   ├── /dashboard/         # Dashboard widgets
│   ├── /tutor/             # AI Tutor
│   ├── /agents/            # Smart Agents
│   ├── /math/              # Math toolkit
│   ├── /analytics_system/  # Analytics
│   ├── /prompts_system/    # Prompt management
│   ├── /social/            # Social (feature-flagged)
│   ├── /community/         # Community
│   ├── /messaging/         # Messaging (feature-flagged)
│   ├── /admin/             # Admin API
│   ├── audio.py            # Audio processing (flat file)
│   ├── health.py           # Health checks
│   └── deprecation.py      # API deprecation
"""

# Core packages
from app.api.v1 import auth, health, deprecation

# User-facing packages
from app.api.v1 import (
    users, profile, courses, chapters, lessons, exams,
    categories, learning_methods, subscriptions, tokens_wallet,
    organisations, feedback, tts, dashboard
)

# System feature packages
from app.api.v1 import tutor, agents, math, analytics_system, prompts_system

# Admin Package
from app.api.v1 import admin

# Social/Community/Messaging Packages (feature-flagged)
try:
    from app.api.v1 import social
except ImportError:
    social = None

try:
    from app.api.v1 import community
except ImportError:
    community = None

try:
    from app.api.v1 import messaging
except ImportError:
    messaging = None

__all__ = [
    'auth', 'health', 'deprecation',
    'users', 'profile', 'courses', 'chapters', 'lessons', 'exams',
    'categories', 'learning_methods', 'subscriptions', 'tokens_wallet',
    'organisations', 'feedback', 'tts', 'dashboard',
    'tutor', 'agents', 'math', 'analytics_system', 'prompts_system',
    'admin', 'social', 'community', 'messaging'
]
