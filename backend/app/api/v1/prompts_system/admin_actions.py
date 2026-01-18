"""
Prompts Actions Endpoints (DDD)

Actions for prompt templates: duplicate, set-default, preview, usage-stats.
Simplified migration from admin/prompts/actions.py.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.extensions import limiter
from app.api.middleware.auth import token_required
from app.infrastructure.security.permissions import require_permission, Permissions
from app.infrastructure.persistence.repositories.prompts.templates import PromptTemplateRepository

from app.api.v1.prompts_system.blueprints import prompts_actions_bp

logger = logging.getLogger(__name__)


@prompts_actions_bp.route('/<template_id>/duplicate', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("30 per minute")
def duplicate_prompt_template(template_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Duplicate a prompt template.

    Args:
        template_id: Template UUID to duplicate

    Returns:
        JSON response with new template

    DDD: Business rule - creates copy with "(Copy)" suffix
    """
    try:
        # Fetch original template
        original = PromptTemplateRepository.find_by_id(template_id)
        if not original:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404

        # Create duplicate
        user_id = g.current_user['user_id']
        duplicate = PromptTemplateRepository.duplicate(template_id, user_id)

        return jsonify({
            'success': True,
            'template': duplicate,
            'message': 'Template duplicated'
        }), 201

    except Exception as e:
        logger.error(f"Error duplicating prompt template: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to duplicate template',
            'message': str(e)
        }), 500


@prompts_actions_bp.route('/<template_id>/set-default', methods=['POST'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("30 per minute")
def set_default_prompt_template(template_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Set a template as default for its category/style combination.

    Args:
        template_id: Template UUID

    Returns:
        JSON response with success status

    DDD: Business rule - only one default per category/style
    """
    try:
        success = PromptTemplateRepository.set_as_default(template_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Template set as default'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to set as default'
            }), 500

    except Exception as e:
        logger.error(f"Error setting default prompt template: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to set as default',
            'message': str(e)
        }), 500


# Additional action endpoints (preview, usage-stats) - simplified for migration
# Full implementation uses existing PromptTemplateRepository methods
