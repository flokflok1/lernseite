"""
LernsystemX Setup - KI API Configuration (Part 1: Encryption & Validation)

Handles secure configuration of AI API keys:
- Encryption key generation and derivation (PBKDF2)
- API key encryption and decryption (Fernet)
- Provider-specific API key validation

ISO 27001:2013 compliant - Secure API key management

See ai_part2.py for database storage and provider management.
"""

import os
import base64
from typing import Dict, Optional, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class KISetup:
    """
    Setup and manage AI API keys

    Implements secure encryption, validation, and storage of API keys.

    Encryption & validation methods are in this file (ai.py).
    Database storage & provider management are in ai_part2.py.
    """

    SUPPORTED_PROVIDERS = ['openai', 'anthropic', 'google', 'cohere', 'huggingface']

    PROVIDER_ENDPOINTS = {
        'openai': 'https://api.openai.com/v1/models',
        'anthropic': 'https://api.anthropic.com/v1/messages',
        'google': 'https://generativelanguage.googleapis.com/v1beta/models',
        'cohere': 'https://api.cohere.ai/v1/check-api-key',
        'huggingface': 'https://huggingface.co/api/whoami'
    }

    @classmethod
    def setup_encryption_key(cls) -> str:
        """
        Generate encryption key for API keys

        Returns:
            Base64-encoded encryption key

        Example:
            >>> key = KISetup.setup_encryption_key()
            >>> # Store this key securely in environment variables
        """
        encryption_key = Fernet.generate_key()
        return encryption_key.decode('utf-8')

    @classmethod
    def derive_encryption_key(cls, master_key: str, salt: Optional[bytes] = None) -> Tuple[Fernet, bytes]:
        """
        Derive encryption key from master key using PBKDF2

        Args:
            master_key: Master encryption key
            salt: Salt for key derivation (generated if None)

        Returns:
            Tuple of (Fernet instance, salt)

        Example:
            >>> fernet, salt = KISetup.derive_encryption_key(master_key)
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        fernet = Fernet(key)

        return fernet, salt

    @classmethod
    def encrypt_api_key(cls, api_key: str, master_key: str) -> Dict[str, str]:
        """
        Encrypt API key

        Args:
            api_key: Plain text API key
            master_key: Master encryption key

        Returns:
            Dictionary with encrypted_key and salt

        Example:
            >>> encrypted = KISetup.encrypt_api_key('sk-...', master_key)
            >>> print(encrypted['encrypted_key'])
        """
        fernet, salt = cls.derive_encryption_key(master_key)
        encrypted = fernet.encrypt(api_key.encode())

        return {
            'encrypted_key': base64.b64encode(encrypted).decode('utf-8'),
            'salt': base64.b64encode(salt).decode('utf-8')
        }

    @classmethod
    def decrypt_api_key(cls, encrypted_key: str, salt: str, master_key: str) -> str:
        """
        Decrypt API key

        Args:
            encrypted_key: Base64-encoded encrypted key
            salt: Base64-encoded salt
            master_key: Master encryption key

        Returns:
            Decrypted API key

        Example:
            >>> api_key = KISetup.decrypt_api_key(encrypted['encrypted_key'], encrypted['salt'], master_key)
        """
        encrypted_bytes = base64.b64decode(encrypted_key.encode())
        salt_bytes = base64.b64decode(salt.encode())

        fernet, _ = cls.derive_encryption_key(master_key, salt_bytes)
        decrypted = fernet.decrypt(encrypted_bytes)

        return decrypted.decode('utf-8')

    @classmethod
    def validate_api_key(cls, provider: str, api_key: str) -> Tuple[bool, str]:
        """
        Validate API key by testing with provider

        Args:
            provider: AI provider name (openai, anthropic, etc.)
            api_key: API key to validate

        Returns:
            Tuple of (is_valid, message)

        Example:
            >>> valid, msg = KISetup.validate_api_key('openai', 'sk-...')
            >>> if not valid:
            ...     print(f"Validation failed: {msg}")
        """
        if provider not in cls.SUPPORTED_PROVIDERS:
            return False, f"Unsupported provider. Must be one of: {', '.join(cls.SUPPORTED_PROVIDERS)}"

        if not api_key or len(api_key) < 10:
            return False, "API key is too short or empty"

        try:
            if provider == 'openai':
                return cls._validate_openai(api_key)
            elif provider == 'anthropic':
                return cls._validate_anthropic(api_key)
            elif provider == 'google':
                return cls._validate_google(api_key)
            elif provider == 'cohere':
                return cls._validate_cohere(api_key)
            elif provider == 'huggingface':
                return cls._validate_huggingface(api_key)
            else:
                return True, "API key format looks valid (not tested with provider)"

        except Exception as e:
            return False, f"Validation error: {str(e)}"

    @staticmethod
    def _validate_openai(api_key: str) -> Tuple[bool, str]:
        """
        Validate OpenAI API key

        Args:
            api_key: OpenAI API key

        Returns:
            Tuple of (is_valid, message)
        """
        try:
            import requests

            headers = {
                'Authorization': f'Bearer {api_key}'
            }

            response = requests.get(
                'https://api.openai.com/v1/models',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return True, "OpenAI API key is valid"
            elif response.status_code == 401:
                return False, "OpenAI API key is invalid (401 Unauthorized)"
            else:
                return False, f"OpenAI API returned status {response.status_code}"

        except ImportError:
            return False, "requests library not installed - cannot validate"
        except Exception as e:
            return False, f"OpenAI validation failed: {str(e)}"

    @staticmethod
    def _validate_anthropic(api_key: str) -> Tuple[bool, str]:
        """
        Validate Anthropic API key

        Args:
            api_key: Anthropic API key

        Returns:
            Tuple of (is_valid, message)
        """
        try:
            import requests

            headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'content-type': 'application/json'
            }

            data = {
                'model': 'claude-3-haiku-20240307',
                'max_tokens': 1,
                'messages': [{'role': 'user', 'content': 'Hi'}]
            }

            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=data,
                timeout=10
            )

            if response.status_code == 200:
                return True, "Anthropic API key is valid"
            elif response.status_code == 401:
                return False, "Anthropic API key is invalid (401 Unauthorized)"
            else:
                return False, f"Anthropic API returned status {response.status_code}"

        except ImportError:
            return False, "requests library not installed - cannot validate"
        except Exception as e:
            return False, f"Anthropic validation failed: {str(e)}"

    @staticmethod
    def _validate_google(api_key: str) -> Tuple[bool, str]:
        """Validate Google API key"""
        try:
            import requests

            response = requests.get(
                f'https://generativelanguage.googleapis.com/v1beta/models?key={api_key}',
                timeout=10
            )

            if response.status_code == 200:
                return True, "Google API key is valid"
            elif response.status_code in [401, 403]:
                return False, "Google API key is invalid"
            else:
                return False, f"Google API returned status {response.status_code}"

        except Exception as e:
            return False, f"Google validation failed: {str(e)}"

    @staticmethod
    def _validate_cohere(api_key: str) -> Tuple[bool, str]:
        """Validate Cohere API key"""
        try:
            import requests

            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.post(
                'https://api.cohere.ai/v1/check-api-key',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return True, "Cohere API key is valid"
            else:
                return False, "Cohere API key is invalid"

        except Exception as e:
            return False, f"Cohere validation failed: {str(e)}"

    @staticmethod
    def _validate_huggingface(api_key: str) -> Tuple[bool, str]:
        """Validate HuggingFace API key"""
        try:
            import requests

            headers = {'Authorization': f'Bearer {api_key}'}
            response = requests.get(
                'https://huggingface.co/api/whoami',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return True, "HuggingFace API key is valid"
            else:
                return False, "HuggingFace API key is invalid"

        except Exception as e:
            return False, f"HuggingFace validation failed: {str(e)}"
