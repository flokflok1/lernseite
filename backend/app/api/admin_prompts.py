"""
LernsystemX Admin Prompts API

Prompt template management endpoints for KI-Studio:
- GET    /api/v1/admin/prompts                  - List all prompt templates
- GET    /api/v1/admin/prompts/categories       - List available categories
- GET    /api/v1/admin/prompts/styles           - List styles for a category
- GET    /api/v1/admin/prompts/<id>             - Get prompt details
- POST   /api/v1/admin/prompts                  - Create new prompt
- PATCH  /api/v1/admin/prompts/<id>             - Update prompt
- DELETE /api/v1/admin/prompts/<id>             - Delete prompt (soft)
- POST   /api/v1/admin/prompts/<id>/duplicate   - Duplicate a prompt
- POST   /api/v1/admin/prompts/<id>/set-default - Set as default for category+style
- GET    /api/v1/admin/prompts/preview          - Preview rendered prompt
- GET    /api/v1/admin/prompts/usage-stats      - Get usage statistics

Phase KI-Studio - Prompt Editor
"""

from flask import request, jsonify, g
from pydantic import ValidationError
import logging
import json

logger = logging.getLogger(__name__)

from app.api import api_v1
from app.extensions import limiter
from app.repositories.prompt_template_repository import PromptTemplateRepository
from app.security.permissions import require_permission, Permissions


# ============================================================================
# Prompt Template CRUD
# ============================================================================

@api_v1.route('/admin/prompts', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def list_prompt_templates():
    """
    List all prompt templates.

    Query Parameters:
        category: Filter by category (theory, lesson, quiz, etc.)

    Response 200:
        {
            "success": true,
            "templates": [...],
            "count": 10
        }
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
        logger.error(f"Error listing prompt templates: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to list templates',
            'message': str(e)
        }), 500


@api_v1.route('/admin/prompts/categories', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def list_prompt_categories():
    """
    List available prompt categories with their styles.

    Response 200:
        {
            "success": true,
            "categories": [
                {
                    "id": "theory",
                    "name": "Theorieblatt",
                    "icon": "📚",
                    "styles": ["adhs", "detailed", "short", "exam_focus"]
                }
            ]
        }
    """
    try:
        # Predefined categories with metadata
        categories = [
            {
                'id': 'theory',
                'name': 'Theorieblatt',
                'icon': '📚',
                'description': 'Umfassende Theorie fuer ein Kapitel'
            },
            {
                'id': 'lesson',
                'name': 'Lektions-Erklaerung',
                'icon': '📖',
                'description': 'Schritt-fuer-Schritt Erklaerungen'
            },
            {
                'id': 'quiz',
                'name': 'Quiz-Generator',
                'icon': '❓',
                'description': 'Multiple-Choice Fragen'
            },
            {
                'id': 'flashcard',
                'name': 'Karteikarten',
                'icon': '🃏',
                'description': 'Frage-Antwort Paare'
            },
            {
                'id': 'tutor',
                'name': 'Tutor-Dialog',
                'icon': '👨‍🏫',
                'description': 'Interaktive Erklaerungen'
            },
            {
                'id': 'summary',
                'name': 'Zusammenfassung',
                'icon': '📋',
                'description': 'Kompakte Uebersichten'
            }
        ]

        # Add available styles from DB for each category
        for cat in categories:
            try:
                styles = PromptTemplateRepository.list_styles_for_category(cat['id'])
                cat['styles'] = [s['style'] for s in styles] if styles else ['standard']
            except Exception:
                cat['styles'] = ['standard']

        return jsonify({
            'success': True,
            'categories': categories
        }), 200

    except Exception as e:
        logger.error(f"Error listing categories: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to list categories',
            'message': str(e)
        }), 500


@api_v1.route('/admin/prompts/styles', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def list_prompt_styles():
    """
    List available styles for a category.

    Query Parameters:
        category: Category to get styles for (required)

    Response 200:
        {
            "success": true,
            "category": "theory",
            "styles": [
                {
                    "id": "adhs",
                    "name": "ADHS-freundlich",
                    "icon": "🧠",
                    "description": "Kurz, visuell, Schritt-fuer-Schritt",
                    "is_default": true,
                    "tts_enabled": true
                }
            ]
        }
    """
    try:
        category = request.args.get('category')

        if not category:
            return jsonify({
                'success': False,
                'error': 'category parameter is required'
            }), 400

        # Get templates for this category
        templates = PromptTemplateRepository.list_by_category(category)

        # Group by style
        styles_map = {}
        for t in templates:
            style = t.get('style', 'standard')
            if style not in styles_map:
                styles_map[style] = {
                    'id': style,
                    'name': _get_style_display_name(style),
                    'icon': t.get('icon', '📝'),
                    'description': t.get('description', ''),
                    'is_default': t.get('is_default', False),
                    'tts_enabled': t.get('tts_enabled', False),
                    'template_count': 0
                }
            styles_map[style]['template_count'] += 1
            if t.get('is_default'):
                styles_map[style]['is_default'] = True

        # Predefined styles if none in DB
        if not styles_map:
            styles_map = {
                'standard': {'id': 'standard', 'name': 'Standard', 'icon': '📝', 'is_default': True},
                'adhs': {'id': 'adhs', 'name': 'ADHS-freundlich', 'icon': '🧠', 'is_default': False},
                'short': {'id': 'short', 'name': 'Kurz & Knapp', 'icon': '⚡', 'is_default': False},
                'detailed': {'id': 'detailed', 'name': 'Ausfuehrlich', 'icon': '📚', 'is_default': False},
                'exam_focus': {'id': 'exam_focus', 'name': 'Pruefungsfokus', 'icon': '🎯', 'is_default': False},
            }

        return jsonify({
            'success': True,
            'category': category,
            'styles': list(styles_map.values())
        }), 200

    except Exception as e:
        logger.error(f"Error listing styles: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to list styles',
            'message': str(e)
        }), 500


@api_v1.route('/admin/prompts/<template_id>', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def get_prompt_template(template_id: str):
    """
    Get prompt template details.

    Response 200:
        {
            "success": true,
            "template": {...}
        }
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
        logger.error(f"Error getting template: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get template',
            'message': str(e)
        }), 500


