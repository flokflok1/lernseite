#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create database if it doesn't exist"""

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


def create_db():
    """Create database"""

    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT', 5432))
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')

    print()
    print("Create Database")
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

        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        exists = cursor.fetchone()

        if exists:
            print(f"Database '{db_name}' already exists!")
        else:
            # Create database
            print(f"Creating database '{db_name}'...")
            cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user};")
            print(f"  ✓ Database created")

        cursor.close()
        conn.close()

        # Connect to new database and add extensions
        print("Adding extensions...")
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
        print("  ✓ uuid-ossp")

        cursor.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
        print("  ✓ pgcrypto")

        cursor.close()
        conn.close()

        print()
        print("✅ SUCCESS!")
        print()
        print("Database is ready. Next: Go to http://10.0.20.111:5173/setup")
        print()

        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = create_db()
    sys.exit(0 if success else 1)
