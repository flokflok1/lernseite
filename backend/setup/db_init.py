"""
LernsystemX Setup - Database Initialization

Handles complete database setup:
- Database creation (if not exists)
- Schema creation (all tables)
- Indexes for performance
- Row-Level Security policies
- Migration tracking

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

            # 6. Count created tables and indexes for reporting
            with psycopg.connect(self.conninfo) as conn:
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
                cursor.execute(f'CREATE DATABASE {self.db_name}')
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
        """Create migration tracking table"""
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS migration_history (
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

                CREATE INDEX IF NOT EXISTS idx_migration_version ON migration_history(version);
                CREATE INDEX IF NOT EXISTS idx_migration_executed_at ON migration_history(executed_at);
                CREATE INDEX IF NOT EXISTS idx_migration_status ON migration_history(status);
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
            backend_path = Path(__file__).parent.parent
            if str(backend_path) not in sys.path:
                sys.path.insert(0, str(backend_path))

            logger.info(f"[DB_INIT] Backend path: {backend_path}")
            logger.info(f"[DB_INIT] Migrations dir: {backend_path / 'migrations'}")

            # Connect and run migrations directly
            with psycopg.connect(self.conninfo) as conn:
                migrations_dir = backend_path / 'migrations'
                executed = []

                # Get all .sql files (exclude backups, verify scripts, and files starting with _)
                sql_files = sorted([
                    f for f in migrations_dir.glob('*.sql')
                    if not f.name.startswith('_')  # Exclude files starting with underscore
                    and 'verify' not in f.name.lower()  # Exclude verify scripts
                    and not f.name.endswith(('.bak', '.old', '.tmp'))  # Exclude backups
                ])

                logger.info(f"[DB_INIT] Found {len(sql_files)} migration files")
                if len(sql_files) == 0:
                    logger.error(f"[DB_INIT] ERROR: No migrations found in {migrations_dir}")
                    all_files = list(migrations_dir.glob('*.sql'))
                    logger.error(f"[DB_INIT] All SQL files: {[f.name for f in all_files]}")

                for sql_file in sql_files:
                    migration_name = sql_file.stem

                    # Check if already executed
                    with conn.cursor() as cur:
                        cur.execute(
                            "SELECT 1 FROM migration_history WHERE migration_name = %s",
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
                                INSERT INTO migration_history
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
        """Count total tables in database"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            """)
            return cur.fetchone()[0]

    def _count_indexes(self, conn) -> int:
        """Count total indexes in database"""
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*)
                FROM pg_indexes
                WHERE schemaname = 'public'
            """)
            return cur.fetchone()[0]

    # =========================================================================
    # Legacy Methods (Deprecated - kept for backwards compatibility)
    # =========================================================================
    # The following methods are deprecated and no longer used.
    # Database schema is now managed through migration files in backend/migrations/
    # These methods are kept for reference only.

    def _create_core_tables_legacy(self, conn) -> int:
        """
        [DEPRECATED] Create all core database tables

        This method is no longer used. Schema is now managed via migrations.
        Kept for backwards compatibility only.

        Args:
            conn: psycopg connection

        Returns:
            int: Number of tables created
        """
        tables_sql = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                role VARCHAR(50) NOT NULL DEFAULT 'user',
                organisation_id INTEGER,
                two_factor_enabled BOOLEAN DEFAULT FALSE,
                two_factor_secret VARCHAR(255),
                email_verified BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                last_login TIMESTAMP
            )
            """,

            # Roles table
            """
            CREATE TABLE IF NOT EXISTS roles (
                role_id SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                display_name VARCHAR(100) NOT NULL,
                description TEXT,
                hierarchy_level INTEGER NOT NULL,
                permissions JSONB,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,

            # Organisations table
            """
            CREATE TABLE IF NOT EXISTS organisations (
                organisation_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                type VARCHAR(50) NOT NULL,
                domain VARCHAR(255) UNIQUE,
                branding JSONB,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,

            # Courses table
            """
            CREATE TABLE IF NOT EXISTS courses (
                course_id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                creator_id INTEGER REFERENCES users(user_id),
                organisation_id INTEGER REFERENCES organisations(organisation_id),
                category_id INTEGER,
                language VARCHAR(2) DEFAULT 'de',
                difficulty VARCHAR(50),
                is_published BOOLEAN DEFAULT FALSE,
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,

            # Modules table
            """
            CREATE TABLE IF NOT EXISTS modules (
                module_id SERIAL PRIMARY KEY,
                course_id INTEGER REFERENCES courses(course_id) ON DELETE CASCADE,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                content JSONB,
                order_index INTEGER NOT NULL,
                duration_minutes INTEGER,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,

            # Learning Methods table
            """
            CREATE TABLE IF NOT EXISTS learning_methods (
                method_id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT,
                tier VARCHAR(50) NOT NULL DEFAULT 'basic',
                config JSONB,
                active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT check_tier CHECK (tier IN ('basic', 'premium', 'pro'))
            )
            """,

            # Token Wallets table
            """
            CREATE TABLE IF NOT EXISTS token_wallets (
                wallet_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id) UNIQUE,
                total_tokens INTEGER DEFAULT 0,
                used_tokens INTEGER DEFAULT 0,
                available_tokens INTEGER GENERATED ALWAYS AS (total_tokens - used_tokens) STORED,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,

            # Token Transactions table
            """
            CREATE TABLE IF NOT EXISTS token_transactions (
                transaction_id SERIAL PRIMARY KEY,
                wallet_id INTEGER REFERENCES token_wallets(wallet_id),
                user_id INTEGER REFERENCES users(user_id),
                amount INTEGER NOT NULL,
                transaction_type VARCHAR(50) NOT NULL,
                description TEXT,
                reference_id INTEGER,
                reference_type VARCHAR(50),
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,

            # Subscriptions table
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                subscription_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id) UNIQUE,
                plan VARCHAR(50) NOT NULL,
                status VARCHAR(50) NOT NULL,
                stripe_subscription_id VARCHAR(255),
                stripe_customer_id VARCHAR(255),
                current_period_start TIMESTAMP,
                current_period_end TIMESTAMP,
                cancel_at_period_end BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,

            # System Config table
            """
            CREATE TABLE IF NOT EXISTS system_config (
                config_id SERIAL PRIMARY KEY,
                key VARCHAR(255) UNIQUE NOT NULL,
                value TEXT,
                encrypted BOOLEAN DEFAULT FALSE,
                description TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,

            # Audit Log table
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id SERIAL PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                user_id INTEGER REFERENCES users(user_id),
                severity VARCHAR(50),
                ip_address VARCHAR(50),
                user_agent TEXT,
                details JSONB,
                created_at TIMESTAMP DEFAULT NOW()
            )
            """,

            # AI API Keys table (encrypted storage)
            """
            CREATE TABLE IF NOT EXISTS ai_api_keys (
                key_id SERIAL PRIMARY KEY,
                provider VARCHAR(50) UNIQUE NOT NULL,
                encrypted_key TEXT NOT NULL,
                salt VARCHAR(255) NOT NULL,
                metadata JSONB,
                active BOOLEAN DEFAULT TRUE,
                last_validated TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
            """,

            # Categories table (5-level hierarchy)
            """
            CREATE TABLE IF NOT EXISTS categories (
                category_id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                slug VARCHAR(255) UNIQUE NOT NULL,
                description TEXT,
                parent_id INTEGER REFERENCES categories(category_id) ON DELETE CASCADE,
                level INTEGER NOT NULL DEFAULT 1,
                icon VARCHAR(50),
                color VARCHAR(50),
                active BOOLEAN DEFAULT TRUE,
                order_index INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT check_level CHECK (level >= 1 AND level <= 5)
            )
            """,

            # Recovery Codes table (for account recovery)
            """
            CREATE TABLE IF NOT EXISTS recovery_codes (
                code_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
                code_hash VARCHAR(255) NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                used_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW(),
                expires_at TIMESTAMP DEFAULT (NOW() + INTERVAL '1 year')
            )
            """,

            # Dashboard Layouts table
            """
            CREATE TABLE IF NOT EXISTS dashboard_layouts (
                layout_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                organisation_id INTEGER REFERENCES organisations(organisation_id) ON DELETE SET NULL,
                role VARCHAR(50) NOT NULL,
                layout_json JSONB NOT NULL,
                source VARCHAR(20) NOT NULL DEFAULT 'user',
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT check_source CHECK (source IN ('system', 'role', 'organisation', 'user'))
            )
            """,

            # Analytics Events table
            """
            CREATE TABLE IF NOT EXISTS analytics_events (
                event_id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                organisation_id INTEGER REFERENCES organisations(organisation_id) ON DELETE SET NULL,
                event_type VARCHAR(100) NOT NULL,
                resource_type VARCHAR(100),
                resource_id INTEGER,
                payload JSONB,
                session_id VARCHAR(255),
                ip_address_hash VARCHAR(255),
                created_at TIMESTAMP DEFAULT NOW(),
                CONSTRAINT check_event_type CHECK (event_type IN (
                    'login', 'logout', 'page_view', 'course_view', 'course_enroll',
                    'module_start', 'module_complete', 'lesson_start', 'lesson_complete',
                    'method_execute', 'exam_start', 'exam_complete',
                    'liveroom_join', 'liveroom_leave', 'ki_job_start', 'ki_job_complete',
                    'purchase', 'subscription_start', 'subscription_cancel'
                ))
            )
            """
        ]

        created = 0

        with conn.cursor() as cur:
            for table_sql in tables_sql:
                try:
                    cur.execute(table_sql)
                    created += 1
                except Exception as e:
                    print(f"Table creation warning: {str(e)}")

        conn.commit()
        return created

    def _create_indexes_legacy(self, conn) -> int:
        """
        [DEPRECATED] Create performance indexes

        This method is no longer used. Indexes are now managed via migrations.
        Kept for backwards compatibility only.

        Args:
            conn: psycopg connection

        Returns:
            int: Number of indexes created
        """
        indexes_sql = [
            # User indexes
            "CREATE INDEX IF NOT EXISTS idx_user_email ON users(email)",
            "CREATE INDEX IF NOT EXISTS idx_user_role ON users(role)",
            "CREATE INDEX IF NOT EXISTS idx_user_org ON users(organisation_id)",
            "CREATE INDEX IF NOT EXISTS idx_user_active ON users(is_active)",

            # Course indexes
            "CREATE INDEX IF NOT EXISTS idx_course_creator ON courses(creator_id)",
            "CREATE INDEX IF NOT EXISTS idx_course_org ON courses(organisation_id)",
            "CREATE INDEX IF NOT EXISTS idx_course_category ON courses(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_course_published ON courses(is_published, published_at)",
            "CREATE INDEX IF NOT EXISTS idx_course_language ON courses(language)",

            # Module indexes
            "CREATE INDEX IF NOT EXISTS idx_module_course ON modules(course_id)",
            "CREATE INDEX IF NOT EXISTS idx_module_order ON modules(course_id, order_index)",

            # Organisation indexes
            "CREATE INDEX IF NOT EXISTS idx_org_domain ON organisations(domain) WHERE domain IS NOT NULL",
            "CREATE INDEX IF NOT EXISTS idx_org_type ON organisations(type)",

            # Token indexes
            "CREATE INDEX IF NOT EXISTS idx_token_wallet_user ON token_wallets(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_token_transaction_wallet ON token_transactions(wallet_id)",
            "CREATE INDEX IF NOT EXISTS idx_token_transaction_user ON token_transactions(user_id)",

            # Subscription indexes
            "CREATE INDEX IF NOT EXISTS idx_subscription_user ON subscriptions(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_subscription_status ON subscriptions(status)",

            # Audit log indexes
            "CREATE INDEX IF NOT EXISTS idx_audit_event ON audit_logs(event_type, created_at)",
            "CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id, created_at)",

            # AI API Keys indexes
            "CREATE INDEX IF NOT EXISTS idx_ai_api_provider ON ai_api_keys(provider)",
            "CREATE INDEX IF NOT EXISTS idx_ai_api_active ON ai_api_keys(active)",

            # Categories indexes
            "CREATE INDEX IF NOT EXISTS idx_category_slug ON categories(slug)",
            "CREATE INDEX IF NOT EXISTS idx_category_parent ON categories(parent_id)",
            "CREATE INDEX IF NOT EXISTS idx_category_level ON categories(level)",
            "CREATE INDEX IF NOT EXISTS idx_category_active ON categories(active)",

            # Recovery codes indexes
            "CREATE INDEX IF NOT EXISTS idx_recovery_user ON recovery_codes(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_recovery_used ON recovery_codes(used)",

            # Dashboard layout indexes
            "CREATE INDEX IF NOT EXISTS idx_dashboard_layout_user ON dashboard_layouts(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_dashboard_layout_source ON dashboard_layouts(source)",
            "CREATE INDEX IF NOT EXISTS idx_dashboard_layout_role ON dashboard_layouts(role)",

            # Analytics events indexes
            "CREATE INDEX IF NOT EXISTS idx_analytics_user ON analytics_events(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_org ON analytics_events(organisation_id)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_event_type ON analytics_events(event_type)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_resource ON analytics_events(resource_type, resource_id)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_created_at ON analytics_events(created_at DESC)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_user_created ON analytics_events(user_id, created_at DESC)",
        ]

        created = 0

        with conn.cursor() as cur:
            for index_sql in indexes_sql:
                try:
                    cur.execute(index_sql)
                    created += 1
                except Exception as e:
                    # Index might already exist, that's OK
                    pass

        conn.commit()
        return created

    def _verify_schema_legacy(self, conn) -> bool:
        """
        [DEPRECATED] Verify database schema is correct

        This method is no longer used. Schema verification is now handled by migrations.
        Kept for backwards compatibility only.

        Args:
            conn: psycopg connection

        Returns:
            bool: True if all expected tables exist
        """
        expected_tables = [
            'users', 'roles', 'organisations', 'courses', 'modules',
            'learning_methods', 'token_wallets', 'token_transactions',
            'subscriptions', 'system_config', 'audit_logs',
            'migration_history', 'ai_api_keys', 'categories', 'recovery_codes',
            'dashboard_layouts', 'analytics_events'
        ]

        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            existing_tables = [row[0] for row in cur.fetchall()]

        missing = [t for t in expected_tables if t not in existing_tables]

        if missing:
            print(f"Missing tables: {missing}")
            return False

        return True

    def rollback(self):
        """
        Rollback database changes (DANGEROUS - use with caution)

        Only use during development or when setup fails critically.
        """
        print("WARNING: Rolling back database changes...")

        with psycopg.connect(self.conninfo) as conn:
            with conn.cursor() as cur:
                # Drop all tables
                cur.execute("DROP SCHEMA public CASCADE")
                cur.execute("CREATE SCHEMA public")
            conn.commit()

        print("Database rolled back successfully")


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
