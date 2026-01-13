"""
Agents API Package

Feature-based structure (flattened role-based admin/core, kept feature subdirectories):

**Flat files (from role-based structure):**
- admin_management.py: Admin agent management (83 LOC)
  - From admin/management.py

- engine.py: Agent engine core (219 LOC)
  - From core/engine.py

- factory.py: Agent factory (376 LOC)
  - From core/factory.py

**Feature subdirectories (TRUE FEATURES - kept separate):**
- audio/: Audio processing feature
  - processing.py (171 LOC)

- knowledge/: Knowledge base feature
  - base.py (222 LOC)

- media/: Media handling feature
  - handling.py (100 LOC)

**Helpers:**
- _helpers.py: Shared helper functions

Total: 1171 LOC (flat files: 678 LOC, feature subdirs: 493 LOC)

Architecture Pattern:
- Role-based subdirectories (admin/, core/) → Flattened
- Feature subdirectories (audio/, knowledge/, media/) → Kept (like math/calculator/)

All routes: /api/v1/agents/*
"""

from app.api.v1.agents import (
    admin_management,
    engine,
    factory,
    audio,
    knowledge,
    media
)

__all__ = [
    'admin_management',
    'engine',
    'factory',
    'audio',
    'knowledge',
    'media'
]
