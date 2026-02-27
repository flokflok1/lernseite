"""
LernsystemX AI Provider Repository

Data access layer for AI Providers:
- CRUD operations for AI providers (OpenAI, Anthropic, etc.)
- API key encryption/decryption
- Provider health tracking

Phase B24-05 - ISO 27001:2013 compliant
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
import os
import hashlib
from cryptography.fernet import Fernet
import base64

from app.infrastructure.persistence.database.connection import fetch_one, fetch_all, execute_query


class AIProviderRepository:
    """
    Repository for AI Provider entity

    Handles all database operations for AI providers including:
    - Provider CRUD operations
    - API key encryption/decryption
    - Health status tracking
    """

    table_name = 'ai_pipeline.ai_providers'

    # Encryption key derived from SECRET_KEY
    _fernet = None

    @classmethod
    def _get_fernet(cls):
        """Get or create Fernet instance for encryption"""
        if cls._fernet is None:
            secret_key = os.environ.get('SECRET_KEY', 'default-secret-key-change-me')
            # Derive a 32-byte key from SECRET_KEY using SHA256
            key = hashlib.sha256(secret_key.encode()).digest()
            cls._fernet = Fernet(base64.urlsafe_b64encode(key))
        return cls._fernet

    @classmethod
    def _encrypt_api_key(cls, api_key: str) -> tuple[str, str]:
        """
        Encrypt an API key

        Args:
            api_key: Plain text API key

        Returns:
            Tuple of (encrypted_key, salt)
        """
        if not api_key:
            return None, None

        fernet = cls._get_fernet()
        # Generate a random salt
        salt = os.urandom(16).hex()
        # Encrypt the API key
        encrypted = fernet.encrypt(api_key.encode()).decode()
        return encrypted, salt

    @classmethod
    def _decrypt_api_key(cls, encrypted_key: str, salt: str) -> Optional[str]:
        """
        Decrypt an API key

        Args:
            encrypted_key: Encrypted API key
            salt: Encryption salt

        Returns:
            Decrypted API key or None
        """
        import logging
        logger = logging.getLogger(__name__)

        if not encrypted_key:
            logger.warning("_decrypt_api_key: No encrypted_key provided")
            return None

        try:
            fernet = cls._get_fernet()
            logger.debug(f"_decrypt_api_key: Decrypting key (length: {len(encrypted_key)})")
            decrypted = fernet.decrypt(encrypted_key.encode()).decode()
            logger.info(f"_decrypt_api_key: Successfully decrypted API key (length: {len(decrypted)})")
            return decrypted
        except Exception as e:
            logger.error(f"_decrypt_api_key: Failed to decrypt API key: {str(e)}")
            logger.error(f"_decrypt_api_key: SECRET_KEY starts with: {os.environ.get('SECRET_KEY', 'NOT_SET')[:20]}...")
            return None

    @classmethod
    def get_all(cls, include_inactive: bool = False) -> List[Dict[str, Any]]:
        """
        Get all AI providers

        Args:
            include_inactive: Include inactive providers

        Returns:
            List of providers (without decrypted API keys)
        """
        query = """
            SELECT
                provider_id,
                name,
                display_name,
                provider_type,
                base_url,
                api_version,
                active,
                priority,
                rate_limit_per_minute,
                config,
                last_validated,
                created_at,
                updated_at,
                CASE WHEN encrypted_api_key IS NOT NULL THEN true ELSE false END as has_api_key
            FROM ai_pipeline.ai_providers
        """

        if not include_inactive:
            query += " WHERE active = TRUE"

        query += " ORDER BY priority DESC, name ASC"

        return fetch_all(query)

    @classmethod
    def get_by_id(cls, provider_id: int) -> Optional[Dict[str, Any]]:
        """
        Get provider by ID

        Args:
            provider_id: Provider ID

        Returns:
            Provider dict or None
        """
        query = """
            SELECT
                provider_id,
                name,
                display_name,
                provider_type,
                base_url,
                api_version,
                active,
                priority,
                rate_limit_per_minute,
                config,
                last_validated,
                created_at,
                updated_at,
                CASE WHEN encrypted_api_key IS NOT NULL THEN true ELSE false END as has_api_key
            FROM ai_pipeline.ai_providers
            WHERE provider_id = %s
        """
        return fetch_one(query, (provider_id,))

    @classmethod
    def get_by_name(cls, name: str) -> Optional[Dict[str, Any]]:
        """
        Get provider by name

        Args:
            name: Provider name (e.g., 'openai', 'anthropic')

        Returns:
            Provider dict or None
        """
        query = """
            SELECT
                provider_id,
                name,
                display_name,
                provider_type,
                base_url,
                api_version,
                encrypted_api_key,
                encryption_salt,
                active,
                priority,
                rate_limit_per_minute,
                config,
                last_validated,
                created_at,
                updated_at
            FROM ai_pipeline.ai_providers
            WHERE name = %s
        """
        return fetch_one(query, (name,))

    @classmethod
    def get_decrypted_api_key(cls, provider_name: str) -> Optional[str]:
        """
        Get decrypted API key for a provider

        Args:
            provider_name: Provider name

        Returns:
            Decrypted API key or None
        """
        provider = cls.get_by_name(provider_name)
        if not provider:
            return None

        return cls._decrypt_api_key(
            provider.get('encrypted_api_key'),
            provider.get('encryption_salt')
        )

    @classmethod
    def update_api_key(cls, provider_id: int, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Update provider API key (encrypted)

        Args:
            provider_id: Provider ID
            api_key: Plain text API key

        Returns:
            Updated provider or None
        """
        encrypted_key, salt = cls._encrypt_api_key(api_key)

        query = """
            UPDATE ai_pipeline.ai_providers
            SET
                encrypted_api_key = %s,
                encryption_salt = %s,
                updated_at = NOW()
            WHERE provider_id = %s
            RETURNING provider_id, name, display_name, provider_type, active, priority,
                      CASE WHEN encrypted_api_key IS NOT NULL THEN true ELSE false END as has_api_key
        """

        return fetch_one(query, (encrypted_key, salt, provider_id))

    @classmethod
    def update_provider(cls, provider_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update provider settings

        Args:
            provider_id: Provider ID
            data: Update data (active, priority, base_url, etc.)

        Returns:
            Updated provider or None
        """
        allowed_fields = ['active', 'priority', 'base_url', 'api_version', 'rate_limit_per_minute', 'config', 'display_name']
        updates = []
        params = []

        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])

        if not updates:
            return cls.get_by_id(provider_id)

        updates.append("updated_at = NOW()")
        params.append(provider_id)

        query = f"""
            UPDATE ai_pipeline.ai_providers
            SET {', '.join(updates)}
            WHERE provider_id = %s
            RETURNING provider_id, name, display_name, provider_type, active, priority,
                      base_url, api_version, rate_limit_per_minute, config,
                      CASE WHEN encrypted_api_key IS NOT NULL THEN true ELSE false END as has_api_key
        """

        return fetch_one(query, tuple(params))

    @classmethod
    def set_active(cls, provider_id: int, active: bool) -> Optional[Dict[str, Any]]:
        """
        Set provider active status

        Args:
            provider_id: Provider ID
            active: Active status

        Returns:
            Updated provider or None
        """
        query = """
            UPDATE ai_pipeline.ai_providers
            SET active = %s, updated_at = NOW()
            WHERE provider_id = %s
            RETURNING provider_id, name, display_name, active
        """
        return fetch_one(query, (active, provider_id))

    @classmethod
    def validate_api_key(cls, provider_id: int, is_valid: bool) -> Optional[Dict[str, Any]]:
        """
        Update last validation timestamp

        Args:
            provider_id: Provider ID
            is_valid: Whether the API key is valid

        Returns:
            Updated provider or None
        """
        query = """
            UPDATE ai_pipeline.ai_providers
            SET last_validated = NOW(), updated_at = NOW()
            WHERE provider_id = %s
            RETURNING provider_id, name, last_validated
        """
        return fetch_one(query, (provider_id,))

    @classmethod
    def log_health_check(cls, provider_id: int, status: str, response_time_ms: int = None, error_message: str = None):
        """
        Log a health check result

        Args:
            provider_id: Provider ID
            status: Health status (healthy, degraded, down, unknown)
            response_time_ms: Response time in milliseconds
            error_message: Error message if any
        """
        query = """
            INSERT INTO ai_pipeline.ai_provider_health (provider_id, status, response_time_ms, error_message)
            VALUES (%s, %s, %s, %s)
        """
        execute_query(query, (provider_id, status, response_time_ms, error_message))

    @classmethod
    def get_health_history(cls, provider_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get health check history for a provider

        Args:
            provider_id: Provider ID
            limit: Number of records to return

        Returns:
            List of health check records
        """
        query = """
            SELECT health_id, status, response_time_ms, error_message, checked_at
            FROM ai_pipeline.ai_provider_health
            WHERE provider_id = %s
            ORDER BY checked_at DESC
            LIMIT %s
        """
        return fetch_all(query, (provider_id, limit))

    @classmethod
    def get_active_provider(cls, provider_type: str = None) -> Optional[Dict[str, Any]]:
        """
        Get highest priority active provider

        Args:
            provider_type: Optional filter by provider type

        Returns:
            Active provider with highest priority
        """
        query = """
            SELECT
                provider_id,
                name,
                display_name,
                provider_type,
                base_url,
                api_version,
                encrypted_api_key,
                encryption_salt,
                active,
                priority,
                rate_limit_per_minute,
                config
            FROM ai_pipeline.ai_providers
            WHERE active = TRUE
            AND encrypted_api_key IS NOT NULL
        """

        if provider_type:
            query += " AND provider_type = %s"
            query += " ORDER BY priority DESC LIMIT 1"
            return fetch_one(query, (provider_type,))

        query += " ORDER BY priority DESC LIMIT 1"
        return fetch_one(query)

    @classmethod
    def create(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new AI provider.

        Args:
            data: Provider data (name, display_name, description, base_url, etc.)

        Returns:
            Created provider dict
        """
        query = """
            INSERT INTO ai_pipeline.ai_providers
                (name, display_name, provider_type, base_url, api_version, active, priority)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING provider_id, name, display_name, provider_type, base_url,
                      api_version, active, priority, created_at,
                      CASE WHEN encrypted_api_key IS NOT NULL THEN true ELSE false END as has_api_key
        """
        return fetch_one(query, (
            data.get('name'),
            data.get('display_name'),
            data.get('provider_type', data.get('name', 'custom')),
            data.get('base_url'),
            data.get('api_version'),
            data.get('active', True),
            data.get('priority', 0),
        ))

    @classmethod
    def update(cls, provider_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Alias for update_provider (backward compatibility)."""
        return cls.update_provider(provider_id, data)

    @classmethod
    def delete(cls, provider_id: int) -> bool:
        """
        Delete an AI provider.

        Args:
            provider_id: Provider ID

        Returns:
            True if deleted
        """
        query = "DELETE FROM ai_pipeline.ai_providers WHERE provider_id = %s"
        execute_query(query, (provider_id,))
        return True

    @classmethod
    def seed_defaults(cls) -> int:
        """
        Seed default AI providers if they don't exist.

        Idempotent — safe to call on every app start.

        Returns:
            Number of providers seeded
        """
        defaults = [
            ('openai', 'OpenAI', 'openai', 'https://api.openai.com/v1', 'v1', 1),
            ('anthropic', 'Anthropic', 'anthropic', 'https://api.anthropic.com/v1', '2023-06-01', 2),
            ('google', 'Google AI', 'google', 'https://generativelanguage.googleapis.com/v1', 'v1', 3),
        ]

        count_before = fetch_one(
            "SELECT COUNT(*) as cnt FROM ai_pipeline.ai_providers"
        )
        before = count_before['cnt'] if count_before else 0

        for name, display, ptype, url, ver, prio in defaults:
            execute_query("""
                INSERT INTO ai_pipeline.ai_providers
                    (name, display_name, provider_type, base_url, api_version, active, priority)
                VALUES (%s, %s, %s, %s, %s, true, %s)
                ON CONFLICT (name) DO NOTHING
            """, (name, display, ptype, url, ver, prio))

        count_after = fetch_one(
            "SELECT COUNT(*) as cnt FROM ai_pipeline.ai_providers"
        )
        after = count_after['cnt'] if count_after else 0

        return after - before

    @classmethod
    def clear_api_key(cls, provider_id: int) -> Optional[Dict[str, Any]]:
        """
        Remove API key from provider

        Args:
            provider_id: Provider ID

        Returns:
            Updated provider or None
        """
        query = """
            UPDATE ai_pipeline.ai_providers
            SET
                encrypted_api_key = NULL,
                encryption_salt = NULL,
                active = FALSE,
                updated_at = NOW()
            WHERE provider_id = %s
            RETURNING provider_id, name, active
        """
        return fetch_one(query, (provider_id,))
