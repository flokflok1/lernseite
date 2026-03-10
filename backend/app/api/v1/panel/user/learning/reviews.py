"""
Review API — Panel/User endpoints for spaced repetition.

Endpoints:
  POST /api/v1/user/learning/reviews/initialize  — Init SRS for a course
  GET  /api/v1/user/learning/reviews/queue        — Get due review items
  POST /api/v1/user/learning/reviews/submit        — Submit review result
  GET  /api/v1/user/learning/reviews/mastery       — Get mastery map
  GET  /api/v1/user/learning/reviews/stats         — Get review statistics
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.application.services.learning.review_service import ReviewService

review_bp = Blueprint('reviews', __name__, url_prefix='/user/learning/reviews')


@review_bp.route('/initialize', methods=['POST'])
@jwt_required()
def initialize_reviews():
    """Initialize SRS for all LMs in a course."""
    user_id = get_jwt_identity()
    data = request.json or {}
    course_id = data.get('course_id')
    if not course_id:
        return jsonify({'error': 'course_id required'}), 400

    result = ReviewService.initialize_course_reviews(user_id, course_id)
    return jsonify(result)


@review_bp.route('/queue', methods=['GET'])
@jwt_required()
def get_review_queue():
    """Get prioritized review queue."""
    user_id = get_jwt_identity()
    course_id = request.args.get('course_id')
    try:
        limit = min(int(request.args.get('limit', 20)), 100)
    except (ValueError, TypeError):
        limit = 20

    result = ReviewService.get_review_queue(user_id, course_id, limit)
    return jsonify(result)


@review_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_review():
    """Process a completed review."""
    user_id = get_jwt_identity()
    data = request.json or {}

    method_id = data.get('method_id')
    if not method_id:
        return jsonify({'error': 'method_id required'}), 400

    try:
        score = max(0.0, min(100.0, float(data.get('score', 0))))
    except (ValueError, TypeError):
        return jsonify({'error': 'score must be a number 0-100'}), 400

    try:
        time_seconds = max(0, int(data.get('time_seconds', 0)))
    except (ValueError, TypeError):
        time_seconds = 0

    result = ReviewService.process_review(
        user_id, method_id, score, time_seconds,
    )
    return jsonify({'review': result})


@review_bp.route('/mastery', methods=['GET'])
@jwt_required()
def get_mastery_map():
    """Get per-chapter mastery overview."""
    user_id = get_jwt_identity()
    course_id = request.args.get('course_id')
    if not course_id:
        return jsonify({'error': 'course_id required'}), 400

    mastery = ReviewService.get_mastery_map(user_id, course_id)
    return jsonify({'mastery': mastery})


@review_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_review_stats():
    """Get summary review statistics."""
    user_id = get_jwt_identity()
    course_id = request.args.get('course_id')
    if not course_id:
        return jsonify({'error': 'course_id required'}), 400

    stats = ReviewService.get_stats(user_id, course_id)
    return jsonify({'stats': stats})
