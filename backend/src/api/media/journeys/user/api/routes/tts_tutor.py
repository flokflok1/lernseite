"""
Media Domain - TTS Tutor Routes (User Journey)

Tutor knowledge and context endpoints for TTS integration.

Endpoints:
- POST /tutor/knowledge - Load tutor knowledge (course/chapter)
- GET /tutor/course/<id>/context - Get course context for tutor
- GET /tutor/chapter/<id>/context - Get chapter context for tutor

Architecture: Journey-Based DDD (User)
Database: PostgreSQL via CourseRepository (direct SQL)
ISO 27001:2013 compliant - Tutor context management
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
import logging

from app.middleware.auth import token_required
from app.repositories.course import CourseRepository
from app.repositories.chapter import ChapterRepository

logger = logging.getLogger(__name__)

tts_tutor_bp = Blueprint('tts_tutor', __name__, url_prefix='/tutor')


@tts_tutor_bp.route('/knowledge', methods=['POST'])
@token_required
def get_tutor_knowledge():
    """
    Load tutor knowledge for course or chapter

    Request Body:
        {
            "course_id": "123",      // Optional
            "chapter_id": "456",     // Optional
            "knowledge_type": "full" // Optional: full, summary, outline
        }

    Response:
        200: Knowledge loaded
        {
            "success": true,
            "data": {
                "knowledge_type": "full",
                "course_title": "...",
                "chapter_title": "...",
                "content": "..."
            }
        }

        400: Invalid request
        404: Course/chapter not found

    Notes:
        - Loads course/chapter content for tutor context
        - Used to prepare AI tutor with domain knowledge
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        course_id = data.get('course_id')
        chapter_id = data.get('chapter_id')
        knowledge_type = data.get('knowledge_type', 'full')

        if not course_id and not chapter_id:
            return jsonify({'success': False, 'error': {'code': 'NO_ID', 'message': 'Provide course_id or chapter_id'}}), 400

        # Load knowledge
        knowledge = {}

        if chapter_id:
            chapter = ChapterRepository.find_by_id(chapter_id)
            if not chapter:
                return jsonify({'success': False, 'error': 'Chapter not found'}), 404

            knowledge['chapter_title'] = chapter.get('title')
            knowledge['chapter_description'] = chapter.get('description')
            knowledge['content'] = chapter.get('theory_content', '')

        if course_id:
            course = CourseRepository.find_by_id(course_id)
            if not course:
                return jsonify({'success': False, 'error': 'Course not found'}), 404

            knowledge['course_title'] = course.get('title')
            knowledge['course_description'] = course.get('description')

        return jsonify({
            'success': True,
            'data': {
                'knowledge_type': knowledge_type,
                **knowledge
            }
        })

    except Exception as e:
        logger.error(f"Tutor knowledge error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tts_tutor_bp.route('/course/<course_id>/context', methods=['GET'])
@token_required
def get_course_tutor_context(course_id: str):
    """
    Get course context for tutor

    Path Parameters:
        course_id: Course ID

    Response:
        200: Course context
        {
            "success": true,
            "data": {
                "course_id": "123",
                "title": "Python Basics",
                "description": "...",
                "chapters_count": 10
            }
        }

        404: Course not found
    """
    try:
        user_id = get_jwt_identity()

        course = CourseRepository.find_by_id(course_id)
        if not course:
            return jsonify({'success': False, 'error': 'Course not found'}), 404

        chapters = ChapterRepository.get_by_course_id(course_id)

        return jsonify({
            'success': True,
            'data': {
                'course_id': course_id,
                'title': course.get('title'),
                'description': course.get('description'),
                'chapters_count': len(chapters),
                'chapters': [{'chapter_id': c.get('chapter_id'), 'title': c.get('title')} for c in chapters]
            }
        })

    except Exception as e:
        logger.error(f"Course context error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@tts_tutor_bp.route('/chapter/<chapter_id>/context', methods=['GET'])
@token_required
def get_chapter_tutor_context(chapter_id: str):
    """
    Get chapter context for tutor

    Path Parameters:
        chapter_id: Chapter ID

    Response:
        200: Chapter context
        {
            "success": true,
            "data": {
                "chapter_id": "456",
                "title": "Variables",
                "description": "...",
                "theory_available": true,
                "lessons_count": 5
            }
        }

        404: Chapter not found
    """
    try:
        user_id = get_jwt_identity()

        chapter = ChapterRepository.find_by_id(chapter_id)
        if not chapter:
            return jsonify({'success': False, 'error': 'Chapter not found'}), 404

        return jsonify({
            'success': True,
            'data': {
                'chapter_id': chapter_id,
                'title': chapter.get('title'),
                'description': chapter.get('description'),
                'theory_available': bool(chapter.get('theory_content')),
                'theory_content': chapter.get('theory_content', '')
            }
        })

    except Exception as e:
        logger.error(f"Chapter context error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
