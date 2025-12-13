#!/usr/bin/env python3
"""Delete existing admin user for fresh setup"""

import psycopg
import sys

# Database connection details
DB_HOST = '10.0.10.222'
DB_PORT = '5432'
DB_NAME = 'lernsystemx_dev'
DB_USER = 'lernsystem'
DB_PASSWORD = '***REMOVED***'

def delete_admin():
    try:
        # Connect to database
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )

        with conn.cursor() as cur:
            # Get admin role_id
            cur.execute("SELECT role_id FROM roles WHERE role_name = 'admin'")
            role = cur.fetchone()

            if not role:
                print("[ERROR] Admin role not found")
                sys.exit(1)

            admin_role_id = role[0]

            # Find admin users
            cur.execute("""
                SELECT user_id, email FROM users WHERE role_id = %s
            """, (admin_role_id,))

            admins = cur.fetchall()

            if not admins:
                print("[INFO] No admin users to delete")
                conn.close()
                return

            print(f"[INFO] Found {len(admins)} admin user(s) to delete:")
            for user_id, email in admins:
                print(f"  - {email} ({user_id})")

            # Delete recovery codes first
            for user_id, email in admins:
                cur.execute("DELETE FROM recovery_codes WHERE user_id = %s", (user_id,))
                print(f"[INFO] Deleted recovery codes for {email}")

            # Delete audit logs
            for user_id, email in admins:
                cur.execute("DELETE FROM audit_logs WHERE user_id = %s", (user_id,))
                print(f"[INFO] Deleted audit logs for {email}")

            # Delete admin users
            for user_id, email in admins:
                cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                print(f"[INFO] Deleted admin user: {email}")

            conn.commit()
            print("[SUCCESS] All admin users deleted!")

        conn.close()

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    delete_admin()
