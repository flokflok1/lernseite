"""
LernsystemX Learning Methods API - Public Endpoints

Public endpoints accessible without authentication:
- GET  /api/v1/learning-methods          - List all methods
- GET  /api/v1/learning-methods/:id      - Get method details
- GET  /api/v1/learning-methods/:id/examples - Get usage examples
- GET  /api/v1/learning-methods/:id/feedback - Get method feedback

ISO 27001:2013 compliant - AI execution security and token management
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import Blueprint

from .._helpers import (
    request,
    jsonify,
    LearningMethodResponse,
    LearningMethodRepository,
)

# Blueprint for public learning method endpoints
lm_public_bp = Blueprint(
    'learning_methods_public',
    __name__,
    url_prefix='/learning-methods'
)


@lm_public_bp.route('', methods=['GET'])
def list_learning_methods():
    """
    List all learning methods

    Query Parameters:
        active_only: Only return active methods (default: true)
        tier: Filter by tier (basic, premium, pro)

    Response:
        200: List of learning methods
        {
            "success": true,
            "methods": [
                {
                    "method_id": 1,
                    "name": "Flashcards",
                    "description": "Classic flashcards with Q&A",
                    "tier": "basic",
                    "config": {...},
                    "active": true,
                    "usage_count": 1234
                }
            ],
            "total": 21
        }
    """
    try:
        # Get query parameters
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        tier_filter = request.args.get('tier')

        # Get all methods
        methods = LearningMethodRepository.get_all(active_only)

        # Filter by tier if specified
        if tier_filter:
            methods = [m for m in methods if m['tier'] == tier_filter]

        # Convert to response models
        method_responses = [LearningMethodResponse(**method) for method in methods]

        return jsonify({
            'success': True,
            'methods': [m.model_dump() for m in method_responses],
            'total': len(methods)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list learning methods',
            'details': str(e)
        }), 500


@lm_public_bp.route('/<string:method_id>', methods=['GET'])
def get_learning_method(method_id: str):
    """
    Get learning method details

    Path Parameters:
        method_id: Learning method ID

    Response:
        200: Method details
        404: Method not found
    """
    try:
        method = LearningMethodRepository.find_by_id(method_id)

        if not method:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        # Get feedback stats
        feedback_stats = LearningMethodRepository.get_feedback_stats(method_id)

        # Convert to response model
        method_response = LearningMethodResponse(**method)
        method_dict = method_response.model_dump()
        method_dict['feedback_stats'] = feedback_stats

        return jsonify({
            'success': True,
            'method': method_dict
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get learning method',
            'details': str(e)
        }), 500


@lm_public_bp.route('/<string:method_id>/examples', methods=['GET'])
def get_method_examples(method_id: str):
    """
    Get usage examples for learning method

    Path Parameters:
        method_id: Learning method ID

    Response:
        200: Usage examples based on method type
    """
    try:
        method = LearningMethodRepository.find_by_id(method_id)

        if not method:
            return jsonify({
                'success': False,
                'error': 'Learning method not found'
            }), 404

        # Example prompts by method type
        examples = {
            'KI-Tutor': [
                {
                    'prompt': 'Erkläre mir Polymorphismus in Python',
                    'context': 'Wir sind bei Lektion 3: OOP Konzepte',
                    'difficulty': 'intermediate'
                },
                {
                    'prompt': 'Was sind Decorators und wann verwende ich sie?',
                    'context': 'Python Advanced Concepts',
                    'difficulty': 'advanced'
                }
            ],
            'KI-Glossar': [
                {
                    'prompt': 'Rekursion',
                    'context': 'Informatik Grundlagen',
                    'difficulty': 'beginner'
                },
                {
                    'prompt': 'Algorithmus',
                    'context': None,
                    'difficulty': 'beginner'
                }
            ],
            'Braindump': [
                {
                    'prompt': 'Fasse die wichtigsten Konzepte von SQL zusammen',
                    'context': 'Nach Abschluss von Modul 2: Datenbanken',
                    'difficulty': 'intermediate'
                }
            ],
            'Deep Praxis': [
                {
                    'prompt': 'Erstelle eine REST API für eine Bibliotheksverwaltung',
                    'context': 'Projekt: Library Management System',
                    'difficulty': 'advanced'
                }
            ]
        }

        method_examples = examples.get(method['name'], [
            {
                'prompt': f'Beispiel für {method["name"]}',
                'context': 'Allgemeiner Kontext',
                'difficulty': 'intermediate'
            }
        ])

        return jsonify({
            'success': True,
            'method_id': method_id,
            'method_name': method['name'],
            'examples': method_examples
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get examples',
            'details': str(e)
        }), 500


@lm_public_bp.route('/<string:method_id>/feedback', methods=['GET'])
def get_method_feedback(method_id: str):
    """
    Get feedback for learning method

    Path Parameters:
        method_id: Learning method ID

    Query Parameters:
        limit: Maximum results (default: 50)

    Response:
        200: List of feedback
    """
    try:
        limit = min(int(request.args.get('limit', 50)), 200)

        feedback_list = LearningMethodRepository.get_method_feedback(method_id, limit)
        feedback_stats = LearningMethodRepository.get_feedback_stats(method_id)

        return jsonify({
            'success': True,
            'feedback': feedback_list,
            'stats': feedback_stats,
            'total': len(feedback_list)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get feedback',
            'details': str(e)
        }), 500
