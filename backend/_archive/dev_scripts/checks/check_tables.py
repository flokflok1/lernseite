"""
Check which tables exist in the database
"""
import psycopg

# DB credentials
DB_CONFIG = {
    'host': '10.0.10.222',
    'port': 5432,
    'user': 'lernsystem',
    'password': '***REMOVED***',
    'dbname': 'lernsystemx_dev'
}

def check_tables():
    """Check which tables exist"""
    conn_string = f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']}"

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                # Get all tables
                cur.execute("""
                    SELECT tablename
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """)

                tables = cur.fetchall()

                print("\nExisting tables in database:")
                print("-" * 50)
                for (table,) in tables:
                    print(f"  - {table}")
                print(f"\nTotal: {len(tables)} tables")

                # Check specifically for category-related tables
                print("\nCategory-related tables:")
                category_tables = [t[0] for t in tables if 'categor' in t[0].lower()]
                if category_tables:
                    for table in category_tables:
                        print(f"  - {table}")
                else:
                    print("  (none found)")

                # Check for courses table
                print("\nCourse-related tables:")
                course_tables = [t[0] for t in tables if 'course' in t[0].lower()]
                if course_tables:
                    for table in course_tables:
                        print(f"  - {table}")
                else:
                    print("  (none found)")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    check_tables()
