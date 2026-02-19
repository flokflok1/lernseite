"""
LernsystemX Setup - Database Migration Execution

Continuation of migrations.py (Part 2).
Contains migration execution methods:
- run_migration: Execute a single migration
- run_pending_migrations: Execute all pending migrations
- _ensure_migration_history_table: Create tracking table if needed

These functions are attached to MigrationManager as static methods
via the __init__.py barrel export.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from flask import current_app


def run_migration(migration_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Run a single migration.

    Args:
        migration_id: Migration identifier
        user_id: User executing the migration (optional)

    Returns:
        Dictionary with execution result
    """
    from app.core.bootstrap import extensions
    from app.setup.initialization.migrations import MigrationManager
    import time

    # Find migration
    discovered = MigrationManager.discover_migrations()
    migration = next((m for m in discovered if m.migration_id == migration_id), None)

    if not migration:
        return {
            "success": False,
            "error": f"Migration not found: {migration_id}"
        }

    # Check if already applied
    applied = MigrationManager.get_applied_migrations()
    if migration_id in applied:
        return {
            "success": False,
            "error": f"Migration already applied: {migration_id}",
            "applied_at": applied[migration_id]["executed_at"]
        }

    # Read SQL file
    try:
        with open(migration.up_sql_path, 'r', encoding='utf-8') as f:
            up_sql = f.read()
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read migration file: {str(e)}"
        }

    # Execute migration
    start_time = time.time()

    try:
        with extensions.db_pool.connection() as conn:
            with conn.cursor() as cur:
                # Execute migration SQL
                cur.execute(up_sql)

                execution_time_ms = int((time.time() - start_time) * 1000)

                # Ensure migration_history table exists
                _ensure_migration_history_table(cur)

                # Record in migration history
                cur.execute("""
                    INSERT INTO migration_history (
                        migration_name,
                        version,
                        executed_at,
                        execution_time_ms,
                        executed_by,
                        environment,
                        status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (
                    migration_id,
                    migration.version,
                    datetime.utcnow(),
                    execution_time_ms,
                    user_id,
                    current_app.config.get('LSX_ENV', 'production'),
                    'success'
                ))

            conn.commit()

        return {
            "success": True,
            "migration_id": migration_id,
            "execution_time_ms": execution_time_ms
        }

    except Exception as e:
        current_app.logger.error(f"Migration failed: {migration_id} - {str(e)}")
        return {
            "success": False,
            "error": f"Migration execution failed: {str(e)}"
        }


def run_pending_migrations(user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Run all pending migrations in order.

    Args:
        user_id: User executing the migrations (optional)

    Returns:
        Dictionary with execution results
    """
    from app.setup.initialization.migrations import MigrationManager

    migrations = MigrationManager.list_migrations()
    pending = [m for m in migrations if not m["applied"]]

    if not pending:
        return {
            "success": True,
            "message": "No pending migrations",
            "executed": []
        }

    executed = []
    failed = None

    for migration in pending:
        current_app.logger.info(f"Running migration: {migration['migration_id']}")

        result = run_migration(migration["migration_id"], user_id)

        if result["success"]:
            executed.append({
                "migration_id": migration["migration_id"],
                "execution_time_ms": result["execution_time_ms"]
            })
        else:
            failed = {
                "migration_id": migration["migration_id"],
                "error": result["error"]
            }
            break  # Stop on first failure

    if failed:
        return {
            "success": False,
            "message": f"Migration failed: {failed['migration_id']}",
            "error": failed["error"],
            "executed": executed,
            "failed_migration": failed["migration_id"]
        }

    return {
        "success": True,
        "message": f"Successfully executed {len(executed)} migration(s)",
        "executed": executed
    }


def _ensure_migration_history_table(cursor) -> None:
    """
    Ensure migration_history table exists.

    Args:
        cursor: Database cursor
    """
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS migration_history (
            migration_id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            version VARCHAR(20) NOT NULL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            execution_time_ms INTEGER,
            executed_by INTEGER,
            environment VARCHAR(50) DEFAULT 'production',
            status VARCHAR(20) DEFAULT 'success',
            error_message TEXT,
            CONSTRAINT chk_migration_status CHECK (status IN ('success', 'failed', 'rolled_back'))
        );

        CREATE INDEX IF NOT EXISTS idx_migration_version ON migration_history(version);
        CREATE INDEX IF NOT EXISTS idx_migration_executed_at ON migration_history(executed_at);
        CREATE INDEX IF NOT EXISTS idx_migration_status ON migration_history(status);
    """)
