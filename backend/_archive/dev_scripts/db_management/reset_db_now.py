#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick database reset using dotenv"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment from .env
from dotenv import load_dotenv
load_dotenv()

import os
import psycopg

# Set UTF-8 for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')


def reset():
    """Reset database"""

    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT', 5432))
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')

    print()
    print("Database Reset")
    print(f"Host: {db_host}:{db_port}")
    print(f"User: {db_user}")
    print(f"DB: {db_name}")
    print()

    try:
        # Connect to postgres
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname='postgres',
            autocommit=True
        )
        cursor = conn.cursor()

        # Terminate connections (ignore superuser errors)
        print("Terminating connections...")
        try:
            cursor.execute(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid();
            """)
        except Exception as e:
            print(f"  Warning: {e}")
            print("  Continuing anyway...")

        # Drop database with FORCE (PostgreSQL 13+)
        print(f"Dropping database '{db_name}' with FORCE...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_name} WITH (FORCE);")

        # Create database
        print(f"Creating database '{db_name}'...")
        cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user};")

        cursor.close()
        conn.close()

        # Connect to new database
        print("Enabling extensions...")
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name,
            autocommit=True
        )
        cursor = conn.cursor()

        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

        cursor.close()
        conn.close()

        print()
        print("✅ SUCCESS!")
        print()
        print("Next: Go to http://10.0.20.111:5173/setup")
        print()

        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = reset()
    sys.exit(0 if success else 1)
