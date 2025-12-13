#!/usr/bin/env python3
"""Test admin creation with detailed error output"""

import sys
import traceback

# Add backend to path
sys.path.insert(0, 'C:\\Users\\Pascal\\Desktop\\Lernsystem\\backend')

from setup.admin_setup import AdminSetup

def test_admin_creation():
    try:
        print("[INFO] Testing admin creation...")
        print("-" * 80)

        # Test data
        email = "test_admin@lsx.de"
        password = "TestPass123!"
        first_name = "Test"
        last_name = "Admin"

        print(f"[INFO] Email: {email}")
        print(f"[INFO] Password: {password}")
        print(f"[INFO] First Name: {first_name}")
        print(f"[INFO] Last Name: {last_name}")
        print("-" * 80)

        # Validate password first
        valid_pass, pass_msg = AdminSetup.validate_password(password)
        print(f"[INFO] Password validation: {valid_pass} - {pass_msg}")

        # Validate email
        valid_email, email_msg = AdminSetup.validate_email(email)
        print(f"[INFO] Email validation: {valid_email} - {email_msg}")

        print("-" * 80)
        print("[INFO] Creating admin user...")

        # Create admin
        result = AdminSetup.create_admin(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            enable_2fa=False
        )

        print("[SUCCESS] Admin created successfully!")
        print(f"  User ID: {result['user_id']}")
        print(f"  Email: {result['email']}")
        print(f"  First Name: {result.get('first_name', 'N/A')}")
        print(f"  Last Name: {result.get('last_name', 'N/A')}")
        print(f"  Recovery Codes: {len(result['recovery_codes'])} codes")
        print("-" * 80)

    except ValueError as e:
        print(f"\n[ERROR] Validation Error: {e}")
        traceback.print_exc()
    except Exception as e:
        print(f"\n[ERROR] Unexpected Error: {e}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    test_admin_creation()
