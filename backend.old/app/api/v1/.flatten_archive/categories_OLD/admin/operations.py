"""
LernsystemX Category API - Admin Advanced Operations

Advanced operations for category management:
- POST /api/v1/categories/reorder - Reorder categories
- POST /api/v1/categories/:id/move - Move category to new parent
- POST /api/v1/categories/:id/activate - Activate category
- POST /api/v1/categories/:id/deactivate - Deactivate category

ISO 27001:2013 compliant
"""

from flask import Blueprint, request, jsonify
from pydantic import ValidationError

from app.models.category import CategoryReorderRequest
from app.repositories.category import CategoryRepository
from app.middleware.auth import admin_required


# Blueprint for admin operations
categories_admin_ops_bp = Blueprint(
    'categories_admin_operations',
    __name__,
    url_prefix='/categories'
)


@categories_admin_ops_bp.route('/reorder', methods=['POST'])
@admin_required
def reorder_categories():
    """
    Reorder categories (admin only)

    Request Body:
        {
            "category_orders": [
                {"category_id": 5, "order_index": 0},
                {"category_id": 3, "order_index": 1},
                {"category_id": 8, "order_index": 2}
            ]
        }

    Response:
        200: Categories reordered successfully
        400: Validation error
        403: Insufficient permissions
    """
    try:
        data = request.get_json()

        # Validate with Pydantic
        reorder_data = CategoryReorderRequest(**data)

        # Reorder categories
        CategoryRepository.reorder(reorder_data.category_orders)

        return jsonify({
            'success': True,
            'message': 'Categories reordered successfully'
        }), 200

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Reordering failed',
            'details': str(e)
        }), 500


@categories_admin_ops_bp.route('/<int:category_id>/move', methods=['POST'])
@admin_required
def move_category(category_id: int):
    """
    Move category to a new parent (admin only)

    Moves a category and all its descendants to a new parent.
    Automatically recalculates paths, levels, and root_id for all affected categories.

    Path Parameters:
        category_id: Category ID to move

    Request Body:
        {
            "new_parent_id": 5  // null to make it a root category
        }

    Response:
        200: Category moved successfully
        {
            "success": true,
            "message": "Category moved successfully",
            "category": {...},
            "old_path": "IT/Netzwerk/Cisco",
            "new_path": "Business/IT-Management/Cisco"
        }
        400: Invalid move (circular reference, depth limit exceeded)
        403: Insufficient permissions
        404: Category or new parent not found
    """
    try:
        category = CategoryRepository.find_by_id(category_id)

        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 404

        data = request.get_json()
        new_parent_id = data.get('new_parent_id')

        # Validate new parent exists (if not making it a root)
        if new_parent_id is not None:
            new_parent = CategoryRepository.find_by_id(new_parent_id)
            if not new_parent:
                return jsonify({
                    'success': False,
                    'error': 'New parent category not found'
                }), 404

        old_path = category.get('path', '')

        # Move category
        updated_category = CategoryRepository.move_category(category_id, new_parent_id)

        if not updated_category:
            return jsonify({
                'success': False,
                'error': 'Failed to move category',
                'message': 'Move operation returned no result'
            }), 500

        return jsonify({
            'success': True,
            'message': 'Category moved successfully',
            'category': updated_category,
            'old_path': old_path,
            'new_path': updated_category.get('path', '')
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid move operation',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Move operation failed',
            'details': str(e)
        }), 500


@categories_admin_ops_bp.route('/<int:category_id>/activate', methods=['POST'])
@admin_required
def activate_category(category_id: int):
    """
    Activate category (admin only)

    Response:
        200: Category activated successfully
        403: Insufficient permissions
        404: Category not found
    """
    try:
        category = CategoryRepository.find_by_id(category_id)

        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 404

        # Activate category
        updated_category = CategoryRepository.activate(category_id)

        return jsonify({
            'success': True,
            'message': 'Category activated successfully',
            'category': updated_category
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Activation failed',
            'details': str(e)
        }), 500


@categories_admin_ops_bp.route('/<int:category_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_category(category_id: int):
    """
    Deactivate category (soft delete, admin only)

    Response:
        200: Category deactivated successfully
        403: Insufficient permissions
        404: Category not found
    """
    try:
        category = CategoryRepository.find_by_id(category_id)

        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 404

        # Deactivate category
        updated_category = CategoryRepository.deactivate(category_id)

        return jsonify({
            'success': True,
            'message': 'Category deactivated successfully',
            'category': updated_category
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Deactivation failed',
            'details': str(e)
        }), 500
