"""
AI Providers API Key Management (DDD)

Endpoints for API key management with encryption:
- PUT /api/v1/admin/settings/ai/providers/<id>/api-key - Update provider API key
- DELETE /api/v1/admin/settings/ai/providers/<id>/api-key - Remove API key

Security:
- API keys are encrypted before storage using Fernet
- Keys are NEVER exposed in API responses
- Only 'has_api_key' boolean is returned

Uses:
- Encrypted storage with app.config['SECRET_KEY']
- Audit logging for key changes
"""

from flask import Blueprint, request, jsonify, g, current_app
from typing import Dict, Any, Tuple
from cryptography.fernet import Fernet
import base64
import logging
import hashlib

from app.api.middleware.auth import token_required, permission_required
from app.infrastructure.persistence.repositories.ai.providers import AIProviderRepository
from app.application.services.system.audit.service import AuditService
from app.infrastructure.i18n.error_codes import ErrorCode
from app.infrastructure.i18n.error_codes import error_response

logger = logging.getLogger(__name__)

providers_api_keys_bp = Blueprint(
    'ai_providers_api_keys',
    __name__,
    url_prefix='/admin-panel/settings/ai/providers'
)


def _get_encryption_key() -> bytes:
    """
    Get encryption key from app config.

    Returns:
        32-byte Fernet encryption key
    """
    secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Use SHA256 to derive a 32-byte key from SECRET_KEY
    return base64.urlsafe_b64encode(hashlib.sha256(secret_key.encode()).digest())


def _encrypt_api_key(api_key: str) -> str:
    """
    Encrypt API key for secure storage.

    Args:
        api_key: Plain text API key

    Returns:
        Encrypted API key as string
    """
    fernet = Fernet(_get_encryption_key())
    encrypted = fernet.encrypt(api_key.encode())
    return encrypted.decode()


def _validate_api_key_format(provider_name: str, api_key: str) -> bool:
    """
    Validate API key format based on provider.

    Args:
        provider_name: Provider name (openai, anthropic, etc.)
        api_key: API key to validate

    Returns:
        True if format is valid

    Raises:
        ValueError: If format is invalid
    """
    provider_name_lower = provider_name.lower()

    # OpenAI: sk-proj-... or sk-...
    if provider_name_lower == 'openai':
        if not (api_key.startswith('sk-') or api_key.startswith('sk-proj-')):
            raise ValueError('OpenAI API keys must start with "sk-" or "sk-proj-"')
        if len(api_key) < 20:
            raise ValueError('OpenAI API key too short')

    # Anthropic: sk-ant-...
    elif provider_name_lower == 'anthropic':
        if not api_key.startswith('sk-ant-'):
            raise ValueError('Anthropic API keys must start with "sk-ant-"')
        if len(api_key) < 20:
            raise ValueError('Anthropic API key too short')

    # Google: starts with AIza...
    elif provider_name_lower == 'google':
        if not api_key.startswith('AIza'):
            raise ValueError('Google API keys must start with "AIza"')

    # Generic validation for other providers
    else:
        if len(api_key) < 10:
            raise ValueError('API key too short (minimum 10 characters)')

    return True


@providers_api_keys_bp.route('/<int:provider_id>/api-key', methods=['PUT'])
@permission_required('admin.system:write')
def update_provider_api_key(provider_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Update provider API key.

    Security:
    - API key is encrypted before storage
    - Only 'has_api_key' boolean is returned
    - Audit log created

    Args:
        provider_id: The provider's database ID

    Request Body:
        api_key (str): New API key (plain text, will be encrypted)

    Returns:
        JSON response confirming key update
    """
    try:
        data = request.get_json()
        if not data or 'api_key' not in data:
            return error_response(ErrorCode.VALIDATION_REQUIRED_FIELD, 400,
                details={'field': 'api_key'})

        api_key = data['api_key'].strip()
        if not api_key:
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400,
                details={'field': 'api_key', 'message': 'API key cannot be empty'})

        # Get provider
        provider = AIProviderRepository.get_by_id(provider_id)
        if not provider:
            return error_response(ErrorCode.AI_PROVIDER_NOT_FOUND, 404,
                details={'provider_id': provider_id})

        # Validate API key format
        try:
            _validate_api_key_format(provider.get('name'), api_key)
        except ValueError as ve:
            return error_response(ErrorCode.VALIDATION_INVALID_VALUE, 400,
                details={'field': 'api_key', 'message': str(ve)})

        # Encrypt API key
        encrypted_key = _encrypt_api_key(api_key)

        # Update provider with encrypted key
        updated_provider = AIProviderRepository.update(
            provider_id,
            {
                'api_key_encrypted': encrypted_key,
                'has_api_key': True
            }
        )

        # Don't expose encrypted key
        updated_provider.pop('api_key_encrypted', None)

        # Audit log (NEVER log the actual key!)
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='update_provider_api_key',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            details={
                'provider_name': provider.get('name'),
                'has_api_key': True
            }
        )

        return jsonify({
            'success': True,
            'data': updated_provider,
            'message': f'API key for {provider.get("display_name")} updated'
        }), 200

    except Exception as e:
        logger.error(f"Error updating API key for provider {provider_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500,
            details={'error': str(e)})


@providers_api_keys_bp.route('/<int:provider_id>/api-key', methods=['DELETE'])
@permission_required('admin.system:write')
def remove_provider_api_key(provider_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Remove provider API key.

    Business Rule: Removing API key will disable all operations for this provider.

    Args:
        provider_id: The provider's database ID

    Returns:
        JSON response confirming key removal
    """
    try:
        # Get provider
        provider = AIProviderRepository.get_by_id(provider_id)
        if not provider:
            return error_response(ErrorCode.AI_PROVIDER_NOT_FOUND, 404,
                details={'provider_id': provider_id})

        # Remove API key
        updated_provider = AIProviderRepository.update(
            provider_id,
            {
                'api_key_encrypted': None,
                'has_api_key': False
            }
        )

        # Don't expose encrypted key (should be None anyway)
        updated_provider.pop('api_key_encrypted', None)

        # Audit log
        AuditService.log_action(
            user_id=g.current_user.get('user_id'),
            action='remove_provider_api_key',
            resource_type='ai_provider',
            resource_id=str(provider_id),
            details={
                'provider_name': provider.get('name'),
                'has_api_key': False
            }
        )

        return jsonify({
            'success': True,
            'data': updated_provider,
            'message': f'API key for {provider.get("display_name")} removed'
        }), 200

    except Exception as e:
        logger.error(f"Error removing API key for provider {provider_id}: {e}")
        return error_response(ErrorCode.AI_GENERATION_FAILED, 500,
            details={'error': str(e)})
