#!/usr/bin/env python
"""
Kill all connections to lernsystemx_dev database
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

def kill_connections():
    """Kill all connections to lernsystemx_dev"""
    try:
        conn = psycopg.connect(**DB_CONFIG)
        conn.autocommit = True
        cur = conn.cursor()

        # Terminate all connections to lernsystemx_dev
        cur.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = 'lernsystemx_dev'
              AND pid <> pg_backend_pid();
        """)

        result = cur.fetchall()
        terminated = sum(1 for row in result if row[0])

        print(f"[OK] Terminated {terminated} connection(s) to lernsystemx_dev")

        cur.close()
        conn.close()

        return True

    except Exception as e:
        print(f"[ERROR] Failed to kill connections: {e}")
        return False

if __name__ == '__main__':
    print("Killing all connections to lernsystemx_dev database...")
    if kill_connections():
        print("\n[SUCCESS] All connections terminated. You can now drop the database.")
    else:
        print("\n[FAILED] Could not terminate all connections.")
