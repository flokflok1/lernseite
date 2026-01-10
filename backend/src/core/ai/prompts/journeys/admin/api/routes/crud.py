"""
Prompts CRUD Endpoints (DDD)

CRUD operations for prompt templates.
Simplified migration from admin/prompts/crud.py.
"""

from flask import request, jsonify, g
from typing import Dict, Any, Tuple
import logging

from app.extensions import limiter
from app.middleware.auth import token_required
from app.security.permissions import require_permission, Permissions
from app.repositories.prompts.templates import PromptTemplateRepository

from . import prompts_crud_bp

logger = logging.getLogger(__name__)


@prompts_crud_bp.route('', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("60 per minute")
def list_prompt_templates() -> Tuple[Dict[str, Any], int]:
    """
    List all prompt templates.

    Query Parameters:
        category (str): Filter by category (theory, lesson, quiz, etc.)

    Returns:
        JSON response with templates list

    DDD: Uses PromptTemplateRepository
    """
    try:
        category = request.args.get('category')

        if category:
            templates = PromptTemplateRepository.list_by_category(category)
        else:
            templates = PromptTemplateRepository.list_all_active()

        return jsonify({
            'success': True,
            'templates': templates,
            'count': len(templates)
        }), 200

    except Exception as e:
        logger.error(f"Error listing prompt templates: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list templates',
            'message': str(e)
        }), 500


@prompts_crud_bp.route('/<template_id>', methods=['GET'])
@token_required
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("60 per minute")
def get_prompt_template(template_id: str) -> Tuple[Dict[str, Any], int]:
    """
    Get prompt template details.

    Args:
        template_id: Template UUID

    Returns:
        JSON response with template details

    DDD: Uses PromptTemplateRepository
    """
    try:
        template = PromptTemplateRepository.find_by_id(template_id)

        if not template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404

        return jsonify({
            'success': True,
            'template': template
        }), 200

    except Exception as e:
        logger.error(f"Error getting prompt template {template_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get template',
            'message': str(e)
        }), 500


# Additional CRUD endpoints (create, update, delete) - simplified for migration
# Full implementation uses existing PromptTemplateRepository methods
