#!/usr/bin/env python
"""
Force drop and recreate lernsystemx_dev database
"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'dbname': 'postgres',  # Connect to postgres database
    'user': os.getenv('DB_USER', 'lernsystem'),
    'password': os.getenv('DB_PASSWORD', '')
}

def force_reset_database():
    """Force drop and recreate database"""
    try:
        conn = psycopg.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()

        # Drop database with FORCE (PostgreSQL 13+)
        print("[INFO] Dropping database lernsystemx_dev with FORCE...")
        cur.execute("DROP DATABASE IF EXISTS lernsystemx_dev WITH (FORCE);")
        print("[OK] Database dropped successfully")

        # Create new database
        print("[INFO] Creating new database lernsystemx_dev...")
        cur.execute("CREATE DATABASE lernsystemx_dev OWNER lernsystem;")
        print("[OK] Database created successfully")

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"[ERROR] Failed to reset database: {e}")
        return False

if __name__ == '__main__':
    print("Force resetting lernsystemx_dev database...")
    print("=" * 60)
    if force_reset_database():
        print("\n[SUCCESS] Database has been reset!")
        print("\nNext steps:")
        print("1. Delete .lsx-installed file (if exists)")
        print("2. Navigate to http://10.0.20.111:5173/setup")
        print("3. Complete the setup wizard")
    else:
        print("\n[FAILED] Could not reset database.")
