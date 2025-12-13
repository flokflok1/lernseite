#!/usr/bin/env python3
"""Check if admin user exists in database"""

import psycopg
import sys

# Database connection details
DB_HOST = '10.0.10.222'
DB_PORT = '5432'
DB_NAME = 'lernsystemx_dev'
DB_USER = 'lernsystem'
DB_PASSWORD = '***REMOVED***'

def check_admin():
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
                print("[ERROR] Admin role not found in roles table")
                sys.exit(1)

            admin_role_id = role[0]
            print(f"[INFO] Admin role_id: {admin_role_id}")

            # Check for admin users
            cur.execute("""
                SELECT u.user_id, u.email, u.firstname, u.lastname, u.status, u.email_verified, r.role_name
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                WHERE u.role_id = %s
            """, (admin_role_id,))

            admins = cur.fetchall()

            if not admins:
                print("[INFO] No admin users found")
            else:
                print(f"[INFO] Found {len(admins)} admin user(s):")
                print("-" * 100)
                for admin in admins:
                    user_id, email, firstname, lastname, status, email_verified, role_name = admin
                    print(f"  User ID:        {user_id}")
                    print(f"  Email:          {email}")
                    print(f"  Name:           {firstname} {lastname}")
                    print(f"  Role:           {role_name}")
                    print(f"  Status:         {status}")
                    print(f"  Email Verified: {email_verified}")
                    print("-" * 100)

            # Check audit log for admin creation
            cur.execute("""
                SELECT event_type, action, severity, metadata, created_at
                FROM audit_logs
                WHERE event_type = 'admin_created'
                ORDER BY created_at DESC
                LIMIT 5
            """)

            audit_entries = cur.fetchall()
            if audit_entries:
                print(f"\n[INFO] Admin creation audit log entries:")
                print("-" * 100)
                for entry in audit_entries:
                    event_type, action, severity, metadata, created_at = entry
                    print(f"  Event:    {event_type}")
                    print(f"  Action:   {action}")
                    print(f"  Severity: {severity}")
                    print(f"  Metadata: {metadata}")
                    print(f"  Created:  {created_at}")
                    print("-" * 100)

        conn.close()

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    check_admin()
