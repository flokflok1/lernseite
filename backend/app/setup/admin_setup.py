"""
LernsystemX Setup - Admin Account Creation

Creates the initial superadmin account with:
- Strong password validation
- Optional 2FA (Time-based OTP)
- Recovery codes for account recovery
- Audit logging

ISO 27001:2013 compliant - Secure admin account creation
"""

import re
import secrets
from typing import Dict, Tuple, List, Optional

from app.infrastructure.persistence.repositories.user import UserRepository
from app.infrastructure.persistence.database.connection import execute_query, fetch_one


class AdminSetup:
    """
    Setup initial superadmin account

    Implements secure admin creation with password policy enforcement.
    """

    PASSWORD_MIN_LENGTH = 12
    PASSWORD_POLICY = {
        'min_length': 12,
        'require_uppercase': True,
        'require_lowercase': True,
        'require_digit': True,
        'require_special': True
    }

    @classmethod
    def validate_password(cls, password: str) -> Tuple[bool, str]:
        """
        Validate password against security policy

        Args:
            password: Plain text password

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> valid, msg = AdminSetup.validate_password('SecurePass123!')
            >>> if not valid:
            ...     print(f"Password error: {msg}")
        """
        if len(password) < cls.PASSWORD_POLICY['min_length']:
            return False, f"Password must be at least {cls.PASSWORD_POLICY['min_length']} characters"

        if cls.PASSWORD_POLICY['require_uppercase'] and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"

        if cls.PASSWORD_POLICY['require_lowercase'] and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"

        if cls.PASSWORD_POLICY['require_digit'] and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"

        if cls.PASSWORD_POLICY['require_special']:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                return False, "Password must contain at least one special character"

        return True, "Password is strong"

    @classmethod
    def validate_email(cls, email: str) -> Tuple[bool, str]:
        """
        Validate email format

        Args:
            email: Email address

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> valid, msg = AdminSetup.validate_email('admin@example.com')
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            return False, "Invalid email format"

        return True, "Email is valid"

    @classmethod
    def create_admin(
        cls,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        organisation_id: Optional[int] = None,
        enable_2fa: bool = False
    ) -> Dict:
        """
        Create superadmin user

        Args:
            email: Admin email
            password: Admin password (must meet policy)
            first_name: Admin first name
            last_name: Admin last name
            organisation_id: Organisation ID (optional)
            enable_2fa: Enable 2FA (default: False)

        Returns:
            Dictionary with:
            - user_id: Created user ID
            - email: Admin email
            - recovery_codes: List of recovery codes
            - totp_secret: TOTP secret (if 2FA enabled)

        Raises:
            ValueError: If validation fails

        Example:
            >>> result = AdminSetup.create_admin(
            ...     email='admin@example.com',
            ...     password='SecurePass123!',
            ...     first_name='Admin',
            ...     last_name='User'
            ... )
            >>> print(f"Admin created with ID: {result['user_id']}")
        """
        # Validate email
        valid_email, email_msg = cls.validate_email(email)
        if not valid_email:
            raise ValueError(email_msg)

        # Validate password
        valid_password, password_msg = cls.validate_password(password)
        if not valid_password:
            raise ValueError(password_msg)

        # Check if admin already exists
        # Get admin role_id from roles table
        admin_role = fetch_one(
            "SELECT role_id FROM roles WHERE role_name = %s",
            ('admin',)
        )
        if admin_role:
            existing_admin = fetch_one(
                "SELECT user_id FROM users WHERE role_id = %s LIMIT 1",
                (admin_role['role_id'],)
            )
            if existing_admin:
                raise ValueError("Admin account already exists")

        # Generate recovery codes
        recovery_codes = cls._generate_recovery_codes(count=10)

        # Generate 2FA secret if enabled
        totp_secret = None
        if enable_2fa:
            totp_secret = cls._generate_totp_secret()

        # If no organisation_id provided, use LSX Academy (id=1)
        if organisation_id is None:
            # Get LSX Academy organisation
            org = fetch_one(
                "SELECT organization_id FROM organisations.organisations WHERE name = %s",
                ('LSX Academy',)
            )
            organisation_id = org['organization_id'] if org else None

        # Create admin user
        admin = UserRepository.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='admin',
            organization_id=organisation_id
        )

        # Set as Owner-Admin (first admin becomes owner)
        # Check if this is the first admin (no owner exists yet)
        existing_owner = fetch_one(
            "SELECT user_id FROM users WHERE is_owner = true LIMIT 1"
        )

        if not existing_owner:
            # This is the first admin - make them the Owner-Admin
            execute_query(
                """
                UPDATE users
                SET is_owner = true
                WHERE user_id = %s
                """,
                (admin['user_id'],)
            )

        # Update 2FA settings if enabled
        if enable_2fa and totp_secret:
            execute_query(
                """
                UPDATE users
                SET two_factor_enabled = true,
                    two_factor_secret = %s
                WHERE user_id = %s
                """,
                (totp_secret, admin['user_id'])
            )

        # Mark email as verified (admin account)
        UserRepository.verify_email(admin['user_id'])

        # Store recovery codes (hashed)
        cls._store_recovery_codes(admin['user_id'], recovery_codes)

        # Log admin creation
        cls._log_admin_creation(admin['user_id'], email, enable_2fa)

        return {
            'user_id': admin['user_id'],
            'email': admin['email'],
            'first_name': admin.get('firstname', ''),
            'last_name': admin.get('lastname', ''),
            'is_owner': not bool(existing_owner),  # True if no owner existed before
            'recovery_codes': recovery_codes,
            'totp_secret': totp_secret if enable_2fa else None,
            'two_factor_enabled': enable_2fa
        }

    @staticmethod
    def _generate_recovery_codes(count: int = 10) -> List[str]:
        """
        Generate recovery codes for account recovery

        Args:
            count: Number of codes to generate

        Returns:
            List of recovery codes

        Example:
            >>> codes = AdminSetup._generate_recovery_codes(10)
            >>> print(codes[0])  # e.g., 'a3f9d2e1b4c7'
        """
        return [secrets.token_hex(8) for _ in range(count)]

    @staticmethod
    def _generate_totp_secret() -> str:
        """
        Generate TOTP secret for 2FA

        Returns:
            Base32-encoded secret

        Example:
            >>> secret = AdminSetup._generate_totp_secret()
        """
        # Generate 20 random bytes, base32 encode
        import base64
        random_bytes = secrets.token_bytes(20)
        return base64.b32encode(random_bytes).decode('utf-8')

    @staticmethod
    def _store_recovery_codes(user_id: int, codes: List[str]) -> None:
        """
        Store recovery codes in database (hashed)

        Args:
            user_id: User ID
            codes: List of recovery codes

        Note:
            Recovery codes are stored hashed for security
        """
        import bcrypt

        for code in codes:
            code_hash = bcrypt.hashpw(code.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            execute_query(
                """
                INSERT INTO core.two_factor_backups (user_id, code_hash, used, created_at)
                VALUES (%s, %s, false, NOW())
                ON CONFLICT DO NOTHING
                """,
                (user_id, code_hash)
            )

    @staticmethod
    def _log_admin_creation(user_id: int, email: str, two_factor_enabled: bool) -> None:
        """
        Log admin creation in audit log

        Args:
            user_id: Created user ID
            email: Admin email
            two_factor_enabled: Whether 2FA was enabled
        """
        import json

        metadata = {
            "email": email,
            "2fa_enabled": two_factor_enabled,
            "setup_wizard": True
        }

        execute_query(
            """
            INSERT INTO audit_logs (
                event_type, user_id, action, severity, metadata, created_at
            )
            VALUES (%s, %s, %s, %s, %s, NOW())
            """,
            (
                'admin_created',
                user_id,
                'create',
                'critical',
                json.dumps(metadata)
            )
        )

    @classmethod
    def get_password_policy(cls) -> Dict:
        """
        Get password policy requirements

        Returns:
            Dictionary with password policy details

        Example:
            >>> policy = AdminSetup.get_password_policy()
            >>> print(f"Minimum length: {policy['min_length']}")
        """
        return cls.PASSWORD_POLICY.copy()

    @staticmethod
    def verify_2fa_code(totp_secret: str, code: str) -> bool:
        """
        Verify TOTP code

        Args:
            totp_secret: TOTP secret
            code: 6-digit TOTP code

        Returns:
            bool: True if code is valid

        Example:
            >>> is_valid = AdminSetup.verify_2fa_code(secret, '123456')
        """
        try:
            import pyotp
            totp = pyotp.TOTP(totp_secret)
            return totp.verify(code, valid_window=1)
        except ImportError:
            # pyotp not installed - 2FA not available
            return False
        except Exception:
            return False

    @staticmethod
    def generate_qr_code(email: str, totp_secret: str) -> Optional[str]:
        """
        Generate QR code for TOTP setup

        Args:
            email: User email
            totp_secret: TOTP secret

        Returns:
            Base64-encoded QR code image or None

        Example:
            >>> qr_code = AdminSetup.generate_qr_code('admin@example.com', secret)
            >>> # qr_code can be embedded in HTML: <img src="data:image/png;base64,{qr_code}" />
        """
        try:
            import pyotp
            import qrcode
            import io
            import base64

            # Generate provisioning URI
            totp = pyotp.TOTP(totp_secret)
            uri = totp.provisioning_uri(
                name=email,
                issuer_name='LernsystemX'
            )

            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(uri)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

            return qr_code_base64

        except ImportError:
            # Libraries not installed
            return None
        except Exception:
            return None


# Convenience function
def create_admin(**kwargs) -> Dict:
    """
    Quick admin creation function

    Example:
        >>> admin = create_admin(
        ...     email='admin@example.com',
        ...     password='SecurePass123!',
        ...     first_name='Admin',
        ...     last_name='User'
        ... )
    """
    return AdminSetup.create_admin(**kwargs)