@api_v1.route('/admin/prompts', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def create_prompt_template():
    """
    Create a new prompt template.

    Request Body:
        {
            "code": "my_custom_theory",
            "category": "theory",
            "style": "custom",
            "title": "Mein Custom Theorieblatt",
            "description": "Beschreibung...",
            "system_prompt": "Du bist ein...",
            "user_prompt_template": "Erstelle {{chapter_title}}...",
            "variables": [{"name": "chapter_title", "required": true, "description": "..."}],
            "tts_enabled": true,
            "tts_voice": "alloy"
        }

    Response 201:
        {
            "success": true,
            "template": {...}
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        # Required fields
        required = ['code', 'category', 'title', 'system_prompt', 'user_prompt_template']
        missing = [f for f in required if not data.get(f)]
        if missing:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing)}'
            }), 400

        # Check if code already exists
        existing = PromptTemplateRepository.find_by_code(data['code'])
        if existing:
            return jsonify({
                'success': False,
                'error': f'Template with code "{data["code"]}" already exists'
            }), 409

        # Add created_by
        data['created_by'] = g.current_user['user_id']

        template = PromptTemplateRepository.create(data)

        if not template:
            return jsonify({
                'success': False,
                'error': 'Failed to create template'
            }), 500

        logger.info(f"Created prompt template: {data['code']} by user {g.current_user['user_id']}")

        return jsonify({
            'success': True,
            'template': template
        }), 201

    except Exception as e:
        logger.error(f"Error creating template: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create template',
            'message': str(e)
        }), 500


@api_v1.route('/admin/prompts/<template_id>', methods=['PATCH'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def update_prompt_template(template_id: str):
    """
    Update a prompt template.

    Request Body:
        {
            "title": "Updated title",
            "system_prompt": "Updated system prompt...",
            "user_prompt_template": "Updated user prompt...",
            "tts_enabled": true
        }

    Response 200:
        {
            "success": true,
            "template": {...}
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        # Check if template exists
        existing = PromptTemplateRepository.find_by_id(template_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404

        # Add updated_by
        data['updated_by'] = g.current_user['user_id']

        template = PromptTemplateRepository.update(template_id, data)

        logger.info(f"Updated prompt template: {template_id} by user {g.current_user['user_id']}")

        return jsonify({
            'success': True,
            'template': template
        }), 200

    except Exception as e:
        logger.error(f"Error updating template: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update template',
            'message': str(e)
        }), 500


@api_v1.route('/admin/prompts/<template_id>', methods=['DELETE'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def delete_prompt_template(template_id: str):
    """
    Delete a prompt template (soft delete).

    Note: System templates cannot be deleted.

    Response 200:
        {
            "success": true,
            "message": "Template deleted"
        }
    """
    try:
        # Check if exists
        existing = PromptTemplateRepository.find_by_id(template_id)
        if not existing:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404

        if existing.get('is_system'):
            return jsonify({
                'success': False,
                'error': 'System templates cannot be deleted'
            }), 403

        success = PromptTemplateRepository.delete(template_id)

        if success:
            logger.info(f"Deleted prompt template: {template_id} by user {g.current_user['user_id']}")
            return jsonify({
                'success': True,
                'message': 'Template deleted'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete template'
            }), 500

    except Exception as e:
        logger.error(f"Error deleting template: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete template',
            'message': str(e)
        }), 500


@api_v1.route('/admin/prompts/<template_id>/duplicate', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
@limiter.limit("10 per minute")
def duplicate_prompt_template(template_id: str):
    """
    Duplicate a prompt template.

    Request Body:
        {
            "new_code": "my_custom_theory_v2"
        }

    Response 201:
        {
            "success": true,
            "template": {...}
        }
    """
    try:
        data = request.get_json() or {}
        new_code = data.get('new_code')

        if not new_code:
            # Generate a unique code
            import uuid
            new_code = f"custom_{uuid.uuid4().hex[:8]}"

        # Check if new code already exists
        existing = PromptTemplateRepository.find_by_code(new_code)
        if existing:
            return jsonify({
                'success': False,
                'error': f'Template with code "{new_code}" already exists'
            }), 409

        template = PromptTemplateRepository.duplicate(
            template_id,
            new_code,
            g.current_user['user_id']
        )

        if not template:
            return jsonify({
                'success': False,
                'error': 'Failed to duplicate template (source not found?)'
            }), 404

        logger.info(f"Duplicated prompt template: {template_id} -> {new_code}")

        return jsonify({
            'success': True,
            'template': template
        }), 201

    except Exception as e:
        logger.error(f"Error duplicating template: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to duplicate template',
            'message': str(e)
        }), 500


@api_v1.route('/admin/prompts/<template_id>/set-default', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def set_default_prompt_template(template_id: str):
    """
    Set a template as default for its category and style.

    Response 200:
        {
            "success": true,
            "message": "Template set as default"
        }
    """
    try:
        # Get template to find category and style
        template = PromptTemplateRepository.find_by_id(template_id)
        if not template:
            return jsonify({
                'success': False,
                'error': 'Template not found'
            }), 404

        success = PromptTemplateRepository.set_default(
            template_id,
            template['category'],
            template['style']
        )

        if success:
            logger.info(f"Set default prompt template: {template_id} for {template['category']}/{template['style']}")
            return jsonify({
                'success': True,
                'message': f'Template set as default for {template["category"]}/{template["style"]}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to set default'
            }), 500

    except Exception as e:
        logger.error(f"Error setting default: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to set default',
            'message': str(e)
        }), 500


@api_v1.route('/admin/prompts/preview', methods=['POST'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def preview_prompt():
    """
    Preview a rendered prompt with sample variables.

    Request Body:
        {
            "system_prompt": "Du bist ein Tutor fuer {{course_title}}",
            "user_prompt_template": "Erklaere {{topic}}",
            "variables": {
                "course_title": "Python Grundlagen",
                "topic": "Listen"
            }
        }

    Response 200:
        {
            "success": true,
            "preview": {
                "system": "Du bist ein Tutor fuer Python Grundlagen",
                "user": "Erklaere Listen"
            }
        }
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': 'Request body required'
            }), 400

        system_prompt = data.get('system_prompt', '')
        user_prompt = data.get('user_prompt_template', '')
        variables = data.get('variables', {})

        # Replace variables
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            system_prompt = system_prompt.replace(placeholder, str(var_value))
            user_prompt = user_prompt.replace(placeholder, str(var_value))

        return jsonify({
            'success': True,
            'preview': {
                'system': system_prompt,
                'user': user_prompt
            }
        }), 200

    except Exception as e:
        logger.error(f"Error previewing prompt: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to preview prompt',
            'message': str(e)
        }), 500


@api_v1.route('/admin/prompts/usage-stats', methods=['GET'])
@require_permission(Permissions.ADMIN_COURSE_WRITE)
def get_prompt_usage_stats():
    """
    Get usage statistics for prompt templates.

    Query Parameters:
        template_id: Optional - stats for specific template
        days: Number of days to look back (default 30)

    Response 200:
        {
            "success": true,
            "stats": {
                "total_uses": 150,
                "total_tokens": 500000,
                "total_cost": 12.50,
                "avg_response_time": 2500,
                "tts_count": 45,
                "total_tts_cost": 3.20
            }
        }
    """
    try:
        template_id = request.args.get('template_id')
        days = int(request.args.get('days', 30))

        stats = PromptTemplateRepository.get_usage_stats(template_id, days)

        return jsonify({
            'success': True,
            'stats': stats,
            'period_days': days
        }), 200

    except Exception as e:
        logger.error(f"Error getting usage stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get usage stats',
            'message': str(e)
        }), 500


def _get_style_display_name(style: str) -> str:
    """Get human-readable name for a style."""
    names = {
        'standard': 'Standard',
        'adhs': 'ADHS-freundlich',
        'short': 'Kurz & Knapp',
        'detailed': 'Ausfuehrlich',
        'exam_focus': 'Pruefungsfokus',
        'interactive': 'Interaktiv',
        'visual': 'Visuell'
    }
    return names.get(style, style.replace('_', ' ').title())
