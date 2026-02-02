"""
LernsystemX Setup - Database Initialization (Modern Migration-Based)

Handles complete database setup using migration system:
- Database creation (if not exists)
- PostgreSQL extensions (uuid-ossp, pgcrypto)
- Migration table creation for tracking
- Migration execution from SQL files in backend/migrations/

Legacy deprecated methods (no longer used) are in:
- app.setup.db_init_legacy - DatabaseInitializerLegacy class

Modern database schema is managed through migration files in backend/migrations/
These keep the schema version-controlled and provide rollback capabilities.

ISO/IEC/IEEE 26515:2018 compliant - Database setup documentation
"""

import os
import logging
from typing import Dict
from datetime import datetime

import psycopg

# Setup logger
logger = logging.getLogger(__name__)


class DatabaseInitializer:
    """
    Initialize complete database schema using pure psycopg

    Implements idempotent setup - can be run multiple times safely.
    All operations are tracked in migration_history table.
    """

    def __init__(self, db_host=None, db_port=None, db_user=None, db_password=None, db_name=None):
        """
        Initialize database connection parameters

        Args:
            db_host: Database host (defaults to env DB_HOST or 'localhost')
            db_port: Database port (defaults to env DB_PORT or 5432)
            db_user: Database user (defaults to env DB_USER or 'postgres')
            db_password: Database password (defaults to env DB_PASSWORD or '')
            db_name: Database name (defaults to env DB_NAME or 'lernsystemx_dev')
        """
        # Use provided credentials or fallback to environment variables
        self.db_host = db_host or os.getenv('DB_HOST', 'localhost')
        self.db_port = int(db_port or os.getenv('DB_PORT', 5432))
        self.db_user = db_user or os.getenv('DB_USER', 'postgres')
        self.db_password = db_password or os.getenv('DB_PASSWORD', '')
        self.db_name = db_name or os.getenv('DB_NAME', 'lernsystemx_dev')

        # Build connection info
        self.conninfo = (
            f"host={self.db_host} port={self.db_port} "
            f"user={self.db_user} password={self.db_password} "
            f"dbname={self.db_name}"
        )

    def initialize(self) -> Dict[str, any]:
        """
        Run full database initialization using migration system

        Returns:
            Dict with results:
            - success: bool
            - database_created: bool
            - migrations_executed: int
            - schemas_created: int
            - tables_created: int
            - indexes_created: int
            - errors: List[str]

        Example:
            >>> db_init = DatabaseInitializer()
            >>> results = db_init.initialize()
            >>> if results['success']:
            ...     print("Database ready!")
        """
        results = {
            'success': False,
            'database_created': False,
            'migrations_executed': 0,
            'schemas_created': 0,
            'tables_created': 0,
            'indexes_created': 0,
            'errors': []
        }

        try:
            # 1. Create database if not exists
            db_created = self._create_database_if_not_exists()
            results['database_created'] = db_created

            # 2. Connect to database and enable required extensions
            with psycopg.connect(self.conninfo) as conn:
                # 3. Enable PostgreSQL extensions
                self._enable_extensions(conn)

                # 4. Create migration history table
                self._create_migration_table(conn)

            # 5. Run all pending migrations using MigrationManager
            migration_result = self._run_migrations()

            if migration_result['success']:
                results['migrations_executed'] = len(migration_result.get('executed', []))
                results['success'] = True
            else:
                results['errors'].append(f"Migration failed: {migration_result.get('error', 'Unknown error')}")
                return results

            # 6. Count created schemas, tables and indexes for reporting
            with psycopg.connect(self.conninfo) as conn:
                results['schemas_created'] = self._count_schemas(conn)
                results['tables_created'] = self._count_tables(conn)
                results['indexes_created'] = self._count_indexes(conn)

        except Exception as e:
            results['errors'].append(f'Database initialization error: {str(e)}')

        return results

    def _create_database_if_not_exists(self) -> bool:
        """Create database if it doesn't exist"""
        try:
            # Connect to default 'postgres' database
            conn = psycopg.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                dbname='postgres',
                autocommit=True
            )

            cursor = conn.cursor()

            # Check if database exists
            cursor.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s",
                (self.db_name,)
            )

            exists = cursor.fetchone() is not None

            if not exists:
                # Create database
                from psycopg import sql
                cursor.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(self.db_name)
                    )
                )
                cursor.close()
                conn.close()
                return True
            else:
                cursor.close()
                conn.close()
                return False

        except Exception as e:
            raise Exception(f'Database creation failed: {str(e)}')

    def _create_migration_table(self, conn):
        """Create migration tracking table in core schema"""
        with conn.cursor() as cur:
            # Ensure core schema exists first
            cur.execute("CREATE SCHEMA IF NOT EXISTS core;")

            cur.execute("""
                CREATE TABLE IF NOT EXISTS core.migration_history (
                    migration_id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) NOT NULL UNIQUE,
                    version VARCHAR(50),
                    executed_at TIMESTAMPTZ DEFAULT NOW(),
                    execution_time_ms INTEGER,
                    executed_by INTEGER,
                    environment VARCHAR(50) DEFAULT 'production',
                    status VARCHAR(20) DEFAULT 'success',
                    error_message TEXT,
                    CONSTRAINT chk_migration_status CHECK (status IN ('success', 'failed', 'rolled_back'))
                );

                CREATE INDEX IF NOT EXISTS idx_migration_version ON core.migration_history(version);
                CREATE INDEX IF NOT EXISTS idx_migration_executed_at ON core.migration_history(executed_at);
                CREATE INDEX IF NOT EXISTS idx_migration_status ON core.migration_history(status);
            """)
        conn.commit()

    def _enable_extensions(self, conn):
        """Enable required PostgreSQL extensions"""
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
            cur.execute("CREATE EXTENSION IF NOT EXISTS \"pgcrypto\";")
        conn.commit()

    def _run_migrations(self) -> Dict[str, any]:
        """Run all pending migrations directly from SQL files"""
        try:
            import sys
            from pathlib import Path
            import time

            # Add backend directory to path
            backend_path = Path(__file__).parent.parent.parent
            if str(backend_path) not in sys.path:
                sys.path.insert(0, str(backend_path))

            logger.info(f"[DB_INIT] Backend path: {backend_path}")
            logger.info(f"[DB_INIT] Migrations dir: {backend_path / 'migrations'}")

            # Connect and run migrations directly
            with psycopg.connect(self.conninfo) as conn:
                migrations_dir = backend_path / 'migrations'
                executed = []

                # Get all .sql files recursively from subdirectories (exclude backups, verify scripts, and files starting with _)
                all_sql_files = [
                    f for f in migrations_dir.glob('**/*.sql')  # Recursive search in subdirectories
                    if not f.name.startswith('_')  # Exclude files starting with underscore
                    and 'verify' not in f.name.lower()  # Exclude verify scripts
                    and not f.name.endswith(('.bak', '.old', '.tmp'))  # Exclude backups
                ]

                # Sort by folder number, then filename number to preserve correct order
                # This ensures: 01_Core infrastructure -> 02_Content -> ... -> 00_Seeds (last)
                def get_sort_key(filepath):
                    """
                    Generate sort key: tuple of (folder_priority, folder_number, migration_number)
                    This ensures infrastructure migrations run before content, and seeds run last.
                    """
                    import re
                    relative = filepath.relative_to(migrations_dir)
                    parts = relative.parts  # e.g., ('01_Core', '000_functions.sql')

                    folder = parts[0] if len(parts) > 1 else ''
                    filename = parts[-1]

                    # Extract folder number
                    folder_match = re.match(r'^(\d+)', folder)
                    folder_num = int(folder_match.group(1)) if folder_match else 999

                    # Special handling: 00_Seeds should run LAST (after 01-12)
                    # So we give it priority 999 to sort after all numbered folders
                    if folder_num == 0:  # 00_Seeds
                        folder_priority = 999
                    else:
                        folder_priority = folder_num

                    # Extract migration number from filename
                    filename_match = re.match(r'^(\d+)', filename.replace('.sql', ''))
                    migration_num = int(filename_match.group(1)) if filename_match else 999

                    return (folder_priority, migration_num, filename)

                sql_files = sorted(all_sql_files, key=get_sort_key)

                logger.info(f"[DB_INIT] Found {len(sql_files)} migration files")
                logger.info(f"[DB_INIT] NEW SORTING APPLIED - First 20 migrations:")
                for i, f in enumerate(sql_files[:20]):
                    sort_key = get_sort_key(f)
                    logger.info(f"[DB_INIT]   {i+1}. {f.stem:60} key={sort_key}")
                if len(sql_files) == 0:
                    logger.error(f"[DB_INIT] ERROR: No migrations found in {migrations_dir}")
                    all_files = list(migrations_dir.glob('*.sql'))
                    logger.error(f"[DB_INIT] All SQL files: {[f.name for f in all_files]}")

                for sql_file in sql_files:
                    migration_name = sql_file.stem

                    # Check if already executed
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT 1 FROM core.migration_history WHERE migration_name = %s",
                            (migration_name,)
                        )
                        if cur.fetchone():
                            continue  # Already executed

                    # Execute migration
                    logger.info(f"[DB_INIT] Running migration: {migration_name}")
                    with open(sql_file, 'r', encoding='utf-8') as f:
                        sql = f.read()

                    logger.info(f"[DB_INIT] SQL length: {len(sql)} bytes")

                    try:
                        start = time.time()

                        with conn.cursor() as cur:
                            cur.execute(sql)

                        execution_time = int((time.time() - start) * 1000)

                        # Record in history
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO core.migration_history
                                (migration_name, executed_at, execution_time_ms, status)
                                VALUES (%s, NOW(), %s, 'success')
                            """, (migration_name, execution_time))

                        conn.commit()
                        executed.append(migration_name)
                        logger.info(f"✓ {migration_name} ({execution_time}ms)")

                    except Exception as e:
                        conn.rollback()
                        return {
                            'success': False,
                            'error': f'Migration {migration_name} failed: {str(e)}',
                            'executed': executed
                        }

                return {
                    'success': True,
                    'executed': executed,
                    'message': f'{len(executed)} migrations executed'
                }

        except Exception as e:
            import traceback
            return {
                'success': False,
                'error': f'Migration execution failed: {str(e)}',
                'traceback': traceback.format_exc(),
                'executed': []
            }

    def _count_tables(self, conn) -> int:
        """Count total tables in database across all application schemas"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
                  AND table_type = 'BASE TABLE'
            """)
            return cur.fetchone()[0]

    def _count_indexes(self, conn) -> int:
        """Count total indexes in database across all application schemas"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM pg_indexes
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
            """)
            return cur.fetchone()[0]

    def _count_schemas(self, conn) -> int:
        """Count total application schemas (excluding system schemas)"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.schemata
                WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            """)
            return cur.fetchone()[0]


# Convenience function
def initialize_database() -> Dict:
    """
    Quick database initialization

    Returns:
        Dict: Initialization results

    Example:
        >>> results = initialize_database()
        >>> print(results['tables_created'])
    """
    db_init = DatabaseInitializer()
    return db_init.initialize()
