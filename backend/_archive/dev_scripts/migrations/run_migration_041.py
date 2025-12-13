#!/usr/bin/env python3
"""Run migration 041 - Extend organization types"""

import psycopg

DB_HOST = '10.0.10.222'
DB_PORT = '5432'
DB_NAME = 'lernsystemx_dev'
DB_USER = 'lernsystem'
DB_PASSWORD = '***REMOVED***'

def run_migration():
    conn = psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

    cur = conn.cursor()

    try:
        print("[INFO] Starting migration 041...")

        # Drop existing constraint
        print("[INFO] Dropping existing chk_org_type constraint...")
        cur.execute("""
            ALTER TABLE organizations
            DROP CONSTRAINT IF EXISTS chk_org_type
        """)

        # Add new constraint with all types
        print("[INFO] Adding new constraint with all organization types...")
        cur.execute("""
            ALTER TABLE organizations
            ADD CONSTRAINT chk_org_type CHECK (
                type IN ('school', 'company', 'academy', 'creator_org', 'community', 'system')
            )
        """)

        conn.commit()
        print("[SUCCESS] Migration 041 completed successfully!")

        # Verify
        cur.execute("""
            SELECT pg_get_constraintdef(c.oid)
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            WHERE t.relname = 'organizations' AND c.conname = 'chk_org_type'
        """)
        result = cur.fetchone()
        print(f"[INFO] New constraint: {result[0]}")

    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    run_migration()
