"""
Exam Intelligence Admin API

Endpoints for managing exam types, regions, and topic taxonomy:
- CRUD for exam type registry
- CRUD for exam regions
- CRUD for topic taxonomy per exam type

All endpoints require admin authentication.
"""

import logging
import re
from flask import Blueprint, jsonify, request

from app.api.middleware.auth import admin_required
from app.infrastructure.persistence.repositories.exams.exam_type_registry import (
    ExamTypeRegistryRepository,
)
from app.infrastructure.persistence.repositories.exams.topic_taxonomy import (
    TopicTaxonomyRepository,
)
from app.infrastructure.persistence.repositories.exams.regions import (
    ExamRegionRepository,
)

logger = logging.getLogger(__name__)

intelligence_bp = Blueprint(
    'exam_intelligence_admin',
    __name__,
    url_prefix='/admin/exam-intelligence',
)


# --- Exam Types ---

@intelligence_bp.route('/types', methods=['GET'])
@admin_required
def list_exam_types():
    """List all registered exam types."""
    types = ExamTypeRegistryRepository.find_all()
    return jsonify({'success': True, 'count': len(types), 'exam_types': types})


@intelligence_bp.route('/types', methods=['POST'])
@admin_required
def create_exam_type():
    """Create a new exam type."""
    body = request.get_json(silent=True) or {}
    if not body.get('exam_type') or not body.get('display_name'):
        return jsonify({
            'success': False,
            'error': 'exam_type and display_name required',
        }), 400
    result = ExamTypeRegistryRepository.create(body)
    # Sync display name into i18n system
    from app.application.services.exams.intelligence_service import sync_exam_type_i18n
    sync_exam_type_i18n(body['exam_type'], body['display_name'])
    return jsonify({'success': True, 'exam_type': result}), 201


@intelligence_bp.route('/types/<exam_type>', methods=['PUT'])
@admin_required
def update_exam_type(exam_type):
    """Update an exam type."""
    body = request.get_json(silent=True) or {}
    result = ExamTypeRegistryRepository.update(exam_type, body)
    if not result:
        return jsonify({'success': False, 'error': 'Exam type not found'}), 404
    # Sync display name into i18n system if provided
    if body.get('display_name'):
        from app.application.services.exams.intelligence_service import sync_exam_type_i18n
        sync_exam_type_i18n(exam_type, body['display_name'])
    return jsonify({'success': True, 'exam_type': result})


@intelligence_bp.route('/types/<exam_type>', methods=['DELETE'])
@admin_required
def delete_exam_type(exam_type):
    """Delete an exam type."""
    ExamTypeRegistryRepository.delete(exam_type)
    return jsonify({'success': True})


# --- Regions ---

@intelligence_bp.route('/regions', methods=['GET'])
@admin_required
def list_regions():
    """List all exam regions."""
    regions = ExamRegionRepository.find_all()
    return jsonify({'success': True, 'count': len(regions), 'regions': regions})


@intelligence_bp.route('/regions', methods=['POST'])
@admin_required
def create_region():
    """Create a new exam region."""
    body = request.get_json(silent=True) or {}
    if not body.get('region_code') or not body.get('display_name'):
        return jsonify({
            'success': False,
            'error': 'region_code and display_name required',
        }), 400
    result = ExamRegionRepository.create(body)
    from app.application.services.exams.intelligence_service import sync_exam_region_i18n
    sync_exam_region_i18n(body['region_code'], body['display_name'])
    return jsonify({'success': True, 'region': result}), 201


@intelligence_bp.route('/regions/<region_code>', methods=['PUT'])
@admin_required
def update_region(region_code):
    """Update a region."""
    body = request.get_json(silent=True) or {}
    result = ExamRegionRepository.update(region_code, body)
    if not result:
        return jsonify({'success': False, 'error': 'Region not found'}), 404
    if body.get('display_name'):
        from app.application.services.exams.intelligence_service import sync_exam_region_i18n
        sync_exam_region_i18n(region_code, body['display_name'])
    return jsonify({'success': True, 'region': result})


@intelligence_bp.route('/regions/<region_code>', methods=['DELETE'])
@admin_required
def delete_region(region_code):
    """Delete a region."""
    ExamRegionRepository.delete(region_code)
    return jsonify({'success': True})


