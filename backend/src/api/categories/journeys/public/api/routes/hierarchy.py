"""
Categories Domain - Hierarchy Routes (Public Journey)

Endpoints for hierarchical category operations: tree, breadcrumbs, descendants.

Endpoints:
- GET /categories/tree - Hierarchical tree structure
- GET /categories/:id - Get category details
- GET /categories/:id/breadcrumb - Get category breadcrumb path
- GET /categories/:id/descendants - Get all descendants

Architecture: Journey-Based DDD
Database: PostgreSQL via CategoryRepository (direct SQL)
ISO 27001:2013 compliant - Category hierarchy navigation
"""

from flask import Blueprint, request, jsonify

from app.models.category import (
    CategoryResponse,
    CategoryTreeNode,
    CategoryTreeResponse,
)
from app.repositories.category import CategoryRepository


# Blueprint for hierarchy category endpoints
categories_hierarchy_bp = Blueprint(
    'categories_hierarchy',
    __name__,
    url_prefix='/categories'
)


@categories_hierarchy_bp.route('/tree', methods=['GET'])
def get_category_tree():
    """
    Get hierarchical category tree (unlimited depth, practical limit 20)

    Query Parameters:
        active_only: Only include active categories (default: false)
        max_depth: Limit tree depth (default: unlimited)

    Response:
        200: Hierarchical tree structure
        {
            "success": true,
            "tree": {
                "categories": [
                    {
                        "category_id": 1,
                        "name": "IT & Software",
                        "level": 1,
                        "path": "IT & Software",
                        "children": [
                            {
                                "category_id": 2,
                                "name": "Programming",
                                "level": 2,
                                "path": "IT & Software/Programming",
                                "children": [...]
                            }
                        ]
                    }
                ],
                "total_categories": 150,
                "max_level": 20,
                "active_categories": 142
            }
        }

        500: Server error

    Notes:
        - Recursive structure with unlimited nesting
        - Practical depth limit: 20 levels
        - Returns complete hierarchy from all roots
    """
    try:
        # Get query parameters
        active_only = request.args.get('active_only', 'false').lower() == 'true'

        # Get tree
        tree_data = CategoryRepository.get_tree(active_only)

        # Get statistics
        stats = CategoryRepository.get_statistics()

        # Convert to tree nodes
        tree_nodes = [CategoryTreeNode(**cat) for cat in tree_data]

        # Build response
        tree_response = CategoryTreeResponse(
            categories=tree_nodes,
            total_categories=stats.get('total_categories', 0),
            max_level=stats.get('max_level', 0),
            active_categories=stats.get('active_categories', 0)
        )

        return jsonify({
            'success': True,
            'tree': tree_response.model_dump()
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get category tree',
            'details': str(e)
        }), 500


@categories_hierarchy_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id: int):
    """
    Get category details by ID

    Path Parameters:
        category_id: Category ID

    Response:
        200: Category details with direct children
        {
            "success": true,
            "category": {
                "category_id": 1,
                "name": "IT & Software",
                "slug": "it-software",
                "description": "...",
                "level": 1,
                "path": "IT & Software",
                "children": [...]
            }
        }

        404: Category not found
        500: Server error
    """
    try:
        category = CategoryRepository.find_by_id(category_id)

        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found',
                'message': 'The requested category does not exist'
            }), 404

        # Get subcategories (direct children)
        subcategories = CategoryRepository.get_subcategories(category_id)

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
            'error': 'Failed to get category',
            'details': str(e)
        }), 500


@categories_hierarchy_bp.route('/<int:category_id>/breadcrumb', methods=['GET'])
def get_category_breadcrumb(category_id: int):
    """
    Get category breadcrumb path from root to category

    Path Parameters:
        category_id: Category ID

    Response:
        200: Breadcrumb path
        {
            "success": true,
            "breadcrumb": [
                {"category_id": 1, "name": "IT & Software", "level": 1},
                {"category_id": 2, "name": "Programming", "level": 2},
                {"category_id": 5, "name": "Python", "level": 3}
            ]
        }

        404: Category not found
        500: Server error

    Notes:
        - Returns complete path from root to target category
        - Ordered from root (level 1) to target
        - Useful for navigation breadcrumbs
    """
    try:
        breadcrumb = CategoryRepository.get_breadcrumb(category_id)

        if not breadcrumb:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 404

        return jsonify({
            'success': True,
            'breadcrumb': breadcrumb
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get breadcrumb',
            'details': str(e)
        }), 500


@categories_hierarchy_bp.route('/<int:category_id>/descendants', methods=['GET'])
def get_category_descendants(category_id: int):
    """
    Get all descendants of a category (recursive, unlimited depth)

    Path Parameters:
        category_id: Category ID

    Query Parameters:
        include_self: Include the category itself (default: false)
        active_only: Only return active categories (default: false)

    Response:
        200: List of all descendant categories
        {
            "success": true,
            "category_id": 1,
            "category_name": "IT & Software",
            "category_path": "IT & Software",
            "descendants": [...],
            "total": 45
        }

        404: Category not found
        500: Server error

    Notes:
        - Returns ALL descendants recursively
        - Flattened list (not tree structure)
        - Use include_self=true to include the category itself
    """
    try:
        category = CategoryRepository.find_by_id(category_id)

        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 404

        include_self = request.args.get('include_self', 'false').lower() == 'true'
        active_only = request.args.get('active_only', 'false').lower() == 'true'

        descendants = CategoryRepository.get_descendants(category_id, include_self, active_only)

        # Convert to response models
        descendant_responses = [CategoryResponse(**cat) for cat in descendants]

        return jsonify({
            'success': True,
            'category_id': category_id,
            'category_name': category.get('name'),
            'category_path': category.get('path'),
            'descendants': [cat.model_dump() for cat in descendant_responses],
            'total': len(descendants)
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get descendants',
            'details': str(e)
        }), 500
