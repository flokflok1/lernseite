from app.database.connection import get_connection
import psycopg

with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name='courses'
            ORDER BY ordinal_position
        """)
        print("COURSES TABLE COLUMNS:")
        print("=" * 60)
        for row in cur.fetchall():
            print(f"{row[0]:30} {row[1]}")
