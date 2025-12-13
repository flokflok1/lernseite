#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LernsystemX Database Reset Script (Automated)

Drops and recreates the database using environment variables.
"""

import os
import sys
import psycopg
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def reset_database():
    """Drop and recreate the database - automated with env vars"""

    print()
    print("=" * 80)
    print("  LernsystemX - Automated Database Reset")
    print("=" * 80)
    print()

    # Get credentials from environment
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = int(os.getenv('DB_PORT', 5432))
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'lernsystemx_dev')

    print(f"  Host:       {db_host}:{db_port}")
    print(f"  User:       {db_user}")
    print(f"  Database:   {db_name}")
    print()
    print("=" * 80)
    print()

    try:
        # Connect to default postgres database
        print(f"  → Connecting to PostgreSQL...")
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname='postgres',
            autocommit=True
        )

        cursor = conn.cursor()

        # Terminate existing connections
        print(f"  → Terminating active connections to '{db_name}'...")
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_name}'
            AND pid <> pg_backend_pid();
        """)

        # Drop database
        print(f"  → Dropping database '{db_name}'...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name};")

        # Create fresh database
        print(f"  → Creating new database '{db_name}'...")
        cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user};")

        cursor.close()
        conn.close()

        # Connect to new database to enable extensions
        print(f"  → Enabling PostgreSQL extensions...")
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name,
            autocommit=True
        )

        cursor = conn.cursor()

        # Enable extensions
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        print("     ✓ uuid-ossp enabled")

        cursor.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
        print("     ✓ pgcrypto enabled")

        cursor.close()
        conn.close()

        print()
        print("=" * 80)
        print("  ✅ SUCCESS! Database has been reset.")
        print("=" * 80)
        print()
        print("  Next steps:")
        print()
        print("  1. Go to Setup Wizard: http://10.0.20.111:5173/setup")
        print("  2. Click 'Datenbank initialisieren'")
        print("  3. All 41 migrations will be executed!")
        print()
        print("=" * 80)
        print()

        return True

    except Exception as e:
        print()
        print("=" * 80)
        print("  ❌ ERROR!")
        print("=" * 80)
        print()
        print(f"  Error: {str(e)}")
        print()
        import traceback
        traceback.print_exc()
        print()
        print("=" * 80)
        print()
        return False


if __name__ == '__main__':
    success = reset_database()
    sys.exit(0 if success else 1)
