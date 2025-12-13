"""
Create a 'categories' view/alias for 'course_categories' table
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

def create_view():
    """Create categories view"""
    conn_string = f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']}"

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("Creating 'categories' view as alias for 'course_categories'...")

                # Drop view if exists
                cur.execute("DROP VIEW IF EXISTS categories CASCADE")

                # Create view
                cur.execute("""
                    CREATE VIEW categories AS
                    SELECT
                        category_id,
                        parent_id,
                        name,
                        slug,
                        description,
                        icon,
                        color,
                        level,
                        order_index,
                        active AS is_active,
                        created_at,
                        updated_at
                    FROM course_categories
                """)

                conn.commit()
                print("View 'categories' created successfully")

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == '__main__':
    create_view()
