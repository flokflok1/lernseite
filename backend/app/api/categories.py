"""
LernsystemX Category API

Flexible hierarchical course categorization (unlimited depth):
- GET    /api/v1/categories - List all categories (flat)
- GET    /api/v1/categories/tree - Hierarchical tree structure (unlimited depth)
- GET    /api/v1/categories/roots - Get root categories only
- GET    /api/v1/categories/:id - Get category details
- GET    /api/v1/categories/:id/descendants - Get all descendants
- GET    /api/v1/categories/:id/breadcrumb - Get category breadcrumb path
- GET    /api/v1/categories/by-path - Get category by path
- GET    /api/v1/categories/search - Search categories
- GET    /api/v1/categories/stats - Get category statistics
- POST   /api/v1/categories - Create category (admin only)
- PUT    /api/v1/categories/:id - Update category (admin only)
- DELETE /api/v1/categories/:id - Delete category (admin only)
- POST   /api/v1/categories/:id/move - Move category to new parent (admin only)
- POST   /api/v1/categories/reorder - Reorder categories (admin only)

ISO 27001:2013 compliant - Category management and access control
ISO/IEC/IEEE 26515:2018 compliant - RESTful API design
"""

from flask import request, jsonify
from pydantic import ValidationError

from app.api import api_v1
from app.models.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryTreeNode,
    CategoryTreeResponse,
    CategoryListResponse,
    CategoryReorderRequest
)
from app.repositories.category_repository import CategoryRepository
from app.middleware.auth import token_required, admin_required, get_current_user


# ============================================================================
# PUBLIC CATEGORY ENDPOINTS
# ============================================================================

@api_v1.route('/categories', methods=['GET'])
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


@api_v1.route('/categories/tree', methods=['GET'])
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


@api_v1.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    Get category details by ID

    Path Parameters:
        category_id: Category ID

    Response:
        200: Category details
        404: Category not found
    """
    try:
        category = CategoryRepository.find_by_id(category_id)

        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found',
                'message': 'The requested category does not exist'
            }), 404

        # Get subcategories
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


@api_v1.route('/categories/<int:category_id>/breadcrumb', methods=['GET'])
def get_category_breadcrumb(category_id):
    """
    Get category breadcrumb path from root to category

    Path Parameters:
        category_id: Category ID

    Response:
        200: Breadcrumb path
        [
            {"category_id": 1, "name": "IT & Software", "level": 1},
            {"category_id": 2, "name": "Programming", "level": 2},
            {"category_id": 5, "name": "Python", "level": 3}
        ]
        404: Category not found
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


@api_v1.route('/categories/search', methods=['GET'])
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


@api_v1.route('/categories/stats', methods=['GET'])
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


@api_v1.route('/categories/roots', methods=['GET'])
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


@api_v1.route('/categories/by-path', methods=['GET'])
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


@api_v1.route('/categories/<int:category_id>/descendants', methods=['GET'])
def get_category_descendants(category_id):
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
            "descendants": [...],
            "total": 45
        }
        404: Category not found
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


# ============================================================================
# ADMIN CATEGORY ENDPOINTS
# ============================================================================

@api_v1.route('/categories', methods=['POST'])
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
        import traceback
        from flask import current_app
        current_app.logger.error(f"ERROR in create_category: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Category creation failed',
            'details': str(e)
        }), 500


@api_v1.route('/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
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
        updated_category = CategoryRepository.update(category_id, category_data.model_dump(exclude_none=True))

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


@api_v1.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
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

        return jsonify({
            'success': True,
            'message': f'Kategorie und {result["deleted_categories"] - 1} Unterkategorie(n) erfolgreich gelöscht' if result["deleted_categories"] > 1 else 'Kategorie erfolgreich gelöscht',
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


@api_v1.route('/categories/reorder', methods=['POST'])
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


@api_v1.route('/categories/<int:category_id>/move', methods=['POST'])
@admin_required
def move_category(category_id):
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


@api_v1.route('/categories/<int:category_id>/activate', methods=['POST'])
@admin_required
def activate_category(category_id):
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


@api_v1.route('/categories/<int:category_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_category(category_id):
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


# ============================================================================
# ADMIN CATEGORY MANAGEMENT ROUTES (Phase B24-07)
# Aliased routes under /admin/categories for consistency with frontend
# ============================================================================

@api_v1.route('/admin/categories', methods=['POST'])
@admin_required
def admin_create_category():
    """Admin: Create category (alias to /categories POST)"""
    return create_category()


@api_v1.route('/admin/categories/<int:category_id>', methods=['PATCH', 'PUT'])
@admin_required
def admin_update_category(category_id):
    """Admin: Update category (alias to /categories/:id PUT)"""
    return update_category(category_id)


@api_v1.route('/admin/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def admin_delete_category(category_id):
    """Admin: Delete category (alias to /categories/:id DELETE)"""
    return delete_category(category_id)
