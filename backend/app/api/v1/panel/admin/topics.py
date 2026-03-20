"""Admin Topics API -- topic hierarchy management.

Endpoints:
- GET    /admin/topics/hierarchy     -- Get topic tree
- POST   /admin/topics/auto-cluster  -- Run AI clustering
- PUT    /admin/topics/<key>/parent  -- Move topic to new parent
- GET    /admin/topics/unmapped      -- List unmapped topics
"""
import logging
from flask import Blueprint, jsonify, request

from app.api.middleware.auth import admin_required

logger = logging.getLogger(__name__)

topics_admin_bp = Blueprint(
    'topics_admin', __name__, url_prefix='/admin/topics',
)


@topics_admin_bp.route('/hierarchy', methods=['GET'])
@admin_required
def get_hierarchy():
    """Return full topic tree."""
    from app.application.services.topics.topic_hierarchy_service import (
        TopicHierarchyService,
    )
    try:
        tree = TopicHierarchyService.get_hierarchy()
        return jsonify({'success': True, 'tree': tree}), 200
    except Exception:
        logger.exception("Failed to load topic hierarchy")
        return jsonify({
            'success': False, 'error': 'Failed to load topic hierarchy',
        }), 500


@topics_admin_bp.route('/auto-cluster', methods=['POST'])
@admin_required
def auto_cluster():
    """Run AI clustering to organize topics into a hierarchy."""
    from app.application.services.topics.topic_hierarchy_service import (
        TopicHierarchyService,
    )
    try:
        result = TopicHierarchyService.auto_cluster()
        return jsonify({'success': True, **result}), 200
    except Exception:
        logger.exception("Failed to auto-cluster topics")
        return jsonify({
            'success': False, 'error': 'Failed to auto-cluster topics',
        }), 500


@topics_admin_bp.route('/<topic_key>/parent', methods=['PUT'])
@admin_required
def move_topic(topic_key: str):
    """Move a topic to a different parent."""
    from app.application.services.topics.topic_hierarchy_service import (
        TopicHierarchyService,
    )
    try:
        data = request.get_json() or {}
        new_parent = data.get('parent_key')
        TopicHierarchyService.move_topic(topic_key, new_parent)
        return jsonify({'success': True}), 200
    except Exception:
        logger.exception("Failed to move topic %s", topic_key)
        return jsonify({
            'success': False, 'error': 'Failed to move topic',
        }), 500


@topics_admin_bp.route('/unmapped', methods=['GET'])
@admin_required
def get_unmapped():
    """List topics from exam questions that have no hierarchy node."""
    from app.infrastructure.persistence.repositories.exams.topic_nodes import (
        TopicNodeRepository,
    )
    try:
        unmapped = TopicNodeRepository.get_unmapped_topics()
        return jsonify({'success': True, 'topics': unmapped}), 200
    except Exception:
        logger.exception("Failed to load unmapped topics")
        return jsonify({
            'success': False, 'error': 'Failed to load unmapped topics',
        }), 500
