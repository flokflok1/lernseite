"""
Curriculum Framework Admin API

Endpoints for managing curriculum frameworks:
- CRUD for frameworks (list, get tree, create, delete)
- AI-powered PDF import (parse preview + confirm)
- Link framework to exam type
- Auto-map questions to curriculum objectives via AI
- Question curriculum tagging (get, add, remove)
- Coverage and relevance statistics

All endpoints require admin authentication.
"""

import logging
from flask import Blueprint, jsonify, request

from app.api.middleware.auth import admin_required
from app.infrastructure.persistence.repositories.exams.curriculum import (
    CurriculumFrameworkRepository,
)
from app.application.services.exams.curriculum_service import CurriculumService

logger = logging.getLogger(__name__)

curriculum_bp = Blueprint(
    'curriculum_admin',
    __name__,
    url_prefix='/admin/curriculum',
)


# --- Frameworks ---

@curriculum_bp.route('/frameworks', methods=['GET'])
@admin_required
def list_frameworks():
    """List all curriculum frameworks."""
    frameworks = CurriculumFrameworkRepository.find_all_frameworks()
    return jsonify({
        'success': True,
        'count': len(frameworks),
        'frameworks': frameworks,
    })


@curriculum_bp.route('/frameworks/<int:framework_id>', methods=['GET'])
@admin_required
def get_framework(framework_id):
    """Get a framework with full tree (sections/positions/objectives)."""
    tree = CurriculumFrameworkRepository.load_framework_tree(framework_id)
    if not tree:
        return jsonify({'success': False, 'error': 'Framework not found'}), 404
    return jsonify({'success': True, 'framework': tree})


@curriculum_bp.route('/frameworks', methods=['POST'])
@admin_required
def create_framework():
    """Create a new curriculum framework."""
    body = request.get_json(silent=True) or {}
    if not body.get('name'):
        return jsonify({
            'success': False,
            'error': 'name is required',
        }), 400
    framework = CurriculumFrameworkRepository.create_framework(body)
    return jsonify({'success': True, 'framework': framework}), 201


@curriculum_bp.route('/frameworks/<int:framework_id>', methods=['DELETE'])
@admin_required
def delete_framework(framework_id):
    """Delete a curriculum framework (cascades to children)."""
    CurriculumFrameworkRepository.delete_framework(framework_id)
    return jsonify({'success': True})


# --- AI PDF Import ---

@curriculum_bp.route('/frameworks/import-pdf', methods=['POST'])
@admin_required
def import_pdf_preview():
    """Parse PDF text with AI and return a preview of the structure."""
    body = request.get_json(silent=True) or {}
    pdf_text = body.get('pdf_text', '')
    if len(pdf_text) < 100:
        return jsonify({
            'success': False,
            'error': 'pdf_text must be at least 100 characters',
        }), 400

    try:
        preview = CurriculumService.parse_pdf_with_ai(pdf_text)
        return jsonify({'success': True, 'preview': preview})
    except ValueError as exc:
        logger.exception("AI PDF parse failed")
        return jsonify({'success': False, 'error': str(exc)}), 422
    except Exception:
        logger.exception("Unexpected error during PDF AI parse")
        return jsonify({
            'success': False,
            'error': 'AI processing failed',
        }), 500


@curriculum_bp.route('/frameworks/import-confirm', methods=['POST'])
@admin_required
def import_confirm():
    """Persist an AI-parsed curriculum structure."""
    body = request.get_json(silent=True) or {}
    try:
        framework = CurriculumService.import_from_ai_result(
            ai_result=body.get('ai_result', body),
            source_document=body.get('source_document'),
        )
        return jsonify({'success': True, 'framework': framework}), 201
    except Exception:
        logger.exception("Failed to import curriculum from AI result")
        return jsonify({
            'success': False,
            'error': 'Import failed',
        }), 500


# --- Framework <-> Exam Type Linking ---

@curriculum_bp.route(
    '/frameworks/<int:framework_id>/link/<exam_type_key>',
    methods=['POST'],
)
@admin_required
def link_framework_to_exam_type(framework_id, exam_type_key):
    """Link a curriculum framework to an exam type."""
    CurriculumFrameworkRepository.link_framework_to_exam_type(
        framework_id, exam_type_key,
    )
    return jsonify({'success': True})


# --- Auto-mapping ---

@curriculum_bp.route('/auto-map/<exam_type_key>', methods=['POST'])
@admin_required
def auto_map_questions(exam_type_key):
    """Auto-map unmapped questions to curriculum objectives via AI."""
    try:
        stats = CurriculumService.auto_map_questions(exam_type_key)
        return jsonify({'success': True, 'stats': stats})
    except ValueError as exc:
        return jsonify({'success': False, 'error': str(exc)}), 400
    except Exception:
        logger.exception("Auto-mapping failed for %s", exam_type_key)
        return jsonify({
            'success': False,
            'error': 'Auto-mapping failed',
        }), 500


# --- Question Curriculum Tags ---

@curriculum_bp.route('/questions/<question_id>/tags', methods=['GET'])
@admin_required
def get_question_tags(question_id):
    """Get curriculum tags for a question."""
    tags = CurriculumFrameworkRepository.find_tags_by_question(
        question_id,
    )
    return jsonify({'success': True, 'tags': tags})


@curriculum_bp.route('/questions/<question_id>/tags', methods=['POST'])
@admin_required
def add_question_tag(question_id):
    """Add a curriculum tag to a question."""
    body = request.get_json(silent=True) or {}
    objective_id = body.get('objective_id')
    if not objective_id:
        return jsonify({
            'success': False,
            'error': 'objective_id is required',
        }), 400
    tag = CurriculumFrameworkRepository.tag_question(
        question_id=question_id,
        objective_id=objective_id,
        confidence=body.get('confidence', 1.0),
        tagged_by='admin',
    )
    return jsonify({'success': True, 'tag': tag}), 201


@curriculum_bp.route(
    '/questions/<question_id>/tags/<int:objective_id>',
    methods=['DELETE'],
)
@admin_required
def remove_question_tag(question_id, objective_id):
    """Remove a curriculum tag from a question."""
    CurriculumFrameworkRepository.remove_question_tag(
        question_id, objective_id,
    )
    return jsonify({'success': True})


# --- Coverage & Relevance Stats ---

@curriculum_bp.route(
    '/frameworks/<int:framework_id>/coverage', methods=['GET'],
)
@admin_required
def get_coverage(framework_id):
    """Get coverage statistics for a curriculum framework."""
    stats = CurriculumFrameworkRepository.get_curriculum_coverage_stats(
        framework_id,
    )
    return jsonify({'success': True, 'coverage': stats})


@curriculum_bp.route(
    '/frameworks/<int:framework_id>/relevance', methods=['GET'],
)
@admin_required
def get_relevance(framework_id):
    """Get relevance weights for a curriculum framework."""
    weights = CurriculumService.get_exam_relevance_weights(framework_id)
    return jsonify({'success': True, 'relevance': weights})
