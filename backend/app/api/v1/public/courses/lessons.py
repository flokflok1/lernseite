"""
LernsystemX Courses API - Lesson Progress & Methods

User-facing lesson endpoints for progress tracking and method retrieval.

Endpoints:
- GET /lessons/:id - Get lesson details
- GET /lessons/:id/progress - Get lesson progress
- POST /lessons/:id/start - Mark lesson as started
- POST /lessons/:id/complete - Mark lesson as completed
- PATCH /lessons/:id/progress - Update lesson progress
- GET /lessons/:id/methods - Get learning methods for lesson

All routes: /api/v1/lessons/*
"""

from flask import Blueprint, request, jsonify
import json
import logging
import re

from app.infrastructure.persistence.repositories.courses.lessons import LessonRepository
from app.infrastructure.persistence.repositories.learning_method.instances import (
    LearningMethodInstanceRepository,
)
from app.infrastructure.persistence.repositories.learning_method.progress import (
    LearningMethodProgressRepository,
)
from app.api.middleware.auth import token_required, get_current_user

logger = logging.getLogger(__name__)

lessons_bp = Blueprint('lessons_public', __name__, url_prefix='/lessons')

__all__ = ['lessons_bp']


def _build_lesson_progress(record, lesson_id, user_id):
    """Build a LessonProgress response from a DB record (or None)."""
    if not record:
        return {
            'lesson_id': str(lesson_id),
            'user_id': str(user_id),
            'status': 'not_started',
            'progress_percentage': 0,
            'time_spent_minutes': 0,
            'started_at': None,
            'completed_at': None,
            'last_accessed_at': None,
        }

    completed_at = record.get('completed_at')
    status = 'completed' if completed_at else 'in_progress'
    time_seconds = record.get('time_spent_seconds') or 0

    return {
        'lesson_id': str(record.get('lesson_id', lesson_id)),
        'user_id': str(record.get('user_id', user_id)),
        'status': status,
        'progress_percentage': 100 if completed_at else 50,
        'time_spent_minutes': round(time_seconds / 60, 1),
        'started_at': None,
        'completed_at': str(completed_at) if completed_at else None,
        'last_accessed_at': None,
    }


@lessons_bp.route('/<lesson_id>', methods=['GET'])
@token_required
def get_lesson(lesson_id: str):
    """Get lesson details by ID."""
    try:
        lesson = LessonRepository.find_by_id(lesson_id)
        if not lesson:
            return jsonify({'success': False, 'error': 'Lesson not found'}), 404

        # Transform content for frontend compatibility
        raw_content = lesson.get('content')
        if isinstance(raw_content, str):
            # Strip <p>...</p> wrapper (legacy data from AI authoring)
            cleaned = re.sub(r'^<p>(.*)</p>$', r'\1', raw_content.strip(), flags=re.DOTALL).strip()

            # Try to parse JSON string (AI-generated content stored via json.dumps)
            try:
                parsed = json.loads(cleaned)
                if isinstance(parsed, dict):
                    lesson['content'] = parsed
                else:
                    lesson['content'] = {'html': raw_content}
            except (json.JSONDecodeError, TypeError):
                lesson['content'] = {'html': raw_content}

        return jsonify({'success': True, 'lesson': lesson}), 200

    except Exception as e:
        logger.error(f"Error getting lesson: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500


@lessons_bp.route('/<lesson_id>/progress', methods=['GET'])
@token_required
def get_lesson_progress(lesson_id: str):
    """Get user's progress for a lesson."""
    try:
        user = get_current_user()
        record = LessonRepository.get_user_progress(lesson_id, user['user_id'])
        progress = _build_lesson_progress(record, lesson_id, user['user_id'])

        return jsonify({'success': True, 'progress': progress}), 200

    except Exception as e:
        logger.error(f"Error getting lesson progress: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500


@lessons_bp.route('/<lesson_id>/start', methods=['POST'])
@token_required
def start_lesson(lesson_id: str):
    """Mark a lesson as started for the current user."""
    try:
        user = get_current_user()
        record = LessonRepository.mark_started(lesson_id, user['user_id'])
        progress = _build_lesson_progress(record, lesson_id, user['user_id'])

        return jsonify({'success': True, 'progress': progress}), 200

    except Exception as e:
        logger.error(f"Error starting lesson: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500


@lessons_bp.route('/<lesson_id>/complete', methods=['POST'])
@token_required
def complete_lesson(lesson_id: str):
    """Mark a lesson as completed for the current user."""
    try:
        user = get_current_user()
        record = LessonRepository.mark_completed(lesson_id, user['user_id'])
        progress = _build_lesson_progress(record, lesson_id, user['user_id'])

        return jsonify({'success': True, 'progress': progress}), 200

    except Exception as e:
        logger.error(f"Error completing lesson: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500


@lessons_bp.route('/<lesson_id>/progress', methods=['PATCH'])
@token_required
def update_lesson_progress(lesson_id: str):
    """Update lesson progress (time spent, score)."""
    try:
        user = get_current_user()
        data = request.get_json() or {}

        time_spent_minutes = data.get('time_spent_minutes')
        time_spent_seconds = (
            int(time_spent_minutes * 60) if time_spent_minutes else None
        )
        score = data.get('score')

        record = LessonRepository.update_progress(
            lesson_id, user['user_id'],
            time_spent_seconds=time_spent_seconds,
            score=score,
        )
        progress = _build_lesson_progress(record, lesson_id, user['user_id'])

        return jsonify({'success': True, 'progress': progress}), 200

    except Exception as e:
        logger.error(f"Error updating lesson progress: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500


@lessons_bp.route('/<lesson_id>/methods', methods=['GET'])
@token_required
def get_lesson_methods(lesson_id: str):
    """Get learning methods assigned to a lesson."""
    try:
        methods = LearningMethodInstanceRepository.find_by_lesson(
            lesson_id, published_only=True
        )

        return jsonify({
            'success': True,
            'methods': methods or [],
            'total': len(methods) if methods else 0,
        }), 200

    except Exception as e:
        logger.error(f"Error getting lesson methods: {e}")
        return jsonify({
            'success': True,
            'methods': [],
            'total': 0,
        }), 200


@lessons_bp.route('/<lesson_id>/methods/progress', methods=['GET'])
@token_required
def get_lesson_methods_progress(lesson_id: str):
    """Get user's progress for all learning methods in a lesson."""
    try:
        user = get_current_user()
        progress_list = LearningMethodProgressRepository.get_user_progress_for_lesson(
            user['user_id'], lesson_id
        )

        progress_map = {}
        for p in progress_list:
            progress_map[str(p['method_id'])] = {
                'method_id': str(p['method_id']),
                'score': float(p['score']) if p.get('score') is not None else None,
                'attempts': p.get('attempts', 0),
                'completed': p.get('completed_at') is not None,
            }

        return jsonify({'success': True, 'progress': progress_map}), 200

    except Exception as e:
        logger.error(f"Error getting lesson methods progress: {e}")
        return jsonify({'success': True, 'progress': {}}), 200
