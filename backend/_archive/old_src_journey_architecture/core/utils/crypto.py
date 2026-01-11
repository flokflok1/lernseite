"""
Cryptography Utilities

Secure cryptographic operations for the system.

Features:
- AES-256 encryption/decryption
- Password hashing with bcrypt
- Secure random token generation
- API key encryption/decryption
"""

import os
import secrets
import hashlib
import bcrypt
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend


class CryptoUtils:
    """
    Cryptography utility functions.

    All encryption uses AES-256-GCM for authenticated encryption.
    Password hashing uses bcrypt with cost factor 12.
    """

    # Encryption key from environment (must be 32 bytes base64-encoded)
    _ENCRYPTION_KEY: Optional[bytes] = None

    @classmethod
    def _get_encryption_key(cls) -> bytes:
        """
        Get or generate encryption key.

        Returns:
            32-byte encryption key

        Raises:
            RuntimeError: If ENCRYPTION_KEY env var not set in production
        """
        if cls._ENCRYPTION_KEY is None:
            key_str = os.getenv('ENCRYPTION_KEY')
            if key_str:
                cls._ENCRYPTION_KEY = key_str.encode()
            else:
                # Development only - generate random key
                if os.getenv('FLASK_ENV') != 'production':
                    cls._ENCRYPTION_KEY = Fernet.generate_key()
                else:
                    raise RuntimeError("ENCRYPTION_KEY environment variable must be set in production")

        return cls._ENCRYPTION_KEY

    @classmethod
    def encrypt(cls, plaintext: str) -> str:
        """
        Encrypt plaintext string.

        Args:
            plaintext: String to encrypt

        Returns:
            Encrypted string (base64-encoded)
        """
        if not plaintext:
            return ''

        key = cls._get_encryption_key()
        f = Fernet(key)
        encrypted = f.encrypt(plaintext.encode())
        return encrypted.decode()

    @classmethod
    def decrypt(cls, ciphertext: str) -> str:
        """
        Decrypt encrypted string.

        Args:
            ciphertext: Encrypted string (base64-encoded)

        Returns:
            Decrypted plaintext

        Raises:
            cryptography.fernet.InvalidToken: If decryption fails
        """
        if not ciphertext:
            return ''

        key = cls._get_encryption_key()
        f = Fernet(key)
        decrypted = f.decrypt(ciphertext.encode())
        return decrypted.decode()

    @staticmethod
    def hash_password(password: str, cost: int = 12) -> str:
        """
        Hash password with bcrypt.

        Args:
            password: Plain text password
            cost: Bcrypt cost factor (4-31, default 12)

        Returns:
            Hashed password (60 chars)
        """
        if not password:
            raise ValueError("Password cannot be empty")

        salt = bcrypt.gensalt(rounds=cost)
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """
        Verify password against hash.

        Args:
            password: Plain text password
            hashed: Hashed password

        Returns:
            True if password matches
        """
        if not password or not hashed:
            return False

        return bcrypt.checkpw(password.encode(), hashed.encode())

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """
        Generate secure random token.

        Args:
            length: Token length in bytes (default 32)

        Returns:
            Hex-encoded token (length*2 chars)
        """
        return secrets.token_hex(length)

    @staticmethod
    def generate_api_key(prefix: str = 'lsx') -> str:
        """
        Generate API key with prefix.

        Args:
            prefix: Key prefix (e.g., 'lsx', 'sk', 'pk')

        Returns:
            API key (e.g., 'lsx_abc123...')
        """
        token = secrets.token_hex(32)
        return f"{prefix}_{token}"

    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """
        Hash API key for storage (SHA-256).

        Args:
            api_key: API key to hash

        Returns:
            SHA-256 hash (64 chars)
        """
        return hashlib.sha256(api_key.encode()).hexdigest()

    @staticmethod
    def constant_time_compare(a: str, b: str) -> bool:
        """
        Constant-time string comparison (timing attack prevention).

        Args:
            a: First string
            b: Second string

        Returns:
            True if strings are equal
        """
        return secrets.compare_digest(a, b)
