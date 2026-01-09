"""
LernsystemX Category API - Admin CRUD Endpoints

Basic CRUD operations for category management:
- POST   /api/v1/categories - Create category
- PUT    /api/v1/categories/:id - Update category
- DELETE /api/v1/categories/:id - Delete category

ISO 27001:2013 compliant
"""

from flask import Blueprint, request, jsonify, current_app
from pydantic import ValidationError
import traceback

from app.models.category import (
    CategoryCreate,
    CategoryUpdate,
)
from app.repositories.category import CategoryRepository
from app.middleware.auth import admin_required


# Blueprint for admin CRUD operations
categories_admin_crud_bp = Blueprint(
    'categories_admin_crud',
    __name__,
    url_prefix='/categories'
)


@categories_admin_crud_bp.route('', methods=['POST'])
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


@categories_admin_crud_bp.route('/<int:category_id>', methods=['PUT'])
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


@categories_admin_crud_bp.route('/<int:category_id>', methods=['DELETE'])
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
