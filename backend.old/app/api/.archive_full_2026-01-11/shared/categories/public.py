"""
LernsystemX Category API - Public Endpoints

Public read-only endpoints for category listing, search, and statistics.

Endpoints:
    GET /api/v1/categories        - List all categories (flat)
    GET /api/v1/categories/roots  - Get root categories only
    GET /api/v1/categories/search - Search categories
    GET /api/v1/categories/stats  - Get category statistics
    GET /api/v1/categories/by-path - Get category by path

ISO 27001:2013 compliant - Category management and access control
"""

from flask import Blueprint, request, jsonify

from app.models.category import (
    CategoryResponse,
)
from app.repositories.category import CategoryRepository


# Blueprint for public category endpoints
categories_public_bp = Blueprint(
    'categories_public',
    __name__,
    url_prefix='/categories'
)


@categories_public_bp.route('', methods=['GET'])
def list_categories():
    """
    List all categories (flat list)

    Query Parameters:
        active_only: Only return active categories (default: false)
        page: Page number (default: 1)
        per_page: Items per page (default: 100, max: 500)

    Response:
        200: List of categories ordered by level and order_index
        {
            "success": true,
            "categories": [...],
            "pagination": {
                "page": 1,
                "per_page": 100,
                "total": 150,
                "total_pages": 2
            }
        }
    """
    try:
        # Get query parameters
        active_only = request.args.get('active_only', 'false').lower() == 'true'
        page = max(int(request.args.get('page', 1)), 1)
        per_page = min(int(request.args.get('per_page', 100)), 500)

        # Get all categories
        categories = CategoryRepository.get_all(active_only)

        # Calculate pagination
        total = len(categories)
        total_pages = (total + per_page - 1) // per_page
        offset = (page - 1) * per_page
        paginated_categories = categories[offset:offset + per_page]

        # Convert to response models
        category_responses = [CategoryResponse(**cat) for cat in paginated_categories]

        return jsonify({
            'success': True,
            'categories': [cat.model_dump() for cat in category_responses],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to list categories',
            'details': str(e)
        }), 500


@categories_public_bp.route('/roots', methods=['GET'])
def get_root_categories():
    """
    Get all root categories (level 1, no parent)

    Query Parameters:
        active_only: Only return active categories (default: true)

    Response:
        200: List of root categories
        {
            "success": true,
            "categories": [
                {
                    "category_id": 1,
                    "name": "IT & Software",
                    "slug": "it-software",
                    "level": 1,
                    "course_count": 45,
                    "total_course_count": 250
                }
            ],
            "total": 10
        }
    """
    try:
        active_only = request.args.get('active_only', 'true').lower() == 'true'

        categories = CategoryRepository.get_root_categories(active_only)

        # Convert to response models
        category_responses = [CategoryResponse(**cat) for cat in categories]

        return jsonify({
            'success': True,
            'categories': [cat.model_dump() for cat in category_responses],
            'total': len(categories)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get root categories',
            'details': str(e)
        }), 500


@categories_public_bp.route('/search', methods=['GET'])
def search_categories():
    """
    Search categories by name or description

    Query Parameters:
        q: Search query (required)
        active_only: Only search active categories (default: false)

    Response:
        200: List of matching categories
    """
    try:
        search_term = request.args.get('q', '').strip()

        if not search_term or len(search_term) < 2:
            return jsonify({
                'success': False,
                'error': 'Invalid search query',
                'message': 'Search query must be at least 2 characters long'
            }), 400

        active_only = request.args.get('active_only', 'false').lower() == 'true'

        # Search categories
        categories = CategoryRepository.search(search_term, active_only)

        # Convert to response models
        category_responses = [CategoryResponse(**cat) for cat in categories]

        return jsonify({
            'success': True,
            'categories': [cat.model_dump() for cat in category_responses],
            'total': len(categories),
            'query': search_term
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Search failed',
            'details': str(e)
        }), 500


@categories_public_bp.route('/stats', methods=['GET'])
def get_category_stats():
    """
    Get category statistics

    Response:
        200: Category statistics
        {
            "success": true,
            "stats": {
                "total_categories": 150,
                "active_categories": 142,
                "level_1_count": 10,
                "level_2_count": 45,
                "level_3_count": 60,
                "level_4_count": 30,
                "level_5_count": 5,
                "max_level": 20
            }
        }
    """
    try:
        stats = CategoryRepository.get_statistics()

        return jsonify({
            'success': True,
            'stats': stats
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get statistics',
            'details': str(e)
        }), 500


@categories_public_bp.route('/by-path', methods=['GET'])
def get_category_by_path():
    """
    Get category by its full path

    Query Parameters:
        path: Full category path (required), e.g., "IT/Netzwerk/Cisco/CCNA"

    Response:
        200: Category details with children
        404: Category not found
    """
    try:
        path = request.args.get('path', '').strip()

        if not path:
            return jsonify({
                'success': False,
                'error': 'Path parameter required',
                'message': 'Please provide a category path'
            }), 400

        category = CategoryRepository.get_by_path(path)

        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found',
                'message': f'No category found with path: {path}'
            }), 404

        # Get subcategories
        subcategories = CategoryRepository.get_subcategories(category['category_id'])

        # Convert to response model
        category_response = CategoryResponse(**category)
        category_response.children = [CategoryResponse(**sub) for sub in subcategories]

        return jsonify({
            'success': True,
            'category': category_response.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get category by path',
            'details': str(e)
        }), 500
