"""
LernsystemX Setup - KI API Configuration (Part 2: Storage & Provider Management)

Handles database persistence and provider lifecycle for AI API keys:
- Encrypted API key storage and retrieval
- Provider activation/deactivation
- Provider statistics
- Convenience functions for quick access

ISO 27001:2013 compliant - Secure API key management

See ai.py for encryption and validation logic (KISetupBase).
This file extends KISetupBase with database storage methods.
"""

import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from app.infrastructure.persistence.database.connection import fetch_one, execute_query, insert_returning
from app.setup.initialization.ai import KISetup as KISetupBase


class KISetup(KISetupBase):
    """
    Full KI Setup with encryption, validation, storage, and provider management.

    Inherits encryption and validation from KISetupBase (ai.py).
    Adds database storage and provider lifecycle methods.
    """

    @classmethod
    def store_api_key(
        cls,
        provider: str,
        api_key: str,
        master_key: str,
        validate: bool = True,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Store encrypted API key in database

        Args:
            provider: AI provider name
            api_key: Plain text API key
            master_key: Master encryption key
            validate: Validate key before storing (default: True)
            metadata: Additional metadata (optional)

        Returns:
            Stored API key configuration

        Raises:
            ValueError: If validation fails

        Example:
            >>> config = KISetup.store_api_key(
            ...     'openai',
            ...     'sk-...',
            ...     master_key,
            ...     metadata={'model': 'gpt-4'}
            ... )
        """
        if provider not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")

        if validate:
            is_valid, message = cls.validate_api_key(provider, api_key)
            if not is_valid:
                raise ValueError(f"API key validation failed: {message}")

        encrypted = cls.encrypt_api_key(api_key, master_key)

        existing = fetch_one(
            "SELECT * FROM ai_api_keys WHERE provider = %s",
            (provider,)
        )

        if existing:
            result = execute_query(
                """
                UPDATE ai_api_keys
                SET encrypted_key = %s,
                    salt = %s,
                    metadata = %s,
                    last_validated = NOW(),
                    updated_at = NOW()
                WHERE provider = %s
                RETURNING *
                """,
                (
                    encrypted['encrypted_key'],
                    encrypted['salt'],
                    json.dumps(metadata or {}),
                    provider
                )
            )
        else:
            result = insert_returning(
                'ai_api_keys',
                {
                    'provider': provider,
                    'encrypted_key': encrypted['encrypted_key'],
                    'salt': encrypted['salt'],
                    'metadata': json.dumps(metadata or {}),
                    'active': True,
                    'last_validated': datetime.utcnow(),
                    'created_at': datetime.utcnow()
                }
            )

        return result

    @classmethod
    def get_api_key(cls, provider: str, master_key: str) -> Optional[str]:
        """
        Retrieve and decrypt API key

        Args:
            provider: AI provider name
            master_key: Master encryption key

        Returns:
            Decrypted API key or None

        Example:
            >>> api_key = KISetup.get_api_key('openai', master_key)
        """
        config = fetch_one(
            "SELECT * FROM ai_api_keys WHERE provider = %s AND active = true",
            (provider,)
        )

        if not config:
            return None

        try:
            return cls.decrypt_api_key(
                config['encrypted_key'],
                config['salt'],
                master_key
            )
        except Exception as e:
            print(f"Error decrypting API key for {provider}: {str(e)}")
            return None

    @classmethod
    def list_configured_providers(cls) -> List[Dict]:
        """
        List all configured AI providers

        Returns:
            List of provider configurations (without decrypted keys)

        Example:
            >>> providers = KISetup.list_configured_providers()
            >>> for p in providers:
            ...     print(f"{p['provider']}: {p['active']}")
        """
        from app.infrastructure.persistence.database.connection import fetch_all

        providers = fetch_all(
            """
            SELECT provider, active, last_validated, metadata, created_at
            FROM ai_api_keys
            ORDER BY provider
            """
        )

        return providers

    @classmethod
    def deactivate_provider(cls, provider: str) -> bool:
        """
        Deactivate AI provider

        Args:
            provider: AI provider name

        Returns:
            bool: True if deactivated successfully

        Example:
            >>> KISetup.deactivate_provider('openai')
        """
        execute_query(
            "UPDATE ai_api_keys SET active = false WHERE provider = %s",
            (provider,)
        )
        return True

    @classmethod
    def activate_provider(cls, provider: str) -> bool:
        """
        Activate AI provider

        Args:
            provider: AI provider name

        Returns:
            bool: True if activated successfully

        Example:
            >>> KISetup.activate_provider('openai')
        """
        execute_query(
            "UPDATE ai_api_keys SET active = true WHERE provider = %s",
            (provider,)
        )
        return True

    @classmethod
    def get_provider_stats(cls) -> Dict:
        """
        Get AI provider statistics

        Returns:
            Dictionary with provider stats

        Example:
            >>> stats = KISetup.get_provider_stats()
            >>> print(f"Active providers: {stats['active_count']}")
        """
        total = fetch_one("SELECT COUNT(*) FROM ai_api_keys")
        active = fetch_one("SELECT COUNT(*) FROM ai_api_keys WHERE active = true")

        return {
            'total': total['count'] if total else 0,
            'active_count': active['count'] if active else 0,
            'supported_providers': cls.SUPPORTED_PROVIDERS
        }


# Convenience functions
def setup_encryption_key() -> str:
    """Generate encryption key"""
    return KISetup.setup_encryption_key()


def store_api_key(provider: str, api_key: str, master_key: str, **kwargs) -> Dict:
    """Quick function to store API key"""
    return KISetup.store_api_key(provider, api_key, master_key, **kwargs)


def validate_api_key(provider: str, api_key: str) -> Tuple[bool, str]:
    """Quick function to validate API key"""
    return KISetup.validate_api_key(provider, api_key)
