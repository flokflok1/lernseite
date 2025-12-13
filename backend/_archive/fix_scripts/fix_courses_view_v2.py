"""
Fix courses VIEW - simpler approach without complex triggers
"""
import psycopg

DB_CONFIG = {
    'host': '10.0.10.222',
    'port': 5432,
    'user': 'lernsystem',
    'password': '***REMOVED***',
    'dbname': 'lernsystemx_dev'
}

def fix_view():
    """Drop the complex VIEW and just rename the table back"""
    conn_string = f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']}"

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("Fixing courses VIEW...")

                # Drop the VIEW with all its triggers
                print("  - Dropping courses VIEW and triggers...")
                cur.execute("DROP VIEW IF EXISTS courses CASCADE")

                # Rename courses_base back to courses
                print("  - Renaming courses_base back to courses...")
                cur.execute("ALTER TABLE IF EXISTS courses_base RENAME TO courses")

                # Now add missing columns directly to the table
                print("  - Ensuring language column exists...")
                cur.execute("""
                    ALTER TABLE courses
                    ADD COLUMN IF NOT EXISTS language VARCHAR(10);
                """)

                # Copy language_default to language if needed
                print("  - Copying language_default to language...")
                cur.execute("""
                    UPDATE courses
                    SET language = language_default
                    WHERE language IS NULL AND language_default IS NOT NULL;
                """)

                # Set default for language
                cur.execute("""
                    ALTER TABLE courses
                    ALTER COLUMN language SET DEFAULT 'de';
                """)

                conn.commit()
                print("SUCCESS: Courses table fixed!")
                print("Now the repository can directly access the courses table.")

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == '__main__':
    fix_view()
