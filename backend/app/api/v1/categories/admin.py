"""
LernsystemX Categories API - Admin Operations

Admin CRUD & Advanced Operations:
- POST /categories - Create category
- PUT /categories/<id> - Update category
- DELETE /categories/<id> - Delete category
- POST /categories/reorder - Reorder categories
- POST /categories/<id>/move - Move category to new parent
- POST /categories/<id>/activate - Activate category
- POST /categories/<id>/deactivate - Deactivate category

All routes: /api/v1/categories/*
ISO 27001:2013 compliant
"""

from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
import traceback

from app.models.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryReorderRequest,
)
from app.repositories.category import CategoryRepository
from app.middleware.auth import admin_required

admin_bp = Blueprint('categories_admin', __name__, url_prefix='/categories')

__all__ = ['admin_bp']


# =============================================================================
# ADMIN - CRUD OPERATIONS
# =============================================================================

@admin_bp.route('', methods=['POST'])
@admin_required
def create_category():
    """
    Create a new category (admin only)

    Request Body:
        {
            "name": "Web Development",
            "slug": "web-development",  // optional, auto-generated from name
            "description": "Learn web development",
            "parent_id": 2,  // optional, null for root categories
            "level": 3,  // 1-5
            "icon": "fa-globe",  // optional
            "color": "#3498db",  // optional
            "order_index": 0,  // optional, auto-assigned
            "is_active": true
        }

    Response:
        201: Category created successfully
        400: Validation error
        403: Insufficient permissions
    """
    try:
        data = request.get_json()

        # Validate with Pydantic
        category_data = CategoryCreate(**data)

        # Create category
        category = CategoryRepository.create(category_data.model_dump())

        return jsonify({
            'success': True,
            'message': 'Category created successfully',
            'category': category
        }), 201

    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.errors()
        }), 400

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Invalid category data',
            'message': str(e)
        }), 400

    except Exception as e:
        current_app.logger.error(f"ERROR in create_category: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Category creation failed',
            'details': str(e)
        }), 500


@admin_bp.route('/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id: int):
    """
    Update category (admin only)

    Note: Cannot update level or parent_id to prevent breaking hierarchy

    Request Body: Partial category data to update
        {
            "name": "Updated Name",
            "description": "Updated description",
            "icon": "fa-new-icon",
            "is_active": true
        }

    Response:
        200: Category updated successfully
        400: Validation error
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

        data = request.get_json()

        # Validate with Pydantic
        category_data = CategoryUpdate(**data)

        # Update category
        updated_category = CategoryRepository.update(
            category_id,
            category_data.model_dump(exclude_none=True)
        )

        return jsonify({
            'success': True,
            'message': 'Category updated successfully',
            'category': updated_category
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
            'error': 'Category update failed',
            'details': str(e)
        }), 500


@admin_bp.route('/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id: int):
    """
    Delete category with all subcategories (admin only)

    CASCADE DELETE: Automatically deletes all subcategories.
    Will fail if category or any subcategory has courses assigned.

    Response:
        200: Category and subcategories deleted successfully
        400: Cannot delete (has courses)
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

        # Cascade delete (includes all subcategories)
        result = CategoryRepository.delete(category_id, cascade=True)

        if result["deleted_categories"] > 1:
            message = f'Kategorie und {result["deleted_categories"] - 1} Unterkategorie(n) erfolgreich gelöscht'
        else:
            message = 'Kategorie erfolgreich gelöscht'

        return jsonify({
            'success': True,
            'message': message,
            'deleted_categories': result['deleted_categories']
        }), 200

    except ValueError as e:
        return jsonify({
            'success': False,
            'error': 'Cannot delete category',
            'message': str(e)
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Category deletion failed',
            'details': str(e)
        }), 500


# =============================================================================
# ADMIN - ADVANCED OPERATIONS
# =============================================================================

@admin_bp.route('/reorder', methods=['POST'])
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


@admin_bp.route('/<int:category_id>/move', methods=['POST'])
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


@admin_bp.route('/<int:category_id>/activate', methods=['POST'])
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


@admin_bp.route('/<int:category_id>/deactivate', methods=['POST'])
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
