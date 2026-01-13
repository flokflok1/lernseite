"""
Exams API Package

Feature-based structure (flattened from admin/core/user structure):
- admin_context.py: Admin exam context management (68 LOC)
  - From admin/context.py

- admin_generation.py: Admin exam generation (82 LOC)
  - From admin/generation.py

- models.py: Exam data models (162 LOC)
  - From core/models.py

- value_objects.py: Value object definitions (276 LOC)
  - From core/value_objects.py

- factory.py: Exam object factory (386 LOC)
  - From core/factory.py

- services.py: Exam services (547 LOC)
  - From core/services.py

- user_profile.py: User exam profile (158 LOC)
  - From user/user_profile.py

- user_attempts.py: User exam attempts (237 LOC)
  - From user/attempts.py

- user_simulations.py: Exam simulations (367 LOC)
  - From user/simulations.py

Total: 2283 LOC across 9 feature files

All routes: /api/v1/exams/*
"""

from app.api.v1.exams import (
    admin_context,
    admin_generation,
    models,
    value_objects,
    factory,
    services,
    user_profile,
    user_attempts,
    user_simulations
)

__all__ = [
    'admin_context',
    'admin_generation',
    'models',
    'value_objects',
    'factory',
    'services',
    'user_profile',
    'user_attempts',
    'user_simulations'
]
