"""
LernsystemX Setup - Database Migrations

Migration runner integrated with Setup Wizard for:
- Listing available migrations
- Running pending migrations
- Migration history tracking
- Rollback capabilities

Based on database-migration-strategy.md (Phase 22)
Phase 23 - Setup Wizard Erweiterungen
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import os
import hashlib
from flask import current_app


@dataclass
class Migration:
    """Represents a database migration"""
    migration_id: str
    name: str
    version: str
    description: Optional[str]
    up_sql_path: str
    down_sql_path: str
    applied: bool
    applied_at: Optional[str]
    checksum: Optional[str]
    execution_time_ms: Optional[int]


class MigrationManager:
    """
    Database migration manager for LernsystemX.

    Handles migration discovery, execution, and tracking based on
    the migration strategy defined in database-migration-strategy.md
    """

    MIGRATIONS_DIR = "migrations"
    MIGRATION_NAMING_PATTERN = "{timestamp}_{sequence}_{description}_{direction}.sql"

    @staticmethod
    def get_migrations_directory() -> Path:
        """
        Get path to migrations directory.

        Returns:
            Path to migrations directory
        """
        backend_root = Path(__file__).parent.parent
        migrations_path = backend_root / MigrationManager.MIGRATIONS_DIR

        # Create if doesn't exist
        migrations_path.mkdir(exist_ok=True)

        return migrations_path

    @staticmethod
    def calculate_file_checksum(filepath: str) -> str:
        """
        Calculate SHA-256 checksum of migration file.

        Args:
            filepath: Path to migration file

        Returns:
            SHA-256 hash as hex string
        """
        sha256 = hashlib.sha256()

        with open(filepath, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()

    @staticmethod
    def discover_migrations() -> List[Migration]:
        """
        Discover all migration files in migrations directory.

        Supports two naming patterns:
        1. New pattern: {number}_{description}.sql (e.g., 001_core_users_roles.sql)
        2. Legacy pattern: {timestamp}_{sequence}_{description}_up.sql + _down.sql

        Returns:
            List of discovered migrations
        """
        migrations_dir = MigrationManager.get_migrations_directory()
        migrations: Dict[str, Migration] = {}

        # First, try to find new-style numbered migrations (001-071)
        # Support subdirectories with **/ glob pattern
        # IMPORTANT: Sort by filename (number) not by path!
        for migration_file in sorted(
            migrations_dir.glob("**/[0-9][0-9][0-9]_*.sql"),
            key=lambda p: p.name  # Sort by filename only (001_..., 002_..., etc.)
        ):
            # Skip verify_schema.sql and other non-migration files
            if migration_file.name.startswith('verify_'):
                continue

            # Parse filename: 001_core_users_roles.sql
            filename = migration_file.stem  # Without .sql extension
            parts = filename.split('_', 1)  # Split only on first underscore

            if len(parts) < 2:
                current_app.logger.warning(f"Invalid migration filename: {migration_file.name}")
                continue

            sequence = parts[0]  # e.g., "001"
            description = parts[1]  # e.g., "core_users_roles"

            # Build migration ID
            migration_id = filename

            # Extract version and description from SQL file header
            version = MigrationManager._extract_version_from_sql(str(migration_file))
            desc = MigrationManager._extract_description_from_sql(str(migration_file))

            # Calculate checksum
            checksum = MigrationManager.calculate_file_checksum(str(migration_file))

            migrations[migration_id] = Migration(
                migration_id=migration_id,
                name=description.replace('_', ' ').title(),
                version=version or "1.0.0",
                description=desc,
                up_sql_path=str(migration_file),
                down_sql_path=None,  # New migrations don't have down scripts
                applied=False,  # Will be updated from DB
                applied_at=None,
                checksum=checksum,
                execution_time_ms=None
            )

        # Fallback: Find legacy _up.sql files if no numbered migrations found
        if not migrations:
            for up_file in migrations_dir.glob("*_up.sql"):
                # Parse filename
                # Example: 20250115_001_add_course_version_up.sql
                filename = up_file.stem  # Without .sql extension
                parts = filename.split('_')

                if len(parts) < 4:
                    current_app.logger.warning(f"Invalid migration filename: {up_file.name}")
                    continue

                timestamp = parts[0]
                sequence = parts[1]
                description = '_'.join(parts[2:-1])  # Everything between sequence and 'up'

                # Build migration ID
                migration_id = f"{timestamp}_{sequence}_{description}"

                # Find corresponding down file
                down_file = migrations_dir / f"{migration_id}_down.sql"

                if not down_file.exists():
                    current_app.logger.warning(f"Missing down migration for: {migration_id}")
                    down_file_path = None
                else:
                    down_file_path = str(down_file)

                # Extract version from SQL file (if present in header)
                version = MigrationManager._extract_version_from_sql(str(up_file))

                # Calculate checksum
                checksum = MigrationManager.calculate_file_checksum(str(up_file))

                migrations[migration_id] = Migration(
                    migration_id=migration_id,
                    name=description.replace('_', ' ').title(),
                    version=version or "unknown",
                    description=MigrationManager._extract_description_from_sql(str(up_file)),
                    up_sql_path=str(up_file),
                    down_sql_path=down_file_path,
                    applied=False,  # Will be updated from DB
                    applied_at=None,
                    checksum=checksum,
                    execution_time_ms=None
                )

        return list(migrations.values())

    @staticmethod
    def _extract_version_from_sql(filepath: str) -> Optional[str]:
        """
        Extract version from SQL file header comment.

        Looks for: -- Version: 1.6.0

        Args:
            filepath: Path to SQL file

        Returns:
            Version string or None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('-- Version:'):
                        return line.split(':')[1].strip()
                    # Stop after first 10 lines (header)
                    if not line.startswith('--'):
                        break
        except Exception:
            pass

        return None

    @staticmethod
    def _extract_description_from_sql(filepath: str) -> Optional[str]:
        """
        Extract description from SQL file header comment.

        Looks for: -- Description: ...

        Args:
            filepath: Path to SQL file

        Returns:
            Description string or None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('-- Description:'):
                        return line.split(':')[1].strip()
                    if not line.startswith('--'):
                        break
        except Exception:
            pass

        return None

    @staticmethod
    def get_applied_migrations() -> Dict[str, Dict[str, Any]]:
        """
        Get list of already applied migrations from migration_history table.

        Returns:
            Dictionary mapping migration_id to migration info
        """
        from app.extensions import db_pool

        applied = {}

        try:
            with db_pool.connection() as conn:
                with conn.cursor() as cur:
                    # Check if migration_history exists
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables
                            WHERE table_name = 'migration_history'
                        );
                    """)
                    has_table = cur.fetchone()[0]

                    if not has_table:
                        current_app.logger.info("migration_history table does not exist yet")
                        return applied

                    # Get all applied migrations
                    cur.execute("""
                        SELECT migration_name, version, executed_at, execution_time_ms
                        FROM migration_history
                        ORDER BY executed_at ASC;
                    """)

                    for row in cur.fetchall():
                        applied[row[0]] = {
                            "version": row[1],
                            "executed_at": row[2].isoformat() if row[2] else None,
                            "execution_time_ms": row[3]
                        }

        except Exception as e:
            current_app.logger.error(f"Failed to get applied migrations: {str(e)}")

        return applied

    @staticmethod
    def list_migrations() -> List[Dict[str, Any]]:
        """
        List all migrations with their status (applied/pending).

        Returns:
            List of migration dictionaries
        """
        # Discover all migration files
        discovered = MigrationManager.discover_migrations()

        # Get applied migrations from DB
        applied = MigrationManager.get_applied_migrations()

        # Merge information
        migrations = []
        for migration in discovered:
            applied_info = applied.get(migration.migration_id)

            migrations.append({
                "migration_id": migration.migration_id,
                "name": migration.name,
                "version": migration.version,
                "description": migration.description,
                "applied": migration.migration_id in applied,
                "applied_at": applied_info["executed_at"] if applied_info else None,
                "execution_time_ms": applied_info["execution_time_ms"] if applied_info else None,
                "checksum": migration.checksum,
                "has_rollback": migration.down_sql_path is not None
            })

        # Sort by migration_id (chronological order)
        migrations.sort(key=lambda m: m["migration_id"])

        return migrations

    @staticmethod
    def run_migration(migration_id: str, user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Run a single migration.

        Args:
            migration_id: Migration identifier
            user_id: User executing the migration (optional)

        Returns:
            Dictionary with execution result
        """
        from app.extensions import db_pool
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
            with db_pool.connection() as conn:
                with conn.cursor() as cur:
                    # Execute migration SQL
                    cur.execute(up_sql)

                    execution_time_ms = int((time.time() - start_time) * 1000)

                    # Ensure migration_history table exists
                    MigrationManager._ensure_migration_history_table(cur)

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

    @staticmethod
    def run_pending_migrations(user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Run all pending migrations in order.

        Args:
            user_id: User executing the migrations (optional)

        Returns:
            Dictionary with execution results
        """
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

            result = MigrationManager.run_migration(migration["migration_id"], user_id)

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

    @staticmethod
    def _ensure_migration_history_table(cursor):
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
