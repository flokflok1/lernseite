#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Truncate all tables in database instead of dropping DB"""

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


def truncate_all():
    """Truncate all tables in database"""

    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT', 5432))
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')

    print()
    print("Truncate All Tables")
    print(f"Host: {db_host}:{db_port}")
    print(f"User: {db_user}")
    print(f"DB: {db_name}")
    print()

    try:
        # Connect to database
        conn = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname=db_name,
            autocommit=False
        )
        cursor = conn.cursor()

        # Get all table names
        print("Fetching all tables...")
        cursor.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename;
        """)

        tables = cursor.fetchall()
        table_count = len(tables)

        if table_count == 0:
            print("No tables found!")
            cursor.close()
            conn.close()
            return True

        print(f"Found {table_count} tables")
        print()

        # Build list of all tables for single truncate command
        print("Truncating all tables with CASCADE...")
        table_names = ', '.join([f'"{table[0]}"' for table in tables])
        cursor.execute(f'TRUNCATE TABLE {table_names} CASCADE;')
        print("  ✓ All tables truncated")

        # Commit the changes
        conn.commit()

        cursor.close()
        conn.close()

        print()
        print(f"✅ SUCCESS! All {table_count} tables truncated")
        print()
        print("Next: Delete .lsx-installed and go to http://10.0.20.111:5173/setup")
        print()

        return True

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False


if __name__ == '__main__':
    success = truncate_all()
    sys.exit(0 if success else 1)
