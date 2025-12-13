"""
Check audit_logs table columns
"""
import psycopg

DB_CONFIG = {
    'host': '10.0.10.222',
    'port': 5432,
    'dbname': 'lernsystemx_dev',
    'user': 'lernsystem',
    'password': '***REMOVED***'
}

with psycopg.connect(**DB_CONFIG) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'audit_logs'
            ORDER BY ordinal_position
        """)

        print("Audit_logs table columns:")
        print("-" * 40)
        for row in cur.fetchall():
            print(f"{row[0]}: {row[1]}")
