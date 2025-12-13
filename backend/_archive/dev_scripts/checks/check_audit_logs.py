#!/usr/bin/env python3
"""Check audit_logs table schema"""

import psycopg
import sys

# Database connection details
DB_HOST = '10.0.10.222'
DB_PORT = '5432'
DB_NAME = 'lernsystemx_dev'
DB_USER = 'lernsystem'
DB_PASSWORD = '***REMOVED***'

def check_table_schema():
    try:
        # Connect to database
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        with conn.cursor() as cur:
            # Get table structure
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'audit_logs'
                ORDER BY ordinal_position
            """)

            columns = cur.fetchall()

            print("[INFO] audit_logs table structure:")
            print("-" * 80)
            for col in columns:
                col_name, data_type, max_length, is_nullable = col
                length_str = f"({max_length})" if max_length else ""
                nullable_str = "NULL" if is_nullable == 'YES' else "NOT NULL"
                print(f"  {col_name:<20} {data_type}{length_str:<20} {nullable_str}")

            print("-" * 80)
            print(f"[INFO] Total columns: {len(columns)}")

        conn.close()

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == '__main__':
    check_table_schema()
