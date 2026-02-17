"""
LernsystemX Setup - Initialization Package

Re-exports:
- MigrationManager with execution methods from migrations_part2.py
- KISetup (full class) from ai_part2.py (inherits ai.py base)
"""

from app.setup.initialization.migrations import Migration, MigrationManager
from app.setup.initialization.migrations_part2 import (
    run_migration,
    run_pending_migrations,
    _ensure_migration_history_table,
)
from app.setup.initialization.ai import KISetup as KISetupBase  # noqa: F401
from app.setup.initialization.ai_part2 import KISetup  # noqa: F401

# Attach execution methods to MigrationManager as static methods
# so all consumers can use MigrationManager.run_migration() etc.
MigrationManager.run_migration = staticmethod(run_migration)
MigrationManager.run_pending_migrations = staticmethod(run_pending_migrations)
MigrationManager._ensure_migration_history_table = staticmethod(_ensure_migration_history_table)

__all__ = [
    "Migration",
    "MigrationManager",
    "KISetup",
    "KISetupBase",
]
