"""
Check courses table schema to find column names
"""
import psycopg

DB_CONFIG = {
    'host': '10.0.10.222',
    'port': 5432,
    'user': 'lernsystem',
    'password': '***REMOVED***',
    'dbname': 'lernsystemx_dev'
}

def check_schema():
    conn_string = f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']}"

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Get courses table columns
                cur.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'courses'
                    ORDER BY ordinal_position
                """)

                columns = cur.fetchall()
                print("\nColumns in 'courses' table:")
                print("-" * 70)
                for col_name, data_type, nullable in columns:
                    print(f"  {col_name:<30} {data_type:<20} {'NULL' if nullable == 'YES' else 'NOT NULL'}")

                print(f"\nTotal: {len(columns)} columns")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_schema()
