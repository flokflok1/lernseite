"""
LernsystemX Setup - Organization & AI Configuration Routes

REST API endpoints for organisation and AI provider setup:
- POST /setup/organisation - Create organisation (school, company, etc.)
- POST /setup/ki-config - Configure AI API keys
- GET /setup/ki-config - Get configured AI providers

ISO/IEC/IEEE 26515:2018 compliant - API documentation
"""

import os
from flask import request, jsonify
from app.setup import setup_bp
from app.setup.organisation_setup import OrganisationSetup
from app.setup.ki_setup import KISetup


@setup_bp.route('/organisation', methods=['POST'])
def create_organisation():
    """
    Create organisation (school, company, etc.)

    Request Body:
        {
            "name": str,
            "type": "system"|"school"|"company"|"creator_org"|"community",
            "domain": str (optional),
            "branding": {
                "primary_color": str,
                "secondary_color": str,
                "logo_url": str
            } (optional),
            "settings": dict (optional)
        }

    Returns:
        JSON:
        {
            "success": bool,
            "organisation_id": int,
            "name": str,
            "type": str,
            "domain": str,
            "message": str
        }

    Example:
        POST /setup/organisation
        Body: {
            "name": "LSX Academy",
            "type": "system",
            "domain": "lsx.de"
        }
    """
    try:
        # Validate request data
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400

        # Check if creating LSX Academy
        if data.get('type') == 'system' or data.get('name') == 'LSX Academy':
            # Create LSX Academy
            org = OrganisationSetup.create_lsx_academy()
        else:
            # Create custom organisation
            required_fields = ['name', 'type']
            missing_fields = [f for f in required_fields if f not in data]

            if missing_fields:
                return jsonify({
                    'success': False,
                    'error': 'Missing required fields',
                    'missing': missing_fields
                }), 400

            org = OrganisationSetup.create_organisation(
                name=data['name'],
                org_type=data['type'],
                domain=data.get('domain'),
                branding=data.get('branding'),
                settings=data.get('settings')
            )

        return jsonify({
            'success': True,
            'organisation_id': org['organisation_id'],
            'name': org['name'],
            'type': org['type'],
            'domain': org.get('domain'),
            'message': 'Organisation created successfully'
        }), 201

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Organisation creation failed',
            'details': str(e)
        }), 500


@setup_bp.route('/ki-config', methods=['POST'])
def configure_ki():
    """
    Configure AI API keys

    Request Body (Frontend format):
        {
            "openai_api_key": str (optional),
            "anthropic_api_key": str (optional),
            "deepl_api_key": str (optional),
            "validate": bool (optional, default: false)
        }

    Returns:
        JSON:
        {
            "success": bool,
            "configured_providers": list,
            "message": str
        }

    Example:
        POST /setup/ki-config
        Body: {
            "openai_api_key": "sk-...",
            "anthropic_api_key": "",
            "deepl_api_key": ""
        }
    """
    try:
        # Validate request data
        data = request.get_json()

        if not data:
            # Allow empty configuration (skip step)
            return jsonify({
                'success': True,
                'configured_providers': [],
                'message': 'KI configuration skipped (optional step)'
            }), 200

        # Map frontend field names to provider names
        provider_mapping = {
            'openai_api_key': 'openai',
            'anthropic_api_key': 'anthropic',
            'deepl_api_key': 'deepl'
        }

        # Get master encryption key from environment
        master_key = os.getenv('ENCRYPTION_KEY')

        # Generate master key if not exists
        if not master_key:
            master_key = KISetup.setup_encryption_key()
            os.environ['ENCRYPTION_KEY'] = master_key

        # Process each provider
        configured_providers = []
        validate = data.get('validate', False)  # Default to false for setup wizard

        for field_name, provider in provider_mapping.items():
            api_key = data.get(field_name, '').strip()

            # Skip empty keys
            if not api_key:
                continue

            try:
                # Store API key
                result = KISetup.store_api_key(
                    provider=provider,
                    api_key=api_key,
                    master_key=master_key,
                    validate=validate,
                    metadata=None
                )
                configured_providers.append(provider)
            except Exception as e:
                # Log error but continue with other providers
                print(f"Failed to configure {provider}: {str(e)}")

        # Return success even if no providers were configured
        if configured_providers:
            message = f'KI configuration successful: {", ".join(configured_providers)}'
        else:
            message = 'KI configuration skipped (no API keys provided)'

        return jsonify({
            'success': True,
            'configured_providers': configured_providers,
            'message': message
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'KI configuration failed',
            'details': str(e)
        }), 500


@setup_bp.route('/ki-config', methods=['GET'])
def get_ki_config():
    """
    Get configured AI providers

    Returns:
        JSON:
        {
            "success": bool,
            "providers": [
                {
                    "provider": str,
                    "active": bool,
                    "last_validated": str,
                    "metadata": dict
                }
            ],
            "stats": dict
        }

    Example:
        GET /setup/ki-config
        Response: {
            "success": true,
            "providers": [...],
            "stats": {"total": 2, "active_count": 2}
        }
    """
    try:
        providers = KISetup.list_configured_providers()
        stats = KISetup.get_provider_stats()

        return jsonify({
            'success': True,
            'providers': providers,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve KI configuration',
            'details': str(e)
        }), 500
