#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drop all tables and schemas from database"""

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


def drop_all():
    """Drop all tables and recreate schema"""

    db_host = os.getenv('DB_HOST')
    db_port = int(os.getenv('DB_PORT', 5432))
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')

    print()
    print("Drop All Tables and Schemas")
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

        # Drop public schema CASCADE (drops all tables, views, etc.)
        print("Dropping public schema with CASCADE...")
        cursor.execute("DROP SCHEMA IF EXISTS public CASCADE;")
        print("  ✓ public schema dropped")

        # Recreate public schema
        print("Recreating public schema...")
        cursor.execute("CREATE SCHEMA public;")
        print("  ✓ public schema created")

        # Grant permissions
        print("Granting permissions...")
        cursor.execute("GRANT ALL ON SCHEMA public TO public;")
        cursor.execute(f"GRANT ALL ON SCHEMA public TO {db_user};")
        print("  ✓ Permissions granted")

        # Recreate extensions
        print("Recreating extensions...")
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
        print("  ✓ uuid-ossp")
        cursor.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')
        print("  ✓ pgcrypto")

        # Commit the changes
        conn.commit()

        cursor.close()
        conn.close()

        print()
        print("✅ SUCCESS! All tables and schemas dropped and recreated")
        print()
        print("Database is now completely empty - ready for fresh setup!")
        print("Next: Go to http://10.0.20.111:5173/setup")
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
    success = drop_all()
    sys.exit(0 if success else 1)
