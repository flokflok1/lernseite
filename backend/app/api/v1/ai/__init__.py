"""
AI API Package

Feature-based structure with role separation (Phase 2 Consolidation).

Structure:
├── admin/                   # Admin AI management
│   ├── models/             # AI model management (4 files, 964 LOC)
│   │   ├── crud.py         # Model CRUD operations
│   │   ├── defaults.py     # Default model configuration
│   │   ├── sync.py         # Model synchronization
│   │   └── usage.py        # Model usage tracking
│   ├── providers/          # AI provider management (4 files, 990 LOC)
│   │   ├── api_keys.py     # Provider API key management
│   │   ├── crud.py         # Provider CRUD operations
│   │   ├── health.py       # Provider health checks
│   │   └── testing.py      # Provider testing utilities
│   ├── jobs/               # AI job management (3 files, 831 LOC)
│   │   ├── creation.py     # Job creation
│   │   ├── management.py   # Job management
│   │   └── finalization.py # Job finalization
│   ├── pricing/            # AI pricing (1 file, 522 LOC)
│   │   └── pricing.py      # Pricing configuration
│   ├── profiles/           # AI model profiles (1 file, 320 LOC)
│   │   └── profiles.py     # Model profile management
│   ├── stats/              # AI usage statistics (1 file, 102 LOC)
│   │   └── usage.py        # Usage statistics
│   └── core/               # Core AI services (5 files, 1409 LOC)
│       ├── events.py       # Event handling
│       ├── factory.py      # Factory pattern implementations
│       ├── services.py     # Core services
│       └── value_objects.py # Value objects
│
└── user/                    # User AI endpoints
    └── agents.py           # AI agents (344 LOC)

Consolidated from:
- api/v1/admin/settings/ai/ → ai/admin/
- api/v1/ai/agents.py → ai/user/agents.py

Total: ~5587 LOC in organized feature-based structure

All routes:
- /api/v1/ai/admin/{models,providers,jobs,pricing,profiles,stats}/*
- /api/v1/ai/* (user agents - existing)

Part of: Phase 2 AI Consolidation (Feature-based structure)
"""

from app.api.v1.ai import admin, user

__all__ = ['admin', 'user']
