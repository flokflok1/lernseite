"""
Test courses query directly to diagnose 500 error
"""
import psycopg

DB_CONFIG = {
    'host': '10.0.10.222',
    'port': 5432,
    'user': 'lernsystem',
    'password': '***REMOVED***',
    'dbname': 'lernsystemx_dev'
}

def test_courses_query():
    """Test the admin_list_courses query step by step"""
    conn_string = f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']}"

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("\n=== Testing Courses Query ===\n")

                # Test 1: Simple count
                print("Test 1: Simple COUNT query")
                try:
                    query = "SELECT COUNT(*) as total FROM courses"
                    cur.execute(query)
                    result = cur.fetchone()
                    print(f"SUCCESS - Found {result[0]} courses")
                except Exception as e:
                    print(f"FAILED - {e}")
                    return

                # Test 2: Select basic columns
                print("\nTest 2: Select basic columns")
                try:
                    query = """
                        SELECT course_id, title, creator_user_id, created_at
                        FROM courses
                        LIMIT 1
                    """
                    cur.execute(query)
                    result = cur.fetchone()
                    if result:
                        print(f"SUCCESS - Sample course: {result[1]}")
                    else:
                        print("SUCCESS - No courses found (empty table)")
                except Exception as e:
                    print(f"FAILED - {e}")
                    return

                # Test 3: Join with users table
                print("\nTest 3: JOIN with users table")
                try:
                    query = """
                        SELECT c.course_id, c.title, u.username
                        FROM courses c
                        LEFT JOIN users u ON c.creator_user_id = u.user_id
                        LIMIT 1
                    """
                    cur.execute(query)
                    result = cur.fetchone()
                    if result:
                        print(f"SUCCESS - Course with creator: {result[1]} by {result[2]}")
                    else:
                        print("SUCCESS - No courses to join")
                except Exception as e:
                    print(f"FAILED - {e}")
                    return

                # Test 4: Join with organisations table
                print("\nTest 4: JOIN with organisations table")
                try:
                    query = """
                        SELECT c.course_id, c.title, o.name as org_name
                        FROM courses c
                        LEFT JOIN organisations o ON c.organisation_id = o.organisation_id
                        LIMIT 1
                    """
                    cur.execute(query)
                    result = cur.fetchone()
                    if result:
                        print(f"SUCCESS - Course with org: {result[1]}, org={result[2]}")
                    else:
                        print("SUCCESS - No courses to join")
                except Exception as e:
                    print(f"FAILED - {e}")
                    return

                # Test 5: Full query from admin_list_courses
                print("\nTest 5: Full query with all JOINs")
                try:
                    query = """
                        SELECT
                            c.course_id,
                            c.title,
                            c.description,
                            c.creator_user_id,
                            u.username AS creator_name,
                            c.organisation_id,
                            o.name AS organisation_name,
                            c.category_id,
                            cat.name AS category_name,
                            c.level,
                            c.language,
                            c.price,
                            c.is_published,
                            c.is_public,
                            c.status,
                            c.enrollment_count,
                            c.average_rating,
                            c.created_at,
                            c.updated_at
                        FROM courses c
                        LEFT JOIN users u ON c.creator_user_id = u.user_id
                        LEFT JOIN organisations o ON c.organisation_id = o.organisation_id
                        LEFT JOIN course_categories cat ON c.category_id = cat.category_id
                        WHERE TRUE
                        ORDER BY c.created_at DESC
                        LIMIT 20 OFFSET 0
                    """
                    cur.execute(query)
                    results = cur.fetchall()
                    print(f"SUCCESS - Retrieved {len(results)} courses")

                    if results:
                        print("\nFirst course details:")
                        first = results[0]
                        print(f"  course_id: {first[0]}")
                        print(f"  title: {first[1]}")
                        print(f"  creator_name: {first[4]}")
                        print(f"  category_name: {first[8]}")

                except Exception as e:
                    print(f"FAILED - {e}")
                    print(f"Error type: {type(e).__name__}")
                    import traceback
                    traceback.print_exc()
                    return

                print("\n=== All Tests Passed ===")

    except Exception as e:
        print(f"\nConnection Error: {e}")
        raise

if __name__ == '__main__':
    test_courses_query()
