"""
Run migration 043_extend_audit_logs.sql
"""
import psycopg
from pathlib import Path

# Database connection from db_credentials.txt
DB_CONFIG = {
    'host': '10.0.10.222',
    'port': 5432,
    'dbname': 'lernsystemx_dev',
    'user': 'lernsystem',
    'password': '***REMOVED***'
}

def run_migration():
    migration_file = Path(__file__).parent / 'migrations' / '043_extend_audit_logs.sql'

    print(f"Running migration: {migration_file.name}")
    print("-" * 80)

    # Read migration SQL
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql = f.read()

    # Connect and execute
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Execute migration
                cur.execute(sql)
                conn.commit()

                print("[SUCCESS] Migration 043_extend_audit_logs.sql executed successfully")

                # Verify columns were added
                cur.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'audit_logs'
                    ORDER BY ordinal_position
                """)

                print("\nAudit_logs table structure:")
                for row in cur.fetchall():
                    print(f"  - {row[0]}: {row[1]}")

    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        raise

if __name__ == '__main__':
    run_migration()
