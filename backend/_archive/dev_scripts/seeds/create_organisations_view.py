"""
Create organisations VIEW to alias organizations table
"""
import psycopg

DB_CONFIG = {
    'host': '10.0.10.222',
    'port': 5432,
    'user': 'lernsystem',
    'password': '***REMOVED***',
    'dbname': 'lernsystemx_dev'
}

def create_view():
    """Create organisations view aliasing organizations table"""
    conn_string = f"host={DB_CONFIG['host']} port={DB_CONFIG['port']} dbname={DB_CONFIG['dbname']} user={DB_CONFIG['user']} password={DB_CONFIG['password']}"

    try:
        with psycopg.connect(conn_string) as conn:
            with conn.cursor() as cur:
                print("\n=== Creating organisations VIEW ===\n")

                # Drop existing view if any
                print("  - Dropping old view if exists...")
                cur.execute("DROP VIEW IF EXISTS organisations CASCADE")

                # Create VIEW with British spelling and column aliasing
                print("  - Creating organisations VIEW...")
                cur.execute("""
                    CREATE VIEW organisations AS
                    SELECT
                        organization_id AS organisation_id,
                        name,
                        type,
                        domain,
                        logo_url,
                        billing_email,
                        phone,
                        address_street,
                        address_city,
                        address_state,
                        address_country,
                        address_postal_code,
                        tax_id,
                        token_pool,
                        token_pool_limit,
                        billing_rate,
                        max_users,
                        max_courses,
                        status,
                        created_at,
                        updated_at
                    FROM organizations
                """)

                conn.commit()
                print("\nSUCCESS: organisations VIEW created!")
                print("The repository can now use 'organisations' (British spelling)")

    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == '__main__':
    create_view()
