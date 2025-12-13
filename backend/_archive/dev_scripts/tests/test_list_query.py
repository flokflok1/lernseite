"""
Test the exact admin_list_courses query
"""
import psycopg

DB_CONFIG = {
    'host': '10.0.10.222',
    'port': 5432,
    'user': 'lernsystem',
    'password': '***REMOVED***',
    'dbname': 'lernsystemx_dev'
}

def test_list_query():
    """Test the exact query from admin_list_courses with default params"""
    conn_string = f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']}"

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("\n=== Testing admin_list_courses Query ===\n")

                # This is the exact query from course_repository.py admin_list_courses()
                # with default params (page=1, per_page=20, status='all')

                # Count query first
                count_query = """
                    SELECT COUNT(*) as total
                    FROM courses c
                    WHERE TRUE
                """

                print("1. Testing COUNT query...")
                try:
                    cur.execute(count_query)
                    result = cur.fetchone()
                    print(f"   SUCCESS - Total courses: {result[0]}")
                except Exception as e:
                    print(f"   FAILED - {e}")
                    return

                # Data query with joins
                data_query = """
                    SELECT
                        c.course_id,
                        c.title,
                        c.description,
                        c.creator_user_id,
                        u.firstname || ' ' || u.lastname AS creator_name,
                        c.organisation_id,
                        o.name AS organisation_name,
                        c.category,
                        c.level,
                        c.language,
                        c.price,
                        c.is_public,
                        c.is_published,
                        c.thumbnail_url,
                        c.tags,
                        c.created_at,
                        c.updated_at,
                        c.published_at,
                        c.archived_at,
                        (SELECT COUNT(*) FROM modules WHERE course_id = c.course_id) AS module_count,
                        (SELECT COUNT(*) FROM course_enrollments WHERE course_id = c.course_id) AS enrollment_count,
                        CASE
                            WHEN c.archived_at IS NOT NULL THEN 'archived'
                            WHEN c.is_published = TRUE THEN 'published'
                            ELSE 'draft'
                        END AS status
                    FROM courses c
                    LEFT JOIN users u ON c.creator_user_id = u.user_id
                    LEFT JOIN organisations o ON c.organisation_id = o.organisation_id
                    WHERE TRUE
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """

                print("\n2. Testing DATA query with JOINs...")
                try:
                    cur.execute(data_query, (20, 0))
                    results = cur.fetchall()
                    print(f"   SUCCESS - Retrieved {len(results)} courses")

                    if results:
                        print("\n   First course:")
                        for idx, col in enumerate(cur.description):
                            print(f"      {col.name}: {results[0][idx]}")
                    else:
                        print("   (Table is empty - no courses found)")

                except Exception as e:
                    print(f"   FAILED - {e}")
                    import traceback
                    traceback.print_exc()
                    return

                print("\n=== All Tests Passed ===")

    except Exception as e:
        print(f"\nConnection Error: {e}")
        raise

if __name__ == '__main__':
    test_list_query()
