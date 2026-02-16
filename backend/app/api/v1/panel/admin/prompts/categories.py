"""
Prompts Categories Endpoints (DDD)

Category and style listing endpoints.
Uses PromptCategory and PromptStyle value objects.
"""

from flask import request, jsonify
from typing import Dict, Any, Tuple
import logging

from app.core.bootstrap.extensions import limiter
from app.api.middleware.auth import permission_required

from app.api.v1.panel.admin.prompts.value_objects import PromptCategory, PromptStyle

from app.api.v1.panel.admin.prompts.blueprints import prompts_categories_bp

logger = logging.getLogger(__name__)


@prompts_categories_bp.route('/categories', methods=['GET'])
@permission_required('content.courses:write')
@limiter.limit("60 per minute")
def list_prompt_categories() -> Tuple[Dict[str, Any], int]:
    """
    List available prompt categories with their styles.

    Returns:
        JSON response with categories list

    DDD: Uses PromptCategory value objects

    Response:
        {
            "success": true,
            "categories": [
                {
                    "id": "theory",
                    "name": "Theorieblatt",
                    "icon": "book",
                    "styles": ["adhs", "detailed", "short", "exam_focus"]
                }
            ]
        }
    """
    try:
        # Build categories from value objects
        categories = []
        for category in PromptCategory:
            categories.append({
                'id': category.value,
                'name': category.display_name,
                'icon': _get_category_icon(category),
                'description': _get_category_description(category),
                'styles': [style.value for style in PromptStyle]
            })

        return jsonify({
            'success': True,
            'categories': categories
        }), 200

    except Exception as e:
        logger.error(f"Error listing prompt categories: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list categories',
            'message': str(e)
        }), 500


@prompts_categories_bp.route('/styles', methods=['GET'])
@permission_required('content.courses:write')
@limiter.limit("60 per minute")
def list_prompt_styles() -> Tuple[Dict[str, Any], int]:
    """
    List available prompt styles.

    Query Parameters:
        category (str): Optional category filter

    Returns:
        JSON response with styles list

    DDD: Uses PromptStyle value objects
    """
    try:
        # Build styles from value objects
        styles = []
        for style in PromptStyle:
            styles.append({
                'id': style.value,
                'name': style.display_name,
                'description': _get_style_description(style)
            })

        return jsonify({
            'success': True,
            'styles': styles
        }), 200

    except Exception as e:
        logger.error(f"Error listing prompt styles: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to list styles',
            'message': str(e)
        }), 500


def _get_category_icon(category: PromptCategory) -> str:
    """Get icon for category."""
    icons = {
        PromptCategory.THEORY: 'book',
        PromptCategory.LESSON: 'book-open',
        PromptCategory.QUIZ: 'help-circle',
        PromptCategory.FLASHCARD: 'layers',
        PromptCategory.TUTOR: 'user',
        PromptCategory.SUMMARY: 'file-text',
        PromptCategory.EXAM: 'award'
    }
    return icons.get(category, 'file')


def _get_category_description(category: PromptCategory) -> str:
    """Get description for category."""
    descriptions = {
        PromptCategory.THEORY: 'Umfassende Theorie für ein Kapitel',
        PromptCategory.LESSON: 'Schritt-für-Schritt Erklärungen',
        PromptCategory.QUIZ: 'Multiple-Choice Fragen',
        PromptCategory.FLASHCARD: 'Frage-Antwort Paare',
        PromptCategory.TUTOR: 'Interaktive Erklärungen',
        PromptCategory.SUMMARY: 'Kompakte Zusammenfassungen',
        PromptCategory.EXAM: 'Prüfungsaufgaben'
    }
    return descriptions.get(category, '')


def _get_style_description(style: PromptStyle) -> str:
    """Get description for style."""
    descriptions = {
        PromptStyle.ADHS: 'Kurze Sätze, klare Struktur, visuell',
        PromptStyle.DETAILED: 'Ausführliche Erklärungen mit Details',
        PromptStyle.SHORT: 'Kompakte Zusammenfassungen',
        PromptStyle.EXAM_FOCUS: 'Fokus auf Prüfungsvorbereitung'
    }
    return descriptions.get(style, '')
