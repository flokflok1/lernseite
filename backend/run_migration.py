"""
Quick script to run a specific migration
"""
import psycopg

# DB credentials from db_credentials.txt
DB_CONFIG = {
    'host': '10.0.10.222',
    'port': 5432,
    'user': 'lernsystem',
    'password': '***REMOVED***',
    'dbname': 'lernsystemx_dev'
}

def run_migration(migration_file: str):
    """Run a migration file"""
    conn_string = f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']}"

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Read migration file
                with open(migration_file, 'r', encoding='utf-8') as f:
                    sql = f.read()

                # Execute migration
                print(f"Running migration: {migration_file}")
                cur.execute(sql)
                conn.commit()
                print(f"✓ Migration completed successfully")

    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <migration_file>")
        sys.exit(1)

    migration_file = sys.argv[1]
    run_migration(migration_file)