# --- Topics ---

@intelligence_bp.route('/types/<exam_type>/topics', methods=['GET'])
@admin_required
def list_topics(exam_type):
    """List all topics for an exam type."""
    topics = TopicTaxonomyRepository.find_by_exam_type(exam_type)
    return jsonify({'success': True, 'count': len(topics), 'topics': topics})


@intelligence_bp.route('/types/<exam_type>/topics', methods=['POST'])
@admin_required
def create_topic(exam_type):
    """Create a new topic in the taxonomy."""
    body = request.get_json(silent=True) or {}
    body['exam_type'] = exam_type
    if not body.get('topic_key') or not body.get('topic_label'):
        return jsonify({
            'success': False,
            'error': 'topic_key and topic_label required',
        }), 400
    result = TopicTaxonomyRepository.create(body)
    return jsonify({'success': True, 'topic': result}), 201


@intelligence_bp.route('/topics/<topic_id>', methods=['PUT'])
@admin_required
def update_topic(topic_id):
    """Update a topic."""
    body = request.get_json(silent=True) or {}
    result = TopicTaxonomyRepository.update(topic_id, body)
    if not result:
        return jsonify({'success': False, 'error': 'Topic not found'}), 404
    return jsonify({'success': True, 'topic': result})


@intelligence_bp.route('/topics/<topic_id>', methods=['DELETE'])
@admin_required
def delete_topic(topic_id):
    """Delete a topic."""
    TopicTaxonomyRepository.delete(topic_id)
    return jsonify({'success': True})


# --- Taxonomy Bootstrap ---

@intelligence_bp.route('/types/<exam_type>/topics/bootstrap', methods=['POST'])
@admin_required
def bootstrap_taxonomy(exam_type):
    """Bootstrap topic taxonomy for an exam type via AI grouping.

    Body (optional): {"provider": "...", "model": "..."}
    """
    body = request.get_json(silent=True) or {}
    provider = body.get('provider')
    model = body.get('model')

    from app.application.services.exams.taxonomy_bootstrap_service import (
        TaxonomyBootstrapService,
    )
    try:
        result = TaxonomyBootstrapService.bootstrap_exam_type(
            exam_type=exam_type,
            provider=provider,
            model=model,
        )
    except ValueError as exc:
        logger.warning("Taxonomy bootstrap failed for %s: %s", exam_type, exc)
        return jsonify({'success': False, 'error': str(exc)}), 422
    except Exception:
        logger.exception("Taxonomy bootstrap error for %s", exam_type)
        raise

    return jsonify({'success': True, 'data': result}), 200


@intelligence_bp.route(
    '/types/<exam_type>/topics/classify-orphan', methods=['POST'],
)
@admin_required
def classify_orphan_topic(exam_type):
    """Classify a single orphan topic into an existing parent category.

    Body: {"topic_key": "...", "provider": "...", "model": "..."}
    """
    body = request.get_json(silent=True) or {}
    topic_key = body.get('topic_key', '')
    if not topic_key:
        return jsonify({
            'success': False, 'error': 'topic_key required',
        }), 400

    # W4: Input validation — max 100 chars, alphanumeric + underscores/hyphens/spaces
    if len(topic_key) > 100:
        return jsonify({
            'success': False,
            'error': 'topic_key must be at most 100 characters',
        }), 400
    if not re.match(r'^[\w\s\-äöüÄÖÜß]+$', topic_key):
        return jsonify({
            'success': False,
            'error': 'topic_key contains invalid characters',
        }), 400

    from app.application.services.exams.taxonomy_bootstrap_service import (
        TaxonomyBootstrapService,
    )
    try:
        result = TaxonomyBootstrapService.classify_orphan_topic(
            exam_type=exam_type,
            topic_key=topic_key,
            provider=body.get('provider'),
            model=body.get('model'),
        )
    except ValueError as exc:
        logger.warning(
            "Classify orphan failed for %s/%s: %s",
            exam_type, topic_key, exc,
        )
        return jsonify({'success': False, 'error': str(exc)}), 422
    except Exception:
        logger.exception(
            "Classify orphan error for %s/%s", exam_type, topic_key,
        )
        raise

    return jsonify({'success': True, 'data': result}), 200
