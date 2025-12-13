"""
Fix courses table to match repository expectations
"""
import psycopg

DB_CONFIG = {
    'host': '10.0.10.222',
    'port': 5432,
    'user': 'lernsystem',
    'password': '***REMOVED***',
    'dbname': 'lernsystemx_dev'
}

def fix_courses():
    """Add missing columns and create aliases for courses table"""
    conn_string = f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']}"

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("Fixing courses table schema...")

                # 1. Add is_public column if it doesn't exist
                print("  - Adding is_public column...")
                cur.execute("""
                    ALTER TABLE courses
                    ADD COLUMN IF NOT EXISTS is_public BOOLEAN DEFAULT FALSE;
                """)

                # 2. Add archived_at column if it doesn't exist
                print("  - Adding archived_at column...")
                cur.execute("""
                    ALTER TABLE courses
                    ADD COLUMN IF NOT EXISTS archived_at TIMESTAMP WITH TIME ZONE;
                """)

                # 3. Rename 'published' to 'is_published' if needed
                # First check if we need to rename
                cur.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'courses' AND column_name = 'is_published'
                """)
                has_is_published = cur.fetchone() is not None

                if not has_is_published:
                    print("  - Renaming 'published' to 'is_published'...")
                    cur.execute("""
                        ALTER TABLE courses
                        RENAME COLUMN published TO is_published;
                    """)
                else:
                    print("  - Column 'is_published' already exists")

                # 4. Rename 'organization_id' to 'organisation_id' if needed
                cur.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'courses' AND column_name = 'organisation_id'
                """)
                has_organisation_id = cur.fetchone() is not None

                if not has_organisation_id:
                    print("  - Renaming 'organization_id' to 'organisation_id'...")
                    cur.execute("""
                        ALTER TABLE courses
                        RENAME COLUMN organization_id TO organisation_id;
                    """)
                else:
                    print("  - Column 'organisation_id' already exists")

                # 5. Add 'category' VARCHAR column for backward compatibility
                print("  - Adding 'category' VARCHAR column...")
                cur.execute("""
                    ALTER TABLE courses
                    ADD COLUMN IF NOT EXISTS category VARCHAR(100);
                """)

                # 6. Add 'preview_video_url' if missing
                print("  - Adding 'preview_video_url' column...")
                cur.execute("""
                    ALTER TABLE courses
                    ADD COLUMN IF NOT EXISTS preview_video_url VARCHAR(500);
                """)

                # 7. Ensure all expected columns have correct defaults
                print("  - Setting default values...")
                cur.execute("""
                    ALTER TABLE courses
                    ALTER COLUMN is_public SET DEFAULT FALSE;
                """)

                cur.execute("""
                    ALTER TABLE courses
                    ALTER COLUMN is_published SET DEFAULT FALSE;
                """)

                conn.commit()
                print("\n✓ Courses table fixed successfully!")

                # Show updated schema
                cur.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'courses'
                    ORDER BY ordinal_position
                """)
                columns = cur.fetchall()
                print("\nUpdated schema:")
                print("-" * 50)
                for col_name, data_type in columns:
                    print(f"  {col_name:<30} {data_type}")

    except Exception as e:
        print(f"✗ Error: {e}")
        raise

if __name__ == '__main__':
    fix_courses()
