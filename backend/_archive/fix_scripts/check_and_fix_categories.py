"""
Quick script to check and fix the categories table/view
"""
import psycopg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def main():
    conn = psycopg.connect(DATABASE_URL)
    cur = conn.cursor()

    # Check if categories exists
    cur.execute("""
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema='public'
        AND table_name LIKE '%categor%'
    """)
    results = cur.fetchall()

    print("Existing category-related tables/views:")
    for row in results:
        print(f"  - {row[0]} ({row[1]})")

    # Check if categories view exists
    cur.execute("""
        SELECT table_name
        FROM information_schema.views
        WHERE table_schema='public'
        AND table_name = 'categories'
    """)
    view_exists = cur.fetchone()

    if not view_exists:
        print("\n❌ 'categories' view does NOT exist")

        # Check if course_categories table exists
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            AND table_name = 'course_categories'
        """)
        table_exists = cur.fetchone()

        if table_exists:
            print("✓ 'course_categories' table exists")
            print("\n Creating 'categories' VIEW...")

            # Create the view
            cur.execute("""
                CREATE OR REPLACE VIEW categories AS
                SELECT * FROM course_categories
            """)
            conn.commit()
            print("✅ 'categories' view created successfully!")
        else:
            print("❌ 'course_categories' table does NOT exist either")
            print("   Database schema might need to be initialized")
    else:
        print("\n✅ 'categories' view already exists")

    cur.close()
    conn.close()

if __name__ == '__main__':
    main()
